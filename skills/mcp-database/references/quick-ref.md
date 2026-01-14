# MCP Database 工具速查

## 6 个工具

```
insert   → 插入数据 (table, data)
query    → 查询数据 (table, filters, limit)
update   → 更新数据 (table, data, filters)
delete   → 删除数据 (table, filters)
advanced → 高级操作 (table, operation, params)
execute  → 原生查询 (query, params) *需 DANGEROUS_AGREE=true
```

## 工具调用模板

```json
{
  "tool": "query",
  "arguments": {
    "table": "users",
    "filters": {"status": "active"},
    "limit": 10
  }
}
```

## Filter DSL

```
__gt      >      年龄 > 18
__gte     >=     分数 >= 60
__lt      <      价格 < 100
__lte     <=     库存 <= 0
__contains     名称包含 "John"
__startswith   邮箱开头 "admin"
__endswith     文件结尾 ".pdf"
__in      在列表 ["A","B"]
__isnull 为空
```

## 返回格式

**成功**:
```json
{"success": true, "data": [...], "count": 10}
```

**失败**:
```json
{"success": false, "error": {"type": "query_error", "message": "..."}}
```

## 数据库 URL

```
postgresql://user:pass@host:port/db
mysql+aiomysql://user:pass@host:port/db
mongodb://user:pass@host:port/db
redis://user:pass@host:port/db
```
