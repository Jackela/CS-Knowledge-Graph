# 🎓 Software-to-PM 知识图谱（个人复习笔记）

> **📝 这是一份个人学习与复习笔记**，用于巩固和梳理从软件工程到产品管理的知识体系。
>
> 以"费曼学习法 + 引用互链"为核心方法，贯穿「计算机科学」「软件工程」「AI 与数据系统」「产品管理」四大领域。
>
> 所有知识点以独立 Markdown 文件存在，并通过相对路径引用 `[链接](路径示例)` 构建自洽、可扩展的知识网络。
>
> ⚠️ **免责声明**：本笔记仅代表个人理解，可能存在错误或不完整之处，仅供参考，不构成权威学习资料。

---

## 🧭 笔记愿景

现代工程师的成长不是"学完算法 → 写代码 → 做项目"的线性流程，而是一个相互支撑的多层体系：

1. 计算机科学（Computer Science Fundamentals）：思维与计算的底层逻辑
2. 软件工程与架构（Software Engineering & Architecture）：构建与演进复杂系统
3. 云与 DevOps（Cloud & DevOps）：工程效率与交付自动化
4. AI 与数据系统（AI & Data Systems）：智能应用与数据闭环
5. 产品管理与策略（Product Management & Strategy）：从功能到价值的跃迁

**本笔记以"写出解释、建立引用、持续重构"为基本工作方式，通过个人复习与实践，沉淀一套可阅读、可维护、可扩展的知识地图。**

---

## 📘 目录结构

`	ext
software-to-pm-knowledge-map/
├── README.md
├── computer-science/
│   ├── data-structures/
│   │   ├── array.md
│   │   ├── linked-list.md
│   │   └── hash-table.md
│   ├── algorithms/
│   │   ├── sorting.md
│   │   ├── binary-search.md
│   │   └── dynamic-programming.md
│   └── systems/
│       ├── os.md
│       ├── network.md
│       └── database.md
├── software-engineering/
│   ├── oop-design.md
│   ├── design-patterns.md
│   ├── ddd.md
│   └── architecture-patterns.md
├── cloud-devops/
│   ├── docker.md
│   ├── kubernetes.md
│   ├── cicd.md
│   └── monitoring.md
├── ai-data-systems/
│   ├── llm.md
│   ├── rag.md
│   ├── vector-db.md
│   └── ab-testing.md
├── product-management/
│   ├── brd-prd-srs.md
│   ├── mvp.md
│   ├── agile.md
│   └── market-analysis.md
└── references/
    ├── memory-addressing.md
    ├── time-complexity.md
    └── cap-base.md
`

每个文件表示一个概念或主题，内部可通过相对路径引用其他文档形成互链。例如：

`markdown
数组是一组连续存储的元素，详见 [内存寻址](./references/memory-addressing.md)。
扩容成本的摊销分析参见 [时间复杂度](./references/time-complexity.md)。
`

---

## 🧠 学习方法论

1. 费曼学习法（Feynman Technique）：写下概念 → 解释给“外行” → 发现模糊处 → 补齐前置知识。
2. 双向链接（Bidirectional Linking）：通过互相引用组织知识，而非线性章节式阅读。

---

## 📚 建议学习路线

| 阶段 | 目标 | 核心模块 |
| --- | --- | --- |
| 阶段 1 | 工程基础 | 数据结构、算法、系统原理 |
| 阶段 2 | 工程实践 | 架构设计、CI/CD、分布式系统 |
| 阶段 3 | 智能系统 | LLM、RAG、A/B 测试 |
| 阶段 4 | 产品管理 | BRD/PRD/SRS、PMBOK、敏捷实践 |
| 阶段 5 | 商业与策略 | 市场分析、ROI、增长模型 |

---

## 🧩 文件规范

| 元素 | 规范 |
| --- | --- |
| 文件名 | 全英文小写与短横线（如 rray.md, memory-addressing.md） |
| 内部结构 | 概念 → 原理 → 示例 → 面试要点 → 引用 |
| 引用方式 | 使用相对路径 `[概念名](路径示例)` |
| 语言风格 | 中文为主，首次出现专业名词时给出中英对照 |
| 更新策略 | 每次修改都应提高“可解释性”和“可复用性” |


---

## 📅 进度追踪

| 模块 | 状态 |
| --- | --- |
| Array / Linked List | ✅ 草稿中 |
| 内存寻址（Memory Addressing） | 🚧 进行中 |
| CAP / BASE 理论 | ⏳ 待编写 |
| RAG / Vector DB | ⏳ 待扩展 |
| 产品管理文档体系 | 🧩 计划中 |

---

## ✍️ 关于作者

- **孔维轩（Weixuan Kong）**
- Master of Computer Science, University of Sydney
- 致力于连接软件工程、AI 系统与产品策略(以及找到工作/(ㄒoㄒ)/~~)
- GitHub：https://github.com/Jackela

---

## 💡 使用建议

- **这是个人复习笔记，不是系统教程**：内容根据个人学习进度和理解编写，可能不够全面或存在偏差
- **欢迎参考，但请审慎使用**：建议结合权威教材和官方文档进行学习
- **持续更新中**：笔记会随着学习深入不断补充和修正
- **欢迎交流**：如发现错误或有更好的理解，欢迎通过 Issue 交流讨论

---

## 🔗 相关概念

### 知识导航
- [知识图谱索引](./index.md) - 完整的知识点索引与导航
- [学习路线](./CURRICULUM.md) - 系统化的学习路径规划

### 核心领域
- [数据结构](./computer-science/data-structures/array.md) - 计算机科学基础
- [软件工程](./software-engineering/oop-design.md) - 工程实践方法
- [云与 DevOps](./cloud-devops/docker.md) - 现代运维体系
- [AI 与数据系统](./ai-data-systems/llm.md) - 智能系统前沿
