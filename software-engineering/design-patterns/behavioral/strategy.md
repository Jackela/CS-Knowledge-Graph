# 策略模式 (Strategy Pattern)

## 概念

策略模式（Strategy Pattern）是一种**行为型设计模式**，定义算法族，分别封装，让它们可以互相替换。

> **核心思想**: 将算法独立出来，运行时动态选择。

---

## 原理

### 结构

```
Context --uses--> Strategy <|-- ConcreteStrategyA
                      <|-- ConcreteStrategyB
```

### 代码示例

```python
from abc import ABC, abstractmethod
from typing import List

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]:
        pass

class QuickSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class MergeSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        return self._merge(left, right)
    
    def _merge(self, left: List[int], right: List[int]) -> List[int]:
        result = []
        while left and right:
            result.append(left.pop(0) if left[0] < right[0] else right.pop(0))
        return result + left + right

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: SortStrategy):
        self._strategy = strategy
    
    def sort(self, data: List[int]) -> List[int]:
        return self._strategy.sort(data)
```

---

## 使用场景

1. **多种算法**: 排序、压缩、加密
2. **避免条件语句**: 替代大量 if-else
3. **运行时切换**: 根据配置选择策略

---

## 优点

- 算法独立变化
- 符合开闭原则
- 消除条件语句

---

## 面试要点

1. **vs 状态模式**: 策略是算法选择，状态是状态转换
2. **Spring 中的 @Strategy**: 依赖注入实现

---

## 相关概念

- [模板方法模式](./template-method.md)
- [命令模式](./command.md)
