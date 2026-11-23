# AgentsBuilder

Build your own agentic systems (agents, RAG, tools) on open models.

## Prerequisites
- [conda](https://docs.conda.io/) (Anaconda or Miniconda): provides Python 3.12
- [uv](https://docs.astral.sh/uv/), installed inside the conda env: manages the project's
  packages, `.venv` and `uv.lock` (tested with uv 0.13.9)
- Docker, for the development database only (Postgres + pgvector). The app itself runs
  locally, not in a container.
- [Ollama](https://ollama.com) installed natively, so it can use your GPU / Apple Silicon
- VS Code and Claude Code

Node.js is not required.

### How the Python environment is layered
```
conda env "agentsbuilder"     → Python 3.12 + the uv tool
   └─ .venv/ (project folder) → created by uv from that Python; holds the project's packages
        └─ uv.lock            → exact versions installed in .venv
```
Add project packages with `uv add <package>`, never with `pip install` into the conda env.
The conda env sets `UV_PYTHON_DOWNLOADS=never`, so uv always uses conda's Python and never
downloads its own.

## Setup
```bash
# Python: conda env with Python 3.12, uv inside it, uv never downloads Python
conda create -n agentsbuilder python=3.12
conda activate agentsbuilder
pip install uv
conda env config vars set UV_PYTHON_DOWNLOADS=never -n agentsbuilder
conda activate agentsbuilder    # re-activate so the variable takes effect

cp .env.example .env            # then set AGENTSBUILDER_CHAT_MODEL
docker compose up -d            # Postgres + pgvector on localhost:5433 (Docker Desktop must be running)
ollama pull bge-m3              # embedding model
ollama pull <chat-model>        # the model set in AGENTSBUILDER_CHAT_MODEL
uv sync                         # creates .venv from the conda Python and installs dependencies
uv run agentsbuilder doctor     # checks database, model server, models, embeddings
uv run pytest
```

### Automatic activation (optional)
The `.conda-env` file in the project root names the conda env (`agentsbuilder`). With a small
zsh `chpwd` hook in `~/.zshrc` that reads this file, the env activates when you `cd` into the
project (or any subfolder) and deactivates when you leave. Without the hook, run
`conda activate agentsbuilder` yourself.

## Working with VS Code and Claude Code
Open the folder with `code .`, install the recommended extensions, and select the `.venv`
interpreter if VS Code doesn't pick it up. On native Windows, change
`python.defaultInterpreterPath` in `.vscode/settings.json` to `.venv\Scripts\python.exe`.

Run `claude` from the project root. Claude Code reads `CLAUDE.md` for project context.
