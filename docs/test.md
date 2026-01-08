# 测试文档 (Test Plan)

**项目名称**: MCP Database SDK  
**版本**: v1.0  
**创建日期**: 2024-01-07  
**文档状态**: ⏳ 待评审

---

## 1. 测试策略概述

### 1.1 测试目标
- 确保所有数据库适配器功能正确
- 验证安全机制有效性
- 保证性能指标达标
- 覆盖边界条件和异常场景

### 1.2 测试层次

```mermaid
graph TB
    A[测试金字塔] --> B[单元测试<br/>80%]
    A --> C[集成测试<br/>15%]
    A --> D[E2E 测试<br/>5%]
    
    B --> B1[适配器单元测试]
    B --> B2[工具函数测试]
    B --> B3[异常处理测试]
    
    C --> C1[数据库集成测试]
    C --> C2[MCP 协议测试]
    
    D --> D1[端到端场景测试]
    
    style B fill:#bfb
```

**测试覆盖率目标**:
- 单元测试: > 80%
- 集成测试: 核心流程 100%
- E2E 测试: 关键场景覆盖

**状态**: ⏳ 待实施

---

## 2. 单元测试

### 2.1 过滤器 DSL 测试 ⏳ 待测试

#### Test-001: 等值过滤器
```python
def test_filter_equal():
    """测试等值过滤器"""
    filters = {"age": 25}
    # SQL: WHERE age = 25
    # MongoDB: {age: 25}
    pass
```
**优先级**: P0  
**状态**: ⏳ 待测试

---

#### Test-002: 比较操作符
```python
@pytest.mark.parametrize("operator,value,expected", [
    ("gt", 18, "age > 18"),
    ("gte", 18, "age >= 18"),
    ("lt", 60, "age < 60"),
    ("lte", 60, "age <= 60"),
])
def test_filter_comparison(operator, value, expected):
    """测试比较操作符"""
    filters = {f"age__{operator}": value}
    pass
```
**状态**: ⏳ 待测试

---

#### Test-003: 字符串操作符
```python
def test_filter_contains():
    """测试字符串包含"""
    filters = {"name__contains": "John"}
    # SQL: name LIKE '%John%'
    # MongoDB: {name: {$regex: "John"}}
    pass

def test_filter_startswith():
    """测试字符串开头匹配"""
    filters = {"email__startswith": "admin"}
    pass

def test_filter_endswith():
    """测试字符串结尾匹配"""
    filters = {"domain__endswith": ".com"}
    pass
```
**状态**: ⏳ 待测试

---

#### Test-004: 列表操作符
```python
def test_filter_in():
    """测试 IN 操作符"""
    filters = {"status__in": ["active", "pending"]}
    pass

def test_filter_not_in():
    """测试 NOT IN 操作符"""
    filters = {"status__not_in": ["deleted"]}
    pass
```
**状态**: ⏳ 待测试

---

#### Test-005: 逻辑操作符
```python
def test_filter_or():
    """测试 OR 逻辑"""
    filters = {
        "__or": [
            {"age": 25},
            {"age": 30}
        ]
    }
    pass

def test_filter_and():
    """测试 AND 逻辑（隐式）"""
    filters = {
        "age__gt": 18,
        "age__lt": 60
    }
    pass

def test_filter_complex_logic():
    """测试复杂逻辑组合"""
    filters = {
        "__or": [
            {"age__gt": 60},
            {
                "age__lt": 18,
                "status": "active"
            }
        ]
    }
    pass
```
**状态**: ⏳ 待测试

---

### 2.2 SQL 适配器测试 ⏳ 待测试

#### Test-101: PostgreSQL 连接
```python
@pytest.mark.asyncio
async def test_postgresql_connect():
    """测试 PostgreSQL 连接"""
    url = "postgresql://test:test@localhost:5432/testdb"
    adapter = SQLAdapter(url)
    await adapter.connect(url)
    assert adapter.engine is not None
    await adapter.disconnect()
```
**状态**: ⏳ 待测试

