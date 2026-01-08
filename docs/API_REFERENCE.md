# API 参考文档

本文档描述 MCP Database SDK 为大语言模型提供的工具接口。所有接口均为 Tool 形式，大模型可直接调用执行数据库操作。

---

## 一、工具概览

### 1.1 工具分类

| 类别 | 工具前缀 | 功能描述 |
|-----|---------|---------|
| 插入类 | `db_insert_*` | 添加新记录到数据库 |
| 查询类 | `db_query_*` | 检索数据库中的数据 |
| 更新类 | `db_update_*` | 修改已存在的记录 |
| 删除类 | `db_delete_*` | 从数据库移除记录 |
| 高级类 | `db_advanced_*` | 执行聚合、事务等复杂操作 |

### 1.2 数据库后缀映射

| 后缀 | 数据库 | 类型 |
|-----|-------|------|
| `_postgresql` | PostgreSQL | 关系型 |
| `_mysql` | MySQL | 关系型 |
| `_sqlite` | SQLite | 关系型 |
| `_mongodb` | MongoDB | 文档型 |
| `_redis` | Redis | 键值型 |
| `_opensearch` | OpenSearch | 搜索型 |
| `_supabase` | Supabase | REST API |

---

## 二、插入工具 (db_insert)

### db_insert_postgresql

向 PostgreSQL 数据库插入新记录。

**参数**：
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表名，如 "users"、"orders" |
| data | object/array | 是 | 要插入的数据，单条或批量 |

**返回**：
| 字段 | 类型 | 描述 |
|-----|------|-----|
| success | boolean | 插入是否成功 |
| inserted_count | integer | 插入的记录数 |
| inserted_ids | array | 插入记录的ID列表 |

**调用示例**：
```
工具: db_insert_postgresql
参数: {"table": "users", "data": {"name": "张三", "email": "zhangsan@example.com"}}
```

### db_insert_mysql

向 MySQL 数据库插入新记录。

**参数**：
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表名 |
| data | object/array | 是 | 要插入的数据 |

**返回**：同 PostgreSQL

### db_insert_mongodb

向 MongoDB 集合插入文档。

**参数**：
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 集合名，如 "users"、"products" |
| data | object/array | 是 | 文档数据，支持批量插入 |

**返回**：同 PostgreSQL

### db_insert_redis

向 Redis 存储数据（使用 table:id 键前缀模式）。

**参数**：
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 键前缀，如 "user"、"session" |
| data | object/array | 是 | 要存储的数据 |

**返回**：同 PostgreSQL

---

## 三、查询工具 (db_query)

### db_query_postgresql

从 PostgreSQL 查询数据。

**参数**：
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表名 |
| filters | object | 否 | 过滤条件 |
| limit | integer | 否 | 返回数量限制，默认100 |

**过滤器操作符**：
| 操作符 | 描述 | 示例 |
|-------|-----|------|
| 无后缀 | 等于 | `{"status": "active"}` |
| `__gt` | 大于 | `{"age__gt": 18}` |
| `__gte` | 大于等于 | `{"score__gte": 60}` |
| `__lt` | 小于 | `{"price__lt": 100}` |
| `__lte` | 小于等于 | `{"stock__lte": 0}` |
| `__contains` | 包含 | `{"name__contains": "张"}` |
| `__startswith` | 前缀 | `{"email__startswith": "admin"}` |
| `__endswith` | 后缀 | `{"city__endswith": "市"}` |
| `__in` | 在列表中 | `{"status__in": ["a", "b"]}` |
| `__not_in` | 不在列表 | `{"role__not_in": ["admin"]}` |
| `__isnull` | 为空 | `{"deleted_at__isnull": true}` |

**返回**：
| 字段 | 类型 | 描述 |
|-----|------|-----|
| success | boolean | 查询是否成功 |
| data | array | 结果数据列表 |
| count | integer | 匹配总数 |
| has_more | boolean | 是否还有更多数据 |

**调用示例**：
```
工具: db_query_postgresql
参数: {"table": "users", "filters": {"status": "active", "age__gte": 18}, "limit": 10}
```

### db_query_mongodb

从 MongoDB 查询文档。

**参数**：同 PostgreSQL

**返回**：同 PostgreSQL

### db_query_redis

从 Redis 查询数据。

