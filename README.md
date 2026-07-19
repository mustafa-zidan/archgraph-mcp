# ArchGraph MCP

[![Tests](https://github.com/mustafa-zidan/archgraph-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/mustafa-zidan/archgraph-mcp/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/archgraph-mcp.svg)](https://pypi.org/project/archgraph-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/archgraph-mcp.svg)](https://pypi.org/project/archgraph-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ArchGraph MCP turns a repository into a queryable graph. It parses TypeScript, Java, and Kotlin source with
[Tree-sitter](https://tree-sitter.github.io/), builds a directed graph of files, symbols, and dependencies, and exposes
that graph to AI coding agents over the [Model Context Protocol](https://modelcontextprotocol.io/). Instead of grepping
for call sites, an agent can ask what a function depends on, what breaks if it changes, or how two nodes connect.

## How a repository becomes a queryable graph

```
Repository
   ↓
File Scanner (lazy, generator-based)
   ↓
Parser Layer (Tree-sitter: TypeScript, Java, Kotlin)
   ↓
Graph Builder (NetworkX DiGraph)
   ↓
Kuzu Storage (embedded graph DB + full-text search)
   ↓
Query Engine (BFS, shortest path, impact analysis)
   ↓
MCP Server (FastMCP: stdio, sse, or streamable-http transport)
   ↓
AI Agent (Cursor, Windsurf, Claude Code, etc.)
```

The graph itself lives in **NetworkX** at query time; traversals (BFS, shortest path, impact analysis) run in memory
against that structure. **Kuzu**'s job is persistence and lexical search: it stores nodes and edges across restarts and
powers BM25-style `search_nodes`, falling back to substring matching when full-text search finds nothing. Semantic
search is a separate, optional layer: embedding vectors live in NumPy files next to the Kuzu path rather than inside the
graph database itself.

## Documentation

This README covers installation, usage, and the reference tables. Three guides go deeper:

- [Setup and MCP](docs/setup-and-mcp.md): install, first-time analyze, environment variables, stdio vs HTTP, Claude
  Desktop, Cursor, VS Code, remote URLs, Docker, troubleshooting.
- [Local build and semantic](docs/local-build-and-semantic.md): developing from a clone, `analyze --semantic-index`,
  embedding backends, and serving with the vector index.
- [Release cycle](docs/release-cycle.md): versioning and PyPI releases for maintainers.

## Installing it

`uvx archgraph-mcp` works once the package is on PyPI. Until the first release ships, install from a clone.

### From PyPI, with uvx

[`uvx`](https://docs.astral.sh/uv/guides/tools/) runs the published tool in an isolated environment, no global install
needed:

```bash
uvx archgraph-mcp --help
```

The optional **`[semantic]`** extra pulls in NumPy for `search_nodes_semantic` and the vector index. Pass it with
`--with` so the tool environment includes it:

```bash
uvx --with "archgraph-mcp[semantic]" archgraph-mcp --help
```

### From a git clone

```bash
git clone https://github.com/mustafa-zidan/archgraph-mcp.git
cd archgraph-mcp
uv sync --extra dev --extra semantic
uv run archgraph-mcp --help
```

Drop `--extra semantic` if you don't need vector search; the core graph and full-text search work without it.

## Analyzing and serving a repository

Examples below use `uvx` (PyPI). From a clone, replace `uvx …` with `uv run …`.

### Analyze

```bash
uvx archgraph-mcp analyze ./your-repo
```

This scans the repo, parses it, and writes a Kuzu database (`archgraph.kuzu` by default). Add `--semantic-index` to also
build the vector index, which needs `[semantic]` in the environment:

```bash
uvx --with "archgraph-mcp[semantic]" archgraph-mcp analyze ./your-repo --semantic-index
```

### Serve over stdio (local)

Most desktop agents spawn the process and talk over stdin/stdout:

```bash
uvx archgraph-mcp serve ./your-repo
```

With semantic tooling available to the server process:

```bash
uvx --with "archgraph-mcp[semantic]" archgraph-mcp serve ./your-repo
```

### Serve over HTTP (remote)

```bash
uvx archgraph-mcp serve ./your-repo --transport streamable-http --port 3847
```

### Graph viewer (HTTP transports only)

`--graph-ui` (or `GRAPH_UI=1`) exposes a [vis-network](https://visjs.github.io/vis-network/docs/network/) view at
`/graph` and raw JSON at `/api/graph` (optional `limit` query param, default `500`, caps node count for responsiveness).
It's ignored under `stdio`, since there's no HTTP server to attach it to.

```bash
uvx archgraph-mcp serve ./your-repo --transport streamable-http --port 3847 --graph-ui
```

## Wiring it into an MCP client

Full walkthroughs for Claude Desktop, Cursor, VS Code, and remote URLs are in
[docs/setup-and-mcp.md](docs/setup-and-mcp.md). Quick reference below; it requires `uv` on `PATH` so `uvx` resolves.

**Core** (lexical `search_nodes` only):

```json
{
  "mcpServers": {
    "archgraph": {
      "command": "uvx",
      "args": [
        "archgraph-mcp",
        "serve",
        "/absolute/path/to/your/repo"
      ]
    }
  }
}
```

**With `[semantic]`** (NumPy + `search_nodes_semantic`, once an index exists):

```json
{
  "mcpServers": {
    "archgraph": {
      "command": "uvx",
      "args": [
        "--with",
        "archgraph-mcp[semantic]",
        "archgraph-mcp",
        "serve",
        "/absolute/path/to/your/repo"
      ]
    }
  }
}
```

**From a git clone** (before a PyPI release, or for development):

```json
{
  "mcpServers": {
    "archgraph": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/archgraph-mcp",
        "archgraph-mcp",
        "serve",
        "/absolute/path/to/your/repo"
      ]
    }
  }
}
```

Run `uv sync --extra dev --extra semantic` in that clone before starting the MCP client.

Optional env, e.g. a custom Kuzu path:

```json
{
  "mcpServers": {
    "archgraph": {
      "command": "uvx",
      "args": ["archgraph-mcp", "serve", "/path/to/repo"],
      "env": {
        "ARCHGRAPH_STORE": "/path/to/repo/.archgraph/archgraph.kuzu"
      }
    }
  }
}
```

**Remote server** (streamable-http / SSE):

```json
{
  "mcpServers": {
    "archgraph": {
      "url": "http://your-server:3847/mcp"
    }
  }
}
```

Start the process itself with `uvx archgraph-mcp serve /repo --transport streamable-http --port 3847` (Docker
instructions below).

## The tools it exposes

| Tool                    | Description                                       |
| ----------------------- | ------------------------------------------------- |
| `search_nodes`          | Lexical search (FTS + substring fallback) by type |
| `search_nodes_semantic` | Cosine similarity (requires `[semantic]` + index) |
| `trace_dependencies`    | What does this node depend on?                    |
| `trace_dependents`      | What depends on this node?                        |
| `impact_analysis`       | What breaks if this node changes?                 |
| `trace_path`            | Shortest path between two nodes                   |
| `architecture_summary`  | High-level graph summary                          |

Node ids follow a `type:identifier` shape, e.g. `function:auth.loginUser` or `file:src/auth.ts`. Run `search_nodes`
first if you don't know the exact id.

```
search_nodes(query="login", node_type="function")
impact_analysis(node_id="function:auth.loginUser")
trace_path(source_id="file:src/auth.ts", target_id="database:users")
architecture_summary()
```

## Semantic search

Lexical search (`search_nodes`) matches names and text. Semantic search (`search_nodes_semantic`) matches meaning, at
the cost of an embedding backend and a build step.

1. Install `[semantic]` into the tool environment:
   `uvx --with "archgraph-mcp[semantic]" archgraph-mcp analyze ./repo --semantic-index` (or `uv sync --extra semantic`
   from a clone).
2. Pick a backend via `ARCHGRAPH_EMBED_BACKEND`:
   - `openai` (default): `POST {OPENAI_BASE_URL}/v1/embeddings`. Works against LM Studio, Ollama's OpenAI-compatible
     mode, or OpenAI itself.
   - `local`: in-process models via `sentence-transformers`, installed separately (
     `pip install sentence-transformers`).
3. Build the index during analyze, with the flag or the env var: `archgraph-mcp analyze ./repo --semantic-index` or
   `ARCHGRAPH_BUILD_SEMANTIC_INDEX=1`. This writes `archgraph.vectors.npz` and `archgraph.embeddings.json` next to the
   Kuzu file (`--store` / `ARCHGRAPH_STORE`).

| Variable                      | Purpose                                                                                                                                                                                                          |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ARCHGRAPH_EMBED_BACKEND`     | `openai` or `local`                                                                                                                                                                                              |
| `ARCHGRAPH_EMBED_BATCH_SIZE`  | OpenAI HTTP backend: inputs per request (default `64`). If the server returns fewer vectors than inputs, the client retries one string per request automatically; set `1` to skip the slow failed-batch attempt. |
| `OPENAI_BASE_URL`             | e.g. `http://127.0.0.1:1234/v1` for LM Studio                                                                                                                                                                    |
| `OPENAI_API_KEY`              | Bearer token (dummy value is fine if the server ignores it)                                                                                                                                                      |
| `OPENAI_EMBEDDING_MODEL`      | Model id for `/v1/embeddings`                                                                                                                                                                                    |
| `ARCHGRAPH_LOCAL_EMBED_MODEL` | Sentence-transformers model id when backend is `local`                                                                                                                                                           |

The index build and the query-time call must agree on backend and model; a mismatch produces vectors that don't line up,
not an error.

## Supported languages

- TypeScript / TSX
- Java
- Kotlin (`.kt`, `.kts`)

## Running it as a service

### Docker

```bash
docker build -t archgraph-mcp .
docker run -p 3847:3847 -v /path/to/repo:/repo archgraph-mcp
```

### Railway

1. Connect the GitHub repo at [railway.app](https://railway.app).
2. Set the environment variable `REPO_PATH=/repo`.
3. Deploy; Railway picks up `railway.json` automatically.

### Fly.io

```bash
fly launch
fly deploy
```

## Environment variables

| Variable                         | Default          | Description                                                                                          |
| -------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------- |
| `REPO_PATH`                      | `.`              | Path to the repository to analyze                                                                    |
| `ARCHGRAPH_STORE`                | `archgraph.kuzu` | Kuzu database path (overrides the default when the CLI does not pass `--store`)                      |
| `PORT`                           | `3847`           | Port for SSE transport                                                                               |
| `MCP_TRANSPORT`                  | `stdio`          | Transport mode: `stdio`, `sse`, or `streamable-http`                                                 |
| `GRAPH_UI`                       | unset            | Set to `1` / `true` to enable `/graph` and `/api/graph` (same as `--graph-ui`; HTTP transports only) |
| `ARCHGRAPH_BUILD_SEMANTIC_INDEX` | unset            | Set to `1` / `true` to build the vector index when serving triggers a full analyze (optional)        |

## Developing on it

```bash
uv sync --extra dev
# or: pip install -e ".[dev]"
```

Lint and format:

```bash
ruff check src tests
ruff format src tests
```

Markdown (see [`.mdformat.toml`](.mdformat.toml); [GFM](https://github.github.com/gfm/) tables and wrapping):

```bash
mdformat README.md CHANGELOG.md docs/
mdformat --check README.md CHANGELOG.md docs/
```

Static typing:

```bash
mypy src
```

Tests:

```bash
pytest tests/ -v
```

Optional [pre-commit](https://pre-commit.com/) hooks run Ruff lint and format on commit:

```bash
pip install pre-commit
pre-commit install
```

## Releasing to PyPI

[`.github/workflows/test.yml`](.github/workflows/test.yml) runs on every push and PR to `main`, `master`, or `develop`:
`uv sync --extra dev`, Ruff, mdformat, mypy, and pytest, across Ubuntu, macOS, and Windows on Python 3.12, 3.13, and
3.14.

[`.github/workflows/release.yml`](.github/workflows/release.yml) is manual (`workflow_dispatch`) and publishes to
[PyPI](https://pypi.org/p/archgraph-mcp) via [trusted publishing](https://docs.pypi.org/trusted-publishers/) (OIDC, no
long-lived token). To cut a release:

1. Bump `version` in [`pyproject.toml`](pyproject.toml) and add a matching section to [`CHANGELOG.md`](CHANGELOG.md),
   then merge to the default branch.
2. One-time setup: on PyPI, add a trusted publisher for this repo (workflow `release.yml`, environment `pypi`); on
   GitHub, create an environment named `pypi`.
3. Run **Actions → Release → Run workflow**, entering the same version string as in `pyproject.toml`.

The workflow tags `vX.Y.Z`, builds with `uv build`, publishes to PyPI, signs the artifacts with Sigstore, and creates a
GitHub Release with notes pulled from the changelog. Full maintainer guide:
[docs/release-cycle.md](docs/release-cycle.md).

## License

MIT, see [LICENSE](LICENSE).
