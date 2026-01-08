"""MongoDB 适配器"""

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from pymongo.errors import PyMongoError

from mcp_database.core.adapter import DatabaseAdapter
from mcp_database.core.exceptions import (
    ConnectionError,
    ExceptionTranslator,
    QueryError,
)
from mcp_database.core.filters import MongoFilterTranslator
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


class MongoDBAdapter(DatabaseAdapter):
    """
    MongoDB 适配器

    使用 Motor 异步驱动实现 MongoDB 操作。
    """

    def __init__(self, config: DatabaseConfig):
        """
        初始化 MongoDB 适配器

        Args:
            config: 数据库配置
        """
        super().__init__(config)
        self._client: AsyncIOMotorClient | None = None
        self._database: AsyncIOMotorDatabase | None = None
        self._connected: bool = False
        self._filter_translator = MongoFilterTranslator()

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected

    def _get_database_name(self) -> str:
        """获取数据库名称"""
        url_parts = self.config.url.split("/")
        if len(url_parts) > 3:
            return url_parts[3].split("?")[0]
        return "test"

    def _get_collection(self, table: str) -> AsyncIOMotorCollection:
        """
        获取集合

        Args:
            table: 集合名称

        Returns:
            AsyncIOMotorCollection: MongoDB 集合

        Raises:
            ConnectionError: 未连接时抛出
        """
        if not self._connected or self._database is None:
            raise ConnectionError("Not connected to MongoDB")

        return self._database[table]

    async def connect(self) -> None:
        """
        连接到 MongoDB

        Raises:
            ConnectionError: 连接失败时抛出
        """
        try:
            # 创建 MongoDB 客户端
            self._client = AsyncIOMotorClient(
                self.config.url,
                serverSelectionTimeoutMS=self.config.connect_timeout * 1000,
                socketTimeoutMS=self.config.query_timeout * 1000,
            )

            # 获取数据库
            db_name = self._get_database_name()
            self._database = self._client[db_name]

            # 测试连接
            await self._client.admin.command("ping")

            self._connected = True

        except PyMongoError as e:
            self._connected = False
            translated = ExceptionTranslator.translate(e, "mongodb")
            if isinstance(translated, ConnectionError):
                raise translated
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    async def disconnect(self) -> None:
        """断开 MongoDB 连接"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            self._connected = False

    async def insert(
        self, table: str, data: dict[str, any] | list[dict[str, any]]
    ) -> InsertResult:
        """
        插入文档

        Args:
            table: 集合名称
            data: 要插入的文档字典或列表

        Returns:
            InsertResult: 插入结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            collection = self._get_collection(table)

            # 批量插入
            if isinstance(data, list):
                result = await collection.insert_many(data)
                inserted_ids = result.inserted_ids
                inserted_count = len(inserted_ids)
            else:
                # 单条插入
                result = await collection.insert_one(data)
                inserted_ids = [result.inserted_id]
                inserted_count = 1

            return InsertResult(inserted_count=inserted_count, inserted_ids=inserted_ids)

        except PyMongoError as e:
            translated = ExceptionTranslator.translate(e, "mongodb")
            raise translated

    async def delete(self, table: str, filters: dict[str, any]) -> DeleteResult:
        """
        删除文档

        Args:
            table: 集合名称
            filters: 过滤条件

        Returns:
            DeleteResult: 删除结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            collection = self._get_collection(table)

            # 转换过滤器
            mongo_filters = self._filter_translator.translate(filters)

            result = await collection.delete_many(mongo_filters)
            deleted_count = result.deleted_count

            return DeleteResult(deleted_count=deleted_count)

        except PyMongoError as e:
            translated = ExceptionTranslator.translate(e, "mongodb")
            raise translated

    async def update(

            self,

            table: str,

            data: dict[str, any],

            filters: dict[str, any]

        ) -> UpdateResult:
        """
        更新文档

        Args:
            table: 集合名称
            data: 要更新的数据
            filters: 过滤条件

        Returns:
            UpdateResult: 更新结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            collection = self._get_collection(table)

            # 转换过滤器
            mongo_filters = self._filter_translator.translate(filters)

            result = await collection.update_many(mongo_filters, {"$set": data})
            updated_count = result.modified_count

            return UpdateResult(updated_count=updated_count)

        except PyMongoError as e:
            translated = ExceptionTranslator.translate(e, "mongodb")
            raise translated

    async def query(

            self,

            table: str,

            filters: dict[str, any] | None = None,

            limit: int | None = None

        ) -> QueryResult:
        """
        查询文档

        Args:
            table: 集合名称
            filters: 过滤条件（可选）
            limit: 返回记录数限制（可选）

        Returns:
            QueryResult: 查询结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            collection = self._get_collection(table)

            # 转换过滤器
            mongo_filters = self._filter_translator.translate(filters) if filters else {}

            # 查询总数
            total_count = await collection.count_documents(mongo_filters)

            # 检查结果大小限制
            max_results = self.config.max_query_results
            if total_count > max_results:
                raise QueryError(
                    f"Query result exceeds maximum limit of {max_results} records. "
                    f"Please add more specific filters to reduce the result size."
                )

            # 查询数据
            cursor = collection.find(mongo_filters)

            if limit:
                cursor = cursor.limit(limit)

            data = await cursor.to_list(length=None)

            # 转换 _id 为字符串
            for doc in data:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])

            return QueryResult(
                data=data,
                count=total_count,
                has_more=limit is not None and len(data) == limit and total_count > limit,
            )

        except PyMongoError as e:
            translated = ExceptionTranslator.translate(e, "mongodb")
            raise translated

    async def execute(self, query: str, params: dict[str, any] | None = None) -> ExecuteResult:
        """
        执行自定义查询（MongoDB 不支持原始 SQL）

        Args:
            query: 查询语句（MongoDB 不支持）
            params: 查询参数（可选）

        Returns:
            ExecuteResult: 执行结果

        Raises:
            QueryError: MongoDB 不支持原始 SQL 查询
        """
        raise QueryError("MongoDB does not support raw SQL queries. Use query() method instead.")

    async def advanced_query(self, operation: str, params: dict[str, any]) -> AdvancedResult:
        """
        执行高级查询（聚合、事务等）

        Args:
            operation: 操作类型（如 "aggregate", "transaction"）
            params: 操作参数

        Returns:
            AdvancedResult: 高级查询结果

        Raises:
            QueryError: 查询错误时抛出
        """
        try:
            if operation == "aggregate":
                # 聚合查询
                table = params.get("table")
                pipeline = params.get("pipeline", [])

                collection = self._get_collection(table)
                cursor = collection.aggregate(pipeline)
                data = await cursor.to_list(length=None)

                # 转换 _id 为字符串
                for doc in data:
                    if "_id" in doc:
                        doc["_id"] = str(doc["_id"])

                return AdvancedResult(operation=operation, data=data)

            elif operation == "transaction":
                # 事务操作
                table = params.get("table")
                operations = params.get("operations", [])

                collection = self._get_collection(table)
                results = []

                for op in operations:
                    op_type = op["type"]
                    op_data = op["data"]
                    op_filters = op.get("filters", {})

                    mongo_filters = self._filter_translator.translate(op_filters)

                    if op_type == "insert":
                        result = await collection.insert_one(op_data)
                        results.append({"inserted_id": str(result.inserted_id)})
                    elif op_type == "update":
                        result = await collection.update_many(mongo_filters, {"$set": op_data})
                        results.append({"modified_count": result.modified_count})
                    elif op_type == "delete":
                        result = await collection.delete_many(mongo_filters)
                        results.append({"deleted_count": result.deleted_count})

                return AdvancedResult(operation=operation, data={"results": results})

            else:
                raise QueryError(f"Unsupported operation: {operation}")

        except PyMongoError as e:
            translated = ExceptionTranslator.translate(e, "mongodb")
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
            joins=False,
            aggregation=True,
            full_text_search=True,
            geospatial=True,
        )
