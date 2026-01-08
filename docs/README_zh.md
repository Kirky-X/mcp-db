# MCP Database SDK

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE-MIT)
[![Tests](https://img.shields.io/badge/Tests-passing-green.svg)]()

**为大语言模型提供统一数据库操作能力的 Python SDK，支持 7+ 种数据库。**

[🏠 首页](README.md) • [📖 文档](docs/README_zh.md) • [🤝 贡献指南](docs/CONTRIBUTING.md)

---

</div>

## 核心特性

<table>
<tr>
<td width="50%">

### 🔄 统一接口
- **6 个统一工具**：insert、query、update、delete、advanced、execute
- **7 种数据库支持**：PostgreSQL、MySQL、SQLite、MongoDB、Redis、OpenSearch、Supabase
- **自动识别类型**：通过 DATABASE_URL 自动选择适配器
- **异步优先设计**：基于 asyncio 构建

</td>
<td width="50%">

### 🔒 企业级安全
- **SQL 注入防护**：参数化查询
- **危险语句检测**：阻止 DROP、TRUNCATE 等
- **权限控制**：操作需要显式启用
- **审计日志**：操作记录

</td>
</tr>
</table>

---

## 快速开始

### 安装

```bash
pip install mcp-database
```

### 使用方式

```python
from mcp_database.server import create_server

# 创建 MCP Server
server = create_server("postgresql://user:pass@localhost:5432/db")

# Server 暴露 6 个统一工具供 LLM 调用：
# - insert(table, data) -> {"success": true, "inserted_count": 1}
# - query(table, filters, limit) -> {"success": true, "data": [...]}
# - update(table, data, filters) -> {"success": true, "updated_count": 1}
# - delete(table, filters) -> {"success": true, "deleted_count": 1}
# - advanced(table, operation, params) -> {"success": true, "data": {...}}
# - execute(query, params) -> {"success": true, "rows_affected": 1}
```

### 命令行启动

```bash
# 方式1：使用环境变量
DATABASE_URL=postgresql://user:pass@localhost:5432/db mcp-database

# 方式2：指定 URL
mcp-database --database-url=postgresql://user:pass@localhost:5432/db
```

---

## MCP 工具

| 工具 | 功能 | 说明 |
|-----|------|------|
| `insert` | 插入数据 | 添加新记录 |
| `query` | 查询数据 | 检索数据，支持过滤 |
| `update` | 更新数据 | 修改已存在记录 |
| `delete` | 删除数据 | 移除记录 |
| `advanced` | 高级操作 | 聚合查询、事务 |
| `execute` | 原生执行 | 执行任意查询（受限） |

---

## 支持的数据库

| 数据库 | 类型 | 状态 |
|-------|------|------|
| PostgreSQL | 关系型 | ✅ 稳定 |
| MySQL | 关系型 | ✅ 稳定 |
| SQLite | 关系型 | ✅ 稳定 |
| MongoDB | 文档型 | ✅ 稳定 |
| Redis | 键值型 | ✅ 稳定 |
| OpenSearch | 搜索型 | ✅ 稳定 |
| Supabase | REST/PostgreSQL | ✅ 稳定 |

---

## 过滤器操作符

| 操作符 | 描述 | 示例 |
|-------|------|------|
| `__gt` | 大于 | `{"age__gt": 18}` |
| `__gte` | 大于等于 | `{"score__gte": 60}` |
| `__lt` | 小于 | `{"price__lt": 100}` |
| `__lte` | 小于等于 | `{"stock__lte": 0}` |
| `__contains` | 包含子串 | `{"name__contains": "张"}` |
| `__startswith` | 前缀匹配 | `{"email__startswith": "admin"}` |
| `__endswith` | 后缀匹配 | `{"city__endswith": "市"}` |
| `__in` | 在列表中 | `{"status__in": ["a", "b"]}` |
| `__not_in` | 不在列表 | `{"role__not_in": ["admin"]}` |
| `__isnull` | 为空 | `{"deleted_at__isnull": true}` |

---

## 环境变量配置

```bash
# 数据库连接（自动识别类型）
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# 操作开关
ENABLE_INSERT=true
ENABLE_DELETE=false
ENABLE_UPDATE=true
DANGEROUS_AGREE=false

# 超时配置（秒）
CONNECT_TIMEOUT=10
QUERY_TIMEOUT=30

# 查询限制
MAX_QUERY_RESULTS=10000
```

---

## 项目结构

```
mcp-database/
├── src/mcp_database/
│   ├── core/           # SDK 核心模块
│   │   ├── adapter.py  # DatabaseAdapter 抽象基类
│   │   ├── models.py   # Pydantic 数据模型
│   │   ├── exceptions.py
│   │   ├── filters.py
│   │   ├── security.py
│   │   └── permissions.py
│   ├── adapters/       # 数据库适配器
│   │   ├── sql/        # SQL 适配器
│   │   ├── nosql/      # NoSQL 适配器
│   │   └── http/       # HTTP 适配器
│   ├── server/         # MCP Server 实现
│   └── config/
├── tests/              # 测试
└── docs/               # 文档
```

---

## 安全机制

- **SQL 注入防护**：所有查询使用参数化查询
- **危险语句检测**：自动拦截 DROP、TRUNCATE、ALTER 等
- **权限控制**：操作需要环境变量显式启用
- **安全删除/更新**：必须包含 WHERE 条件

---

## 许可证

MIT License - 详见 [LICENSE-MIT](LICENSE-MIT)。

---

**© 2026 Kirky.X。保留所有权利。**
