"""测试过滤器 DSL 解析器"""


class TestRegexSecurityValidator:
    """测试正则表达式安全验证器"""

    def test_valid_simple_pattern(self):
        """测试简单有效模式通过验证"""
        from mcp_database.core.filters import RegexSecurityValidator

        pattern = "test"
        result = RegexSecurityValidator.validate(pattern)
        assert result == "test"

    def test_valid_complex_pattern(self):
        """测试复杂有效模式通过验证"""
        from mcp_database.core.filters import RegexSecurityValidator

        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        result = RegexSecurityValidator.validate(pattern)
        assert result == pattern

    def test_pattern_too_long(self):
        """测试超长模式抛出异常"""
        from mcp_database.core.exceptions import QueryError
        from mcp_database.core.filters import RegexSecurityValidator

        pattern = "a" * 501  # 超过 MAX_REGEX_LENGTH (500)
        try:
            RegexSecurityValidator.validate(pattern)
            assert False, "Should have raised QueryError"
        except QueryError as e:
            assert "exceeds maximum length" in str(e)

    def test_nested_quantifiers_double_star(self):
        """测试双星号量词检测"""
        from mcp_database.core.exceptions import QueryError
        from mcp_database.core.filters import RegexSecurityValidator

        pattern = r"a**"
        try:
            RegexSecurityValidator.validate(pattern)
            assert False, "Should have raised QueryError"
        except QueryError as e:
            assert "Nested quantifiers" in str(e)

    def test_nested_quantifiers_adjacent(self):
        """测试相邻量词检测"""
        from mcp_database.core.exceptions import QueryError
        from mcp_database.core.filters import RegexSecurityValidator

        pattern = r"a++"
        try:
            RegexSecurityValidator.validate(pattern)
            assert False, "Should have raised QueryError"
        except QueryError as e:
            assert "Nested quantifiers" in str(e)

    def test_nested_quantifiers_curly_braces(self):
        """测试数量词嵌套检测"""
        from mcp_database.core.exceptions import QueryError
        from mcp_database.core.filters import RegexSecurityValidator

        pattern = r"a{2}{3}"
        try:
            RegexSecurityValidator.validate(pattern)
            assert False, "Should have raised QueryError"
        except QueryError as e:
            assert "Nested quantifiers" in str(e)

    def test_too_many_character_classes(self):
        """测试过多字符类检测"""
        from mcp_database.core.exceptions import QueryError
        from mcp_database.core.filters import RegexSecurityValidator

        # 创建超过 MAX_CHAR_CLASSES (10) 的字符类
        pattern = "[a][b][c][d][e][f][g][h][i][j][k]"
        try:
            RegexSecurityValidator.validate(pattern)
            assert False, "Should have raised QueryError"
        except QueryError as e:
            assert "character classes" in str(e)

    def test_too_many_alternations(self):
        """测试过多交替检测"""
        from mcp_database.core.exceptions import QueryError
        from mcp_database.core.filters import RegexSecurityValidator

        # 创建超过 MAX_ALTERNATIONS (20) 的交替
        # 22 个元素会产生 21 个分隔符
        pattern = "|".join(["a"] * 22)
        try:
            RegexSecurityValidator.validate(pattern)
            assert False, "Should have raised QueryError"
        except QueryError as e:
            assert "alternations" in str(e)

    def test_count_nested_quantifiers(self):
        """测试嵌套量词计数"""
        from mcp_database.core.filters import RegexSecurityValidator

        # 没有嵌套量词
        assert RegexSecurityValidator._count_nested_quantifiers("test") == 0
        assert RegexSecurityValidator._count_nested_quantifiers(r"[a-z]+") == 0

        # 单个嵌套量词
        assert RegexSecurityValidator._count_nested_quantifiers(r"a**") == 1
        assert RegexSecurityValidator._count_nested_quantifiers(r"a++") == 1

        # 多个嵌套量词
        assert RegexSecurityValidator._count_nested_quantifiers(r"a**b++") == 2


