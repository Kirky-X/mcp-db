"""SQL 安全检查器"""

import re
from dataclasses import dataclass
from typing import Any

import sqlparse


@dataclass
class SecurityCheckResult:
    """安全检查结果"""

    is_safe: bool
    reason: str | None = None


class SQLSecurityChecker:
    """
    SQL 安全检查器

    检测危险的 SQL 命令和 SQL 注入攻击。
    """

    # 危险关键字（需要 WHERE 条件的命令）
    DANGEROUS_WITHOUT_WHERE = ["DELETE", "UPDATE"]

    # 禁止的关键字
    FORBIDDEN_KEYWORDS = ["DROP", "TRUNCATE", "ALTER", "GRANT", "CREATE"]

    # SQL 注入模式
    INJECTION_PATTERNS = [
        r";\s*DROP",  # DROP 注入
        r";\s*TRUNCATE",  # TRUNCATE 注入
        r";\s*DELETE",  # DELETE 注入
        r"--",  # 注释注入
        r"/\*.*\*/",  # 多行注释注入
        r"UNION\s+SELECT",  # UNION 注入
        r"1\s*=\s*1",  # 布尔注入
        r"OR\s+1\s*=\s*1",  # OR 注入
        r"AND\s+1\s*=\s*1",  # AND 注入
    ]

    def __init__(self):
        """初始化安全检查器"""
        self._injection_regex = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.INJECTION_PATTERNS
        ]

    def check(self, query: str, params: dict[str, Any] | None = None) -> SecurityCheckResult:
        """
        检查 SQL 查询的安全性

        Args:
            query: SQL 查询语句
            params: 查询参数（可选）

        Returns:
            SecurityCheckResult: 安全检查结果
        """
        # 检查禁止的关键字
        forbidden_result = self._check_forbidden_keywords(query)
        if not forbidden_result.is_safe:
            return forbidden_result

        # 检查 SQL 注入模式
        injection_result = self._check_injection_patterns(query)
        if not injection_result.is_safe:
            return injection_result

        # 检查需要 WHERE 条件的命令
        where_result = self._check_where_clause(query)
        if not where_result.is_safe:
            return where_result

        # 检查参数化查询
        param_result = self._check_parameters(query, params)
        if not param_result.is_safe:
            return param_result

        return SecurityCheckResult(is_safe=True)

    def _check_forbidden_keywords(self, query: str) -> SecurityCheckResult:
        """
        检查禁止的关键字

        Args:
            query: SQL 查询语句

        Returns:
            SecurityCheckResult: 安全检查结果
        """
        query_upper = query.upper()

        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in query_upper:
                return SecurityCheckResult(is_safe=False, reason=f"禁止的关键字: {keyword}")

        return SecurityCheckResult(is_safe=True)

    def _check_injection_patterns(self, query: str) -> SecurityCheckResult:
        """
        检查 SQL 注入模式

        Args:
            query: SQL 查询语句

        Returns:
            SecurityCheckResult: 安全检查结果
        """
        for pattern in self._injection_regex:
            if pattern.search(query):
                return SecurityCheckResult(is_safe=False, reason="检测到 SQL 注入模式")

        return SecurityCheckResult(is_safe=True)

    def _check_where_clause(self, query: str) -> SecurityCheckResult:
        """
        检查需要 WHERE 条件的命令

        Args:
            query: SQL 查询语句

        Returns:
            SecurityCheckResult: 安全检查结果
        """
        # 解析 SQL
        parsed = sqlparse.parse(query)
        if not parsed:
            return SecurityCheckResult(is_safe=True)

        statement = parsed[0]

        # 获取第一个关键字
        first_keyword = None
        for token in statement.flatten():
            token_str = str(token).strip().upper()
            if token_str in ["DELETE", "UPDATE", "INSERT", "SELECT"]:
                first_keyword = token_str
                break

        if not first_keyword:
            return SecurityCheckResult(is_safe=True)

        # 检查是否是需要 WHERE 条件的命令
        if first_keyword in self.DANGEROUS_WITHOUT_WHERE:
            # 检查是否有 WHERE 子句
            has_where = False
            for token in statement.flatten():
                token_str = str(token).strip().upper()
                if token_str == "WHERE":
                    has_where = True
                    break

            if not has_where:
                return SecurityCheckResult(
                    is_safe=False, reason=f"{first_keyword} 命令缺少 WHERE 条件"
                )

        return SecurityCheckResult(is_safe=True)

    def _check_parameters(
        self, query: str, params: dict[str, Any] | None
    ) -> SecurityCheckResult:
        """
        检查参数化查询

        Args:
            query: SQL 查询语句
            params: 查询参数

        Returns:
            SecurityCheckResult: 安全检查结果
        """
        # 提取查询中的参数占位符
        placeholders = re.findall(r":(\w+)", query)

        if not placeholders:
            # 没有参数占位符，不需要检查
            return SecurityCheckResult(is_safe=True)

        # 检查参数是否匹配
        if params is None:
            return SecurityCheckResult(is_safe=False, reason="查询包含参数占位符但未提供参数")

        # 检查所有占位符都有对应的参数
        missing_params = set(placeholders) - set(params.keys())
        if missing_params:
            return SecurityCheckResult(
                is_safe=False, reason=f"缺少参数: {', '.join(missing_params)}"
            )

        return SecurityCheckResult(is_safe=True)
