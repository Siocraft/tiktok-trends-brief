from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path


def default_pdf_command() -> str | None:
    """
    When the PyPI package ``md2pdf-mermaid`` is installed, it exposes the ``md2pdf`` CLI.

    Returns a template using ``{input}`` and ``{output}``, or None if ``md2pdf`` is not on PATH.
    """
    if shutil.which("md2pdf"):
        return "md2pdf {input} -o {output}"
    return None


def render_pdf_command(template: str, *, md_path: Path, pdf_path: Path) -> list[str]:
    """
    Build argv from a template string.

    Placeholders: {input}, {output} (absolute paths as strings).
    If template is a single token with no braces, treat as executable name
    and use default: exe {input} -o {output}
    """
    ctx = {"input": str(md_path.resolve()), "output": str(pdf_path.resolve())}
    if "{" not in template:
        return [template, ctx["input"], "-o", ctx["output"]]
    try:
        rendered = template.format(**ctx)
    except KeyError as e:
        raise ValueError(f"pdf command template must use {{input}} and {{output}} only; missing {e}") from e
    return shlex.split(rendered)


def run_pdf(*, md_path: Path, pdf_path: Path, cmd_template: str | None) -> None:
    template = cmd_template or os.environ.get("MD2PDF_CMD", "").strip()
    if not template:
        raise ValueError(
            "PDF command not set. Pass --pdf-cmd or set MD2PDF_CMD, "
            'or install PDF support: pip install -e ".[pdf]" then playwright install chromium '
            "(adds the md2pdf CLI from md2pdf-mermaid)."
        )
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    argv = render_pdf_command(template, md_path=md_path, pdf_path=pdf_path)
    subprocess.run(argv, check=True)
