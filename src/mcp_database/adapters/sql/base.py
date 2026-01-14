"""SQL 适配器基类"""

import os
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
from mcp_database.core.security import SQLSecurityChecker


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
        # 缓存安全检查器实例，避免重复创建
        self._security_checker = SQLSecurityChecker()

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

    def _validate_column_names(self, columns: list[str]) -> list[str]:
        """
        验证列名列表，防止 SQL 注入

        Args:
            columns: 列名列表

        Returns:
            验证后的列名列表

        Raises:
            ValueError: 列名不合法时抛出
        """
        validated = []
        for col in columns:
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", col):
                raise ValueError(f"Invalid column name: {col}")
            validated.append(col)
        return validated

    def _validate_limit(self, limit: int) -> int:
        """
        验证 LIMIT 参数

        Args:
            limit: LIMIT值

        Returns:
            验证后的LIMIT值

        Raises:
            QueryError: LIMIT值不合法时抛出
        """
        if not isinstance(limit, int) or limit < 0:
            raise QueryError(f"Invalid limit value: {limit}. Must be a positive integer.")
        return limit

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

    def _build_insert_sql(self, table: str, columns: list[str], use_returning: bool = True) -> str:
        """
        构建 INSERT SQL 语句

        Args:
            table: 表名
            columns: 列名列表
            use_returning: 是否使用 RETURNING 子句

        Returns:
            SQL 语句
        """
        validated_columns = self._validate_column_names(columns)
        placeholders = ", ".join([f":{col}" for col in validated_columns])
        columns_str = ", ".join(validated_columns)
        sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        if use_returning and self._database_type == "postgresql":
            sql += " RETURNING id"
        return sql

    def _extract_inserted_id(self, result, use_returning: bool = True) -> int | None:
        """
        从执行结果中提取插入的 ID

        Args:
            result: 执行结果
            use_returning: 是否使用 RETURNING 子句

        Returns:
            插入的 ID
        """
        if use_returning and self._database_type == "postgresql":
            return result.scalar()
        return result.lastrowid

    async def insert(self, table: str, data: dict[str, Any] | list[dict[str, Any]]) -> InsertResult:
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
            table = self._validate_table_name(table)

            if isinstance(data, list) and len(data) == 0:
                return InsertResult(inserted_count=0, inserted_ids=[])

            data_list = data if isinstance(data, list) else [data]
            use_returning = self._database_type == "postgresql"

            async with self._get_session() as session:
                columns = list(data_list[0].keys())
                sql = self._build_insert_sql(table, columns, use_returning)
                stmt = text(sql)

                inserted_ids: list[Any] = []

                if len(data_list) > 1:
                    # 批量执行 - 根据数据库类型处理
                    if use_returning:
                        # PostgreSQL: 支持 RETURNING，可以批量获取 ID
                        results = await session.execute(stmt, data_list)
                        for result in results:
                            inserted_id = self._extract_inserted_id(result, use_returning)
                            if inserted_id:
                                inserted_ids.append(inserted_id)
                    else:
                        # SQLite/MySQL: 逐条执行以获取 lastrowid
                        for data_item in data_list:
                            result = await session.execute(stmt, data_item)
                            inserted_id = self._extract_inserted_id(result, use_returning)
                            if inserted_id:
                                inserted_ids.append(inserted_id)
                else:
                    # 单条执行
                    result = await session.execute(stmt, data_list[0])
                    inserted_id = self._extract_inserted_id(result, use_returning)
                    if inserted_id:
                        inserted_ids = [inserted_id]

                await session.commit()

                return InsertResult(inserted_count=len(data_list), inserted_ids=inserted_ids)

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
                deleted_count = result.rowcount if hasattr(result, "rowcount") else 0
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
                updated_count = result.rowcount if hasattr(result, "rowcount") else 0
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

            # 获取最大查询限制
            max_results = self.config.max_query_results

            async with self._get_session() as session:
                # 构建查询语句
                where_clause = ""
                params = {}
                if filters:
                    where_clause, params = self._filter_translator.translate(filters)

                sql = f"SELECT * FROM {table}"

                if where_clause:
                    sql += f" WHERE {where_clause}"

                # 优化策略：先查询少量数据，根据结果决定是否需要 COUNT
                # 只有当结果超过请求的 limit 时才执行 COUNT(*)
                effective_limit = min(limit or max_results, max_results)
                query_sql = sql
                if effective_limit is not None:
                    validated_limit = self._validate_limit(effective_limit)
                    query_sql = f"{sql} LIMIT {validated_limit + 1}"

                result = await session.execute(text(query_sql), params)
                data = [dict(row._mapping) for row in result.fetchall()]

                # 判断是否超过最大限制
                if len(data) > max_results:
                    raise QueryError(
                        f"Query result exceeds maximum limit of {max_results} records. "
                        f"Please add more specific filters to reduce the result size."
                    )

                # 如果结果少于请求的 limit，说明这就是全部数据，不需要 COUNT
                actual_count = len(data)
                if limit is not None and len(data) == limit + 1:
                    # 结果正好等于 limit+1，需要真正的 COUNT
                    count_sql = f"SELECT COUNT(*) FROM {table}"
                    if where_clause:
                        count_sql += f" WHERE {where_clause}"
                    count_result = await session.execute(text(count_sql), params)
                    actual_count = count_result.scalar() or 0
                    data = data[:limit]
                elif limit is not None:
                    data = data[:limit]

                return QueryResult(
                    data=data,
                    count=actual_count,
                    has_more=limit is not None and len(data) == limit and actual_count > limit,
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
            PermissionError: 权限不足时抛出
        """
        try:
            # 执行SQL安全检查（使用缓存的检查器实例）
            allow_ddl = os.getenv("MCP_DATABASE_TEST_MODE") == "true"
            check_result = self._security_checker.check(query, params, allow_ddl=allow_ddl)
            if not check_result.is_safe:
                raise QueryError(f"SQL injection detected: {check_result.reason}")

            async with self._get_session() as session:
                stmt = text(query)

                if params:
                    stmt = stmt.bindparams(**params)

                result = await session.execute(stmt)

                # 判断是否有返回数据
                # SQLAlchemy 2.0: 使用 munged_rows 或检查结果类型
                try:
                    data = [dict(row._mapping) for row in result.fetchall()]
                except Exception:
                    # 如果 fetchall 失败，说明没有返回行
                    data = None

                rows_affected = result.rowcount if hasattr(result, "rowcount") else 0
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
            if operation == "transaction":
                return await self._execute_transaction(params)
            else:
                raise QueryError(f"Unsupported operation: {operation}")

        except Exception as e:
            translated = ExceptionTranslator.translate(e, self._database_type)
            raise translated

    async def _execute_transaction(self, params: dict[str, Any]) -> AdvancedResult:
        """
        执行事务查询

        Args:
            params: 事务参数，包含 queries 列表

        Returns:
            AdvancedResult: 事务执行结果
        """
        async with self._get_session() as session:
            queries = params.get("queries", [])
            results = []

            for query_info in queries:
                query = query_info["query"]
                query_params = query_info.get("params")
                stmt = text(query)

                if query_params:
                    stmt = stmt.bindparams(**query_params)

                result = await session.execute(stmt)
                try:
                    result_data = [dict(row._mapping) for row in result.fetchall()]
                except Exception:
                    result_data = None

                results.append(
                    {
                        "rows_affected": result.rowcount if hasattr(result, "rowcount") else 0,
                        "data": result_data,
                    }
                )

            await session.commit()

            return AdvancedResult(
                operation="transaction", data={"results": results, "committed": True}
            )

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
