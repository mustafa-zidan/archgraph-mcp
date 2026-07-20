# Changelog

## [1.0.0]

Initial PyPI release: MCP server that builds a code knowledge graph (Tree-sitter parsers for TypeScript, Java, and
Kotlin; NetworkX traversal; Kuzu storage with full-text search). Optional semantic search via
`pip install archgraph-mcp[semantic]` (NumPy vector index + OpenAI-compatible or local `sentence-transformers`
embeddings). Ships `stdio`, `sse`, and `streamable-http` transports, an optional graph viewer UI, and Docker/Railway/
Fly.io deployment configs. CI covers Ubuntu, macOS, and Windows across Python 3.12-3.14.
