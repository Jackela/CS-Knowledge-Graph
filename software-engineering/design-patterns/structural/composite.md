# 组合模式 (Composite Pattern)

## 概念

组合模式（Composite Pattern）是一种**结构型设计模式**，它允许将对象组合成树形结构来表示"部分-整体"的层次结构。组合模式使得用户对单个对象和组合对象的使用具有一致性。

> **核心思想**: 将单个对象（叶子）和组合对象（容器）都视为同一种类型，统一处理。

```
传统方式：                                  组合模式：
                                            
File - 单独处理                              Component (统一接口)
Folder - 特殊处理                              ├── File (叶子节点)
                                               └── Folder (容器)
                                                     └── 包含 Component
                                                      
客户端需要区分处理                          客户端统一处理，无需区分
```

---

## 原理

### 为什么需要组合模式？

1. **统一接口**: 单个对象和组合对象对外暴露相同的接口
2. **递归结构**: 自然地表达树形层次结构
3. **简化客户端**: 客户端无需区分处理叶子和容器
4. **易于扩展**: 新增组件类型无需修改现有代码

### 核心角色

| 角色 | 职责 |
|------|------|
| Component | 声明叶子和容器的公共接口 |
| Leaf | 叶子节点，没有子节点 |
| Composite | 容器节点，存储子组件 |
| Client | 通过 Component 接口操作所有元素 |

### 两种实现方式

| 方式 | 特点 | 优缺点 |
|------|------|--------|
| 透明方式 | Component 声明所有接口 | 叶子节点有冗余方法，但接口统一 |
| 安全方式 | 只在 Composite 声明管理方法 | 类型需要判断，但接口更纯粹 |

### 优缺点

**优点：**
- 定义了包含基本对象和组合对象的类层次结构
- 简化客户端代码，统一处理所有对象
- 更容易增加新类型的组件
- 使设计更通用，更容易维护

**缺点：**
- 透明方式下叶子节点需要实现冗余方法
- 可能使设计过于抽象
- 限制类型系统（只能使用 Component 接口）

---

## 实现方式

### 1. 透明方式（推荐）

```python
from abc import ABC, abstractmethod
from typing import List


# 组件接口 - 透明方式
class FileSystemComponent(ABC):
    @abstractmethod
    def get_size(self) -> int:
        """获取大小"""
        pass
    
    @abstractmethod
    def display(self, indent: int = 0):
        """显示信息"""
        pass
    
    def add(self, component):
        """添加子组件（默认抛出异常）"""
        raise NotImplementedError("叶子节点不能添加子组件")
    
    def remove(self, component):
        """移除子组件（默认抛出异常）"""
        raise NotImplementedError("叶子节点不能移除子组件")
    
    def get_child(self, index: int):
        """获取子组件（默认抛出异常）"""
        raise NotImplementedError("叶子节点没有子组件")


# 叶子节点 - 文件
class File(FileSystemComponent):
    def __init__(self, name: str, size: int):
        self.name = name
        self._size = size
    
    def get_size(self) -> int:
        return self._size
    
    def display(self, indent: int = 0):
        print("  " * indent + f"📄 {self.name} ({self._size} bytes)")


# 容器节点 - 文件夹
class Folder(FileSystemComponent):
    def __init__(self, name: str):
        self.name = name
        self._children: List[FileSystemComponent] = []
    
    def add(self, component: FileSystemComponent):
        self._children.append(component)
    
    def remove(self, component: FileSystemComponent):
        self._children.remove(component)
    
    def get_child(self, index: int) -> FileSystemComponent:
        return self._children[index]
    
    def get_size(self) -> int:
        # 递归计算所有子组件大小
        total_size = 0
        for child in self._children:
            total_size += child.get_size()
        return total_size
    
    def display(self, indent: int = 0):
        print("  " * indent + f"📁 {self.name}/")
        for child in self._children:
            child.display(indent + 1)


# 使用场景
root = Folder("root")
documents = Folder("Documents")
pictures = Folder("Pictures")

# 添加文件
documents.add(File("resume.pdf", 1024))
documents.add(File("cover_letter.docx", 512))

pictures.add(File("photo1.jpg", 2048))
pictures.add(File("photo2.jpg", 3072))

# 嵌套文件夹
work = Folder("Work")
work.add(File("project1.py", 1500))
work.add(File("project2.py", 2000))
documents.add(work)

# 组装树
root.add(documents)
root.add(pictures)

# 统一操作
root.display()
print(f"\n总大小: {root.get_size()} bytes")
```

