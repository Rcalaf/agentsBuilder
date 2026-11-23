"""AgentsBuilder command-line interface. Phase 0 runs entirely from here (no UI)."""

import httpx
import psycopg
import typer

from agentsbuilder.config import Settings, get_settings

app = typer.Typer(help="AgentsBuilder development CLI.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """AgentsBuilder development CLI."""


def _ok(message: str) -> None:
    typer.echo(f"[ OK ] {message}")


def _fail(message: str) -> None:
    typer.echo(f"[FAIL] {message}")


def _auth_headers(settings: Settings) -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.llm_api_key.get_secret_value()}"}


def _check_database(settings: Settings) -> bool:
    try:
        with psycopg.connect(settings.database_url, connect_timeout=5) as conn:
            row = conn.execute(
                "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
            ).fetchone()
    except psycopg.Error as exc:
        _fail(f"database: {exc}")
        return False
    if row is None:
        _fail("database: connected, but the pgvector extension is not installed")
        return False
    _ok(f"database: connected, pgvector {row[0]}")
    return True


def _check_model_server(settings: Settings) -> bool:
    try:
        resp = httpx.get(
            f"{settings.llm_base_url}/models", headers=_auth_headers(settings), timeout=10
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        _fail(f"model server at {settings.llm_base_url}: {exc}")
        return False

    available = {model["id"] for model in resp.json().get("data", [])}
    _ok(f"model server: reachable, {len(available)} model(s) available")

    all_ok = True
    for label, name in (
        ("chat model", settings.chat_model),
        ("embedding model", settings.embedding_model),
    ):
        if not name:
            _fail(f"{label}: not set in .env")
            all_ok = False
        elif name in available or f"{name}:latest" in available:
            _ok(f"{label}: {name}")
        else:
            _fail(f"{label}: '{name}' not found on the server (pull it first)")
            all_ok = False
    return all_ok


def _check_embeddings(settings: Settings) -> bool:
    try:
        resp = httpx.post(
            f"{settings.llm_base_url}/embeddings",
            headers=_auth_headers(settings),
            json={"model": settings.embedding_model, "input": "Hola, món"},
            timeout=120,
        )
        resp.raise_for_status()
        dimension = len(resp.json()["data"][0]["embedding"])
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        _fail(f"embeddings: {exc}")
        return False
    _ok(f"embeddings: working, dimension {dimension}")
    return True


@app.command()
def doctor() -> None:
    """Check that the database, model server and models are reachable."""
    settings = get_settings()
    results = [
        _check_database(settings),
        _check_model_server(settings),
        _check_embeddings(settings),
    ]
    if not all(results):
        raise typer.Exit(code=1)
    typer.echo("Environment ready.")
