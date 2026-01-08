# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

MCP Database SDK 是一个为大语言模型（LLM）提供统一数据库操作能力的 Python SDK。通过 MCP (Model Context Protocol) 协议将多种数据库的 CRUD 操作封装为标准接口，使 AI 能够安全、高效地访问和操作数据。

**支持的数据库**：PostgreSQL, MySQL, SQLite, MongoDB, Redis, OpenSearch, Supabase

## 常用命令

### 安装与配置

```bash
# 安装依赖（包括开发依赖）
pip install -e ".[dev]"

# 启动测试数据库（PostgreSQL, MySQL, MongoDB, Redis, OpenSearch）
docker-compose -f docker-compose.test.yml up -d
```

### 测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=mcp_database --cov-report=html

# 运行单个测试文件
pytest tests/test_adapter.py

# 运行单个测试函数
pytest tests/test_adapter.py::test_postgresql_connect

# 运行异步测试
pytest -xvs tests/test_adapters/test_sql_base.py::test_postgresql_crud

# 运行性能基准测试
pytest tests/benchmark/test_performance.py
```

### 代码质量检查

```bash
# 代码格式化（ruff）
ruff format .

# 代码检查（linter）
ruff check .

# 类型检查（mypy）
mypy src/mcp_database

# 运行所有检查
ruff check . && mypy src/mcp_database
```

### 配置环境变量

```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/db
export ENABLE_INSERT=true    # 允许插入操作（默认 false）
export ENABLE_UPDATE=true    # 允许更新操作（默认 false）
export ENABLE_DELETE=true    # 允许删除操作（默认 false）
export DANGEROUS_AGREE=false # 允许危险操作（执行命令等，默认 false）
```

## 架构设计

### 分层架构

项目采用清晰的分层架构，从上到下依次为：

1. **MCP Layer**（协议层）- TODO 待实现
   - 负责 MCP 协议转换
   - 工具注册和参数验证

2. **SDK Core Layer**（核心层）- 主体功能已完成
   - `core/adapter.py`: DatabaseAdapter 抽象基类，定义所有适配器必须实现的接口
   - `core/models.py`: Pydantic 数据模型（InsertResult, QueryResult, Capability 等）
   - `core/exceptions.py`: 统一异常体系（DatabaseError, ConnectionError, QueryError 等）
   - `core/filters.py`: 过滤器 DSL 转换器（SQLFilterTranslator, MongoFilterTranslator, RedisFilterTranslator）
   - `core/security.py`: SQLSecurityChecker 安全检查器
   - `core/permissions.py`: 权限管理器（PermissionManager）和权限检查装饰器

3. **Adapter Layer**（适配器层）
   - `adapters/factory.py`: AdapterFactory 工厂类，根据 URL 自动创建适配器
   - `adapters/sql/base.py`: SQLAdapter（SQLAlchemy 实现，支持 PostgreSQL/MySQL/SQLite）
   - `adapters/nosql/mongodb.py`: MongoDBAdapter（Motor 异步驱动）
   - `adapters/nosql/redis.py`: RedisAdapter（redis-py 异步）
   - `adapters/nosql/opensearch.py`: OpenSearchAdapter

4. **Config Layer**（配置层）
   - `config/settings.py`: 全局配置管理，从环境变量读取权限配置

5. **Utils Layer**（工具层）
   - `utils/audit_logger.py`: 审计日志记录

### 核心接口设计

`DatabaseAdapter` 抽象基类定义了统一的 CRUD 接口：

```python
class DatabaseAdapter(ABC):
    async def connect(self) -> None                    # 连接数据库
    async def disconnect(self) -> None                 # 断开连接
    async def insert(self, table: str, data: Dict) -> InsertResult
    async def delete(self, table: str, filters: Dict) -> DeleteResult
    async def update(self, table: str, data: Dict, filters: Dict) -> UpdateResult
    async def query(self, table: str, filters: Optional[Dict], limit: Optional[int]) -> QueryResult
    async def execute(self, query: str, params: Optional[Dict]) -> ExecuteResult
    async def advanced_query(self, operation: str, params: Dict) -> AdvancedResult
    def get_capabilities(self) -> Capability           # 获取数据库能力
```

### 过滤器 DSL

项目使用统一的过滤器 DSL，支持跨数据库的一致查询语法。所有操作符通过 `__` 分隔字段名和操作符类型：

```python
# 等值
{"age": 25}

# 比较操作符
{"age__gt": 18}     # 大于
{"age__lt": 60}     # 小于
{"age__gte": 18}    # 大于等于
{"age__lte": 60}    # 小于等于

# 字符串操作符
{"name__contains": "John"}     # 包含
{"name__startswith": "A"}      # 开头匹配
{"name__endswith": "e"}        # 结尾匹配

