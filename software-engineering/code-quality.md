# 代码质量 (Code Quality)

## 概念

代码质量（Code Quality）是指代码满足明确需求和隐性期望的程度，包括可读性、可维护性、可测试性、可靠性等维度。

> **核心思想**: 高质量的代码是团队协作和长期维护的基础。

## 质量维度

| 维度 | 描述 | 衡量方式 |
|------|------|----------|
| **可读性** | 代码易于理解 | 代码审查、圈复杂度 |
| **可维护性** | 易于修改和扩展 | 耦合度、内聚性 |
| **可测试性** | 易于编写测试 | 测试覆盖率 |
| **可靠性** | 稳定运行无错误 | 缺陷密度 |
| **性能** | 响应速度和资源使用 | 响应时间、内存占用 |
| **安全性** | 抵御安全威胁 | 漏洞扫描 |

## 代码异味 (Code Smells)

常见的不良代码特征：

- **长方法** - 方法超过20行
- **大类** - 类承担过多职责
- **重复代码** - 复制粘贴的代码
- **过长参数列表** - 参数超过4个
- **全局状态** - 过度使用全局变量

## 提升代码质量的方法

```
1. 代码审查 (Code Review)
   └── 团队相互检查，发现潜在问题

2. 单元测试
   └── 自动化测试保障代码行为

3. 静态分析
   └── SonarQube、ESLint等工具扫描

4. 重构
   └── 持续改善代码结构

5. 设计模式
   └── 应用成熟的解决方案
```

## 相关概念

### 软件工程
- [单元测试](./unit-testing.md) - 自动化验证代码行为
- [代码审查](./code-review.md) - 人工检查代码质量
- [重构](./refactoring.md) - 改善现有代码结构
- [设计模式](./design-patterns.md) - 可复用的设计方案
- [SOLID原则](./solid-principles.md) - 面向对象设计原则
- [TDD](./testing/tdd.md) - 测试驱动提升代码质量
- [代码覆盖率](./testing/code-coverage.md) - 量化测试完整性
- [技术债务](./technical-debt.md) - 质量问题的累积成本

### Cloud与DevOps
- [CI/CD](../cloud-devops/cicd/github-actions.md) - 持续集成保障代码质量
- [DevSecOps](../security/application-security/devsecops.md) - 安全左移实践

### 安全
- [常见漏洞](../security/common-vulnerabilities.md) - 代码安全缺陷
- [代码审计](../security/application-security/code-audit.md) - 源代码安全检查

### 参考资料
- [时间复杂度](../references/time-complexity.md) - 性能评估基础