### 2. 公司组织架构示例

```python
from abc import ABC, abstractmethod
from typing import List


# 组件接口
class Employee(ABC):
    def __init__(self, name: str, position: str, salary: float):
        self.name = name
        self.position = position
        self.salary = salary
    
    @abstractmethod
    def get_subordinates(self) -> List['Employee']:
        pass
    
    @abstractmethod
    def get_department_cost(self) -> float:
        """获取部门总成本（包括所有下属）"""
        pass
    
    @abstractmethod
    def display(self, indent: int = 0):
        pass
    
    def add(self, employee: 'Employee'):
        raise NotImplementedError("普通员工不能添加下属")
    
    def remove(self, employee: 'Employee'):
        raise NotImplementedError("普通员工不能移除下属")


# 叶子节点 - 普通员工
class IndividualEmployee(Employee):
    def __init__(self, name: str, position: str, salary: float):
        super().__init__(name, position, salary)
    
    def get_subordinates(self) -> List['Employee']:
        return []
    
    def get_department_cost(self) -> float:
        return self.salary
    
    def display(self, indent: int = 0):
        prefix = "  " * indent
        print(f"{prefix}👤 {self.name} - {self.position} (${self.salary:,.2f})")


# 容器节点 - 管理者
class Manager(Employee):
    def __init__(self, name: str, position: str, salary: float):
        super().__init__(name, position, salary)
        self._subordinates: List[Employee] = []
    
    def add(self, employee: Employee):
        self._subordinates.append(employee)
    
    def remove(self, employee: Employee):
        self._subordinates.remove(employee)
    
    def get_subordinates(self) -> List['Employee']:
        return self._subordinates.copy()
    
    def get_department_cost(self) -> float:
        # 递归计算部门总成本
        total = self.salary
        for subordinate in self._subordinates:
            total += subordinate.get_department_cost()
        return total
    
    def display(self, indent: int = 0):
        prefix = "  " * indent
        print(f"{prefix}👔 {self.name} - {self.position} (${self.salary:,.2f})")
        for subordinate in self._subordinates:
            subordinate.display(indent + 1)


# 构建组织架构
ceo = Manager("张总", "CEO", 50000)

cto = Manager("李总", "CTO", 40000)
cfo = Manager("王总", "CFO", 40000)

# CTO 下属
tech_lead1 = Manager("赵经理", "技术经理", 25000)
tech_lead2 = Manager("钱经理", "技术经理", 25000)

dev1 = IndividualEmployee("张三", "高级开发", 15000)
dev2 = IndividualEmployee("李四", "高级开发", 15000)
dev3 = IndividualEmployee("王五", "开发工程师", 12000)
dev4 = IndividualEmployee("赵六", "开发工程师", 12000)

tech_lead1.add(dev1)
tech_lead1.add(dev2)
tech_lead2.add(dev3)
tech_lead2.add(dev4)

cto.add(tech_lead1)
cto.add(tech_lead2)

# CFO 下属
accountant = IndividualEmployee("孙七", "会计", 10000)
analyst = IndividualEmployee("周八", "财务分析师", 12000)
cfo.add(accountant)
cfo.add(analyst)

ceo.add(cto)
ceo.add(cfo)

# 统一操作
ceo.display()
print(f"\n公司总人力成本: ${ceo.get_department_cost():,.2f}")
```

### 3. Java 实现示例

