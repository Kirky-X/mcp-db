"""测试 SQL 适配器基类 - 使用真实数据库"""

import os

import pytest

from mcp_database.adapters.sql.base import SQLAdapter
from mcp_database.core.models import DatabaseConfig
from tests.utils import DatabaseTestUtils, TestDataGenerator, wait_for_database_connection


class TestSQLAdapterSQLite:
    """测试 SQLAdapter - SQLite"""

    @pytest.fixture
    async def adapter(self):
        """创建 SQLite 适配器实例"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)
        await adapter.connect()
        yield adapter
        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self, adapter):
        """测试连接和断开"""
        assert adapter.is_connected is True

    @pytest.mark.asyncio
    async def test_create_table(self, adapter):
        """测试创建表"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 验证表存在
        result = await adapter.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert len(result.data) > 0

    @pytest.mark.asyncio
    async def test_insert_single_record(self, adapter):
        """测试插入单条记录"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        user = TestDataGenerator.random_user()
        result = await adapter.insert("users", user)

        assert result.inserted_count == 1
        assert len(result.inserted_ids) == 1

    @pytest.mark.asyncio
    async def test_insert_batch_records(self, adapter):
        """测试批量插入记录"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = TestDataGenerator.generate_users(10)
        result = await adapter.insert("users", users)

        assert result.inserted_count == 10
        assert len(result.inserted_ids) == 10

    @pytest.mark.asyncio
    async def test_query_without_filters(self, adapter):
        """测试无过滤条件的查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = TestDataGenerator.generate_users(5)
        await adapter.insert("users", users)

        result = await adapter.query("users")
        assert len(result.data) == 5

    @pytest.mark.asyncio
    async def test_query_with_equality_filter(self, adapter):
        """测试等值过滤查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        user = TestDataGenerator.random_user()
        user["name"] = "TestUser"
        await adapter.insert("users", user)

        result = await adapter.query("users", {"name": "TestUser"})
        assert len(result.data) == 1
        assert result.data[0]["name"] == "TestUser"

    @pytest.mark.asyncio
    async def test_query_with_gt_filter(self, adapter):
        """测试大于过滤查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert("users", users)

        result = await adapter.query("users", {"age__gt": 25})
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_query_with_lt_filter(self, adapter):
        """测试小于过滤查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert("users", users)

        result = await adapter.query("users", {"age__lt": 35})
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_query_with_gte_filter(self, adapter):
        """测试大于等于过滤查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert("users", users)

        result = await adapter.query("users", {"age__gte": 30})
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_query_with_lte_filter(self, adapter):
        """测试小于等于过滤查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert("users", users)

        result = await adapter.query("users", {"age__lte": 30})
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_query_with_contains_filter(self, adapter):
        """测试包含过滤查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = [{"name": "Alice Smith"}, {"name": "Bob Johnson"}, {"name": "Charlie Brown"}]
        await adapter.insert("users", users)

        result = await adapter.query("users", {"name__contains": "Smith"})
        assert len(result.data) == 1
        assert result.data[0]["name"] == "Alice Smith"

    @pytest.mark.asyncio
    async def test_query_with_in_filter(self, adapter):
        """测试 IN 过滤查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert("users", users)

        result = await adapter.query("users", {"age__in": [20, 40]})
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_query_with_limit(self, adapter):
        """测试限制查询结果数量"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = TestDataGenerator.generate_users(10)
        await adapter.insert("users", users)

        result = await adapter.query("users", limit=5)
        assert len(result.data) == 5

    @pytest.mark.asyncio
    async def test_update_with_filters(self, adapter):
        """测试更新操作"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入简单的测试数据
        user = {"name": "OldName", "age": 25}
        await adapter.insert("users", user)

        result = await adapter.update("users", {"name": "NewName"}, {"name": "OldName"})
        assert result.updated_count == 1

        # 验证更新
        query_result = await adapter.query("users", {"name": "NewName"})
        assert len(query_result.data) == 1

    @pytest.mark.asyncio
    async def test_delete_with_filters(self, adapter):
        """测试删除操作"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入简单的测试数据
        user = {"name": "ToDelete", "age": 25}
        await adapter.insert("users", user)

        result = await adapter.delete("users", {"name": "ToDelete"})
        assert result.deleted_count == 1

        # 验证删除
        query_result = await adapter.query("users", {"name": "ToDelete"})
        assert len(query_result.data) == 0

    @pytest.mark.asyncio
    async def test_execute_with_params(self, adapter):
        """测试执行带参数的 SQL"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        result = await adapter.execute(
            "INSERT INTO users (name, age) VALUES (:name, :age)",
            params={"name": "TestUser", "age": 25},
        )
        assert result.rows_affected == 1

    @pytest.mark.asyncio
    async def test_get_capabilities(self, adapter):
        """测试获取能力信息"""
        capabilities = adapter.get_capabilities()
        assert capabilities.basic_crud is True

    @pytest.mark.asyncio
    async def test_connection_pool(self, adapter):
        """测试连接池"""
        # SQLite 不使用连接池，但测试应该通过
        assert adapter.is_connected is True


