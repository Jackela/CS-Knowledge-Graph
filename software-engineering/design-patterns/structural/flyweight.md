# 享元模式 (Flyweight Pattern)

## 概念

享元模式（Flyweight Pattern）是一种**结构型设计模式**，它运用共享技术有效地支持大量细粒度的对象。享元模式通过共享已经存在的对象来减少内存占用，提高系统性能。

> **核心思想**: 将对象的内部状态（intrinsic）和外部状态（extrinsic）分离，内部状态可以被共享，外部状态由客户端维护。

```
不使用享元模式：                           使用享元模式：
                                            
每个字符一个对象：                          共享字符对象：
                                            
H: Char对象  e: Char对象                   H: 共享对象  e: 共享对象
l: Char对象  l: Char对象                   l: 共享对象  l: 共享对象
o: Char对象  ,: Char对象                   o: 共享对象  ,: 共享对象
 : Char对象  W: Char对象                    : 共享对象  W: 共享对象
o: Char对象  r: Char对象                   o: 引用共享   r: 共享对象
l: Char对象  d: Char对象                   l: 引用共享   d: 共享对象
!: Char对象                                !: 共享对象
                                            
13 个对象 × 1KB = 13KB                     10 个唯一对象 + 3 个引用
                                           10KB + 可忽略的开销
```

---

## 原理

### 为什么需要享元模式？

1. **减少内存占用**: 大量相似对象共享内部状态
2. **提高性能**: 减少对象创建和垃圾回收开销
3. **缓存优化**: 利用对象池重用对象
4. **应对大数据量**: 如游戏中的大量粒子、文档中的字符等

### 内部状态 vs 外部状态

| 类型 | 特征 | 示例 |
|------|------|------|
| 内部状态 (Intrinsic) | 不随环境改变，可共享 | 字符的形状、颜色 |
| 外部状态 (Extrinsic) | 随环境改变，不可共享 | 字符的位置、字体大小 |

### 核心角色

| 角色 | 职责 |
|------|------|
| Flyweight | 享元接口，定义对外暴露的方法 |
| ConcreteFlyweight | 具体享元，实现享元接口，存储内部状态 |
| FlyweightFactory | 享元工厂，创建和管理享元对象池 |
| Client | 客户端，维护外部状态，使用享元对象 |

### 优缺点

**优点：**
- 大幅减少内存占用
- 提高系统性能
- 符合单一职责原则

**缺点：**
- 增加代码复杂度
- 需要分离内部和外部状态
- 运行时间可能增加（需要计算/传递外部状态）

---

## 实现方式

### 1. Python 实现

```python
from abc import ABC, abstractmethod
from typing import Dict, Tuple


# 享元接口
class CharacterFlyweight(ABC):
    @abstractmethod
    def display(self, position: Tuple[int, int], font_size: int):
        """显示字符，position 和 font_size 是外部状态"""
        pass


# 具体享元 - 字符
class Character(CharacterFlyweight):
    """具体享元类，存储内部状态（不可变）"""
    
    def __init__(self, char: str, color: str):
        self._char = char      # 内部状态：字符本身
        self._color = color    # 内部状态：颜色
    
    def display(self, position: Tuple[int, int], font_size: int):
        """使用外部状态显示字符"""
        x, y = position
        print(f"字符 '{self._char}' (颜色: {self._color}) 在位置 ({x}, {y}), "
              f"字号: {font_size}")
    
    def __repr__(self):
        return f"Character('{self._char}', '{self._color}')"


# 享元工厂
class CharacterFactory:
    """享元工厂，管理享元对象池"""
    
    _characters: Dict[Tuple[str, str], Character] = {}
    
    @classmethod
    def get_character(cls, char: str, color: str = "black") -> Character:
        """获取享元对象，如果不存在则创建"""
        key = (char, color)
        if key not in cls._characters:
            cls._characters[key] = Character(char, color)
            print(f"创建新字符: {char} (颜色: {color})")
        else:
            print(f"复用字符: {char} (颜色: {color})")
        return cls._characters[key]
    
    @classmethod
    def get_pool_size(cls) -> int:
        return len(cls._characters)


# 客户端 - 文档编辑器
class DocumentEditor:
    """文档编辑器，维护外部状态"""
    
    def __init__(self):
        self._characters: list = []  # 存储 (Character, position, font_size)
    
    def add_character(self, char: str, x: int, y: int, 
                      color: str = "black", font_size: int = 12):
        """添加字符到文档"""
        character = CharacterFactory.get_character(char, color)
        self._characters.append((character, (x, y), font_size))
    
    def render(self):
        """渲染文档"""
        print("\n=== 渲染文档 ===")
        for character, position, font_size in self._characters:
            character.display(position, font_size)
    
    def get_stats(self):
        """获取统计信息"""
        total_chars = len(self._characters)
        unique_chars = CharacterFactory.get_pool_size()
        print(f"\n统计信息:")
        print(f"  总字符数: {total_chars}")
        print(f"  唯一字符对象数: {unique_chars}")
        print(f"  节省内存: {(1 - unique_chars/total_chars)*100:.1f}%")


# 使用场景
editor = DocumentEditor()
text = "Hello World!"
for i in range(3):
    for j, char in enumerate(text):
        editor.add_character(char, x=j*10, y=i*20, 
                           color="blue" if char.isupper() else "black")

editor.render()
editor.get_stats()
```

