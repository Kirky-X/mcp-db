# MCP Database SDK

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-passing-green.svg)]()

**A unified database operation SDK for Large Language Models.**

[🏠 Home](README.md) • [📖 Docs](docs/README_zh.md) • [🔧 API](docs/API_REFERENCE.md) • [🤝 Contributing](docs/CONTRIBUTING.md)

---

</div>

## 🌟 Key Features

<table>
<tr>
<td width="50%">

### 🔄 Unified Interface
- **Consistent API** across 7 databases
- **Async-first** design with modern Python
- **CRUD operations** made simple
- **Filter DSL** for flexible queries

</td>
<td width="50%">

### 🔒 Enterprise Security
- **SQL injection** prevention
- **Permission control** system
- **Audit logging** support
- **Table validation**

</td>
</tr>
<tr>
<td width="50%">

### 🗄️ Multi-Database Support
- **PostgreSQL**, MySQL, SQLite
- **MongoDB**, Redis
- **OpenSearch**, Supabase
- **Adapter pattern** for extensibility

</td>
<td width="50%">

### ⚡ High Performance
- **Async operations** throughout
- **Connection pooling**
- **SQLAlchemy 2.0** async API
- **Motor** async driver for MongoDB

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Installation

```bash
pip install -e ".[dev]"
```

### Basic Usage

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

## 📦 Supported Databases

| Database | Type | Async Driver | Status |
|----------|------|--------------|--------|
| PostgreSQL | SQL | asyncpg | ✅ Stable |
| MySQL | SQL | aiomysql | ✅ Stable |
| SQLite | SQL | aiosqlite | ✅ Stable |
| MongoDB | NoSQL | Motor | ✅ Stable |
| Redis | NoSQL | redis[asyncio] | ✅ Stable |
| OpenSearch | NoSQL | opensearch-py | ✅ Stable |
| Supabase | HTTP | httpx | ✅ Stable |

---

## 📂 Project Structure

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

## 📖 Filter DSL

The SDK provides a flexible filter DSL for building queries:

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `gt` | Greater than | `{"age__gt": 18}` |
| `lt` | Less than | `{"price__lt": 100}` |
| `gte` | Greater than or equal | `{"score__gte": 60}` |
| `lte` | Less than or equal | `{"stock__lte": 0}` |
| `contains` | Contains substring | `{"name__contains": "John"}` |
| `startswith` | Starts with prefix | `{"email__startswith": "admin"}` |
| `endswith` | Ends with suffix | `{"file__endswith": ".pdf"}` |
| `in` | Value in list | `{"status__in": ["active", "pending"]}` |
| `not_in` | Value not in list | `{"role__not_in": ["admin"]}` |
| `isnull` | Is NULL | `{"deleted_at__isnull": True}` |
| `notnull` | Is NOT NULL | `{"created_at__notnull": True}` |

---

## 🛡️ Security Features

### SQL Injection Prevention

All queries use parameterized queries to prevent SQL injection:

```python
# Safe - using parameterized queries
await adapter.query("users", filters={"name": "John"})

# The SDK automatically uses parameterized queries
# instead of string concatenation
```

### Dangerous Query Detection

The `SQLSecurityChecker` detects and blocks dangerous queries:

```python
from mcp_database.core.security import SQLSecurityChecker

checker = SQLSecurityChecker()
result = checker.check("DROP TABLE users")
# result.is_safe = False
# result.reason = "禁止的关键字: DROP"
```

### Permission Control

Operations can be restricted based on permissions:

```python
from mcp_database.core.permissions import check_execute_permission

class MyAdapter(SQLAdapter):
    @check_execute_permission
    async def execute(self, query: str, params: dict = None):
        # Only executes if permission is granted
        pass
```

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Start test databases
docker-compose -f docker-compose.test.yml up -d

# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_database

# Run specific test file
pytest tests/test_adapter.py

# Run single test function
pytest tests/test_adapter.py::test_postgresql_connect
```

---

## 📚 Documentation

- [README (English)](README.md)
- [README (中文)](docs/README_zh.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Contributing Guide](docs/CONTRIBUTING.md)

---

## 🤝 Contributing

<div align="center">

### 💖 We Love Contributors!

</div>

<table>
<tr>
<td width="33%" align="center">

### 🐛 Report Bugs
Found a bug?<br>
[Create an Issue](../../issues)

</td>
<td width="33%" align="center">

### 💡 Request Features
Have an idea?<br>
[Start a Discussion](../../discussions)

</td>
<td width="33%" align="center">

### 🔧 Submit PRs
Want to contribute?<br>
[Fork & PR](../../pulls)

</td>
</tr>
</table>

---

## 📄 License

<div align="center">

This project is licensed under the MIT License.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🙏 Acknowledgments

<div align="center">

### Built With Amazing Tools

<table>
<tr>
<td align="center" width="25%">
<b>Python</b>
</td>
<td align="center" width="25%">
<b>SQLAlchemy</b>
</td>
<td align="center" width="25%">
<b>Motor</b>
</td>
<td align="center" width="25%">
<b>Pydantic</b>
</td>
</tr>
</table>

</div>

---

<div align="center">

### 💝 Support This Project

If you find this project useful, please consider giving it a ⭐️!

**Built with ❤️ by Kirky.X**

[⬆ Back to Top](#-mcp-database-sdk)

---

<sub>© 2026 Kirky.X. All rights reserved.</sub>

</div>
