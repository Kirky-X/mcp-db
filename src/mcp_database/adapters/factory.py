"""适配器工厂"""

from mcp_database.adapters.http.supabase import SupabaseAdapter
from mcp_database.adapters.nosql.mongodb import MongoDBAdapter
from mcp_database.adapters.nosql.opensearch import OpenSearchAdapter
from mcp_database.adapters.nosql.redis import RedisAdapter
from mcp_database.adapters.sql.base import SQLAdapter
from mcp_database.core.adapter import DatabaseAdapter
from mcp_database.core.exceptions import QueryError
from mcp_database.core.models import DatabaseConfig


class AdapterFactory:
    """数据库适配器工厂"""

    @staticmethod
    def create_adapter(config: DatabaseConfig) -> DatabaseAdapter:
        """
        根据配置创建适配器

        Args:
            config: 数据库配置

        Returns:
            DatabaseAdapter: 数据库适配器实例

        Raises:
            QueryError: 不支持的数据库类型时抛出
        """
        url = config.url.lower()

        # PostgreSQL
        if url.startswith("postgresql://") or url.startswith("postgres://"):
            return SQLAdapter(config)

        # MySQL
        elif url.startswith("mysql://") or url.startswith("mysql+"):
            return SQLAdapter(config)

        # SQLite
        elif url.startswith("sqlite://") or url.startswith("sqlite+"):
            return SQLAdapter(config)

        # MongoDB
        elif url.startswith("mongodb://") or url.startswith("mongodb+"):
            return MongoDBAdapter(config)

        # Redis
        elif url.startswith("redis://") or url.startswith("rediss://"):
            return RedisAdapter(config)

        # OpenSearch
        elif url.startswith("http://") or url.startswith("https://"):
            # 检查是否是 OpenSearch
            if ":9200" in url or ":9201" in url:
                return OpenSearchAdapter(config)
            # 检查是否是 Supabase REST API
            elif "supabase.co" in url:
                return SupabaseAdapter(config)
            else:
                raise QueryError(f"Unsupported database URL: {config.url}")

        # Supabase (PostgreSQL)
        elif "supabase" in url or url.startswith("postgresql+supabase://"):
            return SQLAdapter(config)

        else:
            raise QueryError(f"Unsupported database URL: {config.url}")

    @staticmethod
    def get_adapter_type(url: str) -> str | None:
        """
        根据 URL 获取适配器类型

        Args:
            url: 数据库 URL

        Returns:
            适配器类型，如果不支持则返回 None
        """
        url = url.lower()

        if url.startswith("postgresql://") or url.startswith("postgres://"):
            return "postgresql"
        elif url.startswith("mysql://"):
            return "mysql"
        elif url.startswith("sqlite://"):
            return "sqlite"
        elif url.startswith("mongodb://"):
            return "mongodb"
        elif url.startswith("redis://"):
            return "redis"
        elif url.startswith("http://") or url.startswith("https://"):
            if ":9200" in url or ":9201" in url:
                return "opensearch"
            elif "supabase.co" in url:
                return "supabase"
        elif "supabase" in url:
            return "supabase"

        return None
