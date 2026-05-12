#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.is_dir():
    sys.path.insert(0, str(SRC))

from trends_brief.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Gather trends, write Markdown, optional PDF.")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Report date (YYYY-MM-DD). Default: today.",
    )
    parser.add_argument("--skip-pdf", action="store_true", help="Do not run the PDF step.")
    parser.add_argument(
        "--pdf-optional",
        action="store_true",
        help="If PDF fails, print a warning and exit 0.",
    )
    parser.add_argument(
        "--pdf-cmd",
        default=None,
        help="Override PDF command template (else MD2PDF_CMD env). Use {input} and {output}.",
    )
    parser.add_argument(
        "--sources",
        type=Path,
        default=None,
        help="Path to sources YAML (default: config/sources.yaml if present else built-in stub only).",
    )
    args = parser.parse_args()

    sources_path = args.sources
    if sources_path is None:
        explicit = ROOT / "config" / "sources.yaml"
        example = ROOT / "config" / "sources.example.yaml"
        if explicit.is_file():
            sources_path = explicit
        else:
            sources_path = example if example.is_file() else explicit

    run_pipeline(
        root=ROOT,
        date_str=args.date,
        skip_pdf=args.skip_pdf,
        pdf_optional=args.pdf_optional,
        pdf_cmd=args.pdf_cmd,
        sources_path=sources_path,
    )


if __name__ == "__main__":
    main()