---

#### Test-102: Insert 操作
```python
@pytest.mark.asyncio
async def test_sql_insert_single():
    """测试单条插入"""
    result = await adapter.insert(
        "users",
        {"name": "Alice", "age": 25}
    )
    assert result.inserted_count == 1
    assert result.inserted_ids[0] is not None

@pytest.mark.asyncio
async def test_sql_insert_batch():
    """测试批量插入"""
    data = [
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 35}
    ]
    result = await adapter.insert("users", data)
    assert result.inserted_count == 2
```
**状态**: ⏳ 待测试

---

#### Test-103: Query 操作
```python
@pytest.mark.asyncio
async def test_sql_query_all():
    """测试查询所有"""
    result = await adapter.query("users")
    assert result.count > 0

@pytest.mark.asyncio
async def test_sql_query_with_filters():
    """测试带过滤器查询"""
    result = await adapter.query(
        "users",
        filters={"age__gt": 18}
    )
    assert all(user["age"] > 18 for user in result.data)

@pytest.mark.asyncio
async def test_sql_query_with_pagination():
    """测试分页查询"""
    result = await adapter.query(
        "users",
        limit=10,
        offset=5
    )
    assert len(result.data) <= 10
```
**状态**: ⏳ 待测试

---

#### Test-104: Update 操作
```python
@pytest.mark.asyncio
async def test_sql_update():
    """测试更新操作"""
    result = await adapter.update(
        "users",
        filters={"name": "Alice"},
        data={"age": 26}
    )
    assert result.updated_count >= 0
```
**状态**: ⏳ 待测试

---

#### Test-105: Delete 操作
```python
@pytest.mark.asyncio
async def test_sql_delete():
    """测试删除操作"""
    result = await adapter.delete(
        "users",
        filters={"name": "Test"}
    )
    assert result.deleted_count >= 0
```
**状态**: ⏳ 待测试

---

### 2.3 MongoDB 适配器测试 ⏳ 待测试

#### Test-201: MongoDB 连接
```python
@pytest.mark.asyncio
async def test_mongodb_connect():
    """测试 MongoDB 连接"""
    url = "mongodb://localhost:27017/testdb"
    adapter = MongoAdapter(url)
    await adapter.connect(url)
    assert adapter.client is not None
    await adapter.disconnect()
```
**状态**: ⏳ 待测试

---

#### Test-202: MongoDB 过滤器转换
```python
def test_mongo_filter_conversion():
    """测试过滤器转换"""
    dsl_filter = {"age__gt": 18}
    mongo_filter = MongoAdapter._convert_filters(dsl_filter)
    assert mongo_filter == {"age": {"$gt": 18}}

def test_mongo_or_logic():
    """测试 OR 逻辑转换"""
    dsl_filter = {
        "__or": [
            {"age": 25},
            {"age": 30}
        ]
    }
    mongo_filter = MongoAdapter._convert_filters(dsl_filter)
    assert "$or" in mongo_filter
```
**状态**: ⏳ 待测试

---

#### Test-203: MongoDB CRUD 操作
```python
@pytest.mark.asyncio
async def test_mongodb_insert():
    """测试 MongoDB 插入"""
    result = await adapter.insert(
        "users",
        {"name": "Alice", "age": 25}
    )
    assert result.inserted_count == 1

@pytest.mark.asyncio
async def test_mongodb_query():
    """测试 MongoDB 查询"""
    result = await adapter.query(
        "users",
        filters={"age__gte": 18}
    )
    assert result.count >= 0
```
**状态**: ⏳ 待测试

---

### 2.4 Redis 适配器测试 ⏳ 待测试

#### Test-301: Redis 连接
```python
@pytest.mark.asyncio
async def test_redis_connect():
    """测试 Redis 连接"""
    url = "redis://localhost:6379/0"
    adapter = RedisAdapter(url)
    await adapter.connect(url)
    assert adapter.client is not None
    await adapter.disconnect()
```
**状态**: ⏳ 待测试

