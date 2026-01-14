"""权限控制"""

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any

from mcp_database.config.settings import settings
from mcp_database.core.exceptions import PermissionError


class PermissionManager:
    """权限管理器"""

    def __init__(self, config=None):
        """
        初始化权限管理器

        Args:
            config: 配置对象，如果为 None 则使用全局配置
        """
        self._config = config

    def check_permission(self, operation: str, dangerous: bool = False) -> bool:
        """
        检查操作权限

        Args:
            operation: 操作类型（insert, update, delete, execute）
            dangerous: 是否为危险操作

        Returns:
            bool: 是否允许

        Raises:
            PermissionError: 权限不足时抛出
        """
        config = self._config if self._config is not None else settings
        if not config.is_operation_allowed(operation):
            raise PermissionError(f"Operation '{operation}' is not allowed")

        if dangerous and not config.is_dangerous_operation_allowed():
            raise PermissionError(
                "Dangerous operations are not allowed. Set DANGEROUS_AGREE=true to enable."
            )

        return True

    @classmethod
    def get_instance(cls, config=None) -> "PermissionManager":
        """
        获取单例实例

        Args:
            config: 可选的配置对象，如果为 None 则使用全局配置

        Returns:
            PermissionManager 实例
        """
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = cls(config if config is not None else settings)
        elif config is not None:
            cls._instance = cls(config)
        return cls._instance


def require_permission(operation: str, dangerous: bool = False):
    """
    权限检查装饰器

    Args:
        operation: 操作类型
        dangerous: 是否为危险操作

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            PermissionManager.get_instance().check_permission(operation, dangerous)
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            PermissionManager.get_instance().check_permission(operation, dangerous)
            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def check_insert_permission(func: Callable) -> Callable:
    """检查插入权限装饰器"""
    return require_permission("insert")(func)


def check_update_permission(func: Callable) -> Callable:
    """检查更新权限装饰器"""
    return require_permission("update")(func)


def check_delete_permission(func: Callable) -> Callable:
    """检查删除权限装饰器"""
    return require_permission("delete", dangerous=True)(func)


def check_execute_permission(func: Callable) -> Callable:
    """检查执行权限装饰器"""
    return require_permission("execute", dangerous=True)(func)
