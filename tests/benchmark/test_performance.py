"""性能基准测试 - 使用真实数据库"""

import asyncio
import os
import time
from typing import Any

import pytest

from mcp_database.adapters.nosql.mongodb import MongoDBAdapter
from mcp_database.adapters.nosql.opensearch import OpenSearchAdapter
from mcp_database.adapters.nosql.redis import RedisAdapter
from mcp_database.adapters.sql.base import SQLAdapter
from mcp_database.core.models import DatabaseConfig
from tests.utils import DatabaseTestUtils, TestDataGenerator, wait_for_database_connection


class PerformanceBenchmark:
    """性能基准测试类"""

    def __init__(self):
        self.results: list[dict[str, Any]] = []

    def record_result(self, operation: str, duration: float, count: int = 1):
        """记录测试结果"""
        self.results.append(
            {
                "operation": operation,
                "duration": duration,
                "count": count,
                "qps": count / duration if duration > 0 else 0,
            }
        )

    def get_summary(self):
        """获取测试摘要"""
        if not self.results:
            return {}

        total_duration = sum(r["duration"] for r in self.results)
        total_operations = sum(r["count"] for r in self.results)
        average_qps = total_operations / total_duration if total_duration > 0 else 0

        return {
            "total_duration": total_duration,
            "total_operations": total_operations,
            "average_qps": average_qps,
            "operations": len(self.results),
        }


