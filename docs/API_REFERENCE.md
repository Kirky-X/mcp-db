# API 参考文档

本文档描述 MCP Database SDK 为大语言模型提供的工具接口。

---

## 一、工具概览

| 工具名 | 功能 | 说明 |
|-------|------|------|
| `insert` | 插入数据 | 添加新记录 |
| `query` | 查询数据 | 检索数据，支持过滤 |
| `update` | 更新数据 | 修改已存在记录 |
| `delete` | 删除数据 | 移除记录 |
| `advanced` | 高级操作 | 聚合查询、事务 |
| `execute` | 原生执行 | 执行任意查询（高风险） |

---

## 二、insert - 插入数据

向数据库插入新记录。

### 参数

| 字段 | 必填 | 类型 | 描述 |
|-----|:---:|-----|------|
| table | 是 | string | 表/集合/键前缀名 |
| data | 是 | object/array | 要插入的数据，支持单条或批量 |

### 返回

| 字段 | 类型 | 描述 |
|-----|------|------|
| success | boolean | 操作是否成功 |
| inserted_count | integer | 插入的记录数 |
| inserted_ids | array | 插入记录的ID列表 |

### 调用示例

```
工具: insert
参数: {"table": "users", "data": {"name": "张三", "email": "zhangsan@example.com"}}
```

### 批量插入

```
工具: insert
参数: {"table": "users", "data": [{"name": "张三"}, {"name": "李四"}]}
```

---

## 三、query - 查询数据

从数据库查询数据。

### 参数

| 字段 | 必填 | 类型 | 描述 |
|-----|:---:|-----|------|
| table | 是 | string | 表/集合/键前缀名 |
| filters | 否 | object | 过滤条件 |
| limit | 否 | integer | 返回数量限制，默认100，最大10000 |

### 过滤器操作符

| 操作符 | 描述 | 示例 |
|-------|------|------|
| 无后缀 | 等于（默认） | `{"status": "active"}` |
| `__gt` | 大于 | `{"age__gt": 18}` |
| `__gte` | 大于等于 | `{"score__gte": 60}` |
| `__lt` | 小于 | `{"price__lt": 100}` |
| `__lte` | 小于等于 | `{"stock__lte": 0}` |
| `__contains` | 包含子串 | `{"name__contains": "张"}` |
| `__startswith` | 前缀匹配 | `{"email__startswith": "admin"}` |
| `__endswith` | 后缀匹配 | `{"city__endswith": "市"}` |
| `__in` | 在列表中 | `{"status__in": ["active", "pending"]}` |
| `__not_in` | 不在列表 | `{"role__not_in": ["admin"]}` |
| `__isnull` | 为空 | `{"deleted_at__isnull": true}` |

### 返回

| 字段 | 类型 | 描述 |
|-----|------|------|
| success | boolean | 操作是否成功 |
| data | array | 查询结果数据列表 |
| count | integer | 匹配的记录总数 |
| has_more | boolean | 是否还有更多数据 |

### 调用示例

```
工具: query
参数: {"table": "users", "filters": {"status": "active", "age__gte": 18}, "limit": 10}
```

---

## 四、update - 更新数据

更新数据库中已存在的记录。

### 参数

| 字段 | 必填 | 类型 | 描述 |
|-----|:---:|-----|------|
| table | 是 | string | 表/集合/键前缀名 |
| data | 是 | object | 要更新的字段和值 |
| filters | 是 | object | 更新条件（限定更新范围） |

### 返回

| 字段 | 类型 | 描述 |
|-----|------|------|
| success | boolean | 操作是否成功 |
| updated_count | integer | 更新的记录数 |

### 调用示例

```
工具: update
参数: {"table": "users", "data": {"status": "inactive"}, "filters": {"id": 1}}
```

---

## 五、delete - 删除数据

从数据库删除记录。

### 参数

| 字段 | 必填 | 类型 | 描述 |
|-----|:---:|-----|------|
| table | 是 | string | 表/集合/键前缀名 |
| filters | 是 | object | 删除条件（限定删除范围） |

### 返回

| 字段 | 类型 | 描述 |
|-----|------|------|
| success | boolean | 操作是否成功 |
| deleted_count | integer | 删除的记录数 |

### 调用示例

```
工具: delete
参数: {"table": "users", "filters": {"status": "deleted"}}
```

---

## 六、advanced - 高级操作

执行聚合查询、事务等复杂操作。

### 参数

| 字段 | 必填 | 类型 | 描述 |
|-----|:---:|-----|------|
| table | 是 | string | 表/集合名 |
| operation | 是 | string | 操作类型：aggregate / transaction |
| params | 是 | object | 操作参数 |

### 6.1 aggregate - 聚合查询

```
工具: advanced
参数: {
  "table": "orders",
  "operation": "aggregate",
  "pipeline": [
    {"$match": {"status": "completed"}},
    {"$group": {"_id": "$category", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
  ]
}
```

### 6.2 transaction - 事务操作

```
工具: advanced
参数: {
  "table": "users",
  "operation": "transaction",
  "queries": [
    {"query": "UPDATE accounts SET balance = balance - ? WHERE id = ?", "params": [100, 1]},
    {"query": "UPDATE accounts SET balance = balance + ? WHERE id = ?", "params": [100, 2]}
  ]
}
```

### 返回

| 字段 | 类型 | 描述 |
|-----|------|------|
| success | boolean | 操作是否成功 |
| operation | string | 操作类型 |
| data | object | 操作结果数据 |

---

## 七、execute - 原生执行

执行任意原生查询语句。此工具默认禁用，需设置 `DANGEROUS_AGREE=true` 才会生效。

### 参数

| 字段 | 必填 | 类型 | 描述 |
|-----|:---:|-----|------|
| query | 是 | string | 原生 SQL/MongoDB 查询语句 |
| params | 否 | object | 查询参数（用于参数化查询） |

### 返回

| 字段 | 类型 | 描述 |
|-----|------|------|
| success | boolean | 操作是否成功 |
| rows_affected | integer | 影响的行数 |
| data | array | 返回的数据（SELECT 类查询） |

### 调用示例

```
工具: execute
参数: {"query": "SELECT * FROM users WHERE status = :status", "params": {"status": "active"}}
```

---

## 八、错误响应

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

### 错误类型说明

| 类型 | 描述 |
|-------|------|
| connection_error | 数据库连接失败 |
| query_error | 查询语法或执行错误 |
| permission_error | 操作权限被拒绝 |
| timeout_error | 操作超时 |
| integrity_error | 违反完整性约束（如唯一键冲突） |

---

**© 2026 Kirky.X。保留所有权利。**
