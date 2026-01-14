---
name: commit
description: 智能提交代码，自动生成规范的 commit message
usage: |
  /commit [--amend] [--message "msg"] [--no-verify] [--all]
---

# 智能提交代码

分析会话上下文中的变更，自动生成规范的 commit message。

## 分析变更

```bash
git status
git diff HEAD --stat
git log -1 --format="%s"
```

## 智能提交

```bash
# 智能分析，仅提交上下文修改的文件
git add {changed_files}
git commit -m "{generated_message}"
```

## 参数

| 参数 | 说明 |
|------|------|
| `--amend` | 修改最后一次提交（未推送时） |
| `--message "msg"` | 自定义提交信息 |
| `--no-verify` | 跳过 pre-commit 检查 |
| `--all` | 提交所有变更 |

## 示例

```
/commit                    # 智能分析，仅提交上下文修改的文件
/commit --all             # 提交所有变更
/commit --amend           # 修改最后一次提交
/commit --message "fix: 修复登录bug"  # 使用自定义信息
```

## Commit Message 规范

- `feat:` 新功能
- `fix:` 修复 bug
- `refactor:` 重构代码
- `docs:` 文档更新
- `style:` 代码格式调整
- `test:` 测试相关
- `chore:` 构建/工具相关
