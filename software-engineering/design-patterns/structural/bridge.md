# 桥接模式 (Bridge Pattern)

## 概念

桥接模式（Bridge Pattern）是一种**结构型设计模式**，它将抽象部分与实现部分分离，使它们可以独立变化。桥接模式使用组合关系代替继承关系，从而降低抽象和实现之间的耦合度。

> **核心思想**: 将继承关系转化为组合关系，抽象和实现可以沿着各自的维度独立扩展。

```
传统继承方式（类爆炸）：                    桥接模式（组合方式）：
                                              
     Shape                                    Shape
       │                              ┌────────┴────────┐
   ┌───┴───┐                          ▼                 ▼
 Circle  Square                    Abstraction      Implementation
   │       │                           │                  │
  ┌┴┐    ┌┴┐                   ┌──────┴──────┐    ┌──────┴──────┐
  │ │    │ │                   Refined       │    ConcreteImplA│
  ▼ ▼    ▼ ▼                   Abstraction   │    ConcreteImplB│
BlueCircle RedCircle                          │                 │
RedSquare  BlueSquare                         └─────────────────┘
                                              
  4个形状 × 4个颜色 = 16个类                    4个形状 + 4个颜色 = 8个类
```

---

## 原理

### 为什么需要桥接模式？

1. **避免类爆炸**: 当类有多个独立变化维度时，继承会导致类数量指数增长
2. **解耦抽象和实现**: 抽象部分和实现部分可以独立变化，互不影响
3. **提高可扩展性**: 增加新维度时只需添加对应类，无需修改现有代码
4. **隐藏实现细节**: 客户端只需要关注抽象接口

### 核心角色

| 角色 | 职责 |
|------|------|
| Abstraction | 定义抽象接口，维护对 Implementor 的引用 |
| RefinedAbstraction | 扩展抽象接口 |
| Implementor | 定义实现类接口 |
| ConcreteImplementor | 具体实现类 |

### 优缺点

**优点：**
- 分离抽象和实现，两者可以独立扩展
- 符合开闭原则
- 符合单一职责原则
- 隐藏实现细节，提高安全性

**缺点：**
- 增加系统理解难度
- 需要正确识别独立变化的维度

---

## 实现方式

### 1. Python 实现

```python
from abc import ABC, abstractmethod


# 实现化角色 - 颜色接口
class Color(ABC):
    @abstractmethod
    def apply_color(self):
        pass


# 具体实现化 - 红色
class RedColor(Color):
    def apply_color(self):
        return "红色"


# 具体实现化 - 蓝色
class BlueColor(Color):
    def apply_color(self):
        return "蓝色"


# 具体实现化 - 绿色
class GreenColor(Color):
    def apply_color(self):
        return "绿色"


# 抽象化角色 - 形状
class Shape(ABC):
    def __init__(self, color: Color):
        self.color = color
    
    @abstractmethod
    def draw(self):
        pass


# 扩展抽象化 - 圆形
class Circle(Shape):
    def draw(self):
        return f"画一个 {self.color.apply_color()} 的圆形"


# 扩展抽象化 - 正方形
class Square(Shape):
    def draw(self):
        return f"画一个 {self.color.apply_color()} 的正方形"


# 扩展抽象化 - 三角形
class Triangle(Shape):
    def draw(self):
        return f"画一个 {self.color.apply_color()} 的三角形"


# 使用
red = RedColor()
blue = BlueColor()
green = GreenColor()

red_circle = Circle(red)
blue_square = Square(blue)
green_triangle = Triangle(green)

print(red_circle.draw())      # 画一个 红色 的圆形
print(blue_square.draw())     # 画一个 蓝色 的正方形
print(green_triangle.draw())  # 画一个 绿色 的三角形
```

### 2. 消息发送示例

