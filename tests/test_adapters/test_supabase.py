"""测试 Supabase 适配器 - 使用真实数据库"""

import os

import pytest

from mcp_database.adapters.factory import AdapterFactory
from mcp_database.core.models import DatabaseConfig
from tests.utils import wait_for_database_connection

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


@pytest.mark.skipif(not (SUPABASE_URL and SUPABASE_KEY), reason="Supabase credentials not provided")
class TestSupabaseAdapter:
    """测试 Supabase 适配器"""

    @pytest.fixture
    async def adapter(self):
        """创建 Supabase 适配器实例"""
        # Supabase REST API 适配器
        # 使用 SUPABASE_URL 环境变量
        supabase_url = os.getenv("SUPABASE_URL")

        if not supabase_url:
            pytest.skip("SUPABASE_URL environment variable not set")

        config = DatabaseConfig(url=supabase_url)
        adapter = AdapterFactory.create_adapter(config)

        try:
            await wait_for_database_connection(adapter, max_retries=10, delay=3.0)
            yield adapter
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_connect_to_supabase(self, adapter):
        """测试连接到 Supabase"""
        assert adapter.is_connected is True

    # 注意：以下测试需要 Supabase 数据库中有对应的表
    # 如果 Supabase 数据库中没有这些表，这些测试会跳过

    @pytest.mark.asyncio
    async def test_insert_single_document(self, adapter):
        """测试插入单个文档"""
        # 创建符合 users 表结构的测试数据
        user = {"name": "TestUser", "email": "test@example.com", "age": 25, "active": True}
        result = await adapter.insert("users", user)

        assert result.inserted_count == 1
        assert len(result.inserted_ids) == 1

        # 清理
        if result.inserted_ids:
            await adapter.delete("users", {"id": result.inserted_ids[0]})

    @pytest.mark.asyncio
    async def test_query_without_filters(self, adapter):
        """测试无过滤条件的查询"""
        # 尝试查询数据，如果表不存在则跳过
        try:
            result = await adapter.query("users")
            # 如果查询成功，返回结果
            assert isinstance(result.data, list)
        except Exception as e:
            if "Could not find the table" in str(e):
                pytest.skip("Table 'users' does not exist in Supabase database")
            else:
                raise

    @pytest.mark.asyncio
    async def test_query_with_equality_filter(self, adapter):
        """测试等值过滤查询"""
        # 尝试查询数据，如果表不存在则跳过
        try:
            result = await adapter.query("users", {"name": "TestUser"})
            # 如果查询成功，返回结果
            assert isinstance(result.data, list)
        except Exception as e:
            if "Could not find the table" in str(e):
                pytest.skip("Table 'users' does not exist in Supabase database")
            else:
                raise

    @pytest.mark.asyncio
    async def test_update_with_filters(self, adapter):
        """测试更新操作"""
        # 尝试更新数据，如果表不存在则跳过
        try:
            result = await adapter.update("users", {"name": "NewName"}, {"name": "OldName"})
            # 如果更新成功，返回结果
            assert isinstance(result.updated_count, int)
        except Exception as e:
            if "Could not find the table" in str(e):
                pytest.skip("Table 'users' does not exist in Supabase database")
            else:
                raise

    @pytest.mark.asyncio
    async def test_delete_with_filters(self, adapter):
        """测试删除操作"""
        # 尝试删除数据，如果表不存在则跳过
        try:
            result = await adapter.delete("users", {"name": "ToDelete"})
            # 如果删除成功，返回结果
            assert isinstance(result.deleted_count, int)
        except Exception as e:
            if "Could not find the table" in str(e):
                pytest.skip("Table 'users' does not exist in Supabase database")
            else:
                raise