```java
import java.util.ArrayList;
import java.util.List;

// 组件接口
public interface Graphic {
    void draw();
    void move(int x, int y);
    double getArea();
    
    // 透明方式：默认实现抛出异常
    default void add(Graphic graphic) {
        throw new UnsupportedOperationException("不能添加子组件");
    }
    
    default void remove(Graphic graphic) {
        throw new UnsupportedOperationException("不能移除子组件");
    }
    
    default Graphic getChild(int index) {
        throw new UnsupportedOperationException("没有子组件");
    }
}

// 叶子节点 - 圆形
public class Circle implements Graphic {
    private int x, y;
    private double radius;
    
    public Circle(int x, int y, double radius) {
        this.x = x;
        this.y = y;
        this.radius = radius;
    }
    
    @Override
    public void draw() {
        System.out.println("绘制圆形 at (" + x + ", " + y + "), 半径: " + radius);
    }
    
    @Override
    public void move(int x, int y) {
        this.x += x;
        this.y += y;
    }
    
    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }
}

// 容器节点 - 复合图形
public class CompositeGraphic implements Graphic {
    private List<Graphic> children = new ArrayList<>();
    
    @Override
    public void add(Graphic graphic) {
        children.add(graphic);
    }
    
    @Override
    public void remove(Graphic graphic) {
        children.remove(graphic);
    }
    
    @Override
    public Graphic getChild(int index) {
        return children.get(index);
    }
    
    @Override
    public void draw() {
        System.out.println("绘制复合图形（包含 " + children.size() + " 个子图形）:");
        for (Graphic child : children) {
            child.draw();
        }
    }
    
    @Override
    public void move(int x, int y) {
        for (Graphic child : children) {
            child.move(x, y);
        }
    }
    
    @Override
    public double getArea() {
        double total = 0;
        for (Graphic child : children) {
            total += child.getArea();
        }
        return total;
    }
}
```

---

## 示例

### UML 图

