# 抽象工厂模式 (Abstract Factory Pattern)



## 概念



抽象工厂模式（Abstract Factory Pattern）是一种**创建型设计模式**，提供一个创建一系列相关或相互依赖对象的接口，而无需指定它们具体的类。



> **核心思想**: 创建相关对象的家族，而不需要明确指定具体类。



```

┌─────────────────────────────────────────────────────────────────┐

│                         抽象工厂                                │

│                    ┌─────────────────────┐                      │

│                    │   AbstractFactory   │                      │

│                    │  createProductA()   │                      │

│                    │  createProductB()   │                      │

│                    └──────────┬──────────┘                      │

└───────────────────────────────┼─────────────────────────────────┘

                                │

              ┌─────────────────┴─────────────────┐

              ▼                                   ▼

    ┌─────────────────────┐           ┌─────────────────────┐

    │   ConcreteFactory1  │           │   ConcreteFactory2  │

    │  ┌───────────────┐  │           │  ┌───────────────┐  │

    │  │  ProductA1    │  │           │  │  ProductA2    │  │

    │  └───────────────┘  │           │  └───────────────┘  │

    │  ┌───────────────┐  │           │  ┌───────────────┐  │

    │  │  ProductB1    │  │           │  │  ProductB2    │  │

    │  └───────────────┘  │           │  └───────────────┘  │

    └─────────────────────┘           └─────────────────────┘

```



---



## 原理



### 为什么需要抽象工厂？



1. **产品族概念**: 多个相关的产品对象需要一起使用

2. **一致性**: 确保同一产品族的对象能够协同工作

3. **切换成本**: 方便在不同产品族之间切换（如切换 UI 主题）

4. **隔离变化**: 产品族的实现细节对客户端透明



### 与工厂方法的区别



| 特性 | 工厂方法 | 抽象工厂 |

|------|----------|----------|

| 维度 | 单一产品等级结构 | 多个产品等级结构（产品族） |

| 方法数量 | 一个工厂方法 | 多个工厂方法 |

| 复杂度 | 较低 | 较高 |

| 适用场景 | 一个产品系列 | 多个相关产品系列 |



---



## 实现方式



### Python 实现：跨平台 UI 组件



```python

from abc import ABC, abstractmethod



# ==================== 抽象产品接口 ====================



class Button(ABC):

    @abstractmethod

    def render(self) -> str:

        pass



    @abstractmethod

    def on_click(self) -> str:

        pass



class Checkbox(ABC):

    @abstractmethod

    def render(self) -> str:

        pass



    @abstractmethod

    def toggle(self) -> str:

        pass



class TextField(ABC):

    @abstractmethod

    def render(self) -> str:

        pass



    @abstractmethod

    def set_text(self, text: str) -> str:

        pass



# ==================== Windows 产品族 ====================



class WindowsButton(Button):

    def render(self) -> str:

        return "渲染 Windows 风格按钮"



    def on_click(self) -> str:

        return "Windows 按钮点击事件"



class WindowsCheckbox(Checkbox):

    def render(self) -> str:

        return "渲染 Windows 风格复选框"



    def toggle(self) -> str:

        return "Windows 复选框切换状态"



class WindowsTextField(TextField):

    def render(self) -> str:

        return "渲染 Windows 风格文本框"



    def set_text(self, text: str) -> str:

        return f"Windows 文本框设置内容: {text}"



# ==================== Mac 产品族 ====================



class MacButton(Button):

    def render(self) -> str:

        return "渲染 macOS 风格按钮"



    def on_click(self) -> str:

        return "macOS 按钮点击事件"



class MacCheckbox(Checkbox):

    def render(self) -> str:

        return "渲染 macOS 风格复选框"



    def toggle(self) -> str:

        return "macOS 复选框切换状态"



class MacTextField(TextField):

    def render(self) -> str:

        return "渲染 macOS 风格文本框"



    def set_text(self, text: str) -> str:

        return f"macOS 文本框设置内容: {text}"



# ==================== Linux 产品族 ====================



class LinuxButton(Button):

    def render(self) -> str:

        return "渲染 Linux 风格按钮"



    def on_click(self) -> str:

        return "Linux 按钮点击事件"



class LinuxCheckbox(Checkbox):

    def render(self) -> str:

        return "渲染 Linux 风格复选框"



    def toggle(self) -> str:

        return "Linux 复选框切换状态"



class LinuxTextField(TextField):

    def render(self) -> str:

        return "渲染 Linux 风格文本框"



    def set_text(self, text: str) -> str:

        return f"Linux 文本框设置内容: {text}"



# ==================== 抽象工厂 ====================



class GUIFactory(ABC):

    @abstractmethod

    def create_button(self) -> Button:

        pass



    @abstractmethod

    def create_checkbox(self) -> Checkbox:

        pass



    @abstractmethod

    def create_text_field(self) -> TextField:

        pass



# ==================== 具体工厂 ====================



class WindowsFactory(GUIFactory):

    def create_button(self) -> Button:

        return WindowsButton()



    def create_checkbox(self) -> Checkbox:

        return WindowsCheckbox()



    def create_text_field(self) -> TextField:

        return WindowsTextField()



class MacFactory(GUIFactory):

    def create_button(self) -> Button:

        return MacButton()



    def create_checkbox(self) -> Checkbox:

        return MacCheckbox()



    def create_text_field(self) -> TextField:

        return MacTextField()



class LinuxFactory(GUIFactory):

    def create_button(self) -> Button:

        return LinuxButton()



    def create_checkbox(self) -> Checkbox:

        return LinuxCheckbox()



    def create_text_field(self) -> TextField:

        return LinuxTextField()



# ==================== 客户端代码 ====================



class Application:

    def __init__(self, factory: GUIFactory):

        self.factory = factory

        self.button = factory.create_button()

        self.checkbox = factory.create_checkbox()

        self.text_field = factory.create_text_field()



    def render_ui(self):

        return [

            self.button.render(),

            self.checkbox.render(),

            self.text_field.render()

        ]



# ==================== 使用示例 ====================



# 根据操作系统选择工厂

import platform



def get_factory_for_os() -> GUIFactory:

    system = platform.system()

    if system == "Windows":

        return WindowsFactory()

    elif system == "Darwin":

        return MacFactory()

    else:

        return LinuxFactory()



# 创建应用

factory = get_factory_for_os()

app = Application(factory)

app.render_ui()

```



