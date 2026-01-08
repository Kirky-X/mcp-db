# 架构设计文档

## 一、概述

MCP Database SDK 是一个专为 MCP（Model Context Protocol）协议设计的数据库操作工具集。它为大型语言模型提供标准化的数据库访问能力，使 AI 能够通过统一的工具接口执行 CRUD 操作。

### 设计目标

1. **工具化接口** - 所有操作通过 MCP Tool 暴露，大模型可直接调用
2. **统一工具** - 只有 6 个工具（insert/query/update/delete/advanced/execute）
3. **数据库透明** - 通过 DATABASE_URL 自动识别数据库类型
4. **安全优先** - 严格的安全检查防止误操作

---

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Client (LLM)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ MCP Tool Call
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Database Server                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    6 Tools                           │    │
│  │  insert  query  update  delete  advanced  execute   │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Adapter Factory                           │
│         根据 DATABASE_URL 自动选择适配器                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ SQL Adapters │  │ NoSQL Adapters│ │ HTTP Adapters│
│ PostgreSQL   │  │ MongoDB      │  │ Supabase     │
│ MySQL        │  │ Redis        │  └──────────────┘
│ SQLite       │  │ OpenSearch   │
└──────────────┘  └──────────────┘
```

---

## 三、核心组件

### 3.1 MCP Server

使用 FastMCP 框架，提供 6 个统一工具：

| 工具 | 参数 | 返回 |
|-----|------|------|
| insert | table, data | success, inserted_count, inserted_ids |
| query | table, filters, limit | success, data, count, has_more |
| update | table, data, filters | success, updated_count |
| delete | table, filters | success, deleted_count |
| advanced | table, operation, params | success, operation, data |
| execute | query, params | success, rows_affected, data |

### 3.2 Adapter Factory

根据 DATABASE_URL 自动选择适配器：

```python
# PostgreSQL
postgresql://user:pass@host:port/db -> SQLAdapter

# MySQL
mysql://user:pass@host:port/db -> SQLAdapter

# MongoDB
mongodb://user:pass@host:port/db -> MongoDBAdapter

# Redis
redis://host:port -> RedisAdapter

# OpenSearch
http://host:9200 -> OpenSearchAdapter

# Supabase
https://project.supabase.co -> SupabaseAdapter
```

### 3.3 数据库适配器

所有适配器继承自 DatabaseAdapter 抽象基类，实现统一接口：

```python
class DatabaseAdapter(ABC):
    @property
    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def insert(self, table: str, data: dict) -> InsertResult: ...

    @abstractmethod
    async def query(self, table: str, filters: dict, limit: int) -> QueryResult: ...

    @abstractmethod
    async def update(self, table: str, data: dict, filters: dict) -> UpdateResult: ...

    @abstractmethod
    async def delete(self, table: str, filters: dict) -> DeleteResult: ...

    @abstractmethod
    async def execute(self, query: str, params: dict) -> ExecuteResult: ...

    @abstractmethod
    async def advanced_query(self, operation: str, params: dict) -> AdvancedResult: ...
```

---

## 四、数据流

```
1. LLM 调用工具
   ↓
2. MCP Server 接收请求
   ↓
3. 调用适配器方法
   ↓
4. 适配器执行数据库操作
   ↓
5. 返回结果给 LLM
```

### 查询流程示例

```
工具: query
参数: {"table": "users", "filters": {"status": "active"}, "limit": 10}
     ↓
MCP Server 解析参数
     ↓
调用 adapter.query("users", {"status": "active"}, 10)
     ↓
SQLAdapter 执行：
  1. 翻译过滤器为 WHERE 条件
  2. 安全检查（SQL 注入检测）
  3. 执行查询
  4. 返回结果
     ↓
返回: {"success": true, "data": [...], "count": 100, "has_more": true}
```

---

## 五、数据库能力矩阵

| 数据库 | 插入 | 查询 | 更新 | 删除 | 聚合 | 事务 |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| PostgreSQL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| MySQL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SQLite | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| MongoDB | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Redis | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| OpenSearch | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Supabase | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 六、安全架构

### 6.1 SQL 注入防护

- 所有查询使用参数化查询
- 自动转义用户输入

### 6.2 危险语句检测

自动检测并拦截：

| 禁止语句 | 说明 |
|---------|------|
| DROP | 删除表/数据库 |
| TRUNCATE | 清空表 |
| ALTER | 修改表结构 |
| GRANT | 权限修改 |

### 6.3 权限控制

通过环境变量控制操作权限：

| 操作 | 默认状态 | 环境变量 |
|-----|---------|---------|
| INSERT | 启用 | - |
| SELECT | 启用 | - |
| UPDATE | 启用 | - |
| DELETE | 禁用 | ENABLE_DELETE=true |
| EXECUTE | 禁用 | DANGEROUS_AGREE=true |

### 6.4 安全更新/删除

UPDATE 和 DELETE 操作必须包含 WHERE 条件，否则拒绝执行。

---

## 七、技术栈

| 类别 | 技术 | 版本 | 用途 |
|-----|------|------|------|
| 语言 | Python | 3.10+ | 核心开发 |
| MCP | mcp | 0.9+ | MCP 协议 |
| 数据验证 | Pydantic | 2.5+ | 模型定义 |
| ORM | SQLAlchemy | 2.0+ | SQL 适配 |
| 异步 PostgreSQL | asyncpg | 0.29+ | 连接池 |
| 异步 MySQL | aiomysql | 0.2+ | 连接池 |
| 异步 SQLite | aiosqlite | 0.19+ | 连接池 |
| MongoDB | Motor | 3.3+ | 异步驱动 |
| Redis | redis | 5.0+ | 客户端 |
| OpenSearch | opensearch-py | 2.4+ | 客户端 |
| HTTP | httpx | 0.25+ | HTTP 客户端 |

---

**© 2026 Kirky.X。保留所有权利。**
