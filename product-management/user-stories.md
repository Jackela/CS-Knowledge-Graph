# 用户故事 (User Stories)

## 简介
用户故事是从最终用户的角度描述软件功能的简短、简单的描述。它是敏捷开发中的核心实践，用于捕捉产品功能需求，强调以用户为中心的设计思维。

## 核心概念

### 用户故事格式
- **经典格式**: "作为[角色]，我想要[功能]，以便于[价值]"
- **3C原则**: Card(卡片), Conversation(对话), Confirmation(确认)
- **INVEST标准**: Independent(独立), Negotiable(可协商), Valuable(有价值), Estimable(可估算), Small(小), Testable(可测试)

### 用户故事层级
- **Epic(史诗)**: 大型用户故事，需要分解成多个小 story
- **Story(故事)**: 可在一个迭代周期内完成的用户功能描述
- **Task(任务)**: 实现 story 所需的具体技术任务

### 验收标准 (Acceptance Criteria)
- 定义故事完成的明确条件
- 使用 Given-When-Then 格式
- 确保开发和测试有一致的理解

## 实现方式 / 应用方法

### 编写用户故事步骤
1. **识别用户角色**: 创建用户画像(Persona)
2. **梳理用户旅程**: 理解用户与产品的交互流程
3. **编写故事**: 遵循3C原则，使用标准格式
4. **定义验收标准**: 明确完成定义(DoD)
5. **估算与排序**: 使用故事点(Story Points)估算工作量

### 故事拆分技术
- 按业务流程拆分
- 按数据边界拆分
- 按操作类型拆分(CRUD)
- 按接受/拒绝路径拆分

### 估算方法
- **规划扑克(Planning Poker)**: 团队集体估算
- **T恤尺码**: S/M/L/XL 快速估算
- **斐波那契数列**: 1, 2, 3, 5, 8, 13, 21...

## 应用场景

- **敏捷开发**: Scrum、Kanban 团队需求管理
- **产品规划**: 将大功能分解为可交付的小单元
- **需求沟通**: 作为业务与开发的沟通桥梁
- **迭代规划**: Sprint Planning 的基础输入
- **MVP定义**: 确定最小可行产品的功能范围

## 面试要点

1. **如何写好用户故事?** 遵循INVEST原则，关注用户价值
2. **Epic和Story的区别?** Epic是大的业务目标，Story是可交付的功能单元
3. **如何处理技术债务?** 使用技术故事或预留重构时间
4. **故事点 vs 工时?** 故事点是相对估算，与工时不同
5. **Spike是什么?** 用于技术调研的用户故事

## 相关概念

### 产品管理
- [Scrum框架](./scrum.md) - Sprint中的用户故事
- [看板方法](./kanban.md) - 看板中的工作项
- [敏捷开发](./agile.md) - 敏捷需求管理
- [用户研究](./user-research.md) - 用户角色识别

### 软件工程
- [需求工程](../software-engineering/requirements-engineering.md) - 需求规格化方法
- [单元测试](../software-engineering/unit-testing.md) - 验收标准与测试

### 数据结构
- [树](../computer-science/data-structures/tree.md) - 史诗-故事-任务层级

### 系统实现
- [GitLab CI](../cloud-devops/gitlab-ci.md) - 故事验收自动化
---

**相关知识点**: [敏捷宣言](https://agilemanifesto.org/) | [用户故事地图](https://www.jpattonassociates.com/user-story-mapping/)
