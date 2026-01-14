# 🚀 MCP Database SDK

_A unified database operation SDK for Large Language Models_

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![Tests](https://img.shields.io/badge/Tests-passing-green.svg)]()

**The missing link between LLMs and your database.**

---

[📖 Documentation](docs/README_zh.md) · [🔧 API Reference](docs/API_REFERENCE.md) · [🤝 Contributing](docs/CONTRIBUTING.md) · [🏗️ Architecture](docs/ARCHITECTURE.md)

---

## ✨ Why MCP Database SDK?

| | |
|:--|:--|
| **🔄 One SDK, Seven Databases** | Write once, run anywhere. Same API for PostgreSQL, MySQL, SQLite, MongoDB, Redis, OpenSearch, Supabase |
| **⚡ Built for Speed** | Async-first architecture with connection pooling and optimized drivers (SQLAlchemy 2.0, Motor) |

---

## 🎯 Key Features

| | |
|:--|:--|
| **🔄 Unified Interface** | Consistent API across 7 databases with async-first design |
| **🔒 Enterprise Security** | SQL injection prevention, permission control, audit logging |
| **🗄️ Multi-Database Support** | PostgreSQL, MySQL, SQLite, MongoDB, Redis, OpenSearch, Supabase |
| **⚡ High Performance** | Async operations, connection pooling, optimized drivers |

---

## 🚀 Quick Start

### 📦 Installation

```bash
pip install mcp-database
```

### ⚡ Quick Example

```python
from mcp_database import create_adapter

# Create adapter for PostgreSQL
adapter = create_adapter("postgresql", url="postgresql://user:pass@localhost:5432/db")

# Connect to database
await adapter.connect()

# Insert data
result = await adapter.insert("users", {"name": "John", "email": "john@example.com"})
print(f"Inserted {result.inserted_count} records")

# Query data
result = await adapter.query("users", filters={"status__isnull": True}, limit=10)
print(f"Found {result.count} records")

# Update data
result = await adapter.update("users", {"status": "active"}, {"name": "John"})
print(f"Updated {result.updated_count} records")

# Delete data
result = await adapter.delete("users", {"status": "inactive"})
print(f"Deleted {result.deleted_count} records")

# Disconnect
await adapter.disconnect()
```

---

## 🗄️ Supported Databases

| Database | Type | Driver | |
|----------|------|--------|-|
| 🐘 **PostgreSQL** | SQL | asyncpg | ✅ |
| 🐬 **MySQL** | SQL | aiomysql | ✅ |
| 📦 **SQLite** | SQL | aiosqlite | ✅ |
| 🍃 **MongoDB** | NoSQL | Motor | ✅ |
| ⚡ **Redis** | NoSQL | redis[asyncio] | ✅ |
| 🔍 **OpenSearch** | NoSQL | opensearch-py | ✅ |
| 🔥 **Supabase** | HTTP | httpx | ✅ |

---

## 📁 Project Structure

```
mcp-database/
├── src/mcp_database/
│   ├── core/              # SDK core modules
│   │   ├── adapter.py     # DatabaseAdapter abstract base class
│   │   ├── models.py      # Pydantic data models
│   │   ├── exceptions.py  # Exception hierarchy
│   │   ├── filters.py     # Filter DSL parsers
│   │   ├── security.py    # SQL security checker
│   │   └── permissions.py # Permission control
│   ├── adapters/          # Database-specific adapters
│   │   ├── sql/           # SQL database adapters
│   │   ├── nosql/         # NoSQL database adapters
│   │   └── http/          # HTTP-based adapters
│   ├── config/            # Configuration management
│   └── utils/             # Utilities (audit logging)
├── tests/                 # Unit and integration tests
├── docs/                  # Documentation
└── pyproject.toml         # Project configuration
```

---

## 🔧 Configuration

### Environment Variables

```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/db
export ENABLE_INSERT=true
export ENABLE_DELETE=true
export ENABLE_UPDATE=true
export DANGEROUS_AGREE=false
```

### Programmatic Configuration

```python
from mcp_database import DatabaseConfig

config = DatabaseConfig(
    url="postgresql://user:pass@localhost:5432/db",
    pool_size=10,
    max_overflow=20,
    connect_timeout=10,
    query_timeout=30,
    max_query_results=1000,
)
```

---

## 🔍 Filter DSL

Powerful query builder with intuitive operators:

| Operator | Meaning | Example |
|:---------|---------|---------|
| `__gt` | Greater than | `{"age__gt": 18}` |
| `__lt` | Less than | `{"price__lt": 100}` |
| `__gte` | ≥ | `{"score__gte": 60}` |
| `__lte` | ≤ | `{"stock__lte": 0}` |
| `__contains` | Contains | `{"name__contains": "John"}` |
| `__startswith` | Starts with | `{"email__startswith": "admin"}` |
| `__endswith` | Ends with | `{"file__endswith": ".pdf"}` |
| `__in` | In list | `{"status__in": ["active"]}` |
| `__isnull` | Is NULL | `{"deleted_at__isnull": True}` |

---

## 🛡️ Security Built-In

#### SQL Injection Protection
All queries use parameterized queries automatically.

```python
await adapter.query("users", filters={"name": "John"})  # Safe ✅
```

#### Dangerous Query Detection
The `SQLSecurityChecker` blocks harmful queries:

```python
from mcp_database.core.security import SQLSecurityChecker

checker = SQLSecurityChecker()
result = checker.check("DROP TABLE users")
# result.is_safe = False
```

---

## 🧪 Testing

### Run Tests

```bash
# Install dependencies
pip install -e ".[dev]"

# Start test databases
docker-compose -f docker-compose.test.yml up -d

# Run tests
pytest              # All tests
pytest --cov=mcp_database  # With coverage
```

---

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [中文文档](docs/README_zh.md) | Chinese README |
| [Architecture](docs/ARCHITECTURE.md) | System design |
| [API Reference](docs/API_REFERENCE.md) | Full API docs |
| [Contributing](docs/CONTRIBUTING.md) | Contribution guide |

---

## 🤝 Contributing

We welcome contributions!

| Action | Description |
|--------|-------------|
| [🐛 Report Bug](../../issues) | Found an issue? Let us know |
| [💡 Request Feature](../../discussions) | Have an idea? Share it |
| [🔧 Submit PR](../../pulls) | Want to contribute code? |

---

## 📄 License

Licensed under [MIT](LICENSE).

---

**Built with ❤️ by Kirky.X**

<a href="../../stargazers">
  <img src="https://img.shields.io/github/stars/Kirky-X/mcp-db?style=social" alt="Stars">
</a>

<sub>© 2026 Kirky.X</sub>