### 2. 游戏粒子系统示例

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import random


# 享元接口
class ParticleFlyweight(ABC):
    @abstractmethod
    def render(self, x: float, y: float, velocity: Tuple[float, float], 
               lifetime: float):
        pass


# 具体享元 - 粒子类型
class ParticleType(ParticleFlyweight):
    """粒子类型（内部状态）"""
    
    def __init__(self, shape: str, color: str, texture: str):
        self._shape = shape
        self._color = color
        self._texture = texture
        # 模拟大内存占用
        self._mesh_data = f"Mesh data for {shape}" * 1000
        self._texture_data = f"Texture: {texture}" * 1000
    
    def render(self, x: float, y: float, velocity: Tuple[float, float], 
               lifetime: float):
        """渲染粒子，参数是外部状态"""
        vx, vy = velocity
        print(f"渲染 {self._color} {self._shape} 粒子 at ({x:.1f}, {y:.1f}), "
              f"速度: ({vx:.1f}, {vy:.1f}), 剩余生命: {lifetime:.1f}s")


# 享元工厂
class ParticleFactory:
    """粒子类型工厂 - 享元工厂"""
    
    _particle_types: Dict[str, ParticleType] = {}
    
    @classmethod
    def get_particle_type(cls, shape: str, color: str, 
                          texture: str) -> ParticleType:
        key = f"{shape}_{color}_{texture}"
        if key not in cls._particle_types:
            cls._particle_types[key] = ParticleType(shape, color, texture)
            print(f"[工厂] 创建新粒子类型: {key}")
        else:
            print(f"[工厂] 复用粒子类型: {key}")
        return cls._particle_types[key]


# 粒子上下文 - 外部状态
class Particle:
    """粒子实例 - 存储外部状态"""
    
    def __init__(self, particle_type: ParticleType, x: float, y: float,
                 vx: float, vy: float, lifetime: float):
        self._type = particle_type
        self._x = x
        self._y = y
        self._vx = vx
        self._vy = vy
        self._lifetime = lifetime
    
    def update(self, dt: float):
        """更新粒子状态"""
        self._x += self._vx * dt
        self._y += self._vy * dt
        self._lifetime -= dt
    
    def render(self):
        """渲染粒子"""
        if self._lifetime > 0:
            self._type.render(self._x, self._y, (self._vx, self._vy), 
                            self._lifetime)
    
    def is_alive(self) -> bool:
        return self._lifetime > 0


