# 原型模式 (Prototype Pattern)



## 概念



原型模式（Prototype Pattern）是一种**创建型设计模式**，用于通过复制现有对象来创建新对象，而不是通过实例化类。



> **核心思想**: 通过复制（克隆）现有对象来创建新对象，避免重复的初始化代码。



```

┌─────────────────────────────────────────────────────────────────┐

│                         原型模式                                │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│   ┌─────────────────┐         ┌─────────────────┐              │

│   │   Prototype     │◀────────│   Concrete      │              │

│   │   (抽象原型)     │  继承    │   Prototype     │              │

│   │                 │         │   (具体原型)     │              │

│   │ + clone()       │         │                 │              │

│   │                 │         │ + clone()       │              │

│   └─────────────────┘         │   (实现复制)     │              │

│           ▲                   └─────────────────┘              │

│           │                                                     │

│   ┌───────┴───────┐                                            │

│   │    Client     │                                            │

│   │    (客户端)    │                                            │

│   │               │                                            │

│   │ 通过clone创建  │                                            │

│   └───────────────┘                                            │

│                                                                 │

└─────────────────────────────────────────────────────────────────┘

```



---



## 原理



### 为什么需要原型模式？



1. **对象创建成本高**: 初始化需要大量计算或 I/O 操作

2. **运行时动态配置**: 需要在运行时决定创建的对象类型

3. **避免子类爆炸**: 减少为每个变体创建子类的需求

4. **保持历史状态**: 保存对象快照用于撤销操作



### 深拷贝 vs 浅拷贝



| 类型 | 特点 | 风险 |

|------|------|------|

| 浅拷贝 | 复制对象本身，引用类型共享 | 修改引用影响原对象 |

| 深拷贝 | 递归复制所有引用对象 | 循环引用、性能开销 |



---



## 实现方式



### 1. Python 实现（使用 copy 模块）



```python

import copy

from abc import ABC, abstractmethod



# 抽象原型

class Prototype(ABC):

    @abstractmethod

    def clone(self):

        pass



# 具体原型：文档

class Document(Prototype):

    def __init__(self, title, content, author):

        self.title = title

        self.content = content

        self.author = author

        self.comments = []

        self.metadata = {}



    def add_comment(self, comment):

        self.comments.append(comment)



    def set_metadata(self, key, value):

        self.metadata[key] = value



    def clone(self):

        # 深拷贝确保完全独立

        return copy.deepcopy(self)



    def __str__(self):

        return f"Document(title='{self.title}', author='{self.author}')"



# 使用示例

original = Document("原始文档", "这是内容...", "张三")

original.add_comment("评论1")

original.set_metadata("created", "2024-01-01")



# 克隆文档

cloned = original.clone()

cloned.title = "克隆文档"

cloned.add_comment("评论2")  # 不影响原文档



print(original.comments)  # ['评论1']

print(cloned.comments)    # ['评论1', '评论2']

```



### 2. Java 实现（实现 Cloneable 接口）



```java

// 原型接口

public interface Prototype {

    Prototype clone();

}



// 具体原型

public class Document implements Prototype, Cloneable {

    private String title;

    private String content;

    private Author author;  // 引用类型

    private List<String> tags;



    public Document(String title, String content, Author author) {

        this.title = title;

        this.content = content;

        this.author = author;

        this.tags = new ArrayList<>();

    }



    // 浅拷贝 - 使用 Object.clone()

    @Override

    public Document shallowClone() {

        try {

            return (Document) super.clone();

        } catch (CloneNotSupportedException e) {

            throw new RuntimeException(e);

        }

    }



    // 深拷贝 - 手动复制引用对象

    @Override

    public Document deepClone() {

        Document cloned = shallowClone();

        cloned.author = new Author(this.author.getName());  // 复制引用对象

        cloned.tags = new ArrayList<>(this.tags);           // 复制集合

        return cloned;

    }



    @Override

    public Prototype clone() {

        return deepClone();  // 默认使用深拷贝

    }

}



// 引用对象

public class Author {

    private String name;

    

    public Author(String name) {

        this.name = name;

    }

    

    // getter/setter

}

```



### 3. 原型注册表模式



