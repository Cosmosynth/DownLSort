"""DownLSort command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from . import __version__
    from .app import App
    from .scanner import DEFAULT_FOLDER
except ImportError:
    from downlsort import __version__
    from downlsort.app import App
    from downlsort.scanner import DEFAULT_FOLDER


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="downlsort",
        description="Organize a cluttered folder through a clean GUI.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_FOLDER,
        help=f"Folder to organize (default: {DEFAULT_FOLDER})",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    app = App(folder=args.path)
    app.mainloop()


if __name__ == "__main__":
    main()
