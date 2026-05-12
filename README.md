# trends-brief

Local **Python 3** pipeline for a daily-style trend brief: **gather → Markdown → optional PDF**. No database; outputs live under `data/` and `reports/`. Intended for development under the [**siocraft**](https://github.com/siocraft) GitHub organization (create the remote repo and push this project when ready).

## Requirements

- macOS (or any OS with Python **3.11+**)
- Optional: [md2pdf-mermaid](https://www.npmjs.com/package/md2pdf-mermaid) or another Markdown-to-PDF CLI

## Setup

```bash
cd /path/to/tiktok
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Copy examples and customize:

```bash
cp config/persona.example.yaml config/persona.yaml
cp config/sources.example.yaml config/sources.yaml
```

Edit `config/sources.yaml` to enable adapters (e.g. `http_json` with a URL you are allowed to call).

## Run the pipeline

From the repo root:

```bash
source .venv/bin/activate
python3 scripts/run_pipeline.py --skip-pdf
```

Options:

| Flag | Meaning |
|------|--------|
| `--date YYYY-MM-DD` | Report date (default: today) |
| `--skip-pdf` | Stop after writing Markdown |
| `--pdf-cmd '...'` | PDF command template; use `{input}` and `{output}` placeholders |
| `--pdf-optional` | If PDF fails, print a warning and exit successfully |
| `--sources PATH` | Override sources YAML |

PDF command is read from `--pdf-cmd` or the **`MD2PDF_CMD`** environment variable. Example (adjust to match your installed CLI):

```bash
export MD2PDF_CMD='md2pdf-mermaid {input} -o {output}'
python3 scripts/run_pipeline.py
```

If the tool uses different flags, set `MD2PDF_CMD` accordingly.

## Outputs

| Path | Description |
|------|-------------|
| `data/raw/<DATE>/` | Raw JSON per adapter |
| `data/derived/<DATE>.json` | Merged normalized brief |
| `reports/<DATE>.md` | Human-readable report |
| `reports/pdf/<DATE>.pdf` | Created when PDF step runs |

## Smoke check

```bash
python -m trends_brief
```

Runs a temporary pipeline with stub data (no PDF).

## GitHub (siocraft)

1. Create a repository under `https://github.com/siocraft` (for example `tiktok-trends-brief`).
2. Add the remote and push (do not commit `config/persona.yaml`, `config/sources.yaml`, or `.env` — they are gitignored).

```bash
git init
git remote add origin git@github.com:siocraft/<repo-name>.git
git add .
git commit -m "Initial trends-brief pipeline"
git push -u origin main
```

## License

Add a `LICENSE` file when you publish under the organization.
