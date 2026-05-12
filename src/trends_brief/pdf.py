from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path


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
            "PDF command not set. Pass --pdf-cmd or set MD2PDF_CMD "
            '(e.g. \'md2pdf-mermaid {input} -o {output}\').'
        )
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    argv = render_pdf_command(template, md_path=md_path, pdf_path=pdf_path)
    subprocess.run(argv, check=True)
