# Changelog

## [1.0.2]

Fix: `pyproject.toml` had no `classifiers`, so PyPI had no `Programming Language :: Python :: X.Y` trove classifiers to
read. That's what the README's "Python versions" shield badge is generated from, not `requires-python`, so it rendered
as missing on every load. Added classifiers for 3.12-3.14 and an SPDX `license = "MIT"` field.

## [1.0.1]

Fix: `pyproject.toml` had no `readme` field, so 1.0.0 published to PyPI with no long description on the project page.
Added `readme = "README.md"`.

## [1.0.0]

Initial PyPI release: MCP server that builds a code knowledge graph (Tree-sitter parsers for TypeScript, Java, and
Kotlin; NetworkX traversal; Kuzu storage with full-text search). Optional semantic search via
`pip install archgraph-mcp[semantic]` (NumPy vector index + OpenAI-compatible or local `sentence-transformers`
embeddings). Ships `stdio`, `sse`, and `streamable-http` transports, an optional graph viewer UI, and Docker/Railway/
Fly.io deployment configs. CI covers Ubuntu, macOS, and Windows across Python 3.12-3.14.
