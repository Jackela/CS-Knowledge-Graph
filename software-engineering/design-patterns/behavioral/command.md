# 命令模式 (Command Pattern)

## 概念

命令模式（Command Pattern）是一种**行为型设计模式**，将请求封装为对象，从而可以用不同的请求、队列或日志来参数化其他对象。

> **核心思想**: 解耦请求发送者和接收者，支持撤销、队列、日志等功能。

---

## 原理

### 结构

```
Invoker（调用者）──uses──▶ Command（命令接口）
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
            ConcreteCommand      ConcreteCommand
                    │                     │
                    ▼                     ▼
                  Receiver            Receiver
                （接收者）           （接收者）
```

### 角色

1. **Command（命令接口）**: 声明执行方法
2. **ConcreteCommand（具体命令）**: 绑定接收者和动作
3. **Receiver（接收者）**: 执行实际工作的对象
4. **Invoker（调用者）**: 触发命令执行
5. **Client（客户端）**: 创建并配置命令

---

## 实现

### Python 示例

```python
from abc import ABC, abstractmethod
from typing import List

class Command(ABC):
    """命令接口"""
    
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass


class Light:
    """接收者：灯"""
    def on(self):
        print("灯已打开")
    
    def off(self):
        print("灯已关闭")


class LightOnCommand(Command):
    """开灯命令"""
    def __init__(self, light: Light):
        self._light = light
    
    def execute(self):
        self._light.on()
    
    def undo(self):
        self._light.off()


class LightOffCommand(Command):
    """关灯命令"""
    def __init__(self, light: Light):
        self._light = light
    
    def execute(self):
        self._light.off()
    
    def undo(self):
        self._light.on()


class RemoteControl:
    """调用者：遥控器"""
    def __init__(self):
        self._commands: List[Command] = []
        self._undo_stack: List[Command] = []
    
    def set_command(self, command: Command):
        self._commands.append(command)
    
    def press_button(self, slot: int):
        command = self._commands[slot]
        command.execute()
        self._undo_stack.append(command)
    
    def press_undo(self):
        if self._undo_stack:
            command = self._undo_stack.pop()
            command.undo()


class MacroCommand(Command):
    """宏命令：批量执行"""
    def __init__(self, commands: List[Command]):
        self._commands = commands
    
    def execute(self):
        for cmd in self._commands:
            cmd.execute()
    
    def undo(self):
        for cmd in reversed(self._commands):
            cmd.undo()


# 使用
light = Light()
light_on = LightOnCommand(light)
light_off = LightOffCommand(light)

remote = RemoteControl()
remote.set_command(light_on)
remote.set_command(light_off)

remote.press_button(0)  # 开灯
remote.press_undo()     # 撤销（关灯）
```

---

## 使用场景

1. **撤销/重做功能**: 编辑器、绘图软件
2. **任务队列**: 异步任务处理
3. **日志记录**: 操作日志和回放
4. **事务系统**: 数据库事务

---

## 优点

- 解耦发送者和接收者
- 支持撤销/重做
- 支持命令组合（宏命令）
- 支持日志和审计

---

## 面试要点

1. **vs 策略模式**: 命令是行为封装，策略是算法替换
2. **事务实现**: 用命令模式实现原子操作
3. **队列应用**: 工作队列、线程池

---

## 相关概念

### 设计模式
- [观察者模式](./observer.md) - 事件通知机制
- [模板方法模式](./template-method.md) - 算法骨架
- [备忘录模式](./memento.md) - 状态保存（配合撤销）

### 系统实现
- [事务](../../../computer-science/databases/transaction-acid.md) - 原子操作保障

### 软件工程
- [事件驱动架构](../../architecture-patterns/event-driven.md) - 命令的事件化应用
- [CQRS](../../architecture-patterns/cqrs.md) - 命令查询分离
