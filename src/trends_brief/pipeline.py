from __future__ import annotations

from pathlib import Path

from trends_brief.gather import get_adapter
from trends_brief.normalize import build_derived, write_derived
from trends_brief.paths import ProjectPaths
from trends_brief.pdf import run_pdf
from trends_brief.render_md import load_persona, render_markdown, write_report


def _rel_under(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _print_summary(
    *,
    root: Path,
    paths: ProjectPaths,
    date_str: str,
    md_path: Path,
    quiet: bool,
    pdf_path: Path | None,
    pdf_skipped_reason: str | None,
) -> None:
    if quiet:
        return
    print(f"Pipeline done — {date_str}")
    print(f"  Raw:     {_rel_under(root, paths.raw_day(date_str))}")
    print(f"  Derived: {_rel_under(root, paths.derived_file(date_str))}")
    print(f"  Report:  {_rel_under(root, md_path)}")
    if pdf_path is not None:
        print(f"  PDF:     {_rel_under(root, pdf_path)}")
    elif pdf_skipped_reason:
        print(f"  PDF:     ({pdf_skipped_reason})")
    else:
        print("  PDF:     (skipped)")


def load_sources_config(path: Path) -> list[dict]:
    if not path.is_file():
        return [{"name": "stub", "enabled": True, "config": {}}]
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    adapters = data.get("adapters")
    if not isinstance(adapters, list):
        return [{"name": "stub", "enabled": True, "config": {}}]
    out: list[dict] = []
    for item in adapters:
        if isinstance(item, dict) and item.get("name"):
            out.append(item)
    return out or [{"name": "stub", "enabled": True, "config": {}}]


def run_gather(*, date_str: str, raw_day_dir: Path, sources_config_path: Path) -> None:
    raw_day_dir.mkdir(parents=True, exist_ok=True)
    for entry in load_sources_config(sources_config_path):
        if not entry.get("enabled", True):
            continue
        name = str(entry["name"])
        cfg = entry.get("config") or {}
        if not isinstance(cfg, dict):
            cfg = {}
        try:
            adapter = get_adapter(name)
        except KeyError as e:
            raise ValueError(f"Unknown adapter {name!r}. See config/sources.example.yaml.") from e
        adapter.run(date_str=date_str, raw_day_dir=raw_day_dir, config=cfg)


def run_pipeline(
    *,
    root: Path,
    date_str: str,
    skip_pdf: bool,
    pdf_optional: bool,
    pdf_cmd: str | None,
    sources_path: Path,
    quiet: bool = False,
) -> None:
    paths = ProjectPaths(root)
    raw_day = paths.raw_day(date_str)
    run_gather(date_str=date_str, raw_day_dir=raw_day, sources_config_path=sources_path)

    derived = build_derived(date_str=date_str, raw_day_dir=raw_day)
    write_derived(derived, paths.derived_file(date_str))

    persona = load_persona(paths.config_dir)
    md_content = render_markdown(derived=derived, persona=persona)
    md_path = paths.report_md(date_str)
    write_report(md_content, md_path)

    if skip_pdf:
        _print_summary(
            root=root,
            paths=paths,
            date_str=date_str,
            md_path=md_path,
            quiet=quiet,
            pdf_path=None,
            pdf_skipped_reason="not generated",
        )
        return
    pdf_path = paths.report_pdf(date_str)
    try:
        run_pdf(md_path=md_path, pdf_path=pdf_path, cmd_template=pdf_cmd)
    except Exception as exc:
        if pdf_optional:
            import sys

            print(f"Warning: PDF step failed ({exc}). Markdown saved at {md_path}.", file=sys.stderr)
            _print_summary(
                root=root,
                paths=paths,
                date_str=date_str,
                md_path=md_path,
                quiet=quiet,
                pdf_path=None,
                pdf_skipped_reason="not generated (PDF step failed)",
            )
            return
        raise
    _print_summary(
        root=root,
        paths=paths,
        date_str=date_str,
        md_path=md_path,
        quiet=quiet,
        pdf_path=pdf_path,
        pdf_skipped_reason=None,
    )
