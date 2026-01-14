"""过滤器 DSL 解析器"""

import re
from collections.abc import Callable
from typing import Any

from mcp_database.core.exceptions import QueryError


class RegexSecurityValidator:
    """正则表达式安全验证器"""

    MAX_REGEX_LENGTH: int = 500
    MAX_NESTED_QUANTIFIERS: int = 2
    MAX_CHAR_CLASSES: int = 10
    MAX_ALTERNATIONS: int = 20

    @classmethod
    def validate(cls, pattern: str) -> str:
        """
        验证正则表达式安全性

        Args:
            pattern: 要验证的正则表达式模式

        Returns:
            str: 验证通过的模式

        Raises:
            QueryError: 正则模式包含恶意构造或超过安全阈值
        """
        # 检查长度
        if len(pattern) > cls.MAX_REGEX_LENGTH:
            msg = f"Regex pattern exceeds maximum length of {cls.MAX_REGEX_LENGTH}"
            raise QueryError(msg)

        # 检查嵌套量词 - 任何嵌套量词都是危险的
        nested = cls._count_nested_quantifiers(pattern)
        if nested > 0:
            msg = f"Nested quantifiers detected in regex pattern: {nested}"
            raise QueryError(msg)

        # 检查字符类数量
        char_classes = len(re.findall(r"\[[^\]]*\]", pattern))
        if char_classes > cls.MAX_CHAR_CLASSES:
            msg = f"Too many character classes: {char_classes}"
            raise QueryError(msg)

        # 检查交替数量
        alternations = pattern.count("|")
        if alternations > cls.MAX_ALTERNATIONS:
            msg = f"Too many alternations: {alternations}"
            raise QueryError(msg)

        return pattern

    @classmethod
    def _count_nested_quantifiers(cls, pattern: str) -> int:
        """
        计算嵌套量词数量

        检测可能导致 ReDoS 的嵌套量词构造，如:
        - a** (量词后跟另一个量词)
        - a++ (相邻量词)
        - (a*)* (组内和组外都有量词)
        - {n}{m} (多个数量词相邻)
        """
        # 移除转义字符以简化检测
        unescaped = pattern.replace("\\", "")

        # 检测嵌套量词
        # 模式说明:
        # [*+]\s*[*+]  - 相邻量词如 **, *+, ++
        # \{\d+\}\s*\{\d+\}  - 相邻的数量词如 {2}{3}
        # [*+]\s*\{         - 量词后直接跟数量词如 *{
        nested_pattern = re.compile(r"[*+]\s*[*+]|" r"\{\d+\}\s*\{|" r"[*+]\s*\{")
        matches = nested_pattern.findall(unescaped)
        count = len(matches)

        # 检测组内外的量词嵌套，如 (a+)*
        # 查找包含量词的组：\(...[*+?{]...\) 或 \(...{n,m}...\)
        group_with_quantifier = re.compile(
            r"\([^)]*[*+?\{][^)]*\)[*+?]|\([^)]*\{\d+(?:,\d*)?\}[^)]*\)[*+?{]"
        )
        group_matches = group_with_quantifier.findall(unescaped)
        count += len(group_matches)

        return count


# 正则表达式安全阈值配置 (保留用于向后兼容)
MAX_REGEX_LENGTH: int = RegexSecurityValidator.MAX_REGEX_LENGTH
MAX_NESTED_QUANTIFIERS: int = RegexSecurityValidator.MAX_NESTED_QUANTIFIERS
MAX_CHAR_CLASSES: int = RegexSecurityValidator.MAX_CHAR_CLASSES


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

        return self._translate_list_condition(field, values, "IN")

    def _translate_not_in(self, field: str, values: list[Any]) -> tuple[str, dict[str, Any]]:
        """转换 NOT IN 操作符"""
        if not values:
            return "1=1", {}

        return self._translate_list_condition(field, values, "NOT IN")

    def _translate_list_condition(
        self, field: str, values: list[Any], operator: str
    ) -> tuple[str, dict[str, Any]]:
        """
        通用列表条件转换方法

        Args:
            field: 字段名
            values: 值列表
            operator: SQL 操作符 (IN 或 NOT IN)

        Returns:
            (SQL 条件, 参数字典)
        """
        prefix = "in" if operator == "IN" else "notin"
        placeholders = []
        params = {}
        for i, value in enumerate(values):
            param_name = f"{field}_{prefix}_{i}"
            placeholders.append(f":{param_name}")
            params[param_name] = value

        return f"{field} {operator} ({', '.join(placeholders)})", params

    def _translate_isnull(self, field: str, value: Any) -> tuple[str, dict[str, Any]]:
        """转换 IS NULL 操作符"""
        if not isinstance(value, bool):
            raise QueryError(f"Filter '{field}__isnull' must be true or false")
        return f"{field} IS {'NULL' if value else 'NOT NULL'}", {}

    def _translate_notnull(self, field: str, value: Any) -> tuple[str, dict[str, Any]]:
        """转换 NOT NULL 操作符（与 isnull 反向）"""
        if not isinstance(value, bool):
            raise QueryError(f"Filter '{field}__notnull' must be true or false")
        return f"{field} IS {'NOT NULL' if value else 'NULL'}", {}


class MongoFilterTranslator:
    """MongoDB 过滤器转换器"""

    def __init__(self) -> None:
        self._regex_validator = RegexSecurityValidator()

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

    def _translate_contains(self, value: Any) -> dict[str, Any]:
        """
        转换 contains 操作符

        Args:
            value: 包含的值

        Returns:
            MongoDB $regex 查询条件

        Raises:
            QueryError: 正则模式包含恶意构造或超过安全阈值
        """
        str_value = str(value)
        # 使用正则验证器进行安全检查
        self._regex_validator.validate(str_value)
        # 对值进行转义以防止注入
        return {"$regex": re.escape(str_value), "$options": "i"}

    def _translate_operator(self, operator: str, value: Any) -> dict[str, Any]:
        """转换操作符"""
        # 对正则操作符进行安全验证
        if operator in ("contains", "startswith", "endswith"):
            str_value = str(value)
            if operator == "contains":
                return self._translate_contains(str_value)
            elif operator == "startswith":
                return {"$regex": f"^{re.escape(str_value)}", "$options": "i"}
            elif operator == "endswith":
                return {"$regex": f"{re.escape(str_value)}$", "$options": "i"}

        operator_map = {
            "gt": {"$gt": value},
            "lt": {"$lt": value},
            "gte": {"$gte": value},
            "lte": {"$lte": value},
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
