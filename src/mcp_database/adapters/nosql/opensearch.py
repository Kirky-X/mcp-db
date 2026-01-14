"""OpenSearch 适配器"""

import os
import ssl
from typing import Any

# OpenSearch异常类和客户端（使用兼容的导入方式）
try:
    from opensearch import AsyncOpenSearch  # type: ignore[import-untyped]
    from opensearch.exceptions import OpenSearchException  # type: ignore[import-untyped]
except ImportError:
    # 如果没有安装opensearch-py，使用占位符
    OpenSearchException = Exception
    AsyncOpenSearch = None

from mcp_database.core.adapter import DatabaseAdapter
from mcp_database.core.exceptions import (
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

# OpenSearch 查询操作符映射
_QUERY_OPERATORS = {
    "gt": lambda field, value: {"range": {field: {"gt": value}}},
    "lt": lambda field, value: {"range": {field: {"lt": value}}},
    "gte": lambda field, value: {"range": {field: {"gte": value}}},
    "lte": lambda field, value: {"range": {field: {"lte": value}}},
    "in": lambda field, value: {"terms": {field: value}},
    "contains": lambda field, value: {"match": {field: value}},
}

# 允许的OpenSearch索引（从环境变量配置，使用延迟加载避免模块加载时执行）
_ALLOWED_INDICES_CACHE: frozenset[str] | None = None


def _get_allowed_indices() -> frozenset[str]:
    """获取允许的 OpenSearch 索引（延迟加载）"""
    global _ALLOWED_INDICES_CACHE
    if _ALLOWED_INDICES_CACHE is None:
        env_indices = os.getenv("OPENSEARCH_ALLOWED_INDICES", "")
        if env_indices:
            _ALLOWED_INDICES_CACHE = frozenset(
                index.strip() for index in env_indices.split(",") if index.strip()
            )
        else:
            _ALLOWED_INDICES_CACHE = frozenset({"*"})
    return _ALLOWED_INDICES_CACHE


# 禁止的查询参数
FORBIDDEN_QUERY_PARAMS = frozenset({"_source", "script", "script_fields"})


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
        self._connected: bool = False

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected

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

            self._connected = True

        except OpenSearchException as e:
            translated = ExceptionTranslator.translate(e, "opensearch")
            raise translated

    async def disconnect(self) -> None:
        """断开数据库连接"""
        if self._client:
            await self._client.close()
            self._client = None
            self._connected = False

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
            if isinstance(data, list):
                if len(data) == 0:
                    return InsertResult(inserted_count=0, inserted_ids=[])

                if len(data) == 1:
                    assert self._client is not None
                    response = await self._client.index(index=table, body=data[0])
                    doc_id = response.get("_id")
                    return InsertResult(inserted_count=1, inserted_ids=[doc_id], success=True)

                operations = []
                for doc in data:
                    operations.append({"index": {"_index": table}})
                    operations.append(doc)

                assert self._client is not None
                response = await self._client.bulk(body=operations)

                # 处理部分成功的情况
                successful_ids = []
                failed_items = []

                for item in response.get("items", []):
                    index_result = item.get("index", {})
                    if index_result.get("error"):
                        failed_items.append(index_result)
                    else:
                        successful_ids.append(index_result.get("_id"))

                if len(failed_items) == len(data):
                    # 所有文档都失败
                    raise QueryError(f"All documents failed to insert: {failed_items}")

                return InsertResult(
                    inserted_count=len(successful_ids),
                    inserted_ids=successful_ids,
                    success=len(failed_items) == 0,
                )

            else:
                assert self._client is not None
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
            assert self._client is not None
            search_result = await self._client.search(index=table, body={"query": query})

            # 使用 bulk API 批量删除
            hits = search_result["hits"]["hits"]
            if hits:
                operations = [{"delete": {"_index": table, "_id": hit["_id"]}} for hit in hits]
                response = await self._client.bulk(body=operations)
                deleted_count = sum(
                    1
                    for item in response.get("items", [])
                    if item.get("delete", {}).get("result") == "deleted"
                )
            else:
                deleted_count = 0

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
            assert self._client is not None
            search_result = await self._client.search(index=table, body={"query": query})

            # 使用 bulk API 批量更新
            hits = search_result["hits"]["hits"]
            if hits:
                operations = [
                    {"update": {"_index": table, "_id": hit["_id"]}, "doc": data} for hit in hits
                ]
                response = await self._client.bulk(body=operations)
                updated_count = sum(
                    1
                    for item in response.get("items", [])
                    if "update" in item and item["update"].get("result") in ("updated", "created")
                )
            else:
                updated_count = 0

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
            search_body: dict[str, Any] = {"query": query}
            if limit:
                search_body["size"] = limit

            assert self._client is not None
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

    def _validate_index_access(self, index: str) -> None:
        """
        验证索引访问权限

        Args:
            index: 要访问的索引名

        Raises:
            QueryError: 索引不允许访问时抛出
        """
        # 禁止通配符访问
        if "*" in index:
            raise QueryError("Wildcard index access not allowed")

        # 如果配置了允许的索引列表，检查是否在白名单中
        allowed_indices = _get_allowed_indices()
        if allowed_indices and "*" not in allowed_indices:
            if index not in allowed_indices:
                raise QueryError(f"Index '{index}' not allowed")

    def _validate_query_body(self, body: dict[str, Any]) -> None:
        """
        验证查询体不包含危险参数

        Args:
            body: 查询体

        Raises:
            QueryError: 包含危险参数时抛出
        """

        def check_dict(d: dict) -> bool:
            for key in d.keys():
                if key in FORBIDDEN_QUERY_PARAMS:
                    return True
                if isinstance(d[key], dict):
                    if check_dict(d[key]):
                        return True
            return False

        if check_dict(body):
            raise QueryError("Query contains forbidden parameters")

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
                index = params.get("index", "*")
                body = params.get("body", {})

                # 验证索引访问
                self._validate_index_access(index)

                # 验证查询体
                self._validate_query_body(body)

                assert self._client is not None
                result = await self._client.search(index=index, body=body)
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
                # 使用字典查找操作符处理器
                query_builder = _QUERY_OPERATORS.get(operator)
                if query_builder:
                    must_clauses.append(query_builder(field_name, value))
                else:
                    # 默认使用 match 查询
                    must_clauses.append({"match": {field_name: value}})
            else:
                # 等值查询 - 使用 match 而不是 term，因为 term 需要精确匹配
                must_clauses.append({"match": {field: value}})

        return {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}}
