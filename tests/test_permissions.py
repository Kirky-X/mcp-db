"""权限控制测试"""

from unittest.mock import patch

import pytest

from mcp_database.core.exceptions import PermissionError
from mcp_database.core.permissions import (
    PermissionManager,
    check_delete_permission,
    check_insert_permission,
    require_permission,
)


class TestPermissionManager:
    """测试权限管理器"""

    def test_check_insert_permission_allowed(self):
        """测试检查插入权限（允许）"""
        from mcp_database.config.settings import Settings

        config = Settings(enable_insert=True)
        manager = PermissionManager(config)

        assert manager.check_permission("insert") is True

    def test_check_insert_permission_denied(self):
        """测试检查插入权限（拒绝）"""
        from mcp_database.config.settings import Settings

        config = Settings(enable_insert=False)
        manager = PermissionManager(config)

        with pytest.raises(PermissionError) as exc_info:
            manager.check_permission("insert")

        assert "insert" in str(exc_info.value)

    def test_check_dangerous_operation_allowed(self):
        """测试检查危险操作权限（允许）"""
        from mcp_database.config.settings import Settings

        config = Settings(dangerous_agree=True)
        manager = PermissionManager(config)

        assert manager.check_permission("delete", dangerous=True) is True

    def test_check_dangerous_operation_denied(self):
        """测试检查危险操作权限（拒绝）"""
        from mcp_database.config.settings import Settings

        config = Settings(dangerous_agree=False)
        manager = PermissionManager(config)

        with pytest.raises(PermissionError) as exc_info:
            manager.check_permission("delete", dangerous=True)

        assert "Dangerous operations" in str(exc_info.value)

    def test_check_both_permissions_denied(self):
        """测试检查两种权限都被拒绝"""
        from mcp_database.config.settings import Settings

        config = Settings(enable_delete=False, dangerous_agree=False)
        manager = PermissionManager(config)

        with pytest.raises(PermissionError) as exc_info:
            manager.check_permission("delete", dangerous=True)

        assert "not allowed" in str(exc_info.value)


class TestPermissionDecorators:
    """测试权限装饰器"""

    @pytest.mark.asyncio
    async def test_require_permission_async_allowed(self):
        """测试权限装饰器（异步，允许）"""
        from mcp_database.config.settings import Settings

        with patch("mcp_database.core.permissions.settings", Settings(enable_insert=True)):

            @require_permission("insert")
            async def test_func():
                return "success"

            result = await test_func()
            assert result == "success"

    @pytest.mark.asyncio
    async def test_require_permission_async_denied(self):
        """测试权限装饰器（异步，拒绝）"""
        from mcp_database.config.settings import Settings

        with patch("mcp_database.core.permissions.settings", Settings(enable_insert=False)):

            @require_permission("insert")
            async def test_func():
                return "success"

            with pytest.raises(PermissionError):
                await test_func()

    def test_require_permission_sync_allowed(self):
        """测试权限装饰器（同步，允许）"""
        from mcp_database.config.settings import Settings

        with patch("mcp_database.core.permissions.settings", Settings(enable_insert=True)):

            @require_permission("insert")
            def test_func():
                return "success"

            result = test_func()
            assert result == "success"

    def test_require_permission_sync_denied(self):
        """测试权限装饰器（同步，拒绝）"""
        from mcp_database.config.settings import Settings

        with patch("mcp_database.core.permissions.settings", Settings(enable_insert=False)):

            @require_permission("insert")
            def test_func():
                return "success"

            with pytest.raises(PermissionError):
                test_func()

    @pytest.mark.asyncio
    async def test_check_insert_permission_decorator(self):
        """测试插入权限装饰器"""
        from mcp_database.config.settings import Settings

        with patch("mcp_database.core.permissions.settings", Settings(enable_insert=True)):

            @check_insert_permission
            async def test_func():
                return "success"

            result = await test_func()
            assert result == "success"

    @pytest.mark.asyncio
    async def test_check_delete_permission_decorator(self):
        """测试删除权限装饰器"""
        from mcp_database.config.settings import Settings

        with patch("mcp_database.core.permissions.settings", Settings(dangerous_agree=True)):

            @check_delete_permission
            async def test_func():
                return "success"

            result = await test_func()
            assert result == "success"