# 粒子系统
class ParticleSystem:
    """管理大量粒子"""
    
    def __init__(self):
        self._particles: List[Particle] = []
    
    def emit(self, shape: str, color: str, texture: str,
             x: float, y: float, count: int = 1):
        """发射粒子"""
        particle_type = ParticleFactory.get_particle_type(shape, color, texture)
        
        for _ in range(count):
            vx = random.uniform(-50, 50)
            vy = random.uniform(-50, 50)
            lifetime = random.uniform(1.0, 3.0)
            particle = Particle(particle_type, x, y, vx, vy, lifetime)
            self._particles.append(particle)
```

### 3. Java 实现示例

```java
import java.util.HashMap;
import java.util.Map;

// 享元接口
public interface Shape {
    void draw(int x, int y, String color);
}

// 具体享元 - 圆形
public class Circle implements Shape {
    private String shapeType;
    private int radius;
    
    public Circle(int radius) {
        this.shapeType = "Circle";
        this.radius = radius;
    }
    
    @Override
    public void draw(int x, int y, String color) {
        System.out.println("绘制 " + color + " " + shapeType + 
                          " (半径: " + radius + ") at (" + x + ", " + y + ")");
    }
}

// 享元工厂
public class ShapeFactory {
    private static final Map<String, Shape> shapes = new HashMap<>();
    
    public static Shape getCircle(int radius) {
        String key = "circle_" + radius;
        if (!shapes.containsKey(key)) {
            shapes.put(key, new Circle(radius));
            System.out.println("[工厂] 创建新圆形，半径: " + radius);
        }
        return shapes.get(key);
    }
    
    public static int getShapeCount() {
        return shapes.size();
    }
}

// 使用
public class Client {
    public static void main(String[] args) {
        for (int i = 0; i < 1000; i++) {
            int radius = (i % 3) * 10 + 10;
            Shape circle = ShapeFactory.getCircle(radius);
            circle.draw(i * 10, i * 10, "red");
        }
        
        System.out.println("\n享元池中形状数量: " + ShapeFactory.getShapeCount());
        System.out.println("如果不用享元模式，需要创建 1000 个对象");
        System.out.println("使用享元模式，只创建 3 个对象");
    }
}
```

---

## 示例

### UML 图

```
┌─────────────────────────────────────────────────────────────────┐
│                        享元模式 UML                             │
│                    （字符渲染示例）                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  <<interface>>                                          │   │
│  │      CharacterFlyweight                                 │   │
│  │                                                         │   │
│  │  +display(position, font_size): void                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ▲                                                     │
│           │                                                     │
│  ┌────────┴────────┐                                           │
│  │                 │                                           │
│  │    Character    │  ◀──── 具体享元类                         │
│  │                 │                                           │
│  │ -_char: str     │  ◀──── 内部状态（共享）                   │
│  │ -_color: str    │  ◀──── 内部状态（共享）                   │
│  │                 │                                           │
│  │ +display()      │  ◀──── 使用外部状态参数                   │
│  └─────────────────┘                                           │
│           ▲                                                     │
│           │ 被创建和管理                                        │
│           │                                                     │
│  ┌────────┴─────────────────────────────────────────────┐      │
│  │             CharacterFactory                          │      │
│  │                                                       │      │
│  │ -_characters: Map                                     │      │
│  │                                                       │      │
│  │ +get_character(char, color): Character                │      │
│  │ +get_pool_size(): int                                 │      │
│  └───────────────────────────────────────────────────────┘      │
│           ▲                                                     │
│           │ 使用                                                │
│           │                                                     │
│  ┌────────┴─────────────────────────────────────────────┐      │
│  │              DocumentEditor                           │      │
│  │                                                       │      │
│  │ -_characters: List                                    │      │
│  │                                                       │      │
│  │ +add_character(char, x, y, color, font_size)          │      │
│  │ +render()                                             │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                 │
│  状态分离：                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  内部状态 (Intrinsic)            外部状态 (Extrinsic)   │   │
│  │  ─────────────────────          ────────────────────    │   │
│  │  • 字符形状 ('H', 'e')           • 位置 (x, y)          │   │
│  │  • 颜色 ("red", "blue")          • 字号 (12, 14)        │   │
│  │  • 字体类型                      • 旋转角度             │   │
│  │  ─────────────────────          ────────────────────    │   │
│  │  存储在享元对象中                由客户端维护            │   │
│  │  可被共享                        不可共享               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

