from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trends_brief.gather.base import GatherAdapter


class StubAdapter(GatherAdapter):
    """Deterministic sample data for local testing without network."""

    name = "stub"

    def run(self, *, date_str: str, raw_day_dir: Path, config: dict[str, Any]) -> list[str]:
        raw_day_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "source": self.name,
            "date": date_str,
            "trends": [
                {
                    "title": "#MorningRoutine",
                    "type": "hashtag",
                    "score": 0.92,
                    "notes": "Sample stub entry for pipeline smoke tests.",
                    "links": ["https://www.tiktok.com/tag/morningroutine"],
                },
                {
                    "title": "POV: toddler discovers the camera",
                    "type": "format",
                    "score": 0.88,
                    "notes": "Relatable family hook; pair with a fast cut intro.",
                    "links": [],
                },
                {
                    "title": "Soft-launch life update",
                    "type": "topic",
                    "score": 0.74,
                    "notes": "Low-key announcement style trending in lifestyle niches.",
                    "links": [],
                },
            ],
        }
        out = raw_day_dir / "stub.json"
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return [out.name]