```python
from abc import ABC, abstractmethod
from typing import List


# 实现化角色 - 消息发送方式
class MessageSender(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str):
        pass


# 具体实现化 - 邮件发送
class EmailSender(MessageSender):
    def send(self, message: str, recipient: str):
        print(f"发送邮件给 {recipient}: {message}")


# 具体实现化 - 短信发送
class SmsSender(MessageSender):
    def send(self, message: str, recipient: str):
        print(f"发送短信给 {recipient}: {message}")


# 具体实现化 - 微信发送
class WeChatSender(MessageSender):
    def send(self, message: str, recipient: str):
        print(f"发送微信给 {recipient}: {message}")


# 抽象化角色 - 消息
class Message(ABC):
    def __init__(self, sender: MessageSender):
        self.sender = sender
    
    @abstractmethod
    def send(self, content: str, recipient: str):
        pass


# 扩展抽象化 - 普通消息
class NormalMessage(Message):
    def send(self, content: str, recipient: str):
        formatted = f"[普通消息] {content}"
        self.sender.send(formatted, recipient)


# 扩展抽象化 - 紧急消息
class UrgentMessage(Message):
    def send(self, content: str, recipient: str):
        formatted = f"【紧急】{content}"
        self.sender.send(formatted, recipient)


# 扩展抽象化 - 群发消息
class BroadcastMessage(Message):
    def __init__(self, sender: MessageSender, recipients: List[str]):
        super().__init__(sender)
        self.recipients = recipients
    
    def send(self, content: str, recipient: str = None):
        formatted = f"[群发] {content}"
        for r in self.recipients:
            self.sender.send(formatted, r)


# 使用场景
email_sender = EmailSender()
sms_sender = SmsSender()

# 紧急邮件
urgent_email = UrgentMessage(email_sender)
urgent_email.send("系统故障，请立即处理！", "admin@company.com")

# 普通短信
normal_sms = NormalMessage(sms_sender)
normal_sms.send("您的验证码是 123456", "13800138000")

# 群发邮件
broadcast_email = BroadcastMessage(email_sender, ["user1@test.com", "user2@test.com"])
broadcast_email.send("周末愉快！")
```

### 3. Java 实现示例

```java
// 实现化角色 - 数据库驱动接口
public interface Driver {
    void connect();
    void execute(String sql);
    void disconnect();
}

// 具体实现化 - MySQL 驱动
public class MySQLDriver implements Driver {
    @Override
    public void connect() {
        System.out.println("连接到 MySQL 数据库");
    }
    
    @Override
    public void execute(String sql) {
        System.out.println("MySQL 执行: " + sql);
    }
    
    @Override
    public void disconnect() {
        System.out.println("断开 MySQL 连接");
    }
}

// 具体实现化 - PostgreSQL 驱动
public class PostgreSQLDriver implements Driver {
    @Override
    public void connect() {
        System.out.println("连接到 PostgreSQL 数据库");
    }
    
    @Override
    public void execute(String sql) {
        System.out.println("PostgreSQL 执行: " + sql);
    }
    
    @Override
    public void disconnect() {
        System.out.println("断开 PostgreSQL 连接");
    }
}

// 抽象化角色 - 数据库操作
public abstract class Database {
    protected Driver driver;
    
    public Database(Driver driver) {
        this.driver = driver;
    }
    
    public abstract void query(String sql);
}

// 扩展抽象化 - 简单查询
public class SimpleDatabase extends Database {
    public SimpleDatabase(Driver driver) {
        super(driver);
    }
    
    @Override
    public void query(String sql) {
        driver.connect();
        driver.execute(sql);
        driver.disconnect();
    }
}

// 扩展抽象化 - 连接池查询
public class PooledDatabase extends Database {
    public PooledDatabase(Driver driver) {
        super(driver);
    }
    
    @Override
    public void query(String sql) {
        System.out.println("从连接池获取连接");
        driver.execute(sql);
        System.out.println("归还连接到连接池");
    }
}

// 使用
public class Client {
    public static void main(String[] args) {
        Driver mysqlDriver = new MySQLDriver();
        Driver pgDriver = new PostgreSQLDriver();
        
        Database simpleMySQL = new SimpleDatabase(mysqlDriver);
        simpleMySQL.query("SELECT * FROM users");
        
        Database pooledPG = new PooledDatabase(pgDriver);
        pooledPG.query("SELECT * FROM orders");
    }
}
```

