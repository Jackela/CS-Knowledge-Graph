# 事务与ACID特性

## 概念

**事务（Transaction）** 是数据库操作的基本单位，是一个不可分割的工作单元。事务中的所有操作要么全部成功，要么全部失败回滚。

> **核心思想**: 保证数据库从一个一致状态转换到另一个一致状态。

---

## ACID 特性

```
┌─────────────────────────────────────────────────────────────┐
│                    ACID 特性                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Atomicity    Consistency    Isolation    Durability      │
│   原子性        一致性          隔离性        持久性         │
│                                                             │
│   ┌─────┐     ┌─────┐       ┌─────┐      ┌─────┐         │
│   │ 全  │     │ 规  │       │ 隔  │      │ 永  │         │
│   │ 或  │     │ 则  │       │ 离  │      │ 久  │         │
│   │ 无  │     │ 遵  │       │ 执  │      │ 保  │         │
│   │     │     │ 循  │       │ 行  │      │ 存  │         │
│   └─────┘     └─────┘       └─────┘      └─────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1. 原子性（Atomicity）

事务是不可分割的最小执行单元，所有操作要么全部提交，要么全部回滚。

```sql
-- 转账事务：原子性保证
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 扣款
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;  -- 收款
    -- 任意一步失败，全部回滚
COMMIT;
```

### 2. 一致性（Consistency）

事务执行前后，数据库必须处于一致状态，满足所有约束和业务规则。

```sql
-- 一致性约束示例
CREATE TABLE accounts (
    id INT PRIMARY KEY,
    balance DECIMAL(10, 2) CHECK (balance >= 0)  -- 余额不能为负
);

-- 事务必须保持这一约束
BEGIN;
    -- 如果余额不足，事务回滚，保持一致性
    UPDATE accounts SET balance = balance - 200 WHERE id = 1;
    -- 若id=1余额只有100，CHECK约束阻止更新，事务失败
COMMIT;
```

### 3. 隔离性（Isolation）

并发事务之间相互隔离，一个事务的中间状态对其他事务不可见。

```sql
-- 会话A
BEGIN;
UPDATE accounts SET balance = 200 WHERE id = 1;
-- 未提交

-- 会话B（同时执行）
SELECT balance FROM accounts WHERE id = 1;
-- 根据隔离级别，可能看到：100（读已提交）或 被阻塞
```

### 4. 持久性（Durability）

事务一旦提交，对数据库的修改就是永久的，即使系统故障也不会丢失。

```
提交流程：
1. 写日志（WAL - Write Ahead Log）
2. 刷盘（fsync）
3. 返回成功
4. 后台异步刷数据页

故障恢复：从日志重做（REDO）
```

---

## 事务隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|----------|------|------------|------|
| READ UNCOMMITTED | ✓ | ✓ | ✓ |
| READ COMMITTED | ✗ | ✓ | ✓ |
| REPEATABLE READ | ✗ | ✗ | ✓ |
| SERIALIZABLE | ✗ | ✗ | ✗ |

---

## 事务实现机制

### 日志（WAL）

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   事务开始   │────→│   操作日志   │────→│   事务提交   │
│  BEGIN      │     │  UPDATE...  │     │  COMMIT     │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
                                        ┌─────────────┐
                                        │   刷盘确认   │
                                        └─────────────┘
```

### 并发控制

- **锁机制**: 悲观并发控制
- **MVCC**: 乐观并发控制（多版本并发控制）
- **时间戳**: 基于时间戳的排序

---

## 面试要点

### Q1: ACID如何保证？
- A: 日志+回滚
- C: 约束检查+触发器
- I: 锁/MVCC
- D: 日志刷盘

### Q2: 分布式事务？
- 2PC（两阶段提交）
- 3PC（三阶段提交）
- TCC（Try-Confirm-Cancel）
- Saga模式

### Q3: 事务与性能？
- 隔离级别越高，性能越低
- 长事务影响并发性能
- 大事务增加日志压力

---

## 相关概念

### 数据库
- [并发控制](./concurrency-control.md) - 事务隔离实现
- [索引](./indexing.md) - 加速事务查询
- [分布式事务](../distributed-systems/distributed-transactions.md) - 跨库事务

### 分布式系统
- [CAP定理](../distributed-systems/cap-theorem.md) - 一致性权衡
- [2PC/3PC](../distributed-systems/distributed-transactions.md) - 分布式事务协议

### 系统实现
- [日志](../systems/logging.md) - WAL原理
- [锁机制](../systems/synchronization.md) - 并发控制
