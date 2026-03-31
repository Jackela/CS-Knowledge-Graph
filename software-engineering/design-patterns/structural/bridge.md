## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念 (Concept)

**桥接模式 (Bridge Pattern)** 是一种结构型设计模式，它将抽象部分与实现部分分离，使它们可以独立变化。

桥接模式的核心思想是**组合优于继承**。当类存在两个独立变化的维度时（如形状和颜色、设备和遥控器），使用桥接模式避免继承爆炸。

```
┌─────────────────────────────────────────────────────────────┐
│                     桥接模式 (Bridge)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Abstraction ──────────▶ Implementation                    │
│   (抽象部分)               (实现部分接口)                    │
│   ├─ impl: Implementation  ├─ operationImpl()               │
│   ├─ operation()               ▲                          │
│   └─ refineAbstraction()       │                          │
│                                │                          │
│            ┌───────────────────┼───────────────────┐        │
│            ▼                   ▼                   ▼        │
│    ConcreteImplA      ConcreteImplB      ConcreteImplC      │
│    (实现A)            (实现B)            (实现C)            │
│                                                             │
│   分离前: Shape ──▶ Rectangle, Circle, RedRect, BlueRect... │
│   分离后: Shape ──▶ Color ──▶ Red, Blue                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 设计原则 (Principle)

桥接模式遵循以下设计原则：

1. **组合优于继承 (Favor Composition Over Inheritance)**：使用组合关系替代多层继承
2. **单一职责原则 (Single Responsibility Principle)**：抽象和实现各自独立变化
3. **开闭原则 (Open/Closed Principle)**：扩展抽象或实现无需修改对方

**解决的问题**：
- 避免类爆炸（n×m 个类 → n+m 个类）
- 抽象和实现可以独立演进
- 运行时可以切换实现

---

## 实现示例 (Example)

### 1. 形状与颜色的分离

```python
from abc import ABC, abstractmethod

# ============== 实现部分：颜色 ==============

class Color(ABC):
    """颜色 - 实现部分接口"""
    
    @abstractmethod
    def apply_color(self) -> str:
        pass

class Red(Color):
    def apply_color(self) -> str:
        return "红色"

class Blue(Color):
    def apply_color(self) -> str:
        return "蓝色"

class Green(Color):
    def apply_color(self) -> str:
        return "绿色"

# ============== 抽象部分：形状 ==============

class Shape(ABC):
    """形状 - 抽象部分"""
    
    def __init__(self, color: Color):
        self.color = color
    
    @abstractmethod
    def draw(self) -> str:
        pass
    
    @abstractmethod
    def get_area(self) -> float:
        pass

class Circle(Shape):
    """圆形"""
    
    def __init__(self, color: Color, radius: float):
        super().__init__(color)
        self.radius = radius
    
    def draw(self) -> str:
        return f"绘制{self.color.apply_color()}圆形"
    
    def get_area(self) -> float:
        import math
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    """矩形"""
    
    def __init__(self, color: Color, width: float, height: float):
        super().__init__(color)
        self.width = width
        self.height = height
    
    def draw(self) -> str:
        return f"绘制{self.color.apply_color()}矩形"
    
    def get_area(self) -> float:
        return self.width * self.height

class Triangle(Shape):
    """三角形"""
    
    def __init__(self, color: Color, base: float, height: float):
        super().__init__(color)
        self.base = base
        self.height = height
    
    def draw(self) -> str:
        return f"绘制{self.color.apply_color()}三角形"
    
    def get_area(self) -> float:
        return 0.5 * self.base * self.height

# ============== 使用 ==============

# 创建不同颜色的形状（自由组合）
red_circle = Circle(Red(), 5)
blue_rectangle = Rectangle(Blue(), 10, 20)
green_triangle = Triangle(Green(), 8, 12)

print(red_circle.draw())        # 绘制红色圆形
print(blue_rectangle.draw())    # 绘制蓝色矩形
print(green_triangle.draw())    # 绘制绿色三角形

# 运行时动态改变颜色
print("\n--- 动态改变颜色 ---")
blue_circle = Circle(Blue(), 5)
print(blue_circle.draw())       # 绘制蓝色圆形
```

### 2. 设备与遥控器的桥接

```python
from abc import ABC, abstractmethod

# ============== 实现部分：设备 ==============

class Device(ABC):
    """设备接口 - 实现部分"""
    
    @abstractmethod
    def is_enabled(self) -> bool:
        pass
    
    @abstractmethod
    def enable(self):
        pass
    
    @abstractmethod
    def disable(self):
        pass
    
    @abstractmethod
    def get_volume(self) -> int:
        pass
    
    @abstractmethod
    def set_volume(self, volume: int):
        pass
    
    @abstractmethod
    def get_channel(self) -> int:
        pass
    
    @abstractmethod
    def set_channel(self, channel: int):
        pass

