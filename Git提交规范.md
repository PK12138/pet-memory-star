# 📝 Git 提交规范

> 解决中文乱码问题，统一团队协作规范

---

## 🐛 中文乱码问题

### 问题原因
- Windows PowerShell 默认使用 GBK 编码
- Git 期望 UTF-8 编码
- 导致中文 commit message 显示为乱码

### 已应用的配置
```bash
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
```

**注意**：这些配置只对新提交生效，历史记录无法修复。

---

## ✅ 推荐方案：使用英文 Commit Message

### 为什么使用英文？
1. ✅ 永远不会乱码
2. ✅ 国际化标准
3. ✅ 兼容所有系统
4. ✅ 专业开发规范
5. ✅ 方便团队协作

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| **feat** | 新功能 | `feat: add theme settings page` |
| **fix** | 修复bug | `fix: resolve visit-stat API 422 error` |
| **update** | 更新功能 | `update: improve memorial detail UI` |
| **style** | 样式修改 | `style: adjust theme card layout` |
| **refactor** | 重构代码 | `refactor: optimize API request logic` |
| **docs** | 文档更新 | `docs: add deployment guide` |
| **test** | 测试相关 | `test: add unit tests for API` |
| **chore** | 构建/工具 | `chore: update dependencies` |

### Scope 范围（可选）

- **frontend** - 前端相关
- **backend** - 后端相关
- **api** - API相关
- **ui** - UI相关
- **miniprogram** - 小程序相关

---

## 📋 提交示例

### 示例1：新功能
```bash
git commit -m "feat(miniprogram): add mood diary feature with 6 mood types"
```

### 示例2：Bug修复
```bash
git commit -m "fix(api): change visit-stat endpoint from Form to JSON format"
```

### 示例3：UI更新
```bash
git commit -m "update(ui): enhance memorial detail page with visit stats"
```

### 示例4：多行提交
```bash
git commit -m "feat(miniprogram): implement theme settings

- Add 8 beautiful theme options
- Support theme preview and switching
- Store theme preference in local storage
- Add theme button in user center"
```

### 示例5：修复并关联issue
```bash
git commit -m "fix(api): resolve 422 error in visit-stat endpoint

Changed parameter format from Form to JSON to match frontend request format.

Fixes #123"
```

---

## 🎯 常用提交模板

### 功能开发
```bash
# 单个功能
git commit -m "feat: add <feature-name>"

# 详细说明
git commit -m "feat(<scope>): add <feature-name>

- Feature detail 1
- Feature detail 2
- Feature detail 3"
```

### Bug修复
```bash
# 简单修复
git commit -m "fix: resolve <bug-description>"

# 详细说明
git commit -m "fix(<scope>): resolve <bug-description>

Root cause: ...
Solution: ...

Fixes #<issue-number>"
```

### 文档更新
```bash
git commit -m "docs: update <document-name>"
git commit -m "docs: add deployment guide for new features"
```

### 样式调整
```bash
git commit -m "style: adjust <component> layout"
git commit -m "style: improve responsive design for mobile"
```

---

## 🚀 实际使用

### 本项目的提交示例

#### ✅ 好的提交
```bash
git commit -m "feat(miniprogram): add forgot password feature"
git commit -m "fix(api): change visit-stat from Form to JSON"
git commit -m "update(ui): enhance memorial detail statistics display"
git commit -m "docs: add comprehensive testing report"
```

#### ❌ 不推荐的提交
```bash
git commit -m "修复bug"  # 太简略，且可能乱码
git commit -m "更新"      # 没说明更新了什么
git commit -m "fix"       # 没说明修复了什么
git commit -m "asdf"      # 无意义
```

---

## 🔧 提交前检查清单

- [ ] Commit message 使用英文
- [ ] 包含 type 类型
- [ ] 说明清楚做了什么
- [ ] 如果是修复，说明了原因和解决方案
- [ ] 代码已测试通过
- [ ] 没有包含调试代码
- [ ] 文件修改合理

---

## 📊 提交频率建议

### 何时提交？
- ✅ 完成一个完整功能
- ✅ 修复一个bug
- ✅ 完成一次重构
- ✅ 更新一份文档

### 避免
- ❌ 过于频繁（每改一行就提交）
- ❌ 提交不完整的代码
- ❌ 提交包含错误的代码

---

## 🛠️ Git Bash 使用（备选方案）

如果确实需要使用中文 commit message：

### 1. 打开 Git Bash
```bash
# 右键项目文件夹 → Git Bash Here
```

### 2. 正常提交
```bash
git add .
git commit -m "修复访问统计API的数据格式问题"
git push origin main
```

Git Bash 原生支持 UTF-8，不会出现乱码。

---

## 📚 参考资源

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Angular Commit Message Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
- [Git Commit Good Practice](https://wiki.openstack.org/wiki/GitCommitMessages)

---

## 🎓 总结

### 推荐做法
1. **使用英文 Commit Message**（最推荐）
2. 遵循 `<type>: <description>` 格式
3. 描述清晰、简洁、有意义
4. 一次提交做一件事

### 如果必须用中文
- 使用 **Git Bash** 而不是 PowerShell
- 或者配置 PowerShell 编码（复杂）

---

**建议**：从下一次提交开始，使用英文 Commit Message，保持代码库的专业性和国际化。

**文档版本**: v1.0  
**创建时间**: 2025-10-24  
**维护者**: AI Assistant

