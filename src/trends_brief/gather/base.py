from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class GatherAdapter(ABC):
    """Writes one or more files under raw_day_dir."""

    name: str

    @abstractmethod
    def run(self, *, date_str: str, raw_day_dir: Path, config: dict[str, Any]) -> list[str]:
        """
        Perform gather; return list of filenames written (relative to raw_day_dir).
        """