```python

import copy

from typing import Dict



class PrototypeRegistry:

    """原型注册表 - 管理原型对象的缓存"""



    _prototypes: Dict[str, object] = {}



    @classmethod

    def register(cls, name: str, prototype: object):

        """注册原型"""

        cls._prototypes[name] = prototype



    @classmethod

    def unregister(cls, name: str):

        """注销原型"""

        del cls._prototypes[name]



    @classmethod

    def create(cls, name: str) -> object:

        """基于原型创建新对象"""

        if name not in cls._prototypes:

            raise ValueError(f"未找到原型: {name}")

        return copy.deepcopy(cls._prototypes[name])



    @classmethod

    def list_prototypes(cls):

        """列出所有可用的原型"""

        return list(cls._prototypes.keys())





# 使用示例

# 创建并注册原型

doc_template = Document("模板", "请在此处填写内容", "系统")

doc_template.set_metadata("template", "true")

PrototypeRegistry.register("document_template", doc_template)



# 从原型创建新对象

new_doc = PrototypeRegistry.create("document_template")

new_doc.title = "新文档"

```



---



## 示例



### 游戏角色克隆



```python

import copy



class GameCharacter:

    """游戏角色 - 使用原型模式快速创建相似角色"""



    def __init__(self, name: str, character_class: str, level: int = 1):

        self.name = name

        self.character_class = character_class

        self.level = level

        self.stats = self._init_stats()

        self.skills = []

        self.equipment = {}



    def _init_stats(self) -> dict:

        """根据职业初始化属性"""

        base_stats = {

            "warrior": {"hp": 150, "mp": 30, "atk": 20, "def": 15},

            "mage": {"hp": 80, "mp": 150, "atk": 35, "def": 5},

            "archer": {"hp": 100, "mp": 50, "atk": 25, "def": 10},

        }

        return base_stats.get(self.character_class, {}).copy()



    def add_skill(self, skill: str):

        self.skills.append(skill)



    def equip(self, slot: str, item: str):

        self.equipment[slot] = item



    def clone(self, new_name: str = None):

        """克隆角色"""

        cloned = copy.deepcopy(self)

        if new_name:

            cloned.name = new_name

        return cloned



    def __str__(self):

        return f"{self.name} [{self.character_class} Lv.{self.level}]"





# 使用：创建战士模板并克隆

warrior_template = GameCharacter("战士模板", "warrior", level=10)

warrior_template.add_skill("强力攻击")

warrior_template.add_skill("防御姿态")

warrior_template.equip("weapon", "铁剑")



# 快速创建相似角色

player1 = warrior_template.clone("亚瑟")

player2 = warrior_template.clone("盖伦")



print(player1)  # 亚瑟 [warrior Lv.10]

print(player2)  # 盖伦 [warrior Lv.10]



# 独立修改

player1.add_skill("狂暴")

print(player1.skills)  # ['强力攻击', '防御姿态', '狂暴']

print(player2.skills)  # ['强力攻击', '防御姿态'] - 不受影响

```



---



## 面试要点



1. **原型模式 vs 工厂模式**

   - 工厂：通过类创建新对象

   - 原型：通过复制现有对象创建



2. **深拷贝 vs 浅拷贝**

   - 浅拷贝：仅复制对象本身，引用类型共享（copy.copy）

   - 深拷贝：递归复制所有对象（copy.deepcopy）



3. **适用场景**

   - 对象创建成本高（需要大量初始化）

   - 运行时动态决定对象类型

   - 需要保存/恢复对象状态

   - 避免创建大量相似子类



4. **注意事项**

   - 循环引用处理困难

   - 深拷贝可能性能开销大

   - clone() 方法可能需要特殊处理



5. **实际应用**

   - Java Object.clone()

   - Python copy 模块

   - JavaScript Object.assign()

   - 游戏开发中的角色/道具克隆



---



## 相关概念



### 设计模式

- [工厂模式](./factory.md) - 另一种创建方式

- [备忘录模式](../behavioral/memento.md) - 保存对象状态

- [单例模式](./singleton.md) - 原型可返回单例实例

- [享元模式](../structural/flyweight.md) - 共享对象 vs 克隆对象



### 复杂度分析

- [时间复杂度](../../../references/time-complexity.md) - 克隆操作的时间开销

- [空间复杂度](../../../references/space-complexity.md) - 深拷贝的内存占用

