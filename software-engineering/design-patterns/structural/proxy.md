# 代理模式 (Proxy Pattern)

## 概念

代理模式（Proxy Pattern）是一种**结构型设计模式**，它为其他对象提供一种代理以控制对这个对象的访问。代理对象在客户端和目标对象之间起到中介的作用，可以在不修改目标对象的前提下，增加额外的功能。

> **核心思想**: 通过引入代理对象来控制对真实对象的访问，实现访问控制、延迟加载、日志记录等功能。

```
直接访问：                              通过代理访问：
                                        
Client ──▶ RealSubject                  Client ──▶ Proxy ──▶ RealSubject
                                        
客户端直接操作目标对象                  代理控制访问，可添加额外逻辑
                                        （权限检查、缓存、日志等）
```

---

## 原理

### 为什么需要代理模式？

1. **访问控制**: 在访问对象之前进行权限检查
2. **延迟加载**: 延迟创建开销大的对象，只在需要时创建
3. **远程代理**: 为远程对象提供本地代表
4. **智能引用**: 在访问对象时执行额外操作（计数、缓存、日志）
5. **保护代理**: 控制对原始对象的访问权限

### 代理类型

| 类型 | 用途 | 典型场景 |
|------|------|----------|
| 虚拟代理 | 延迟加载 | 大图片加载、复杂对象初始化 |
| 保护代理 | 访问控制 | 权限检查、角色验证 |
| 远程代理 | 访问远程对象 | RPC、Web Service |
| 智能引用 | 增强功能 | 引用计数、日志记录、缓存 |
| 缓存代理 | 缓存结果 |  expensive 操作结果缓存 |

### 核心角色

| 角色 | 职责 |
|------|------|
| Subject | 抽象主题，定义真实主题和代理的共同接口 |
| RealSubject | 真实主题，定义代理所代表的真实对象 |
| Proxy | 代理，保存对真实主题的引用，控制访问 |
| Client | 客户端，通过 Subject 接口操作 |

### 优缺点

**优点：**
- 职责清晰，真实主题只关注业务逻辑
- 高扩展性，代理可以灵活添加功能
- 保护真实主题，控制访问
- 符合开闭原则

**缺点：**
- 增加系统复杂度
- 请求处理速度变慢
- 需要额外的工作量实现代理

---

## 实现方式

### 1. 虚拟代理（延迟加载）

```python
from abc import ABC, abstractmethod


# 抽象主题
class Image(ABC):
    @abstractmethod
    def display(self):
        pass
    
    @abstractmethod
    def get_filename(self) -> str:
        pass


# 真实主题 - 真实图片
class RealImage(Image):
    """真实图片类，加载和显示真实图片（开销大）"""
    
    def __init__(self, filename: str):
        self._filename = filename
        self._load_from_disk()
    
    def _load_from_disk(self):
        """模拟从磁盘加载图片（耗时操作）"""
        print(f"[RealImage] 从磁盘加载图片: {self._filename} ...")
        import time
        time.sleep(1)
        print(f"[RealImage] 图片加载完成: {self._filename}")
    
    def display(self):
        print(f"[RealImage] 显示图片: {self._filename}")
    
    def get_filename(self) -> str:
        return self._filename


# 代理 - 图片代理
class ProxyImage(Image):
    """图片代理，延迟加载真实图片"""
    
    def __init__(self, filename: str):
        self._filename = filename
        self._real_image = None  # 延迟创建
    
    def display(self):
        # 延迟加载：只在需要显示时才创建真实图片
        if self._real_image is None:
            print(f"[ProxyImage] 首次显示，创建真实图片对象")
            self._real_image = RealImage(self._filename)
        self._real_image.display()
    
    def get_filename(self) -> str:
        return self._filename


# 使用场景
print("=== 虚拟代理 - 图片延迟加载 ===\n")

# 创建代理对象（不会立即加载图片）
images = [
    ProxyImage("photo1.jpg"),
    ProxyImage("photo2.jpg"),
    ProxyImage("photo3.jpg")
]
print("图片代理创建完成（未加载实际图片）\n")

# 只显示第一张图片（此时才加载）
print("显示第一张图片:")
images[0].display()

print("\n再次显示第一张图片（从缓存）:")
images[0].display()
```

