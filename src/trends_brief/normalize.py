from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _normalize_trend_item(item: Any, default_source: str) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    title = item.get("title")
    if not isinstance(title, str) or not title.strip():
        return None
    t_type = item.get("type")
    if not isinstance(t_type, str):
        t_type = "topic"
    score = item.get("score")
    if isinstance(score, (int, float)):
        score_f = float(score)
    else:
        score_f = 0.5
    notes = item.get("notes")
    if not isinstance(notes, str):
        notes = ""
    links = item.get("links")
    if isinstance(links, list):
        links_out = [str(x) for x in links if x]
    else:
        links_out = []
    return {
        "title": title.strip(),
        "type": t_type,
        "score": score_f,
        "notes": notes,
        "links": links_out,
        "source": item.get("source") or default_source,
    }


def _trends_from_doc(data: dict[str, Any], filename: str) -> list[dict[str, Any]]:
    source = str(data.get("source") or filename)
    out: list[dict[str, Any]] = []
    trends = data.get("trends")
    if isinstance(trends, list):
        for item in trends:
            norm = _normalize_trend_item(item, source)
            if norm:
                out.append(norm)
        return out
    if "title" in data and isinstance(data.get("title"), str):
        norm = _normalize_trend_item(data, source)
        if norm:
            out.append(norm)
        return out
    preview = json.dumps(data, indent=2)[:800]
    out.append(
        {
            "title": f"Unstructured snapshot: {filename}",
            "type": "topic",
            "score": 0.1,
            "notes": preview,
            "links": [],
            "source": source,
        }
    )
    return out


def build_derived(*, date_str: str, raw_day_dir: Path) -> dict[str, Any]:
    if not raw_day_dir.is_dir():
        raise FileNotFoundError(f"Raw day directory missing: {raw_day_dir}")

    merged: list[dict[str, Any]] = []
    sources_seen: list[str] = []

    for path in sorted(raw_day_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            data: dict[str, Any] = {"source": path.stem, "trends": raw}
        elif isinstance(raw, dict):
            data = raw
        else:
            continue
        src = str(data.get("source") or path.stem)
        if src not in sources_seen:
            sources_seen.append(src)
        merged.extend(_trends_from_doc(data, path.name))

    dedup: dict[tuple[str, str], dict[str, Any]] = {}
    for t in merged:
        key = (t["title"].lower(), t["type"].lower())
        existing = dedup.get(key)
        if existing is None or t["score"] > existing["score"]:
            dedup[key] = t

    trends_sorted = sorted(dedup.values(), key=lambda x: x["score"], reverse=True)
    for t in trends_sorted:
        t.pop("source", None)

    return {
        "date": date_str,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "sources": sorted(set(sources_seen)),
        "trends": trends_sorted,
    }


def write_derived(derived: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(derived, indent=2) + "\n", encoding="utf-8")