---

#### Test-302: Redis 键前缀模式
```python
@pytest.mark.asyncio
async def test_redis_key_pattern():
    """测试键前缀模式"""
    await adapter.insert(
        "users",
        {"id": "user1", "name": "Alice"}
    )
    # 验证键名为 "users:user1"
    exists = await adapter.client.exists("users:user1")
    assert exists == 1
```
**状态**: ⏳ 待测试

---

#### Test-303: Redis 查询（SCAN）
```python
@pytest.mark.asyncio
async def test_redis_scan_query():
    """测试 SCAN 查询"""
    # 插入测试数据
    for i in range(10):
        await adapter.insert(
            "users",
            {"id": f"user{i}", "name": f"User{i}"}
        )
    
    # 查询所有
    result = await adapter.query("users")
    assert result.count == 10
```
**状态**: ⏳ 待测试

---

### 2.5 安全检查器测试 ⏳ 待测试

#### Test-401: 危险命令检测
```python
def test_detect_drop_table():
    """测试 DROP 命令检测"""
    command = "DROP TABLE users"
    with pytest.raises(PermissionError):
        SQLSecurityChecker.validate(command, None)

def test_detect_truncate():
    """测试 TRUNCATE 命令检测"""
    command = "TRUNCATE TABLE logs"
    with pytest.raises(PermissionError):
        SQLSecurityChecker.validate(command, None)
```
**状态**: ⏳ 待测试

---

#### Test-402: 参数化查询验证
```python
def test_non_parameterized_query():
    """测试非参数化查询检测"""
    command = "SELECT * FROM users WHERE id = " + user_input
    with pytest.raises(QueryError):
        SQLSecurityChecker.validate(command, None)

def test_parameterized_query():
    """测试参数化查询通过"""
    command = "SELECT * FROM users WHERE id = :id"
    params = {"id": 1}
    result = SQLSecurityChecker.validate(command, params)
    assert result.allowed is True
```
**状态**: ⏳ 待测试

---

#### Test-403: SQL 注入测试
```python
@pytest.mark.parametrize("malicious_input", [
    "1; DROP TABLE users--",
    "' OR '1'='1",
    "1 UNION SELECT * FROM passwords",
])
def test_sql_injection_prevention(malicious_input):
    """测试 SQL 注入防护"""
    # 参数化查询应该安全
    command = "SELECT * FROM users WHERE id = :id"
    params = {"id": malicious_input}
    # 不应抛出异常，但实际查询应返回空结果
    result = SQLSecurityChecker.validate(command, params)
    assert result.allowed is True
```
**状态**: ⏳ 待测试

---

### 2.6 异常转换测试 ⏳ 待测试

#### Test-501: 唯一约束错误转换
```python
@pytest.mark.asyncio
async def test_unique_constraint_error():
    """测试唯一约束错误转换"""
    # 插入重复数据
    await adapter.insert("users", {"email": "test@example.com"})
    
    with pytest.raises(IntegrityError) as exc_info:
        await adapter.insert("users", {"email": "test@example.com"})
    
    assert "unique" in str(exc_info.value).lower()
```
**状态**: ⏳ 待测试

---

#### Test-502: 连接错误转换
```python
@pytest.mark.asyncio
async def test_connection_error():
    """测试连接错误转换"""
    url = "postgresql://wrong:wrong@nonexistent:5432/db"
    adapter = SQLAdapter(url)
    
    with pytest.raises(ConnectionError) as exc_info:
        await adapter.connect(url)
    
    assert exc_info.value.database_type == "postgresql"
```
**状态**: ⏳ 待测试

---

### 2.7 权限控制测试 ⏳ 待测试

#### Test-601: INSERT 权限控制
```python
@pytest.mark.asyncio
async def test_insert_disabled(monkeypatch):
    """测试 INSERT 禁用"""
    monkeypatch.setenv("ENABLE_INSERT", "false")
    
    with pytest.raises(PermissionError) as exc_info:
        await adapter.insert("users", {"name": "Alice"})
    
    assert "INSERT" in str(exc_info.value)
```
**状态**: ⏳ 待测试

