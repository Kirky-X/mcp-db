# Filter DSL 操作符速查

## 比较操作符

| 操作符 | SQL 等价 | 示例 | 说明 |
|--------|----------|------|------|
| `__gt` | `>` | `{"age__gt": 18}` | 大于 |
| `__gte` | `>=` | `{"score__gte": 60}` | 大于等于 |
| `__lt` | `<` | `{"price__lt": 100}` | 小于 |
| `__lte` | `<=` | `{"stock__lte": 0}` | 小于等于 |

## 字符串操作符

| 操作符 | SQL 等价 | 示例 | 说明 |
|--------|----------|------|------|
| `__contains` | `LIKE %...%` | `{"name__contains": "John"}` | 包含子串 |
| `__startswith` | `LIKE ...%` | `{"email__startswith": "admin"}` | 前缀匹配 |
| `__endswith` | `LIKE %...` | `{"file__endswith": ".pdf"}` | 后缀匹配 |

## 列表操作符

| 操作符 | SQL 等价 | 示例 | 说明 |
|--------|----------|------|------|
| `__in` | `IN` | `{"status__in": ["A", "B"]}` | 在列表中 |
| `__not_in` | `NOT IN` | `{"role__not_in": ["admin"]}` | 不在列表中 |

## NULL 操作符

| 操作符 | SQL 等价 | 示例 | 说明 |
|--------|----------|------|------|
| `__isnull` | `IS NULL` / `IS NOT NULL` | `{"deleted_at__isnull": true}` | 为 NULL |
| `__notnull` | `IS NOT NULL` | `{"created_at__notnull": true}` | 不为 NULL |

## 组合使用

```json
{
  "category": "electronics",
  "price__gte": 100,
  "price__lte": 1000,
  "name__contains": "pro",
  "stock__gt": 0
}
```