```
┌─────────────────────────────────────────────────────────────────┐
│                        组合模式 UML                             │
│                     （文件系统示例）                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                <<interface>>                            │   │
│  │            FileSystemComponent                          │   │
│  │                                                         │   │
│  │  +get_size(): int                                       │   │
│  │  +display(indent): void                                 │   │
│  │  +add(component): void                                  │   │
│  │  +remove(component): void                               │   │
│  │  +get_child(index): FileSystemComponent                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ▲                                    ▲               │
│           │                                    │               │
│  ┌────────┴────────┐              ┌────────────┴────────────┐  │
│  │                 │              │                         │  │
│  │    File         │              │        Folder           │  │
│  │  (Leaf)         │              │      (Composite)        │  │
│  │                 │              │                         │  │
│  │ -name: str      │              │ -name: str              │  │
│  │ -size: int      │              │ -children: List         │  │
│  │                 │              │                         │  │
│  │ +get_size()     │              │ +add(component)         │  │
│  │ +display()      │              │ +remove(component)      │  │
│  │                 │              │ +get_child(index)       │  │
│  │                 │              │ +get_size()             │  │
│  │                 │              │ +display()              │  │
│  └─────────────────┘              └─────────────────────────┘  │
│                                                                 │
│  树形结构示意：                                                  │
│                                                                 │
│                      root/                                      │
│                      ├── Documents/                             │
│                      │   ├── resume.pdf                        │
│                      │   ├── cover_letter.docx                 │
│                      │   └── Work/                             │
│                      │       ├── project1.py                   │
│                      │       └── project2.py                   │
│                      └── Pictures/                              │
│                          ├── photo1.jpg                         │
│                          └── photo2.jpg                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

1. **Q: 什么是组合模式？**
   
   A: 组合模式是一种结构型设计模式，允许将对象组合成树形结构来表示"部分-整体"的层次结构。它让客户端可以统一处理单个对象和组合对象，无需区分。

2. **Q: 透明方式和安全方式的区别？**
   
   A: 透明方式在 Component 接口中声明所有方法（包括管理子组件的方法），叶子节点需要实现但抛出异常，优点是接口统一；安全方式只在 Composite 中声明管理方法，优点是类型安全，但客户端需要区分类型。

3. **Q: 组合模式与装饰器模式的区别？**
   
   A: 组合模式关注"部分-整体"的层次结构，目的是统一处理树形结构中的所有对象；装饰器模式关注动态添加功能，保持接口不变，目的是增强对象功能。

4. **Q: 如何处理组合模式中的循环引用？**
   
   A: 可以在添加子组件时检查是否会造成循环引用，即检查待添加组件是否是当前组件的父级。可以在 Component 中添加 parent 引用，在 add 方法中进行检测。

5. **Q: 实际应用场景有哪些？**
   
   A: 常见场景包括：
   - 文件系统（文件和文件夹）
   - 组织架构（员工和部门）
   - UI 组件树（DOM 结构）
   - 图形编辑器（简单图形和组合图形）
   - 菜单系统（菜单项和子菜单）

---

## 相关概念

### 数据结构
- [树](../../../computer-science/data-structures/tree.md) - 组合模式的基础数据结构
- [链表](../../../computer-science/data-structures/linked-list.md) - 简单组合结构
- [图](../../../computer-science/data-structures/graph.md) - 复杂关系建模

### 算法
- [深度优先搜索](../../../computer-science/algorithms/graph-traversal.md) - 树形结构遍历
- [广度优先搜索](../../../computer-science/algorithms/graph-traversal.md) - 层次遍历

### 复杂度分析
- [时间复杂度](../../../references/time-complexity.md) - 递归操作复杂度分析
- [空间复杂度](../../../references/space-complexity.md) - 树结构内存占用

### 系统实现
- [文件系统](../../../computer-science/systems/file-systems.md) - 目录树实现
- [DOM 解析](../../../computer-science/systems/os.md) - HTML/XML 树结构

### 设计模式
- [装饰器模式](./decorator.md) - 单对象功能增强
- [迭代器模式](../behavioral/iterator.md) - 树形结构遍历
- [访问者模式](../behavioral/visitor.md) - 树节点操作分离
- [享元模式](./flyweight.md) - 共享大量细粒度对象


> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念 (Concept)

**组合模式 (Composite Pattern)** 是一种结构型设计模式，它允许你将对象组合成树形结构来表现"部分-整体"层次结构。组合模式让客户端对单个对象和组合对象的使用具有一致性。

组合模式的核心思想是**统一处理单个对象和组合对象**。在树形结构中，叶子节点和分支节点都实现相同的接口。

```
┌─────────────────────────────────────────────────────────────┐
│                    组合模式 (Composite)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Component (interface)                    │
│                    ├─ operation()                           │
│                    ├─ add(Component)                        │
│                    ├─ remove(Component)                     │
│                    └─ getChildren()                         │
│                           ▲                                 │
│            ┌──────────────┼──────────────┐                  │
│            │              │              │                  │
│            ▼              ▼              ▼                  │
│         Leaf          Composite       Leaf                  │
│       (叶子节点)        (组合节点)      (叶子节点)           │
│                      ├─ children[]                        │
│                      ├─ operation()  # 遍历调用子节点        │
│                                                             │
│   典型应用：文件系统、UI组件树、组织结构、菜单系统            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 设计原则 (Principle)

组合模式遵循以下设计原则：

1. **单一职责原则 (Single Responsibility Principle)**：统一接口处理简单和复杂对象
2. **开闭原则 (Open/Closed Principle)**：新增叶子或组合节点无需修改现有代码
3. **里氏替换原则 (Liskov Substitution Principle)**：叶子和组合可以互换使用

**透明性 vs 安全性**：
- **透明方式**：在Component中声明所有方法，叶子节点的add/remove可能无意义或抛出异常
- **安全方式**：只在Composite中声明add/remove，客户端需要类型判断

---

## 实现示例 (Example)

### 1. 文件系统（透明方式）