# 列表操作符
{"status__in": ["active", "pending"]}   # IN
{"status__not_in": ["deleted"]}          # NOT IN
```

每类适配器都有自己的 `FilterTranslator` 将 DSL 转换为目标数据库语法：
- SQLFilterTranslator: 转换为 SQL WHERE 子句
- MongoFilterTranslator: 转换为 MongoDB `$` 操作符（如 `$gt`, `$regex`, `$in`）
- RedisFilterTranslator: 返回 Python 过滤函数（内存过滤）

### 权限控制机制

权限通过环境变量控制，实现了细粒度的操作权限管理：

```python
from mcp_database.core.permissions import PermissionManager, require_permission

# 方式 1: 使用装饰器
@require_permission("insert")           # 插入需要权限
@require_permission("delete", dangerous=True)  # 删除是危险操作
async def some_function():
    pass

# 方式 2: 手动检查
pm = PermissionManager()
pm.check_permission("insert")
pm.check_permission("execute", dangerous=True)  # 检查危险操作权限
```

权限检查在 `core/permissions.py` 中实现，装饰器会自动识别同步/异步函数。

### 安全机制

多层安全防护：

1. **SQLSecurityChecker** (`core/security.py`)
   - 检测禁止的关键字（DROP, TRUNCATE, ALTER, GRANT, CREATE 等）
   - 检测 SQL 注入模式（`--`, `UNION SELECT`, `OR 1=1` 等）
   - 验证 DELETE/UPDATE 操作必须带 WHERE 条件
   - 检查参数化查询（必须使用 `:param` 形式）

2. **权限控制**
   - INSERT/UPDATE/DELETE 操作默认禁用，需要设置环境变量启用
   - EXECUTE 操作（原生命令执行）需要 `DANGEROUS_AGREE=true`

3. **异常转换**
   - `ExceptionTranslator` 将各数据库原生异常转换为标准异常类型
   - 所有异常信息包含数据库类型标识

### 数据库适配器工厂

`AdapterFactory` 根据 DATABASE_URL 自动识别数据库类型并创建适配器：

```python
from mcp_database.core.models import DatabaseConfig
from mcp_database.adapters.factory import AdapterFactory

config = DatabaseConfig(url="postgresql://user:pass@localhost:5432/db")
adapter = AdapterFactory.create_adapter(config)
await adapter.connect()
```

支持的 URL 格式：
- PostgreSQL: `postgresql://user:pass@localhost:5432/db`
- MySQL: `mysql://user:pass@localhost:3306/db`
- SQLite: `sqlite:///path/to/db.sqlite`
- MongoDB: `mongodb://localhost:27017/db`
- Redis: `redis://localhost:6379/0`
- OpenSearch: `http://localhost:9200`
- Supabase: `postgresql+supabase://user:pass@host/db`

### 异步设计

整个 SDK 采用异步设计，使用 Python 的 `asyncio`：

- 所有数据库操作都是 `async` 方法
- 使用 SQLAlchemy 2.0 的异步 API (`create_async_engine`, `AsyncSession`)
- MongoDB 使用 Motor 异步驱动
- Redis 使用 `redis[asyncio]` 异步客户端

测试需要使用 `pytest-asyncio`，测试函数使用 `@pytest.mark.asyncio` 装饰器。

## 测试说明

### 测试文件组织

```
tests/
├── test_adapter.py        # DatabaseAdapter 抽象基类测试
├── test_models.py         # 数据模型测试
├── test_exceptions.py     # 异常处理测试
├── test_filters.py        # 过滤器 DSL 测试
├── test_security.py       # 安全检查器测试
├── test_permissions.py    # 权限控制测试
├── test_factory.py        # 适配器工厂测试
├── test_config.py         # 配置管理测试
├── test_audit_log.py      # 审计日志测试
├── test_adapters/         # 各适配器测试
│   ├── test_mongodb.py
│   ├── test_redis.py
│   ├── test_opensearch.py
│   └── test_sql_base.py   # SQL 适配器测试
├── integration/           # 集成测试
│   ├── test_error_handling.py
│   └── test_concurrent.py
└── benchmark/             # 性能测试
    └── test_performance.py
```

### 运行特定数据库测试

由于需要实际的数据库实例，大部分集成测试需要先启动测试数据库：

```bash
# 启动测试数据库
docker-compose -f docker-compose.test.yml up -d

# 运行特定数据库测试
pytest tests/test_adapters/test_sql_base.py -k postgresql
pytest tests/test_adapters/test_mongodb.py
pytest tests/test_adapters/test_redis.py
```

### 性能基准测试

性能测试使用 `pytest-benchmark`：

```bash
pytest tests/benchmark/test_performance.py
```

性能目标：
- QPS: 200 请求/秒（单实例）
- P95 延迟:< 100ms（本地数据库）

## 代码规范

### 类型注解

项目强制使用类型注解，mypy 配置要求：

```python
from typing import Dict, Any, Optional

async def query(
    self,
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None
) -> QueryResult:
    pass
```

