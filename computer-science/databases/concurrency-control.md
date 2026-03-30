# 并发控制 (Concurrency Control)

## 简介

**并发控制 (Concurrency Control)** 是数据库管理系统的核心机制，用于管理多个事务同时访问数据库时的交互行为，确保数据的一致性、隔离性和完整性。

```
┌─────────────────────────────────────────────────────────────┐
│                   并发控制的核心目标                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│   │ 一致性   │  │ 隔离性   │  │ 性能优化 │                 │
│   │Consistency│  │ Isolation│  │ Performance│               │
│   └──────────┘  └──────────┘  └──────────┘                 │
│                                                             │
│   • 防止丢失更新    • 防止脏读      • 提高吞吐量            │
│   • 防止不可重复读  • 防止幻读      • 减少等待时间          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 并发问题

### 1. 丢失更新 (Lost Update)

```
时间线：

T1: 读取账户余额 = 100
T2: 读取账户余额 = 100
T1: 余额 = 100 + 50 = 150
T2: 余额 = 100 + 30 = 130
T1: 写入 150
T2: 写入 130  ← T1的更新丢失！

最终结果：130（期望180）
```

### 2. 脏读 (Dirty Read)

```
时间线：

T1: 更新余额 = 150
T2: 读取余额 = 150  ← 读取了未提交的数据
T1: 回滚，余额恢复为100
T2: 基于150进行计算（错误！）
```

### 3. 不可重复读 (Non-repeatable Read)

```
时间线：

T1: 读取余额 = 100
T2: 更新余额 = 150 并提交
T1: 再次读取余额 = 150  ← 同一事务内数据不一致！
```

### 4. 幻读 (Phantom Read)

```
时间线：

T1: SELECT * FROM orders WHERE amount > 100
    结果：2条记录
T2: INSERT INTO orders VALUES (...amount=150...) 并提交
T1: 再次查询 amount > 100
    结果：3条记录  ← 出现了"幻影"记录！
```

## 隔离级别

SQL标准定义了四个隔离级别，每个级别解决不同的问题：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 实现机制 |
|----------|------|------------|------|----------|
| READ UNCOMMITTED | ✗ | ✗ | ✗ | 无锁 |
| READ COMMITTED | ✓ | ✗ | ✗ | 行锁 |
| REPEATABLE READ | ✓ | ✓ | ✗ | MVCC/间隙锁 |
| SERIALIZABLE | ✓ | ✓ | ✓ | 串行化 |

```
隔离级别与一致性强度：

READ UNCOMMITTED ─────────────────────────────────────►
READ COMMITTED   ───────────────────────────►
REPEATABLE READ  ──────────────────►
SERIALIZABLE     ─────────►

一致性增强 ◄───────────────────────────────────────────
并发性能降低 ◄─────────────────────────────────────────
```

## 并发控制技术

### 1. 锁机制 (Locking)

#### 锁的类型

```
┌─────────────────────────────────────────────────────────────┐
│                      锁的分类体系                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  按粒度分：                                                 │
│  ├─ 行级锁 (Row Lock)    - 最细粒度，并发最高               │
│  ├─ 页级锁 (Page Lock)   - 中等粒度                        │
│  ├─ 表级锁 (Table Lock)  - 粗粒度，开销小                   │
│  └─ 意向锁 (Intent Lock) - 表示意图获取更细粒度锁           │
│                                                             │
│  按模式分：                                                 │
│  ├─ 共享锁 (S Lock / Shared)     - 读锁，可并发             │
│  ├─ 排他锁 (X Lock / Exclusive)  - 写锁，独占               │
│  ├─ 更新锁 (U Lock / Update)     - 防止死锁的中间状态       │
│  └─ 意向锁 (IS/IX/SIX)           - 表级意向锁               │
│                                                             │
│  按行为分：                                                 │
│  ├─ 乐观锁 (Optimistic)  - 提交时检查冲突                   │
│  └─ 悲观锁 (Pessimistic) - 操作前加锁                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 锁兼容性矩阵

