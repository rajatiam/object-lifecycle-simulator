import argparse, json
from pathlib import Path
from .core import plan, write_plan


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Plan object lifecycle actions without cloud calls or deletion"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("plan")
    run.add_argument("objects")
    run.add_argument("policies")
    run.add_argument("--as-of", required=True)
    run.add_argument("--output")
    args = parser.parse_args(argv)
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
