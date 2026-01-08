"""MCP Database Server - 统一数据库操作 MCP Server"""

import asyncio
from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_database import AdapterFactory, DatabaseConfig
from mcp_database.core.exceptions import DatabaseError
from mcp_database.core.models import (
    AdvancedResult,
    DeleteResult,
    ExecuteResult,
    InsertResult,
    QueryResult,
    UpdateResult,
)

mcp = FastMCP("MCP Database")

_database_url: str = ""
_adapter: Any = None


def set_database_url(url: str) -> None:
    """设置数据库连接 URL"""
    global _database_url, _adapter
    _database_url = url
    _adapter = None


def get_adapter() -> Any:
    """获取数据库适配器单例"""
    global _adapter
    if _adapter is None:
        config = DatabaseConfig(url=_database_url)
        _adapter = AdapterFactory.create_adapter(config)
    return _adapter


async def ensure_connected() -> None:
    """确保数据库已连接"""
    adapter = get_adapter()
    if not adapter.is_connected:
        await adapter.connect()


@mcp.tool()
async def insert(table: str, data: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    """
    向数据库插入新记录。

    Args:
        table: 表/集合/键前缀名
        data: 要插入的数据（对象或数组，支持批量插入）

    Returns:
        包含 success、inserted_count、inserted_ids 的字典
    """
    await ensure_connected()
    adapter = get_adapter()
    try:
        result: InsertResult = await adapter.insert(table, data)
        return {
            "success": result.success,
            "inserted_count": result.inserted_count,
            "inserted_ids": result.inserted_ids,
        }
    except DatabaseError as e:
        return {"success": False, "error": {"type": "query_error", "message": str(e)}}


@mcp.tool()
async def query(
    table: str, filters: dict[str, Any] | None = None, limit: int | None = None
) -> dict[str, Any]:
    """
    从数据库查询数据。

    Args:
        table: 表/集合/键前缀名
        filters: 过滤条件，支持操作符：__gt、__gte、__lt、__lte、__contains、__startswith、__endswith、__in、__not_in、__isnull
        limit: 返回数量限制，默认100，最大10000

    Returns:
        包含 success、data、count、has_more 的字典
    """
    await ensure_connected()
    adapter = get_adapter()
    try:
        result: QueryResult = await adapter.query(table, filters, limit)
        return {
            "success": result.success,
            "data": result.data,
            "count": result.count,
            "has_more": result.has_more,
        }
    except DatabaseError as e:
        return {"success": False, "error": {"type": "query_error", "message": str(e)}}


@mcp.tool()
async def update(table: str, data: dict[str, Any], filters: dict[str, Any]) -> dict[str, Any]:
    """
    更新数据库中已存在的记录。

    Args:
        table: 表/集合/键前缀名
        data: 要更新的字段和值
        filters: 更新条件（限定更新范围）

    Returns:
        包含 success、updated_count 的字典
    """
    await ensure_connected()
    adapter = get_adapter()
    try:
        result: UpdateResult = await adapter.update(table, data, filters)
        return {
            "success": result.success,
            "updated_count": result.updated_count,
        }
    except DatabaseError as e:
        return {"success": False, "error": {"type": "query_error", "message": str(e)}}


@mcp.tool()
async def delete(table: str, filters: dict[str, Any]) -> dict[str, Any]:
    """
    从数据库删除记录。

    Args:
        table: 表/集合/键前缀名
        filters: 删除条件（限定删除范围）

    Returns:
        包含 success、deleted_count 的字典
    """
    await ensure_connected()
    adapter = get_adapter()
    try:
        result: DeleteResult = await adapter.delete(table, filters)
        return {
            "success": result.success,
            "deleted_count": result.deleted_count,
        }
    except DatabaseError as e:
        return {"success": False, "error": {"type": "query_error", "message": str(e)}}


@mcp.tool()
async def advanced(table: str, operation: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    执行高级操作，如聚合查询、事务等。

    Args:
        table: 表/集合名
        operation: 操作类型，如 aggregate、transaction
        params: 操作参数

    Returns:
        包含 success、operation、data 的字典
    """
    await ensure_connected()
    adapter = get_adapter()
    try:
        result: AdvancedResult = await adapter.advanced_query(operation, params)
        return {
            "success": result.success,
            "operation": result.operation,
            "data": result.data,
        }
    except DatabaseError as e:
        return {"success": False, "error": {"type": "query_error", "message": str(e)}}


@mcp.tool()
async def execute(query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    执行任意原生查询语句。此工具默认禁用，需设置 DANGEROUS_AGREE=true 才会生效。

    Args:
        query: 原生 SQL/MongoDB 查询语句
        params: 查询参数（用于参数化查询）

    Returns:
        包含 success、rows_affected、data 的字典
    """
    await ensure_connected()
    adapter = get_adapter()
    try:
        result: ExecuteResult = await adapter.execute(query, params)
        return {
            "success": result.success,
            "rows_affected": result.rows_affected,
            "data": result.data,
        }
    except DatabaseError as e:
        return {"success": False, "error": {"type": "query_error", "message": str(e)}}


def create_server(database_url: str) -> FastMCP:
    """
    创建 MCP Database Server 实例。

    Args:
        database_url: 数据库连接 URL

    Returns:
        配置好的 FastMCP 服务器实例
    """
    set_database_url(database_url)
    return mcp
