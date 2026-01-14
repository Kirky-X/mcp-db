---
name: mcp-database
description: MCP Database SDK - 统一数据库操作 MCP Server 接口定义
version: 1.0.0
author: MCP Database Team
tags: [mcp, database, server, sdk, fastmcp]
trigger: when working with mcp-database MCP server or database operations via MCP
context_size: large
---

# MCP Database Server 接口规范

## 服务概述

MCP Database Server 是基于 FastMCP 框架的数据库操作服务，提供统一的 CRUD 接口，支持 7 种数据库。

## 工具列表

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `insert` | 插入记录 | table, data |
| `query` | 查询数据 | table, filters, limit |
| `update` | 更新记录 | table, data, filters |
| `delete` | 删除记录 | table, filters |
| `advanced` | 高级操作 | table, operation, params |
| `execute` | 原生查询 | query, params |

---

## 工具详细定义

### 1. insert - 插入数据

```python
@mcp.tool()
async def insert(table: str, data: dict | list[dict]) -> dict
```

**描述**: 向数据库插入新记录，支持单条和批量插入

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| table | string | 是 | 表/集合/键前缀名 |
| data | object \| array | 是 | 要插入的数据（对象或数组） |

**返回**:
```json
{
  "success": true,
  "inserted_count": 1,
  "inserted_ids": ["id1", "id2"]
}
```

**示例**:
```json
// 单条插入
{
  "table": "users",
  "data": {"name": "John", "email": "john@example.com"}
}

// 批量插入
{
  "table": "users",
  "data": [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"}
  ]
}
```

---

### 2. query - 查询数据

```python
@mcp.tool()
async def query(table: str, filters: dict | None, limit: int | None) -> dict
```

**描述**: 从数据库查询数据，支持复杂过滤条件

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| table | string | 是 | 表/集合/键前缀名 |
| filters | object | 否 | 过滤条件，支持 DSL 操作符 |
| limit | integer | 否 | 返回数量限制，默认 100，最大 10000 |

**返回**:
```json
{
  "success": true,
  "data": [...],
  "count": 10,
  "has_more": false
}
```

**Filter DSL 操作符**:
| 操作符 | 含义 | 示例 |
|--------|------|------|
| `__gt` | 大于 | `{"age__gt": 18}` |
| `__gte` | 大于等于 | `{"score__gte": 60}` |
| `__lt` | 小于 | `{"price__lt": 100}` |
| `__lte` | 小于等于 | `{"stock__lte": 0}` |
| `__contains` | 包含子串 | `{"name__contains": "John"}` |
| `__startswith` | 前缀匹配 | `{"email__startswith": "admin"}` |
| `__endswith` | 后缀匹配 | `{"file__endswith": ".pdf"}` |
| `__in` | 在列表中 | `{"status__in": ["active", "pending"]}` |
| `__not_in` | 不在列表中 | `{"role__not_in": ["admin"]}` |
| `__isnull` | 为 NULL | `{"deleted_at__isnull": true}` |

**示例**:
```json
// 基础查询
{
  "table": "users",
  "filters": {"status": "active"},
  "limit": 10
}

// 复杂条件
{
  "table": "products",
  "filters": {
    "category": "electronics",
    "price__lt": 1000,
    "stock__gte": 10
  }
}

// NULL 查询
{
  "table": "orders",
  "filters": {"deleted_at__isnull": true}
}
```

---

### 3. update - 更新数据

```python
@mcp.tool()
async def update(table: str, data: dict, filters: dict) -> dict
```

**描述**: 更新数据库中已存在的记录

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| table | string | 是 | 表/集合/键前缀名 |
| data | object | 是 | 要更新的字段和值 |
| filters | object | 是 | 更新条件（限定更新范围） |

**返回**:
```json
{
  "success": true,
  "updated_count": 5
}
```

**示例**:
```json
{
  "table": "users",
  "data": {"status": "active", "last_login": "2024-01-01"},
  "filters": {"name": "John"}
}
```

---

### 4. delete - 删除数据

```python
@mcp.tool()
async def delete(table: str, filters: dict) -> dict
```

