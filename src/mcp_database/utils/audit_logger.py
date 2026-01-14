"""审计日志系统"""

import asyncio
import json
import logging
import os
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

from mcp_database.core.models import DatabaseConfig

# 敏感字段白名单 - 这些字段的值会被脱敏
SENSITIVE_FIELDS = frozenset(
    {
        "password",
        "secret",
        "api_key",
        "token",
        "credential",
        "auth",
        "authorization",
        "private_key",
        "access_key",
        "passphrase",
        "session_id",
        "refresh_token",
        "pass_code",
        "pin",
        "security_answer",
    }
)


class AuditLogger:
    """审计日志记录器"""

    def __init__(self, config: DatabaseConfig | None = None):
        """
        初始化审计日志记录器

        Args:
            config: 数据库配置
        """
        self._config = config
        self._logger = logging.getLogger("mcp_database.audit")
        self._logger.setLevel(logging.INFO)

        # 从环境变量或配置中获取审计日志路径
        audit_log_path = self._get_audit_log_path()

        # 确保目录存在
        log_dir = os.path.dirname(audit_log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 创建文件处理器
        if not self._logger.handlers:
            handler = logging.FileHandler(audit_log_path)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def _sanitize_value(self, value: Any) -> Any:
        """
        递归清理值中的敏感信息

        Args:
            value: 要清理的值

        Returns:
            清理后的值
        """
        if isinstance(value, str):
            return "[REDACTED]"

        elif isinstance(value, dict):
            return {k: self._sanitize_value(v) for k, v in value.items()}

        elif isinstance(value, list):
            return [self._sanitize_value(item) for item in value]

        elif isinstance(value, set):
            sanitized = set()
            for item in value:
                if isinstance(item, str):
                    sanitized.add("[REDACTED]")
                else:
                    sanitized.add(self._sanitize_value(item))
            return sanitized

        elif isinstance(value, tuple):
            return tuple(self._sanitize_value(item) for item in value)

        return value

    def _is_sensitive_key(self, key: str) -> bool:
        """
        检查键是否为敏感字段

        Args:
            key: 字段名

        Returns:
            是否为敏感字段
        """
        key_lower = key.lower()
        return any(sensitive in key_lower for sensitive in SENSITIVE_FIELDS)

    def _sanitize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        移除或脱敏敏感参数

        Args:
            params: 原始参数字典

        Returns:
            清理后的参数字典
        """
        if not params:
            return {}

        sanitized = {}
        for key, value in params.items():
            if self._is_sensitive_key(key):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_params(value)
            elif isinstance(value, list):
                sanitized[key] = self._sanitize_list(value)
            else:
                sanitized[key] = value
        return sanitized

    def _sanitize_list(self, items: list) -> list:
        """
        递归清理列表中的敏感信息

        Args:
            items: 原始列表

        Returns:
            清理后的列表
        """
        sanitized = []
        for item in items:
            if isinstance(item, dict):
                sanitized.append(self._sanitize_params(item))
            else:
                sanitized.append(item)
        return sanitized

    def _get_audit_log_path(self) -> str:
        """
        获取审计日志路径

        优先级：
        1. 环境变量 MCP_AUDIT_LOG_PATH
        2. 配置文件中的 audit_log_path
        3. 默认值 ./logs/audit.log

        Returns:
            审计日志文件路径
        """
        # 1. 从环境变量获取
        env_path = os.getenv("MCP_AUDIT_LOG_PATH")
        if env_path:
            return env_path

        # 2. 从配置获取
        if self._config and hasattr(self._config, "options") and self._config.options:
            if "audit_log_path" in self._config.options:
                return self._config.options["audit_log_path"]

        # 3. 使用默认值
        return "./logs/audit.log"

    def log_operation(
        self,
        operation: str,
        table: str,
        params: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        """
        记录操作日志

        Args:
            operation: 操作类型（insert, update, delete, query, execute）
            table: 表名
            params: 操作参数（已脱敏）
            result: 操作结果
            error: 错误信息
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "table": table,
            "params": self._sanitize_params(params) if params else {},
            "result": result or {},
            "error": error,
        }

        if error:
            self._logger.error(json.dumps(log_entry))
        else:
            self._logger.info(json.dumps(log_entry))

    def log_execute(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        """
        记录 execute 操作日志

        Args:
            query: 查询语句类型（不记录原始 SQL）
            params: 查询参数（已脱敏）
            result: 执行结果
            error: 错误信息
        """
        # 解析查询类型，不记录原始 SQL 内容
        query_type = "unknown"
        if query:
            query_upper = query.strip().upper()
            for op in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]:
                if query_upper.startswith(op):
                    query_type = op
                    break

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": "execute",
            "query_type": query_type,
            "params": self._sanitize_params(params) if params else {},
            "result": result or {},
            "error": error,
        }

        if error:
            self._logger.error(json.dumps(log_entry))
        else:
            self._logger.info(json.dumps(log_entry))


def audit_log(operation: str):
    """
    审计日志装饰器

    Args:
        operation: 操作类型

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            table = args[0] if args else kwargs.get("table", "unknown")
            logger = getattr(self, "_audit_logger", None)

            try:
                result = await func(self, *args, **kwargs)
                if logger:
                    logger.log_operation(
                        operation=operation, table=table, params=kwargs, result={"success": True}
                    )
                return result
            except Exception as e:
                if logger:
                    logger.log_operation(
                        operation=operation, table=table, params=kwargs, error=str(e)
                    )
                raise

        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            table = args[0] if args else kwargs.get("table", "unknown")
            logger = getattr(self, "_audit_logger", None)

            try:
                result = func(self, *args, **kwargs)
                if logger:
                    logger.log_operation(
                        operation=operation, table=table, params=kwargs, result={"success": True}
                    )
                return result
            except Exception as e:
                if logger:
                    logger.log_operation(
                        operation=operation, table=table, params=kwargs, error=str(e)
                    )
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def audit_execute(func: Callable) -> Callable:
    """
    execute 操作审计装饰器

    Args:
        func: 被装饰的函数

    Returns:
        装饰后的函数
    """

    @wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        query = args[0] if args else kwargs.get("query", "unknown")
        logger = getattr(self, "_audit_logger", None)

        try:
            result = await func(self, *args, **kwargs)
            if logger:
                logger.log_execute(
                    query=query, params=kwargs.get("params"), result={"success": True}
                )
            return result
        except Exception as e:
            if logger:
                logger.log_execute(query=query, params=kwargs.get("params"), error=str(e))
            raise

    @wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        query = args[0] if args else kwargs.get("query", "unknown")
        logger = getattr(self, "_audit_logger", None)

        try:
            result = func(self, *args, **kwargs)
            if logger:
                logger.log_execute(
                    query=query, params=kwargs.get("params"), result={"success": True}
                )
            return result
        except Exception as e:
            if logger:
                logger.log_execute(query=query, params=kwargs.get("params"), error=str(e))
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