### 2. 保护代理（访问控制）

```python
from abc import ABC, abstractmethod
from enum import Enum


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"


class User:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role
    
    def has_permission(self, permission: Permission) -> bool:
        permissions = {
            "admin": [Permission.READ, Permission.WRITE, Permission.DELETE],
            "editor": [Permission.READ, Permission.WRITE],
            "viewer": [Permission.READ]
        }
        return permission in permissions.get(self.role, [])


# 抽象主题 - 文档操作
class Document(ABC):
    @abstractmethod
    def read(self) -> str:
        pass
    
    @abstractmethod
    def write(self, content: str):
        pass
    
    @abstractmethod
    def delete(self):
        pass


# 真实主题 - 真实文档
class RealDocument(Document):
    """真实文档类，实现实际的文档操作"""
    
    def __init__(self, filename: str):
        self._filename = filename
        self._content = ""
        print(f"[RealDocument] 创建文档: {filename}")
    
    def read(self) -> str:
        print(f"[RealDocument] 读取文档: {self._filename}")
        return self._content
    
    def write(self, content: str):
        print(f"[RealDocument] 写入文档: {self._filename}")
        self._content = content
    
    def delete(self):
        print(f"[RealDocument] 删除文档: {self._filename}")


# 保护代理 - 文档代理
class DocumentProxy(Document):
    """文档代理，控制对文档的访问"""
    
    def __init__(self, filename: str, user: User):
        self._filename = filename
        self._user = user
        self._real_document = None
    
    def _check_access(self, permission: Permission) -> bool:
        """检查用户权限"""
        if not self._user.has_permission(permission):
            print(f"[DocumentProxy] 访问拒绝: 用户 {self._user.username} "
                  f"没有 {permission.value} 权限")
            return False
        return True
    
    def _get_real_document(self) -> RealDocument:
        """获取真实文档对象（延迟加载）"""
        if self._real_document is None:
            self._real_document = RealDocument(self._filename)
        return self._real_document
    
    def read(self) -> str:
        if not self._check_access(Permission.READ):
            raise PermissionError("没有读取权限")
        return self._get_real_document().read()
    
    def write(self, content: str):
        if not self._check_access(Permission.WRITE):
            raise PermissionError("没有写入权限")
        self._get_real_document().write(content)
    
    def delete(self):
        if not self._check_access(Permission.DELETE):
            raise PermissionError("没有删除权限")
        self._get_real_document().delete()
```

### 3. 智能引用代理（日志、缓存、计数）

