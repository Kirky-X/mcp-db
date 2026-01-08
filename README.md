# MCP Database SDK

为大语言模型提供统一数据库操作能力的 Python SDK。

## 功能特性

- 支持 7 种数据库：PostgreSQL, MySQL, SQLite, MongoDB, Redis, OpenSearch, Supabase
- 统一的 CRUD 接口
- 灵活的过滤器 DSL
- 完善的权限控制
- 多层安全防护
- MCP 协议集成

## 快速开始

```bash
# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 启动测试数据库
docker-compose -f docker-compose.test.yml up -d
```

## 配置

```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/db
export ENABLE_INSERT=true
export ENABLE_DELETE=true
export ENABLE_UPDATE=true
```

## 文档

- [产品需求文档](docs/prd.md)
- [任务清单](docs/task.md)
- [技术设计](docs/tdd.md)
- [测试计划](docs/test.md)
- [用户验收](docs/uat.md)