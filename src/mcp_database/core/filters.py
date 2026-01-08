"""过滤器 DSL 解析器"""

import re
from collections.abc import Callable
from typing import Any

from mcp_database.core.exceptions import QueryError


class FilterParser:
    """过滤器解析器基类"""

    def parse(self, filters: dict[str, Any]) -> dict[str, Any] | None:
        """
        解析过滤器

        Args:
            filters: 过滤器字典

        Returns:
            解析后的过滤器，如果为空则返回 None
        """
        if not filters:
            return None

        filtered = {k: v for k, v in filters.items() if v is not None}
        if not filtered:
            return None
        return filtered


class SQLFilterTranslator:
    """SQL 过滤器转换器 - 使用参数化查询防止 SQL 注入"""

    def translate(self, filters: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """
        将过滤器转换为 SQL WHERE 子句和参数字典

        Args:
            filters: 过滤器字典

        Returns:
            (WHERE 子句, 参数字典)

        Raises:
            QueryError: 过滤器包含无效值时抛出
        """
        if not filters:
            return "", {}

        conditions = []
        params = {}

        for key, value in filters.items():
            if "__" in key:
                field, operator = key.rsplit("__", 1)
                condition, field_params = self._translate_operator(field, operator, value)
            else:
                condition, field_params = self._translate_equality(key, value)

            if condition:
                conditions.append(condition)
                params.update(field_params)

        where_clause = " AND ".join(conditions) if conditions else ""
        return where_clause, params

    def _translate_equality(self, field: str, value: Any) -> tuple[str, dict[str, Any]]:
        """转换等值条件 - 使用参数化查询"""
        if value is None:
            msg = "Filter '{}' cannot have None value. Use '{}__isnull=True' for null queries."
            raise QueryError(msg.format(field, field))
        param_name = f"{field}_eq"
        return f"{field} = :{param_name}", {param_name: value}

    def _translate_operator(
        self, field: str, operator: str, value: Any
    ) -> tuple[str, dict[str, Any]]:
        """转换操作符 - 使用参数化查询"""
        param_name = f"{field}_{operator}"

        operator_map = {
            "gt": lambda: (f"{field} > :{param_name}", {param_name: value}),
            "lt": lambda: (f"{field} < :{param_name}", {param_name: value}),
            "gte": lambda: (f"{field} >= :{param_name}", {param_name: value}),
            "lte": lambda: (f"{field} <= :{param_name}", {param_name: value}),
            "contains": lambda: (f"{field} LIKE :{param_name}", {param_name: f"%{value}%"}),
            "startswith": lambda: (f"{field} LIKE :{param_name}", {param_name: f"{value}%"}),
            "endswith": lambda: (f"{field} LIKE :{param_name}", {param_name: f"%{value}"}),
            "in": lambda: self._translate_in(field, value),
            "not_in": lambda: self._translate_not_in(field, value),
            "isnull": lambda: self._translate_isnull(field, value),
            "notnull": lambda: self._translate_notnull(field, value),
        }

        if operator in operator_map:
            return operator_map[operator]()

        return self._translate_equality(field, value)

    def _translate_in(self, field: str, values: list[Any]) -> tuple[str, dict[str, Any]]:
        """转换 IN 操作符"""
        if not values:
            return "1=0", {}

        placeholders = []
        params = {}
        for i, value in enumerate(values):
            param_name = f"{field}_in_{i}"
            placeholders.append(f":{param_name}")
            params[param_name] = value

        return f"{field} IN ({', '.join(placeholders)})", params

    def _translate_not_in(self, field: str, values: list[Any]) -> tuple[str, dict[str, Any]]:
        """转换 NOT IN 操作符"""
        if not values:
            return "1=1", {}

        placeholders = []
        params = {}
        for i, value in enumerate(values):
            param_name = f"{field}_notin_{i}"
            placeholders.append(f":{param_name}")
            params[param_name] = value

        return f"{field} NOT IN ({', '.join(placeholders)})", params

    def _translate_isnull(self, field: str, value: Any) -> tuple[str, dict[str, Any]]:
        """转换 IS NULL 操作符"""
        if not isinstance(value, bool):
            raise QueryError(f"Filter '{field}__isnull' must be true or false")
        if value:
            return f"{field} IS NULL", {}
        else:
            return f"{field} IS NOT NULL", {}

    def _translate_notnull(self, field: str, value: Any) -> tuple[str, dict[str, Any]]:
        """转换 NOT NULL 操作符（与 isnull 反向）"""
        if not isinstance(value, bool):
            raise QueryError(f"Filter '{field}__notnull' must be true or false")
        if value:
            return f"{field} IS NOT NULL", {}
        else:
            return f"{field} IS NULL", {}


class MongoFilterTranslator:
    """MongoDB 过滤器转换器"""

    def translate(self, filters: dict[str, Any]) -> dict[str, Any]:
        """
        将过滤器转换为 MongoDB 查询条件

        Args:
            filters: 过滤器字典

        Returns:
            MongoDB 查询条件
        """
        mongo_filters = {}

        for key, value in filters.items():
            if "__" in key:
                field, operator = key.rsplit("__", 1)
                mongo_filters[field] = self._translate_operator(operator, value)
            else:
                mongo_filters[key] = value

        return mongo_filters

    def _translate_operator(self, operator: str, value: Any) -> dict[str, Any]:
        """转换操作符"""
        operator_map = {
            "gt": {"$gt": value},
            "lt": {"$lt": value},
            "gte": {"$gte": value},
            "lte": {"$lte": value},
            "contains": {"$regex": str(value), "$options": "i"},
            "startswith": {"$regex": f"^{re.escape(str(value))}", "$options": "i"},
            "endswith": {"$regex": f"{re.escape(str(value))}$", "$options": "i"},
            "in": {"$in": value},
            "not_in": {"$nin": value},
            "isnull": {"$exists": False} if value else {"$exists": True},
            "notnull": {"$exists": True} if value else {"$exists": False},
        }

        return operator_map.get(operator, value)


class RedisFilterTranslator:
    """Redis 过滤器转换器"""

    def translate(self, filters: dict[str, Any]) -> Callable[[dict[str, Any]], bool]:
        """
        将过滤器转换为过滤函数

        Args:
            filters: 过滤器字典

        Returns:
            过滤函数
        """

        def filter_func(data: dict[str, Any]) -> bool:
            """过滤函数"""
            for key, value in filters.items():
                if "__" in key:
                    field, operator = key.rsplit("__", 1)
                    if not self._check_operator(data, field, operator, value):
                        return False
                else:
                    if data.get(key) != value:
                        return False
            return True

        return filter_func

    def _check_operator(self, data: dict[str, Any], field: str, operator: str, value: Any) -> bool:
        """检查操作符条件"""
        field_value = data.get(field)

        if operator == "gt":
            return field_value is not None and field_value > value
        elif operator == "lt":
            return field_value is not None and field_value < value
        elif operator == "gte":
            return field_value is not None and field_value >= value
        elif operator == "lte":
            return field_value is not None and field_value <= value
        elif operator == "contains":
            return field_value is not None and value in str(field_value)
        elif operator == "startswith":
            return field_value is not None and str(field_value).startswith(str(value))
        elif operator == "endswith":
            return field_value is not None and str(field_value).endswith(str(value))
        elif operator == "in":
            return field_value in value
        elif operator == "not_in":
            return field_value not in value
        elif operator == "isnull":
            if not isinstance(value, bool):
                return False
            return field_value is None if value else field_value is not None
        elif operator == "notnull":
            if not isinstance(value, bool):
                return False
            return field_value is not None if value else field_value is None

        return field_value == value
