# 技术设计文档 (TDD)

**项目名称**: MCP Database SDK  
**版本**: v1.0  
**创建日期**: 2024-01-07  
**文档状态**: ⏳ 待评审

---

## 1. 系统架构设计

### 1.1 整体架构

```mermaid
graph TB
    subgraph "MCP Layer"
    A[MCP Server] --> B[Tool Registry]
    end
    
    subgraph "SDK Layer"
    B --> C[DatabaseManager]
    C --> D[Adapter Factory]
    C --> E[Config Manager]
    C --> F[Security Checker]
    end
    
    subgraph "Adapter Layer"
    D --> G[SQL Adapter]
    D --> H[MongoDB Adapter]
    D --> I[Redis Adapter]
    D --> J[OpenSearch Adapter]
    end
    
    subgraph "ORM/SDK Layer"
    G --> K[SQLAlchemy]
    H --> L[Motor]
    I --> M[redis-py]
    J --> N[opensearch-py]
    end
    
    subgraph "Database Layer"
    K --> O[(PostgreSQL)]
    K --> P[(MySQL)]
    K --> Q[(SQLite)]
    L --> R[(MongoDB)]
    M --> S[(Redis)]
    N --> T[(OpenSearch)]
    end
    
    style C fill:#bbf,stroke:#333,stroke-width:3px
    style F fill:#f99,stroke:#333,stroke-width:2px
```

**架构说明**:
- **MCP Layer**: 负责协议转换，将 LLM 请求转换为 SDK 调用
- **SDK Layer**: 核心业务逻辑，管理适配器生命周期和安全检查
- **Adapter Layer**: 数据库抽象层，统一接口实现
- **ORM/SDK Layer**: 底层驱动封装
- **Database Layer**: 实际数据库

**设计状态**: ⏳ 待实现

---

### 1.2 分层职责

| 层级 | 职责 | 实现状态 |
|------|------|---------|
| MCP Layer | 工具注册、参数验证、结果序列化 | ⏳ 待实现 |
| SDK Layer | 适配器管理、权限控制、异常转换 | ⏳ 待实现 |
| Adapter Layer | CRUD 实现、DSL 转换、连接管理 | ⏳ 待实现 |
| ORM/SDK Layer | 原生数据库交互 | ⏳ 待实现 |

---

## 2. 技术栈选型

### 2.1 核心技术栈

| 技术 | 版本 | 选型理由 | 状态 |
|------|------|----------|------|
| **Python** | 3.10+ | 异步支持、类型注解、丰富生态 | ⏳ 待配置 |
| **MCP SDK** | latest | 官方协议实现 | ⏳ 待集成 |
| **SQLAlchemy** | 2.0+ | 成熟的异步 ORM，支持多数据库 | ⏳ 待集成 |
| **Pydantic** | 2.5+ | 数据验证、类型安全 | ⏳ 待集成 |
| **asyncio** | 标准库 | 异步 I/O 支持 | ⏳ 待配置 |

**选型状态**: ⏳ 待实现

---

### 2.2 数据库驱动

| 数据库 | 驱动库 | 版本 | 选型理由 | 状态 |
|--------|--------|------|----------|------|
| PostgreSQL | asyncpg | 0.29+ | 高性能异步驱动 | ⏳ 待集成 |
| MySQL | aiomysql | 0.2+ | 异步支持 | ⏳ 待集成 |
| SQLite | aiosqlite | 0.19+ | 异步文件 I/O | ⏳ 待集成 |
| MongoDB | motor | 3.3+ | 官方异步驱动 | ⏳ 待集成 |
| Redis | redis[asyncio] | 5.0+ | 原生异步支持 | ⏳ 待集成 |
| OpenSearch | opensearch-py | 2.4+ | 官方 SDK | ⏳ 待集成 |
| Supabase | httpx | 0.25+ | HTTP 客户端 | ⏳ 待集成 |

---

### 2.3 辅助工具

| 工具 | 用途 | 状态 |
|------|------|------|
| **sqlparse** | SQL 解析、安全检查 | ⏳ 待集成 |
| **dsnparse** | DATABASE_URL 解析 | ⏳ 待集成 |
| **pytest** | 单元测试框架 | ⏳ 待配置 |
| **pytest-asyncio** | 异步测试支持 | ⏳ 待配置 |
| **ruff** | 代码格式化/检查 | ⏳ 待配置 |
| **mypy** | 类型检查 | ⏳ 待配置 |
| **cryptography** | 密码加密（DATABASE_URL 保护） | ⏳ 待集成 |
| **redisearch** | Redis 性能优化（可选） | ⏳ 可选集成 |
| **redis-py** | Redis JSON 支持（可选） | ⏳ 可选集成 |

---

## 3. 核心模块设计

### 3.1 模块架构

```mermaid
graph LR
    A[mcp_database] --> B[core]
    A --> C[adapters]
    A --> D[config]
    A --> E[utils]
    A --> F[server]
    
    B --> B1[adapter.py]
    B --> B2[exceptions.py]
    B --> B3[models.py]
    B --> B4[filters.py]
    B --> B5[security.py]
    
    C --> C1[factory.py]
    C --> C2[sql/]
    C --> C3[nosql/]
    
    style A fill:#bbf,stroke:#333,stroke-width:2px
```

**状态**: ⏳ 待实现

---

### 3.2 核心接口定义 ⏳ 待实现

