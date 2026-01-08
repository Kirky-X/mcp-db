"""SQL 适配器基类"""

import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from mcp_database.core.adapter import DatabaseAdapter
from mcp_database.core.exceptions import (
    ConnectionError,
    ExceptionTranslator,
    QueryError,
)
from mcp_database.core.filters import SQLFilterTranslator
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
from mcp_database.core.permissions import check_execute_permission


class SQLAdapter(DatabaseAdapter):
    """
    SQL 适配器基类

    使用 SQLAlchemy 2.0 异步 API 实现，支持 PostgreSQL、MySQL、SQLite。
    """

    def __init__(self, config: DatabaseConfig):
        """
        初始化 SQL 适配器

        Args:
            config: 数据库配置
        """
        super().__init__(config)
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._connected: bool = False
        self._filter_translator = SQLFilterTranslator()

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected

    @property
    def _database_type(self) -> str:
        """获取数据库类型"""
        url = self.config.url.lower()
        if "postgresql" in url or "postgres" in url:
            return "postgresql"
        elif "mysql" in url:
            return "mysql"
        elif "sqlite" in url:
            return "sqlite"
        else:
            return "unknown"

    def _validate_table_name(self, table: str) -> str:
        """
        验证表名，防止 SQL 注入

        Args:
            table: 表名

        Returns:
            验证后的表名

        Raises:
            ValueError: 表名不合法时抛出
        """
        # 表名只能包含字母、数字和下划线，且必须以字母或下划线开头
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table):
            raise ValueError(f"Invalid table name: {table}")
        return table

    async def connect(self) -> None:
        """
        连接到数据库

        Raises:
            ConnectionError: 连接失败时抛出
        """
        try:
            # 根据数据库类型创建引擎参数
            engine_kwargs = {
                "pool_pre_ping": True,  # 连接健康检查
                "echo": False,
            }

            # SQLite 不支持连接池参数
            if self._database_type != "sqlite":
                engine_kwargs["pool_size"] = self.config.pool_size
                engine_kwargs["max_overflow"] = self.config.max_overflow

            # 创建异步引擎
            self._engine = create_async_engine(self.config.url, **engine_kwargs)

            # 创建会话工厂
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            # 测试连接
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))

            self._connected = True

        except Exception as e:
            self._connected = False
            translated = ExceptionTranslator.translate(e, self._database_type)
            if isinstance(translated, ConnectionError):
                raise translated
            raise ConnectionError(f"Failed to connect to database: {e}")

    async def disconnect(self) -> None:
        """断开数据库连接"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._connected = False

    def _get_session(self) -> AsyncSession:
        """
        获取会话

        Returns:
            AsyncSession: 异步会话

        Raises:
            ConnectionError: 未连接时抛出
        """
        if not self._connected or not self._session_factory:
            raise ConnectionError("Not connected to database")

        return self._session_factory()

    async def insert(
        self, table: str, data: dict[str, Any] | list[dict[str, Any]]
    ) -> InsertResult:
        """

        插入数据



        Args:

            table: 表名

            data: 要插入的数据字典或列表



        Returns:

            InsertResult: 插入结果



        Raises:

            QueryError: 查询错误时抛出

        """

        try:
            # 验证表名

            table = self._validate_table_name(table)

            async with self._get_session() as session:
                # 批量插入

                if isinstance(data, list):
                    columns = list(data[0].keys())

                    placeholders = ", ".join([f":{col}" for col in columns])

                    columns_str = ", ".join(columns)

                    if self._database_type == "postgresql":
                        # PostgreSQL 使用 RETURNING 获取 ID
                        sql = (
                            f"INSERT INTO {table} ({columns_str}) "
                            f"VALUES ({placeholders}) RETURNING id"
                        )

                        stmt = text(sql)

                        inserted_ids = []

                        for row in data:
                            result = await session.execute(stmt, row)

                            inserted_id = result.scalar()

                            inserted_ids.append(inserted_id)

                    else:
                        # MySQL 和 SQLite 使用 lastrowid

                        sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

                        stmt = text(sql)

                        inserted_ids = []

                        for row in data:
                            result = await session.execute(stmt, row)

                            inserted_ids.append(result.lastrowid)

                    inserted_count = len(data)

                else:
                    # 单条插入

                    columns = list(data.keys())

                    placeholders = ", ".join([f":{col}" for col in columns])

                    columns_str = ", ".join(columns)

                    if self._database_type == "postgresql":
                        # PostgreSQL 使用 RETURNING 获取 ID
                        sql = (
                            f"INSERT INTO {table} ({columns_str}) "
                            f"VALUES ({placeholders}) RETURNING id"
                        )

                        stmt = text(sql)

                        result = await session.execute(stmt, data)

                        inserted_id = result.scalar()

                        inserted_ids = [inserted_id] if inserted_id else []

                    else:
                        # MySQL 和 SQLite 使用 lastrowid

                        sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

                        stmt = text(sql)

                        result = await session.execute(stmt, data)

                        inserted_ids = [result.lastrowid] if result.lastrowid else []

                    inserted_count = 1

                await session.commit()

                return InsertResult(inserted_count=inserted_count, inserted_ids=inserted_ids)

        except Exception as e:
            translated = ExceptionTranslator.translate(e, self._database_type)

            raise translated

    async def delete(self, table: str, filters: dict[str, Any]) -> DeleteResult:
        """
        删除数据

        Args:
            table: 表名
            filters: 过滤条件

        Returns:
            DeleteResult: 删除结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            # 验证表名
            table = self._validate_table_name(table)

            async with self._get_session() as session:
                # 构建删除语句
                where_clause, params = self._filter_translator.translate(filters)
                sql = f"DELETE FROM {table}"

                if where_clause:
                    sql += f" WHERE {where_clause}"

                stmt = text(sql)
                result = await session.execute(stmt, params)
                deleted_count = result.rowcount
                await session.commit()

                return DeleteResult(deleted_count=deleted_count)

        except Exception as e:
            translated = ExceptionTranslator.translate(e, self._database_type)
            raise translated

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
            QueryError: 查询错误时抛出
        """
        try:
            # 验证表名
            table = self._validate_table_name(table)

            async with self._get_session() as session:
                # 构建更新语句
                set_clause = ", ".join([f"{col} = :{col}" for col in data.keys()])
                where_clause, filter_params = self._filter_translator.translate(filters)
                sql = f"UPDATE {table} SET {set_clause}"

                if where_clause:
                    sql += f" WHERE {where_clause}"

                # 合并参数
                all_params = {**data, **filter_params}

                stmt = text(sql)
                result = await session.execute(stmt, all_params)
                updated_count = result.rowcount
                await session.commit()

                return UpdateResult(updated_count=updated_count)

        except Exception as e:
            translated = ExceptionTranslator.translate(e, self._database_type)
            raise translated

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
        try:
            # 验证表名
            table = self._validate_table_name(table)

            async with self._get_session() as session:
                # 构建查询语句
                where_clause = ""
                params = {}
                if filters:
                    where_clause, params = self._filter_translator.translate(filters)

                sql = f"SELECT * FROM {table}"

                if where_clause:
                    sql += f" WHERE {where_clause}"

                # 先查询总数
                count_sql = f"SELECT COUNT(*) FROM {table}"
                if where_clause:
                    count_sql += f" WHERE {where_clause}"

                count_result = await session.execute(text(count_sql), params)
                total_count = count_result.scalar()

                # 检查结果大小限制
                max_results = self.config.max_query_results
                if total_count > max_results:
                    raise QueryError(
                        f"Query result exceeds maximum limit of {max_results} records. "
                        f"Please add more specific filters to reduce the result size."
                    )

                # 查询数据
                if limit:
                    sql += f" LIMIT {limit}"

                result = await session.execute(text(sql), params)
                data = [dict(row._mapping) for row in result.fetchall()]

                return QueryResult(
                    data=data,
                    count=total_count,
                    has_more=limit is not None and len(data) == limit and total_count > limit,
                )

        except Exception as e:
            translated = ExceptionTranslator.translate(e, self._database_type)
            raise translated

    @check_execute_permission
    async def execute(self, query: str, params: dict[str, Any] | None = None) -> ExecuteResult:
        """
        执行自定义查询

        Args:
            query: 查询语句
            params: 查询参数（可选）

        Returns:
            ExecuteResult: 执行结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            async with self._get_session() as session:
                stmt = text(query)

                if params:
                    stmt = stmt.bindparams(**params)

                result = await session.execute(stmt)

                # 判断是否有返回数据
                if result.returns_rows:
                    data = [dict(row._mapping) for row in result.fetchall()]
                else:
                    data = None

                rows_affected = result.rowcount
                await session.commit()

                return ExecuteResult(
                    rows_affected=rows_affected if rows_affected >= 0 else 0, data=data
                )

        except Exception as e:
            translated = ExceptionTranslator.translate(e, self._database_type)
            raise translated

    async def advanced_query(self, operation: str, params: dict[str, Any]) -> AdvancedResult:
        """
        执行高级查询（事务、聚合等）

        Args:
            operation: 操作类型（如 "transaction", "aggregate"）
            params: 操作参数

        Returns:
            AdvancedResult: 高级查询结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            async with self._get_session() as session:
                if operation == "transaction":
                    # 执行事务
                    queries = params.get("queries", [])
                    results = []

                    for query_info in queries:
                        query = query_info["query"]
                        query_params = query_info.get("params")
                        stmt = text(query)

                        if query_params:
                            stmt = stmt.bindparams(**query_params)

                        result = await session.execute(stmt)
                        results.append(
                            {
                                "rows_affected": result.rowcount,
                                "data": [dict(row._mapping) for row in result.fetchall()]
                                if result.returns_rows
                                else None,
                            }
                        )

                    await session.commit()

                    return AdvancedResult(
                        operation=operation, data={"results": results, "committed": True}
                    )

                else:
                    raise QueryError(f"Unsupported operation: {operation}")

        except Exception as e:
            translated = ExceptionTranslator.translate(e, self._database_type)
            raise translated

    def get_capabilities(self) -> Capability:
        """
        获取数据库能力

        Returns:
            Capability: 数据库能力描述
        """
        return Capability(
            basic_crud=True,
            transactions=True,
            joins=True,
            aggregation=True,
            full_text_search=self._database_type == "postgresql",
            geospatial=self._database_type == "postgresql",
        )
