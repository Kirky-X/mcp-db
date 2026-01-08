# 架构设计文档

## 一、概述

MCP Database SDK 是一个专为 MCP（Model Context Protocol）协议设计的数据库操作工具集。它为大型语言模型提供标准化的数据库访问能力，使 AI 能够通过统一的工具接口执行 CRUD 操作。

### 设计目标

1. **工具化接口** - 所有操作通过 MCP Tool 暴露，大模型可直接调用
2. **上下文感知** - 工具描述包含完整的参数说明和返回格式
3. **安全优先** - 严格的安全检查防止误操作
4. **多数据库兼容** - 支持关系型、文档型、键值型等多种数据库

---

## 二、MCP 工具接口定义

### 2.1 工具命名规范

所有工具遵循统一的命名规范：`db_<操作>_<数据库类型>`

| 工具类型 | 命名模式 | 示例 |
|---------|---------|------|
| 插入工具 | `db_insert_<db>` | `db_insert_postgresql` |
| 查询工具 | `db_query_<db>` | `db_query_mongodb` |
| 更新工具 | `db_update_<db>` | `db_update_redis` |
| 删除工具 | `db_delete_<db>` | `db_delete_mysql` |
| 高级工具 | `db_advanced_<db>` | `db_advanced_mongodb` |

### 2.2 通用工具描述模板

```json
{
  "name": "db_query_<db>",
  "description": "从<数据库名>查询数据，支持灵活的过滤条件。返回匹配的所有记录及其总数。适用于数据检索、统计等场景。",
  "parameters": {
    "type": "object",
    "properties": {
      "table": {
        "type": "string",
        "description": "表/集合/键前缀名称，如 'users'、'products'"
      },
      "filters": {
        "type": "object",
        "description": "过滤条件，支持的操作符：eq(等于)、gt(大于)、lt(小于)、contains(包含)、in(列表)、isnull(空值)。示例：{\"status\": \"active\", \"age__gte\": 18}"
      },
      "limit": {
        "type": "integer",
        "description": "返回记录数量限制，默认100，最大10000"
      }
    },
    "required": ["table"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean", "description": "操作是否成功"},
      "data": {"type": "array", "description": "查询结果数据列表"},
      "count": {"type": "integer", "description": "匹配的记录总数"},
      "has_more": {"type": "boolean", "description": "是否还有更多数据"}
    }
  }
}
```

---

## 三、工具详细定义

### 3.1 插入工具 (db_insert)

**适用场景**：向数据库添加新记录

**参数说明**：
| 参数 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表/集合/键前缀名称 |
| data | object/array | 是 | 要插入的数据，支持单条或批量 |

**返回说明**：
| 字段 | 类型 | 描述 |
|-----|------|-----|
| success | boolean | 插入是否成功 |
| inserted_count | integer | 插入的记录数量 |
| inserted_ids | array | 插入记录的ID列表 |

**调用示例**：
```
工具: db_insert_postgresql
参数: {
  "table": "users",
  "data": {
    "name": "张三",
    "email": "zhangsan@example.com",
    "status": "active"
  }
}
```

### 3.2 查询工具 (db_query)

**适用场景**：检索数据库中的数据

**参数说明**：
| 参数 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表/集合/键前缀名称 |
| filters | object | 否 | 过滤条件，支持多种操作符 |
| limit | integer | 否 | 返回数量限制，默认100 |

**支持的过滤器操作符**：
| 操作符 | 描述 | 示例 |
|-------|-----|------|
| `__eq` | 等于（默认） | `{"status": "active"}` |
| `__gt` | 大于 | `{"age__gt": 18}` |
| `__gte` | 大于等于 | `{"score__gte": 60}` |
| `__lt` | 小于 | `{"price__lt": 100}` |
| `__lte` | 小于等于 | `{"stock__lte": 0}` |
| `__contains` | 包含子串 | `{"name__contains": "张"}` |
| `__startswith` | 前缀匹配 | `{"email__startswith": "admin"}` |
| `__endswith` | 后缀匹配 | `{"file__endswith": ".pdf"}` |
| `__in` | 在列表中 | `{"status__in": ["a", "b"]}` |
| `__not_in` | 不在列表中 | `{"role__not_in": ["admin"]}` |
| `__isnull` | 是否为空 | `{"deleted_at__isnull": true}` |

**返回说明**：
| 字段 | 类型 | 描述 |
|-----|------|-----|
| success | boolean | 查询是否成功 |
| data | array | 查询结果数据 |
| count | integer | 匹配的记录总数 |
| has_more | boolean | 是否还有更多数据 |

### 3.3 更新工具 (db_update)

**适用场景**：修改数据库中已存在的记录

**参数说明**：
| 参数 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表/集合/键前缀名称 |
| data | object | 是 | 要更新的字段和值 |
| filters | object | 是 | 更新条件，限定更新范围 |

**返回说明**：
| 字段 | 类型 | 描述 |
|-----|------|-----|
| success | boolean | 更新是否成功 |
| updated_count | integer | 更新的记录数量 |

### 3.4 删除工具 (db_delete)

**适用场景**：从数据库删除记录