1. **Q: 什么是享元模式？**
   
   A: 享元模式是一种结构型设计模式，运用共享技术有效地支持大量细粒度的对象。它通过分离内部状态和外部状态，使内部状态可以被多个对象共享，从而减少内存占用。

2. **Q: 内部状态和外部状态的区别？**
   
   A: 内部状态是对象的固有属性，不随环境改变，可以被共享（如字符的形状）；外部状态随环境改变，不能共享，由客户端维护（如字符的位置、颜色）。

3. **Q: 享元模式与对象池的区别？**
   
   A: 享元模式强调**共享不可变对象**，多个客户端同时使用同一个对象；对象池强调**重用可变对象**，一个对象同一时间只能被一个客户端使用。

4. **Q: 享元模式与单例模式的区别？**
   
   A: 享元模式管理**一组**共享对象，每个对象对应一种内部状态组合；单例模式只管理**一个**对象。享元模式是对象池的特例，单例是享元的特例（池大小为1）。

5. **Q: 实际应用场景有哪些？**
   
   A: 常见场景包括：
   - 文本编辑器中的字符渲染（如 Java String.intern()）
   - 游戏中的粒子系统、子弹、树木等
   - 地图应用中的图标标记
   - 数据库连接池（有限享元）
   - 缓存系统（如 IntegerCache、对象池）

---

## 相关概念

### 数据结构
- [哈希表](../../../computer-science/data-structures/hash-table.md) - 享元对象池实现
- [对象池](../../../computer-science/systems/memory-management.md) - 资源复用技术

### 算法
- [缓存算法](../../../computer-science/algorithms/caching.md) - LRU/LFU 缓存策略

### 复杂度分析
- [空间复杂度](../../../references/space-complexity.md) - 内存优化核心
- [时间复杂度](../../../references/time-complexity.md) - 查找开销分析

### 系统实现
- [内存管理](../../../computer-science/systems/memory-management.md) - 对象生命周期
- [数据库连接池](../../../computer-science/databases/indexing.md) - 连接复用
- [JVM 字符串池](../../../computer-science/systems/os.md) - String.intern()

### 设计模式
- [单例模式](../creational/singleton.md) - 单一对象管理
- [对象池模式](../creational/object-pool.md) - 可变对象复用
- [组合模式](./composite.md) - 树形结构共享
- [代理模式](./proxy.md) - 访问控制


> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念 (Concept)

**享元模式 (Flyweight Pattern)** 是一种结构型设计模式，它运用共享技术有效地支持大量细粒度对象的复用。通过共享已经存在的对象，减少内存占用，提高性能。

享元模式的核心思想是**分离内部状态（Intrinsic State）和外部状态（Extrinsic State）**：
- **内部状态**：存储在享元对象内部，不随环境改变，可以共享
- **外部状态**：取决于使用场景，随环境改变，不能共享

```
┌─────────────────────────────────────────────────────────────┐
│                    享元模式 (Flyweight)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   FlyweightFactory                                          │
│   ├─ flyweights: Map<key, Flyweight>                       │
│   ├─ getFlyweight(key) -> Flyweight                        │
│   └─ getCount() -> int                                     │
│                                                             │
│   Flyweight (interface)                                     │
│   └─ operation(extrinsicState)                              │
│          ▲                                                  │
│          │ implements                                       │
│   ┌──────┴──────┐                                           │
│   ▼             ▼                                           │
│ Concrete     Unshared                                       │
│ Flyweight    Concrete                                       │
│ (共享对象)    Flyweight                                     │
│ (存储内部状态) (存储所有状态)                                │
│                                                             │
│   Client -> 计算/传递外部状态 -> Flyweight.operation()       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 设计原则 (Principle)

享元模式遵循以下设计原则：

1. **单一职责原则 (Single Responsibility Principle)**：将状态分离，享元只管理内部状态
2. **对象复用**：通过共享减少对象创建数量
3. **状态分离**：明确区分内部状态和外部状态

**适用条件**：
- 程序使用了大量相似对象，造成内存开销
- 对象的大部分状态可以变为外部状态
- 如果移除外部状态，可以用相对较少的共享对象取代很多组对象

---

## 实现示例 (Example)

### 1. 文本编辑器中的字符渲染

```python
from typing import Dict, List