```python
from abc import ABC, abstractmethod
from typing import Optional
import time


# 抽象主题
class Service(ABC):
    @abstractmethod
    def fetch_data(self, query: str) -> str:
        pass


# 真实主题 - 数据库服务
class DatabaseService(Service):
    """真实数据库服务"""
    
    def fetch_data(self, query: str) -> str:
        print(f"[Database] 执行查询: {query}")
        time.sleep(1)  # 模拟耗时操作
        return f"查询结果: {query}"


# 智能引用代理
class SmartProxy(Service):
    """智能代理，提供缓存、日志、计数功能"""
    
    def __init__(self, real_service: Service):
        self._real_service = real_service
        self._cache = {}
        self._access_count = 0
        self._cache_hit_count = 0
    
    def fetch_data(self, query: str) -> str:
        self._access_count += 1
        print(f"[SmartProxy] 第 {self._access_count} 次访问")
        
        # 1. 检查缓存
        if query in self._cache:
            self._cache_hit_count += 1
            print(f"[SmartProxy] 缓存命中! (命中率: {self._get_hit_rate():.1%})")
            return self._cache[query]
        
        # 2. 记录日志
        print(f"[SmartProxy] 缓存未命中，执行实际查询")
        start_time = time.time()
        
        # 3. 调用真实服务
        result = self._real_service.fetch_data(query)
        
        # 4. 存入缓存
        self._cache[query] = result
        
        # 5. 记录耗时
        elapsed = time.time() - start_time
        print(f"[SmartProxy] 查询耗时: {elapsed:.2f}s")
        
        return result
    
    def _get_hit_rate(self) -> float:
        if self._access_count == 0:
            return 0.0
        return self._cache_hit_count / self._access_count
    
    def get_stats(self):
        print(f"\n[SmartProxy] 统计信息:")
        print(f"  总访问次数: {self._access_count}")
        print(f"  缓存命中次数: {self._cache_hit_count}")
        print(f"  缓存命中率: {self._get_hit_rate():.1%}")
        print(f"  缓存条目数: {len(self._cache)}")
```

### 4. Java 实现示例

```java
// 抽象主题
public interface BankAccount {
    void deposit(double amount);
    void withdraw(double amount);
    double getBalance();
}

// 真实主题
public class RealBankAccount implements BankAccount {
    private double balance;
    private String accountNumber;
    
    public RealBankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
        System.out.println("创建真实账户: " + accountNumber);
    }
    
    @Override
    public void deposit(double amount) {
        balance += amount;
        System.out.println("存入: ¥" + amount + ", 当前余额: ¥" + balance);
    }
    
    @Override
    public void withdraw(double amount) {
        if (balance >= amount) {
            balance -= amount;
            System.out.println("取出: ¥" + amount + ", 当前余额: ¥" + balance);
        } else {
            System.out.println("余额不足");
        }
    }
    
    @Override
    public double getBalance() {
        return balance;
    }
}

// 代理 - 日志和事务代理
public class BankAccountProxy implements BankAccount {
    private RealBankAccount realAccount;
    private String accountNumber;
    private double initialBalance;
    
    public BankAccountProxy(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.initialBalance = initialBalance;
    }
    
    private RealBankAccount getRealAccount() {
        if (realAccount == null) {
            realAccount = new RealBankAccount(accountNumber, initialBalance);
        }
        return realAccount;
    }
    
    @Override
    public void deposit(double amount) {
        log("存款操作", amount);
        getRealAccount().deposit(amount);
        log("存款完成", amount);
    }
    
    private void log(String operation, double amount) {
        System.out.println("[代理日志] " + operation + 
                          (amount > 0 ? ", 金额: ¥" + amount : "") +
                          ", 时间: " + java.time.LocalDateTime.now());
    }
    
    @Override
    public void withdraw(double amount) {
        log("取款操作", amount);
        getRealAccount().withdraw(amount);
    }
    
    @Override
    public double getBalance() {
        return getRealAccount().getBalance();
    }
}
```

---

## 示例

### UML 图