### Java 实现：数据库访问层



```java

// 抽象产品：连接

public interface Connection {

    void connect();

    void disconnect();

}



// 抽象产品：命令

public interface Command {

    void execute(String sql);

}



// 抽象产品：结果集

public interface ResultSet {

    boolean next();

    String getString(String column);

}



// ==================== MySQL 产品族 ====================



public class MySQLConnection implements Connection {

    public void connect() { System.out.println("MySQL 连接"); }

    public void disconnect() { System.out.println("MySQL 断开"); }

}



public class MySQLCommand implements Command {

    public void execute(String sql) { System.out.println("MySQL 执行: " + sql); }

}



public class MySQLResultSet implements ResultSet {

    public boolean next() { return false; }

    public String getString(String column) { return "MySQL数据"; }

}



// ==================== PostgreSQL 产品族 ====================



public class PostgreSQLConnection implements Connection {

    public void connect() { System.out.println("PostgreSQL 连接"); }

    public void disconnect() { System.out.println("PostgreSQL 断开"); }

}



public class PostgreSQLCommand implements Command {

    public void execute(String sql) { System.out.println("PostgreSQL 执行: " + sql); }

}



public class PostgreSQLResultSet implements ResultSet {

    public boolean next() { return false; }

    public String getString(String column) { return "PostgreSQL数据"; }

}



// ==================== 抽象工厂 ====================



public interface DatabaseFactory {

    Connection createConnection();

    Command createCommand();

    ResultSet createResultSet();

}



// ==================== 具体工厂 ====================



public class MySQLFactory implements DatabaseFactory {

    public Connection createConnection() { return new MySQLConnection(); }

    public Command createCommand() { return new MySQLCommand(); }

    public ResultSet createResultSet() { return new MySQLResultSet(); }

}



public class PostgreSQLFactory implements DatabaseFactory {

    public Connection createConnection() { return new PostgreSQLConnection(); }

    public Command createCommand() { return new PostgreSQLCommand(); }

    public ResultSet createResultSet() { return new PostgreSQLResultSet(); }

}



// ==================== 客户端 ====================



public class DatabaseClient {

    private Connection connection;

    private Command command;



    public DatabaseClient(DatabaseFactory factory) {

        this.connection = factory.createConnection();

        this.command = factory.createCommand();

    }



    public void query(String sql) {

        connection.connect();

        command.execute(sql);

        connection.disconnect();

    }

}

```



