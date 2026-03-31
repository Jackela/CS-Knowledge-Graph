## 版权声明

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

## 相关引用 (References)

- 返回：[设计模式总览](../../design-patterns.md)
- 相关：[装饰器模式](./decorator.md) - 动态添加功能
- 相关：[适配器模式](./adapter.md) - 接口转换
- 原理：[SOLID原则](../../solid-principles.md)