---

#### Test-602: DELETE 权限控制
```python
@pytest.mark.asyncio
async def test_delete_disabled(monkeypatch):
    """测试 DELETE 禁用"""
    monkeypatch.setenv("ENABLE_DELETE", "false")
    
    with pytest.raises(PermissionError):
        await adapter.delete("users", {"id": 1})
```
**状态**: ⏳ 待测试

---

#### Test-603: EXECUTE 权限控制
```python
@pytest.mark.asyncio
async def test_execute_disabled(monkeypatch):
    """测试 EXECUTE 禁用"""
    monkeypatch.setenv("DANGEROUS_AGREE", "false")
    
    with pytest.raises(PermissionError):
        await adapter.execute("SELECT 1")
```
**状态**: ⏳ 待测试

---

## 3. 集成测试

### 3.1 数据库集成测试矩阵 ⏳ 待测试

#### 测试矩阵设计

| 数据库 | Insert | Query | Update | Delete | Execute | Advanced |
|--------|--------|-------|--------|--------|---------|----------|
| PostgreSQL | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| MySQL | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| SQLite | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| MongoDB | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| Redis | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| OpenSearch | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

**状态**: ⏳ 待测试

---

### 3.2 跨数据库一致性测试 ⏳ 待测试

#### Test-701: 相同过滤器不同数据库
```python
@pytest.mark.parametrize("adapter_type", [
    "postgresql",
    "mysql",
    "sqlite",
    "mongodb"
])
@pytest.mark.asyncio
async def test_filter_consistency(adapter_type):
    """测试过滤器在不同数据库的一致性"""
    adapter = create_adapter(adapter_type)
    
    # 插入相同测试数据
    await insert_test_data(adapter)
    
    # 执行相同查询
    result = await adapter.query(
        "users",
        filters={"age__gt": 18}
    )
    
    # 验证结果一致
    assert all(user["age"] > 18 for user in result.data)
```
**状态**: ⏳ 待测试

---

### 3.3 MCP 协议集成测试 ⏳ 待测试

#### Test-801: MCP 工具调用
```python
@pytest.mark.asyncio
async def test_mcp_query_tool():
    """测试 MCP query 工具"""
    request = {
        "tool": "database_query",
        "arguments": {
            "table": "users",
            "filters": {"age__gt": 18}
        }
    }
    
    response = await mcp_server.handle_tool_call(request)
    assert response["success"] is True
    assert "data" in response
```
**状态**: ⏳ 待测试

---

#### Test-802: MCP 权限错误传递
```python
@pytest.mark.asyncio
async def test_mcp_permission_error():
    """测试 MCP 权限错误传递"""
    request = {
        "tool": "database_insert",
        "arguments": {
            "table": "users",
            "data": {"name": "Alice"}
        }
    }
    
    # ENABLE_INSERT=false
    response = await mcp_server.handle_tool_call(request)
    assert response["success"] is False
    assert "PermissionError" in response["error"]["type"]
```
**状态**: ⏳ 待测试

---

### 3.4 连接池测试 ⏳ 待测试

#### Test-901: 并发连接测试
```python
@pytest.mark.asyncio
async def test_concurrent_queries():
    """测试并发查询"""
    tasks = [
        adapter.query("users", {"id": i})
        for i in range(100)
    ]
    
    results = await asyncio.gather(*tasks)
    assert len(results) == 100
```
**状态**: ⏳ 待测试

---

#### Test-902: 连接泄漏测试
```python
@pytest.mark.asyncio
async def test_connection_leak():
    """测试连接泄漏"""
    initial_pool_size = adapter.engine.pool.size()
    
    # 执行多次查询
    for _ in range(100):
        await adapter.query("users")
    
    # 验证连接池大小未增长
    final_pool_size = adapter.engine.pool.size()
    assert final_pool_size == initial_pool_size
```
**状态**: ⏳ 待测试

