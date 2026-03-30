# Contributing to CS Knowledge Graph

感谢您对 CS Knowledge Graph 项目的关注！本指南将帮助您了解如何使用 GitHub 最佳实践来贡献内容。

## 分支管理策略 (Feature Branch Workflow)

我们采用 GitHub Flow 工作流模型：

### 分支命名规范

```
feature/<domain>/<description>    # 新功能/新知识文档
fix/<description>                 # 修复错误
docs/<description>                # 文档更新
ref/<description>                 # 交叉引用更新
```

**示例：**
- `feature/cs/ds-stack-queue` - 添加栈和队列数据结构
- `feature/cs/algo-graph-traversal` - 添加图遍历算法
- `feature/se/unit-testing` - 添加单元测试文档
- `fix/broken-links-wave-1` - 修复断链

### 工作流程

1. **从 main 创建功能分支**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/cs/ds-stack
   ```

2. **进行更改**
   - 遵循文件命名规范
   - 保持文档结构一致
   - 添加交叉引用

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat(ds): add stack data structure documentation"
   ```

4. **推送到远程**
   ```bash
   git push -u origin feature/cs/ds-stack
   ```

5. **创建 Pull Request**
   - 使用 PR 模板
   - 填写所有必填项
   - 请求审查

6. **合并到 main**
   - 通过 CI 检查
   - 获得批准后合并
   - 删除功能分支

## 提交信息规范

我们采用语义化提交信息：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型 (Type)

| 类型 | 描述 |
|------|------|
| `feat` | 新知识点/文档 |
| `add` | 现有文档的新章节 |
| `ref` | 交叉引用/链接更新 |
| `fix` | 内容修正 |
| `docs` | README/CONTRIBUTING 更新 |
| `struct` | 目录结构变更 |

### 示例

```
feat(ds): add stack and queue documentation

- 添加栈的基本概念和 LIFO 原理
- 添加队列的基本概念和 FIFO 原理
- 包含复杂度分析和代码示例
- 添加面试常见问题

Relates to #12
```

## 文档规范

### 文件命名

- 使用小写字母
- 单词之间用连字符分隔
- 使用英文文件名

**示例：**
- ✅ `stack.md`, `binary-search.md`, `red-black-tree.md`
- ❌ `Stack.md`, `binary_search.md`, `数据结构.md`

### 文档结构

每个 Markdown 文件应包含以下部分：

```markdown
# 概念名称 (Concept Name)

简要中文解释，首次出现专业名词时给出英文对照。

## 原理 (Principles)

深入解释原理、数学基础、算法步骤。

### 关键性质
- 性质1: 解释
- 性质2: 解释

## 复杂度分析 (Complexity Analysis)

- 时间复杂度: O(?)
- 空间复杂度: O(?)

## 实现示例 (Implementation)

\`\`\`python
# 代码示例
\`\`\`

## 应用场景 (Applications)

- 场景1: 说明
- 场景2: 说明

## 面试要点 (Interview Questions)

**Q1: 问题？**
> 答案要点...

**Q2: 问题？**
> 答案要点...

## 相关概念 (Related Concepts)

- [相关概念1](../path/to/file.md)
- [相关概念2](../path/to/file.md)

## 参考资料 (References)

- [链接](URL)
```

### 交叉引用

使用相对路径链接到其他文档：

```markdown
栈常用于实现 [深度优先搜索](../algorithms/graph-traversal.md)。
详见 [数组](../data-structures/array.md) 的内存布局。
```

## 质量保证检查清单

在提交 PR 前，请确保：

- [ ] 文件命名符合规范（小写，连字符分隔）
- [ ] 包含所有必需章节
- [ ] 首次出现专业名词给出英文对照
- [ ] 包含复杂度分析（算法/数据结构）
- [ ] 代码示例正确无误
- [ ] 包含 3-5 个面试问题
- [ ] 添加了交叉引用（至少 3 个）
- [ ] Markdown 语法正确
- [ ] 所有内部链接有效
- [ ] 内容使用中文撰写

## 代码审查流程

1. **自动化检查**
   - Markdown 语法检查 (markdownlint)
   - 链接有效性检查 (lychee)

2. **人工审查**
   - 内容准确性
   - 结构一致性
   - 交叉引用完整性

3. **合并要求**
   - 所有 CI 检查通过
   - 至少 1 人批准
   - 无未解决的审查意见

## 开发环境设置

### 安装依赖

```bash
# 安装 markdownlint
npm install -g markdownlint-cli

# 安装 lychee (链接检查)
# macOS
brew install lychee

# Linux
cargo install lychee
```

### 本地检查

```bash
# 检查 Markdown 语法
markdownlint '**/*.md' --ignore node_modules

# 检查链接
lychee '**/*.md'
```

## 问题报告

如果发现内容错误或链接失效：

1. 搜索现有 Issues
2. 如果没有，创建新 Issue
3. 使用相应标签：`content-error`, `broken-link`, `enhancement`

## 许可证

通过贡献代码，您同意您的贡献将在与项目相同的许可证下发布。

---

如有任何问题，欢迎通过 Issue 讨论！
