# 🚀 MCP Database SDK

_为大语言模型提供统一数据库操作能力的 Python SDK_

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE-MIT) [![Tests](https://img.shields.io/badge/Tests-passing-green.svg)]()

**支持 7+ 种数据库的统一接口**

---

[🏠 English](README.md) · [🤝 贡献指南](docs/CONTRIBUTING.md) · [🔧 API](docs/API_REFERENCE.md) · [🏗️ 架构](docs/ARCHITECTURE.md)

---

## ✨ 核心特性

| | |
|:--|:--|
| **🔄 统一接口** | 6 个工具 + 7 种数据库支持，自动识别类型 |
| **🔒 企业级安全** | SQL 注入防护、危险语句检测、权限控制 |
| **⚡ 异步优先** | 基于 asyncio 构建，高性能连接池 |

---

## 🚀 快速开始

### 安装

```bash
pip install mcp-database
```

### 使用方式

```python
from mcp_database.server import create_server

server = create_server("postgresql://user:pass@localhost:5432/db")

# Server 暴露 6 个统一工具供 LLM 调用
```

### 命令行

```bash
DATABASE_URL=postgresql://... mcp-database
# 或
mcp-database --database-url=postgresql://...
```

---

## 🛠️ MCP 工具

| Tool | Function |
|:-----|:---------|
| `insert` | 插入数据 |
| `query` | 查询数据 |
| `update` | 更新数据 |
| `delete` | 删除数据 |
| `advanced` | 高级操作 |
| `execute` | 原生执行（⚠️ 受限） |

---

## 🗄️ 支持的数据库

| Database | Type | |
|:---------|:-----|:-|
| 🐘 PostgreSQL | 关系型 | ✅ |
| 🐬 MySQL | 关系型 | ✅ |
| 📦 SQLite | 关系型 | ✅ |
| 🍃 MongoDB | 文档型 | ✅ |
| ⚡ Redis | 键值型 | ✅ |
| 🔍 OpenSearch | 搜索型 | ✅ |
| 🔥 Supabase | REST | ✅ |

---

## 🔍 过滤器操作符

| Operator | Meaning | Example |
|:---------|:--------|:--------|
| `__gt` | 大于 | `{"age__gt": 18}` |
| `__gte` | ≥ | `{"score__gte": 60}` |
| `__lt` | 小于 | `{"price__lt": 100}` |
| `__lte` | ≤ | `{"stock__lte": 0}` |
| `__contains` | 包含 | `{"name__contains": "张"}` |
| `__startswith` | 前缀 | `{"email__startswith": "admin"}` |
| `__in` | 在列表 | `{"status__in": ["a"]}` |
| `__isnull` | 为空 | `{"deleted_at__isnull": true}` |

---

## ⚙️ 环境变量

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/db
ENABLE_INSERT=true
ENABLE_DELETE=false
ENABLE_UPDATE=true
DANGEROUS_AGREE=false
CONNECT_TIMEOUT=10
QUERY_TIMEOUT=30
MAX_QUERY_RESULTS=10000
```

---

## 📁 项目结构

```
mcp-database/
├── src/mcp_database/
│   ├── core/           # SDK 核心模块
│   │   ├── adapter.py  # DatabaseAdapter
│   │   ├── models.py   # Pydantic 模型
│   │   ├── exceptions.py
│   │   ├── filters.py
│   │   ├── security.py
│   │   └── permissions.py
│   ├── adapters/       # 数据库适配器
│   │   ├── sql/
│   │   ├── nosql/
│   │   └── http/
│   ├── server/         # MCP Server
│   └── config/
├── tests/              # 测试
└── docs/               # 文档
```

---

## 🛡️ 安全机制

- **SQL 注入防护**：参数化查询
- **危险语句检测**：拦截 DROP/TRUNCATE/ALTER
- **权限控制**：DELETE/EXECUTE 需要显式启用
- **安全更新/删除**：必须包含 WHERE 条件

---

## 📄 许可证

MIT License - 详见 [LICENSE-MIT](LICENSE-MIT)。

---

**© 2026 Kirky.X**
