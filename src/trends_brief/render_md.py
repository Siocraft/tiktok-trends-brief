from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape


def _default_persona() -> dict[str, Any]:
    return {
        "niche_keywords": ["family", "mom life", "day in the life"],
        "persona_one_line": "Creator persona (edit config/persona.yaml).",
        "idea_templates": [
            "Hook in first 2s referencing {title}; show one specific moment from today.",
            "Pair {title} with a relatable caption about routines and small wins.",
        ],
    }


def load_persona(config_dir: Path) -> dict[str, Any]:
    base = _default_persona()
    local = config_dir / "persona.yaml"
    example = config_dir / "persona.example.yaml"
    path = local if local.is_file() else example
    if not path.is_file():
        return base
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return base
    merged = {**base, **data}
    if "niche_keywords" in data and isinstance(data["niche_keywords"], list):
        merged["niche_keywords"] = [str(x) for x in data["niche_keywords"]]
    if "idea_templates" in data and isinstance(data["idea_templates"], list):
        merged["idea_templates"] = [str(x) for x in data["idea_templates"]]
    return merged


def render_markdown(*, derived: dict[str, Any], persona: dict[str, Any]) -> str:
    env = Environment(
        loader=PackageLoader("trends_brief", "templates"),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.md.j2")
    return template.render(derived=derived, persona=persona, derived_json=json.dumps(derived, indent=2))


def write_report(content: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