class TestFilterParser:
    """测试 FilterParser 基类"""

    def test_parse_simple_equality(self):
        """测试简单等值过滤"""
        from mcp_database.core.filters import FilterParser

        parser = FilterParser()
        filters = {"age": 25}
        parsed = parser.parse(filters)
        assert parsed is not None

    def test_parse_empty_filters(self):
        """测试空过滤器"""
        from mcp_database.core.filters import FilterParser

        parser = FilterParser()
        parsed = parser.parse({})
        assert parsed is None


class TestSQLFilterTranslator:
    """测试 SQL 过滤器转换器"""

    def test_simple_equality(self):
        """测试简单等值条件"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age": 25}
        where_clause, params = translator.translate(filters)
        assert "age" in where_clause
        assert params["age_eq"] == 25

    def test_gt_operator(self):
        """测试大于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__gt": 18}
        where_clause, params = translator.translate(filters)
        assert ">" in where_clause
        assert params["age_gt"] == 18

    def test_lt_operator(self):
        """测试小于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__lt": 60}
        where_clause, params = translator.translate(filters)
        assert "<" in where_clause
        assert params["age_lt"] == 60

    def test_gte_operator(self):
        """测试大于等于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__gte": 18}
        where_clause, params = translator.translate(filters)
        assert ">=" in where_clause
        assert params["age_gte"] == 18

    def test_lte_operator(self):
        """测试小于等于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__lte": 60}
        where_clause, params = translator.translate(filters)
        assert "<=" in where_clause
        assert params["age_lte"] == 60

    def test_contains_operator(self):
        """测试包含操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"name__contains": "John"}
        where_clause, params = translator.translate(filters)
        assert "LIKE" in where_clause
        assert params["name_contains"] == "%John%"

    def test_startswith_operator(self):
        """测试开始于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"name__startswith": "A"}
        where_clause, params = translator.translate(filters)
        assert "LIKE" in where_clause
        assert params["name_startswith"] == "A%"

    def test_endswith_operator(self):
        """测试结束于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"name__endswith": "son"}
        where_clause, params = translator.translate(filters)
        assert "LIKE" in where_clause
        assert params["name_endswith"] == "%son"

    def test_in_operator(self):
        """测试 IN 操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"status__in": ["active", "pending"]}
        where_clause, params = translator.translate(filters)
        assert "IN" in where_clause

    def test_not_in_operator(self):
        """测试 NOT IN 操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"status__not_in": ["deleted", "archived"]}
        where_clause, params = translator.translate(filters)
        assert "NOT IN" in where_clause

    def test_multiple_conditions(self):
        """测试多个条件"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__gte": 18, "status": "active"}
        where_clause, params = translator.translate(filters)
        assert "age" in where_clause
        assert "status" in where_clause
        assert "AND" in where_clause

    def test_string_value_quoting(self):
        """测试字符串值参数化查询"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"name": "John Doe"}
        where_clause, params = translator.translate(filters)
        assert "name" in where_clause
        assert "name_eq" in params
        assert params["name_eq"] == "John Doe"