# ============== 享元：字符（内部状态） ==============

class CharacterFlyweight:
    """字符享元 - 只存储内部状态（字符本身）"""
    
    def __init__(self, char: str, font_family: str, font_size: int):
        # 内部状态：可以被多个上下文共享
        self._char = char
        self._font_family = font_family
        self._font_size = font_size
    
    def render(self, x: int, y: int, color: str):
        """
        渲染字符
        x, y, color 是外部状态，由调用方传入
        """
        print(f"渲染 '{self._char}' ({self._font_family} {self._font_size}pt) "
              f"在位置 ({x}, {y}), 颜色: {color}")
    
    def __repr__(self):
        return f"Character('{self._char}', {self._font_family}, {self._font_size})"

# ============== 享元工厂 ==============

class CharacterFactory:
    """字符享元工厂 - 管理和复用字符对象"""
    
    def __init__(self):
        self._characters: Dict[str, CharacterFlyweight] = {}
        self._created_count = 0
    
    def get_character(self, char: str, font_family: str, font_size: int) -> CharacterFlyweight:
        """获取字符享元，如果不存在则创建"""
        # 使用复合键：字符+字体+字号
        key = f"{char}:{font_family}:{font_size}"
        
        if key not in self._characters:
            # 创建新的享元对象
            self._characters[key] = CharacterFlyweight(char, font_family, font_size)
            self._created_count += 1
            print(f"[创建] {key}")
        else:
            print(f"[复用] {key}")
        
        return self._characters[key]
    
    def get_pool_size(self) -> int:
        """获取享元池大小"""
        return len(self._characters)
    
    def get_created_count(self) -> int:
        """获取创建的对象数量"""
        return self._created_count

# ============== 上下文：文档 ==============

class DocumentCharacter:
    """文档中的字符 - 包含外部状态"""
    
    def __init__(self, char_flyweight: CharacterFlyweight, x: int, y: int, color: str):
        self._flyweight = char_flyweight  # 享元引用
        self._x = x                       # 外部状态：位置X
        self._y = y                       # 外部状态：位置Y
        self._color = color               # 外部状态：颜色
    
    def render(self):
        """渲染时传入外部状态"""
        self._flyweight.render(self._x, self._y, self._color)

# ============== 使用示例 ==============

factory = CharacterFactory()

# 创建文档内容
# 假设我们渲染 "Hello World" 多次
document: List[DocumentCharacter] = []

# 第一行 "Hello"
x_pos = 0
for char in "Hello":
    flyweight = factory.get_character(char, "Arial", 12)
    document.append(DocumentCharacter(flyweight, x_pos, 0, "black"))
    x_pos += 10

# 第二行 "Hello"（不同的位置，但字符对象复用）
x_pos = 0
for char in "Hello":
    flyweight = factory.get_character(char, "Arial", 12)  # 复用！
    document.append(DocumentCharacter(flyweight, x_pos, 20, "red"))  # 不同颜色
    x_pos += 10

# 第三行 "World"
x_pos = 0
for char in "World":
    flyweight = factory.get_character(char, "Arial", 12)
    document.append(DocumentCharacter(flyweight, x_pos, 40, "blue"))
    x_pos += 10

# 大号字体的 "Hello"（需要新的享元，因为字号不同）
x_pos = 0
for char in "Hello":
    flyweight = factory.get_character(char, "Arial", 24)  # 新创建
    document.append(DocumentCharacter(flyweight, x_pos, 80, "black"))
    x_pos += 20

print(f"\n文档字符总数: {len(document)}")
print(f"享元池大小: {factory.get_pool_size()}")
print(f"实际创建的对象数: {factory.get_created_count()}")
print(f"节省的对象数: {len(document) - factory.get_created_count()}")

