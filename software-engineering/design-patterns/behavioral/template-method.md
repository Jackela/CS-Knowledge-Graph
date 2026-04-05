# 模板方法模式 (Template Method Pattern)

## 概念

模板方法模式（Template Method Pattern）是一种**行为型设计模式**，在父类中定义算法的骨架，将某些步骤延迟到子类中实现。

> **核心思想**: 复用算法结构，个性化可变步骤。

---

## 原理

### 结构

```
AbstractClass
├── templateMethod()  # 定义算法骨架
├── step1()           # 通用步骤（已实现）
├── step2()           # 通用步骤（已实现）
├── hook()            # 钩子方法（可选实现）
└── abstract step3()  # 抽象步骤（子类实现）

ConcreteClass extends AbstractClass
└── step3()           # 实现抽象步骤
```

### 角色

1. **AbstractClass（抽象类）**: 定义模板方法和基本步骤
2. **ConcreteClass（具体类）**: 实现抽象步骤
3. **Hook（钩子）**: 可选扩展点

---

## 实现

### Python 示例

```python
from abc import ABC, abstractmethod

class DataMiner(ABC):
    """数据挖掘模板"""
    
    def mine(self, path: str):
        """模板方法：定义算法骨架"""
        file = self._open(path)
        raw_data = self._extract(file)
        data = self._parse(raw_data)
        analysis = self._analyze(data)
        self._send_report(analysis)
        self._close(file)
    
    def _open(self, path: str):
        print(f"打开文件: {path}")
        return open(path, 'r')
    
    def _close(self, file):
        print("关闭文件")
        file.close()
    
    @abstractmethod
    def _extract(self, file):
        """抽象步骤：数据提取"""
        pass
    
    @abstractmethod
    def _parse(self, raw_data):
        """抽象步骤：数据解析"""
        pass
    
    def _analyze(self, data):
        """通用步骤：数据分析"""
        return f"分析 {len(data)} 条记录"
    
    def _send_report(self, analysis):
        """钩子方法：发送报告（可选覆盖）"""
        print(f"报告: {analysis}")


class PDFDataMiner(DataMiner):
    """PDF数据挖掘"""
    
    def _extract(self, file):
        print("从PDF提取数据...")
        return file.read()
    
    def _parse(self, raw_data):
        print("解析PDF内容...")
        return raw_data.split('\n')


class CSVDataMiner(DataMiner):
    """CSV数据挖掘"""
    
    def _extract(self, file):
        print("从CSV提取数据...")
        return file.readlines()
    
    def _parse(self, raw_data):
        print("解析CSV内容...")
        return [line.strip().split(',') for line in raw_data]
    
    def _send_report(self, analysis):
        """覆盖钩子：自定义报告格式"""
        print(f"[CSV专项] {analysis}")


# 使用
pdf_miner = PDFDataMiner()
pdf_miner.mine("data.pdf")

csv_miner = CSVDataMiner()
csv_miner.mine("data.csv")
```

---

## 使用场景

1. **算法骨架复用**: 多个类有相似的算法流程
2. **框架设计**: 允许用户扩展框架行为
3. **生命周期回调**: 如Servlet的doGet/doPost

---

## 模板方法 vs 策略模式

| 特性 | 模板方法 | 策略模式 |
|------|----------|----------|
| 复用级别 | 算法结构 | 算法本身 |
| 实现方式 | 继承 | 组合 |
| 灵活性 | 较低 | 较高 |
| 耦合度 | 较高 | 较低 |

---

## 面试要点

1. **好莱坞原则**: "别调用我们，我们会调用你"
2. **钩子方法**: 提供可选的扩展点
3. **避免过度设计**: 简单场景直接用策略模式

---

## 相关概念

### 设计模式
- [策略模式](./strategy.md) - 运行时替换算法
- [命令模式](./command.md) - 将请求封装为对象
- [工厂模式](../creational/factory.md) - 对象创建模板

### 面向对象
- [SOLID原则](../../solid-principles.md) - 设计原则基础
- [继承 vs 组合](../../oop-design.md) - 代码复用方式

### 实际应用
- [单元测试](../../unit-testing.md) - 测试框架的setUp/tearDown
- [框架设计](../../architecture-patterns.md) - 框架扩展机制
