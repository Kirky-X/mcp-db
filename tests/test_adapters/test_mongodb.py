"""测试 MongoDB 适配器 - 使用真实数据库"""

import os

import pytest

from mcp_database.adapters.nosql.mongodb import MongoDBAdapter
from mcp_database.core.models import DatabaseConfig
from tests.utils import DatabaseTestUtils, TestDataGenerator, wait_for_database_connection


@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip MongoDB tests in CI environment")
class TestMongoDBAdapter:
    """测试 MongoDB 适配器"""

    @pytest.fixture
    async def adapter(self):
        """创建 MongoDB 适配器实例"""
        config = DatabaseConfig(url=DatabaseTestUtils.MONGODB_URL)
        adapter = MongoDBAdapter(config)

        try:
            await wait_for_database_connection(adapter, max_retries=5, delay=2.0)
            yield adapter
        finally:
            await adapter.disconnect()

    @staticmethod
    async def clear_mongodb_database(adapter):
        """清理 MongoDB 数据库中的所有数据"""
        try:
            # 删除所有集合
            collections = await adapter._database.list_collection_names()
            for collection_name in collections:
                await adapter._database[collection_name].delete_many({})
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_connect_to_mongodb(self, adapter):
        """测试连接到 MongoDB"""
        assert adapter.is_connected is True

    @pytest.mark.asyncio
    async def test_insert_single_document(self, adapter):
        """测试插入单个文档"""
        await self.clear_mongodb_database(adapter)

        user = TestDataGenerator.random_user()
        result = await adapter.insert("users", user)

        assert result.inserted_count == 1
        assert len(result.inserted_ids) == 1

    @pytest.mark.asyncio
    async def test_insert_multiple_documents(self, adapter):
        """测试插入多个文档"""
        await self.clear_mongodb_database(adapter)

        users = TestDataGenerator.generate_users(10)
        result = await adapter.insert("users", users)

        assert result.inserted_count == 10
        assert len(result.inserted_ids) == 10

    @pytest.mark.asyncio
    async def test_query_without_filters(self, adapter):
        """测试无过滤条件的查询"""
        await self.clear_mongodb_database(adapter)

        users = TestDataGenerator.generate_users(5)
        await adapter.insert("users", users)

        result = await adapter.query("users")
        assert len(result.data) == 5

    @pytest.mark.asyncio
    async def test_query_with_equality_filter(self, adapter):
        """测试等值过滤查询"""
        await self.clear_mongodb_database(adapter)

        user = TestDataGenerator.random_user()
        user["name"] = "TestUser"
        await adapter.insert("users", user)

        result = await adapter.query("users", {"name": "TestUser"})
        assert len(result.data) == 1
        assert result.data[0]["name"] == "TestUser"

    @pytest.mark.asyncio
    async def test_query_with_gt_filter(self, adapter):
        """测试大于过滤查询"""
        await self.clear_mongodb_database(adapter)

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
        await self.clear_mongodb_database(adapter)

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
        await self.clear_mongodb_database(adapter)

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
        await self.clear_mongodb_database(adapter)

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
        await self.clear_mongodb_database(adapter)

        users = [{"name": "Alice Smith"}, {"name": "Bob Johnson"}, {"name": "Charlie Brown"}]
        await adapter.insert("users", users)

        result = await adapter.query("users", {"name__contains": "Smith"})
        assert len(result.data) == 1
        assert result.data[0]["name"] == "Alice Smith"

    @pytest.mark.asyncio
    async def test_query_with_in_filter(self, adapter):
        """测试 IN 过滤查询"""
        await self.clear_mongodb_database(adapter)

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
        await self.clear_mongodb_database(adapter)

        users = TestDataGenerator.generate_users(10)
        await adapter.insert("users", users)

        result = await adapter.query("users", limit=5)
        assert len(result.data) == 5

    @pytest.mark.asyncio
    async def test_update_with_filters(self, adapter):
        """测试更新操作"""
        await self.clear_mongodb_database(adapter)

        user = TestDataGenerator.random_user()
        user["name"] = "OldName"
        await adapter.insert("users", user)

        result = await adapter.update("users", {"name": "NewName"}, {"name": "OldName"})
        assert result.updated_count == 1

        # 验证更新
        query_result = await adapter.query("users", {"name": "NewName"})
        assert len(query_result.data) == 1

    @pytest.mark.asyncio
    async def test_delete_with_filters(self, adapter):
        """测试删除操作"""
        await self.clear_mongodb_database(adapter)

        user = TestDataGenerator.random_user()
        user["name"] = "ToDelete"
        await adapter.insert("users", user)

        result = await adapter.delete("users", {"name": "ToDelete"})
        assert result.deleted_count == 1

        # 验证删除
        query_result = await adapter.query("users", {"name": "ToDelete"})
        assert len(query_result.data) == 0

    @pytest.mark.asyncio
    async def test_get_capabilities(self, adapter):
        """测试获取能力信息"""
        capabilities = adapter.get_capabilities()
        assert capabilities.basic_crud is True

    @pytest.mark.asyncio
    async def test_filter_translation(self, adapter):
        """测试过滤器翻译"""
        await self.clear_mongodb_database(adapter)

        # 插入测试数据
        users = [
            {"name": "Alice", "age": 25, "active": True},
            {"name": "Bob", "age": 30, "active": False},
            {"name": "Charlie", "age": 35, "active": True},
        ]
        await adapter.insert("users", users)

        # 测试多个过滤条件
        result = await adapter.query("users", {"age__gt": 20, "active": True})
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_nested_document_query(self, adapter):
        """测试嵌套文档查询"""
        await self.clear_mongodb_database(adapter)

        # 插入嵌套文档
        user = {"name": "Alice", "address": {"city": "New York", "zip": "10001"}}
        await adapter.insert("users", user)

        # 查询嵌套字段
        result = await adapter.query("users", {"address.city": "New York"})
        assert len(result.data) == 1

    @pytest.mark.asyncio
    async def test_array_operations(self, adapter):
        """测试数组操作"""
        await self.clear_mongodb_database(adapter)

        # 插入包含数组的文档
        user = {"name": "Alice", "tags": ["python", "mongodb", "developer"]}
        await adapter.insert("users", user)

        # 查询包含特定值的数组
        result = await adapter.query("users", {"tags": "python"})
        assert len(result.data) == 1

    @pytest.mark.asyncio
    async def test_bulk_update(self, adapter):
        """测试批量更新"""
        await self.clear_mongodb_database(adapter)

        users = [
            {"name": "User1", "status": "pending"},
            {"name": "User2", "status": "pending"},
            {"name": "User3", "status": "pending"},
        ]
        await adapter.insert("users", users)

        # 批量更新：将所有 status 为 "pending" 的记录更新为 "active"
        result = await adapter.update("users", {"status": "active"}, {"status": "pending"})
        assert result.updated_count == 3

    @pytest.mark.asyncio
    async def test_bulk_delete(self, adapter):
        """测试批量删除"""
        await self.clear_mongodb_database(adapter)

        users = [
            {"name": "User1", "status": "inactive"},
            {"name": "User2", "status": "inactive"},
            {"name": "User3", "status": "active"},
        ]
        await adapter.insert("users", users)

        # 批量删除
        result = await adapter.delete("users", {"status": "inactive"})
        assert result.deleted_count == 2

        # 验证剩余数据
        remaining = await adapter.query("users")
        assert len(remaining.data) == 1