```
          S    X    IS   IX   SIX
        ┌────┬────┬────┬────┬────┐
    S   │ ✓  │ ✗  │ ✓  │ ✗  │ ✗  │
        ├────┼────┼────┼────┼────┤
    X   │ ✗  │ ✗  │ ✗  │ ✗  │ ✗  │
        ├────┼────┼────┼────┼────┤
    IS  │ ✓  │ ✗  │ ✓  │ ✓  │ ✓  │
        ├────┼────┼────┼────┼────┤
    IX  │ ✗  │ ✗  │ ✓  │ ✓  │ ✗  │
        ├────┼────┼────┼────┼────┤
    SIX │ ✗  │ ✗  │ ✓  │ ✗  │ ✗  │
        └────┴────┴────┴────┴────┘
        
✓ = 兼容（可并发）  ✗ = 不兼容（需等待）
```

#### 两阶段锁协议 (2PL)

```
两阶段锁协议确保可串行化：

    锁数量
      │
      │      加锁阶段              解锁阶段
      │         │                    │
      │    _____│_____          _____│_____
      │   /      │      \\        /      │      \\
      │  /       │       \\      /       │       \\
      │ /        │        \\____/        │        \\____
      │/         │                      │
      └──────────┴──────────────────────┴──────────────────► 时间
                扩展点                收缩点
      
规则：
1. 加锁阶段：只能获取锁，不能释放锁
2. 解锁阶段：只能释放锁，不能获取锁
```

#### 严格两阶段锁 (Strict 2PL)

```
改进：所有排他锁在事务提交后才释放

优势：
- 防止级联回滚
- 更容易恢复

示例：
T1: Lock-X(A) → 修改A → Unlock(A)  [在COMMIT后]
                ↓
T2: 等待T1的X锁释放
```

### 2. 多版本并发控制 (MVCC)

#### 基本原理

```
MVCC 通过保存数据的多个版本来实现并发：

┌─────────────────────────────────────────────────────────────┐
│                      MVCC 版本链                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   事务ID    数据版本    创建时间    过期时间    数据值        │
│   ─────────────────────────────────────────────────         │
│   T100      V1         T100       T200        A=100         │
│   T200      V2         T200       ∞           A=150         │
│                                                             │
│   当前活跃事务：T150, T250                                   │
│                                                             │
│   T150读取：看到V1 (T150在V1的可见范围内)                   │
│   T250读取：看到V2 (T250 > T200且V2未过期)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 可见性规则

```python
# MVCC 可见性判断逻辑
def is_visible(transaction_id, version):
    """
    判断事务是否能看见某个数据版本
    """
    # 版本由创建该版本的事务在提交时产生
    creator_id = version.created_by
    
    # 规则1：版本创建者是自己的事务，可见
    if creator_id == transaction_id:
        return True
    
    # 规则2：创建版本的事务未提交，不可见
    if not is_committed(creator_id):
        return False
    
    # 规则3：创建版本的事务在快照创建后提交，不可见
    if creator_id > snapshot.transaction_ids:
        return False
    
    # 规则4：版本已过期（被删除或更新），不可见
    if version.expired and version.expired_by <= transaction_id:
        return False
    
    return True
```

#### PostgreSQL MVCC 实现

```sql
-- PostgreSQL 在每一行存储事务信息
-- 隐藏的系统列：
-- xmin: 插入该行的事务ID
-- xmax: 删除该行的事务ID (0表示未删除)
-- cmin/cmax: 命令ID

-- 查询示例
SELECT xmin, xmax, * FROM accounts WHERE id = 1;

-- 结果：
-- xmin  │ xmax │ id │ balance
-- ──────┼──────┼────┼─────────
-- 100   │ 0    │ 1  │ 1000
```

#### MySQL InnoDB MVCC 实现

```sql
-- InnoDB 使用 undo log 构建版本链
-- 每行包含：
-- DB_TRX_ID: 最后修改的事务ID
-- DB_ROLL_PTR: 指向undo log的指针

-- 一致性非锁定读 (Consistent Non-locking Read)
START TRANSACTION;
SELECT * FROM accounts WHERE id = 1;  -- 读取快照版本
-- 其他事务修改并提交
SELECT * FROM accounts WHERE id = 1;  -- 仍读取快照版本（可重复读）
COMMIT;

-- 当前读 (Current Read) - 读取最新版本
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
SELECT * FROM accounts WHERE id = 1 LOCK IN SHARE MODE;
```

### 3. 乐观并发控制 (OCC)

```
乐观并发控制流程：

