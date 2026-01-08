"""测试工具类，提供数据库连接、环境清理和测试数据生成功能"""

import asyncio
import os
import random
import string
from typing import Any


class TestDataGenerator:
    """测试数据生成器"""

    @staticmethod
    def random_string(length: int = 10) -> str:
        """生成随机字符串"""
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def random_email() -> str:
        """生成随机邮箱"""
        return f"test_{TestDataGenerator.random_string(8)}@example.com"

    @staticmethod
    def random_user() -> dict[str, Any]:
        """生成随机用户数据"""
        return {
            "name": f"User_{TestDataGenerator.random_string(8)}",
            "email": TestDataGenerator.random_email(),
            "age": random.randint(18, 80),
            "active": random.choice([True, False]),
            "score": random.uniform(0.0, 100.0),
        }

    @staticmethod
    def generate_users(count: int) -> list[dict[str, Any]]:
        """生成多个用户数据"""
        return [TestDataGenerator.random_user() for _ in range(count)]

    @staticmethod
    def random_product() -> dict[str, Any]:
        """生成随机产品数据"""
        return {
            "name": f"Product_{TestDataGenerator.random_string(8)}",
            "price": round(random.uniform(10.0, 1000.0), 2),
            "quantity": random.randint(1, 100),
            "category": random.choice(["Electronics", "Books", "Clothing", "Food"]),
            "in_stock": random.choice([True, False]),
        }

    @staticmethod
    def generate_products(count: int) -> list[dict[str, Any]]:
        """生成多个产品数据"""
        return [TestDataGenerator.random_product() for _ in range(count)]


class DatabaseTestUtils:
    """数据库测试工具类"""

    # 数据库连接配置
    POSTGRES_URL = os.getenv(
        "TEST_POSTGRES_URL", "postgresql+asyncpg://testuser:testpass@localhost:15432/testdb"
    )
    MYSQL_URL = os.getenv(
        "TEST_MYSQL_URL", "mysql+aiomysql://testuser:testpass@localhost:13306/testdb"
    )
    SQLITE_URL = os.getenv("TEST_SQLITE_URL", "sqlite+aiosqlite:///:memory:")
    MONGODB_URL = os.getenv(
        "TEST_MONGODB_URL", "mongodb://testuser:testpass@localhost:27018/testdb?authSource=admin"
    )
    REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://:testpass@localhost:16379/0")
    OPENSEARCH_URL = os.getenv("TEST_OPENSEARCH_URL", "http://localhost:19200")

    @staticmethod
    async def create_test_table(adapter, table_name: str, schema: dict[str, str]) -> None:
        """
        创建测试表

        Args:
            adapter: 数据库适配器
            table_name: 表名
            schema: 表结构定义
        """
        db_type = adapter.config.url.split("+")[0].split(":")[0]

        if db_type in ["postgresql", "mysql", "sqlite"]:
            columns = []
            for col_name, col_type in schema.items():
                # PostgreSQL ID 字段使用 SERIAL 实现自增
                if db_type == "postgresql" and col_name == "id" and "PRIMARY KEY" in col_type:
                    col_type = col_type.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
                # MySQL ID 字段使用 AUTO_INCREMENT 实现自增
                elif db_type == "mysql" and col_name == "id" and "PRIMARY KEY" in col_type:
                    col_type = col_type.replace(
                        "INTEGER PRIMARY KEY", "INTEGER AUTO_INCREMENT PRIMARY KEY"
                    )
                columns.append(f"{col_name} {col_type}")

            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            await adapter.execute(sql)

        elif db_type == "mongodb":
            # MongoDB 不需要预先创建集合
            pass

        elif db_type == "redis":
            # Redis 不需要预先创建表
            pass

        elif db_type == "http":
            # OpenSearch 需要创建索引
            if hasattr(adapter, "_client"):
                await adapter._client.indices.create(
                    index=table_name,
                    body={
                        "mappings": {
                            "properties": {
                                name: {"type": "text"} if typ == "TEXT" else {"type": typ.lower()}
                                for name, typ in schema.items()
                            }
                        }
                    },
                )

    @staticmethod
    async def drop_test_table(adapter, table_name: str) -> None:
        """
        删除测试表

        Args:
            adapter: 数据库适配器
            table_name: 表名
        """
        db_type = adapter.config.url.split("+")[0].split(":")[0]

        if db_type in ["postgresql", "mysql", "sqlite"]:
            try:
                await adapter.execute(f"DROP TABLE IF EXISTS {table_name}")
            except Exception:
                pass

        elif db_type == "mongodb":
            try:
                collection = adapter._database[table_name]
                await collection.drop()
            except Exception:
                pass

        elif db_type == "redis":
            try:
                # 删除所有匹配的键
                pattern = f"{table_name}:*"
                keys = []
                async for key in adapter._client.scan_iter(match=pattern):
                    keys.append(key)
                if keys:
                    await adapter._client.delete(*keys)
            except Exception:
                pass

        elif db_type == "http":
            try:
                if hasattr(adapter, "_client"):
                    await adapter._client.indices.delete(index=table_name)
            except Exception:
                pass

    @staticmethod
    async def clear_test_data(adapter, table_name: str) -> None:
        """
        清空测试数据（不删除表）

        Args:
            adapter: 数据库适配器
            table_name: 表名
        """
        db_type = adapter.config.url.split("+")[0].split(":")[0]

        if db_type in ["postgresql", "mysql", "sqlite"]:
            try:
                await adapter.execute(f"DELETE FROM {table_name}")
            except Exception:
                pass

        elif db_type == "mongodb":
            try:
                collection = adapter._database[table_name]
                await collection.delete_many({})
            except Exception:
                pass

        elif db_type == "redis":
            try:
                pattern = f"{table_name}:*"
                keys = []
                async for key in adapter._client.scan_iter(match=pattern):
                    keys.append(key)
                if keys:
                    await adapter._client.delete(*keys)
            except Exception:
                pass

        elif db_type == "http":
            try:
                if hasattr(adapter, "_client"):
                    await adapter._client.delete_by_query(
                        index=table_name, body={"query": {"match_all": {}}}
                    )
            except Exception:
                pass

    @staticmethod
    def get_test_schema() -> dict[str, str]:
        """获取标准测试表结构"""
        return {
            "id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(100)",
            "email": "VARCHAR(255)",
            "age": "INTEGER",
            "active": "BOOLEAN",
            "score": "FLOAT",
            "created_at": "TIMESTAMP",
        }

    @staticmethod
    def get_product_schema() -> dict[str, str]:
        """获取产品测试表结构"""
        return {
            "id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(100)",
            "price": "FLOAT",
            "quantity": "INTEGER",
            "category": "VARCHAR(50)",
            "in_stock": "BOOLEAN",
        }


async def wait_for_database_connection(adapter, max_retries: int = 10, delay: float = 1.0) -> bool:
    """
    等待数据库连接就绪

    Args:
        adapter: 数据库适配器
        max_retries: 最大重试次数
        delay: 重试延迟（秒）

    Returns:
        是否连接成功
    """
    for attempt in range(max_retries):
        try:
            await adapter.connect()
            if adapter.is_connected:
                return True
        except Exception:
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                raise
    return False


def skip_if_database_not_available(url_env_var: str):
    """
    跳过测试装饰器，如果数据库不可用

    Args:
        url_env_var: 环境变量名
    """
    import pytest

    url = os.getenv(url_env_var)
    if not url:
        return pytest.mark.skip(f"Database not available: {url_env_var} not set")
    return pytest.mark.skipif(False, reason="Database available")