@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip PostgreSQL tests in CI environment")
class TestSQLAdapterPostgreSQL:
    """测试 SQLAdapter - PostgreSQL"""

    @pytest.fixture
    async def adapter(self):
        """创建 PostgreSQL 适配器实例"""
        config = DatabaseConfig(url=DatabaseTestUtils.POSTGRES_URL)
        adapter = SQLAdapter(config)

        try:
            await wait_for_database_connection(adapter, max_retries=5, delay=2.0)
            yield adapter
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self, adapter):
        """测试连接和断开"""
        assert adapter.is_connected is True

    @pytest.mark.asyncio
    async def test_insert_single_record(self, adapter):
        """测试插入单条记录"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        user = TestDataGenerator.random_user()
        result = await adapter.insert("users", user)

        assert result.inserted_count == 1

    @pytest.mark.asyncio
    async def test_query_with_filters(self, adapter):
        """测试带过滤条件的查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = TestDataGenerator.generate_users(5)
        await adapter.insert("users", users)

        result = await adapter.query("users", {"age__gt": 25})
        assert len(result.data) > 0

    @pytest.mark.asyncio
    async def test_update_with_filters(self, adapter):
        """测试更新操作"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)
        await DatabaseTestUtils.clear_test_data(adapter, "users")

        user = TestDataGenerator.random_user()
        user["name"] = "OldName"
        await adapter.insert("users", user)

        result = await adapter.update("users", {"name": "NewName"}, {"name": "OldName"})
        assert result.updated_count == 1

    @pytest.mark.asyncio
    async def test_delete_with_filters(self, adapter):
        """测试删除操作"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        user = TestDataGenerator.random_user()
        user["name"] = "ToDelete"
        await adapter.insert("users", user)

        result = await adapter.delete("users", {"name": "ToDelete"})
        assert result.deleted_count == 1

    @pytest.mark.asyncio
    async def test_execute_with_params(self, adapter):
        """测试执行带参数的 SQL"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        result = await adapter.execute(
            "INSERT INTO users (name, age) VALUES (:name, :age)",
            params={"name": "TestUser", "age": 25},
        )
        assert result.rows_affected == 1


@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip MySQL tests in CI environment")
class TestSQLAdapterMySQL:
    """测试 SQLAdapter - MySQL"""

    @pytest.fixture
    async def adapter(self):
        """创建 MySQL 适配器实例"""
        config = DatabaseConfig(url=DatabaseTestUtils.MYSQL_URL)
        adapter = SQLAdapter(config)

        try:
            await wait_for_database_connection(adapter, max_retries=5, delay=2.0)
            yield adapter
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self, adapter):
        """测试连接和断开"""
        assert adapter.is_connected is True

    @pytest.mark.asyncio
    async def test_insert_single_record(self, adapter):
        """测试插入单条记录"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        user = TestDataGenerator.random_user()
        result = await adapter.insert("users", user)

        assert result.inserted_count == 1

    @pytest.mark.asyncio
    async def test_query_with_filters(self, adapter):
        """测试带过滤条件的查询"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        users = TestDataGenerator.generate_users(5)
        await adapter.insert("users", users)

        result = await adapter.query("users", {"age__gt": 25})
        assert len(result.data) > 0

    @pytest.mark.asyncio
    async def test_update_with_filters(self, adapter):
        """测试更新操作"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)
        await DatabaseTestUtils.clear_test_data(adapter, "users")

        user = TestDataGenerator.random_user()
        user["name"] = "OldName"
        await adapter.insert("users", user)

        result = await adapter.update("users", {"name": "NewName"}, {"name": "OldName"})
        assert result.updated_count == 1

    @pytest.mark.asyncio
    async def test_delete_with_filters(self, adapter):
        """测试删除操作"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        user = TestDataGenerator.random_user()
        user["name"] = "ToDelete"
        await adapter.insert("users", user)

        result = await adapter.delete("users", {"name": "ToDelete"})
        assert result.deleted_count == 1

    @pytest.mark.asyncio
    async def test_execute_with_params(self, adapter):
        """测试执行带参数的 SQL"""
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        result = await adapter.execute(
            "INSERT INTO users (name, age) VALUES (:name, :age)",
            params={"name": "TestUser", "age": 25},
        )
        assert result.rows_affected == 1