阶段1：读取阶段
┌─────────┐     ┌─────────┐
│ 事务T1  │────▶│ 读取数据 │
│         │     │ 到私有区 │
└─────────┘     └─────────┘

阶段2：验证阶段
┌─────────┐     ┌─────────────────┐
│ 事务T1  │────▶│ 检查数据是否     │
│         │     │ 被其他事务修改   │
└─────────┘     └─────────────────┘
                    │
            ┌───────┴───────┐
           通过              失败
            │                │
            ▼                ▼
      ┌─────────┐      ┌─────────┐
      │ 提交阶段 │      │ 回滚重试 │
      └─────────┘      └─────────┘

阶段3：提交阶段
┌─────────┐     ┌─────────┐
│ 事务T1  │────▶│ 写入数据 │
│         │     │ 到数据库 │
└─────────┘     └─────────┘
```

#### 乐观锁实现

```sql
-- 使用版本号实现乐观锁
CREATE TABLE accounts (
    id INT PRIMARY KEY,
    balance DECIMAL(10, 2),
    version INT DEFAULT 0  -- 版本号
);

-- 读取时获取版本号
SELECT id, balance, version FROM accounts WHERE id = 1;
-- 结果：id=1, balance=1000, version=5

-- 更新时检查版本号
UPDATE accounts 
SET balance = balance - 100, version = version + 1
WHERE id = 1 AND version = 5;

-- 如果返回0行，说明数据已被修改，需要重试
```

```java
// Java 乐观锁示例
@Version
private Long version;

@Transactional
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    Account from = accountRepository.findById(fromId).orElseThrow();
    Account to = accountRepository.findById(toId).orElseThrow();
    
    from.debit(amount);
    to.credit(amount);
    
    // 保存时会自动检查版本号
    accountRepository.save(from);
    accountRepository.save(to);
    // OptimisticLockException 会在版本冲突时抛出
}
```

## 死锁处理

### 死锁的产生

```
死锁示例：

T1: Lock(A) ─────────────▶ Wait(B) ──▶ Deadlock!
              ↘                    ↗
T2: Lock(B) ─────────────▶ Wait(A) ──┘

T1拥有A等待B，T2拥有B等待A
```

### 死锁检测与预防

#### 等待图检测

```
等待图 (Wait-for Graph)：

    T1 ───▶ T2  (T1等待T2)
    ▲       │
    │       ▼
    T4 ◀─── T3
    
如果图中存在环，则发生死锁。
```

#### 死锁预防策略

| 策略 | 描述 | 适用场景 |
|------|------|----------|
| 一次性封锁 | 事务开始时获取所有需要的锁 | 锁范围可预知 |
| 顺序封锁法 | 按固定顺序获取锁 | 资源有明确顺序 |
| 超时机制 | 超过等待时间自动回滚 | 通用方案 |
| 等待-死亡 | 老事务等待，新事务死亡 | 优先老事务 |
| 伤害-等待 | 老事务伤害新事务，新事务等待 | 优先老事务 |

```sql
-- MySQL 死锁检测配置
SHOW VARIABLES LIKE 'innodb_deadlock_detect';
SET GLOBAL innodb_deadlock_detect = ON;

-- 查看死锁日志
SHOW ENGINE INNODB STATUS;  -- 包含最近的死锁信息
```

## 数据库实现对比

### MySQL InnoDB

```sql
-- 查看当前锁
SELECT * FROM information_schema.INNODB_LOCKS;
SELECT * FROM information_schema.INNODB_LOCK_WAITS;

-- 查看事务
SELECT * FROM information_schema.INNODB_TRX;

-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 行锁示例
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;  -- 排他锁
SELECT * FROM accounts WHERE id = 1 LOCK IN SHARE MODE;  -- 共享锁
COMMIT;

-- 间隙锁 (Gap Lock)
-- 防止幻读
SELECT * FROM accounts WHERE id BETWEEN 10 AND 20 FOR UPDATE;
-- 锁定id在10-20之间的所有记录，以及间隙
```

### PostgreSQL

```sql
-- PostgreSQL 默认使用 MVCC
-- 支持 SERIALIZABLE 快照隔离

