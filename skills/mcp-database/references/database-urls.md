# 数据库 URL 格式速查

## SQL 数据库

| 数据库 | URL 格式 |
|--------|----------|
| PostgreSQL | `postgresql://user:pass@host:port/db` |
| MySQL | `mysql+aiomysql://user:pass@host:port/db` |
| SQLite | `sqlite:///./path/to/file.db` |

## NoSQL 数据库

| 数据库 | URL 格式 |
|--------|----------|
| MongoDB | `mongodb://user:pass@host:port/db` |
| Redis | `redis://user:pass@host:port/db` |

## 示例

```python
# PostgreSQL
"postgresql://admin:secret@localhost:5432/shopdb"

# MySQL
"mysql+aiomysql://root:password@db.example.com:3306/app"

# MongoDB
"mongodb://localhost:27017/test"

# Redis
"redis://:password@redis.example.com:6379/0"
```