### 异常处理

所有数据库操作都应该捕获并转换异常：

```python
from mcp_database.core.exceptions import ExceptionTranslator

try:
    # 数据库操作
    result = await session.execute(stmt)
except Exception as e:
    # 转换为标准异常
    translated = ExceptionTranslator.translate(e, self._database_type)
    raise translated
```

### 数据模型使用

使用 Pydantic 模型确保类型安全：

```python
from mcp_database.core.models import InsertResult, QueryResult

# 返回时使用 Pydantic 模型
return InsertResult(inserted_count=1, inserted_ids=[1])

# 验证输入
from pydantic import validate_call

@validate_call
async def insert(self, table: str, data: Dict[str, Any]) -> InsertResult:
    # Pydantic 会自动验证参数类型
```

## 常见任务

### 添加新的数据库支持

1. 在 `adapters/nosql/` 或 `adapters/sql/` 下创建新的适配器文件
2. 继承 `DatabaseAdapter` 抽象基类
3. 实现所有抽象方法（connect, insert, delete, update, query, execute, advanced_query, get_capabilities）
4. 在 `adapters/factory.py` 中注册新的 URL scheme
5. 在 `core/filters.py` 中添加对应的 FilterTranslator（如果需要不同的过滤逻辑）
6. 在 `tests/test_adapters/` 中添加测试

### 添加新的过滤器操作符

1. 在 SQLFilterTranslator._translate_operator 中添加映射
2. 在 MongoFilterTranslator._translate_operator 中添加映射
3. 在 RedisFilterTranslator._check_operator 中添加判断逻辑
4. 在测试文件中添加测试用例

### 修改权限控制逻辑

权限配置在 `config/settings.py` 中，权限检查在 `core/permissions.py` 中。

如需添加新的权限类型：
1. 在 `Settings` 类中添加新的配置属性
2. 在 `PermissionManager.check_permission` 中添加检查逻辑
3. 添加对应的装饰器（如 `@require_permission("new_operation")`）

### 调试数据库连接问题

连接问题时，检查以下几点：

1. DATABASE_URL 格式是否正确
2. 测试数据库是否已启动（`docker-compose -f docker-compose.test.yml ps`）
3. 网络连接是否正常（`telnet localhost 5432`）
4. 异常信息中是否包含有用的错误详情

启用 SQLAlchemy echo 可以查看实际执行的 SQL：

```python
# 在 SQLAdapter.connect() 中临时启用
self._engine = create_async_engine(
    self.config.url,
    echo=True  # 打印 SQL
)
```

## 重要注意事项

### 安全性

- **永远不要**执行用户直接输入拼接的 SQL
- **必须使用**参数化查询（`:param` 形式）
- **删除和更新操作必须**有 WHERE 条件（SQLSecurityChecker 会检查）
- **execute 接口应该**仅在 DANGEROUS_AGREE=true 时暴露给 AI

### Redis 适配器的特殊之处

Redis 本身不支持表结构，适配器使用 "表键前缀" 模式：
- 表名作为键前缀：`users:user1`, `users:user2`
- 查询使用 SCAN（非阻塞）+ MGET（批量获取）
- 过滤在内存中进行（性能较差，适合小数据集）
- 对于大数据集，考虑使用 Redis Modules（RediSearch）

### 异常处理的最佳实践

```python
# 错误示例：捕获所有异常
try:
    await adapter.insert(table, data)
except BaseException:
    pass  # 太宽泛

# 正确示例：捕获特定的数据库异常
from mcp_database.core.exceptions import ConnectionError, QueryError

try:
    await adapter.insert(table, data)
except ConnectionError as e:
    # 连接失败，可能需要重试
    logger.error(f"Connection failed: {e}")
except QueryError as e:
    # 查询错误，可能是数据问题
    logger.error(f"Query failed: {e}")
```

### 性能优化建议

1. **批量插入**：使用列表而非循环调用 insert
   ```python
   # 推荐
   await adapter.insert(table, [data1, data2, data3])

   # 不推荐
   for data in [data1, data2, data3]:
       await adapter.insert(table, data)
   ```

2. **查询分页**：始终使用 limit 避免 OOM
   ```python
   await adapter.query(table, filters=filters, limit=100)
   ```

3. **连接池配置**：根据负载调整连接池大小
   ```python
   config = DatabaseConfig(
       url="postgresql://user:pass@localhost/db",
       pool_size=10,        # 核心连接数
       max_overflow=20      # 最大溢出连接
   )
   ```

4. **索引优化**：在数据库层面为常用查询字段创建索引（不在 SDK 层面）

## 相关文档

- [产品需求文档](docs/prd.md) - 功能需求和验收标准
- [技术设计文档](docs/tdd.md) - 架构设计和实现细节
- [测试计划](docs/test.md) - 测试策略和覆盖率要求
- [用户验收](docs/uat.md) - UAT 测试场景
