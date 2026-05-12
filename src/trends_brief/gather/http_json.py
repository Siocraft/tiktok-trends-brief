from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from trends_brief.gather.base import GatherAdapter


class HttpJsonAdapter(GatherAdapter):
    """
    GET a URL and save JSON response to raw_day_dir.

    Config keys:
      url: str (required)
      out_filename: str (default "http_json.json")
      timeout_seconds: float (default 30)
    """

    name = "http_json"

    def run(self, *, date_str: str, raw_day_dir: Path, config: dict[str, Any]) -> list[str]:
        url = config.get("url")
        if not url or not isinstance(url, str):
            raise ValueError("http_json adapter requires config.url (string)")
        out_name = config.get("out_filename") or "http_json.json"
        if not isinstance(out_name, str):
            raise ValueError("out_filename must be a string")
        timeout = float(config.get("timeout_seconds") or 30)
        raw_day_dir.mkdir(parents=True, exist_ok=True)
        out_path = raw_day_dir / out_name

        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            body = response.text
        try:
            parsed = json.loads(body)
            body_out = json.dumps(parsed, indent=2) + "\n"
        except json.JSONDecodeError:
            wrapped = {"source": self.name, "url": url, "date": date_str, "raw_text": body}
            body_out = json.dumps(wrapped, indent=2) + "\n"

        out_path.write_text(body_out, encoding="utf-8")
        return [out_path.name]