**参数**：同 PostgreSQL

**返回**：同 PostgreSQL

---

## 四、更新工具 (db_update)

### db_update_postgresql

更新 PostgreSQL 中的记录。

**参数**：
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表名 |
| data | object | 是 | 要更新的字段和值 |
| filters | object | 是 | 更新条件（必需） |

**返回**：
| 字段 | 类型 | 描述 |
|-----|------|-----|
| success | boolean | 更新是否成功 |
| updated_count | integer | 更新的记录数 |

**调用示例**：
```
工具: db_update_postgresql
参数: {"table": "users", "data": {"status": "inactive"}, "filters": {"id": 1}}
```

### db_update_mongodb

更新 MongoDB 中的文档。

**参数**：同 PostgreSQL

**返回**：同 PostgreSQL

---

## 五、删除工具 (db_delete)

### db_delete_postgresql

从 PostgreSQL 删除记录。

**参数**：
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表名 |
| filters | object | 是 | 删除条件（必需） |

**返回**：
| 字段 | 类型 | 描述 |
|-----|------|-----|
| success | boolean | 删除是否成功 |
| deleted_count | integer | 删除的记录数 |

**调用示例**：
```
工具: db_delete_postgresql
参数: {"table": "users", "filters": {"status": "deleted"}}
```

### db_delete_mongodb

从 MongoDB 删除文档。

**参数**：同 PostgreSQL

**返回**：同 PostgreSQL

---

## 六、高级工具 (db_advanced)

### db_advanced_mongodb

执行 MongoDB 聚合查询或事务。

**参数**：
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 集合名 |
| operation | string | 是 | 操作类型：aggregate / transaction |
| params | object | 是 | 操作参数 |

**聚合查询示例**：
```
工具: db_advanced_mongodb
参数: {
  "table": "orders",
  "operation": "aggregate",
  "pipeline": [
    {"$match": {"status": "completed"}},
    {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
  ]
}
```

**事务示例**：
```
工具: db_advanced_mongodb
参数: {
  "table": "users",
  "operation": "transaction",
  "operations": [
    {"type": "insert", "data": {"name": "新用户"}},
    {"type": "update", "data": {"status": "active"}, "filters": {"name": "新用户"}}
  ]
}
```

### db_advanced_postgresql

执行 PostgreSQL 事务操作。

**参数**：
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表名 |
| operation | string | 是 | 操作类型：transaction |
| params | object | 是 | 包含 queries 数组 |

**事务示例**：
```
工具: db_advanced_postgresql
参数: {
  "table": "orders",
  "operation": "transaction",
  "queries": [
    {"query": "UPDATE accounts SET balance = balance - ? WHERE id = ?", "params": [100, 1]},
    {"query": "UPDATE accounts SET balance = balance + ? WHERE id = ?", "params": [100, 2]}
  ]
}
```

---

## 七、错误响应格式

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

**错误类型说明**：
| 类型 | 描述 |
|-----|------|
| connection_error | 数据库连接失败 |
| query_error | 查询语法或执行错误 |
| permission_error | 操作权限被拒绝 |
| timeout_error | 操作超时 |
| integrity_error | 违反完整性约束 |

---

## 八、使用建议

### 8.1 工具选择指南

| 需求 | 推荐的工具 |
|-----|-----------|
| 添加单个记录 | db_insert_<db> |
| 批量添加记录 | db_insert_<db>（传入数组） |
| 获取列表数据 | db_query_<db> |
| 获取单条记录 | db_query_<db> + limit=1 |
| 按ID查询 | db_query_<db> + filters: {"id": 123} |
| 按条件筛选 | db_query_<db> + filters |
| 修改数据 | db_update_<db> |
| 移除数据 | db_delete_<db> |
| 统计/聚合 | db_advanced_<db> + aggregate |
| 原子操作 | db_advanced_<db> + transaction |

### 8.2 最佳实践

1. **使用过滤器限定范围**：更新和删除操作必须包含 filters，防止全表操作
2. **设置合理的 limit**：默认返回100条，根据需要调整
3. **使用正确的操作符**：选择合适的过滤器操作符提高查询精度
4. **处理 has_more**：当返回 has_more=true 时，考虑添加更具体的过滤条件

---

**© 2026 Kirky.X。保留所有权利。**