```
┌─────────────────────────────────────────────────────────────────┐
│                        代理模式 UML                             │
│                   （图片加载示例）                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  <<interface>>                                          │   │
│  │          Image                                          │   │
│  │                                                         │   │
│  │  +display(): void                                       │   │
│  │  +get_filename(): str                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ▲                                    ▲               │
│           │                                    │               │
│  ┌────────┴────────┐              ┌────────────┴────────────┐  │
│  │                 │              │                         │  │
│  │   RealImage     │              │       ProxyImage        │  │
│  │                 │              │                         │  │
│  │ -_filename      │              │ -_filename              │  │
│  │                 │              │ -_real_image: RealImage │  │
│  │ +display()      │              │                         │  │
│  │ +get_filename() │              │ +display()              │  │
│  │                 │              │   - lazy loading        │  │
│  │ -_load_from_disk()             │   - caching             │  │
│  │                 │              │ +get_filename()         │  │
│  └─────────────────┘              └─────────────────────────┘  │
│                                                                 │
│  代理类型对比：                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  类型           │  用途            │  实现要点          │   │
│  ├─────────────────┼──────────────────┼────────────────────┤   │
│  │  虚拟代理       │  延迟加载        │  需要时创建对象    │   │
│  │  保护代理       │  访问控制        │  权限检查          │   │
│  │  远程代理       │  访问远程对象    │  网络通信封装      │   │
│  │  智能引用       │  增强功能        │  日志/缓存/计数    │   │
│  │  缓存代理       │  结果缓存        │  缓存策略管理      │   │
│  └─────────────────┴──────────────────┴────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

1. **Q: 什么是代理模式？**
   
   A: 代理模式是一种结构型设计模式，为其他对象提供一种代理以控制对这个对象的访问。代理对象在客户端和目标对象之间起到中介作用，可以增加额外的功能而不修改目标对象。

2. **Q: 代理模式与装饰器模式的区别？**
   
   A: 两者都包装对象，但目的不同：代理模式侧重**访问控制**，装饰器模式侧重**功能增强**。代理通常只有一个，装饰器可以层层叠加；代理控制对象的创建和访问，装饰器保持接口不变添加功能。

3. **Q: 代理模式与适配器模式的区别？**
   
   A: 代理模式保持接口不变，控制对相同接口对象的访问；适配器模式转换接口，使不兼容的接口能够协同工作。

4. **Q: 动态代理和静态代理的区别？**
   
   A: 静态代理在编译时确定代理类，需要为每个被代理类写代理类；动态代理在运行时生成代理类（如 Java 的 Proxy.newProxyInstance()），一个代理类可以代理多个接口，更灵活。

5. **Q: 实际应用场景有哪些？**
   
   A: 常见场景包括：
   - Spring AOP（面向切面编程）
   - Hibernate 延迟加载
   - RPC 远程调用框架（Dubbo、gRPC）
   - 权限检查、日志记录、事务管理
   - 图片/视频懒加载
   - 数据库连接池

---

## 相关概念

### 数据结构
- [接口与抽象类](../../oop-design.md) - 代理接口设计
- [哈希表](../../../computer-science/data-structures/hash-table.md) - 代理缓存实现

### 算法
- [缓存算法](../../../computer-science/algorithms/caching.md) - 缓存代理策略

### 复杂度分析
- [时间复杂度](../../../references/time-complexity.md) - 代理调用开销
- [空间复杂度](../../../references/space-complexity.md) - 代理对象内存

### 系统实现
- [RPC 框架](../../architecture-patterns/microservices.md) - 远程代理实现
- [数据库连接池](../../../computer-science/databases/indexing.md) - 资源管理代理
- [AOP 框架](../../architecture-patterns/dependency-injection.md) - 动态代理应用

### 设计模式
- [装饰器模式](./decorator.md) - 功能动态增强
- [适配器模式](./adapter.md) - 接口转换
- [外观模式](./facade.md) - 简化接口
- [享元模式](./flyweight.md) - 对象共享


> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念 (Concept)

**代理模式 (Proxy Pattern)** 是一种结构型设计模式，它为另一个对象提供一个替身或占位符，以控制对这个对象的访问。

代理模式的核心思想是**通过代理对象间接访问目标对象**，可以在不改变目标对象的情况下，增加额外的控制逻辑。

```
┌─────────────────────────────────────────────────────────────┐
│                    代理模式 (Proxy)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Client ──────▶ Subject (interface)                        │
│                   ├─ request()                              │
│                        ▲                                    │
│                        │ implements                         │
│            ┌───────────┴───────────┐                        │
│            ▼                       ▼                        │
│   ┌──────────────┐      ┌──────────────┐                    │
│   │ RealSubject  │      │    Proxy     │                    │
│   │ (真实对象)   │      │   (代理)     │                    │
│   │ request()    │      │  ├─ realSubject                   │
│   │ (核心业务)   │      │  ├─ request()                     │
│   └──────────────┘      │  │  ├─ 前置处理                   │
│                         │  │  ├─ realSubject.request()      │
│                         │  │  └─ 后置处理                   │
│                         │  └─ ...                           │
│                         └──────────────┘                    │
│                                                             │
│   代理类型：虚拟代理、保护代理、远程代理、缓存代理、智能引用    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 设计原则 (Principle)

