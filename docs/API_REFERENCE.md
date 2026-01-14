# 🔧 API Reference

_MCP Database SDK 工具接口文档_

本文档描述 MCP Database SDK 为大语言模型提供的 6 个统一工具接口。

---

## 🛠️ 工具概览

| Tool | Function | Description |
|:-----|:---------|:------------|
| `insert` | 插入数据 | 添加新记录 |
| `query` | 查询数据 | 检索数据，支持过滤 |
| `update` | 更新数据 | 修改已存在记录 |
| `delete` | 删除数据 | 移除记录 |
| `advanced` | 高级操作 | 聚合查询、事务 |
| `execute` | 原生执行 | 执行任意查询（⚠️ 高风险） |

---

## 📝 insert - 插入数据

向数据库插入新记录。

#### Parameters

| Param | Required | Type | Description |
|:------|:--------:|:-----|:------------|
| `table` | ✅ | string | 表/集合/键前缀名 |
| `data` | ✅ | object/array | 要插入的数据，支持单条或批量 |

#### Response

| Field | Type | Description |
|:------|:-----|:------------|
| `success` | boolean | 操作是否成功 |
| `inserted_count` | integer | 插入的记录数 |
| `inserted_ids` | array | 插入记录的ID列表 |

#### Example

```json
{
  "tool": "insert",
  "args": {
    "table": "users",
    "data": {"name": "张三", "email": "zhangsan@example.com"}
  }
}
```

#### Batch Insert

```json
{
  "tool": "insert",
  "args": {
    "table": "users",
    "data": [{"name": "张三"}, {"name": "李四"}]
  }
}
```

---

## 🔍 query - 查询数据

从数据库查询数据。

#### Parameters

| Param | Required | Type | Description |
|:------|:--------:|:-----|:------------|
| `table` | ✅ | string | 表/集合/键前缀名 |
| `filters` | ❌ | object | 过滤条件 |
| `limit` | ❌ | integer | 返回数量限制，默认100，最大10000 |

#### Filter Operators

| Operator | Meaning | Example |
|:---------|:--------|:--------|
| (none) | Equals | `{"status": "active"}` |
| `__gt` | Greater than | `{"age__gt": 18}` |
| `__gte` | ≥ | `{"score__gte": 60}` |
| `__lt` | Less than | `{"price__lt": 100}` |
| `__lte` | ≤ | `{"stock__lte": 0}` |
| `__contains` | Contains | `{"name__contains": "张"}` |
| `__startswith` | Starts with | `{"email__startswith": "admin"}` |
| `__endswith` | Ends with | `{"city__endswith": "市"}` |
| `__in` | In list | `{"status__in": ["active"]}` |
| `__isnull` | Is NULL | `{"deleted_at__isnull": true}` |

#### Response

| Field | Type | Description |
|:------|:-----|:------------|
| `success` | boolean | 操作是否成功 |
| `data` | array | 查询结果数据列表 |
| `count` | integer | 匹配的记录总数 |
| `has_more` | boolean | 是否还有更多数据 |

#### Example

```json
{
  "tool": "query",
  "args": {
    "table": "users",
    "filters": {"status": "active", "age__gte": 18},
    "limit": 10
  }
}
```

---

## ✏️ update - 更新数据

更新数据库中已存在的记录。

#### Parameters

| Param | Required | Type | Description |
|:------|:--------:|:-----|:------------|
| `table` | ✅ | string | 表/集合/键前缀名 |
| `data` | ✅ | object | 要更新的字段和值 |
| `filters` | ✅ | object | 更新条件（限定更新范围） |

#### Response

| Field | Type | Description |
|:------|:-----|:------------|
| `success` | boolean | 操作是否成功 |
| `updated_count` | integer | 更新的记录数 |

#### Example

```json
{
  "tool": "update",
  "args": {
    "table": "users",
    "data": {"status": "inactive"},
    "filters": {"id": 1}
  }
}
```

---

## 🗑️ delete - 删除数据

从数据库删除记录。

#### Parameters

| Param | Required | Type | Description |
|:------|:--------:|:-----|:------------|
| `table` | ✅ | string | 表/集合/键前缀名 |
| `filters` | ✅ | object | 删除条件（限定删除范围） |

#### Response

| Field | Type | Description |
|:------|:-----|:------------|
| `success` | boolean | 操作是否成功 |
| `deleted_count` | integer | 删除的记录数 |

#### Example

```json
{
  "tool": "delete",
  "args": {
    "table": "users",
    "filters": {"status": "deleted"}
  }
}
```

---

## ⚡ advanced - 高级操作

执行聚合查询、事务等复杂操作。

#### Parameters

| Param | Required | Type | Description |
|:------|:--------:|:-----|:------------|
| `table` | ✅ | string | 表/集合名 |
| `operation` | ✅ | string | `aggregate` / `transaction` |
| `params` | ✅ | object | 操作参数 |

##### Aggregate

```json
{
  "tool": "advanced",
  "args": {
    "table": "orders",
    "operation": "aggregate",
    "pipeline": [
      {"$match": {"status": "completed"}},
      {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
    ]
  }
}
```

##### Transaction

```json
{
  "tool": "advanced",
  "args": {
    "table": "users",
    "operation": "transaction",
    "queries": [
      {"query": "UPDATE accounts SET balance = ? WHERE id = ?", "params": [100, 1]},
      {"query": "UPDATE accounts SET balance = ? WHERE id = ?", "params": [100, 2]}
    ]
  }
}
```

#### Response

| Field | Type | Description |
|:------|:-----|:------------|
| `success` | boolean | 操作是否成功 |
| `operation` | string | 操作类型 |
| `data` | object | 操作结果数据 |

---

## 🔥 execute - 原生执行

执行任意原生查询语句。⚠️ 默认禁用，需设置 `DANGEROUS_AGREE=true`

#### Parameters

| Param | Required | Type | Description |
|:------|:--------:|:-----|:------------|
| `query` | ✅ | string | 原生 SQL/MongoDB 查询语句 |
| `params` | ❌ | object | 查询参数（用于参数化查询） |

#### Response

| Field | Type | Description |
|:------|:-----|:------------|
| `success` | boolean | 操作是否成功 |
| `rows_affected` | integer | 影响的行数 |
| `data` | array | 返回的数据（SELECT 类查询） |

#### Example

```json
{
  "tool": "execute",
  "args": {
    "query": "SELECT * FROM users WHERE status = :status",
    "params": {"status": "active"}
  }
}
```

---

## ⚠️ 错误响应

所有工具调用失败时返回统一错误格式：

```json
{
  "success": false,
  "error": {
    "type": "connection_error|query_error|permission_error|timeout_error|integrity_error",
    "message": "详细的错误描述"
  }
}
```

#### 错误类型

| Type | Description |
|:-----|:------------|
| `connection_error` | 数据库连接失败 |
| `query_error` | 查询语法或执行错误 |
| `permission_error` | 操作权限被拒绝 |
| `timeout_error` | 操作超时 |
| `integrity_error` | 违反完整性约束（如唯一键冲突） |

---

**© 2026 Kirky.X**
