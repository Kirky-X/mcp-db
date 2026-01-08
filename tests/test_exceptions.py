"""测试异常体系"""


class TestDatabaseError:
    """测试 DatabaseError 基类"""

    def test_database_error_creation(self):
        """测试创建数据库错误"""
        from mcp_database.core.exceptions import DatabaseError

        error = DatabaseError("Test error")
        assert str(error) == "Test error"
        assert error.database_type is None

    def test_database_error_with_type(self):
        """测试带数据库类型的错误"""
        from mcp_database.core.exceptions import DatabaseError

        error = DatabaseError("Test error", database_type="postgresql")
        assert error.database_type == "postgresql"


class TestConnectionError:
    """测试 ConnectionError"""

    def test_connection_error(self):
        """测试连接错误"""
        from mcp_database.core.exceptions import ConnectionError, DatabaseError

        error = ConnectionError("Cannot connect to database", database_type="postgresql")
        assert isinstance(error, DatabaseError)
        assert error.database_type == "postgresql"


class TestQueryError:
    """测试 QueryError"""

    def test_query_error(self):
        """测试查询错误"""
        from mcp_database.core.exceptions import DatabaseError, QueryError

        error = QueryError("Invalid query", database_type="mysql")
        assert isinstance(error, DatabaseError)


class TestPermissionError:
    """测试 PermissionError"""

    def test_permission_error(self):
        """测试权限错误"""
        from mcp_database.core.exceptions import DatabaseError, PermissionError

        error = PermissionError("INSERT operation is disabled")
        assert isinstance(error, DatabaseError)
        assert "INSERT" in str(error)


class TestIntegrityError:
    """测试 IntegrityError"""

    def test_integrity_error(self):
        """测试完整性错误"""
        from mcp_database.core.exceptions import DatabaseError, IntegrityError

        error = IntegrityError("Duplicate key", database_type="postgresql")
        assert isinstance(error, DatabaseError)


class TestTimeoutError:
    """测试 TimeoutError"""

    def test_timeout_error(self):
        """测试超时错误"""
        from mcp_database.core.exceptions import DatabaseError, TimeoutError

        error = TimeoutError("Query timeout", database_type="mongodb")
        assert isinstance(error, DatabaseError)


class TestExceptionTranslator:
    """测试异常转换器"""

    def test_translate_postgresql_unique_violation(self):
        """测试 PostgreSQL 唯一约束错误转换"""
        from mcp_database.core.exceptions import ExceptionTranslator, IntegrityError

        # 模拟 PostgreSQL 唯一约束错误
        original_error = Exception("duplicate key value violates unique constraint")

        translated = ExceptionTranslator.translate(original_error, "postgresql")
        assert isinstance(translated, IntegrityError)
        assert translated.database_type == "postgresql"

    def test_translate_mysql_connection_error(self):
        """测试 MySQL 连接错误转换"""
        from mcp_database.core.exceptions import ConnectionError, ExceptionTranslator

        original_error = ConnectionRefusedError("Can't connect to MySQL server")

        translated = ExceptionTranslator.translate(original_error, "mysql")
        assert isinstance(translated, ConnectionError)

    def test_translate_unknown_error(self):
        """测试未知错误转换"""
        from mcp_database.core.exceptions import DatabaseError, ExceptionTranslator

        original_error = ValueError("Unknown error")

        translated = ExceptionTranslator.translate(original_error, "sqlite")
        assert isinstance(translated, DatabaseError)

    def test_translate_with_original_error(self):
        """测试保留原始错误信息"""
        from mcp_database.core.exceptions import ExceptionTranslator

        original_error = Exception("Original error message")

        translated = ExceptionTranslator.translate(original_error, "postgresql")
        assert "Original error message" in str(translated)
        assert translated.original_error is original_error

    def test_translate_postgresql_timeout(self):
        """测试 PostgreSQL 超时错误转换"""
        from mcp_database.core.exceptions import ExceptionTranslator, TimeoutError

        original_error = Exception("connection timeout")

        translated = ExceptionTranslator.translate(original_error, "postgresql")
        assert isinstance(translated, TimeoutError)

    def test_translate_sqlite_locked(self):
        """测试 SQLite 数据库锁定错误转换"""
        from mcp_database.core.exceptions import ExceptionTranslator, TimeoutError

        original_error = Exception("database is locked")

        translated = ExceptionTranslator.translate(original_error, "sqlite")
        assert isinstance(translated, TimeoutError)

    def test_translate_mongodb_network_timeout(self):
        """测试 MongoDB 网络超时错误转换"""
        from mcp_database.core.exceptions import ExceptionTranslator, TimeoutError

        original_error = Exception("network timeout")

        translated = ExceptionTranslator.translate(original_error, "mongodb")
        assert isinstance(translated, TimeoutError)

    def test_translate_redis_connection(self):
        """测试 Redis 连接错误转换"""
        from mcp_database.core.exceptions import ConnectionError, ExceptionTranslator

        original_error = Exception("connection error")

        translated = ExceptionTranslator.translate(original_error, "redis")
        assert isinstance(translated, ConnectionError)

    def test_translate_preserves_database_type(self):
        """测试转换器保留数据库类型"""
        from mcp_database.core.exceptions import ExceptionTranslator

        for db_type in ["postgresql", "mysql", "sqlite", "mongodb", "redis"]:
            original_error = Exception("test error")
            translated = ExceptionTranslator.translate(original_error, db_type)
            assert translated.database_type == db_type