**参数说明**：
| 参数 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表/集合/键前缀名称 |
| filters | object | 是 | 删除条件，限定删除范围 |

**返回说明**：
| 字段 | 类型 | 描述 |
|-----|------|-----|
| success | boolean | 删除是否成功 |
| deleted_count | integer | 删除的记录数量 |

### 3.5 高级工具 (db_advanced)

**适用场景**：执行复杂操作如聚合查询、事务等

**参数说明**：
| 参数 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| table | string | 是 | 表/集合名称 |
| operation | string | 是 | 操作类型：aggregate/transaction |
| params | object | 是 | 操作参数 |

**支持的操作类型**：
- `aggregate`：聚合查询，支持分组、统计、管道操作
- `transaction`：事务操作，支持多步骤原子执行

---

## 四、数据库能力矩阵

### 4.1 支持的数据库及特性

| 数据库 | 类型 | 插入 | 查询 | 更新 | 删除 | 聚合 | 事务 |
|--------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| PostgreSQL | 关系型 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| MySQL | 关系型 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SQLite | 关系型 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| MongoDB | 文档型 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Redis | 键值型 | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| OpenSearch | 搜索型 | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Supabase | REST | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 4.2 工具与数据库映射

| 数据库 | 插入工具 | 查询工具 | 更新工具 | 删除工具 | 高级工具 |
|--------|:-------:|:-------:|:-------:|:-------:|:-------:|
| PostgreSQL | db_insert_postgresql | db_query_postgresql | db_update_postgresql | db_delete_postgresql | db_advanced_postgresql |
| MySQL | db_insert_mysql | db_query_mysql | db_update_mysql | db_delete_mysql | db_advanced_mysql |
| SQLite | db_insert_sqlite | db_query_sqlite | db_update_sqlite | db_delete_sqlite | db_advanced_sqlite |
| MongoDB | db_insert_mongodb | db_query_mongodb | db_update_mongodb | db_delete_mongodb | db_advanced_mongodb |
| Redis | db_insert_redis | db_query_redis | db_update_redis | db_delete_redis | - |
| OpenSearch | db_insert_opensearch | db_query_opensearch | db_update_opensearch | db_delete_opensearch | db_advanced_opensearch |
| Supabase | db_insert_supabase | db_query_supabase | db_update_supabase | db_delete_supabase | db_advanced_supabase |

---

## 五、使用流程

### 5.1 工具发现

MCP 客户端启动时，服务器会返回所有可用工具列表：

```json
{
  "tools": [
    {
      "name": "db_query_postgresql",
      "description": "从PostgreSQL查询数据...",
      "inputSchema": {...}
    },
    {
      "name": "db_insert_mongodb",
      "description": "向MongoDB插入文档...",
      "inputSchema": {...}
    }
  ]
}
```

### 5.2 工具调用流程

```
1. 大模型分析用户意图
   ↓
2. 选择合适的工具（如需要查询用户：db_query_postgresql）
   ↓
3. 构建参数（table="users", filters={"status": "active"}）
   ↓
4. 调用工具
   ↓
5. 返回结果给大模型
   ↓
6. 大模型处理结果并响应用户
```

### 5.3 错误处理

工具调用失败时返回标准错误格式：

```json
{
  "success": false,
  "error": {
    "type": "connection_error|query_error|permission_error",
    "message": "错误描述信息"
  }
}
```

---

## 六、安全机制

### 6.1 操作权限控制

| 操作 | 默认状态 | 环境变量控制 |
|-----|---------|-------------|
| 插入 | 启用 | ENABLE_INSERT |
| 查询 | 启用 | - |
| 更新 | 启用 | ENABLE_UPDATE |
| 删除 | 禁用 | ENABLE_DELETE |
| 执行 | 禁用 | DANGEROUS_AGREE |

### 6.2 SQL 安全检测

自动检测危险操作：
- 禁止： DROP、TRUNCATE、ALTER、GRANT
- 必需 WHERE：DELETE、UPDATE（无 WHERE 拒绝执行）
- 注入检测：识别 SQL 注入模式

### 6.3 查询限制

- 单次查询最大返回：10,000 条记录
- 查询超时：30 秒（可配置）
- 连接超时：10 秒（可配置）

---

## 七、连接配置

### 7.1 数据库 URL 格式

| 数据库 | URL 格式 |
|-------|---------|
| PostgreSQL | `postgresql://user:pass@host:port/db` |
| MySQL | `mysql://user:pass@host:port/db` |
| SQLite | `sqlite:///path/to/file.db` |
| MongoDB | `mongodb://user:pass@host:port/db` |
| Redis | `redis://host:port` |
| OpenSearch | `http://host:9200` |
| Supabase | `https://project.supabase.co` |

### 7.2 环境变量配置

```bash
# 数据库连接
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# 操作开关
ENABLE_INSERT=true
ENABLE_DELETE=true
ENABLE_UPDATE=true
DANGEROUS_AGREE=false

# 超时配置
CONNECT_TIMEOUT=10
QUERY_TIMEOUT=30
```

---

**© 2026 Kirky.X。保留所有权利。**
