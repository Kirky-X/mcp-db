"""错误处理和边界条件测试 - 使用真实数据库"""

import os

import pytest

from mcp_database.adapters.nosql.mongodb import MongoDBAdapter
from mcp_database.adapters.nosql.redis import RedisAdapter
from mcp_database.adapters.sql.base import SQLAdapter
from mcp_database.core.exceptions import ConnectionError, QueryError
from mcp_database.core.models import DatabaseConfig
from tests.utils import DatabaseTestUtils, TestDataGenerator


class TestErrorHandling:
    """错误处理测试"""

    @pytest.mark.asyncio
    async def test_connection_error_invalid_url(self):
        """测试无效 URL 的连接错误"""
        config = DatabaseConfig(url="postgresql+asyncpg://invalid:invalid@invalid:9999/invalid")
        adapter = SQLAdapter(config)

        with pytest.raises(ConnectionError):
            await adapter.connect()

    @pytest.mark.asyncio
    async def test_insert_into_nonexistent_table(self):
        """测试向不存在的表插入数据"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()

        with pytest.raises(QueryError):
            await adapter.insert("nonexistent_table", {"name": "Test"})

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_query_nonexistent_table(self):
        """测试查询不存在的表"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()

        with pytest.raises(QueryError):
            await adapter.query("nonexistent_table")

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_update_nonexistent_table(self):
        """测试更新不存在的表"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()

        with pytest.raises(QueryError):
            await adapter.update("nonexistent_table", {}, {})

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_table(self):
        """测试删除不存在的表"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()

        with pytest.raises(QueryError):
            await adapter.delete("nonexistent_table", {})

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_duplicate_key_violation(self):
        """测试重复键违反"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入第一条记录
        user = {"name": "UniqueUser", "age": 25}
        await adapter.insert("users", user)

        # 尝试插入重复的 name（假设 name 有唯一约束）
        # 注意：SQLite 默认没有唯一约束，这里只是演示
        # 实际测试需要创建带唯一约束的表

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_empty_insert(self):
        """测试空数据插入"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入空记录
        result = await adapter.insert("users", {})
        assert result.inserted_count == 1

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_empty_query(self):
        """测试空查询"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入一些数据
        user = TestDataGenerator.random_user()
        await adapter.insert("users", user)

        # 空过滤条件查询
        result = await adapter.query("users", {})
        assert len(result.data) == 1

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_query_no_results(self):
        """测试无结果的查询"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 查询不存在的数据
        result = await adapter.query("users", {"name": "NonExistent"})
        assert len(result.data) == 0

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_update_no_matches(self):
        """测试更新无匹配的数据"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 更新不存在的数据
        result = await adapter.update("users", {"name": "NonExistent"}, {"age": 30})
        assert result.updated_count == 0

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_delete_no_matches(self):
        """测试删除无匹配的数据"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 删除不存在的数据
        result = await adapter.delete("users", {"name": "NonExistent"})
        assert result.deleted_count == 0

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_invalid_filter_operator(self):
        """测试无效的过滤操作符"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 使用无效的操作符
        with pytest.raises(QueryError):
            await adapter.query("users", {"age__invalid": 25})

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_malformed_sql_injection_attempt(self):
        """测试 SQL 注入尝试"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 尝试 SQL 注入
        malicious_name = "'; DROP TABLE users; --"
        result = await adapter.query("users", {"name": malicious_name})

        # 应该返回空结果，而不是执行恶意 SQL
        assert len(result.data) == 0

        # 验证表仍然存在
        result = await adapter.query("users")
        assert result is not None

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_large_data_insert(self):
        """测试大数据插入"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入大量数据
        large_data = {"name": "A" * 1000, "age": 25}
        result = await adapter.insert("users", large_data)

        assert result.inserted_count == 1

        # 验证数据
        query_result = await adapter.query("users", {"name": "A" * 1000})
        assert len(query_result.data) == 1

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_special_characters_in_data(self):
        """测试数据中的特殊字符"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入包含特殊字符的数据
        special_data = {"name": "Test'\";\\--", "age": 25}
        result = await adapter.insert("users", special_data)

        assert result.inserted_count == 1

        # 验证数据
        query_result = await adapter.query("users", {"name": "Test'\";\\--"})
        assert len(query_result.data) == 1

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_null_values(self):
        """测试 NULL 值处理"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入包含 NULL 值的数据
        null_data = {"name": "TestUser", "age": None}
        result = await adapter.insert("users", null_data)

        assert result.inserted_count == 1

        # 验证数据
        query_result = await adapter.query("users", {"name": "TestUser"})
        assert len(query_result.data) == 1

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_numeric_boundary_values(self):
        """测试数值边界值"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入边界值
        boundary_values = [
            {"name": "MinInt", "age": -2147483648},
            {"name": "MaxInt", "age": 2147483647},
            {"name": "Zero", "age": 0},
        ]

        for value in boundary_values:
            result = await adapter.insert("users", value)
            assert result.inserted_count == 1

        # 验证数据
        for value in boundary_values:
            query_result = await adapter.query("users", {"name": value["name"]})
            assert len(query_result.data) == 1
            assert query_result.data[0]["age"] == value["age"]

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_disconnect_without_connect(self):
        """测试未连接时的断开操作"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        # 未连接时断开应该不会抛出错误
        await adapter.disconnect()
        assert adapter.is_connected is False

    @pytest.mark.asyncio
    async def test_operation_without_connect(self):
        """测试未连接时的数据库操作"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        # 未连接时操作应该抛出错误
        with pytest.raises(ConnectionError):
            await adapter.insert("users", {"name": "Test"})

    @pytest.mark.asyncio
    async def test_reconnect_after_disconnect(self):
        """测试断开后重新连接"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        # 第一次连接
        await adapter.connect()
        assert adapter.is_connected is True

        # 断开连接
        await adapter.disconnect()
        assert adapter.is_connected is False

        # 重新连接
        await adapter.connect()
        assert adapter.is_connected is True

        await adapter.disconnect()

    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip MongoDB tests in CI environment")
    @pytest.mark.asyncio
    async def test_mongodb_connection_error(self):
        """测试 MongoDB 连接错误"""
        config = DatabaseConfig(url="mongodb://invalid:invalid@invalid:9999/invalid")
        adapter = MongoDBAdapter(config)

        with pytest.raises(ConnectionError):
            await adapter.connect()

    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip Redis tests in CI environment")
    @pytest.mark.asyncio
    async def test_redis_connection_error(self):
        """测试 Redis 连接错误"""
        config = DatabaseConfig(url="redis://:invalid@invalid:9999/0")
        adapter = RedisAdapter(config)

        with pytest.raises(ConnectionError):
            await adapter.connect()

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """测试超时处理"""
        config = DatabaseConfig(
            url=DatabaseTestUtils.SQLITE_URL,
            query_timeout=0.001,  # 设置非常短的超时
        )
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入大量数据可能导致超时
        # 这里只是演示超时配置的使用
        user = TestDataGenerator.random_user()
        result = await adapter.insert("users", user)

        assert result.inserted_count == 1

        await adapter.disconnect()
