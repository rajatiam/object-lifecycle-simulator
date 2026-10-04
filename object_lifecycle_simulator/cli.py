import argparse, json
from pathlib import Path
from .core import plan, write_plan, compare


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Plan and compare lifecycle decisions without cloud operations"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("compare")
    sub.add_argument("before")
    sub.add_argument("after")
    sub = commands.add_parser("plan")
    sub.add_argument("objects")
    sub.add_argument("policies")
    sub.add_argument("--as-of", required=True)
    sub.add_argument("--output")
    args = parser.parse_args(argv)
    if args.command == "compare":
        result = compare(
            json.loads(Path(args.before).read_text(encoding="utf-8")),
            json.loads(Path(args.after).read_text(encoding="utf-8")),
        )
    else:
        if args.output and Path(args.output).resolve() in [
            Path(args.objects).resolve(),
            Path(args.policies).resolve(),
        ]:
            raise ValueError("Output must differ from input files")
        result = plan(
            json.loads(Path(args.objects).read_text(encoding="utf-8")),
            json.loads(Path(args.policies).read_text(encoding="utf-8")),
            args.as_of,
        )
        if args.output:
            write_plan(args.output, result)
    print(json.dumps(result, indent=2))
