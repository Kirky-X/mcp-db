# 贡献指南

感谢您有兴趣为 MCP Database SDK 做出贡献！我们欢迎各种形式的贡献，包括代码改进、文档更新、问题报告等。

---

## 贡献方式

<table>
<tr>
<td width="33%" align="center">

### 🐛 报告问题
发现 bug？<br>
[创建 Issue](../../issues)

</td>
<td width="33%" align="center">

### 💡 功能建议
有好的想法？<br>
[发起讨论](../../discussions)

</td>
<td width="33%" align="center">

### 🔧 提交代码
想贡献代码？<br>
[Fork & PR](../../pulls)

</td>
</tr>
</table>

---

## 开发环境设置

### 前置条件

- Python 3.10+
- pip 或 poetry
- Git

### 安装开发环境

```bash
# 克隆仓库
git clone https://github.com/yourusername/mcp-database.git
cd mcp-database

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .
mypy src/mcp_database
```

---

## 开发流程

### 1. 创建分支

```bash
# 更新主分支
git fetch upstream
git checkout main
git merge upstream/main

# 创建功能分支
git checkout -b feature/your-feature-name

# 或修复 bug
git checkout -b fix/issue-123
```

### 2. 编写代码

遵循项目编码规范：

- 使用 ruff 格式化代码
- 添加类型注解
- 编写文档字符串
- 遵循 PEP 8

### 3. 编写测试

```bash
# 运行测试
pytest

# 运行特定测试
pytest tests/test_adapter.py

# 运行带覆盖率
pytest --cov=mcp_database
```

### 4. 提交更改

```bash
# 暂存更改
git add .

# 提交（遵循 Conventional Commits）
git commit -m "feat: Add new feature"

# 推送到 fork
git push origin feature/your-feature
```

### 5. 创建 Pull Request

---

## 代码规范

### Python 风格

- 使用 ruff 进行格式化
- 遵循 PEP 8
- 类型注解必需（mypy disallow_untyped_defs）
- 使用绝对导入

### 导入顺序

```python
# 标准库
import os
from typing import Any

# 第三方库
from pydantic import BaseModel

# 本地模块
from mcp_database.core.adapter import DatabaseAdapter
```

### 文档字符串

使用 Google 风格：

```python
async def insert(self, table: str, data: dict[str, Any]) -> InsertResult:
    """
    向数据库插入新记录。

    Args:
        table: 表/集合名
        data: 要插入的数据

    Returns:
        InsertResult: 插入结果

    Raises:
        QueryError: 查询错误时抛出
    """
```

---

## 测试指南

### 单元测试

- 每个新功能应有对应测试
- 测试文件命名：`test_*.py`
- 使用 pytest-asyncio

### 集成测试

- 测试数据库连接
- 测试实际 CRUD 操作
- 使用环境变量或 fixture

---

## 文档更新

- 更新 README（如果需要）
- 添加 API 文档
- 更新 CHANGELOG
- 保持文档与代码同步

---

## 代码审查

### 审查标准

- 功能正确性
- 代码质量
- 测试覆盖
- 文档完整性
- 性能影响
- 安全性

### 响应反馈

```bash
# 回应审查意见
git add .
git commit -m "Address review comments"
git push origin feature/your-feature
```

---

## 行为准则

请尊重并包容所有贡献者。详细的准则请参阅 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

---

## 联系方式

- [GitHub Issues](../../issues)
- [GitHub Discussions](../../discussions)

---

感谢您的贡献！

**© 2026 Kirky.X。保留所有权利。**
