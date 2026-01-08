"""审计日志测试"""

import os

import pytest

AUDIT_LOG_PATH = "logs/audit.log"


class TestAuditLogger:
    """测试审计日志记录器"""

    def test_log_operation_success(self):
        """测试记录成功操作"""
        from mcp_database.utils.audit_logger import AuditLogger

        logger = AuditLogger()

        # 记录操作
        logger.log_operation(
            operation="insert",
            table="users",
            params={"data": {"name": "Alice"}},
            result={"success": True},
        )

        # 验证日志文件存在
        assert os.path.exists(AUDIT_LOG_PATH)

    def test_log_operation_error(self):
        """测试记录错误操作"""
        from mcp_database.utils.audit_logger import AuditLogger

        logger = AuditLogger()

        # 记录错误
        logger.log_operation(
            operation="delete",
            table="users",
            params={"filters": {"id": 1}},
            error="Permission denied",
        )

        # 验证日志文件存在
        assert os.path.exists(AUDIT_LOG_PATH)

    def test_log_execute(self):
        """测试记录 execute 操作"""
        from mcp_database.utils.audit_logger import AuditLogger

        logger = AuditLogger()

        # 记录 execute
        logger.log_execute(query="SELECT * FROM users", params={"limit": 10}, result={"rows": 10})

        # 验证日志文件存在
        assert os.path.exists(AUDIT_LOG_PATH)

    @pytest.mark.asyncio
    async def test_audit_log_decorator(self):
        """测试审计日志装饰器"""
        from mcp_database.utils.audit_logger import AuditLogger, audit_log

        # 创建测试类
        class TestAdapter:
            def __init__(self):
                self._audit_logger = AuditLogger()

            @audit_log("insert")
            async def insert(self, table, data):
                return {"success": True}

        adapter = TestAdapter()
        result = await adapter.insert("users", {"name": "Alice"})

        # 验证结果
        assert result["success"] is True
        assert os.path.exists(AUDIT_LOG_PATH)

    @pytest.mark.asyncio
    async def test_audit_log_decorator_with_error(self):
        """测试审计日志装饰器（带错误）"""
        from mcp_database.utils.audit_logger import AuditLogger, audit_log

        # 创建测试类
        class TestAdapter:
            def __init__(self):
                self._audit_logger = AuditLogger()

            @audit_log("delete")
            async def delete(self, table, filters):
                raise Exception("Delete failed")

        adapter = TestAdapter()

        # 验证抛出异常
        with pytest.raises(Exception):
            await adapter.delete("users", {"id": 1})

        # 验证日志文件存在
        assert os.path.exists(AUDIT_LOG_PATH)

    @pytest.mark.asyncio
    async def test_audit_execute_decorator(self):
        """测试 execute 审计装饰器"""
        from mcp_database.utils.audit_logger import AuditLogger, audit_execute

        # 创建测试类
        class TestAdapter:
            def __init__(self):
                self._audit_logger = AuditLogger()

            @audit_execute
            async def execute(self, query, params=None):
                return {"success": True, "rows": 5}

        adapter = TestAdapter()
        result = await adapter.execute("SELECT * FROM users", {"limit": 10})

        # 验证结果
        assert result["success"] is True
        assert os.path.exists(AUDIT_LOG_PATH)

    def test_log_entry_format(self):
        """测试日志条目格式"""
        from mcp_database.utils.audit_logger import AuditLogger

        logger = AuditLogger()

        # 记录操作
        logger.log_operation(
            operation="query", table="users", params={"filters": {"age": 25}}, result={"count": 10}
        )

        # 读取日志文件
        with open(AUDIT_LOG_PATH) as f:
            log_content = f.read()

        # 验证日志格式
        assert "query" in log_content
        assert "users" in log_content

    @classmethod
    def teardown_class(cls):
        """清理测试文件"""
        if os.path.exists(AUDIT_LOG_PATH):
            os.remove(AUDIT_LOG_PATH)
        if os.path.exists("logs"):
            import shutil

            shutil.rmtree("logs", ignore_errors=True)
