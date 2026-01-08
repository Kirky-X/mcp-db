"""审计日志系统"""

import json
import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any

from mcp_database.core.models import DatabaseConfig


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
            params: 操作参数
            result: 操作结果
            error: 错误信息
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "table": table,
            "params": params or {},
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
            query: 查询语句
            params: 查询参数
            result: 执行结果
            error: 错误信息
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": "execute",
            "query": query,
            "params": params or {},
            "result": result or {},
            "error": error,
        }

        if error:
            self._logger.error(json.dumps(log_entry))
        else:
            self._logger.warning(json.dumps(log_entry))  # execute 操作使用 warning 级别


def audit_log(operation: str):
    """
    审计日志装饰器

    Args:
        operation: 操作类型

    Returns:
        装饰器函数
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            table = args[0] if args else kwargs.get("table", "unknown")
            logger = getattr(self, "_audit_logger", None)

            try:
                # 执行操作
                result = await func(self, *args, **kwargs)

                # 记录成功日志
                if logger:
                    logger.log_operation(
                        operation=operation, table=table, params=kwargs, result={"success": True}
                    )

                return result

            except Exception as e:
                # 记录错误日志
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
                # 执行操作
                result = func(self, *args, **kwargs)

                # 记录成功日志
                if logger:
                    logger.log_operation(
                        operation=operation, table=table, params=kwargs, result={"success": True}
                    )

                return result

            except Exception as e:
                # 记录错误日志
                if logger:
                    logger.log_operation(
                        operation=operation, table=table, params=kwargs, error=str(e)
                    )
                raise

        # 根据函数类型返回对应的包装器
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def audit_execute(func):
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
            # 执行操作
            result = await func(self, *args, **kwargs)

            # 记录成功日志
            if logger:
                logger.log_execute(
                    query=query, params=kwargs.get("params"), result={"success": True}
                )

            return result

        except Exception as e:
            # 记录错误日志
            if logger:
                logger.log_execute(query=query, params=kwargs.get("params"), error=str(e))
            raise

    @wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        query = args[0] if args else kwargs.get("query", "unknown")
        logger = getattr(self, "_audit_logger", None)

        try:
            # 执行操作
            result = func(self, *args, **kwargs)

            # 记录成功日志
            if logger:
                logger.log_execute(
                    query=query, params=kwargs.get("params"), result={"success": True}
                )

            return result

        except Exception as e:
            # 记录错误日志
            if logger:
                logger.log_execute(query=query, params=kwargs.get("params"), error=str(e))
            raise

    # 根据函数类型返回对应的包装器
    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
