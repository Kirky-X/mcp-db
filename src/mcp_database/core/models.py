"""核心数据模型定义"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class InsertResult(BaseModel):
    """插入操作结果"""

    inserted_count: int = Field(..., ge=0, description="插入的记录数")
    inserted_ids: list[Any] = Field(default_factory=list, description="插入的 ID 列表")
    success: bool = Field(default=True, description="操作是否成功")


class UpdateResult(BaseModel):
    """更新操作结果"""

    updated_count: int = Field(..., ge=0, description="更新的记录数")
    success: bool = Field(default=True, description="操作是否成功")


class DeleteResult(BaseModel):
    """删除操作结果"""

    deleted_count: int = Field(..., ge=0, description="删除的记录数")
    success: bool = Field(default=True, description="操作是否成功")


class QueryResult(BaseModel):
    """查询操作结果"""

    data: list[dict[str, Any]] = Field(default_factory=list, description="查询结果数据")
    count: int = Field(..., ge=0, description="匹配的记录总数")
    has_more: bool = Field(default=False, description="是否还有更多数据")


class ExecuteResult(BaseModel):
    """执行命令结果"""

    rows_affected: int = Field(..., ge=0, description="影响的行数")
    data: list[dict[str, Any]] | None = Field(default=None, description="返回的数据")
    success: bool = Field(default=True, description="操作是否成功")


class AdvancedResult(BaseModel):
    """高级查询结果"""

    operation: str = Field(..., description="操作类型")
    data: Any = Field(..., description="操作结果数据")
    success: bool = Field(default=True, description="操作是否成功")


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
    pool_size: int = Field(default=5, ge=1, description="连接池大小")
    max_overflow: int = Field(default=10, ge=0, description="最大溢出连接数")
    connect_timeout: int = Field(default=10, ge=1, description="连接超时（秒）")
    query_timeout: int = Field(default=30, ge=1, description="查询超时（秒）")
    max_query_results: int = Field(default=10000, ge=1, description="查询结果最大数量")
    options: dict[str, Any] = Field(default_factory=dict, description="其他配置选项")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """验证 URL 格式"""
        if not v:
            raise ValueError("Database URL cannot be empty")
        return v