代理模式遵循以下设计原则：

1. **单一职责原则 (Single Responsibility Principle)**：代理负责访问控制，真实对象负责业务逻辑
2. **开闭原则 (Open/Closed Principle)**：通过代理扩展功能，无需修改真实对象
3. **依赖倒置原则 (Dependency Inversion Principle)**：客户端依赖于抽象接口

**代理类型**：
- **虚拟代理 (Virtual Proxy)**：延迟加载大对象
- **保护代理 (Protection Proxy)**：访问权限控制
- **远程代理 (Remote Proxy)**：访问远程对象
- **缓存代理 (Cache Proxy)**：缓存结果
- **智能引用 (Smart Reference)**：引用计数、延迟释放等

---

## 实现示例 (Example)

### 1. 虚拟代理：延迟加载图片

```python
from abc import ABC, abstractmethod
from typing import Optional
import time

# ============== 主题接口 ==============

class Image(ABC):
    """图片接口"""
    
    @abstractmethod
    def display(self):
        pass
    
    @abstractmethod
    def get_size(self) -> tuple:
        pass

# ============== 真实主题 ==============

class RealImage(Image):
    """真实图片 - 加载成本高"""
    
    def __init__(self, filename: str):
        self._filename = filename
        self._width = 0
        self._height = 0
        self._load_image()  # 加载成本高
    
    def _load_image(self):
        """模拟从磁盘加载图片"""
        print(f"[RealImage] 从磁盘加载: {self._filename}...")
        time.sleep(2)  # 模拟加载时间
        self._width = 1920
        self._height = 1080
        print(f"[RealImage] 加载完成: {self._filename}")
    
    def display(self):
        print(f"[RealImage] 显示: {self._filename} ({self._width}x{self._height})")
    
    def get_size(self) -> tuple:
        return (self._width, self._height)

# ============== 虚拟代理 ==============

class ImageProxy(Image):
    """图片代理 - 延迟加载"""
    
    def __init__(self, filename: str):
        self._filename = filename
        self._real_image: Optional[RealImage] = None
        self._cached_size = (0, 0)
    
    def display(self):
        """显示时才加载真实图片"""
        if self._real_image is None:
            print(f"[ImageProxy] 首次访问，创建真实图片对象...")
            self._real_image = RealImage(self._filename)
        self._real_image.display()
    
    def get_size(self) -> tuple:
        """可能不需要加载就能获得大小（从元数据）"""
        if self._real_image:
            return self._real_image.get_size()
        
        # 模拟从元数据读取
        if self._cached_size == (0, 0):
            print(f"[ImageProxy] 从元数据读取图片大小...")
            self._cached_size = (1920, 1080)  # 假设从EXIF读取
        
        return self._cached_size

# ============== 使用示例 ==============

print("=== 使用代理模式 ===")
print("创建图片列表（此时不加载实际图片）：")

images = [
    ImageProxy("photo1.jpg"),
    ImageProxy("photo2.jpg"),
    ImageProxy("photo3.jpg"),
]

print(f"\n获取第一张图片大小（无需加载）：")
size = images[0].get_size()
print(f"图片大小: {size}")

print(f"\n显示第一张图片（此时加载）：")
images[0].display()

print(f"\n再次显示第一张图片（已缓存）：")
images[0].display()

print(f"\n显示第二张图片（首次加载）：")
images[1].display()
```