---

## 4. 边界条件测试

### 4.1 数据边界测试 ⏳ 待测试

#### Test-1001: 空数据插入
```python
@pytest.mark.asyncio
async def test_insert_empty_data():
    """测试插入空数据"""
    with pytest.raises(ValueError):
        await adapter.insert("users", {})
```
**状态**: ⏳ 待测试

---

#### Test-1002: 大批量插入
```python
@pytest.mark.asyncio
async def test_large_batch_insert():
    """测试大批量插入"""
    data = [{"name": f"User{i}"} for i in range(10000)]
    result = await adapter.insert("users", data)
    assert result.inserted_count == 10000
```
**状态**: ⏳ 待测试

---

#### Test-1003: 查询结果数量限制
```python
@pytest.mark.asyncio
async def test_query_limit():
    """测试查询限制"""
    result = await adapter.query("users", limit=5)
    assert len(result.data) <= 5
```
**状态**: ⏳ 待测试

---

### 4.2 连接异常测试 ⏳ 待测试

#### Test-1101: 数据库不可达
```python
@pytest.mark.asyncio
async def test_database_unreachable():
    """测试数据库不可达"""
    url = "postgresql://localhost:9999/db"
    adapter = SQLAdapter(url)
    
    with pytest.raises(ConnectionError):
        await adapter.connect(url)
```
**状态**: ⏳ 待测试

---

#### Test-1102: 连接超时
```python
@pytest.mark.asyncio
async def test_connection_timeout():
    """测试连接超时"""
    url = "postgresql://slow-host:5432/db?connect_timeout=1"
    adapter = SQLAdapter(url)
    
    with pytest.raises(ConnectionError):
        await adapter.connect(url)
```
**状态**: ⏳ 待测试

---

### 4.3 过滤器边界测试 ⏳ 待测试

#### Test-1201: 空过滤器
```python
@pytest.mark.asyncio
async def test_empty_filters():
    """测试空过滤器"""
    result = await adapter.query("users", filters={})
    # 应返回所有数据
    assert result.count >= 0
```
**状态**: ⏳ 待测试

---

#### Test-1202: 不存在的字段
```python
@pytest.mark.asyncio
async def test_nonexistent_field():
    """测试不存在的字段"""
    with pytest.raises(QueryError):
        await adapter.query("users", filters={"nonexistent_field": "value"})
```
**状态**: ⏳ 待测试

---

## 5. 性能测试

### 5.1 性能基准测试 ⏳ 待测试

#### Test-1301: QPS 测试
```python
@pytest.mark.benchmark
async def test_qps_benchmark():
    """测试 QPS"""
    import time
    
    start = time.time()
    count = 0
    
    while time.time() - start < 1:  # 1秒
        await adapter.query("users", limit=10)
        count += 1
    
    qps = count / (time.time() - start)
    assert qps >= 200  # 目标 200 QPS
```
**状态**: ⏳ 待测试

---

#### Test-1302: 延迟测试
```python
@pytest.mark.benchmark
async def test_latency():
    """测试 P95 延迟"""
    import time
    
    latencies = []
    for _ in range(1000):
        start = time.time()
        await adapter.query("users", limit=10)
        latencies.append(time.time() - start)
    
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    assert p95 < 0.1  # P95 < 100ms
```
**状态**: ⏳ 待测试

---

### 5.2 资源使用测试 ⏳ 待测试

#### Test-1401: 内存使用
```python
@pytest.mark.benchmark
async def test_memory_usage():
    """测试内存使用"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 执行 1000 次查询
    for _ in range(1000):
        await adapter.query("users")
    
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = final_memory - initial_memory
    
    assert memory_increase < 50  # 内存增长 < 50MB
```
**状态**: ⏳ 待测试

---

## 6. E2E 测试场景

### 6.1 用户注册流程 ⏳ 待测试

