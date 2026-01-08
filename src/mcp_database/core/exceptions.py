"""异常体系定义"""


class DatabaseError(Exception):
    """数据库错误基类"""

    def __init__(self, message: str, database_type: str | None = None):
        super().__init__(message)
        self.database_type = database_type
        self.original_error: Exception | None = None


class ConnectionError(DatabaseError):
    """连接错误"""

    pass


class QueryError(DatabaseError):
    """查询错误"""

    pass


class PermissionError(DatabaseError):
    """权限错误"""

    pass


class IntegrityError(DatabaseError):
    """完整性错误（如唯一约束、外键约束）"""

    pass


class TimeoutError(DatabaseError):
    """超时错误"""

    pass


class ExceptionTranslator:
    """异常转换器"""

    # PostgreSQL 错误映射
    POSTGRESQL_ERROR_MAP = {
        "duplicate key": IntegrityError,
        "unique constraint": IntegrityError,
        "foreign key": IntegrityError,
        "connection refused": ConnectionError,
        "timeout": TimeoutError,
    }

    # MySQL 错误映射
    MYSQL_ERROR_MAP = {
        "duplicate entry": IntegrityError,
        "foreign key constraint": IntegrityError,
        "can't connect": ConnectionError,
        "timeout": TimeoutError,
    }

    # SQLite 错误映射
    SQLITE_ERROR_MAP = {
        "unique constraint": IntegrityError,
        "foreign key": IntegrityError,
        "database is locked": TimeoutError,
    }

    # MongoDB 错误映射
    MONGODB_ERROR_MAP = {
        "duplicate key": IntegrityError,
        "network timeout": TimeoutError,
        "connection": ConnectionError,
    }

    # Redis 错误映射
    REDIS_ERROR_MAP = {
        "connection": ConnectionError,
        "timeout": TimeoutError,
    }

    @classmethod
    def translate(cls, original_error: Exception, database_type: str) -> DatabaseError:
        """
        将数据库特定异常转换为标准异常

        Args:
            original_error: 原始异常
            database_type: 数据库类型

        Returns:
            转换后的标准异常
        """
        error_message = str(original_error).lower()
        database_type = database_type.lower()

        # 选择错误映射表
        error_map = cls._get_error_map(database_type)

        # 尝试匹配错误类型
        error_class = DatabaseError  # 默认
        for pattern, mapped_class in error_map.items():
            if pattern in error_message:
                error_class = mapped_class
                break

        # 创建转换后的异常
        translated_error = error_class(str(original_error), database_type=database_type)
        translated_error.original_error = original_error

        return translated_error

    @classmethod
    def _get_error_map(cls, database_type: str) -> dict:
        """获取错误映射表"""
        if database_type in ["postgresql", "postgres"]:
            return cls.POSTGRESQL_ERROR_MAP
        elif database_type == "mysql":
            return cls.MYSQL_ERROR_MAP
        elif database_type == "sqlite":
            return cls.SQLITE_ERROR_MAP
        elif database_type == "mongodb":
            return cls.MONGODB_ERROR_MAP
        elif database_type == "redis":
            return cls.REDIS_ERROR_MAP
        else:
            return {}