### 2. 保护代理：访问控制

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"

class User:
    """用户"""
    def __init__(self, username: str, permissions: List[Permission]):
        self.username = username
        self.permissions = permissions
    
    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

# ============== 文档接口 ==============

class Document(ABC):
    """文档接口"""
    
    @abstractmethod
    def read(self) -> str:
        pass
    
    @abstractmethod
    def write(self, content: str):
        pass
    
    @abstractmethod
    def delete(self):
        pass
    
    @abstractmethod
    def get_info(self) -> Dict:
        pass

# ============== 真实文档 ==============

class RealDocument(Document):
    """真实文档"""
    
    def __init__(self, title: str, content: str, owner: str):
        self._title = title
        self._content = content
        self._owner = owner
    
    def read(self) -> str:
        return self._content
    
    def write(self, content: str):
        print(f"[RealDocument] 写入文档: {self._title}")
        self._content = content
    
    def delete(self):
        print(f"[RealDocument] 删除文档: {self._title}")
    
    def get_info(self) -> Dict:
        return {
            "title": self._title,
            "owner": self._owner,
            "length": len(self._content)
        }

# ============== 保护代理 ==============

class ProtectedDocument(Document):
    """受保护的文档代理"""
    
    def __init__(self, document: RealDocument, current_user: User):
        self._document = document
        self._current_user = current_user
    
    def _check_permission(self, permission: Permission):
        """检查权限"""
        if not self._current_user.has_permission(permission):
            raise PermissionError(
                f"用户 '{self._current_user.username}' 没有 '{permission.value}' 权限"
            )
    
    def read(self) -> str:
        """所有人都可以读取"""
        print(f"[ProtectedDocument] {self._current_user.username} 读取文档")
        return self._document.read()
    
    def write(self, content: str):
        """需要写权限"""
        self._check_permission(Permission.WRITE)
        print(f"[ProtectedDocument] {self._current_user.username} 写入文档")
        self._document.write(content)
    
    def delete(self):
        """需要删除权限"""
        self._check_permission(Permission.DELETE)
        print(f"[ProtectedDocument] {self._current_user.username} 删除文档")
        self._document.delete()
    
    def get_info(self) -> Dict:
        """所有人都可以查看信息"""
        return self._document.get_info()

# ============== 文档管理器 ==============

class DocumentManager:
    """文档管理器 - 创建受保护的文档"""
    
    def __init__(self):
        self._documents: Dict[str, RealDocument] = {}
    
    def create_document(self, title: str, content: str, owner: str) -> Document:
        """创建文档"""
        doc = RealDocument(title, content, owner)
        self._documents[title] = doc
        return doc
    
    def get_document(self, title: str, user: User) -> Document:
        """获取文档（返回受保护代理）"""
        real_doc = self._documents.get(title)
        if not real_doc:
            raise ValueError(f"文档不存在: {title}")
        
        # 返回保护代理而非真实文档
        return ProtectedDocument(real_doc, user)

# ============== 使用示例 ==============

manager = DocumentManager()
manager.create_document("机密报告.pdf", "这是机密内容...", "admin")

# 管理员用户
admin = User("admin", [Permission.READ, Permission.WRITE, Permission.DELETE])
# 普通用户
user = User("user", [Permission.READ])

print("=== 管理员操作 ===")
admin_doc = manager.get_document("机密报告.pdf", admin)
print(f"读取: {admin_doc.read()[:20]}...")
admin_doc.write("更新后的内容")

print("\n=== 普通用户操作 ===")
user_doc = manager.get_document("机密报告.pdf", user)
print(f"读取: {user_doc.read()[:20]}...")

try:
    user_doc.write("尝试写入")
except PermissionError as e:
    print(f"权限错误: {e}")
