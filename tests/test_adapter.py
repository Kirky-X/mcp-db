"""测试 DatabaseAdapter 抽象基类"""

from abc import ABC

import pytest


class TestDatabaseAdapter:
    """测试 DatabaseAdapter 抽象基类"""

    def test_is_abstract_class(self):
        """测试是抽象基类"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert issubclass(DatabaseAdapter, ABC)

    def test_has_connect_method(self):
        """测试有 connect 方法"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "connect")

    def test_has_disconnect_method(self):
        """测试有 disconnect 方法"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "disconnect")

    def test_has_insert_method(self):
        """测试有 insert 方法"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "insert")

    def test_has_delete_method(self):
        """测试有 delete 方法"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "delete")

    def test_has_update_method(self):
        """测试有 update 方法"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "update")

    def test_has_query_method(self):
        """测试有 query 方法"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "query")

    def test_has_execute_method(self):
        """测试有 execute 方法"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "execute")

    def test_has_advanced_query_method(self):
        """测试有 advanced_query 方法"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "advanced_query")

    def test_has_get_capabilities_method(self):
        """测试有 get_capabilities 方法"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "get_capabilities")

    def test_cannot_instantiate_abstract_class(self):
        """测试不能直接实例化抽象类"""
        from mcp_database.core.adapter import DatabaseAdapter

        with pytest.raises(TypeError):
            DatabaseAdapter()

    def test_has_config_property(self):
        """测试有 config 属性"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "config")

    def test_has_is_connected_property(self):
        """测试有 is_connected 属性"""
        from mcp_database.core.adapter import DatabaseAdapter

        assert hasattr(DatabaseAdapter, "is_connected")


class TestConcreteAdapter:
    """测试具体适配器实现"""

    def test_concrete_adapter_can_be_instantiated(self):
        """测试具体适配器可以实例化"""
        from mcp_database.core.adapter import DatabaseAdapter
        from mcp_database.core.models import (
            AdvancedResult,
            Capability,
            DatabaseConfig,
            DeleteResult,
            ExecuteResult,
            InsertResult,
            QueryResult,
            UpdateResult,
        )

        class ConcreteAdapter(DatabaseAdapter):
            """具体适配器实现"""

            def __init__(self, config: DatabaseConfig):
                super().__init__(config)
                self._connected = False

            async def connect(self) -> None:
                self._connected = True

            async def disconnect(self) -> None:
                self._connected = False

            async def insert(self, table: str, data: dict) -> InsertResult:
                pass

            async def delete(self, table: str, filters: dict) -> DeleteResult:
                pass

            async def update(self, table: str, data: dict, filters: dict) -> UpdateResult:
                pass

            async def query(
                self, table: str, filters: dict = None, limit: int = None
            ) -> QueryResult:
                pass

            async def execute(self, query: str, params: dict = None) -> ExecuteResult:
                pass

            async def advanced_query(self, operation: str, params: dict) -> AdvancedResult:
                pass

            def get_capabilities(self) -> Capability:
                pass

            @property
            def is_connected(self) -> bool:
                return self._connected

        config = DatabaseConfig(url="sqlite:///test.db")
        adapter = ConcreteAdapter(config)
        assert adapter.config == config
        assert adapter.is_connected is False
