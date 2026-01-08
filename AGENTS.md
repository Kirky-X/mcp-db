# AGENTS.md

This file provides guidance for AI agents working in this repository.

## Build/Lint/Test Commands

### Installation
```bash
pip install -e ".[dev]"  # Install all dependencies including dev tools
```

### Testing
```bash
pytest                              # Run all tests
pytest --cov=mcp_database           # Run with coverage report
pytest tests/test_adapter.py        # Run single test file
pytest tests/test_adapter.py::test_postgresql_connect  # Run single test function
pytest -xvs tests/test_adapters/test_sql_base.py::test_postgresql_crud  # Async test
pytest tests/benchmark/test_performance.py  # Performance benchmarks
```

### Code Quality
```bash
ruff format .                        # Format code
ruff check .                         # Lint code
mypy src/mcp_database                # Type checking
ruff check . && mypy src/mcp_database  # All checks
```

### Database for Tests
```bash
docker-compose -f docker-compose.test.yml up -d  # Start test databases
```

## Code Style Guidelines

### Imports
- Use absolute imports: `from mcp_database.core.models import X`
- Sort imports: stdlib → third-party → local (ruff handles this)
- Group related imports together
- Avoid wildcard imports

### Formatting
- Line length: 100 characters
- Use ruff for automatic formatting
- Use black-compatible formatting
- Put imports in alphabetical order within groups

### Type Annotations
- **Required for all public functions and methods** (mypy `disallow_untyped_defs`)
- Use Python 3.10+ syntax: `dict[str, Any]` instead of `Dict[str, Any]`
- Use `| None` instead of `Optional[]` for union types
- All async methods must have return type annotations
- Private attributes in dataclasses should be typed

Example:
```python
async def query(
    self, table: str, filters: dict[str, Any] | None = None, limit: int | None = None
) -> QueryResult:
    ...
```

### Naming Conventions
- **Classes**: PascalCase (`DatabaseAdapter`, `SQLSecurityChecker`)
- **Functions/variables**: snake_case (`get_capabilities`, `security_check`)
- **Constants**: UPPER_SNAKE_CASE (`FORBIDDEN_KEYWORDS`, `DANGEROUS_WITHOUT_WHERE`)
- **Private attributes**: leading underscore (`_config`, `_engine`)
- **Type variables**: PascalCase (`T`, `K`, `V`)
- Use descriptive names: `inserted_count` not `ic`

### Error Handling
- Always use specific exception types from `mcp_database.core.exceptions`:
  - `DatabaseError` (base)
  - `ConnectionError`, `QueryError`, `PermissionError`, `IntegrityError`, `TimeoutError`
- Use `ExceptionTranslator.translate()` to convert database-specific exceptions
- Catch specific exceptions, not `BaseException`
- Document raised exceptions in docstrings

Example:
```python
try:
    result = await session.execute(stmt)
except Exception as e:
    translated = ExceptionTranslator.translate(e, self._database_type)
    raise translated
```

### Docstrings
- Use triple-quoted strings for all public classes and methods
- Follow Google style for docstrings
- Document Args, Returns, and Raises sections
- Keep docstrings concise but informative

### Security
- **Never** concatenate user input into SQL queries
- **Always** use parameterized queries (`:param` format)
- DELETE/UPDATE operations **must** have WHERE clauses (checked by SQLSecurityChecker)
- The `execute` interface should only be exposed when `DANGEROUS_AGREE=true`

### Null Value Query Support
All adapters now support null value queries with consistent semantics:
- **SQL**: `status__isnull=true` → `"status IS NULL"`, `status__isnull=false` → `"status IS NOT NULL"`
- **MongoDB**: `status__isnull=true` → `{"status": {"$exists": False}}`, `status__isnull=false` → `{"status": {"$exists": True}}`
- **Redis**: `status__isnull=true` → field_value is None, `status__isnull=false` → field_value is not None

Usage examples:
```python
# Find records with null status
await adapter.query("users", filters={"status__isnull": True})

# Find records with non-null status  
await adapter.query("users", filters={"status__isnull": False})
```

### Async/Await
- All database operations are async (uses asyncio, SQLAlchemy 2.0 async API)
- MongoDB uses Motor async driver
- Redis uses `redis[asyncio]` async client
- Use `pytest-asyncio` with `@pytest.mark.asyncio` for tests

### Pydantic Models
- Use Pydantic v2 models for all data structures
- Use `@validate_call` for function parameter validation
- Return Pydantic models from all adapter methods

### Project Structure
- `src/mcp_database/core/`: SDK core (adapter, models, exceptions, filters, security, permissions)
- `src/mcp_database/adapters/`: Database-specific adapters (sql/, nosql/)
- `src/mcp_database/config/`: Configuration management
- `src/mcp_database/utils/`: Utilities (audit logging)
- `tests/`: Unit and integration tests
- Inherit from `DatabaseAdapter` abstract base class for new adapters
- Implement all abstract methods: `connect`, `disconnect`, `insert`, `delete`, `update`, `query`, `execute`, `advanced_query`, `get_capabilities`