**描述**: 从数据库删除记录

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| table | string | 是 | 表/集合/键前缀名 |
| filters | object | 是 | 删除条件（限定删除范围） |

**返回**:
```json
{
  "success": true,
  "deleted_count": 3
}
```

**示例**:
```json
{
  "table": "users",
  "filters": {"status": "inactive", "last_login__lt": "2023-01-01"}
}
```

---

### 5. advanced - 高级操作

```python
@mcp.tool()
async def advanced(table: str, operation: str, params: dict) -> dict
```

**描述**: 执行高级操作，如聚合查询、事务等

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| table | string | 是 | 表/集合名 |
| operation | string | 是 | 操作类型（aggregate, transaction） |
| params | object | 是 | 操作参数 |

**返回**:
```json
{
  "success": true,
  "operation": "aggregate",
  "data": [...]
}
```

---

### 6. execute - 原生查询

```python
@mcp.tool()
async def execute(query: str, params: dict | None) -> dict
```

**描述**: 执行任意原生查询语句（默认禁用，需 `DANGEROUS_AGREE=true`）

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 原生 SQL/MongoDB 查询语句 |
| params | object | 否 | 查询参数（用于参数化查询） |

**返回**:
```json
{
  "success": true,
  "rows_affected": 10,
  "data": [...]
}
```

---

## 数据库 URL 格式

```python
# PostgreSQL
"postgresql://user:pass@localhost:5432/db"

# MySQL
"mysql+aiomysql://user:pass@localhost:3306/db"

# MongoDB
"mongodb://user:pass@localhost:27017/db"

# Redis
"redis://user:pass@localhost:6379/0"

# SQLite
"sqlite:///./example.db"
```

---

## 安全特性

### SQL 注入防护
- 所有查询使用参数化查询
- 自动转义用户输入
- 禁止字符串拼接构建 SQL

### 危险操作检测
- `DROP`, `DELETE`, `TRUNCATE` 等危险语句会被检测
- 无 WHERE 子句的 UPDATE/DELETE 会被阻止

### 权限控制
- 默认禁用 `execute` 工具
- 需设置 `DANGEROUS_AGREE=true` 才能使用

---

## 错误处理

所有工具返回统一的错误格式：

```json
{
  "success": false,
  "error": {
    "type": "query_error",
    "message": "详细错误信息"
  }
}
```

**错误类型**:
| 类型 | 说明 |
|------|------|
| `connection_error` | 数据库连接失败 |
| `query_error` | 查询执行错误 |
| `permission_error` | 权限不足 |
| `integrity_error` | 数据完整性错误 |
| `timeout_error` | 操作超时 |

---

## 返回结果结构

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 操作是否成功 |
| inserted_count | integer | 插入数量 |
| updated_count | integer | 更新数量 |
| deleted_count | integer | 删除数量 |
| count | integer | 查询结果数量 |
| data | array | 返回的数据列表 |
| has_more | boolean | 是否有更多数据 |
| error | object | 错误信息 |

---

## 使用示例

### 完整工作流

```json
// 1. 插入数据
{
  "tool": "insert",
  "arguments": {
    "table": "users",
    "data": {"name": "Alice", "email": "alice@example.com"}
  }
}

// 2. 查询数据
{
  "tool": "query",
  "arguments": {
    "table": "users",
    "filters": {"name__contains": "Ali"},
    "limit": 10
  }
}

// 3. 更新数据
{
  "tool": "update",
  "arguments": {
    "table": "users",
    "data": {"status": "active"},
    "filters": {"name": "Alice"}
  }
}

// 4. 删除数据
{
  "tool": "delete",
  "arguments": {
    "table": "users",
    "filters": {"status": "banned"}
  }
}
```

---

## MCP Server 启动

```python
from mcp_database.server import create_server

# 创建 MCP Server
mcp = create_server("postgresql://user:pass@localhost:5432/db")

# 启动服务
mcp.run()
```

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | 数据库连接 URL | - |
| DANGEROUS_AGREE | 启用危险操作 | false |
