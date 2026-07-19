"""Optional semantic index build after graph persistence."""

from __future__ import annotations

import logging
import os

from archgraph_mcp.models import Node

logger = logging.getLogger("archgraph_mcp.semantic.build")


def maybe_build_semantic_index(store_path: str, nodes: list[Node]) -> None:
    """If ``ARCHGRAPH_BUILD_SEMANTIC_INDEX`` is truthy, write ``*.vectors.npz`` next to the store."""
    flag = os.environ.get("ARCHGRAPH_BUILD_SEMANTIC_INDEX", "").strip().lower()
    if flag not in ("1", "true", "yes"):
        return
    try:
        from archgraph_mcp.semantic.embeddings import describe_embedding_backend, get_backend_from_env
        from archgraph_mcp.semantic.vector_index import build_index
    except ImportError:
        logger.warning("ARCHGRAPH_BUILD_SEMANTIC_INDEX set but semantic extra is not installed")
        return
    try:
        backend = get_backend_from_env()
        logger.info("Building semantic vector index using embeddings: %s", describe_embedding_backend(backend))
        build_index(store_path, nodes, backend)
    except Exception:
        logger.exception("Failed to build semantic vector index")