---

## 示例

### 跨平台 GUI 组件

```python
from abc import ABC, abstractmethod


# 实现化角色 - 操作系统接口
class OSPlatform(ABC):
    @abstractmethod
    def render_window(self, title: str):
        pass
    
    @abstractmethod
    def render_button(self, text: str):
        pass
    
    @abstractmethod
    def render_text(self, content: str):
        pass


# 具体实现化 - Windows 平台
class WindowsPlatform(OSPlatform):
    def render_window(self, title: str):
        return f"[Windows 窗口] {title}"
    
    def render_button(self, text: str):
        return f"[Windows 按钮] {text}"
    
    def render_text(self, content: str):
        return f"[Windows 文本] {content}"


# 具体实现化 - macOS 平台
class MacOSPlatform(OSPlatform):
    def render_window(self, title: str):
        return f"[macOS 窗口] {title}"
    
    def render_button(self, text: str):
        return f"[macOS 按钮] {text}"
    
    def render_text(self, content: str):
        return f"[macOS 文本] {content}"


# 具体实现化 - Linux 平台
class LinuxPlatform(OSPlatform):
    def render_window(self, title: str):
        return f"[Linux 窗口] {title}"
    
    def render_button(self, text: str):
        return f"[Linux 按钮] {text}"
    
    def render_text(self, content: str):
        return f"[Linux 文本] {content}"


# 抽象化角色 - UI 组件
class UIComponent(ABC):
    def __init__(self, platform: OSPlatform):
        self.platform = platform
    
    @abstractmethod
    def render(self):
        pass


# 扩展抽象化 - 对话框
class Dialog(UIComponent):
    def __init__(self, platform: OSPlatform, title: str, message: str):
        super().__init__(platform)
        self.title = title
        self.message = message
    
    def render(self):
        return f"""
{self.platform.render_window(self.title)}
  ├── {self.platform.render_text(self.message)}
  ├── {self.platform.render_button("确定")}
  └── {self.platform.render_button("取消")}
        """.strip()


# 扩展抽象化 - 登录表单
class LoginForm(UIComponent):
    def __init__(self, platform: OSPlatform):
        super().__init__(platform)
    
    def render(self):
        return f"""
{self.platform.render_window("用户登录")}
  ├── {self.platform.render_text("用户名: __________")}
  ├── {self.platform.render_text("密码: __________")}
  └── {self.platform.render_button("登录")}
        """.strip()


# 使用场景 - 跨平台渲染
windows = WindowsPlatform()
macos = MacOSPlatform()
linux = LinuxPlatform()

win_dialog = Dialog(windows, "警告", "磁盘空间不足！")
print(win_dialog.render())

mac_login = LoginForm(macos)
print(mac_login.render())
```

### UML 图