```python
from abc import ABC, abstractmethod
from typing import List

class FileSystemComponent(ABC):
    """文件系统组件 - 抽象组件"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def get_size(self) -> int:
        """获取大小（字节）"""
        pass
    
    @abstractmethod
    def display(self, indent: int = 0):
        """显示信息"""
        pass
    
    # 透明方式：在抽象类中定义子节点操作
    def add(self, component: 'FileSystemComponent'):
        """添加子节点 - 默认不支持"""
        raise NotImplementedError("Cannot add to a leaf node")
    
    def remove(self, component: 'FileSystemComponent'):
        """移除子节点 - 默认不支持"""
        raise NotImplementedError("Cannot remove from a leaf node")
    
    def get_children(self) -> List['FileSystemComponent']:
        """获取子节点 - 默认空列表"""
        return []

class File(FileSystemComponent):
    """文件 - 叶子节点"""
    
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self._size = size
    
    def get_size(self) -> int:
        return self._size
    
    def display(self, indent: int = 0):
        print("  " * indent + f"📄 {self.name} ({self._size} bytes)")

class Directory(FileSystemComponent):
    """目录 - 组合节点"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._children: List[FileSystemComponent] = []
    
    def get_size(self) -> int:
        """递归计算目录总大小"""
        return sum(child.get_size() for child in self._children)
    
    def display(self, indent: int = 0):
        print("  " * indent + f"📁 {self.name}/")
        for child in self._children:
            child.display(indent + 1)
    
    def add(self, component: FileSystemComponent):
        self._children.append(component)
    
    def remove(self, component: FileSystemComponent):
        self._children.remove(component)
    
    def get_children(self) -> List[FileSystemComponent]:
        return self._children.copy()

# ============== 使用示例 ==============

# 构建文件系统树
root = Directory("root")

# 添加文件到根目录
root.add(File("readme.txt", 1024))
root.add(File("config.json", 512))

# 创建子目录
docs = Directory("docs")
docs.add(File("manual.pdf", 20480))
docs.add(File("guide.md", 4096))

src = Directory("src")
src.add(File("main.py", 2048))
src.add(File("utils.py", 1024))

# 嵌套目录
utils_dir = Directory("utils")
utils_dir.add(File("helper.py", 512))
src.add(utils_dir)

# 组装树
root.add(docs)
root.add(src)

# 统一操作 - 客户端无需区分文件和目录
print("文件系统结构:")
root.display()

print(f"\n总大小: {root.get_size()} bytes")
print(f"docs目录大小: {docs.get_size()} bytes")
```

### 2. UI组件树

```python
from abc import ABC, abstractmethod
from typing import List

class UIComponent(ABC):
    """UI组件基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.visible = True
    
    @abstractmethod
    def render(self) -> str:
        pass
    
    @abstractmethod
    def get_bounds(self) -> dict:
        pass
    
    def add(self, component: 'UIComponent'):
        raise NotImplementedError(f"{self.name} cannot contain children")
    
    def remove(self, component: 'UIComponent'):
        raise NotImplementedError(f"{self.name} has no children to remove")

class Button(UIComponent):
    """按钮 - 叶子节点"""
    
    def __init__(self, name: str, text: str):
        super().__init__(name)
        self.text = text
    
    def render(self) -> str:
        return f"[Button: {self.text}]"
    
    def get_bounds(self) -> dict:
        return {"width": 100, "height": 40}

class TextField(UIComponent):
    """文本框 - 叶子节点"""
    
    def __init__(self, name: str, placeholder: str = ""):
        super().__init__(name)
        self.placeholder = placeholder
    
    def render(self) -> str:
        return f"[TextField: {self.placeholder}]"
    
    def get_bounds(self) -> dict:
        return {"width": 200, "height": 30}

class Panel(UIComponent):
    """面板 - 组合节点"""
    
    def __init__(self, name: str, layout: str = "vertical"):
        super().__init__(name)
        self.layout = layout
        self.children: List[UIComponent] = []
    
    def add(self, component: UIComponent):
        self.children.append(component)
    
    def remove(self, component: UIComponent):
        self.children.remove(component)
    
    def render(self) -> str:
        result = [f"Panel({self.name})["]
        for child in self.children:
            result.append("  " + child.render())
        result.append("]")
        return "\n".join(result)
    
    def get_bounds(self) -> dict:
        total_width = 0
        total_height = 0
        for child in self.children:
            bounds = child.get_bounds()
            total_width = max(total_width, bounds["width"])
            total_height += bounds["height"]
        return {"width": total_width, "height": total_height}

class Window(UIComponent):
    """窗口 - 根组合节点"""
    
    def __init__(self, title: str):
        super().__init__(title)
        self.title = title
        self.children: List[UIComponent] = []
    
    def add(self, component: UIComponent):
        self.children.append(component)
    
    def remove(self, component: UIComponent):
        self.children.remove(component)
    
    def render(self) -> str:
        result = [f"╔{'═' * 38}╗"]
        result.append(f"║ {self.title:<36} ║")
        result.append(f"╠{'═' * 38}╣")
        for child in self.children:
            lines = child.render().split('\n')
            for line in lines:
                result.append(f"║ {line:<36} ║")
        result.append(f"╚{'═' * 38}╝")
        return "\n".join(result)
    
    def get_bounds(self) -> dict:
        return {"width": 400, "height": 300}

# ============== 构建UI ==============

# 创建登录窗口
window = Window("Login")

# 主面板
main_panel = Panel("main", "vertical")
main_panel.add(TextField("username", "Username"))
main_panel.add(TextField("password", "Password"))

# 按钮面板
button_panel = Panel("buttons", "horizontal")
button_panel.add(Button("login", "Login"))
button_panel.add(Button("cancel", "Cancel"))

main_panel.add(button_panel)
window.add(main_panel)

# 渲染
print(window.render())
print(f"\n窗口尺寸: {window.get_bounds()}")
```

