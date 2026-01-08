"""测试 OpenSearch 适配器 - 使用真实数据库"""

import os
import uuid

import pytest

from mcp_database.adapters.nosql.opensearch import OpenSearchAdapter
from mcp_database.core.models import DatabaseConfig
from tests.utils import DatabaseTestUtils, TestDataGenerator, wait_for_database_connection


@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip OpenSearch tests in CI environment")
class TestOpenSearchAdapter:
    """测试 OpenSearch 适配器"""

    @pytest.fixture
    async def adapter(self):
        """创建 OpenSearch 适配器实例"""
        config = DatabaseConfig(url=DatabaseTestUtils.OPENSEARCH_URL)
        adapter = OpenSearchAdapter(config)

        try:
            await wait_for_database_connection(adapter, max_retries=10, delay=3.0)
            yield adapter
        finally:
            await adapter.disconnect()

    @pytest.fixture
    def index_name(self):
        """生成唯一的索引名称"""
        return f"users_{uuid.uuid4().hex[:8]}"

    @staticmethod
    async def clear_opensearch_database(adapter, index_name):
        """清理 OpenSearch 数据库中的特定索引"""
        try:
            # 删除指定索引
            await adapter._client.indices.delete(index=index_name, ignore=[400, 404])

            # 等待索引删除完成
            import asyncio

            await asyncio.sleep(0.5)
        except Exception:
            # 忽略索引不存在的错误
            pass

    @pytest.mark.asyncio
    async def test_connect_to_opensearch(self, adapter):
        """测试连接到 OpenSearch"""
        assert adapter.is_connected is True

    @pytest.mark.asyncio
    async def test_insert_single_document(self, adapter, index_name):
        """测试插入单个文档"""
        user = TestDataGenerator.random_user()
        result = await adapter.insert(index_name, user)

        assert result.inserted_count == 1
        assert len(result.inserted_ids) == 1

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_insert_multiple_documents(self, adapter, index_name):
        """测试插入多个文档"""
        users = TestDataGenerator.generate_users(10)
        result = await adapter.insert(index_name, users)

        assert result.inserted_count == 10
        assert len(result.inserted_ids) == 10

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_query_without_filters(self, adapter, index_name):
        """测试无过滤条件的查询"""
        users = TestDataGenerator.generate_users(5)
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.query(index_name)
        assert len(result.data) == 5

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_query_with_equality_filter(self, adapter, index_name):
        """测试等值过滤查询"""
        user = TestDataGenerator.random_user()
        user["name"] = "TestUser"
        await adapter.insert(index_name, user)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.query(index_name, {"name": "TestUser"})
        assert len(result.data) == 1
        assert result.data[0]["name"] == "TestUser"

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_query_with_gt_filter(self, adapter, index_name):
        """测试大于过滤查询"""
        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.query(index_name, {"age__gt": 25})
        assert len(result.data) == 2

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_query_with_lt_filter(self, adapter, index_name):
        """测试小于过滤查询"""
        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.query(index_name, {"age__lt": 35})
        assert len(result.data) == 2

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_query_with_gte_filter(self, adapter, index_name):
        """测试大于等于过滤查询"""
        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.query(index_name, {"age__gte": 30})
        assert len(result.data) == 2

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_query_with_lte_filter(self, adapter, index_name):
        """测试小于等于过滤查询"""
        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.query(index_name, {"age__lte": 30})
        assert len(result.data) == 2

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_query_with_contains_filter(self, adapter, index_name):
        """测试包含过滤查询"""
        users = [{"name": "Alice Smith"}, {"name": "Bob Johnson"}, {"name": "Charlie Brown"}]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.query(index_name, {"name__contains": "Smith"})
        assert len(result.data) == 1
        assert result.data[0]["name"] == "Alice Smith"

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_query_with_in_filter(self, adapter, index_name):
        """测试 IN 过滤查询"""
        users = [
            {"name": "User1", "age": 20},
            {"name": "User2", "age": 30},
            {"name": "User3", "age": 40},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.query(index_name, {"age__in": [20, 40]})
        assert len(result.data) == 2

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_query_with_limit(self, adapter, index_name):
        """测试限制查询结果数量"""
        users = TestDataGenerator.generate_users(10)
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.query(index_name, limit=5)
        assert len(result.data) == 5

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_update_with_filters(self, adapter, index_name):
        """测试更新操作"""
        user = TestDataGenerator.random_user()
        user["name"] = "OldName"
        await adapter.insert(index_name, user)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.update(index_name, {"name": "NewName"}, {"name": "OldName"})
        assert result.updated_count == 1

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 验证更新
        query_result = await adapter.query(index_name, {"name": "NewName"})
        assert len(query_result.data) == 1

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_delete_with_filters(self, adapter, index_name):
        """测试删除操作"""
        user = TestDataGenerator.random_user()
        user["name"] = "ToDelete"
        await adapter.insert(index_name, user)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        result = await adapter.delete(index_name, {"name": "ToDelete"})
        assert result.deleted_count == 1

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 验证删除
        query_result = await adapter.query(index_name, {"name": "ToDelete"})
        assert len(query_result.data) == 0

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_get_capabilities(self, adapter):
        """测试获取能力信息"""
        capabilities = adapter.get_capabilities()
        assert capabilities.basic_crud is True

    @pytest.mark.asyncio
    async def test_filter_translation(self, adapter, index_name):
        """测试过滤器翻译"""
        # 插入测试数据
        users = [
            {"name": "Alice", "age": 25, "active": True},
            {"name": "Bob", "age": 30, "active": False},
            {"name": "Charlie", "age": 35, "active": True},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 测试多个过滤条件
        result = await adapter.query(index_name, {"age__gt": 20, "active": True})
        assert len(result.data) == 2

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_text_search(self, adapter, index_name):
        """测试文本搜索"""
        # 插入测试数据
        users = [
            {"name": "Alice Smith", "description": "Python developer"},
            {"name": "Bob Johnson", "description": "Java developer"},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 测试文本搜索
        result = await adapter.query(index_name, {"description__contains": "Python"})
        assert len(result.data) == 1

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_bulk_update(self, adapter, index_name):
        """测试批量更新"""
        users = [
            {"name": "User1", "status": "pending"},
            {"name": "User2", "status": "pending"},
            {"name": "User3", "status": "pending"},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 批量更新：将所有 status 为 "pending" 的记录更新为 "active"
        result = await adapter.update(index_name, {"status": "active"}, {"status": "pending"})
        assert result.updated_count == 3

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, adapter, index_name):
        """测试批量删除"""
        users = [
            {"name": "User1", "status": "inactive"},
            {"name": "User2", "status": "inactive"},
            {"name": "User3", "status": "active"},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 批量删除
        result = await adapter.delete(index_name, {"status": "inactive"})
        assert result.deleted_count == 2

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 验证剩余数据
        remaining = await adapter.query(index_name)
        assert len(remaining.data) == 1

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_index_creation(self, adapter, index_name):
        """测试索引创建"""
        # 插入数据会自动创建索引
        user = TestDataGenerator.random_user()
        await adapter.insert(index_name, user)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 验证索引存在
        exists = await adapter._client.indices.exists(index=index_name)
        assert exists is True

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_range_query(self, adapter, index_name):
        """测试范围查询"""
        users = [
            {"name": "User1", "score": 85.5},
            {"name": "User2", "score": 92.3},
            {"name": "User3", "score": 78.9},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 测试浮点数过滤
        result = await adapter.query(index_name, {"score__gt": 80.0})
        assert len(result.data) == 2

        # 清理
        await self.clear_opensearch_database(adapter, index_name)

    @pytest.mark.asyncio
    async def test_boolean_filtering(self, adapter, index_name):
        """测试布尔值过滤"""
        users = [
            {"name": "User1", "active": True},
            {"name": "User2", "active": False},
            {"name": "User3", "active": True},
        ]
        await adapter.insert(index_name, users)

        # 等待索引刷新
        await adapter._client.indices.refresh(index=index_name)

        # 测试布尔值过滤
        result = await adapter.query(index_name, {"active": True})
        assert len(result.data) == 2

        # 清理
        await self.clear_opensearch_database(adapter, index_name)
