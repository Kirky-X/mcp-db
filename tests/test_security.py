"""测试 SQL 安全检查器"""



class TestSQLSecurityChecker:
    """测试 SQL 安全检查器"""

    def test_safe_select_query(self):
        """测试安全的 SELECT 查询"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "SELECT * FROM users WHERE id = :id"

        result = checker.check(query, params={"id": 1})
        assert result.is_safe is True

    def test_safe_insert_query(self):
        """测试安全的 INSERT 查询"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "INSERT INTO users (name, age) VALUES (:name, :age)"

        result = checker.check(query, params={"name": "Alice", "age": 25})
        assert result.is_safe is True

    def test_dangerous_drop_command(self):
        """测试危险的 DROP 命令"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "DROP TABLE users"

        result = checker.check(query)
        assert result.is_safe is False
        assert "DROP" in result.reason

    def test_dangerous_truncate_command(self):
        """测试危险的 TRUNCATE 命令"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "TRUNCATE TABLE users"

        result = checker.check(query)
        assert result.is_safe is False

    def test_dangerous_delete_without_filters(self):
        """测试没有过滤条件的危险 DELETE"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "DELETE FROM users"

        result = checker.check(query)
        assert result.is_safe is False

    def test_safe_delete_with_filters(self):
        """测试带过滤条件的安全 DELETE"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "DELETE FROM users WHERE id = :id"

        result = checker.check(query, params={"id": 1})
        assert result.is_safe is True

    def test_sql_injection_attempt(self):
        """测试 SQL 注入攻击尝试"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "SELECT * FROM users WHERE name = 'admin'; DROP TABLE users; --"

        result = checker.check(query)
        assert result.is_safe is False

    def test_comment_based_injection(self):
        """测试基于注释的注入"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "SELECT * FROM users WHERE id = 1 -- AND admin = 1"

        result = checker.check(query)
        assert result.is_safe is False

    def test_union_based_injection(self):
        """测试基于 UNION 的注入"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "SELECT * FROM users WHERE id = 1 UNION SELECT * FROM passwords"

        result = checker.check(query)
        assert result.is_safe is False

    def test_parameterized_query_validation(self):
        """测试参数化查询验证"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "SELECT * FROM users WHERE id = :id AND name = :name"

        result = checker.check(query, params={"id": 1, "name": "Alice"})
        assert result.is_safe is True

    def test_missing_parameters(self):
        """测试缺少参数"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "SELECT * FROM users WHERE id = :id AND name = :name"

        result = checker.check(query, params={"id": 1})
        assert result.is_safe is False

    def test_case_insensitive_keywords(self):
        """测试大小写不敏感的关键字检测"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "drop table users"

        result = checker.check(query)
        assert result.is_safe is False

    def test_safe_update_query(self):
        """测试安全的 UPDATE 查询"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "UPDATE users SET age = :age WHERE id = :id"

        result = checker.check(query, params={"age": 26, "id": 1})
        assert result.is_safe is True

    def test_dangerous_update_without_filters(self):
        """测试没有过滤条件的危险 UPDATE"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "UPDATE users SET age = 25"

        result = checker.check(query)
        assert result.is_safe is False

    def test_dangerous_alter_command(self):
        """测试危险的 ALTER 命令"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "ALTER TABLE users ADD COLUMN email TEXT"

        result = checker.check(query)
        assert result.is_safe is False

    def test_dangerous_grant_command(self):
        """测试危险的 GRANT 命令"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "GRANT ALL PRIVILEGES ON users TO admin"

        result = checker.check(query)
        assert result.is_safe is False

    def test_dangerous_create_command(self):
        """测试危险的 CREATE 命令"""
        from mcp_database.core.security import SQLSecurityChecker

        checker = SQLSecurityChecker()
        query = "CREATE TABLE new_table (id INT)"

        result = checker.check(query)
        assert result.is_safe is False