# 渲染文档
print("\n=== 渲染文档 ===")
for doc_char in document:
    doc_char.render()
```

### 2. 游戏中的森林渲染

```python
import random
from typing import Dict, List

# ============== 享元：树的类型（内部状态） ==============

class TreeType:
    """树的类型 - 享元对象"""
    
    def __init__(self, name: str, color: str, texture: str):
        # 内部状态：树的固有属性
        self._name = name
        self._color = color
        self._texture = texture
    
    def draw(self, canvas, x: int, y: int, size: int):
        """
        在画布上绘制树
        x, y, size 是外部状态
        """
        # 模拟绘制操作
        print(f"🌳 绘制 {self._name}树 (颜色:{self._color}, 纹理:{self._texture}) "
              f"在 ({x}, {y}), 大小:{size}")
    
    def __repr__(self):
        return f"TreeType({self._name}, {self._color})"

# ============== 享元工厂 ==============

class TreeFactory:
    """树类型工厂"""
    
    _tree_types: Dict[str, TreeType] = {}
    
    @classmethod
    def get_tree_type(cls, name: str, color: str, texture: str) -> TreeType:
        """获取树类型享元"""
        key = f"{name}:{color}:{texture}"
        if key not in cls._tree_types:
            cls._tree_types[key] = TreeType(name, color, texture)
            print(f"[创建树类型] {key}")
        return cls._tree_types[key]
    
    @classmethod
    def get_type_count(cls) -> int:
        return len(cls._tree_types)

# ============== 上下文：具体的树 ==============

class Tree:
    """具体的树实例 - 包含外部状态"""
    
    def __init__(self, x: int, y: int, size: int, tree_type: TreeType):
        self._x = x
        self._y = y
        self._size = size
        self._type = tree_type  # 共享的享元对象
    
    def draw(self, canvas):
        """绘制树"""
        self._type.draw(canvas, self._x, self._y, self._size)

# ============== 森林 ==============

class Forest:
    """森林 - 包含大量树"""
    
    def __init__(self):
        self._trees: List[Tree] = []
    
    def plant_tree(self, x: int, y: int, name: str, color: str, 
                   texture: str, size: int):
        """种植一棵树"""
        tree_type = TreeFactory.get_tree_type(name, color, texture)
        tree = Tree(x, y, size, tree_type)
        self._trees.append(tree)
    
    def draw(self, canvas):
        """绘制整个森林"""
        print(f"\n=== 绘制森林 ({len(self._trees)} 棵树) ===")
        for tree in self._trees:
            tree.draw(canvas)
    
    def get_stats(self):
        """获取统计信息"""
        return {
            "trees": len(self._trees),
            "tree_types": TreeFactory.get_type_count(),
            "memory_saved": len(self._trees) - TreeFactory.get_type_count()
        }

# ============== 使用示例 ==============

forest = Forest()

# 随机生成森林
random.seed(42)
tree_types = [
    ("橡树", "深绿", "rough"),
    ("松树", "翠绿", "needle"),
    ("桦树", "浅绿", "smooth"),
    ("枫树", "橙红", "rough"),
]

# 种植10000棵树（但只有4种类型）
for i in range(10000):
    name, color, texture = random.choice(tree_types)
    x = random.randint(0, 1000)
    y = random.randint(0, 1000)
    size = random.randint(5, 20)
    forest.plant_tree(x, y, name, color, texture, size)

# 绘制前100棵树作为演示
class Canvas:
    pass

forest.draw(Canvas())

# 统计信息
stats = forest.get_stats()
print(f"\n=== 统计信息 ===")
print(f"总树数: {stats['trees']:,}")
print(f"树类型数: {stats['tree_types']}")
print(f"节省的对象数: {stats['memory_saved']:,}")
print(f"内存使用比例: {stats['tree_types'] / stats['trees'] * 100:.2f}%")
```

### 3. 网页中缓存的DOM元素样式

```python
from typing import Dict, List

# ============== 享元：样式规则 ==============

