"""Supabase REST API 适配器（异步版）"""

import os
from typing import Any

import httpx
from httpx import ConnectError, HTTPStatusError, TimeoutException

from mcp_database.core.adapter import DatabaseAdapter
from mcp_database.core.exceptions import (
    ConnectionError,
    ExceptionTranslator,
    QueryError,
)
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


class SupabaseAdapter(DatabaseAdapter):
    """Supabase REST API 适配器（使用 httpx 实现真正的异步）"""

    def __init__(self, config: DatabaseConfig):
        """
        初始化 Supabase 适配器

        Args:
            config: 数据库配置
        """
        super().__init__(config)
        self._client: httpx.AsyncClient | None = None
        self._connected: bool = False
        self._supabase_url: str | None = None
        self._supabase_key: str | None = None

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected

    async def connect(self) -> None:
        """
        连接到 Supabase 数据库

        Raises:
            ConnectionError: 连接失败时抛出
        """
        try:
            # 从环境变量获取 Supabase URL 和 Key
            self._supabase_url = os.getenv("SUPABASE_URL")
            self._supabase_key = os.getenv("SUPABASE_KEY")

            if not self._supabase_url or not self._supabase_key:
                raise ConnectionError("Missing required Supabase credentials")

            # 创建异步 HTTP 客户端
            self._client = httpx.AsyncClient(
                base_url=self._supabase_url,
                headers={
                    "apikey": self._supabase_key,
                    "Authorization": f"Bearer {self._supabase_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                timeout=30.0,
            )

            # 测试连接
            await self._client.get("/")

            self._connected = True

        except Exception as e:
            translated = ExceptionTranslator.translate(e, "supabase")
            raise translated

    async def disconnect(self) -> None:
        """断开数据库连接"""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._connected = False

    async def insert(self, table: str, data: dict[str, Any]) -> InsertResult:
        """
        插入文档

        Args:
            table: 表名
            data: 文档数据

        Returns:
            InsertResult: 插入结果

        Raises:
            QueryError: 插入错误时抛出
            ConnectionError: 连接错误时抛出
        """
        try:
            # 批量插入 - 使用 Supabase 的批量插入功能
            if isinstance(data, list):
                response = await self._client.post(f"/rest/v1/{table}", json=data)
                response.raise_for_status()
                results = response.json()
                inserted_ids = [r.get("id") for r in results if r.get("id")]

                return InsertResult(
                    inserted_count=len(inserted_ids), inserted_ids=inserted_ids, success=True
                )

            # 单个插入
            else:
                response = await self._client.post(f"/rest/v1/{table}", json=data)
                response.raise_for_status()
                result = response.json()
                doc_id = result[0].get("id") if result else None

                return InsertResult(
                    inserted_count=1, inserted_ids=[doc_id] if doc_id else [], success=True
                )

        except TimeoutException as e:
            raise ConnectionError(f"Supabase request timed out: {e}")
        except ConnectError as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")
        except HTTPStatusError as e:
            raise QueryError(
                f"Supabase request failed with status {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            translated = ExceptionTranslator.translate(e, "supabase")
            raise translated

    async def delete(self, table: str, filters: dict[str, Any]) -> DeleteResult:
        """
        删除文档

        Args:
            table: 表名
            filters: 过滤条件

        Returns:
            DeleteResult: 删除结果

        Raises:
            QueryError: 删除错误时抛出
        """
        try:
            # 构建查询参数
            params = {}
            for field, value in filters.items():
                params[field] = f"eq.{value}"

            # 获取要删除的记录
            response = await self._client.get(f"/rest/v1/{table}", params=params)
            response.raise_for_status()
            records = response.json()
            deleted_count = len(records) if records else 0

            # 删除记录
            if deleted_count > 0:
                for record in records:
                    params = {"id": f"eq.{record['id']}"}
                    await self._client.delete(f"/rest/v1/{table}", params=params)

            return DeleteResult(deleted_count=deleted_count)

        except TimeoutException as e:
            raise ConnectionError(f"Supabase request timed out: {e}")
        except ConnectError as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")
        except HTTPStatusError as e:
            raise QueryError(
                f"Supabase request failed with status {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            translated = ExceptionTranslator.translate(e, "supabase")
            raise translated

    async def update(
        self, table: str, data: dict[str, Any], filters: dict[str, Any]
    ) -> UpdateResult:
        """
        更新文档

        Args:
            table: 表名
            data: 要更新的数据
            filters: 过滤条件

        Returns:
            UpdateResult: 更新结果

        Raises:
            QueryError: 更新错误时抛出
        """
        try:
            # 构建查询参数
            params = {}
            for field, value in filters.items():
                params[field] = f"eq.{value}"

            # 获取要更新的记录
            response = await self._client.get(f"/rest/v1/{table}", params=params)
            response.raise_for_status()
            records = response.json()
            updated_count = len(records) if records else 0

            # 更新记录
            if updated_count > 0:
                for record in records:
                    params = {"id": f"eq.{record['id']}"}
                    await self._client.patch(f"/rest/v1/{table}", json=data, params=params)

            return UpdateResult(updated_count=updated_count)

        except TimeoutException as e:
            raise ConnectionError(f"Supabase request timed out: {e}")
        except ConnectError as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")
        except HTTPStatusError as e:
            raise QueryError(
                f"Supabase request failed with status {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            translated = ExceptionTranslator.translate(e, "supabase")
            raise translated

    async def query(
        self, table: str, filters: dict[str, Any] | None = None, limit: int | None = None
    ) -> QueryResult:
        """
        查询文档

        Args:
            table: 表名
            filters: 过滤条件（可选）
            limit: 返回记录数限制（可选）

        Returns:
            QueryResult: 查询结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            # 构建查询参数
            params = {}

            # 应用过滤器
            if filters:
                for field, value in filters.items():
                    if "__" in field:
                        # 操作符
                        field_name, operator = field.split("__", 1)
                        if operator == "gt":
                            params[field_name] = f"gt.{value}"
                        elif operator == "lt":
                            params[field_name] = f"lt.{value}"
                        elif operator == "gte":
                            params[field_name] = f"gte.{value}"
                        elif operator == "lte":
                            params[field_name] = f"lte.{value}"
                        elif operator == "in":
                            params[field_name] = f"in.({','.join(map(str, value))})"
                        elif operator == "contains":
                            params[field_name] = f"like.*{value}*"
                        else:
                            params[field_name] = f"eq.{value}"
                    else:
                        # 等值查询
                        params[field] = f"eq.{value}"

            # 应用限制
            if limit:
                params["limit"] = limit

            # 执行查询
            response = await self._client.get(f"/rest/v1/{table}", params=params)
            response.raise_for_status()
            data = response.json() if response.json() else []

            # 检查结果大小限制
            max_results = self.config.max_query_results
            if len(data) > max_results:
                raise QueryError(
                    f"Query result exceeds maximum limit of {max_results} records. "
                    f"Please add more specific filters to reduce the result size."
                )

            return QueryResult(data=data, count=len(data), has_more=False)

        except TimeoutException as e:
            raise ConnectionError(f"Supabase request timed out: {e}")
        except ConnectError as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")
        except HTTPStatusError as e:
            raise QueryError(
                f"Supabase request failed with status {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            translated = ExceptionTranslator.translate(e, "supabase")
            raise translated

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> ExecuteResult:
        """
        执行原生查询（Supabase REST API 不支持 SQL，此方法抛出异常）

        Args:
            query: 查询语句
            params: 查询参数

        Returns:
            ExecuteResult: 执行结果

        Raises:
            QueryError: Supabase REST API 不支持 SQL 查询
        """
        raise QueryError("Supabase REST API does not support SQL queries")

    async def advanced_query(self, operation: str, params: dict[str, Any]) -> AdvancedResult:
        """
        执行高级查询

        Args:
            operation: 操作类型（如 "aggregation"）
            params: 操作参数

        Returns:
            AdvancedResult: 高级查询结果

        Raises:
            QueryError: 查询错误时抛出
        """
        raise QueryError(f"Unsupported advanced operation: {operation}")

    def get_capabilities(self) -> Capability:
        """
        获取数据库能力

        Returns:
            Capability: 能力描述
        """
        return Capability(
            basic_crud=True,
            full_text_search=True,
            aggregation=False,
            transactions=False,
            advanced_query=False,
        )