```
┌─────────────────────────────────────────────────────────────────┐
│                         桥接模式 UML                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐     ┌─────────────────────────┐    │
│  │  <<interface>>          │     │  <<interface>>          │    │
│  │      Color              │     │       Driver            │    │
│  │  +apply_color()         │     │  +connect()             │    │
│  └─────────────────────────┘     │  +execute(sql)          │    │
│           ▲                      │  +disconnect()          │    │
│           │                      └─────────────────────────┘    │
│  ┌────────┴────────┐                      ▲                     │
│  │                 │                      │                     │
│  ▼                 ▼           ┌──────────┴──────────┐         │
│ ┌───────┐     ┌────────┐       │                     │         │
│ │  Red  │     │  Blue  │  ┌────▼────┐        ┌───────▼──────┐  │
│ └───────┘     └────────┘  │  MySQL  │        │  PostgreSQL  │  │
│                           │ Driver  │        │    Driver    │  │
│                           └─────────┘        └──────────────┘  │
│                                                                 │
│                           ┌─────────────────────────┐          │
│                           │       Database          │──────────┘
│                           │  (Abstraction)          │  has-a
│                           │  -driver: Driver        │
│                           │  +query(sql)            │
│                           └─────────────────────────┘
│                                    ▲
│                           ┌────────┴────────┐
│                           │                 │
│                    ┌──────▼──────┐   ┌─────▼──────┐
│                    │   Simple    │   │   Pooled   │
│                    │   Database  │   │   Database │
│                    │             │   │            │
│                    └─────────────┘   └────────────┘
│
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

1. **Q: 什么是桥接模式？**
   
   A: 桥接模式是一种结构型设计模式，将抽象部分与实现部分分离，使它们可以独立变化。通过组合关系代替继承关系，解决了多维度变化导致的类爆炸问题。

2. **Q: 桥接模式与策略模式的区别？**
   
   A: 桥接模式关注**抽象和实现的分离**，通常有两个或多个独立变化的维度；策略模式关注**算法的替换**，只有一个行为维度。桥接模式从类设计的角度出发，策略模式从行为变化的角度出发。

3. **Q: 如何判断是否使用桥接模式？**
   
   A: 当出现以下情况时考虑使用：
   - 类有两个独立变化的维度
   - 继承导致类数量爆炸式增长
   - 需要在多个平台上实现相同功能（跨平台）
   - 需要运行时切换实现

4. **Q: 桥接模式与装饰器模式的区别？**
   
   A: 桥接模式分离抽象和实现，两者可以独立扩展；装饰器模式动态添加功能，保持接口不变。桥接模式关注的是解耦，装饰器模式关注的是增强。

5. **Q: 实际应用场景有哪些？**
   
   A: 常见场景包括：
   - JDBC 驱动（数据库类型 × 连接方式）
   - GUI 框架（组件类型 × 平台渲染）
   - 消息系统（消息类型 × 发送方式）
   - 支付方式（支付类型 × 风控策略）

---

## 相关概念

### 数据结构
- [接口与抽象类](../../oop-design.md) - 多态的基础
- [树](../../../computer-science/data-structures/tree.md) - 组合结构实现

### 算法
- [动态规划](../../../computer-science/algorithms/dynamic-programming.md) - 多维度问题求解

### 复杂度分析
- [时间复杂度](../../../references/time-complexity.md) - 桥接调用开销分析
- [空间复杂度](../../../references/space-complexity.md) - 对象组合内存占用

### 系统实现
- [数据库连接池](../../../computer-science/databases/indexing.md) - JDBC 桥接实现
- [操作系统](../../../computer-science/systems/os.md) - 硬件抽象层

### 设计模式
- [适配器模式](./adapter.md) - 接口转换
- [策略模式](../behavioral/strategy.md) - 算法封装与替换
- [装饰器模式](./decorator.md) - 功能动态增强
- [抽象工厂](../creational/abstract-factory.md) - 产品族创建


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

- [组合优于继承](../../oop-design.md) - 桥接模式的核心设计哲学
- [单一职责原则](../../solid-principles.md) - 抽象与实现职责分离
- [开闭原则](../../solid-principles.md) - 扩展抽象或实现无需修改对方
- [策略模式](../behavioral/strategy.md) - 运行时切换实现行为的相似模式
- [依赖注入](../../architecture-patterns/dependency-injection.md) - 通过注入实现类完成桥接

### 应用场景关联

- [面向对象设计](../../oop-design.md) - 多维类设计的解耦技术
- [软件架构](../../architecture-patterns.md) - 分层架构中的抽象层与实现层分离


#### 计算机科学基础

- [树结构的表示与实现分离](../../../computer-science/data-structures/tree.md) - 树的抽象接口与具体实现
- [图的存储结构桥接](../../../computer-science/data-structures/graph.md) - 邻接表与邻接矩阵的抽象统一
- [堆的实现抽象](../../../computer-science/data-structures/heap.md) - 堆接口与底层数组实现分离

---

## 相关引用 (References)

- 返回：[设计模式总览](../../design-patterns.md)
- 相关： - 接口转换
- 相关： - 算法封装
- 原理：[SOLID原则](../../solid-principles.md)
