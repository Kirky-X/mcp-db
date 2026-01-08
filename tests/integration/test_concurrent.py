"""并发操作测试 - 使用真实数据库"""

import asyncio
import os

import pytest

from mcp_database.adapters.nosql.mongodb import MongoDBAdapter
from mcp_database.adapters.nosql.redis import RedisAdapter
from mcp_database.adapters.sql.base import SQLAdapter
from mcp_database.core.models import DatabaseConfig
from tests.utils import DatabaseTestUtils, TestDataGenerator, wait_for_database_connection


class TestConcurrentOperations:
    """并发操作测试"""

    @pytest.mark.asyncio
    async def test_concurrent_inserts_sqlite(self):
        """测试 SQLite 并发插入"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        async def insert_user(user_id: int):
            user = TestDataGenerator.random_user()
            user["name"] = f"User{user_id}"
            return await adapter.insert("users", user)

        # 并发插入 100 个用户
        num_users = 100
        tasks = [insert_user(i) for i in range(num_users)]
        results = await asyncio.gather(*tasks)

        # 验证所有插入成功
        assert len(results) == num_users
        assert all(r.inserted_count == 1 for r in results)

        # 验证数据
        query_result = await adapter.query("users")
        assert len(query_result.data) == num_users

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_concurrent_queries_sqlite(self):
        """测试 SQLite 并发查询"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入测试数据
        users = TestDataGenerator.generate_users(50)
        for user in users:
            await adapter.insert("users", user)

        async def query_users():
            return await adapter.query("users", {"age__gt": 25})

        # 并发查询 100 次
        num_queries = 100
        tasks = [query_users() for _ in range(num_queries)]
        results = await asyncio.gather(*tasks)

        # 验证所有查询成功
        assert len(results) == num_queries
        assert all(len(r.data) > 0 for r in results)

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_concurrent_mixed_operations_sqlite(self):
        """测试 SQLite 混合并发操作"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入初始数据
        users = TestDataGenerator.generate_users(20)
        for user in users:
            await adapter.insert("users", user)

        async def insert_operation():
            user = TestDataGenerator.random_user()
            return await adapter.insert("users", user)

        async def query_operation():
            return await adapter.query("users", {"age__gt": 20})

        async def update_operation():
            return await adapter.update("users", {"active": True}, {"age__gt": 25})

        # 混合并发操作
        tasks = (
            [insert_operation() for _ in range(10)]
            + [query_operation() for _ in range(20)]
            + [update_operation() for _ in range(5)]
        )
        results = await asyncio.gather(*tasks)

        # 验证所有操作成功
        assert len(results) == 35

        await adapter.disconnect()

    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip MongoDB tests in CI environment")
    @pytest.mark.asyncio
    async def test_concurrent_inserts_mongodb(self):
        """测试 MongoDB 并发插入"""
        config = DatabaseConfig(url=DatabaseTestUtils.MONGODB_URL)
        adapter = MongoDBAdapter(config)

        await wait_for_database_connection(adapter, max_retries=5, delay=2.0)

        async def insert_user(user_id: int):
            user = TestDataGenerator.random_user()
            user["name"] = f"User{user_id}"
            return await adapter.insert("users", user)

        # 并发插入 100 个用户
        num_users = 100
        tasks = [insert_user(i) for i in range(num_users)]
        results = await asyncio.gather(*tasks)

        # 验证所有插入成功
        assert len(results) == num_users
        assert all(r.inserted_count == 1 for r in results)

        # 验证数据
        query_result = await adapter.query("users")
        assert len(query_result.data) == num_users

        await adapter.disconnect()

    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip Redis tests in CI environment")
    @pytest.mark.asyncio
    async def test_concurrent_inserts_redis(self):
        """测试 Redis 并发插入"""
        config = DatabaseConfig(url=DatabaseTestUtils.REDIS_URL)
        adapter = RedisAdapter(config)

        await wait_for_database_connection(adapter, max_retries=5, delay=2.0)

        async def insert_user(user_id: int):
            user = TestDataGenerator.random_user()
            user["name"] = f"User{user_id}"
            return await adapter.insert("users", user)

        # 并发插入 100 个用户
        num_users = 100
        tasks = [insert_user(i) for i in range(num_users)]
        results = await asyncio.gather(*tasks)

        # 验证所有插入成功
        assert len(results) == num_users
        assert all(r.inserted_count == 1 for r in results)

        # 验证数据
        query_result = await adapter.query("users")
        assert len(query_result.data) == num_users

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_concurrent_with_errors_sqlite(self):
        """测试 SQLite 并发操作中的错误处理"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        async def insert_user(user_id: int):
            user = TestDataGenerator.random_user()
            user["name"] = f"User{user_id}"
            return await adapter.insert("users", user)

        async def query_nonexistent_table():
            try:
                return await adapter.query("nonexistent_table")
            except Exception:
                return None

        # 并发执行包含错误的操作
        tasks = [insert_user(i) for i in range(50)] + [query_nonexistent_table() for _ in range(10)]

        # 使用 return_exceptions=True 来收集所有结果
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 验证成功的操作
        successful_inserts = [r for r in results[:50] if not isinstance(r, Exception)]
        assert len(successful_inserts) == 50

        # 验证错误操作（query_nonexistent_table 返回 None，不是异常）
        # 注意：query_nonexistent_table 捕获了异常并返回 None
        # 所以这里我们验证 None 的数量
        none_results = [r for r in results[50:] if r is None]
        assert len(none_results) == 10

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_concurrent_with_timeout(self):
        """测试并发操作的超时处理"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        async def slow_query():
            await asyncio.sleep(1)  # 模拟慢查询
            return await adapter.query("users")

        async def fast_query():
            return await adapter.query("users", {"age__gt": 0})

        # 并发执行，设置超时
        tasks = [asyncio.wait_for(slow_query(), timeout=0.5), fast_query()]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 第一个任务应该超时
        assert isinstance(results[0], asyncio.TimeoutError)
        # 第二个任务应该成功
        assert not isinstance(results[1], Exception)

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_concurrent_transaction_isolation(self):
        """测试并发事务隔离"""
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入初始数据
        user = {"name": "TestUser", "age": 25}
        await adapter.insert("users", user)

        async def read_and_update():
            # 读取数据
            result = await adapter.query("users", {"name": "TestUser"})
            if result.data:
                # 更新数据
                return await adapter.update(
                    "users", {"name": "TestUser"}, {"age": result.data[0]["age"] + 1}
                )
            return None

        # 并发更新
        tasks = [read_and_update() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # 验证所有更新成功
        assert all(r.updated_count == 1 for r in results if r)

        # 验证最终状态
        final_result = await adapter.query("users", {"name": "TestUser"})
        assert final_result.data[0]["age"] == 35  # 25 + 10

        await adapter.disconnect()
