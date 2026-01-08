# Pre-commit 钩子配置说明

本文档描述如何为 MCP Database SDK 项目配置和使用 pre-commit 钩子。

---

## 概述

pre-commit 钩子在每次 `git commit` 前自动运行代码检查，确保代码质量符合标准。

## 安装步骤

### 1. 安装 pre-commit

```bash
# 使用 pip 安装
pip install pre-commit

# 或使用 conda
conda install -c conda-forge pre-commit
```

### 2. 安装钩子

```bash
# 在项目根目录执行
pre-commit install

# 输出应显示：
# pre-commit installed at .git/hooks/pre-commit
```

### 3. 验证安装

```bash
# 检查 pre-commit 版本
pre-commit --version

# 查看已安装的钩子
pre-commit installed-hooks
```

---

## 检查工具配置

项目已配置以下检查工具：

### 1. Ruff（代码格式化和 Linting）

| 检查项 | 命令 | 说明 |
|-------|------|------|
| Linting | `ruff check .` | 代码质量问题检查 |
| Formatting | `ruff format --check .` | 代码格式检查 |

**配置来源**：`pyproject.toml` 中的 `[tool.ruff]` 配置

### 2. MyPy（类型检查）

| 检查项 | 命令 | 说明 |
|-------|------|------|
| Type check | `mypy src/mcp_database` | 静态类型检查 |

**配置来源**：`pyproject.toml` 中的 `[tool.mypy]` 配置

### 3. Pre-commit Hooks

| 检查项 | 说明 |
|-------|------|
| trailing-whitespace | 修复行尾空格 |
| end-of-file-fixer | 确保文件以换行符结尾 |
| check-yaml | 检查 YAML 语法 |
| check-json | 检查 JSON 语法 |
| check-added-large-files | 检查大文件（>1MB） |

---

## 使用方法

### 提交代码（自动检查）

```bash
git add .
git commit -m "Your commit message"
```

如果任何检查失败，提交将被阻止并显示错误信息。

### 手动运行检查

```bash
# 运行所有检查
pre-commit run --all-files

# 运行特定检查
pre-commit run ruff
pre-commit run mypy

# 仅检查暂存的文件
pre-commit run

# 检查特定文件
pre-commit run --files src/mcp_database/server/__init__.py
```

### 跳过检查（不推荐）

```bash
# 跳过所有 pre-commit 检查
git commit --no-verify -m "message"

# 跳过特定检查（在文件中添加）
# ruff: noqa: F401
```

---

## 常见问题

### Q: 如何更新检查工具版本？

```bash
# 更新所有工具到最新版本
pre-commit autoupdate

# 更新特定工具
pre-commit autoupdate --repo https://github.com/astral-sh/ruff-pre-commit
```

### Q: 如何排除某些文件？

编辑 `.pre-commit-config.yaml` 中的 `exclude` 模式：

```yaml
exclude: |
  (?x)^(
    .git/ |
    __pycache__/ |
    tests/fixtures/ |
    docs/_build/
  )
```

### Q: 检查很慢怎么办？

```bash
# 仅检查暂存的文件（最快）
git add .
pre-commit run

# 缓存结果
pre-commit run --cache
```

### Q: 如何禁用某个检查？

在 `.pre-commit-config.yaml` 中注释掉对应的 hook，或使用 `pass_filenames: false`：

```yaml
- repo: ...
  hooks:
    - id: some-hook
      pass_filenames: false  # 禁用
```

---

## CI 集成

Pre-commit 也在 CI 中运行，确保所有代码都通过检查：

```bash
# 在 CI 中手动运行
pre-commit run --all-files
```

---

## 配置文件位置

| 文件 | 说明 |
|------|------|
| `.pre-commit-config.yaml` | Pre-commit 配置文件 |
| `pyproject.toml` | Ruff 和 MyPy 配置 |
| `.pre-commit-hooks.yaml` | 自定义钩子定义（可选） |

---

## 故障排除

### 问题：pre-commit 命令未找到

```bash
# 确保在虚拟环境中
source .venv/bin/activate
pip install pre-commit
```

### 问题：MyPy 找不到依赖

```bash
# 安装额外的依赖
pip install pydantic sqlalchemy
```

### 问题：检查失败但不知道原因

```bash
# 详细输出
pre-commit run --verbose

# 查看日志
cat ~/.cache/pre-commit/pre-commit.log
```

---

**© 2026 Kirky.X。保留所有权利。**
