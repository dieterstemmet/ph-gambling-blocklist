"""Run `python -m phblock build` or `python -m phblock refresh`."""

import argparse
from pathlib import Path
import sys

from .catalog import build
from .discovery import refresh


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    commands = parser.add_subparsers(dest="command", required=True)
    build_command = commands.add_parser("build", help="build reviewed DNS lists")
    build_command.add_argument("--check", action="store_true", help="check outputs without writing")
    refresh_command = commands.add_parser("refresh", help="propose changes from PAGCOR")
    refresh_command.add_argument("--pdf", type=Path, help="use a locally downloaded PAGCOR PDF")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            drift = build(args.root, check=args.check)
            if drift:
                print("Generated files need rebuilding: " + ", ".join(drift), file=sys.stderr)
                return 1
            print("Reviewed blocklists verified." if args.check else "Reviewed blocklists built.")
        else:
            report = refresh(args.root, pdf=args.pdf)
            print(f"PAGCOR {report['source']['published_on']}: {len(report['additions'])} additions, {len(report['missing'])} missing, {len(report['excluded'])} excluded, {len(report['source']['extraction_issues'])} extraction issues. Review reports/pagcor.json; published lists unchanged.")
    except (ValueError, OSError, ImportError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