### 3. 组织架构管理

```python
from abc import ABC, abstractmethod
from typing import List

class Employee(ABC):
    """员工 - 抽象组件"""
    
    def __init__(self, name: str, title: str, salary: float):
        self.name = name
        self.title = title
        self.salary = salary
    
    @abstractmethod
    def get_subordinates(self) -> List['Employee']:
        pass
    
    @abstractmethod
    def get_department_budget(self) -> float:
        pass
    
    @abstractmethod
    def display(self, indent: int = 0):
        pass
    
    def add(self, employee: 'Employee'):
        raise NotImplementedError("Cannot add subordinates to this employee")

class IndividualEmployee(Employee):
    """普通员工 - 叶子节点"""
    
    def __init__(self, name: str, title: str, salary: float):
        super().__init__(name, title, salary)
    
    def get_subordinates(self) -> List[Employee]:
        return []
    
    def get_department_budget(self) -> float:
        return self.salary
    
    def display(self, indent: int = 0):
        prefix = "  " * indent
        print(f"{prefix}👤 {self.name} - {self.title} (${self.salary:,.2f})")

class Manager(Employee):
    """经理 - 组合节点"""
    
    def __init__(self, name: str, title: str, salary: float):
        super().__init__(name, title, salary)
        self.subordinates: List[Employee] = []
    
    def add(self, employee: Employee):
        self.subordinates.append(employee)
    
    def get_subordinates(self) -> List[Employee]:
        return self.subordinates.copy()
    
    def get_department_budget(self) -> float:
        """递归计算部门总预算"""
        total = self.salary
        for subordinate in self.subordinates:
            total += subordinate.get_department_budget()
        return total
    
    def display(self, indent: int = 0):
        prefix = "  " * indent
        print(f"{prefix}👔 {self.name} - {self.title} (${self.salary:,.2f})")
        for subordinate in self.subordinates:
            subordinate.display(indent + 1)

# ============== 构建组织架构 ==============

# CEO
ceo = Manager("Alice", "CEO", 200000)

# CTO
cto = Manager("Bob", "CTO", 150000)
cto.add(IndividualEmployee("Charlie", "Senior Developer", 120000))
cto.add(IndividualEmployee("David", "Developer", 90000))

# CFO
cfo = Manager("Eve", "CFO", 150000)
cfo.add(IndividualEmployee("Frank", "Accountant", 80000))

# 销售总监
sales_director = Manager("Grace", "Sales Director", 130000)
sales_director.add(IndividualEmployee("Henry", "Sales Rep", 70000))
sales_director.add(IndividualEmployee("Ivy", "Sales Rep", 70000))

# 组装
ceo.add(cto)
ceo.add(cfo)
ceo.add(sales_director)

# 显示
print("组织架构:")
ceo.display()
print(f"\n公司总预算: ${ceo.get_department_budget():,.2f}")
print(f"技术部预算: ${cto.get_department_budget():,.2f}")
```

---

## 使用场景 (Use Cases)

