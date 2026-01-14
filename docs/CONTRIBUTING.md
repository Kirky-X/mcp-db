# 🤝 Contributing

_贡献指南_

感谢您有兴趣为 MCP Database SDK 做出贡献！

---

## 💪 Ways to Contribute

| Action | Description |
|:-------|:------------|
| [🐛 Report Bug](../../issues) | 发现 bug？告诉我们 |
| [💡 Request Feature](../../discussions) | 有好的想法？分享它 |
| [🔧 Submit PR](../../pulls) | 想贡献代码？Fork & PR |

---

## 🛠️ 开发环境

### 前置条件

- Python 3.10+
- Git

### 安装

```bash
git clone https://github.com/yourusername/mcp-database.git
cd mcp-database
pip install -e ".[dev]"

# 运行测试
pytest
ruff check .
mypy src/mcp_database
```

---

## 🔄 开发流程

### 1. 创建分支

```bash
git fetch upstream
git checkout main
git merge upstream/main
git checkout -b feature/your-feature-name
```

### 2. 编写代码

- 使用 ruff 格式化
- 添加类型注解
- 编写 Google 风格文档字符串

### 3. 编写测试

```bash
pytest                    # 所有测试
pytest --cov=mcp_database # 带覆盖率
```

### 4. 提交更改

```bash
git add .
git commit -m "feat: Add new feature"
git push origin feature/your-feature
```

### 5. 创建 Pull Request

---

## 📏 代码规范

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
    """
```

---

## 🧪 测试

- 每个新功能应有对应测试
- 测试文件命名：`test_*.py`
- 使用 pytest-asyncio

---

## 📝 文档

- 更新 README（如果需要）
- 添加 API 文档
- 保持文档与代码同步

---

## 🔍 代码审查

### 审查标准

- 功能正确性
- 代码质量
- 测试覆盖

### 响应反馈

```bash
git add .
git commit -m "Address review comments"
git push origin feature/your-feature
```

---

## 📞 联系方式

- [GitHub Issues](../../issues)
- [GitHub Discussions](../../discussions)

---

感谢您的贡献！

**© 2026 Kirky.X**
