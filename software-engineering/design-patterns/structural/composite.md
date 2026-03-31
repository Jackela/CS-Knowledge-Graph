## 版权声明

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

- [树](../../computer-science/data-structures/tree.md) - 组合模式的核心是树形结构
- [二叉树](../../computer-science/data-structures/binary-tree.md) - 特殊树结构，理解递归遍历的基础
- [B树](../../computer-science/data-structures/b-tree.md) - 多叉平衡树，文件系统常用结构



## 相关引用 (References)

- 返回：[设计模式总览](../../design-patterns.md)
- 相关：[装饰器模式](./decorator.md) - 动态添加功能
- 相关：[迭代器模式](../behavioral/iterator.md) - 遍历组合结构
- 相关：[访问者模式](../behavioral/visitor.md) - 操作组合结构
- 原理：[SOLID原则](../../solid-principles.md)