class TV(Device):
    """电视 - 具体实现"""
    
    def __init__(self):
        self._enabled = False
        self._volume = 50
        self._channel = 1
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def enable(self):
        self._enabled = True
        print("电视已开启")
    
    def disable(self):
        self._enabled = False
        print("电视已关闭")
    
    def get_volume(self) -> int:
        return self._volume
    
    def set_volume(self, volume: int):
        self._volume = max(0, min(100, volume))
        print(f"电视音量设置为: {self._volume}")
    
    def get_channel(self) -> int:
        return self._channel
    
    def set_channel(self, channel: int):
        self._channel = channel
        print(f"电视切换到频道: {channel}")

class Radio(Device):
    """收音机 - 具体实现"""
    
    def __init__(self):
        self._enabled = False
        self._volume = 30
        self._channel = 88
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def enable(self):
        self._enabled = True
        print("收音机已开启")
    
    def disable(self):
        self._enabled = False
        print("收音机已关闭")
    
    def get_volume(self) -> int:
        return self._volume
    
    def set_volume(self, volume: int):
        self._volume = max(0, min(100, volume))
        print(f"收音机音量设置为: {self._volume}")
    
    def get_channel(self) -> int:
        return self._channel
    
    def set_channel(self, channel: int):
        self._channel = channel
        print(f"收音机调频到: {channel} FM")

# ============== 抽象部分：遥控器 ==============

class RemoteControl(ABC):
    """遥控器 - 抽象部分"""
    
    def __init__(self, device: Device):
        self.device = device
    
    def toggle_power(self):
        if self.device.is_enabled():
            self.device.disable()
        else:
            self.device.enable()
    
    def volume_up(self):
        self.device.set_volume(self.device.get_volume() + 10)
    
    def volume_down(self):
        self.device.set_volume(self.device.get_volume() - 10)
    
    def channel_up(self):
        self.device.set_channel(self.device.get_channel() + 1)
    
    def channel_down(self):
        self.device.set_channel(self.device.get_channel() - 1)

class AdvancedRemoteControl(RemoteControl):
    """高级遥控器 - 扩展的抽象"""
    
    def mute(self):
        print("静音")
        self.device.set_volume(0)
    
    def set_favorite_channel(self, channel: int):
        print(f"设置收藏频道: {channel}")
        self.device.set_channel(channel)

# ============== 使用 ==============

# 基础遥控器控制电视
tv = TV()
basic_remote = RemoteControl(tv)
basic_remote.toggle_power()   # 开启电视
basic_remote.volume_up()      # 增加音量
basic_remote.channel_up()     # 换台

print("\n--- 切换到收音机 ---")

# 同一个遥控器可以控制不同的设备
radio = Radio()
basic_remote = RemoteControl(radio)
basic_remote.toggle_power()   # 开启收音机
basic_remote.set_channel(105) # 调频

print("\n--- 高级遥控器 ---")

# 高级遥控器
advanced_remote = AdvancedRemoteControl(TV())
advanced_remote.toggle_power()
advanced_remote.set_favorite_channel(5)
advanced_remote.mute()
```

### 3. 消息发送的桥接

```python
from abc import ABC, abstractmethod
from typing import List

# ============== 实现部分：发送方式 ==============

class MessageSender(ABC):
    """消息发送接口 - 实现部分"""
    
    @abstractmethod
    def send_message(self, message: str, recipient: str) -> bool:
        pass

class EmailSender(MessageSender):
    """邮件发送"""
    
    def send_message(self, message: str, recipient: str) -> bool:
        print(f"[Email] To: {recipient}")
        print(f"[Email] Body: {message}")
        return True

class SMSSender(MessageSender):
    """短信发送"""
    
    def send_message(self, message: str, recipient: str) -> bool:
        print(f"[SMS] To: {recipient}")
        print(f"[SMS] Content: {message[:70]}...")  # 短信长度限制
        return True

class PushNotificationSender(MessageSender):
    """推送通知发送"""
    
    def send_message(self, message: str, recipient: str) -> bool:
        print(f"[Push] To device: {recipient}")
        print(f"[Push] Message: {message}")
        return True

# ============== 抽象部分：消息类型 ==============

class Message(ABC):
    """消息 - 抽象部分"""
    
    def __init__(self, sender: MessageSender):
        self.sender = sender
    
    @abstractmethod
    def format_message(self, content: str) -> str:
        pass
    
    def send(self, content: str, recipient: str) -> bool:
        formatted = self.format_message(content)
        return self.sender.send_message(formatted, recipient)

