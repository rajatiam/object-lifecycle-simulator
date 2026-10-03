"""Deterministic lifecycle dry runs with retention and legal-hold precedence."""

from datetime import date
import json, os, tempfile, re
from pathlib import Path

CLASSES = {"standard", "infrequent", "archive"}


def day(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Dates must use YYYY-MM-DD strings")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid ISO date") from exc


def plan(objects, policies, as_of):
    as_of = day(as_of)
    if not isinstance(objects, list) or not isinstance(policies, list):
        raise ValueError("Objects and policies must be arrays")
    prefixes = set()
    for policy in policies:
        if not isinstance(policy, dict):
            raise ValueError("Policy must be an object")
        prefix = policy.get("prefix")
        if not isinstance(prefix, str) or prefix in prefixes:
            raise ValueError("Policy prefixes must be unique strings")
        prefixes.add(prefix)
        if not any(
            key in policy for key in ["expire_after_days", "transition_after_days"]
        ):
            raise ValueError("Policy must define expiry or transition")
        for field in ["expire_after_days", "transition_after_days"]:
            if field in policy and (
                type(policy[field]) is not int or policy[field] < 0
            ):
                raise ValueError("Policy ages must be nonnegative integers")
        if (
            "transition_after_days" in policy
            and policy.get("storage_class") not in CLASSES
        ):
            raise ValueError("Transition requires a supported storage class")
    results = []
    keys = set()
    for obj in objects:
        if not isinstance(obj, dict):
            raise ValueError("Inventory entry must be an object")
        key = obj.get("key")
        if not isinstance(key, str) or not key or key in keys:
            raise ValueError("Object keys must be unique nonempty strings")
        keys.add(key)
        if (
            obj.get("storage_class", "standard") not in CLASSES
            or type(obj.get("legal_hold", False)) is not bool
        ):
            raise ValueError("Invalid storage class or legal hold")
        created = day(obj.get("created"))
        if created > as_of:
            raise ValueError("Object creation date is in the future")
        age = (as_of - created).days
        retain = day(obj["retain_until"]) if obj.get("retain_until") else None
        candidates = [p for p in policies if key.startswith(p["prefix"])]
        policy = max(candidates, key=lambda p: len(p["prefix"])) if candidates else None
        item = {
            "key": key,
            "action": "keep",
            "reason": "No matching policy",
            "age_days": age,
        }
        if policy:
            item.update(
                policy_prefix=policy["prefix"], reason="Age threshold not reached"
            )
            expired = (
                "expire_after_days" in policy and age >= policy["expire_after_days"]
            )
            held = obj.get("legal_hold", False) or (retain and retain > as_of)
            if expired and held:
                item["reason"] = "Deletion blocked by legal hold or retention"
            elif expired:
                item.update(action="delete", reason="Expiration threshold reached")
            elif (
                "transition_after_days" in policy
                and age >= policy["transition_after_days"]
                and obj.get("storage_class", "standard") != policy["storage_class"]
            ):
                item.update(
                    action="transition",
                    storage_class=policy["storage_class"],
                    reason="Transition threshold reached",
                )
        results.append(item)
    results.sort(key=lambda item: item["key"])
    return {
        "as_of": as_of.isoformat(),
        "dry_run": True,
        "objects": results,
        "summary": {
            action: sum(item["action"] == action for item in results)
            for action in ["keep", "transition", "delete"]
        },
    }


def write_plan(path, result):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as out:
        temporary = Path(out.name)
        json.dump(result, out, indent=2)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