class TestPerformanceBenchmark:
    """性能基准测试"""

    @pytest.mark.asyncio
    async def test_sql_adapter_insert_performance(self):
        """测试 SQL 适配器插入性能"""
        benchmark = PerformanceBenchmark()
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 性能测试：插入 100 条记录
        num_records = 100
        start_time = time.time()

        for i in range(num_records):
            await adapter.insert("users", {"name": f"User{i}", "age": 20 + i % 30})

        duration = time.time() - start_time
        benchmark.record_result("sqlite_insert", duration, num_records)

        # 验证性能
        summary = benchmark.get_summary()
        assert summary["average_qps"] > 10  # 至少 10 QPS

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_sql_adapter_query_performance(self):
        """测试 SQL 适配器查询性能"""
        benchmark = PerformanceBenchmark()
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 插入测试数据
        users = TestDataGenerator.generate_users(100)
        for user in users:
            await adapter.insert("users", user)

        # 性能测试：查询 100 次
        num_queries = 100
        start_time = time.time()

        for _ in range(num_queries):
            await adapter.query("users", {"age__gt": 25})

        duration = time.time() - start_time
        benchmark.record_result("sqlite_query", duration, num_queries)

        # 验证性能
        summary = benchmark.get_summary()
        assert summary["average_qps"] > 50  # 至少 50 QPS

        await adapter.disconnect()

    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip MongoDB tests in CI environment")
    @pytest.mark.asyncio
    async def test_mongodb_adapter_insert_performance(self):
        """测试 MongoDB 适配器插入性能"""
        benchmark = PerformanceBenchmark()
        config = DatabaseConfig(url=DatabaseTestUtils.MONGODB_URL)
        adapter = MongoDBAdapter(config)

        await wait_for_database_connection(adapter, max_retries=5, delay=2.0)

        # 性能测试：插入 100 条记录
        num_records = 100
        start_time = time.time()

        for i in range(num_records):
            await adapter.insert("users", {"name": f"User{i}", "age": 20 + i % 30})

        duration = time.time() - start_time
        benchmark.record_result("mongodb_insert", duration, num_records)

        # 验证性能
        summary = benchmark.get_summary()
        assert summary["average_qps"] > 10  # 至少 10 QPS

        await adapter.disconnect()

    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip Redis tests in CI environment")
    @pytest.mark.asyncio
    async def test_redis_adapter_insert_performance(self):
        """测试 Redis 适配器插入性能"""
        benchmark = PerformanceBenchmark()
        config = DatabaseConfig(url=DatabaseTestUtils.REDIS_URL)
        adapter = RedisAdapter(config)

        await wait_for_database_connection(adapter, max_retries=5, delay=2.0)

        # 性能测试：插入 100 条记录
        num_records = 100
        start_time = time.time()

        for i in range(num_records):
            await adapter.insert("users", {"name": f"User{i}", "age": 20 + i % 30})

        duration = time.time() - start_time
        benchmark.record_result("redis_insert", duration, num_records)

        # 验证性能
        summary = benchmark.get_summary()
        assert summary["average_qps"] > 50  # 至少 50 QPS

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """测试并发操作"""
        benchmark = PerformanceBenchmark()
        config = DatabaseConfig(url=DatabaseTestUtils.SQLITE_URL)
        adapter = SQLAdapter(config)

        await adapter.connect()
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 并发插入测试
        async def insert_user(user_id: int):
            return await adapter.insert(
                "users", {"name": f"User{user_id}", "age": 20 + user_id % 30}
            )

        num_concurrent = 50
        start_time = time.time()

        tasks = [insert_user(i) for i in range(num_concurrent)]
        await asyncio.gather(*tasks)

        duration = time.time() - start_time
        benchmark.record_result("concurrent_insert", duration, num_concurrent)

        # 验证性能
        summary = benchmark.get_summary()
        assert summary["average_qps"] > 20  # 至少 20 QPS

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_performance_summary(self):
        """测试性能摘要生成"""
        benchmark = PerformanceBenchmark()

        # 模拟一些性能数据
        benchmark.record_result("insert", 1.0, 100)
        benchmark.record_result("query", 0.5, 200)
        benchmark.record_result("update", 0.3, 150)

        summary = benchmark.get_summary()

        assert summary["total_duration"] == 1.8
        assert summary["total_operations"] == 450
        assert summary["average_qps"] == 250.0
        assert summary["operations"] == 3

    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip PostgreSQL tests in CI environment")
    @pytest.mark.asyncio
    async def test_postgresql_insert_performance(self):
        """测试 PostgreSQL 插入性能"""
        benchmark = PerformanceBenchmark()
        config = DatabaseConfig(url=DatabaseTestUtils.POSTGRES_URL)
        adapter = SQLAdapter(config)

        await wait_for_database_connection(adapter, max_retries=5, delay=2.0)
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 性能测试：插入 100 条记录
        num_records = 100
        start_time = time.time()

        for i in range(num_records):
            await adapter.insert("users", {"name": f"User{i}", "age": 20 + i % 30})

        duration = time.time() - start_time
        benchmark.record_result("postgresql_insert", duration, num_records)

        # 验证性能
        summary = benchmark.get_summary()
        assert summary["average_qps"] > 10  # 至少 10 QPS

        await adapter.disconnect()

    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip MySQL tests in CI environment")
    @pytest.mark.asyncio
    async def test_mysql_insert_performance(self):
        """测试 MySQL 插入性能"""
        benchmark = PerformanceBenchmark()
        config = DatabaseConfig(url=DatabaseTestUtils.MYSQL_URL)
        adapter = SQLAdapter(config)

        await wait_for_database_connection(adapter, max_retries=5, delay=2.0)
        schema = DatabaseTestUtils.get_test_schema()
        await DatabaseTestUtils.create_test_table(adapter, "users", schema)

        # 性能测试：插入 100 条记录
        num_records = 100
        start_time = time.time()

        for i in range(num_records):
            await adapter.insert("users", {"name": f"User{i}", "age": 20 + i % 30})

        duration = time.time() - start_time
        benchmark.record_result("mysql_insert", duration, num_records)

        # 验证性能
        summary = benchmark.get_summary()
        assert summary["average_qps"] > 10  # 至少 10 QPS

        await adapter.disconnect()

    @pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip OpenSearch tests in CI environment")
    @pytest.mark.asyncio
    async def test_opensearch_insert_performance(self):
        """测试 OpenSearch 插入性能"""
        benchmark = PerformanceBenchmark()
        config = DatabaseConfig(url=DatabaseTestUtils.OPENSEARCH_URL)
        adapter = OpenSearchAdapter(config)

        await wait_for_database_connection(adapter, max_retries=10, delay=3.0)

        # 性能测试：插入 100 条记录
        num_records = 100
        start_time = time.time()

        for i in range(num_records):
            await adapter.insert("users", {"name": f"User{i}", "age": 20 + i % 30})

        duration = time.time() - start_time
        benchmark.record_result("opensearch_insert", duration, num_records)

        # 验证性能
        summary = benchmark.get_summary()
        assert summary["average_qps"] > 5  # 至少 5 QPS

        await adapter.disconnect()