class TextMessage(Message):
    """纯文本消息"""
    
    def format_message(self, content: str) -> str:
        return f"[TEXT] {content}"

class HTMLMessage(Message):
    """HTML格式消息"""
    
    def format_message(self, content: str) -> str:
        return f"<html><body><p>{content}</p></body></html>"

class EncryptedMessage(Message):
    """加密消息"""
    
    def format_message(self, content: str) -> str:
        # 简单模拟加密
        encrypted = ''.join(chr(ord(c) + 1) for c in content)
        return f"[ENCRYPTED] {encrypted}"

# ============== 使用 ==============

# 任意组合消息类型和发送方式
text_email = TextMessage(EmailSender())
html_email = HTMLMessage(EmailSender())
text_sms = TextMessage(SMSSender())
encrypted_push = EncryptedMessage(PushNotificationSender())

# 发送消息
text_email.send("Hello World!", "user@example.com")
html_email.send("Hello World!", "user@example.com")
text_sms.send("Your code is 123456", "+8613800138000")
encrypted_push.send("Secret message", "device_token_123")
```

---

## 使用场景 (Use Cases)

| 场景 | 说明 |
|------|------|
| 多维度变化 | 类有两个以上独立变化的维度（如UI控件的皮肤和平台） |
| 避免继承爆炸 | 避免 n×m 个子类（如20种形状 × 10种颜色 = 200个类） |
| 运行时切换 | 需要在运行时切换实现 |
| 隐藏实现 | 客户端不需要知道具体实现 |
| 跨平台支持 | 不同平台的统一API封装 |

---

## 面试要点 (Interview Points)

**Q1: 桥接模式和策略模式的区别？**

> - **桥接模式**：处理抽象和实现的分离，两个维度可以独立变化，通常用于设计阶段的结构解耦
> - **策略模式**：封装算法族，让算法可以互相替换，通常用于运行时的行为选择
>
> 桥接是"结构"模式，策略是"行为"模式。

**Q2: 桥接模式和适配器模式的区别？**

> - **桥接模式**：预先设计，将抽象和实现分离，目的是使它们独立变化
> - **适配器模式**：事后补救，使不兼容的接口能够工作
>
> 桥接是"前瞻性设计"，适配器是"事后补救"。

**Q3: 如何判断是否需要使用桥接模式？**

> 当遇到以下情况时考虑桥接：
> 1. 类的继承层次呈指数增长（n×m问题）
> 2. 需要在多个维度上扩展功能
> 3. 抽象和实现需要独立变化
> 4. 想在运行时切换实现

**Q4: 桥接模式的优缺点？**

> **优点**：
> - 减少子类数量，避免类爆炸
> - 抽象和实现独立扩展
> - 隐藏实现细节
> - 符合单一职责原则
>
> **缺点**：
> - 增加系统复杂度
> - 需要识别正确的抽象和实现维度

---

## 相关概念

桥接模式与其他设计模式和软件工程概念密切相关：

### 结构型模式对比

| 模式 | 关系说明 |
|------|---------|
| [适配器模式](./adapter.md) | 适配器是事后补救接口不兼容，桥接是前瞻性设计分离抽象与实现 |
| [装饰器模式](./decorator.md) | 装饰器动态添加职责，桥接分离两个独立变化维度 |
| [代理模式](./proxy.md) | 代理控制对象访问，桥接分离抽象与实现以支持独立变化 |
| [外观模式](./facade.md) | 外观简化复杂子系统接口，桥接处理多维度类设计 |
| [组合模式](./composite.md) | 组合处理树形结构的部分-整体关系，桥接处理多维组合 |
| [享元模式](./flyweight.md) | 享元通过共享减少内存，桥接通过分离减少子类数量 |

### 设计原则与架构

- [组合优于继承](../oop-design.md) - 桥接模式的核心设计哲学
- [单一职责原则](../solid-principles.md) - 抽象与实现职责分离
- [开闭原则](../solid-principles.md) - 扩展抽象或实现无需修改对方
- [策略模式](../behavioral/strategy.md) - 运行时切换实现行为的相似模式
- [依赖注入](../architecture-patterns.md) - 通过注入实现类完成桥接

### 应用场景关联

- [面向对象设计](../oop-design.md) - 多维类设计的解耦技术
- [软件架构](../architecture-patterns.md) - 分层架构中的抽象层与实现层分离

---

## 相关引用 (References)

- 返回：[设计模式总览](../../design-patterns.md)
- 相关：[适配器模式](./adapter.md) - 接口转换
- 相关：[策略模式](../behavioral/strategy.md) - 算法封装
- 原理：[SOLID原则](../../solid-principles.md)
