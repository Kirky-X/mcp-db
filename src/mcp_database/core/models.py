"""核心数据模型定义"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

# 配置常量
DEFAULT_POOL_SIZE = 5
DEFAULT_MAX_OVERFLOW = 10
DEFAULT_CONNECT_TIMEOUT = 10
DEFAULT_QUERY_TIMEOUT = 30
DEFAULT_MAX_QUERY_RESULTS = 10000
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_LIMIT = 100
MAX_LIMIT = 10000


class OperationResult(BaseModel):
    """操作结果基类"""

    success: bool = Field(default=True, description="操作是否成功")


class InsertResult(OperationResult):
    """插入操作结果"""

    inserted_count: int = Field(..., ge=0, description="插入的记录数")
    inserted_ids: list[Any] = Field(default_factory=list, description="插入的 ID 列表")


class UpdateResult(OperationResult):
    """更新操作结果"""

    updated_count: int = Field(..., ge=0, description="更新的记录数")


class DeleteResult(OperationResult):
    """删除操作结果"""

    deleted_count: int = Field(..., ge=0, description="删除的记录数")


class QueryResult(OperationResult):
    """查询操作结果"""

    data: list[dict[str, Any]] = Field(default_factory=list, description="查询结果数据")
    count: int = Field(..., ge=0, description="匹配的记录总数")
    has_more: bool = Field(default=False, description="是否还有更多数据")


class ExecuteResult(OperationResult):
    """执行命令结果"""

    rows_affected: int = Field(..., ge=0, description="影响的行数")
    data: list[dict[str, Any]] | None = Field(default=None, description="返回的数据")


class AdvancedResult(OperationResult):
    """高级查询结果"""

    operation: str = Field(..., description="操作类型")
    data: Any = Field(..., description="操作结果数据")


class Capability(BaseModel):
    """数据库能力描述"""

    basic_crud: bool = Field(default=True, description="是否支持基础 CRUD")
    transactions: bool = Field(default=False, description="是否支持事务")
    joins: bool = Field(default=False, description="是否支持 JOIN")
    aggregation: bool = Field(default=False, description="是否支持聚合")
    full_text_search: bool = Field(default=False, description="是否支持全文搜索")
    geospatial: bool = Field(default=False, description="是否支持地理空间查询")


class DatabaseConfig(BaseModel):
    """数据库配置"""

    url: str = Field(..., description="数据库连接 URL")
    pool_size: int = Field(default=DEFAULT_POOL_SIZE, ge=1, description="连接池大小")
    max_overflow: int = Field(default=DEFAULT_MAX_OVERFLOW, ge=0, description="最大溢出连接数")
    connect_timeout: int = Field(
        default=DEFAULT_CONNECT_TIMEOUT, ge=1, description="连接超时（秒）"
    )
    query_timeout: int = Field(default=DEFAULT_QUERY_TIMEOUT, ge=1, description="查询超时（秒）")
    max_query_results: int = Field(
        default=DEFAULT_MAX_QUERY_RESULTS, ge=1, description="查询结果最大数量"
    )
    options: dict[str, Any] = Field(default_factory=dict, description="其他配置选项")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """验证 URL 格式并检查安全性"""
        import logging

        if not v:
            raise ValueError("Database URL cannot be empty")

        # 检查 URL 长度防止资源耗尽
        if len(v) > 2000:
            raise ValueError("Database URL exceeds maximum length")

        # 核心安全检查：只阻止明显危险或无效的 scheme
        try:
            from urllib.parse import urlparse

            parsed = urlparse(v)
            if parsed.scheme:
                scheme_lower = parsed.scheme.lower()
                # 阻止空 scheme 或常见危险 scheme
                forbidden_schemes = {"javascript", "data:", "file:", "vbscript"}
                if scheme_lower in forbidden_schemes:
                    raise ValueError(f"Invalid database scheme: {parsed.scheme}")
                # 检查 scheme 格式是否有效（应只包含字母、数字、+）
                if not all(c.isalnum() or c in "+-" for c in scheme_lower):
                    raise ValueError(f"Invalid scheme format: {parsed.scheme}")

            # 安全警告：检查 URL 中是否包含嵌入式凭据
            if parsed.password or parsed.username:
                logger = logging.getLogger(__name__)
                logger.warning(
                    "Security advisory: Database URL contains embedded credentials. "
                    "Consider using environment variables instead. "
                    "URL format: %s://[username]:[password]@host...",
                    parsed.scheme if parsed.scheme else "unknown",
                )

        except ValueError:
            raise
        except Exception as e:
            raise ValueError("Invalid database URL format") from e

        return v
