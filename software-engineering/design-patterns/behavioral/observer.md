# 观察者模式 (Observer Pattern)

## 概念

观察者模式（Observer Pattern）是一种**行为型设计模式**，定义对象间一对多依赖关系，当一个对象状态改变时，所有依赖者自动收到通知。

> **核心思想**: 订阅-发布机制，解耦观察者与主题。

---

## 原理

### 角色

1. **Subject (主题)**: 被观察的对象
2. **Observer (观察者)**: 接收通知的对象
3. **ConcreteSubject**: 具体主题实现
4. **ConcreteObserver**: 具体观察者实现

### UML 结构

```
    Subject <|-- ConcreteSubject
    + attach()
    + detach()  
    + notify()
    
    Observer <|-- ConcreteObserver
    + update()
```

---

## 实现

### Python 示例

```python
from abc import ABC, abstractmethod
from typing import List

class Observer(ABC):
    @abstractmethod
    def update(self, message: str):
        pass

class Subject:
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer):
        self._observers.append(observer)
    
    def detach(self, observer: Observer):
        self._observers.remove(observer)
    
    def notify(self, message: str):
        for observer in self._observers:
            observer.update(message)

class NewsPublisher(Subject):
    def publish(self, news: str):
        print(f"发布新闻: {news}")
        self.notify(news)

class EmailSubscriber(Observer):
    def update(self, message: str):
        print(f"邮件通知: {message}")

class SMSSubscriber(Observer):
    def update(self, message: str):
        print(f"短信通知: {message}")
```

---

## 使用场景

1. **事件处理**: GUI 事件监听
2. **消息队列**: Pub/Sub 模式
3. **数据绑定**: MVVM 框架
4. **股票市场**: 价格变动通知

---

## 推 vs 拉模式

**推模式 (Push)**:
```python
def notify(self, data):
    for observer in self._observers:
        observer.update(data)  # 主动推送数据
```

**拉模式 (Pull)**:
```python
def update(self, subject):
    data = subject.get_data()  # 观察者主动拉取
```

---

## 面试要点

1. **vs 发布订阅**: 观察者直接通信，发布订阅通过中间件
2. **内存泄漏**: 注意移除观察者引用
3. **通知顺序**: 观察者之间不应有依赖

---

## 相关概念

- [事件驱动架构](../../architecture-patterns/event-driven.md)
- [消息队列](../../../cloud-devops/messaging.md)
