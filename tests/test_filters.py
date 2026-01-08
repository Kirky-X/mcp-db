"""测试过滤器 DSL 解析器"""



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
        condition = translator.translate(filters)
        assert "age" in condition
        assert "25" in condition

    def test_gt_operator(self):
        """测试大于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__gt": 18}
        condition = translator.translate(filters)
        assert ">" in condition
        assert "18" in condition

    def test_lt_operator(self):
        """测试小于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__lt": 60}
        condition = translator.translate(filters)
        assert "<" in condition
        assert "60" in condition

    def test_gte_operator(self):
        """测试大于等于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__gte": 18}
        condition = translator.translate(filters)
        assert ">=" in condition

    def test_lte_operator(self):
        """测试小于等于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__lte": 60}
        condition = translator.translate(filters)
        assert "<=" in condition

    def test_contains_operator(self):
        """测试包含操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"name__contains": "John"}
        condition = translator.translate(filters)
        assert "LIKE" in condition
        assert "%John%" in condition

    def test_startswith_operator(self):
        """测试开始于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"name__startswith": "A"}
        condition = translator.translate(filters)
        assert "LIKE" in condition
        assert "A%" in condition

    def test_endswith_operator(self):
        """测试结束于操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"name__endswith": "son"}
        condition = translator.translate(filters)
        assert "LIKE" in condition
        assert "%son" in condition

    def test_in_operator(self):
        """测试 IN 操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"status__in": ["active", "pending"]}
        condition = translator.translate(filters)
        assert "IN" in condition

    def test_not_in_operator(self):
        """测试 NOT IN 操作符"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"status__not_in": ["deleted", "archived"]}
        condition = translator.translate(filters)
        assert "NOT IN" in condition

    def test_multiple_conditions(self):
        """测试多个条件"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"age__gte": 18, "status": "active"}
        condition = translator.translate(filters)
        assert "age" in condition
        assert "status" in condition

    def test_string_value_quoting(self):
        """测试字符串值引号处理"""
        from mcp_database.core.filters import SQLFilterTranslator

        translator = SQLFilterTranslator()
        filters = {"name": "John Doe"}
        condition = translator.translate(filters)
        assert "'" in condition or '"' in condition


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
