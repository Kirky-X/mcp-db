# 🔒 Pre-commit 钩子

_代码质量检查配置_

pre-commit 钩子在每次 `git commit` 前自动运行代码检查。

---

## 🛠️ 安装

```bash
pip install pre-commit
pre-commit install
pre-commit --version
```

---

## 📋 检查工具

| Tool | Command | Description |
|:-----|:--------|:------------|
| **Ruff** | `ruff check .` | 代码质量检查 |
| **Ruff Format** | `ruff format --check .` | 代码格式检查 |
| **MyPy** | `mypy src/mcp_database` | 静态类型检查 |

### 内置 Hooks

| Hook | Action |
|:-----|:-------|
| `trailing-whitespace` | 修复行尾空格 |
| `end-of-file-fixer` | 确保文件以换行符结尾 |
| `check-yaml` | 检查 YAML 语法 |
| `check-json` | 检查 JSON 语法 |
| `check-added-large-files` | 检查大文件（>1MB） |

---

## 📖 使用方法

### 提交代码（自动检查）

```bash
git add .
git commit -m "Your commit message"
```

### 手动运行

```bash
pre-commit run --all-files     # 所有文件
pre-commit run                 # 仅暂存文件
pre-commit run ruff            # 特定检查
pre-commit run --cache         # 使用缓存
```

### 跳过检查（不推荐）

```bash
git commit --no-verify -m "message"
```

---

## ❓ 常见问题

### 更新工具版本

```bash
pre-commit autoupdate
```

### 排除文件

编辑 `.pre-commit-config.yaml` 中的 `exclude` 模式。

### 检查很慢？

```bash
pre-commit run  # 仅检查暂存文件，最快
```

---

## 📁 配置文件

| File | Description |
|:-----|:------------|
| `.pre-commit-config.yaml` | Pre-commit 配置 |
| `pyproject.toml` | Ruff / MyPy 配置 |

---

## 🐛 故障排除

### 命令未找到

```bash
source .venv/bin/activate
pip install pre-commit
```

### MyPy 找不到依赖

```bash
pip install pydantic sqlalchemy
```

### 检查失败？

```bash
pre-commit run --verbose
cat ~/.cache/pre-commit/pre-commit.log
```

---

**© 2026 Kirky.X**