| 场景 | 说明 |
|------|------|
| 文件系统 | 文件和文件夹的统一处理 |
| UI组件树 | 简单控件和容器的统一渲染 |
| 组织架构 | 员工和部门的统一操作 |
| 菜单系统 | 菜单项和子菜单的统一处理 |
| 图形编辑器 | 简单图形和组合图形的统一操作 |
| XML/HTML解析 | 节点和元素树的处理 |

---

## 面试要点 (Interview Points)

**Q1: 组合模式和装饰器模式的区别？**

> - **组合模式**：处理树形结构，统一处理叶子和组合，关注"部分-整体"层次
> - **装饰器模式**：动态添加功能，保持接口不变，关注"功能增强"
>
> 组合是"结构组织"，装饰器是"功能包装"。

**Q2: 透明方式和安全方式的区别？**

> - **透明方式**：Component声明所有接口，叶子抛出异常或不实现，客户端无需类型判断
> - **安全方式**：只在Composite声明子节点操作，叶子无这些方法，客户端需要类型判断
>
> Java AWT/Swing 使用透明方式；DOM API 更接近安全方式。

**Q3: 组合模式的优缺点？**

> **优点**：
> - 统一处理简单和复杂对象
> - 易于扩展新组件类型
> - 树形结构清晰，递归操作简洁
>
> **缺点**：
> - 透明方式可能违反里氏替换原则（叶子抛出异常）
> - 设计较复杂，需要平衡通用性和类型安全
> - 限制较多（如子节点顺序、唯一性等难以约束）

**Q4: 如何在组合模式中实现迭代器？**

> 可以实现深度优先或广度优先迭代器：
> - 外部迭代器：维护栈/队列状态
> - 内部迭代器：accept(Visitor) 方式遍历
> - Python 中实现 `__iter__` 方法支持 for 循环

---

---

## 相关概念 (Related Concepts)

### 结构型模式 (Structural Patterns)

| 模式 | 说明 | 关联性 |
|------|------|--------|
| [适配器模式](./adapter.md) | 将不兼容接口转换为兼容接口 | 同为结构型，处理接口兼容性问题 |
| [桥接模式](./bridge.md) | 将抽象与实现分离，独立变化 | 同为树形结构组织，但桥接关注维度分离 |
| [装饰器模式](./decorator.md) | 动态地为对象添加功能 | 同为对象组合，面试常对比二者差异 |
| [外观模式](./facade.md) | 为子系统提供统一的高层接口 | 同为简化客户端调用，但外观是简化而非统一 |
| [享元模式](./flyweight.md) | 共享细粒度对象，节省内存 | 可结合使用，优化大量相似叶子节点 |
| [代理模式](./proxy.md) | 为对象提供代理以控制访问 | 同为结构包装，但代理关注访问控制 |

### 行为型模式 (Behavioral Patterns)

| 模式 | 说明 | 关联性 |
|------|------|--------|
| [迭代器模式](../behavioral/iterator.md) | 遍历聚合对象中的元素 | 组合结构需要迭代器来遍历树节点 |
| [访问者模式](../behavioral/visitor.md) | 在不改变元素类的前提下定义新操作 | 组合结构常与访问者配合，实现遍历操作 |
| [策略模式](../behavioral/strategy.md) | 定义算法族，分别封装起来 | 可为不同节点类型选择不同处理策略 |

### 面向对象设计原则

- [单一职责原则](../../solid-principles.md) - 组件接口设计遵循单一职责
- [开闭原则](../../solid-principles.md) - 新增节点类型无需修改现有代码
- [里氏替换原则](../../solid-principles.md) - 叶子和组合节点可互换使用
- [依赖倒置原则](../../solid-principles.md) - 客户端依赖抽象组件而非具体实现

### 数据结构

- [树](../../../computer-science/data-structures/tree.md) - 组合模式的核心是树形结构
- [二叉树](../../../computer-science/data-structures/binary-tree.md) - 特殊树结构，理解递归遍历的基础
- [B树](../../../computer-science/data-structures/b-tree.md) - 多叉平衡树，文件系统常用结构



## 相关引用 (References)

- 返回：[设计模式总览](../../design-patterns.md)
- 相关： - 动态添加功能
-  - 遍历组合结构
-  - 操作组合结构
- 原理：[SOLID原则](../../solid-principles.md)