---



## 示例



### 游戏装备系统



```python

from abc import ABC, abstractmethod



# 产品接口

class Weapon(ABC):

    @abstractmethod

    def attack(self) -> str:

        pass



class Armor(ABC):

    @abstractmethod

    def defend(self) -> str:

        pass



class Potion(ABC):

    @abstractmethod

    def heal(self) -> str:

        pass



# 战士装备族

class Sword(Weapon):

    def attack(self) -> str:

        return "剑刃斩击!"



class PlateArmor(Armor):

    def defend(self) -> str:

        return "板甲格挡!"



class HealthPotion(Potion):

    def heal(self) -> str:

        return "恢复药水!"



# 法师装备族

class Staff(Weapon):

    def attack(self) -> str:

        return "魔法飞弹!"



class Robe(Armor):

    def defend(self) -> str:

        return "魔法护盾!"



class ManaPotion(Potion):

    def heal(self) -> str:

        return "法力药水!"



# 抽象工厂

class EquipmentFactory(ABC):

    @abstractmethod

    def create_weapon(self) -> Weapon:

        pass



    @abstractmethod

    def create_armor(self) -> Armor:

        pass



    @abstractmethod

    def create_potion(self) -> Potion:

        pass



# 具体工厂

class WarriorEquipmentFactory(EquipmentFactory):

    def create_weapon(self) -> Weapon:

        return Sword()



    def create_armor(self) -> Armor:

        return PlateArmor()



    def create_potion(self) -> Potion:

        return HealthPotion()



class MageEquipmentFactory(EquipmentFactory):

    def create_weapon(self) -> Weapon:

        return Staff()



    def create_armor(self) -> Armor:

        return Robe()



    def create_potion(self) -> Potion:

        return ManaPotion()



# 角色类

class Character:

    def __init__(self, name: str, factory: EquipmentFactory):

        self.name = name

        self.weapon = factory.create_weapon()

        self.armor = factory.create_armor()

        self.potion = factory.create_potion()



    def battle_info(self):

        return f"{self.name}: {self.weapon.attack()}, {self.armor.defend()}, {self.potion.heal()}"



# 使用

warrior = Character("战士", WarriorEquipmentFactory())

mage = Character("法师", MageEquipmentFactory())



print(warrior.battle_info())

print(mage.battle_info())

```



---



## 面试要点



1. **抽象工厂 vs 工厂方法**

   - 工厂方法：一个产品等级结构，一个抽象方法

   - 抽象工厂：多个产品等级结构，多个抽象方法（产品族）



2. **产品族 vs 产品等级**

   - **产品族**: 同一工厂生产的不同产品（如 Windows 按钮 + Windows 文本框）

   - **产品等级**: 不同工厂生产的同类产品（如 Windows 按钮 + Mac 按钮）



3. **优缺点**

   - **优点**: 保证产品一致性、易于切换产品族、符合开闭原则

   - **缺点**: 新增产品等级困难（需要修改所有工厂）、类数量爆炸



4. **适用场景**

   - 需要生成产品族

   - 系统独立于产品创建

   - 需要一致的产品外观



5. **实际应用**

   - Java AWT/Swing 的 Look and Feel

   - 跨平台 GUI 框架

   - 数据库访问层抽象



---



## 相关概念



### 数据结构

- [抽象数据类型](../../../computer-science/data-structures/index.md) - 接口与实现的分离



### 算法

- [策略模式](../behavioral/strategy.md) - 运行时选择工厂



### 设计模式

- [工厂模式](./factory.md) - 单一产品创建

- [建造者模式](./builder.md) - 复杂对象构建

- [外观模式](../structural/facade.md) - 简化接口

- [桥接模式](../structural/bridge.md) - 抽象与实现分离



### 复杂度分析

- [时间复杂度](../../../references/time-complexity.md) - 工厂方法调用开销

- [空间复杂度](../../../references/space-complexity.md) - 多产品内存占用



### 系统实现

- [依赖注入](../../architecture-patterns/dependency-injection.md) - 工厂与 DI 容器

- [ORM 框架](../../../computer-science/databases/orm.md) - 数据库抽象工厂应用