```

### 3. 缓存代理

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import hashlib

# ============== 数据服务接口 ==============

class DataService(ABC):
    """数据服务接口"""
    
    @abstractmethod
    def fetch_data(self, query: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def calculate(self, params: Dict) -> float:
        pass

# ============== 真实数据服务 ==============

class RealDataService(DataService):
    """真实数据服务 - 操作耗时"""
    
    def fetch_data(self, query: str) -> Dict[str, Any]:
        """模拟数据库查询"""
        print(f"[RealDataService] 执行数据库查询: {query}")
        time.sleep(2)  # 模拟慢查询
        
        # 模拟返回结果
        return {
            "query": query,
            "results": [f"result_{i}" for i in range(5)],
            "timestamp": time.time()
        }
    
    def calculate(self, params: Dict) -> float:
        """模拟复杂计算"""
        print(f"[RealDataService] 执行复杂计算: {params}")
        time.sleep(3)  # 模拟计算时间
        
        # 模拟计算结果
        result = sum(params.values()) * 1.5
        return result

# ============== 缓存代理 ==============

class CachedDataService(DataService):
    """缓存代理"""
    
    def __init__(self, service: DataService, ttl: int = 60):
        self._service = service
        self._cache: Dict[str, Dict] = {}
        self._ttl = ttl  # 缓存有效期（秒）
    
    def _get_cache_key(self, *args) -> str:
        """生成缓存键"""
        key_data = str(args)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_valid(self, entry: Dict) -> bool:
        """检查缓存是否有效"""
        return time.time() - entry["timestamp"] < self._ttl
    
    def fetch_data(self, query: str) -> Dict[str, Any]:
        """带缓存的数据获取"""
        cache_key = self._get_cache_key("fetch_data", query)
        
        # 检查缓存
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if self._is_valid(entry):
                print(f"[CachedDataService] 缓存命中: {query}")
                return entry["data"]
            else:
                print(f"[CachedDataService] 缓存过期: {query}")
        
        # 调用真实服务
        result = self._service.fetch_data(query)
        
        # 存入缓存
        self._cache[cache_key] = {
            "data": result,
            "timestamp": time.time()
        }
        
        return result
    
    def calculate(self, params: Dict) -> float:
        """带缓存的计算"""
        cache_key = self._get_cache_key("calculate", params)
        
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if self._is_valid(entry):
                print(f"[CachedDataService] 缓存命中计算: {params}")
                return entry["data"]
        
        result = self._service.calculate(params)
        
        self._cache[cache_key] = {
            "data": result,
            "timestamp": time.time()
        }
        
        return result
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        print("[CachedDataService] 缓存已清空")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "entries": len(self._cache),
            "ttl": self._ttl
        }

# ============== 使用示例 ==============

print("=== 使用缓存代理 ===")
real_service = RealDataService()
cached_service = CachedDataService(real_service, ttl=5)

print("\n第一次查询（无缓存）：")
result1 = cached_service.fetch_data("SELECT * FROM users")

print("\n第二次查询（命中缓存）：")
result2 = cached_service.fetch_data("SELECT * FROM users")

print("\n计算（无缓存）：")
calc1 = cached_service.calculate({"a": 10, "b": 20})

print("\n计算（命中缓存）：")
calc2 = cached_service.calculate({"a": 10, "b": 20})

print(f"\n缓存统计: {cached_service.get_cache_stats()}")
```

---

## 使用场景 (Use Cases)

| 场景 | 说明 |
|------|------|
| 延迟加载 | 大对象的按需加载（虚拟代理） |
| 访问控制 | 权限验证（保护代理） |
| 远程调用 | RPC、WebService客户端（远程代理） |
| 缓存 | 结果缓存，避免重复计算（缓存代理） |
| 监控 | 方法调用统计、日志记录 |
| 智能指针 | 引用计数、延迟释放 |

---

## 面试要点 (Interview Points)

**Q1: 代理模式和装饰器模式的区别？**

