"""测试核心数据模型"""

import pytest
from pydantic import ValidationError


class TestInsertResult:
    """测试 InsertResult 模型"""

    def test_insert_result_single(self):
        """测试单条插入结果"""
        from mcp_database.core.models import InsertResult

        result = InsertResult(inserted_count=1, inserted_ids=[1])
        assert result.inserted_count == 1
        assert result.inserted_ids == [1]
        assert result.success is True

    def test_insert_result_batch(self):
        """测试批量插入结果"""
        from mcp_database.core.models import InsertResult

        result = InsertResult(inserted_count=3, inserted_ids=[1, 2, 3])
        assert result.inserted_count == 3
        assert len(result.inserted_ids) == 3

    def test_insert_result_default_success(self):
        """测试默认 success 值"""
        from mcp_database.core.models import InsertResult

        result = InsertResult(inserted_count=1, inserted_ids=[1])
        assert result.success is True


class TestUpdateResult:
    """测试 UpdateResult 模型"""

    def test_update_result(self):
        """测试更新结果"""
        from mcp_database.core.models import UpdateResult

        result = UpdateResult(updated_count=5)
        assert result.updated_count == 5
        assert result.success is True

    def test_update_result_zero(self):
        """测试零更新"""
        from mcp_database.core.models import UpdateResult

        result = UpdateResult(updated_count=0)
        assert result.updated_count == 0


class TestDeleteResult:
    """测试 DeleteResult 模型"""

    def test_delete_result(self):
        """测试删除结果"""
        from mcp_database.core.models import DeleteResult

        result = DeleteResult(deleted_count=3)
        assert result.deleted_count == 3
        assert result.success is True


class TestQueryResult:
    """测试 QueryResult 模型"""

    def test_query_result(self):
        """测试查询结果"""
        from mcp_database.core.models import QueryResult

        result = QueryResult(data=[{"id": 1, "name": "Alice"}], count=1)
        assert len(result.data) == 1
        assert result.count == 1
        assert result.has_more is False

    def test_query_result_with_pagination(self):
        """测试分页查询结果"""
        from mcp_database.core.models import QueryResult

        result = QueryResult(data=[{"id": i} for i in range(10)], count=100, has_more=True)
        assert len(result.data) == 10
        assert result.count == 100
        assert result.has_more is True


class TestExecuteResult:
    """测试 ExecuteResult 模型"""

    def test_execute_result_with_data(self):
        """测试带数据的执行结果"""
        from mcp_database.core.models import ExecuteResult

        result = ExecuteResult(rows_affected=5, data=[{"id": 1}])
        assert result.rows_affected == 5
        assert result.data is not None
        assert result.success is True

    def test_execute_result_without_data(self):
        """测试不带数据的执行结果"""
        from mcp_database.core.models import ExecuteResult

        result = ExecuteResult(rows_affected=5)
        assert result.rows_affected == 5
        assert result.data is None


class TestAdvancedResult:
    """测试 AdvancedResult 模型"""

    def test_advanced_result(self):
        """测试高级查询结果"""
        from mcp_database.core.models import AdvancedResult

        result = AdvancedResult(operation="transaction", data={"committed": True})
        assert result.operation == "transaction"
        assert result.data is not None
        assert result.success is True


class TestCapability:
    """测试 Capability 模型"""

    def test_capability_default(self):
        """测试默认能力"""
        from mcp_database.core.models import Capability

        capability = Capability()
        assert capability.basic_crud is True
        assert capability.transactions is False
        assert capability.joins is False
        assert capability.aggregation is False
        assert capability.full_text_search is False
        assert capability.geospatial is False

    def test_capability_custom(self):
        """测试自定义能力"""
        from mcp_database.core.models import Capability

        capability = Capability(transactions=True, joins=True, aggregation=True)
        assert capability.transactions is True
        assert capability.joins is True
        assert capability.aggregation is True


class TestDatabaseConfig:
    """测试 DatabaseConfig 模型"""

    def test_database_config_from_url(self):
        """测试从 URL 创建配置"""
        from mcp_database.core.models import DatabaseConfig

        config = DatabaseConfig(url="postgresql://localhost/test")
        assert config.url == "postgresql://localhost/test"
        assert config.pool_size == 5
        assert config.max_overflow == 10

    def test_database_config_with_pool_params(self):
        """测试带连接池参数的配置"""
        from mcp_database.core.models import DatabaseConfig

        config = DatabaseConfig(url="postgresql://localhost/test", pool_size=20, max_overflow=20)
        assert config.pool_size == 20
        assert config.max_overflow == 20

    def test_database_config_timeout(self):
        """测试超时配置"""
        from mcp_database.core.models import DatabaseConfig

        config = DatabaseConfig(
            url="postgresql://localhost/test", connect_timeout=30, query_timeout=60
        )
        assert config.connect_timeout == 30
        assert config.query_timeout == 60

    def test_database_config_empty_url(self):
        """测试空 URL 应该失败"""
        from mcp_database.core.models import DatabaseConfig

        with pytest.raises(ValidationError):
            DatabaseConfig(url="")
