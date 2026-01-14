# 错误响应格式

## 成功响应

```json
{
  "success": true,
  "inserted_count": 1,
  "inserted_ids": ["uuid-1"]
}
```

## 错误响应

```json
{
  "success": false,
  "error": {
    "type": "query_error",
    "message": "relation 'users' does not exist"
  }
}
```

## 错误类型

| type | 说明 |
|------|------|
| `connection_error` | 无法连接到数据库 |
| `query_error` | SQL 语法错误或查询失败 |
| `permission_error` | 操作被权限系统拒绝 |
| `integrity_error` | 外键/唯一约束违反 |
| `timeout_error` | 查询超过超时限制 |
| `security_error` | 危险操作被拦截 |

## 危险操作拦截示例

```json
{
  "success": false,
  "error": {
    "type": "security_error",
    "message": "DELETE statement requires a WHERE clause"
  }
}
```