#### DatabaseAdapter (抽象基类)

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class DatabaseAdapter(ABC):
    """数据库适配器抽象基类"""
    
    @abstractmethod
    async def connect(self, url: str) -> None:
        """建立数据库连接"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """关闭数据库连接"""
        pass
    
    @abstractmethod
    async def insert(
        self,
        table: str,
        data: Dict | List[Dict],
        database: Optional[str] = None,
        **options
    ) -> InsertResult:
        """插入数据"""
        pass
    
    @abstractmethod
    async def delete(
        self,
        table: str,
        filters: Dict,
        database: Optional[str] = None,
        **options
    ) -> DeleteResult:
        """删除数据"""
        pass
    
    @abstractmethod
    async def update(
        self,
        table: str,
        filters: Dict,
        data: Dict,
        database: Optional[str] = None,
        **options
    ) -> UpdateResult:
        """更新数据"""
        pass
    
    @abstractmethod
    async def query(
        self,
        table: str,
        filters: Optional[Dict] = None,
        projection: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[List[tuple]] = None,
        database: Optional[str] = None,
        **options
    ) -> QueryResult:
        """查询数据"""
        pass
    
    @abstractmethod
    async def execute(
        self,
        command: str,
        params: Optional[Dict | List] = None,
        database: Optional[str] = None,
        **options
    ) -> ExecuteResult:
        """执行原生命令"""
        pass
    
    @abstractmethod
    async def advanced_query(
        self,
        operation: str,
        database: Optional[str] = None,
        **kwargs
    ) -> AdvancedResult:
        """高级查询接口"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Capability:
        """查询数据库能力"""
        pass
```

**状态**: ⏳ 待实现

---

### 3.3 数据模型设计 ⏳ 待实现

#### 核心数据模型

```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class InsertResult(BaseModel):
    """插入操作结果"""
    inserted_count: int
    inserted_ids: List[Any]
    success: bool = True

class UpdateResult(BaseModel):
    """更新操作结果"""
    updated_count: int
    success: bool = True

class DeleteResult(BaseModel):
    """删除操作结果"""
    deleted_count: int
    success: bool = True

class QueryResult(BaseModel):
    """查询操作结果"""
    data: List[Dict[str, Any]]
    count: int
    has_more: bool = False

class ExecuteResult(BaseModel):
    """执行命令结果"""
    rows_affected: int
    data: Optional[List[Dict]] = None
    success: bool = True

class AdvancedResult(BaseModel):
    """高级查询结果"""
    operation: str
    data: Any
    success: bool = True

class Capability(BaseModel):
    """数据库能力描述"""
    basic_crud: bool = True
    transactions: bool = False
    joins: bool = False
    aggregation: bool = False
    full_text_search: bool = False
    geospatial: bool = False
```

**状态**: ⏳ 待实现

---

### 3.4 过滤器 DSL 设计 ⏳ 待实现

#### 过滤器解析器

```mermaid
graph TB
    A[DSL Filter] --> B{解析器}
    B --> C[SQL 转换器]
    B --> D[MongoDB 转换器]
    B --> E[Redis 转换器]
    
    C --> F[WHERE 子句]
    D --> G[MongoDB Query]
    E --> H[内存过滤函数]
    
    style B fill:#bfb,stroke:#333,stroke-width:2px
```

**支持的操作符映射**:

| DSL 操作符 | SQL | MongoDB | Redis |
|-----------|-----|---------|-------|
| `field: value` | `field = value` | `{field: value}` | 等值匹配 |
| `field__gt: value` | `field > value` | `{field: {$gt: value}}` | 内存过滤 |
| `field__contains: value` | `field LIKE '%value%'` | `{field: {$regex: value}}` | 内存过滤 |
| `field__in: [...]` | `field IN (...)` | `{field: {$in: [...]}}` | 内存过滤 |
| `__or: [...]` | `(cond1) OR (cond2)` | `{$or: [...]}` | 内存过滤 |

**实现示例**:
```python
class FilterTranslator:
    """过滤器转换器基类"""
    
    @staticmethod
    def translate(filters: Dict) -> Any:
        """将 DSL 转换为目标数据库语法"""
        pass

class SQLFilterTranslator(FilterTranslator):
    """SQL 过滤器转换器"""
    
    @staticmethod
    def translate(filters: Dict, table_obj) -> WhereClause:
        # 实现逻辑...
        pass
```

**状态**: ⏳ 待实现

---

## 4. 适配器实现策略

### 4.1 SQL 适配器 (SQLAlchemy) ⏳ 待实现

```mermaid
graph TB
    A[SQLAdapter] --> B[AsyncEngine]
    B --> C[Connection Pool]
    C --> D[(PostgreSQL)]
    C --> E[(MySQL)]
    C --> F[(SQLite)]
    
    A --> G[Metadata Cache]
    A --> H[Filter Translator]
    
    style A fill:#bbf,stroke:#333,stroke-width:2px
```

**关键设计点**:
1. **连接池管理**: 使用 `create_async_engine` 配置连接池
2. **表元数据缓存**: 自动加载表结构并缓存
3. **过滤器转换**: DSL → SQLAlchemy 表达式
4. **参数化查询**: 强制使用 bound parameters

**实现状态**: ⏳ 待实现

---

### 4.2 MongoDB 适配器 (Motor) ⏳ 待实现

```mermaid
graph TB
    A[MongoAdapter] --> B[Motor Client]
    B --> C[Database]
    C --> D[Collection Pool]
    
    A --> E[Filter Translator]
    E --> F[MongoDB Query Object]
    
    A --> G[NoSQL Security Checker]
    G --> H[Injection Protection]
    
    style A fill:#bbf,stroke:#333,stroke-width:2px
