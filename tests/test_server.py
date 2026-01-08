"""测试 MCP Server 工具接口"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMCPServerTools:
    """测试 MCP Server 工具"""

    @pytest.fixture
    def mock_adapter(self):
        """创建模拟适配器"""
        adapter = MagicMock()
        adapter.is_connected = True
        adapter.insert = AsyncMock()
        adapter.query = AsyncMock()
        adapter.update = AsyncMock()
        adapter.delete = AsyncMock()
        adapter.advanced_query = AsyncMock()
        adapter.execute = AsyncMock()
        return adapter

    @pytest.fixture
    def setup_server(self, mock_adapter):
        """设置测试环境"""
        with patch("mcp_database.server.get_adapter", return_value=mock_adapter):
            with patch("mcp_database.server.ensure_connected", new_callable=AsyncMock):
                from mcp_database.server import (
                    advanced,
                    delete,
                    execute,
                    insert,
                    query,
                    set_database_url,
                    update,
                )

                set_database_url("postgresql://test@localhost/test")
                yield {
                    "insert": insert,
                    "query": query,
                    "update": update,
                    "delete": delete,
                    "advanced": advanced,
                    "execute": execute,
                    "adapter": mock_adapter,
                }

    @pytest.mark.asyncio
    async def test_insert_single_record(self, setup_server):
        """测试插入单条记录"""
        from mcp_database.core.models import InsertResult

        setup_server["adapter"].insert.return_value = InsertResult(
            inserted_count=1, inserted_ids=[1], success=True
        )

        result = await setup_server["insert"](
            table="users", data={"name": "张三", "email": "zhangsan@example.com"}
        )

        assert result["success"] is True
        assert result["inserted_count"] == 1
        assert result["inserted_ids"] == [1]
        setup_server["adapter"].insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_insert_batch_records(self, setup_server):
        """测试批量插入"""
        from mcp_database.core.models import InsertResult

        setup_server["adapter"].insert.return_value = InsertResult(
            inserted_count=2, inserted_ids=[1, 2], success=True
        )

        result = await setup_server["insert"](
            table="users",
            data=[
                {"name": "张三", "email": "z1@example.com"},
                {"name": "李四", "email": "l4@example.com"},
            ],
        )

        assert result["success"] is True
        assert result["inserted_count"] == 2

    @pytest.mark.asyncio
    async def test_query_simple(self, setup_server):
        """测试简单查询"""
        from mcp_database.core.models import QueryResult

        setup_server["adapter"].query.return_value = QueryResult(
            data=[{"id": 1, "name": "张三"}], count=1, has_more=False, success=True
        )

        result = await setup_server["query"](table="users")

        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["count"] == 1
        assert result["has_more"] is False

    @pytest.mark.asyncio
    async def test_query_with_filters(self, setup_server):
        """测试带过滤条件的查询"""
        from mcp_database.core.models import QueryResult

        setup_server["adapter"].query.return_value = QueryResult(
            data=[{"id": 1, "name": "张三", "status": "active"}],
            count=1,
            has_more=False,
            success=True,
        )

        result = await setup_server["query"](
            table="users", filters={"status": "active", "age__gte": 18}, limit=10
        )

        assert result["success"] is True
        setup_server["adapter"].query.assert_called_once_with(
            "users", {"status": "active", "age__gte": 18}, 10
        )

    @pytest.mark.asyncio
    async def test_update_records(self, setup_server):
        """测试更新记录"""
        from mcp_database.core.models import UpdateResult

        setup_server["adapter"].update.return_value = UpdateResult(updated_count=3, success=True)

        result = await setup_server["update"](
            table="users", data={"status": "inactive"}, filters={"status": "pending"}
        )

        assert result["success"] is True
        assert result["updated_count"] == 3
        setup_server["adapter"].update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_records(self, setup_server):
        """测试删除记录"""
        from mcp_database.core.models import DeleteResult

        setup_server["adapter"].delete.return_value = DeleteResult(deleted_count=5, success=True)

        result = await setup_server["delete"](table="users", filters={"status": "deleted"})

        assert result["success"] is True
        assert result["deleted_count"] == 5
        setup_server["adapter"].delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_advanced_aggregate(self, setup_server):
        """测试高级操作 - 聚合查询"""
        from mcp_database.core.models import AdvancedResult

        setup_server["adapter"].advanced_query.return_value = AdvancedResult(
            operation="aggregate",
            data=[{"_id": "active", "count": 10}],
            success=True,
        )

        result = await setup_server["advanced"](
            table="users",
            operation="aggregate",
            params={"pipeline": [{"$match": {"status": "active"}}]},
        )

        assert result["success"] is True
        assert result["operation"] == "aggregate"
        assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_advanced_transaction(self, setup_server):
        """测试高级操作 - 事务"""
        from mcp_database.core.models import AdvancedResult

        setup_server["adapter"].advanced_query.return_value = AdvancedResult(
            operation="transaction",
            data={"results": [{"updated_count": 1}], "committed": True},
            success=True,
        )

        result = await setup_server["advanced"](
            table="orders",
            operation="transaction",
            params={
                "queries": [
                    {
                        "query": "UPDATE accounts SET balance = balance - 100 WHERE id = 1",
                        "params": None,
                    }
                ]
            },
        )

        assert result["success"] is True
        assert result["operation"] == "transaction"

    @pytest.mark.asyncio
    async def test_execute_query(self, setup_server):
        """测试原生查询执行"""
        from mcp_database.core.models import ExecuteResult

        setup_server["adapter"].execute.return_value = ExecuteResult(
            rows_affected=5, data=[{"id": 1}], success=True
        )

        result = await setup_server["execute"](
            query="SELECT * FROM users WHERE status = :status",
            params={"status": "active"},
        )

        assert result["success"] is True
        assert result["rows_affected"] == 5

    @pytest.mark.asyncio
    async def test_error_handling(self, setup_server):
        """测试错误处理"""
        from mcp_database.core.exceptions import QueryError

        setup_server["adapter"].query.side_effect = QueryError("Table not found")

        result = await setup_server["query"](table="nonexistent")

        assert result["success"] is False
        assert "error" in result
        assert result["error"]["type"] == "query_error"


class TestMCPServerRegistration:
    """测试 MCP Server 工具注册"""

    def test_all_tools_registered(self):
        """验证所有 6 个工具已注册"""
        from mcp_database.server import mcp

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]

        assert "insert" in tool_names
        assert "query" in tool_names
        assert "update" in tool_names
        assert "delete" in tool_names
        assert "advanced" in tool_names
        assert "execute" in tool_names
        assert len(tools) == 6

    def test_create_server_function(self):
        """验证 create_server 函数存在"""
        from mcp_database.server import create_server

        assert callable(create_server)
