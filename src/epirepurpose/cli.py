"""Command-line interface."""
from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__
from .data.download import download_all


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="epirepurpose")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command")

    dl = sub.add_parser("download", help="Download raw data listed in the manifest")
    dl.add_argument("--manifest", default="data/manifest.yaml")
    dl.add_argument("--raw-dir", default="data/raw")

    args = parser.parse_args(argv)
    if args.command == "download":
        download_all(Path(args.manifest), Path(args.raw_dir))
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