class StyleRule:
    """CSS样式规则 - 享元对象"""
    
    def __init__(self, font_family: str, font_size: int, color: str, 
                 background_color: str, border: str):
        # 内部状态：样式属性
        self._font_family = font_family
        self._font_size = font_size
        self._color = color
        self._background_color = background_color
        self._border = border
    
    def apply_to(self, element_id: str):
        """将样式应用到指定元素"""
        print(f"应用样式到 #{element_id}: "
              f"font={self._font_family} {self._font_size}pt, "
              f"color={self._color}, bg={self._background_color}")
    
    def __repr__(self):
        return (f"Style({self._font_family} {self._font_size}pt, "
                f"{self._color} on {self._background_color})")

# ============== 样式工厂 ==============

class StyleFactory:
    """样式享元工厂"""
    
    _styles: Dict[str, StyleRule] = {}
    _cache_hits = 0
    _cache_misses = 0
    
    @classmethod
    def get_style(cls, font_family: str, font_size: int, color: str,
                  background_color: str = "transparent", border: str = "none") -> StyleRule:
        """获取或创建样式规则"""
        key = f"{font_family}:{font_size}:{color}:{background_color}:{border}"
        
        if key in cls._styles:
            cls._cache_hits += 1
            return cls._styles[key]
        
        cls._cache_misses += 1
        style = StyleRule(font_family, font_size, color, background_color, border)
        cls._styles[key] = style
        return style
    
    @classmethod
    def get_stats(cls):
        total = cls._cache_hits + cls._cache_misses
        return {
            "styles_created": len(cls._styles),
            "cache_hits": cls._cache_hits,
            "cache_misses": cls._cache_misses,
            "hit_rate": cls._cache_hits / total if total > 0 else 0
        }

# ============== 上下文：DOM元素 ==============

class DOMElement:
    """DOM元素 - 包含外部状态"""
    
    def __init__(self, element_id: str, tag: str, content: str,
                 x: int, y: int, style: StyleRule):
        self._id = element_id
        self._tag = tag
        self._content = content
        self._x = x          # 外部状态：位置
        self._y = y          # 外部状态：位置
        self._style = style  # 共享的样式享元
    
    def render(self):
        """渲染元素"""
        self._style.apply_to(self._id)
        print(f"  渲染 <{self._tag} id='{self._id}'>{self._content}</{self._tag}> "
              f"在 ({self._x}, {self._y})")

# ============== 网页 ==============

class WebPage:
    """网页 - 包含多个元素"""
    
    def __init__(self):
        self._elements: List[DOMElement] = []
    
    def add_element(self, element: DOMElement):
        self._elements.append(element)
    
    def render(self):
        print("\n=== 渲染网页 ===")
        for element in self._elements:
            element.render()

# ============== 使用示例 ==============

page = WebPage()

# 创建一些常用样式
heading_style = StyleFactory.get_style("Arial", 24, "black", "white")
body_style = StyleFactory.get_style("Arial", 14, "#333", "white")
button_style = StyleFactory.get_style("Arial", 14, "white", "#007bff", "1px solid")
alert_style = StyleFactory.get_style("Arial", 14, "#721c24", "#f8d7da")

# 添加多个元素（复用样式）
page.add_element(DOMElement("h1", "h1", "Welcome", 0, 0, heading_style))
page.add_element(DOMElement("p1", "p", "This is paragraph 1", 0, 50, body_style))
page.add_element(DOMElement("p2", "p", "This is paragraph 2", 0, 80, body_style))
page.add_element(DOMElement("btn1", "button", "Submit", 0, 120, button_style))
page.add_element(DOMElement("btn2", "button", "Cancel", 100, 120, button_style))
page.add_element(DOMElement("alert", "div", "Error message", 0, 160, alert_style))

# 添加更多元素（会复用已有样式）
page.add_element(DOMElement("h2", "h1", "Section 2", 0, 200, heading_style))  # 复用heading_style

page.render()