> - **代理模式**：控制对对象的访问，通常代理和真实对象的关系在编译时确定
> - **装饰器模式**：动态添加功能，可以层层叠加
>
> 代理是"访问控制"，装饰器是"功能增强"。代理通常是单一职责，装饰器通常是层层叠加。

**Q2: 代理模式和适配器模式的区别？**

> - **代理模式**：接口与真实对象相同，目的是控制访问
> - **适配器模式**：接口与目标不同，目的是接口转换
>
> 代理是"相同接口，不同控制"，适配器是"不同接口，功能相同"。

**Q3: 静态代理和动态代理的区别？**

> - **静态代理**：编译时代码确定，需要为每个接口写代理类
> - **动态代理**：运行时生成代理类，Java使用`Proxy`类和`InvocationHandler`
>
> Java中：JDK动态代理（基于接口）、CGLIB（基于继承）

**Q4: 代理模式在Spring中的应用？**

> - **AOP（面向切面编程）**：使用动态代理实现
> - **事务管理**：`@Transactional`使用代理控制事务
> - **懒加载**：JPA/Hibernate的延迟加载使用代理
> - **安全控制**：Spring Security的方法级安全

**Q5: 如何实现一个通用的日志代理？**

```python
> class LoggingProxy:>     def __init__(self, target):>         self._target = target
>     >     def __getattr__(self, name):>         attr = getattr(self._target, name)>         if callable(attr):>             def wrapper(*args, **kwargs):>                 print(f"调用 {name}({args}, {kwargs})")>                 result = attr(*args, **kwargs)>                 print(f"返回: {result}")>                 return result
>             return wrapper
>         return attr
```

---

## 相关概念

### 结构型设计模式 (Structural Patterns)

代理模式常与其他结构型模式协同使用：

| 模式 | 关联说明 |
|------|----------|
| [适配器模式](./adapter.md) | 代理保持相同接口控制访问，适配器转换不同接口 |
| [桥接模式](./bridge.md) | 桥接分离抽象与实现，代理控制对实现的访问 |
| [组合模式](./composite.md) | 代理可作为组合中节点的访问控制器 |
| [装饰器模式](./decorator.md) | 装饰器动态添加功能，代理控制访问行为 |
| [外观模式](./facade.md) | 外观简化复杂接口，代理控制对对象的访问 |
| [享元模式](./flyweight.md) | 虚拟代理与享元都用于优化资源使用 |

### 面向对象设计原则

代理模式体现了以下设计原则的应用：

- [SOLID原则](../../solid-principles.md) - 单一职责、开闭原则、依赖倒置
- [面向对象设计](../../oop-design.md) - 封装、多态与接口隔离

### 安全与访问控制

保护代理与安全领域的核心概念密切相关：

- [认证与授权](../../../security/authentication.md) - 身份验证是保护代理的基础
- [访问控制](../../../security/system-security/access-control.md) - 基于角色的权限验证(RBAC)
- [审计日志](../../../security/system-security/audit-logging.md) - 操作追踪与行为监控

### 创建型与行为型模式

代理常与以下模式结合实现特定功能：

- [单例模式](../creational/singleton.md) - 代理控制对单例的访问
- [工厂模式](../creational/factory.md) - 动态创建代理实例
- [策略模式](../behavioral/strategy.md) - 代理中切换不同访问策略
- [观察者模式](../behavioral/observer.md) - 代理触发访问事件通知

#### 计算机科学基础

- [虚拟内存与缓存](../../../computer-science/systems/virtual-memory.md) - 虚拟代理的内存管理原理
- [内存管理](../../../computer-science/systems/memory-management.md) - 智能指针与资源代理
- [文件系统缓存](../../../computer-science/systems/file-systems.md) - 文件访问的缓存代理机制

---

## 相关引用 (References)

- 返回：[设计模式总览](../../design-patterns.md)
- 相关： - 动态添加功能
- 相关： - 接口转换
- 原理：
