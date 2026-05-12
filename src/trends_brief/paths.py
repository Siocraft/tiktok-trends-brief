from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Filesystem layout under project root."""

    root: Path

    @property
    def config_dir(self) -> Path:
        return self.root / "config"

    @property
    def data_raw(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def data_derived(self) -> Path:
        return self.root / "data" / "derived"

    @property
    def reports(self) -> Path:
        return self.root / "reports"

    @property
    def reports_pdf(self) -> Path:
        return self.reports / "pdf"

    def raw_day(self, date_str: str) -> Path:
        return self.data_raw / date_str

    def derived_file(self, date_str: str) -> Path:
        return self.data_derived / f"{date_str}.json"

    def report_md(self, date_str: str) -> Path:
        return self.reports / f"{date_str}.md"

    def report_pdf(self, date_str: str) -> Path:
        return self.reports_pdf / f"{date_str}.pdf"
