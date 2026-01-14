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
    def _get_url_prefix_type(url: str) -> str | None:
        """
        从 URL 提取协议前缀作为类型标识

        Args:
            url: 数据库 URL

        Returns:
            类型标识字符串，如 "postgresql", "mysql", "mongodb" 等
        """
        url_lower = url.lower()
        for prefix in [
            "postgresql://",
            "postgresql+",  # Add postgresql+ scheme
            "postgres://",
            "mysql://",
            "mysql+",
            "sqlite://",
            "sqlite+",
            "mongodb://",
            "mongodb+",
            "redis://",
            "rediss://",
        ]:
            if url_lower.startswith(prefix):
                # 提取协议名（去掉 :// 后缀）
                return prefix.rstrip(":/+")
        if url_lower.startswith("http://") or url_lower.startswith("https://"):
            return "http"
        return None

    @staticmethod
    def _get_special_database_type(url: str) -> str | None:
        """
        检测特殊数据库类型（通过端口或域名）

        Args:
            url: 数据库 URL

        Returns:
            特殊类型标识，如 "opensearch", "supabase"，普通类型返回 None
        """
        url_lower = url.lower()
        # OpenSearch detection (by port)
        if ":9200" in url_lower or ":9201" in url_lower:
            return "opensearch"
        # Supabase detection (only by domain for get_adapter_type, scheme handled separately)
        if "supabase.co" in url_lower:
            return "supabase"
        return None

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
        url = config.url

        # 首先检查特殊类型
        special_type = AdapterFactory._get_special_database_type(url)
        if special_type == "opensearch":
            return OpenSearchAdapter(config)
        if special_type == "supabase":
            return SupabaseAdapter(config)

        # 然后检查协议前缀
        prefix_type = AdapterFactory._get_url_prefix_type(url)

        if prefix_type in ("postgresql", "postgres", "mysql", "sqlite"):
            return SQLAdapter(config)
        elif prefix_type == "mongodb":
            return MongoDBAdapter(config)
        elif prefix_type == "redis":
            return RedisAdapter(config)
        elif prefix_type == "http":
            # 检查是否是 OpenSearch
            if ":9200" in url.lower() or ":9201" in url.lower():
                return OpenSearchAdapter(config)
            # 检查是否是 Supabase REST API (by domain)
            if "supabase.co" in url.lower():
                return SupabaseAdapter(config)
            raise QueryError(f"Unsupported database URL: {config.url}")
        elif url.lower().startswith("postgresql+supabase://") or "supabase" in url.lower():
            # postgresql+supabase:// scheme should return SQLAdapter (not SupabaseAdapter)
            return SQLAdapter(config)

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
        url_lower = url.lower()

        # 检查特殊类型（HTTP-based）
        if url_lower.startswith("http://") or url_lower.startswith("https://"):
            if ":9200" in url_lower or ":9201" in url_lower:
                return "opensearch"
            if "supabase.co" in url_lower:
                return "supabase"

        # 检查 supabase 字符串（用于 postgresql+supabase:// 等）
        # 这个检查必须在 prefix_type 检查之前，因为原始代码的行为是：
        # get_adapter_type("postgresql+supabase://...") 返回 "supabase"
        # 但 create_adapter("postgresql+supabase://...") 返回 SQLAdapter
        if "supabase" in url_lower:
            return "supabase"

        # 检查普通类型
        prefix_type = AdapterFactory._get_url_prefix_type(url)
        if prefix_type:
            # 映射到标准类型名
            type_mapping = {
                "postgresql": "postgresql",
                "postgres": "postgresql",
                "mysql": "mysql",
                "sqlite": "sqlite",
                "mongodb": "mongodb",
                "redis": "redis",
            }
            return type_mapping.get(prefix_type)

        return None
