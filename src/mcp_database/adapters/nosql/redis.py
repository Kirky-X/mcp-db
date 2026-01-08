"""Redis 适配器"""

import json
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from mcp_database.core.adapter import DatabaseAdapter
from mcp_database.core.exceptions import (
    ConnectionError,
    ExceptionTranslator,
    QueryError,
)
from mcp_database.core.filters import RedisFilterTranslator
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


class RedisAdapter(DatabaseAdapter):
    """
    Redis 适配器（优化版）

    使用 redis-py 异步驱动实现 Redis 操作。
    使用 table:id 键前缀模式存储数据。
    使用 SET 数据结构作为索引，避免全键扫描。
    """

    @staticmethod
    def _is_counter_key(key: str | bytes) -> bool:
        """检查键是否是计数器键"""
        if isinstance(key, bytes):
            return key.endswith(b":_id_counter")
        else:
            return key.endswith(":_id_counter")

    @staticmethod
    def _is_index_key(table: str) -> str:
        """获取表的索引键名"""
        return f"{table}:_index"

    def __init__(self, config: DatabaseConfig):
        """
        初始化 Redis 适配器

        Args:
            config: 数据库配置
        """
        super().__init__(config)
        self._client: Redis | None = None
        self._connected: bool = False
        self._filter_translator = RedisFilterTranslator()

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected

    def _make_key(self, table: str, record_id: Any) -> str:
        """
        生成 Redis 键

        Args:
            table: 表名
            record_id: 记录 ID

        Returns:
            str: Redis 键
        """
        return f"{table}:{record_id}"

    async def connect(self) -> None:
        """
        连接到 Redis

        Raises:
            ConnectionError: 连接失败时抛出
        """
        try:
            # 创建 Redis 客户端
            self._client = Redis.from_url(
                self.config.url,
                socket_connect_timeout=self.config.connect_timeout,
                socket_timeout=self.config.query_timeout,
                decode_responses=True,
            )

            # 测试连接
            await self._client.ping()

            self._connected = True

        except RedisError as e:
            self._connected = False
            translated = ExceptionTranslator.translate(e, "redis")
            if isinstance(translated, ConnectionError):
                raise translated
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    async def disconnect(self) -> None:
        """断开 Redis 连接"""
        if self._client:
            await self._client.close()
            self._client = None
            self._connected = False

    async def insert(
        self, table: str, data: dict[str, Any] | list[dict[str, Any]]
    ) -> InsertResult:
        """
        插入记录

        Args:
            table: 表名
            data: 要插入的数据字典或列表

        Returns:
            InsertResult: 插入结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            # 批量插入
            if isinstance(data, list):
                inserted_ids = []
                for record in data:
                    # 生成 ID
                    record_id = await self._client.incr(f"{table}:_id_counter")
                    inserted_ids.append(record_id)

                    # 存储数据
                    key = self._make_key(table, record_id)
                    record_with_id = record.copy()
                    record_with_id["id"] = record_id
                    await self._client.set(key, json.dumps(record_with_id))

                    # 添加到索引
                    await self._client.sadd(self._is_index_key(table), key)

                inserted_count = len(data)
            else:
                # 单条插入
                record_id = await self._client.incr(f"{table}:_id_counter")
                inserted_ids = [record_id]

                # 存储数据
                key = self._make_key(table, record_id)
                record_with_id = data.copy()
                record_with_id["id"] = record_id
                await self._client.set(key, json.dumps(record_with_id))

                # 添加到索引
                await self._client.sadd(self._is_index_key(table), key)

                inserted_count = 1

            return InsertResult(inserted_count=inserted_count, inserted_ids=inserted_ids)

        except RedisError as e:
            translated = ExceptionTranslator.translate(e, "redis")
            raise translated

    async def delete(self, table: str, filters: dict[str, Any]) -> DeleteResult:
        """
        删除记录

        Args:
            table: 表名
            filters: 过滤条件

        Returns:
            DeleteResult: 删除结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            # 转换过滤器为过滤函数
            filter_func = self._filter_translator.translate(filters)

            # 从索引中获取所有键（O(1) 复杂度）
            index_key = self._is_index_key(table)
            keys = await self._client.smembers(index_key)

            # 过滤并删除
            deleted_count = 0
            keys_to_delete = []

            for key in keys:
                data_str = await self._client.get(key)
                if data_str:
                    data = json.loads(data_str)
                    if filter_func(data):
                        keys_to_delete.append(key)

            # 批量删除
            if keys_to_delete:
                await self._client.delete(*keys_to_delete)
                await self._client.srem(index_key, *keys_to_delete)
                deleted_count = len(keys_to_delete)

            return DeleteResult(deleted_count=deleted_count)

        except RedisError as e:
            translated = ExceptionTranslator.translate(e, "redis")
            raise translated

    async def update(
        self, table: str, data: dict[str, Any], filters: dict[str, Any]
    ) -> UpdateResult:
        """
        更新记录

        Args:
            table: 表名
            data: 要更新的数据
            filters: 过滤条件

        Returns:
            UpdateResult: 更新结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            # 转换过滤器为过滤函数
            filter_func = self._filter_translator.translate(filters)

            # 从索引中获取所有键（O(1) 复杂度）
            index_key = self._is_index_key(table)
            keys = await self._client.smembers(index_key)

            # 过滤并更新
            updated_count = 0
            for key in keys:
                data_str = await self._client.get(key)
                if data_str:
                    record = json.loads(data_str)
                    if filter_func(record):
                        # 更新数据
                        record.update(data)
                        await self._client.set(key, json.dumps(record))
                        updated_count += 1

            return UpdateResult(updated_count=updated_count)

        except RedisError as e:
            translated = ExceptionTranslator.translate(e, "redis")
            raise translated

    async def query(
        self, table: str, filters: dict[str, Any] | None = None, limit: int | None = None
    ) -> QueryResult:
        """
        查询记录

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
            # 转换过滤器为过滤函数
            filter_func = self._filter_translator.translate(filters) if filters else None

            # 从索引中获取所有键（O(1) 复杂度）
            index_key = self._is_index_key(table)
            keys = await self._client.smembers(index_key)

            # 获取所有数据
            all_data = []
            for key in keys:
                data_str = await self._client.get(key)
                if data_str:
                    record = json.loads(data_str)
                    # 应用过滤器
                    if filter_func is None or filter_func(record):
                        all_data.append(record)

            # 检查结果大小限制
            max_results = self.config.max_query_results
            if len(all_data) > max_results:
                raise QueryError(
                    f"Query result exceeds maximum limit of {max_results} records. "
                    f"Please add more specific filters to reduce the result size."
                )

            # 应用限制
            if limit:
                data = all_data[:limit]
            else:
                data = all_data

            return QueryResult(
                data=data,
                count=len(all_data),
                has_more=limit is not None and len(data) == limit and len(all_data) > limit,
            )

        except RedisError as e:
            translated = ExceptionTranslator.translate(e, "redis")
            raise translated

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> ExecuteResult:
        """
        执行自定义查询（Redis 不支持原始 SQL）

        Args:
            query: 查询语句（Redis 不支持）
            params: 查询参数（可选）

        Returns:
            ExecuteResult: 执行结果

        Raises:
            QueryError: Redis 不支持原始 SQL 查询
        """
        raise QueryError("Redis does not support raw SQL queries. Use query() method instead.")

    async def advanced_query(self, operation: str, params: dict[str, Any]) -> AdvancedResult:
        """
        执行高级查询（Redis 不支持复杂操作）

        Args:
            operation: 操作类型
            params: 操作参数

        Returns:
            AdvancedResult: 高级查询结果

        Raises:
            QueryError: Redis 不支持高级查询
        """
        raise QueryError("Redis does not support advanced queries. Use basic CRUD methods instead.")

    def get_capabilities(self) -> Capability:
        """
        获取数据库能力

        Returns:
            Capability: 数据库能力描述
        """
        return Capability(
            basic_crud=True,
            transactions=False,
            joins=False,
            aggregation=False,
            full_text_search=False,
            geospatial=False,
        )
