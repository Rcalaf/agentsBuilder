# AgentsBuilder: project context

This document hands the project over from the planning conversation (in Claude chat) to
development in Claude Code. `CLAUDE.md` holds the rules to follow day to day; this file explains
what the product is, why each decision was taken, and what comes next.

## 1. The product

AgentsBuilder is a web platform that lets companies, mainly small and medium-sized ones, create
their own proprietary agentic systems: agents with their own knowledge bases (RAG) and their own
tools, connected to the company's systems. The agents serve purposes such as customer support,
technical support and internal helpdesks.

Value proposition:
- Runs on open-weight models, so clients don't pay per-token fees to commercial AI providers.
- Can run on the client's own infrastructure (on-prem), so data doesn't have to leave it.
- Clients own the agents they build.

Project owner: Roger Calaf. He works in Catalan, Spanish and English; the target market is
expected to include all three, so the product must work well in each.

## 2. Decisions taken, and why

| Decision | Reason |
|---|---|
| Own core, built from scratch | Full control of the spec format, runtime and licensing. Existing platforms (Dify, Flowise, Langflow, n8n) were considered; some have licence limits on multi-tenant SaaS use. |
| Generic builder from day one | Use cases are templates (pre-filled agent specs), not separate products. To keep this sellable, the core is generic but ships with concrete templates. |
| Both hosted SaaS and on-prem | Forces the control plane / data plane split (section 3). |
| Python backend | The RAG, document parsing and evaluation ecosystem is Python-first. |
| API framework | FastAPI was recommended (async streaming, shared Pydantic models, generated OpenAPI docs). Roger said Flask or another framework could be used. **Not yet confirmed.** Only needed from Phase 1. |
| Builder UI in TypeScript/React | Recommended for Phase 1+. Not part of Phase 0. |
| Name: AgentsBuilder | Chosen by Roger over a metaphoric name. Note: close to OpenAI's "Agent Builder"; trademark and domain availability not yet checked. |
| conda + uv, Python 3.12, Postgres + pgvector, Ollama | Development environment. conda provides Python 3.12 (Roger's standard Python manager across projects); uv, installed inside the conda env, manages the project's packages, `.venv` and `uv.lock`. uv alone was considered and would also work; conda was kept for consistency with Roger's other projects. `UV_PYTHON_DOWNLOADS=never` is set in the conda env. Node.js is not involved. |
| App runs locally; Docker only for the dev database | The app runs from `.venv` on the developer's machine. Docker Compose runs only Postgres + pgvector for development. Containerizing the app is deferred (on-prem packaging is Phase 2). |

## 3. Architecture

The central idea: **an agent is a declarative, versioned spec**, and a runtime interprets it. The
builder UI is only an editor for specs. This gives templates, versioning, rollback, evaluation
per spec version, and portability between SaaS and on-prem.

**Control plane** (Phase 1+): builder UI, spec registry, tenants, roles, secrets, API.

**Data plane** (Phase 0 starts here): agent runtime, knowledge (ingestion, embeddings,
retrieval), tools, model gateway, traces and evals. Deployable anywhere as containers, with no
dependency on Encert-hosted services.

What we build ourselves: spec format, runtime loop, tool registry, control plane, evaluation
harness.

What we reuse:
- Document parsing: Docling (optional `ingest` extra, heavy dependency)
- Storage and vector search: Postgres + pgvector
- Model serving: Ollama for development, vLLM for production, both through their
  OpenAI-compatible HTTP API
- Embeddings: bge-m3 (multilingual), served by the same model server
- Tracing: own traces first; OpenTelemetry/Langfuse considered for later

## 4. Roadmap

- **Phase 0, runtime experiment (current):** spec, runtime, one knowledge base, one HTTP tool,
  local model, traces, evaluation. CLI only.
- **Phase 1, control plane:** multi-tenancy, secrets, spec editor UI, API.
- **Phase 2:** evaluation sets in the product, web chat widget, MCP/OpenAPI tool import,
  on-prem packaging (Docker Compose, later Helm).
- **Phase 3:** multi-agent orchestration, template library, more channels (Slack/Teams, email,
  WhatsApp).

## 5. Phase 0 in detail

**The question Phase 0 answers:** can open-weight models, on hardware an SMB or Encert can
afford, run tool-using agents with RAG reliably enough for a client's live support channel? If
not, the positioning changes (for example, open models for most traffic plus a commercial API for
hard cases). Phase 0 is an experiment with measurable results, not a demo.

**Metrics (thresholds still to be set by Roger, from what a client would accept):**
- Tool-call validity: well-formed calls with correct arguments
- Groundedness: answers supported by retrieved sources, with citations
- Latency per turn
- Cost per conversation on the target hardware

Also: compare at least two model sizes (the useful output is the quality-versus-cost curve), and
test in Catalan, Spanish and English.

**Proposed build order** (a suggestion, adjust if needed):
1. Agent spec as Pydantic models with `spec_version`, exported as JSON Schema; load from YAML.
2. Model client over the OpenAI-compatible API: chat, tool calling, embeddings.
3. Knowledge: database schema (with `tenant_id`), chunking, embedding, storage, hybrid retrieval
   (pgvector similarity + Postgres full-text search).
4. HTTP tool type: definition in the spec, Pydantic-validated arguments, read/write permission.
5. Runtime loop: retrieve, call model, validate tool calls, retry on invalid calls, execute tools,
   answer with citations.
6. Traces for every step.
7. Evaluation set format and runner reporting the four metrics.
8. CLI commands for each of the above (`ingest`, `chat`, `eval`).

**Known risks:**
- Tool calling is less reliable with open models. Mitigate with constrained decoding (JSON schema
  enforcement where the server supports it), validation and retry.
- Prompt injection: text in retrieved documents or tool outputs may try to trigger tools. Write
  actions need explicit permission in the spec, optionally with human confirmation.
- Scope creep: Phase 0 must not grow a UI, login or extra tool types unless an eval result
  requires it.

## 6. Current state

- Project skeleton exists: configuration (`config.py`), CLI with a `doctor` command that checks
  the database, model server, models and embeddings, two tests, Docker Compose for Postgres.
- Development environment set up and verified on Roger's machine (Apple M4, 16 GB RAM) on
  2026-11-23: conda env `agentsbuilder` (Python 3.12.16, uv 0.13.9), `uv sync` with `uv.lock`,
  tests pass (2/2), ruff clean, and `doctor` passes against live services (Postgres with
  pgvector 0.8.7, Ollama, `bge-m3` embeddings at dimension 1024).
- `AGENTSBUILDER_CHAT_MODEL=qwen3:8b` in the local `.env`, as the first development model. The
  development machine is not necessarily the target hardware; that question stays open
  (section 7).

## 7. Open questions (ask, don't assume)

- Hardware for model serving (GPU and VRAM, or Apple Silicon and RAM). Decides which chat models
  to test and the cost figures.
- A real document set and API to test against.
- Phase 0 exit-criteria thresholds.
- API framework for Phase 1 (FastAPI recommended, not confirmed).
- Whether AgentsBuilder is an Encert Predict product or an independent / open-source project.
  This affects licensing and repository ownership.
- Name availability (trademark, domain, PyPI).

## 8. Working with Roger

- Never fabricate or fill gaps. If information is missing, say so and ask for the specific
  detail.
- Explain what you change and why; Roger reviews code before using it.
- For documents, he prefers a list of changes to apply over a full rewrite.
- Never require updating Node.js or npm. This project doesn't use them, and other projects on
  his machine depend on the current versions.
- Work in small, verifiable steps: each step should end with passing tests and a command he can
  run to see it working.
