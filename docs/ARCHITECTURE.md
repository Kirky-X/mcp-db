# 🏗️ Architecture

_系统架构设计文档_

MCP Database SDK 是一个专为 MCP（Model Context Protocol）协议设计的数据库操作工具集。

## 🎯 设计目标

| Goal | Description |
|:-----|:------------|
| **工具化接口** | 所有操作通过 MCP Tool 暴露，大模型可直接调用 |
| **统一工具** | 只有 6 个工具（insert/query/update/delete/advanced/execute） |
| **数据库透明** | 通过 DATABASE_URL 自动识别数据库类型 |
| **安全优先** | 严格的安全检查防止误操作 |

---

## 🏗️ 系统架构

```
LLM → MCP Server → Adapter Factory → Database
           ↓
      6 Tools (insert/query/update/delete/advanced/execute)
           ↓
    SQL | NoSQL | HTTP Adapters
```

---

## 🔧 核心组件

### MCP Server

使用 FastMCP 框架，提供 6 个统一工具：

| Tool | Parameters | Returns |
|:-----|:-----------|:--------|
| `insert` | table, data | success, inserted_count, inserted_ids |
| `query` | table, filters, limit | success, data, count, has_more |
| `update` | table, data, filters | success, updated_count |
| `delete` | table, filters | success, deleted_count |
| `advanced` | table, operation, params | success, operation, data |
| `execute` | query, params | success, rows_affected, data |

### Adapter Factory

根据 DATABASE_URL 自动选择适配器：

| URL Pattern | Adapter |
|:------------|:--------|
| `postgresql://...` | SQLAdapter |
| `mysql://...` | SQLAdapter |
| `mongodb://...` | MongoDBAdapter |
| `redis://...` | RedisAdapter |
| `http://...:9200` | OpenSearchAdapter |
| `https://project.supabase.co` | SupabaseAdapter |

### Database Adapters

所有适配器继承自 `DatabaseAdapter` 抽象基类：

```python
class DatabaseAdapter(ABC):
    @property @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def insert(self, table: str, data: dict) -> InsertResult: ...
    async def query(self, table: str, filters: dict, limit: int) -> QueryResult: ...
    async def update(self, table: str, data: dict, filters: dict) -> UpdateResult: ...
    async def delete(self, table: str, filters: dict) -> DeleteResult: ...
    async def execute(self, query: str, params: dict) -> ExecuteResult: ...
    async def advanced_query(self, operation: str, params: dict) -> AdvancedResult: ...
```

---

## 📊 数据流

```
1. LLM 调用工具
     ↓
2. MCP Server 解析参数
     ↓
3. 调用 adapter.query(...)
     ↓
4. 适配器执行：翻译过滤器 → 安全检查 → 执行查询
     ↓
5. 返回结果: {"success": true, "data": [...], "count": 100}
```

---

## 🗄️ 数据库能力矩阵

| Database | INSERT | QUERY | UPDATE | DELETE | AGGREGATE | TRANSACTION |
|:---------|:------:|:-----:|:------:|:------:|:---------:|:-----------:|
| PostgreSQL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| MySQL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SQLite | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| MongoDB | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Redis | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| OpenSearch | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Supabase | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🛡️ 安全架构

#### SQL 注入防护
- 所有查询使用参数化查询
- 自动转义用户输入

#### 危险语句检测

| Statement | Action |
|:----------|:-------|
| DROP | 拦截 ❌ |
| TRUNCATE | 拦截 ❌ |
| ALTER | 拦截 ❌ |
| GRANT | 拦截 ❌ |

#### 权限控制

| Operation | Default | Env Variable |
|:----------|:-------:|:-------------|
| INSERT | ✅ | - |
| SELECT | ✅ | - |
| UPDATE | ✅ | - |
| DELETE | ❌ | `ENABLE_DELETE=true` |
| EXECUTE | ❌ | `DANGEROUS_AGREE=true` |

> ⚠️ UPDATE 和 DELETE 操作必须包含 WHERE 条件

---

## 🛠️ 技术栈

| Category | Technology | Purpose |
|:---------|:-----------|:--------|
| Language | Python 3.10+ | Core |
| MCP | mcp 0.9+ | Protocol |
| Validation | Pydantic 2.5+ | Models |
| ORM | SQLAlchemy 2.0+ | SQL |
| PostgreSQL | asyncpg | Async driver |
| MySQL | aiomysql | Async driver |
| SQLite | aiosqlite | Async driver |
| MongoDB | Motor 3.3+ | Async driver |
| Redis | redis 5.0+ | Client |
| OpenSearch | opensearch-py 2.4+ | Client |
| HTTP | httpx 0.25+ | Client |

---

**© 2026 Kirky.X**
