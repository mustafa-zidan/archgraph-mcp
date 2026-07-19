"""Deterministic enums for graph node and edge types."""

from enum import StrEnum


class NodeType(StrEnum):
    """Types of nodes in the code knowledge graph."""

    REPOSITORY = "repository"
    MODULE = "module"
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    API = "api"
    DATABASE = "database"


class EdgeType(StrEnum):
    """Types of edges (relationships) in the code knowledge graph."""

    IMPORTS = "imports"
    CALLS = "calls"
    DEFINES = "defines"
    READS_TABLE = "reads_table"
    WRITES_TABLE = "writes_table"
    EXPOSES_API = "exposes_api"
    DEPENDS_ON = "depends_on"
