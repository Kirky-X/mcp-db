"""配置管理"""

from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from mcp_database.core.models import DatabaseConfig


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # 数据库配置
    database_url: str = "sqlite:///./database.db"

    # 权限配置
    enable_insert: bool = True
    enable_update: bool = True
    enable_delete: bool = True
    dangerous_agree: bool = False

    # MCP 配置
    mcp_server_name: str = "mcp-database"
    mcp_server_version: str = "0.1.0"

    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 性能配置
    max_connections: int = 10
    query_timeout: int = 30

    @classmethod
    def load_from_env(cls) -> "Settings":
        """
        从环境变量加载配置

        Returns:
            Settings: 配置实例
        """
        return cls()

    def get_database_config(self) -> "DatabaseConfig":
        """
        获取数据库配置

        Returns:
            DatabaseConfig: 数据库配置
        """
        from mcp_database.core.models import DatabaseConfig

        return DatabaseConfig(
            url=self.database_url,
            pool_size=self.max_connections,
            max_overflow=5,
            pool_timeout=self.query_timeout,
        )

    def is_operation_allowed(self, operation: str) -> bool:
        """
        检查操作是否允许

        Args:
            operation: 操作类型（insert, update, delete）

        Returns:
            bool: 是否允许
        """
        if operation == "insert":
            return self.enable_insert
        elif operation == "update":
            return self.enable_update
        elif operation == "delete":
            return self.enable_delete or self.dangerous_agree
        else:
            return True

    def is_dangerous_operation_allowed(self) -> bool:
        """
        检查危险操作是否允许

        Returns:
            bool: 是否允许
        """
        return self.dangerous_agree


# 全局配置实例
settings = Settings.load_from_env()
