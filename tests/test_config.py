"""配置管理测试"""

import os
from unittest.mock import patch


class TestSettings:
    """测试配置管理"""

    def test_default_settings(self):
        """测试默认配置"""
        from mcp_database.config.settings import Settings

        settings = Settings()

        assert settings.database_url == "sqlite:///./database.db"
        assert settings.enable_insert is True
        assert settings.enable_update is True
        assert settings.enable_delete is True
        assert settings.dangerous_agree is False

    def test_load_from_env(self):
        """测试从环境变量加载"""
        from mcp_database.config.settings import Settings

        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://localhost/test",
                "ENABLE_INSERT": "false",
                "ENABLE_DELETE": "false",
                "DANGEROUS_AGREE": "true",
            },
        ):
            settings = Settings.load_from_env()

            assert settings.database_url == "postgresql://localhost/test"
            assert settings.enable_insert is False
            assert settings.enable_delete is False
            assert settings.dangerous_agree is True

    def test_get_database_config(self):
        """测试获取数据库配置"""
        from mcp_database.config.settings import Settings
        from mcp_database.core.models import DatabaseConfig

        settings = Settings()
        db_config = settings.get_database_config()

        assert isinstance(db_config, DatabaseConfig)
        assert db_config.url == "sqlite:///./database.db"
        assert db_config.pool_size == 10

    def test_is_operation_allowed(self):
        """测试操作权限检查"""
        from mcp_database.config.settings import Settings

        settings = Settings()

        # 默认权限
        assert settings.is_operation_allowed("insert") is True
        assert settings.is_operation_allowed("update") is True
        assert settings.is_operation_allowed("delete") is True
        assert settings.is_operation_allowed("query") is True

        # 禁用删除
        settings.enable_delete = False
        assert settings.is_operation_allowed("delete") is False

        # 启用危险操作
        settings.dangerous_agree = True
        assert settings.is_operation_allowed("delete") is True

    def test_is_dangerous_operation_allowed(self):
        """测试危险操作权限检查"""
        from mcp_database.config.settings import Settings

        settings = Settings()

        # 默认不允许危险操作
        assert settings.is_dangerous_operation_allowed() is False

        # 启用危险操作
        settings.dangerous_agree = True
        assert settings.is_dangerous_operation_allowed() is True

    def test_global_settings_instance(self):
        """测试全局配置实例"""
        from mcp_database.config.settings import settings

        assert settings is not None
        assert isinstance(settings.database_url, str)
