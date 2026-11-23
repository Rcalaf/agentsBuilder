# AgentsBuilder

Background, decision rationale and roadmap: `docs/PROJECT_CONTEXT.md`. Read it before starting a
new build step or proposing a design change.

Platform for companies to build their own proprietary agentic systems (agents, RAG knowledge
bases, tools) for uses such as customer support, technical support and internal helpdesks.
Runs on open-weight models so clients don't pay per-token fees to commercial AI providers.

Product decisions already taken:
- Own core, built from scratch. Use mature libraries for commodity layers (parsing, storage,
  model serving), but the spec format, runtime loop, tool registry and evals are ours.
- Generic builder: use cases are templates (pre-filled agent specs), not separate products.
- Offered both as hosted SaaS and on-prem. Architecture: control plane (builder UI, spec
  registry, tenants, secrets) separate from data plane (runtime, knowledge, tools, model
  gateway, traces). The data plane must run anywhere: no SaaS-only dependencies.
- Python backend. FastAPI for the API (Phase 1). TypeScript/React only for the builder UI later.

## Current phase: Phase 0

Phase 0 is an experiment that answers one question: can open models on affordable hardware
run tool-using agents with RAG reliably enough for a client's live support channel?

In scope:
- Versioned agent spec (Pydantic model, exported as JSON Schema): instructions, model
  profile, knowledge base refs, tools, tool permissions (read vs write), escalation rules.
- Runtime that loads a spec and runs a conversation turn with retrieval and tool calls.
- One knowledge base: ingest documents, chunk, embed, store in pgvector, hybrid retrieval.
- One HTTP tool type, with validated arguments and retry on invalid tool calls.
- Traces of every turn (retrieval, model calls, tool calls, latency).
- Evaluation set and runner: tool-call validity, groundedness, latency, cost per conversation.
- Test in Catalan, Spanish and English. Compare at least two model sizes.

Out of scope for Phase 0 (do not build): web UI, authentication, multi-tenancy logic,
FastAPI server, multi-agent orchestration, channels (widget, Slack, email).

## Rules
- Every stored record and every trace carries a `tenant_id`, even though there is only one
  tenant now.
- The agent spec has a `spec_version` field. Changes to the spec format must be deliberate.
- Talk to models only through the OpenAI-compatible HTTP API (`AGENTSBUILDER_LLM_BASE_URL`), so
  Ollama and vLLM are interchangeable. No provider-specific SDKs in the runtime.
- Validate model output with Pydantic. Never trust a tool call's arguments unvalidated.
- Configuration comes from `agentsbuilder.config.Settings` (env vars prefixed `AGENTSBUILDER_`). No hard-coded
  URLs, model names or credentials.
- Keep functions small and typed. Add tests in `tests/` for new behaviour.
- Do not change the developer's Node.js or npm installation. This project needs neither.

## Environment
- Python 3.12 comes from the conda env `agentsbuilder`. uv is installed inside that env and
  manages `.venv` and `uv.lock`. The env sets `UV_PYTHON_DOWNLOADS=never`: uv must use conda's
  Python, never a downloaded one.
- The env activates automatically on `cd` into the project (`.conda-env` + a zsh hook in
  `~/.zshrc`). In a non-interactive shell where it isn't active, call
  `/opt/anaconda3/envs/agentsbuilder/bin/uv` directly.
- Add packages with `uv add`, never `pip install` into the conda env.
- The app runs locally from `.venv`. Docker is only for the development Postgres; do not
  containerize the app.

## Commands
- `uv sync` install dependencies (`uv sync --extra ingest` for document parsing)
- `docker compose up -d` start Postgres + pgvector (host port 5433; Docker Desktop must be running)
- `uv run agentsbuilder doctor` verify database, model server and models
- `uv run pytest` run tests
- `uv run ruff check . && uv run ruff format .` lint and format

## Layout
- `src/agentsbuilder/config.py` settings
- `src/agentsbuilder/cli.py` CLI entry point (`agentsbuilder`)
- `db/init.sql` database initialisation (pgvector extension)
- `tests/` tests

Planned modules (create when needed): `spec/`, `runtime/`, `knowledge/`, `tools/`,
`tracing/`, `evals/` under `src/agentsbuilder/`.

## Open questions (do not assume answers)
- Hardware for model serving, which decides which chat models to test.
- Real document set and API to test against.
- Exit-criteria thresholds for Phase 0.