class TestMongoFilterTranslator:
    """测试 MongoDB 过滤器转换器"""

    def test_simple_equality(self):
        """测试简单等值条件"""
        from mcp_database.core.filters import MongoFilterTranslator

        translator = MongoFilterTranslator()
        filters = {"age": 25}
        condition = translator.translate(filters)
        assert condition["age"] == 25

    def test_gt_operator(self):
        """测试大于操作符"""
        from mcp_database.core.filters import MongoFilterTranslator

        translator = MongoFilterTranslator()
        filters = {"age__gt": 18}
        condition = translator.translate(filters)
        assert "$gt" in condition.get("age", {})

    def test_lt_operator(self):
        """测试小于操作符"""
        from mcp_database.core.filters import MongoFilterTranslator

        translator = MongoFilterTranslator()
        filters = {"age__lt": 60}
        condition = translator.translate(filters)
        assert "$lt" in condition.get("age", {})

    def test_gte_operator(self):
        """测试大于等于操作符"""
        from mcp_database.core.filters import MongoFilterTranslator

        translator = MongoFilterTranslator()
        filters = {"age__gte": 18}
        condition = translator.translate(filters)
        assert "$gte" in condition.get("age", {})

    def test_lte_operator(self):
        """测试小于等于操作符"""
        from mcp_database.core.filters import MongoFilterTranslator

        translator = MongoFilterTranslator()
        filters = {"age__lte": 60}
        condition = translator.translate(filters)
        assert "$lte" in condition.get("age", {})

    def test_contains_operator(self):
        """测试包含操作符"""
        from mcp_database.core.filters import MongoFilterTranslator

        translator = MongoFilterTranslator()
        filters = {"name__contains": "John"}
        condition = translator.translate(filters)
        assert "$regex" in condition.get("name", {})

    def test_in_operator(self):
        """测试 IN 操作符"""
        from mcp_database.core.filters import MongoFilterTranslator

        translator = MongoFilterTranslator()
        filters = {"status__in": ["active", "pending"]}
        condition = translator.translate(filters)
        assert "$in" in condition.get("status", {})

    def test_not_in_operator(self):
        """测试 NOT IN 操作符"""
        from mcp_database.core.filters import MongoFilterTranslator

        translator = MongoFilterTranslator()
        filters = {"status__not_in": ["deleted", "archived"]}
        condition = translator.translate(filters)
        assert "$nin" in condition.get("status", {})

    def test_multiple_conditions(self):
        """测试多个条件"""
        from mcp_database.core.filters import MongoFilterTranslator

        translator = MongoFilterTranslator()
        filters = {"age__gte": 18, "status": "active"}
        condition = translator.translate(filters)
        assert "age" in condition
        assert "status" in condition


class TestRedisFilterTranslator:
    """测试 Redis 过滤器转换器"""

    def test_simple_equality(self):
        """测试简单等值条件"""
        from mcp_database.core.filters import RedisFilterTranslator

        translator = RedisFilterTranslator()
        filters = {"age": 25}
        filter_func = translator.translate(filters)
        assert filter_func is not None

    def test_filter_function(self):
        """测试过滤函数"""
        from mcp_database.core.filters import RedisFilterTranslator

        translator = RedisFilterTranslator()
        filters = {"age": 25}
        filter_func = translator.translate(filters)

        # 测试过滤函数
        test_data = {"age": 25, "name": "John"}
        result = filter_func(test_data)
        assert result is True

        test_data2 = {"age": 30, "name": "Jane"}
        result2 = filter_func(test_data2)
        assert result2 is False

    def test_gt_operator(self):
        """测试大于操作符"""
        from mcp_database.core.filters import RedisFilterTranslator

        translator = RedisFilterTranslator()
        filters = {"age__gt": 18}
        filter_func = translator.translate(filters)

        test_data = {"age": 25}
        result = filter_func(test_data)
        assert result is True

        test_data2 = {"age": 15}
        result2 = filter_func(test_data2)
        assert result2 is False

    def test_contains_operator(self):
        """测试包含操作符"""
        from mcp_database.core.filters import RedisFilterTranslator

        translator = RedisFilterTranslator()
        filters = {"name__contains": "John"}
        filter_func = translator.translate(filters)

        test_data = {"name": "John Doe"}
        result = filter_func(test_data)
        assert result is True

        test_data2 = {"name": "Jane Smith"}
        result2 = filter_func(test_data2)
        assert result2 is False

    def test_multiple_conditions(self):
        """测试多个条件（AND 逻辑）"""
        from mcp_database.core.filters import RedisFilterTranslator

        translator = RedisFilterTranslator()
        filters = {"age__gte": 18, "status": "active"}
        filter_func = translator.translate(filters)

        test_data = {"age": 25, "status": "active"}
        result = filter_func(test_data)
        assert result is True

        test_data2 = {"age": 15, "status": "active"}
        result2 = filter_func(test_data2)
        assert result2 is False

        test_data3 = {"age": 25, "status": "inactive"}
        result3 = filter_func(test_data3)
        assert result3 is False
