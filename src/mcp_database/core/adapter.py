"""DatabaseAdapter 抽象基类"""

from abc import ABC, abstractmethod
from typing import Any

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


class DatabaseAdapter(ABC):
    """
    数据库适配器抽象基类

    所有数据库适配器都必须继承此类并实现所有抽象方法。
    """

    def __init__(self, config: DatabaseConfig):
        """
        初始化适配器

        Args:
            config: 数据库配置
        """
        self._config = config

    @property
    def config(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self._config

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """是否已连接"""
        pass

    @abstractmethod
    async def connect(self) -> None:
        """
        连接到数据库

        Raises:
            ConnectionError: 连接失败时抛出
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开数据库连接"""
        pass

    @abstractmethod
    async def insert(self, table: str, data: dict[str, Any]) -> InsertResult:
        """
        插入数据

        Args:
            table: 表名
            data: 要插入的数据字典

        Returns:
            InsertResult: 插入结果

        Raises:
            PermissionError: 权限不足时抛出
            QueryError: 查询错误时抛出
        """
        pass

    @abstractmethod
    async def delete(self, table: str, filters: dict[str, Any]) -> DeleteResult:
        """
        删除数据

        Args:
            table: 表名
            filters: 过滤条件

        Returns:
            DeleteResult: 删除结果

        Raises:
            PermissionError: 权限不足时抛出
            QueryError: 查询错误时抛出
        """
        pass

    @abstractmethod
    async def update(
        self, table: str, data: dict[str, Any], filters: dict[str, Any]
    ) -> UpdateResult:
        """
        更新数据

        Args:
            table: 表名
            data: 要更新的数据
            filters: 过滤条件

        Returns:
            UpdateResult: 更新结果

        Raises:
            PermissionError: 权限不足时抛出
            QueryError: 查询错误时抛出
        """
        pass

    @abstractmethod
    async def query(
        self, table: str, filters: dict[str, Any] | None = None, limit: int | None = None
    ) -> QueryResult:
        """
        查询数据

        Args:
            table: 表名
            filters: 过滤条件（可选）
            limit: 返回记录数限制（可选）

        Returns:
            QueryResult: 查询结果

        Raises:
            QueryError: 查询错误时抛出
        """
        pass

    @abstractmethod
    async def execute(self, query: str, params: dict[str, Any] | None = None) -> ExecuteResult:
        """
        执行自定义查询

        Args:
            query: 查询语句
            params: 查询参数（可选）

        Returns:
            ExecuteResult: 执行结果

        Raises:
            PermissionError: 权限不足时抛出
            QueryError: 查询错误时抛出
        """
        pass

    @abstractmethod
    async def advanced_query(self, operation: str, params: dict[str, Any]) -> AdvancedResult:
        """
        执行高级查询（事务、聚合等）

        Args:
            operation: 操作类型（如 "transaction", "aggregate"）
            params: 操作参数

        Returns:
            AdvancedResult: 高级查询结果

        Raises:
            PermissionError: 权限不足时抛出
            QueryError: 查询错误时抛出
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Capability:
        """
        获取数据库能力

        Returns:
            Capability: 数据库能力描述
        """
        pass