#### Test-1501: 完整注册流程
```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_user_registration_flow():
    """测试用户注册完整流程"""
    # 1. 检查用户是否存在
    existing = await adapter.query(
        "users",
        filters={"email": "newuser@example.com"}
    )
    assert existing.count == 0
    
    # 2. 插入新用户
    result = await adapter.insert(
        "users",
        {
            "email": "newuser@example.com",
            "name": "New User",
            "created_at": datetime.now()
        }
    )
    assert result.inserted_count == 1
    
    # 3. 验证用户已插入
    user = await adapter.query(
        "users",
        filters={"email": "newuser@example.com"}
    )
    assert user.count == 1
```
**状态**: ⏳ 待测试

---

### 6.2 数据迁移场景 ⏳ 待测试

#### Test-1502: 跨数据库数据迁移
```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_data_migration():
    """测试跨数据库数据迁移"""
    source = SQLAdapter("postgresql://...")
    target = MongoAdapter("mongodb://...")
    
    # 1. 从 PostgreSQL 读取
    data = await source.query("users")
    
    # 2. 写入 MongoDB
    result = await target.insert("users", data.data)
    
    # 3. 验证数据一致
    assert result.inserted_count == data.count
```
**状态**: ⏳ 待测试

---

## 7. 测试环境配置

### 7.1 Docker Compose 配置 ⏳ 待配置

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: test
      POSTGRES_DB: testdb
    ports:
      - "5432:5432"
  
  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: test
      MYSQL_DATABASE: testdb
    ports:
      - "3306:3306"
  
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  opensearch:
    image: opensearchproject/opensearch:2
    environment:
      - discovery.type=single-node
      - DISABLE_SECURITY_PLUGIN=true
    ports:
      - "9200:9200"
```

**状态**: ⏳ 待配置

---

### 7.2 Pytest 配置 ⏳ 待配置

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    asyncio: async tests
    integration: integration tests
    e2e: end-to-end tests
    benchmark: performance tests

addopts = 
    --cov=mcp_database
    --cov-report=html
    --cov-report=term
    -v
```

**状态**: ⏳ 待配置

---

## 8. 测试覆盖率要求

### 8.1 覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| core/ | 90% | ⏳ 待测试 |
| adapters/ | 85% | ⏳ 待测试 |
| config/ | 80% | ⏳ 待测试 |
| utils/ | 80% | ⏳ 待测试 |
| server.py | 90% | ⏳ 待测试 |

**总体目标**: > 80%  
**状态**: ⏳ 待达成

---

## 9. 测试执行计划

### 9.1 测试阶段

| 阶段 | 测试内容 | 时间 | 状态 |
|------|---------|------|------|
| Phase 1 | 单元测试 (核心模块) | Week 1-2 | ⏳ 待执行 |
| Phase 2 | 集成测试 (数据库) | Week 3-4 | ⏳ 待执行 |
| Phase 3 | 性能测试 | Week 5 | ⏳ 待执行 |
| Phase 4 | E2E 测试 | Week 6 | ⏳ 待执行 |
| Phase 5 | 回归测试 | Week 7 | ⏳ 待执行 |

---

## 10. 缺陷管理

### 10.1 缺陷严重级别

| 级别 | 定义 | 响应时间 |
|------|------|---------|
| P0 - Critical | 核心功能不可用 | 24小时 |
| P1 - High | 重要功能受影响 | 3天 |
| P2 - Medium | 次要功能问题 | 1周 |
| P3 - Low | 优化建议 | 2周 |

**状态**: ⏳ 待执行

---

## 附录

### A. 测试数据准备脚本
```python
# test_fixtures.py
@pytest.fixture
async def sample_users():
    """示例用户数据"""
    return [
        {"name": "Alice", "age": 25, "email": "alice@example.com"},
        {"name": "Bob", "age": 30, "email": "bob@example.com"},
        {"name": "Charlie", "age": 35, "email": "charlie@example.com"}
    ]
```

### B. 性能测试工具
- pytest-benchmark: 性能基准测试
- locust: 负载测试
- psutil: 资源监控
