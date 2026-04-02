# 整洁架构 (Clean Architecture)

## 简介

**整洁架构**（Clean Architecture）由 Robert C. Martin（Uncle Bob）提出，是一种软件架构设计理念，强调业务逻辑独立于框架、UI、数据库和外部接口。通过依赖规则（Dependency Rule），内层不依赖外层，使系统更易于测试、维护和演进。

## 核心概念

| 概念 | 说明 |
|------|------|
| **Entities** | 实体，包含企业级业务规则，独立于框架 |
| **Use Cases** | 用例，包含应用特定业务规则 |
| **Interface Adapters** | 接口适配器，转换数据格式 |
| **Frameworks & Drivers** | 框架和驱动，最外层，包含工具 |
| **Dependency Rule** | 依赖规则，代码依赖只能向内指向 |

## 架构层次

```
┌─────────────────────────────────────────┐
│   Frameworks & Drivers (UI, DB, Web)   │
├─────────────────────────────────────────┤
│   Interface Adapters (Controllers,     │
│   Presenters, Gateways)                │
├─────────────────────────────────────────┤
│   Application Business Rules (Use      │
│   Cases, Interactors)                  │
├─────────────────────────────────────────┤
│   Enterprise Business Rules (Entities) │
└─────────────────────────────────────────┘
```

## 实现方式

### 1. 实体层

```python
# entities/user.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]
    name: str
    email: str
    
    def is_valid(self) -> bool:
        return len(self.name) > 0 and '@' in self.email
    
    def update_email(self, new_email: str) -> 'User':
        return User(self.id, self.name, new_email)
```

### 2. 用例层

```python
# use_cases/create_user.py
from typing import Protocol
from entities.user import User

class UserRepository(Protocol):
    def save(self, user: User) -> None:
        ...
    
    def find_by_email(self, email: str) -> Optional[User]:
        ...

class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self, name: str, email: str) -> User:
        # 业务规则
        if self.user_repository.find_by_email(email):
            raise ValueError(f"User with email {email} already exists")
        
        user = User(id=None, name=name, email=email)
        if not user.is_valid():
            raise ValueError("Invalid user data")
        
        self.user_repository.save(user)
        return user
```

### 3. 接口适配器层

```python
# adapters/user_controller.py
from use_cases.create_user import CreateUserUseCase

class UserController:
    def __init__(self, create_user_use_case: CreateUserUseCase):
        self.create_user_use_case = create_user_use_case
    
    def create(self, request: dict) -> dict:
        try:
            user = self.create_user_use_case.execute(
                request['name'],
                request['email']
            )
            return {'id': user.id, 'name': user.name, 'email': user.email}
        except ValueError as e:
            return {'error': str(e)}
```

### 4. 框架层

```python
# frameworks/db/sqlalchemy_repo.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from entities.user import User

class SqlAlchemyUserRepository:
    def __init__(self, session):
        self.session = session
    
    def save(self, user: User) -> None:
        db_user = UserModel(name=user.name, email=user.email)
        self.session.add(db_user)
        self.session.commit()
        user.id = db_user.id
    
    def find_by_email(self, email: str) -> Optional[User]:
        db_user = self.session.query(UserModel).filter_by(email=email).first()
        if db_user:
            return User(id=db_user.id, name=db_user.name, email=db_user.email)
        return None
```

## 应用场景

- **大型企业应用**: 需要长期维护的业务系统
- **微服务**: 服务内部架构
- **跨平台应用**: 核心逻辑独立于 UI 框架

## 面试要点

**Q: 整洁架构与分层架构的区别？**
A: 整洁架构更强调业务逻辑的中心地位，依赖方向向内；分层架构关注职责分离，可能允许双向依赖。

**Q: 如何处理跨层数据传输？**
A: 使用 DTO（Data Transfer Object）或简单数据结构，避免直接传递实体。

## 相关概念

- [分层架构](./layered-architecture.md)
- [六边形架构](./hexagonal-architecture.md)
- [领域驱动设计](../ddd.md)