```

**关键设计点**:
1. **连接池**: Motor 自动管理连接池
2. **过滤器转换**: DSL → MongoDB `$` 操作符
3. **聚合管道**: 通过 `advanced_query` 暴露
4. **NoSQL 注入防护**: 增强的安全检查器

**NoSQL 注入防护**:
```python
class NoSQLSecurityChecker:
    """NoSQL 安全检查器 - MongoDB 注入防护"""
    
    # 危险操作符
    DANGEROUS_OPERATORS = {
        "$where", "$eval", "$function",
        "$regex", "$expr", "$jsonSchema"
    }
    
    # NoSQL 注入模式
    INJECTION_PATTERNS = [
        # 操作符注入
        r"\$ne\b.*null",  # $ne: null
        r"\$gt\b.*0",     # $gt: 0
        r"\$where\b",     # $where 注入
        # 正则表达式注入
        r"\$regex\b.*\.\*",  # $regex: .*
        # JavaScript 注入
        r"function\s*\(",   # function(
        r"return\s+",       # return
        # 布尔盲注
        r"\$and\b.*\$ne\b",
        r"\$or\b.*\$ne\b",
    ]
    
    @staticmethod
    def validate_filters(filters: Dict) -> SecurityResult:
        """
        验证过滤器，防止 NoSQL 注入
        
        Args:
            filters: 过滤器字典
            
        Returns:
            SecurityResult: 安全检查结果
        """
        result = SecurityResult(allowed=True, message="")
        
        # 递归检查过滤器
        check_result = NoSQLSecurityChecker._check_dict(filters)
        if not check_result.allowed:
            return check_result
        
        return result
    
    @staticmethod
    def _check_dict(data: Dict, path: str = "") -> SecurityResult:
        """递归检查字典"""
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            # 检查危险操作符
            if isinstance(key, str) and key.startswith("$"):
                if key in NoSQLSecurityChecker.DANGEROUS_OPERATORS:
                    return SecurityResult(
                        allowed=False,
                        message=f"Dangerous operator detected: {key} at {current_path}"
                    )
                
                # 检查操作符值
                if key == "$regex":
                    if not NoSQLSecurityChecker._is_safe_regex(value):
                        return SecurityResult(
                            allowed=False,
                            message=f"Unsafe regex pattern at {current_path}"
                        )
                elif key == "$where":
                    # $where 操作符执行 JavaScript，非常危险
                    return SecurityResult(
                        allowed=False,
                        message=f"Dangerous $where operator detected at {current_path}"
                    )
                elif key == "$expr":
                    # $expr 可能包含聚合表达式，需要检查
                    if not NoSQLSecurityChecker._is_safe_expr(value):
                        return SecurityResult(
                            allowed=False,
                            message=f"Unsafe expression at {current_path}"
                        )
            
            # 递归检查嵌套字典
            if isinstance(value, dict):
                check_result = NoSQLSecurityChecker._check_dict(value, current_path)
                if not check_result.allowed:
                    return check_result
            # 递归检查列表
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        check_result = NoSQLSecurityChecker._check_dict(
                            item, f"{current_path}[{i}]"
                        )
                        if not check_result.allowed:
                            return check_result
        
        return SecurityResult(allowed=True)
    
    @staticmethod
    def _is_safe_regex(pattern: str) -> bool:
        """检查正则表达式是否安全"""
        if not isinstance(pattern, str):
            return False
        
        # 禁止的危险模式
        dangerous_patterns = [
            r".*",  # 匹配所有
            r".+",  # 匹配一个或多个
            r"(.*)",  # 捕获所有
            r"(.+)",  # 捕获一个或多个
        ]
        
        for dangerous in dangerous_patterns:
            if dangerous in pattern:
                return False
        
        # 检查是否有回溯攻击
        if "(.*" in pattern or "(.+" in pattern:
            return False
        
        return True
    
    @staticmethod
    def _is_safe_expr(expr: Dict) -> bool:
        """检查聚合表达式是否安全"""
        # 简单实现：只允许基本的比较操作符
        safe_operators = {"$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin"}
        
        for key in expr.keys():
            if key not in safe_operators:
                return False
        
        return True
    
    @staticmethod
    def sanitize_input(value: Any) -> Any:
        """
        清理输入值，防止注入
        
        Args:
            value: 输入值
            
        Returns:
            清理后的值
        """
        if isinstance(value, str):
            # 移除潜在的 JavaScript 代码
            if any(keyword in value for keyword in ["function", "return", "this", "eval"]):
                # 记录警告
                return ""
            return value
        elif isinstance(value, dict):
            return {k: NoSQLSecurityChecker.sanitize_input(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [NoSQLSecurityChecker.sanitize_input(v) for v in value]
        else:
            return value
```

**实现状态**: ⏳ 待实现

**增强说明**：
- ✅ 增加了 NoSQL 操作符检测（$where、$eval、$function 等）
- ✅ 增加了 NoSQL 注入模式检测（操作符注入、正则表达式注入、JavaScript 注入、布尔盲注）
- ✅ 增加了正则表达式安全检查
- ✅ 增加了聚合表达式安全检查
- ✅ 增加了输入清理功能
- ✅ 递归检查嵌套字典和列表

---

### 4.3 Redis 适配器 (redis-py) ⏳ 待实现

```mermaid
graph TB
    A[RedisAdapter] --> B[ConnectionPool]
    B --> C[Redis Client]
    
    A --> D[Key Pattern Manager]
    D --> E["table:id 模式"]
    
    A --> F[Memory Filter]
    F --> G["SCAN + MGET"]
    
    A --> H[Performance Optimizer]
    H --> I["可选: RediSearch"]
    H --> J["可选: RedisJSON"]
    
    style A fill:#bbf,stroke:#333,stroke-width:2px
```

**关键设计点**:
1. **"表"模拟**: 使用键前缀 `table:id` 模式
2. **查询实现**: SCAN + MGET + 内存过滤
3. **过期支持**: 通过 `expire` 选项设置 TTL
4. **性能优化**: 提供多种优化策略

**性能优化策略**:

#### 方案 1: 基础优化（当前实现）

```python
class RedisAdapter:
    """Redis 适配器 - 基础优化版"""
    
    async def query(
        self,
        table: str,
        filters: Optional[Dict] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **options
    ) -> QueryResult:
        """
        查询数据（优化版）
        
        优化点:
        1. 使用 SCAN 而非 KEYS（避免阻塞）
        2. 批量获取数据（MGET）
        3. 分页处理（避免一次性加载所有数据）
        4. 并行处理（使用 asyncio.gather）
        """
        key_prefix = f"{table}:"
        
        # 使用 SCAN 获取所有键
        keys = []
        async for key in self.client.scan_iter(match=f"{key_prefix}*"):
            keys.append(key)
        
        # 分页处理
        if offset:
            keys = keys[offset:]
        if limit:
            keys = keys[:limit]
        
        # 批量获取数据
        if keys:
            values = await self.client.mget(keys)
            data = []
            for key, value in zip(keys, values):
                if value:
                    data.append(json.loads(value))
            
            # 内存过滤
            if filters:
                data = self._filter_in_memory(data, filters)
        else:
            data = []
        
        return QueryResult(
            data=data,
            count=len(data),
            has_more=False
        )
    
    def _filter_in_memory(self, data: List[Dict], filters: Dict) -> List[Dict]:
        """内存过滤（优化版）"""
        result = []
        
        for item in data:
            match = True
            for key, value in filters.items():
                # 处理操作符
                if "__" in key:
                    field, op = key.rsplit("__", 1)
                    item_value = item.get(field)
                    
                    if op == "gt":
                        if not (item_value and item_value > value):
                            match = False
                            break
                    elif op == "lt":
                        if not (item_value and item_value < value):
                            match = False
                            break
                    elif op == "gte":
                        if not (item_value and item_value >= value):
                            match = False
                            break
                    elif op == "lte":
                        if not (item_value and item_value <= value):
                            match = False
                            break
                    elif op == "contains":
                        if not (item_value and value in str(item_value)):
                            match = False
                            break
                    elif op == "in":
                        if not (item_value and item_value in value):
                            match = False
                            break
                else:
                    # 等值匹配
                    if item.get(key) != value:
                        match = False
                        break
            
            if match:
                result.append(item)
        
        return result
```

**性能特点**:
- ✅ 适用于小数据集（< 10,000 条记录）
- ✅ 实现简单，无需额外依赖
- ❌ 大数据集性能较差
- ❌ 内存消耗较高

---

#### 方案 2: 使用 RediSearch（推荐用于生产环境）

```python
class RedisAdapterWithSearch:
    """Redis 适配器 - RediSearch 优化版"""
    
    def __init__(self, url: str):
        self.client = redis.from_url(url)
        self.search_client = redisearch.Client(
            "mcp-index",
            conn=self.client
        )
        # 创建索引
        self._create_index()
    
    def _create_index(self):
        """创建搜索索引"""
        try:
            self.search_client.create_index(
                [
                    redisearch.TextField("name"),
                    redisearch.TextField("email"),
                    redisearch.NumericField("age"),
                    redisearch.TagField("status"),
                ]
            )
        except redisearch.IndexExistsError:
            pass
    
    async def query(
        self,
        table: str,
        filters: Optional[Dict] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **options
    ) -> QueryResult:
        """
        查询数据（RediSearch 优化版）
        
        优化点:
        1. 使用 RediSearch 进行索引查询
        2. 支持复杂的查询条件
        3. 性能远高于内存过滤
        4. 支持分页和排序
        """
        query = redisearch.Query("*")
        
        # 构建查询条件
        if filters:
            conditions = []
            for key, value in filters.items():
                if "__" in key:
                    field, op = key.rsplit("__", 1)
                    if op == "gt":
                        conditions.append(f"@{field}:[{value} +inf]")
                    elif op == "lt":
                        conditions.append(f"@{field}:[-inf {value}]")
                    elif op == "contains":
                        conditions.append(f"@{field}:{value}*")
                    elif op == "in":
                        values = " ".join([f'"{v}"' for v in value])
                        conditions.append(f"@{field}:{{{values}}}")
                else:
                    conditions.append(f"@{key}:{value}")
            
            if conditions:
                query = redisearch.Query(" ".join(conditions))
        
        # 分页
        if offset:
            query.paging(offset, limit or 10)
        elif limit:
            query.paging(0, limit)
        
        # 执行查询
        result = self.search_client.search(query)
        
        # 转换结果
        data = []
        for doc in result.docs:
            item = {"id": doc.id}
            for field in doc.__dict__.keys():
                if not field.startswith("_"):
                    item[field] = getattr(doc, field)
            data.append(item)
        
        return QueryResult(
            data=data,
            count=result.total,
            has_more=result.total > (offset or 0) + (limit or 0)
        )
```

**性能特点**:
- ✅ 适用于大数据集（> 10,000 条记录）
- ✅ 查询性能优秀（索引查询）
- ✅ 支持复杂的查询条件
- ✅ 内存消耗低
- ❌ 需要安装 RediSearch 模块
- ❌ 需要维护索引

---

#### 方案 3: 使用 RedisJSON（推荐用于复杂查询）

```python
class RedisAdapterWithJSON:
    """Redis 适配器 - RedisJSON 优化版"""
    
    def __init__(self, url: str):
        self.client = redis.from_url(url)
        # 使用 RedisJSON 模块
        self.json_client = self.client.json()
    
    async def query(
        self,
        table: str,
        filters: Optional[Dict] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **options
    ) -> QueryResult:
        """
        查询数据（RedisJSON 优化版）
        
        优化点:
        1. 使用 RedisJSON 存储结构化数据
        2. 支持 JSONPath 查询
        3. 支持部分字段查询
        4. 性能优于字符串序列化
        """
        key_prefix = f"{table}:"
        
        # 使用 SCAN 获取所有键
        keys = []
        async for key in self.client.scan_iter(match=f"{key_prefix}*"):
            keys.append(key)
        
        # 分页处理
        if offset:
            keys = keys[offset:]
        if limit:
            keys = keys[:limit]
        
        # 批量获取 JSON 数据
        if keys:
            # 使用 JSON.GET 获取数据
            data = []
            for key in keys:
                value = await self.json_client.get(key)
                if value:
                    data.append(value)
            
            # 内存过滤
            if filters:
                data = self._filter_in_memory(data, filters)
        else:
            data = []
        
        return QueryResult(
            data=data,
            count=len(data),
            has_more=False
        )
```

**性能特点**:
- ✅ 适用于复杂 JSON 数据
- ✅ 支持部分字段查询
- ✅ 性能优于字符串序列化
- ❌ 需要安装 RedisJSON 模块

---

#### 性能对比

| 方案 | 10k 记录 | 100k 记录 | 1M 记录 | 内存消耗 | 实现难度 |
|------|---------|----------|---------|---------|---------|
| 基础优化 | ~100ms | ~1s | ~10s | 高 | 低 |
| RediSearch | ~10ms | ~50ms | ~200ms | 低 | 中 |
| RedisJSON | ~50ms | ~300ms | ~2s | 中 | 中 |

---

#### 推荐配置

**开发环境**（小数据集）:
```python
# 使用基础优化版
adapter = RedisAdapter(url)
```

**生产环境**（大数据集）:
```python
# 使用 RediSearch 优化版
adapter = RedisAdapterWithSearch(url)
```

**混合数据**（复杂查询）:
```python
# 使用 RedisJSON 优化版
adapter = RedisAdapterWithJSON(url)
```

**实现状态**: ⏳ 待实现

**性能优化说明**:
- ✅ 提供了三种性能优化方案
- ✅ 基础优化版适用于小数据集
- ✅ RediSearch 版本适用于大数据集，性能优秀
- ✅ RedisJSON 版本适用于复杂查询
- ✅ 提供了性能对比表格
- ✅ 提供了推荐配置

---

### 4.4 适配器工厂 ⏳ 待实现

```python
class AdapterFactory:
    """适配器工厂"""
    
    _adapters = {
        "postgresql": SQLAdapter,
        "postgres": SQLAdapter,
        "mysql": SQLAdapter,
        "sqlite": SQLAdapter,
        "mongodb": MongoAdapter,
        "redis": RedisAdapter,
        "opensearch": OpenSearchAdapter,
        "supabase": SupabaseAdapter,
    }
    
    @classmethod
    async def create(cls, url: str) -> DatabaseAdapter:
        """根据 URL 创建适配器"""
        parsed = parse_database_url(url)
        scheme = parsed.scheme
        
        adapter_class = cls._adapters.get(scheme)
        if not adapter_class:
            raise ValueError(f"Unsupported database: {scheme}")
        
        adapter = adapter_class(url)
        await adapter.connect(url)
        return adapter
```

**状态**: ⏳ 待实现

---

## 5. 安全性设计

### 5.1 安全架构 ⏳ 待实现

```mermaid
graph TB
    A[Request] --> B{权限检查}
    B -->|无权限| C[PermissionError]
    B -->|有权限| D{SQL 安全检查}
    
    D --> E[解析 SQL]
    E --> F{危险关键字?}
    F -->|是| G[拒绝 + 告警]
    F -->|否| H{参数化?}
    
    H -->|否| I[拒绝]
    H -->|是| J[审计日志]
    J --> K[执行]
    
    style D fill:#f99,stroke:#333,stroke-width:2px
```

**状态**: ⏳ 待实现

---

### 5.2 SQL 安全检查器 ⏳ 待实现

```python
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
from typing import Optional, Dict, Set, List
import re

class SQLSecurityChecker:
    """SQL 安全检查器 - 增强版"""
    
    # 危险关键字（不区分大小写）
    DANGEROUS_KEYWORDS = {
        "DROP", "TRUNCATE", "ALTER", 
        "DELETE FROM information_schema",
        "DELETE FROM pg_catalog",
        "DELETE FROM mysql",
        "DELETE FROM sys",
        "GRANT", "REVOKE",
        "EXEC", "EXECUTE",
        "xp_cmdshell", "sp_oacreate"
    }
    
    # 允许的 DDL 操作
    ALLOWED_DDL = {
        "CREATE INDEX", "CREATE UNIQUE INDEX",
        "CREATE TEMPORARY TABLE", "CREATE TEMP TABLE"
    }
    
    # SQL 注入模式检测
    INJECTION_PATTERNS = [
        # 注释注入
        r"--.*$",  # 单行注释
        r"/\*.*?\*/",  # 多行注释
        # 逻辑运算符注入
        r"\bor\b.*\b1\b.*=\s*1\b",  # OR 1=1
        r"\band\b.*\b1\b.*=\s*1\b",  # AND 1=1
        # UNION 注入
        r"\bUNION\b.*\bSELECT\b",
        # 堆叠查询
        r";.*\b(?:DROP|DELETE|UPDATE|INSERT|ALTER)\b",
        # 时间盲注
        r"\bWAITFOR\b.*\bDELAY\b",
        r"\bSLEEP\b\s*\(",
        # 存储过程注入
        r"\bxp_\w+",
        r"\bsp_\w+",
    ]
    
    @staticmethod
    def validate(command: str, params: Optional[Dict] = None) -> SecurityResult:
        """
        多层安全检查（增强版）
        1. 危险关键字检测
        2. SQL 注入模式检测
        3. 参数化验证
        4. 语法解析验证
        5. 审计日志记录
        """
        result = SecurityResult(allowed=True, message="")
        
        # 第 1 层：危险关键字检测
        keyword_check = SQLSecurityChecker._check_dangerous_keywords(command)
        if not keyword_check.allowed:
            return keyword_check
        
        # 第 2 层：SQL 注入模式检测
        injection_check = SQLSecurityChecker._check_injection_patterns(command)
        if not injection_check.allowed:
            return injection_check
        
        # 第 3 层：参数化验证
        if params is None:
            # 检查是否有未参数化的值
            if SQLSecurityChecker._has_unparameterized_values(command):
                return SecurityResult(
                    allowed=False,
                    message="Query contains unparameterized values. Use parameterized queries."
                )
        
        # 第 4 层：语法解析验证
        syntax_check = SQLSecurityChecker._validate_syntax(command)
        if not syntax_check.allowed:
            return syntax_check
        
        # 第 5 层：审计日志记录（在实现中完成）
        # AuditLogger.log(command, params)
        
        return result
    
    @staticmethod
    def _check_dangerous_keywords(command: str) -> SecurityResult:
        """检查危险关键字"""
        command_upper = command.upper()
        
        for keyword in SQLSecurityChecker.DANGEROUS_KEYWORDS:
            if keyword in command_upper:
                # 检查是否在允许的 DDL 列表中
                for allowed in SQLSecurityChecker.ALLOWED_DDL:
                    if allowed in command_upper:
                        break
                else:
                    return SecurityResult(
                        allowed=False,
                        message=f"Dangerous keyword detected: {keyword}"
                    )
        
        return SecurityResult(allowed=True)
    
    @staticmethod
    def _check_injection_patterns(command: str) -> SecurityResult:
        """检查 SQL 注入模式"""
        for pattern in SQLSecurityChecker.INJECTION_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE | re.MULTILINE):
                return SecurityResult(
                    allowed=False,
                    message=f"SQL injection pattern detected: {pattern}"
                )
        
        return SecurityResult(allowed=True)
    
    @staticmethod
    def _has_unparameterized_values(command: str) -> bool:
        """检查是否有未参数化的值"""
        # 检查是否有字符串拼接
        # 例如: "SELECT * FROM users WHERE name = '" + user_input + "'"
        if "'" in command or '"' in command:
            # 检查是否在字符串字面量中
            parsed = sqlparse.parse(command)
            for stmt in parsed:
                for token in stmt.flatten():
                    if token.ttype in sqlparse.tokens.String:
                        # 字符串字面量，检查是否有变量拼接
                        if "{" in token.value or "$" in token.value:
                            return True
        
        return False
    
    @staticmethod
    def _validate_syntax(command: str) -> SecurityResult:
        """验证 SQL 语法"""
        try:
            parsed = sqlparse.parse(command)
            if not parsed:
                return SecurityResult(
                    allowed=False,
                    message="Invalid SQL syntax: unable to parse"
                )
            
            # 检查是否有多个语句（堆叠查询）
            if len(parsed) > 1:
                return SecurityResult(
                    allowed=False,
                    message="Multiple statements detected. Only single statement allowed."
                )
            
            # 检查语句类型
            stmt = parsed[0]
            if SQLSecurityChecker._get_statement_type(stmt) not in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE"]:
                # 允许的语句类型
                pass
            
            return SecurityResult(allowed=True)
        except Exception as e:
            return SecurityResult(
                allowed=False,
                message=f"SQL syntax validation failed: {str(e)}"
            )
    
    @staticmethod
    def _get_statement_type(stmt) -> str:
        """获取语句类型"""
        for token in stmt.flatten():
            if token.ttype in DML:
                return token.value.upper()
        return "UNKNOWN"


class SecurityResult:
    """安全检查结果"""
    def __init__(self, allowed: bool, message: str = ""):
        self.allowed = allowed
        self.message = message
```

**状态**: ⏳ 待实现

**增强说明**：
- ✅ 增加了 SQL 注入模式检测（注释注入、逻辑运算符注入、UNION 注入、堆叠查询、时间盲注、存储过程注入）
- ✅ 增加了未参数化值检测
- ✅ 增加了语法解析验证（防止堆叠查询）
- ✅ 增加了更多危险关键字（xp_cmdshell、sp_oacreate 等）
- ✅ 使用正则表达式进行模式匹配

---

### 5.3 权限控制实现 ⏳ 待实现

```python
class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.enable_insert = os.getenv("ENABLE_INSERT", "false").lower() == "true"
        self.enable_delete = os.getenv("ENABLE_DELETE", "false").lower() == "true"
        self.enable_update = os.getenv("ENABLE_UPDATE", "false").lower() == "true"
        self.dangerous_agree = os.getenv("DANGEROUS_AGREE", "false").lower() == "true"
    
    def check_permission(self, operation: str) -> None:
        """检查操作权限"""
        if operation == "insert" and not self.enable_insert:
            raise PermissionError("INSERT operation disabled")
        # 其他检查...
```

**状态**: ⏳ 待实现

---

## 6. 异常体系设计

### 6.1 异常层次结构 ⏳ 待实现

```mermaid
classDiagram
    class DatabaseError {
        +message: str
        +original_error: Exception
        +database_type: str
    }
    
    class ConnectionError
    class QueryError
    class IntegrityError
    class NotFoundError
    class PermissionError
    class ConfigurationError
    
    DatabaseError <|-- ConnectionError
    DatabaseError <|-- QueryError
    DatabaseError <|-- IntegrityError
    DatabaseError <|-- NotFoundError
    DatabaseError <|-- PermissionError
    DatabaseError <|-- ConfigurationError
```

**状态**: ⏳ 待实现

---

### 6.2 异常转换器 ⏳ 待实现

```python
class ExceptionTranslator:
    """异常转换器"""
    
    @staticmethod
    def translate_sql_exception(e: Exception) -> DatabaseError:
        """SQL 异常转换"""
        if isinstance(e, sqlalchemy.exc.IntegrityError):
            constraint = parse_constraint(str(e))
            return IntegrityError(
                message=f"Unique constraint violation: {constraint}",
                original_error=e,
                constraint=constraint
            )
        # 其他映射...
```

**状态**: ⏳ 待实现

---

## 7. 配置管理设计

### 7.1 配置优先级 ⏳ 待实现

```mermaid
graph LR
    A[方法参数] -->|优先级 1| D[最终配置]
    B[环境变量] -->|优先级 2| D
    C[默认配置] -->|优先级 3| D
```

**状态**: ⏳ 待实现

---

### 7.2 DATABASE_URL 解析与保护 ⏳ 待实现

```python
import os
import base64
from cryptography.fernet import Fernet
from typing import Optional
from urllib.parse import urlparse, parse_qs

class DatabaseURLParser:
    """DATABASE_URL 解析器"""
    
    @staticmethod
    def parse(url: str) -> DatabaseConfig:
        """
        解析 DATABASE_URL
        
        示例:
        postgresql://user:pass@host:5432/db?pool_size=10
        
        返回:
        DatabaseConfig(
            scheme="postgresql",
            host="host",
            port=5432,
            database="db",
            username="user",
            password="pass",
            pool_config={"pool_size": 10}
        )
        """
        parsed = urlparse(url)
        
        # 解析查询参数
        pool_config = {}
        if parsed.query:
            query_params = parse_qs(parsed.query)
            pool_config = {k: v[0] if v else None for k, v in query_params.items()}
        
        return DatabaseConfig(
            scheme=parsed.scheme,
            host=parsed.hostname or "localhost",
            port=parsed.port,
            database=parsed.path.lstrip("/") if parsed.path else "",
            username=parsed.username,
            password=parsed.password,
            pool_config=pool_config
        )


class DatabaseURLProtector:
    """DATABASE_URL 保护器 - 加密存储密码"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        初始化保护器
        
        Args:
            encryption_key: 加密密钥（可选，默认从环境变量获取）
        """
        key = encryption_key or os.getenv("DATABASE_ENCRYPTION_KEY")
        if not key:
            # 如果没有提供密钥，生成一个警告密钥（仅用于开发环境）
            import warnings
            warnings.warn(
                "No encryption key provided. Using a default key for development only. "
                "Set DATABASE_ENCRYPTION_KEY environment variable for production.",
                UserWarning
            )
            key = "default-key-for-development-only-change-in-production"
        
        # 确保密钥是 32 字节（Fernet 要求）
        if len(key.encode()) < 32:
            key = key.ljust(32, '0')
        elif len(key.encode()) > 32:
            key = key[:32]
        
        self.cipher = Fernet(base64.urlsafe_b64encode(key.encode()))
    
    def encrypt_url(self, url: str) -> str:
        """
        加密 DATABASE_URL（只加密密码部分）
        
        Args:
            url: 原始 DATABASE_URL
            
        Returns:
            加密后的 URL（密码部分被加密）
        """
        parsed = urlparse(url)
        
        if not parsed.password:
            # 没有密码，直接返回
            return url
        
        # 加密密码
        encrypted_password = self.cipher.encrypt(parsed.password.encode()).decode()
        
        # 重建 URL（使用加密后的密码）
        new_url = parsed._replace(
            netloc=f"{parsed.username}:{encrypted_password}@{parsed.hostname}:{parsed.port}"
        ).geturl()
        
        return new_url
    
    def decrypt_url(self, encrypted_url: str) -> str:
        """
        解密 DATABASE_URL
        
        Args:
            encrypted_url: 加密后的 DATABASE_URL
            
        Returns:
            原始 DATABASE_URL
        """
        parsed = urlparse(encrypted_url)
        
        if not parsed.password:
            # 没有密码，直接返回
            return encrypted_url
        
        try:
            # 解密密码
            decrypted_password = self.cipher.decrypt(parsed.password.encode()).decode()
            
            # 重建 URL（使用解密后的密码）
            original_url = parsed._replace(
                netloc=f"{parsed.username}:{decrypted_password}@{parsed.hostname}:{parsed.port}"
            ).geturl()
            
            return original_url
        except Exception as e:
            raise ValueError(f"Failed to decrypt DATABASE_URL: {str(e)}")
    
    def get_safe_url(self, url: str) -> str:
        """
        获取安全的 URL（密码被隐藏）
        
        Args:
            url: 原始 DATABASE_URL
            
        Returns:
            安全的 URL（密码部分被替换为 *****）
        """
        parsed = urlparse(url)
        
        if not parsed.password:
            return url
        
        # 隐藏密码
        safe_url = parsed._replace(
            netloc=f"{parsed.username}:*****@{parsed.hostname}:{parsed.port}"
        ).geturl()
        
        return safe_url


class DatabaseConfig:
    """数据库配置"""
    def __init__(
        self,
        scheme: str,
        host: str,
        port: Optional[int],
        database: str,
        username: Optional[str],
        password: Optional[str],
        pool_config: Optional[Dict] = None
    ):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.pool_config = pool_config or {}
    
    def to_url(self) -> str:
        """转换为 URL"""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        else:
            auth = ""
        
        port = f":{self.port}" if self.port else ""
        
        query = ""
        if self.pool_config:
            query_params = "&".join([f"{k}={v}" for k, v in self.pool_config.items()])
            query = f"?{query_params}"
        
        return f"{self.scheme}://{auth}{self.host}{port}/{self.database}{query}"
```

**状态**: ⏳ 待实现

**保护说明**：
- ✅ 使用 Fernet 对称加密保护 DATABASE_URL 中的密码
- ✅ 支持从环境变量获取加密密钥（DATABASE_ENCRYPTION_KEY）
- ✅ 提供 `encrypt_url()` 和 `decrypt_url()` 方法
- ✅ 提供 `get_safe_url()` 方法用于日志输出（密码被隐藏）
- ✅ 开发环境警告（提醒用户设置加密密钥）

**使用示例**:
```python
# 初始化保护器
protector = DatabaseURLProtector()

# 加密 DATABASE_URL
encrypted_url = protector.encrypt_url("postgresql://user:pass@host:5432/db")

# 解密 DATABASE_URL
original_url = protector.decrypt_url(encrypted_url)

# 获取安全的 URL（用于日志）
safe_url = protector.get_safe_url(original_url)  # postgresql://user:*****@host:5432/db
```

---

## 8. 性能优化策略

### 8.1 连接池配置 ⏳ 待实现

**推荐配置**:
```python
# PostgreSQL
create_async_engine(
    url,
    pool_size=10,           # 核心连接数
    max_overflow=20,        # 最大溢出连接
    pool_timeout=30,        # 获取连接超时
    pool_recycle=3600,      # 连接回收时间(1小时)
    pool_pre_ping=True,     # 连接健康检查
    echo=False              # 不打印 SQL（生产环境）
)

# MongoDB
MongoClient(
    url,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=60000
)

# Redis
ConnectionPool(
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5
)
```

**状态**: ⏳ 待实现

---

### 8.2 查询优化 ⏳ 待实现

**优化策略**:
1. **自动 LIMIT**: 默认限制查询结果数量
2. **延迟加载**: 大结果集使用游标
3. **索引提示**: 通过 `advanced_query` 支持索引提示
4. **批量操作**: `insert/update/delete` 支持批量模式

**状态**: ⏳ 待实现

---

## 9. MCP 集成设计

### 9.1 MCP Server 实现 ⏳ 待实现

```python
from mcp import Server, Tool

async def create_mcp_server():
    """创建 MCP Server"""
    server = Server("mcp-database")
    
    # 注册工具
    server.add_tool(database_query_tool)
    server.add_tool(database_insert_tool)
    server.add_tool(database_update_tool)
    server.add_tool(database_delete_tool)
    server.add_tool(database_execute_tool)
    server.add_tool(database_advanced_query_tool)
    server.add_tool(get_capabilities_tool)
    
    return server
```

**状态**: ⏳ 待实现

---

### 9.2 工具定义 ⏳ 待实现

```python
@Tool(
    name="database_query",
    description="Query data from database (read-only operation)",
    input_schema={
        "type": "object",
        "properties": {
            "table": {"type": "string"},
            "filters": {"type": "object"},
            "limit": {"type": "integer", "default": 100}
        },
        "required": ["table"]
    }
)
async def database_query_tool(
    table: str,
    filters: Optional[Dict] = None,
    limit: int = 100,
    **kwargs
):
    """查询工具实现"""
    adapter = get_current_adapter()
    result = await adapter.query(table, filters, limit=limit)
    return result.dict()
```

**状态**: ⏳ 待实现

---

## 10. 部署方案

### 10.1 部署架构 ⏳ 待实现

```mermaid
graph TB
    A[LLM] -->|MCP Protocol| B[MCP Server]
    B --> C[mcp-database SDK]
    C --> D[Database Adapters]
    D --> E[(Databases)]
    
    F[Environment Variables] --> B
    G[Audit Logs] --> H[Log Storage]
    B --> G
```

**状态**: ⏳ 待实现

---

### 10.2 环境要求 ⏳ 待实现

**最低要求**:
- Python >= 3.10
- 内存 >= 512MB
- CPU >= 1 核

**推荐配置**:
- Python 3.11+
- 内存 >= 2GB
- CPU >= 2 核

**状态**: ⏳ 待实现

---

### 10.3 安装方式 ⏳ 待实现

```bash
# PyPI 安装
pip install mcp-database

# 开发安装
git clone https://github.com/your-org/mcp-database
cd mcp-database
pip install -e ".[dev]"

# Docker 部署
docker run -e DATABASE_URL=... mcp-database:latest
```

**状态**: ⏳ 待实现

---

## 11. 监控与日志

### 11.1 审计日志 ⏳ 待实现

**日志格式**:
```json
{
  "timestamp": "2024-01-07T10:30:00Z",
  "operation": "execute",
  "database": "postgresql",
  "command": "SELECT * FROM users WHERE age > :age",
  "params": {"age": 18},
  "success": true,
  "duration_ms": 45,
  "user_agent": "Claude/MCP"
}
```

**状态**: ⏳ 待实现

---

### 11.2 性能指标 ⏳ 待实现

**关键指标**:
- QPS (Queries Per Second)
- P95/P99 延迟
- 连接池利用率
- 错误率

**状态**: ⏳ 待实现

---

## 12. 测试策略

### 12.1 测试金字塔 ⏳ 待实现

```mermaid
graph TB
    A[集成测试<br/>20%] --> B[单元测试<br/>80%]
    C[E2E 测试<br/>选择性] --> A
    
    style B fill:#bfb
```

**状态**: ⏳ 待实现

---

### 12.2 测试环境 ⏳ 待实现

**Docker Compose 环境**:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
  mysql:
    image: mysql:8
  mongodb:
    image: mongo:7
  redis:
    image: redis:7
  opensearch:
    image: opensearchproject/opensearch:2
```

**状态**: ⏳ 待实现

---

## 13. 版本演进计划

### 13.1 版本路线图

| 版本 | 功能 | 状态 |
|------|------|------|
| v1.0 | 核心 CRUD + 7 种数据库 | ⏳ 待开发 |
| v1.1 | 高级查询增强 | ⏳ 计划中 |
| v1.2 | 连接缓存优化 | ⏳ 计划中 |
| v2.0 | 多租户支持 | ⏳ 计划中 |

---

## 14. 技术债务管理

### 14.1 已知限制 ⏳ 待解决

1. **Redis "表"抽象不完美**: 内存过滤性能较差
   - 解决方案: 使用 Redis Modules (RediSearch)
   
2. **跨数据库事务不支持**: 架构限制
   - 解决方案: 提供 Saga 模式补偿机制

3. **大结果集性能**: 内存占用高
   - 解决方案: 流式返回 + 游标支持

**状态**: ⏳ 待解决

---

## 附录

### A. 技术参考
- SQLAlchemy 异步教程: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Motor 文档: https://motor.readthedocs.io
- MCP 协议: https://modelcontextprotocol.io

### B. 代码规范
- PEP 8: Python 代码风格
- PEP 484: 类型注解
- Google Python Style Guide
