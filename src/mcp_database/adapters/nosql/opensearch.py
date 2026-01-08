"""OpenSearch 适配器"""

import ssl
from typing import Any

from opensearchpy import AsyncOpenSearch
from opensearchpy.exceptions import OpenSearchException

from mcp_database.core.adapter import DatabaseAdapter
from mcp_database.core.exceptions import ExceptionTranslator, QueryError
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


class OpenSearchAdapter(DatabaseAdapter):
    """OpenSearch 数据库适配器"""

    def __init__(self, config: DatabaseConfig):
        """
        初始化 OpenSearch 适配器

        Args:
            config: 数据库配置
        """
        super().__init__(config)
        self._client: AsyncOpenSearch | None = None
        self._is_connected: bool = False

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._is_connected

    async def connect(self) -> None:
        """
        连接到 OpenSearch 数据库

        Raises:
            ConnectionError: 连接失败时抛出
        """
        try:
            # 解析 URL
            url = self.config.url

            # 检查是否为 HTTPS 连接
            is_https = url.startswith("https://")

            # 创建客户端 - 默认启用 SSL 证书验证
            # 仅在非 HTTPS 或显式禁用时才禁用验证
            verify_certs = is_https

            # 检查配置中是否显式禁用了 SSL 验证（仅用于测试环境）
            if hasattr(self.config, "options") and self.config.options:
                if "verify_ssl" in self.config.options:
                    verify_certs = self.config.options["verify_ssl"]

            self._client = AsyncOpenSearch(
                hosts=[url],
                verify_certs=verify_certs,
                ssl_show_warn=not verify_certs,
                ssl_context=ssl.create_default_context() if verify_certs else None,
            )

            # 测试连接
            await self._client.ping()

            self._is_connected = True

        except OpenSearchException as e:
            translated = ExceptionTranslator.translate(e, "opensearch")
            raise translated

    async def disconnect(self) -> None:
        """断开数据库连接"""
        if self._client:
            await self._client.close()
            self._client = None
            self._is_connected = False

    async def insert(self, table: str, data: dict[str, Any]) -> InsertResult:
        """
        插入文档

        Args:
            table: 索引名
            data: 文档数据

        Returns:
            InsertResult: 插入结果

        Raises:
            QueryError: 插入错误时抛出
        """
        try:
            # 批量插入
            if isinstance(data, list):
                inserted_ids = []
                for doc in data:
                    response = await self._client.index(index=table, body=doc)
                    inserted_ids.append(response.get("_id"))

                return InsertResult(
                    inserted_count=len(inserted_ids), inserted_ids=inserted_ids, success=True
                )

            # 单个插入
            else:
                response = await self._client.index(index=table, body=data)
                doc_id = response.get("_id")

                return InsertResult(inserted_count=1, inserted_ids=[doc_id], success=True)

        except OpenSearchException as e:
            translated = ExceptionTranslator.translate(e, "opensearch")
            raise translated

    async def delete(self, table: str, filters: dict[str, Any]) -> DeleteResult:
        """
        删除文档

        Args:
            table: 索引名
            filters: 过滤条件

        Returns:
            DeleteResult: 删除结果

        Raises:
            QueryError: 删除错误时抛出
        """
        try:
            # 查询要删除的文档
            query = self._build_query(filters)
            search_result = await self._client.search(index=table, body={"query": query})

            # 删除文档
            deleted_count = 0
            for hit in search_result["hits"]["hits"]:
                doc_id = hit["_id"]
                await self._client.delete(index=table, id=doc_id)
                deleted_count += 1

            return DeleteResult(deleted_count=deleted_count)

        except OpenSearchException as e:
            translated = ExceptionTranslator.translate(e, "opensearch")
            raise translated

    async def update(
        self, table: str, data: dict[str, Any], filters: dict[str, Any]
    ) -> UpdateResult:
        """
        更新文档

        Args:
            table: 索引名
            data: 要更新的数据
            filters: 过滤条件

        Returns:
            UpdateResult: 更新结果

        Raises:
            QueryError: 更新错误时抛出
        """
        try:
            # 查询要更新的文档
            query = self._build_query(filters)
            search_result = await self._client.search(index=table, body={"query": query})

            # 更新文档
            updated_count = 0
            for hit in search_result["hits"]["hits"]:
                doc_id = hit["_id"]
                await self._client.update(index=table, id=doc_id, body={"doc": data})
                updated_count += 1

            return UpdateResult(updated_count=updated_count)

        except OpenSearchException as e:
            translated = ExceptionTranslator.translate(e, "opensearch")
            raise translated

    async def query(
        self, table: str, filters: dict[str, Any] | None = None, limit: int | None = None
    ) -> QueryResult:
        """
        查询文档

        Args:
            table: 索引名
            filters: 过滤条件（可选）
            limit: 返回记录数限制（可选）

        Returns:
            QueryResult: 查询结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            # 构建查询
            query = self._build_query(filters) if filters else {"match_all": {}}

            # 执行查询
            search_body = {"query": query}
            if limit:
                search_body["size"] = limit

            result = await self._client.search(index=table, body=search_body)

            # 提取结果
            hits = result["hits"]
            data = [hit["_source"] for hit in hits["hits"]]
            total = hits["total"]["value"]

            # 检查结果大小限制
            max_results = self.config.max_query_results
            if total > max_results:
                raise QueryError(
                    f"Query result exceeds maximum limit of {max_results} records. "
                    f"Please add more specific filters to reduce the result size."
                )

            return QueryResult(
                data=data,
                count=total,
                has_more=limit is not None and len(data) == limit and total > limit,
            )

        except OpenSearchException as e:
            translated = ExceptionTranslator.translate(e, "opensearch")
            raise translated

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> ExecuteResult:
        """
        执行原生查询（OpenSearch 不支持 SQL，此方法抛出异常）

        Args:
            query: 查询语句
            params: 查询参数

        Returns:
            ExecuteResult: 执行结果

        Raises:
            QueryError: OpenSearch 不支持 SQL 查询
        """
        raise QueryError("OpenSearch does not support SQL queries")

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
        try:
            if operation == "aggregation":
                # 聚合查询
                result = await self._client.search(
                    index=params.get("index", "*"), body=params.get("body", {})
                )
                return AdvancedResult(
                    data=result.get("aggregations", {}), operation=operation, success=True
                )

            else:
                raise QueryError(f"Unsupported advanced operation: {operation}")

        except OpenSearchException as e:
            translated = ExceptionTranslator.translate(e, "opensearch")
            raise translated

    def get_capabilities(self) -> Capability:
        """
        获取数据库能力

        Returns:
            Capability: 能力描述
        """
        return Capability(
            basic_crud=True,
            full_text_search=True,
            aggregation=True,
            transactions=False,
            advanced_query=True,
        )

    def _build_query(self, filters: dict[str, Any]) -> dict[str, Any]:
        """
        构建查询

        Args:
            filters: 过滤条件

        Returns:
            查询字典
        """
        if not filters:
            return {"match_all": {}}

        must_clauses = []

        for field, value in filters.items():
            if "__" in field:
                # 操作符
                field_name, operator = field.split("__", 1)
                if operator == "gt":
                    must_clauses.append({"range": {field_name: {"gt": value}}})
                elif operator == "lt":
                    must_clauses.append({"range": {field_name: {"lt": value}}})
                elif operator == "gte":
                    must_clauses.append({"range": {field_name: {"gte": value}}})
                elif operator == "lte":
                    must_clauses.append({"range": {field_name: {"lte": value}}})
                elif operator == "in":
                    must_clauses.append({"terms": {field_name: value}})
                elif operator == "contains":
                    # 使用 match 查询来实现包含功能
                    must_clauses.append({"match": {field_name: value}})
                else:
                    must_clauses.append({"match": {field_name: value}})
            else:
                # 等值查询 - 使用 match 而不是 term，因为 term 需要精确匹配
                must_clauses.append({"match": {field: value}})

        return {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}}
