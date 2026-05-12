"""
Lightweight smoke check: run pipeline for a fixed date with stub data.

Usage: python -m trends_brief.selfcheck
(requires src on PYTHONPATH or editable install)
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    src = root / "src"
    sys.path.insert(0, str(src))

    from trends_brief.pipeline import run_pipeline

    fixed = "2000-01-01"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp) / "proj"
        (tmp_root / "config").mkdir(parents=True)
        # Minimal sources: stub only
        (tmp_root / "config" / "sources.yaml").write_text(
            "adapters:\n  - name: stub\n    enabled: true\n    config: {}\n",
            encoding="utf-8",
        )
        (tmp_root / "config" / "persona.example.yaml").write_text(
            "niche_keywords: [test]\npersona_one_line: Selfcheck\nidea_templates:\n  - 'Idea: {title}'\n",
            encoding="utf-8",
        )
        run_pipeline(
            root=tmp_root,
            date_str=fixed,
            skip_pdf=True,
            pdf_optional=False,
            pdf_cmd=None,
            sources_path=tmp_root / "config" / "sources.yaml",
        )
        derived = tmp_root / "data" / "derived" / f"{fixed}.json"
        report = tmp_root / "reports" / f"{fixed}.md"
        if not derived.is_file() or not report.is_file():
            print("selfcheck failed: missing outputs", file=sys.stderr)
            return 1
        text = report.read_text(encoding="utf-8")
        if fixed not in text or "#MorningRoutine" not in text:
            print("selfcheck failed: unexpected report content", file=sys.stderr)
            return 1
    print("selfcheck ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