# 统计
stats = StyleFactory.get_stats()
print(f"\n=== 样式缓存统计 ===")
print(f"创建的样式数: {stats['styles_created']}")
print(f"缓存命中: {stats['cache_hits']}")
print(f"缓存未命中: {stats['cache_misses']}")
print(f"命中率: {stats['hit_rate']*100:.1f}%")
```

---

## 使用场景 (Use Cases)

| 场景 | 说明 |
|------|------|
| 大量相似对象 | 游戏中大量相同的敌人、树木、粒子 |
| 字符/文本渲染 | 文本编辑器中的字符对象 |
| 缓存 | 数据库连接池、线程池 |
| Web开发 | DOM节点样式复用、图标缓存 |
| 图形编辑 | 重复的形状、线条样式 |

---

## 面试要点 (Interview Points)

**Q1: 享元模式和对象池的区别？**

> - **享元模式**：关注共享不可变对象，对象没有状态或只有内部状态
> - **对象池**：关注复用可变对象，对象被借出、使用、归还
>
> 享元是"共享"，对象池是"借用"。

**Q2: 如何区分内部状态和外部状态？**

> - **内部状态**：独立于使用场景，可以被多个上下文共享（如字符'A'的字体信息）
> - **外部状态**：取决于使用场景，每个上下文不同（如字符'A'在文档中的位置）
>
> 判断标准：如果移除某些信息后对象可以被共享，那些信息就是外部状态。

**Q3: 享元模式和单例模式的区别？**

> - **单例模式**：一个类只有一个实例
> - **享元模式**：一个类有多个实例（每种内部状态一个），每个实例被多处共享
>
> 单例是"一个实例"，享元是"有限多个实例"。

**Q4: 享元模式的优缺点？**

> **优点**：
> - 大幅减少内存使用
> - 提高性能（减少对象创建）
> - 集中管理相似对象
>
> **缺点**：
> - 代码复杂度增加
> - 需要分离内外状态
> - 运行时的外部状态计算可能耗时

**Q5: 享元模式在Java中的应用？**

> - `String.intern()` 方法：字符串常量池
> - `Integer.valueOf()`：-128到127的整数缓存
> - Java 8的`ConcurrentHashMap`：分段锁使用享元

---
YW|
JS|## 相关概念 (Related Concepts)
YR|
HP|### 结构型设计模式
BX|
VY|享元模式与其他结构型模式共同关注如何组合类和对象以形成更大的结构：
ZJ|
KM|- **[适配器模式](./adapter.md)** - 解决接口不兼容问题，与享元模式都关注对象的包装与复用
ZH|- **[桥接模式](./bridge.md)** - 分离抽象与实现，与享元模式都强调状态的分离管理
NW|- **[组合模式](./composite.md)** - 处理树形结构的部分-整体层次，可与享元结合共享叶节点
SH|- **[装饰器模式](./decorator.md)** - 动态添加职责，与享元模式都涉及对象的包装和扩展
JN|- **[代理模式](./proxy.md)** - 控制对象访问，与享元工厂类似都管理对象的生命周期
SH|- **[外观模式](./facade.md)** - 简化接口，可与享元模式结合提供统一的对象获取入口
XN|
HP|### 设计原则与OOP
BX|
KM|- **[SOLID原则](../../solid-principles.md)** - 享元模式体现了单一职责原则(SRP)和开闭原则(OCP)
ZH|- **[面向对象设计](../../oop-design.md)** - 状态封装、对象复用的核心思想
NW|- **[设计模式总览](../../design-patterns.md)** - 返回查看所有23种设计模式的分类与关系
XN|
HP|### 相关模式
BX|
KM|- **[单例模式](../creational/singleton.md)** - 享元工厂常使用单例确保全局唯一
ZH|- **[工厂模式](../creational/factory.md)** - 享元工厂是工厂模式的应用，专门管理共享对象
XN|
HP|### 应用场景相关
BX|
- [对象池模式](../../references/object-pool.md) - 与享元模式都关注对象复用，但关注点和实现不同

## 相关引用 (References)

- 相关： - 唯一实例
- 相关： - 资源复用
