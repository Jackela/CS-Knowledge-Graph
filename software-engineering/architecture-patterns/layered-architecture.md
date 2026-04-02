# 分层架构 (Layered Architecture)

## 简介

**分层架构**（Layered Architecture）是最常见的软件架构模式之一，将应用程序组织成水平层，每层有特定的职责和角色。上层依赖下层，下层为上层提供服务。这种模式将关注点分离，提高了代码的可维护性和可测试性。

## 核心概念

| 概念 | 说明 |
|------|------|
| **Presentation Layer** | 表现层，处理用户界面和用户交互 |
| **Business Logic Layer** | 业务逻辑层，包含核心业务规则和逻辑 |
| **Data Access Layer** | 数据访问层，负责与数据库或其他存储交互 |
| **Dependency Rule** | 依赖规则，上层依赖下层，下层不依赖上层 |
| **Abstraction** | 抽象，通过接口隔离层与层之间的直接依赖 |

## 实现方式

### 1. 三层架构示例

```python
# data_access_layer.py
from abc import ABC, abstractmethod
from typing import List, Optional

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[dict]:
        pass
    
    @abstractmethod
    def save(self, user: dict) -> None:
        pass

class SqlUserRepository(UserRepository):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_by_id(self, user_id: int) -> Optional[dict]:
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def save(self, user: dict) -> None:
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user['name'], user['email'])
        )
        self.db.commit()

# business_logic_layer.py
class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
    
    def get_user(self, user_id: int) -> Optional[dict]:
        return self.user_repo.get_by_id(user_id)
    
    def create_user(self, name: str, email: str) -> dict:
        if not self._is_valid_email(email):
            raise ValueError("Invalid email format")
        
        user = {'name': name, 'email': email}
        self.user_repo.save(user)
        return user
    
    def _is_valid_email(self, email: str) -> bool:
        import re
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

# presentation_layer.py
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def handle_get_user(self, user_id: int) -> dict:
        user = self.user_service.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {'data': user}, 200
    
    def handle_create_user(self, request_data: dict) -> dict:
        try:
            user = self.user_service.create_user(
                request_data['name'],
                request_data['email']
            )
            return {'data': user, 'message': 'User created'}, 201
        except ValueError as e:
            return {'error': str(e)}, 400

# main.py - 组装应用
import sqlite3

def create_app():
    db = sqlite3.connect('app.db')
    
    # 依赖注入
    user_repo = SqlUserRepository(db)
    user_service = UserService(user_repo)
    user_controller = UserController(user_service)
    
    return user_controller

if __name__ == '__main__':
    app = create_app()
```

### 2. 使用依赖注入框架

```python
# dependency_injection.py
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    db = providers.Singleton(
        sqlite3.connect,
        config.database.url
    )
    
    user_repository = providers.Factory(
        SqlUserRepository,
        db_connection=db
    )
    
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository
    )
    
    user_controller = providers.Factory(
        UserController,
        user_service=user_service
    )

# 使用容器
container = Container()
container.config.database.url.from_env("DATABASE_URL")
controller = container.user_controller()
```

## 应用场景

- **企业应用**: ERP、CRM 等业务系统
- **Web 应用**: 传统的 MVC 应用
- **桌面应用**: 需要清晰分层的业务软件
- **微服务内部**: 单个服务的内部架构

## 面试要点

**Q: 分层架构的优点是什么？**
A: 关注点分离、可维护性高、易于测试、团队分工明确、便于替换实现（如换数据库）。

**Q: 分层架构的缺点是什么？**
A: 性能开销（层层调用）、过度设计风险、变更可能影响多层、不适用于简单应用。

**Q: 如何避免分层架构的层间泄漏？**
A: 通过接口定义契约、DTO 传输数据、不允许跨层调用、使用依赖注入。

## 相关概念

- [MVC](./mvc.md) - 表现层模式
- [依赖注入](./dependency-injection.md) - 解耦技术
- [整洁架构](./clean-architecture.md) - 演进架构
