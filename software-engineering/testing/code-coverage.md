# 代码覆盖率 (Code Coverage)

## 概念

代码覆盖率（Code Coverage）是一种**质量度量指标**，用于衡量测试用例对源代码的覆盖程度。

> **核心思想**: 量化测试完整性，发现未测试的代码区域。

## 覆盖率类型

| 类型 | 定义 | 目标 |
|------|------|------|
| **行覆盖** (Line) | 执行的代码行比例 | > 80% |
| **分支覆盖** (Branch) | 执行的分支比例 | > 70% |
| **函数覆盖** (Function) | 调用的函数比例 | > 90% |
| **语句覆盖** (Statement) | 执行的语句比例 | > 80% |
| **条件覆盖** (Condition) | 布尔条件的真假分支 | > 70% |

## 工具推荐

| 语言 | 工具 |
|------|------|
| Java | JaCoCo, Cobertura |
| Python | pytest-cov, coverage.py |
| JavaScript | Istanbul, nyc |
| Go | go test -cover |
| C# | dotCover, OpenCover |

## 覆盖率误区

⚠️ **警告**:
```
高覆盖率 ≠ 高质量测试
- 100%覆盖率也可能有bug
- 覆盖代码不代表验证正确
- 不要为追求覆盖率而写无效测试
```

## 最佳实践

1. **设定合理目标**: 80%行覆盖通常是合理的起点
2. **关注核心逻辑**: 优先覆盖业务关键路径
3. **分支覆盖更重要**: 比行覆盖更能发现遗漏场景
4. **结合代码审查**: 覆盖率 + 人工审查 = 质量保证


## 相关概念

### 软件工程

- [单元测试](../unit-testing.md) - 覆盖率的基础
- [TDD](./tdd.md) - 测试驱动开发自然产生高覆盖率
- [代码质量](../code-quality.md) - 覆盖率是质量指标之一
- [静态分析](../code-review.md) - 与覆盖率互补的质量手段

#### 计算机科学基础

- [分支与路径分析](../../computer-science/algorithms/graph-traversal.md) - 理解代码执行路径
- [并发控制覆盖](../../computer-science/systems/synchronization.md) - 多线程代码的覆盖率挑战
- [复杂度评估](../../computer-science/algorithms/sorting.md) - 测试用例设计与算法复杂度
