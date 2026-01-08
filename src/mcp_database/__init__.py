"""MCP Database SDK - 为大语言模型提供统一数据库操作能力"""

__version__ = "0.1.0"

from mcp_database.adapters import AdapterFactory
from mcp_database.core import (
    AdvancedResult,
    Capability,
    ConnectionError,
    DatabaseAdapter,
    DatabaseConfig,
    DatabaseError,
    DeleteResult,
    ExecuteResult,
    InsertResult,
    IntegrityError,
    PermissionError,
    QueryError,
    QueryResult,
    TimeoutError,
    UpdateResult,
)

__all__ = [
    "__version__",
    "DatabaseAdapter",
    "DatabaseConfig",
    "InsertResult",
    "UpdateResult",
    "DeleteResult",
    "QueryResult",
    "ExecuteResult",
    "AdvancedResult",
    "Capability",
    "DatabaseError",
    "ConnectionError",
    "QueryError",
    "PermissionError",
    "IntegrityError",
    "TimeoutError",
    "AdapterFactory",
]