BEGIN ISOLATION LEVEL SERIALIZABLE;
-- 事务代码
COMMIT;
-- 如果检测到串行化异常，会自动回滚

-- 显式锁
LOCK TABLE accounts IN SHARE MODE;
LOCK TABLE accounts IN EXCLUSIVE MODE;

-- 行级锁
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
SELECT * FROM accounts WHERE id = 1 FOR SHARE;
SELECT * FROM accounts WHERE id = 1 FOR KEY SHARE;
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;

-- 咨询锁 (Advisory Locks) - 应用级锁
SELECT pg_advisory_lock(123);
SELECT pg_advisory_unlock(123);
```

## 最佳实践

### 1. 事务设计原则

```
┌─────────────────────────────────────────────────────────────┐
│                    事务设计最佳实践                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 保持事务简短                                            │
│     - 尽快提交或回滚                                        │
│     - 避免事务中执行长时间计算                               │
│                                                             │
│  2. 按固定顺序访问资源                                      │
│     - 所有事务按相同顺序获取锁                              │
│     - 有效避免死锁                                          │
│                                                             │
│  3. 使用合适的隔离级别                                      │
│     - 默认使用 READ COMMITTED                               │
│     - 需要时提升到 REPEATABLE READ                          │
│     - 避免不必要的 SERIALIZABLE                             │
│                                                             │
│  4. 正确处理死锁                                            │
│     - 捕获死锁异常                                          │
│     - 实现重试机制                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 锁优化建议

```sql
-- 1. 使用索引减少锁范围
-- 不好的做法：全表扫描，锁定整个表
UPDATE accounts SET status = 'inactive' WHERE created_at < '2020-01-01';

-- 好的做法：使用索引，只锁定符合条件的行
CREATE INDEX idx_created_at ON accounts(created_at);
UPDATE accounts SET status = 'inactive' WHERE created_at < '2020-01-01';

-- 2. 批量操作分批提交
-- 避免一次更新大量数据
UPDATE accounts SET status = 'processed' 
WHERE id IN (SELECT id FROM accounts WHERE status = 'pending' LIMIT 1000);

-- 3. 使用乐观锁减少锁竞争
-- 适合读多写少的场景
UPDATE accounts 
SET balance = balance - 100, version = version + 1
WHERE id = 1 AND version = :expected_version;
```

## 面试要点

### 常见问题

**Q1: 什么是MVCC？**
> MVCC（多版本并发控制）通过保存数据的多个历史版本，使得读操作不阻塞写操作，写操作不阻塞读操作。读事务读取的是快照版本，写事务创建新版本，通过可见性规则确定每个事务能看到哪个版本。

**Q2: 四种隔离级别分别解决了什么问题？**
> - READ UNCOMMITTED：无保护，可能读到脏数据
> - READ COMMITTED：防止脏读，每次查询看到已提交的数据
> - REPEATABLE READ：防止不可重复读，同一事务内多次查询结果一致
> - SERIALIZABLE：防止幻读，完全串行化执行

**Q3: 乐观锁和悲观锁的区别？**
> 悲观锁假设冲突会发生，先加锁再操作；乐观锁假设冲突很少，先操作再检查冲突。悲观锁适合写多读少，乐观锁适合读多写少。

**Q4: 如何避免死锁？**
> 1. 按固定顺序获取锁
> 2. 尽量缩短事务时间
> 3. 使用超时机制
> 4. 减少锁的粒度
> 5. 使用一次性封锁

## 相关概念

- [事务与ACID](./transaction-acid.md) - 数据库事务的基本特性
- [索引](./indexing.md) - 数据库索引对并发的影响
- [SQL基础](./sql-basics.md) - SQL事务控制语句
- [关系模型](./relational-model.md) - 关系数据库理论基础

## 参考资料

1. Bernstein, P.A. et al. "Concurrency Control and Recovery in Database Systems"
2. "Transaction Processing: Concepts and Techniques" by Jim Gray
3. PostgreSQL Documentation: Concurrency Control
4. MySQL Documentation: InnoDB Locking and Transaction Model
5. Wikipedia: [Concurrency control](https://en.wikipedia.org/wiki/Concurrency_control)
