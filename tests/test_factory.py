"""适配器工厂测试"""

import pytest

from mcp_database.adapters.factory import AdapterFactory
from mcp_database.core.models import DatabaseConfig


class TestAdapterFactory:
    """测试适配器工厂"""

    def test_create_postgresql_adapter(self):
        """测试创建 PostgreSQL 适配器"""
        config = DatabaseConfig(url="postgresql://user:pass@localhost:5432/db")
        adapter = AdapterFactory.create_adapter(config)

        from mcp_database.adapters.sql.base import SQLAdapter

        assert isinstance(adapter, SQLAdapter)

    def test_create_mysql_adapter(self):
        """测试创建 MySQL 适配器"""
        config = DatabaseConfig(url="mysql://user:pass@localhost:3306/db")
        adapter = AdapterFactory.create_adapter(config)

        from mcp_database.adapters.sql.base import SQLAdapter

        assert isinstance(adapter, SQLAdapter)

    def test_create_sqlite_adapter(self):
        """测试创建 SQLite 适配器"""
        config = DatabaseConfig(url="sqlite:///test.db")
        adapter = AdapterFactory.create_adapter(config)

        from mcp_database.adapters.sql.base import SQLAdapter

        assert isinstance(adapter, SQLAdapter)

    def test_create_mongodb_adapter(self):
        """测试创建 MongoDB 适配器"""
        config = DatabaseConfig(url="mongodb://localhost:27017/db")
        adapter = AdapterFactory.create_adapter(config)

        from mcp_database.adapters.nosql.mongodb import MongoDBAdapter

        assert isinstance(adapter, MongoDBAdapter)

    def test_create_redis_adapter(self):
        """测试创建 Redis 适配器"""
        config = DatabaseConfig(url="redis://localhost:6379/0")
        adapter = AdapterFactory.create_adapter(config)

        from mcp_database.adapters.nosql.redis import RedisAdapter

        assert isinstance(adapter, RedisAdapter)

    def test_create_opensearch_adapter(self):
        """测试创建 OpenSearch 适配器"""
        config = DatabaseConfig(url="http://localhost:9200")
        adapter = AdapterFactory.create_adapter(config)

        from mcp_database.adapters.nosql.opensearch import OpenSearchAdapter

        assert isinstance(adapter, OpenSearchAdapter)

    def test_create_supabase_adapter(self):
        """测试创建 Supabase 适配器"""
        config = DatabaseConfig(url="postgresql+supabase://user:pass@host/db")
        adapter = AdapterFactory.create_adapter(config)

        from mcp_database.adapters.sql.base import SQLAdapter

        assert isinstance(adapter, SQLAdapter)

    def test_unsupported_database(self):
        """测试不支持的数据库类型"""
        config = DatabaseConfig(url="unsupported://localhost/db")

        from mcp_database.core.exceptions import QueryError

        with pytest.raises(QueryError):
            AdapterFactory.create_adapter(config)

    def test_get_adapter_type(self):
        """测试获取适配器类型"""
        assert AdapterFactory.get_adapter_type("postgresql://localhost/db") == "postgresql"
        assert AdapterFactory.get_adapter_type("mysql://localhost/db") == "mysql"
        assert AdapterFactory.get_adapter_type("sqlite:///test.db") == "sqlite"
        assert AdapterFactory.get_adapter_type("mongodb://localhost/db") == "mongodb"
        assert AdapterFactory.get_adapter_type("redis://localhost/0") == "redis"
        assert AdapterFactory.get_adapter_type("http://localhost:9200") == "opensearch"
        # postgresql+supabase:// returns "postgresql" to match create_adapter behavior
        assert AdapterFactory.get_adapter_type("postgresql+supabase://localhost/db") == "postgresql"
        assert AdapterFactory.get_adapter_type("unsupported://localhost/db") is None
