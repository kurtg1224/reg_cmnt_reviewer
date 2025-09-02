# SSA Regulation Comment Reviewer

This project processes public comments for SSA regulation proposals, detects redaction-required content, extracts short theme descriptions, and clusters themes to identify common issues.

## Features
- Task One: Detect content categories (A–D) requiring redaction via Azure OpenAI.
- Task Two: Extract short theme descriptions via Azure OpenAI.
- Multiprocessing orchestrator to process an input Excel file and produce an enriched Excel with results.
- Embedding-based clustering of themes using Azure OpenAI embeddings + HDBSCAN (with KMeans fallback) to determine common themes and counts.

## Requirements
- Python 3.10+
- See `requirements.txt` for Python dependencies.
- Azure OpenAI credentials

## Environment Variables (.env)
Create a `.env` file (or set env vars in your environment):

```
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT=your-gpt-deployment
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-embedding-deployment
```

## Usage
Install dependencies:

```bash
pip install -r requirements.txt
```

Process comments (Task One & Two) from an Excel file:

```bash
python main.py process \
  --input path/to/input.xlsx \
  --output path/to/comment_processing_results.xlsx \
  --text-column comment
```

... example:

```bash
python main.py process 
--input data/mock_comments.xlsx 
--output data/comment_processing_results.xlsx 
--text-column comment 
--processes 4
```

Cluster themes from the results file:

```bash
python main.py cluster \
  --input path/to/comment_processing_results.xlsx \
  --output path/to/theme_clusters.xlsx \
  --themes-column themes
```

## Notes
- Sensitive config is read from environment variables; do not hardcode secrets.
- Conforms to PEP-8 and uses retries for robustness.
- See `clustering_advice.md` for methodology background.

## DEPLOYMENT OPTIONS

The leanest way to share this internally is to distribute a Windows executable (EXE) with a separate `.env` file placed next to it. This avoids standing up cloud infra and is usually the most frictionless option in agency environments.

- EXE + `.env` (recommended for quick internal use)
  - Build a single EXE (e.g., PyInstaller) that launches the Streamlit app locally (http://127.0.0.1:8501).
  - Put a `.env` file next to the EXE containing Azure OpenAI settings (see `.env.example`). Secrets are NOT baked into the binary.
  - Users double-click the EXE, and the browser opens the app.

- Portable folder (no binary packing)
  - Ship the repo plus a pre-built `.venv` and a `run_app.bat` launcher. Users double-click the BAT.
  - Slightly larger download, but fewer packaging quirks than one-file EXEs.

- Cloud options (heavier)
  - EC2 + Nginx + systemd: straightforward to host for a small team; still needs patching/TLS/ops.
  - ECS Fargate + ALB: managed runtime, better for scaling/updates, but more setup.
  - We do not rely on Streamlit Cloud or Snowflake.

If Streamlit deployment is not ideal for your pipeline, we can convert this into a traditional web app (e.g., FastAPI + a minimal frontend) which may align better with agency DevSecOps tooling and change-management processes.

## TODO

- Re-enable the optional clustering feature in the UI.
- Test clustering end-to-end on realistic datasets.
- Package/bundle clustering so it’s available in EXE and cloud deployments (toggle via env flag like `DISABLE_CLUSTER=0`).
