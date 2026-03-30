# 分布式事务 (Distributed Transactions)

## 简介

**分布式事务 (Distributed Transaction)** 是指跨越多个数据库或服务的事务操作，需要保证所有参与节点的数据一致性。分布式事务处理是构建可靠分布式系统的核心挑战之一。

```
┌─────────────────────────────────────────────────────────────┐
│                   分布式事务场景                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   服务A (订单服务)          服务B (库存服务)                 │
│   ┌─────────────┐          ┌─────────────┐                 │
│   │ 创建订单    │──────────▶│ 扣减库存    │                 │
│   │             │          │             │                 │
│   │ 数据库A     │          │ 数据库B     │                 │
│   └─────────────┘          └─────────────┘                 │
│          │                        │                        │
│          └────────┬───────────────┘                        │
│                   分布式事务                                │
│                   要么全成功，要么全回滚                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ACID在分布式环境中的挑战

### CAP定理约束

```
CAP定理：在分布式系统中，最多同时满足两个特性

         ┌─────────────┐
         │   一致性    │
         │Consistency  │
         └──────┬──────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌───────┐   ┌───────┐   ┌───────┐
│可用性 │   │分区容 │   │一致性 │
│AP系统 │   │错CP系 │   │CA系统 │
│       │   │统     │   │(单机) │
└───────┘   └───────┘   └───────┘

分布式事务通常选择CP（一致性+分区容错）
```

## 两阶段提交 (2PC - Two-Phase Commit)

### 基本原理

```
2PC 协调过程：

阶段1：准备阶段 (Prepare Phase)
┌──────────┐              ┌──────────┐              ┌──────────┐
│  协调者   │◀────────────▶│ 参与者A  │◀────────────▶│ 参与者B  │
│(Coordinator)│            │(Cohort)  │              │(Cohort)  │
└────┬─────┘              └──────────┘              └──────────┘
     │
     │ 1. CanCommit?
     ├─────────────────────▶
     ├────────────────────────────────────────────────▶
     │
     │ 2. Yes/No (Vote)
     │◀─────────────────────Yes
     │◀───────────────────────────────────────────────Yes
     │

阶段2：提交阶段 (Commit Phase)
     │
     │ 3. Commit / Rollback
     ├─────────────────────▶Commit
     ├────────────────────────────────────────────────▶Commit
     │
     │ 4. Ack
     │◀─────────────────────ACK
     │◀───────────────────────────────────────────────ACK
     │
     ▼
  完成
```

### 2PC状态转换

```
协调者状态：

INIT ──▶ WAIT ──▶ COMMIT/ABORT ──▶ COMPLETE
          │
          └── 超时 ──▶ ABORT

参与者状态：

INIT ──▶ READY ──▶ COMMIT/ABORT ──▶ COMPLETE
```

### 2PC优缺点

**优点：**
- 强一致性保证
- 实现相对简单
- 理论成熟

**缺点：**
- **同步阻塞**：参与者需要锁定资源等待协调者决定
- **单点故障**：协调者宕机会导致整个事务挂起
- **数据不一致风险**：协调者宕机后部分参与者可能未收到提交指令

```
2PC故障场景：

协调者宕机（参与者已投票Yes）：
┌──────────┐              ┌──────────┐
│ 协调者   │───宕机───X   │ 参与者   │
│          │              │ 持有锁   │◀── 资源被锁定
└──────────┘              │ 等待中   │    直到协调者恢复
                          └──────────┘
```

## 三阶段提交 (3PC - Three-Phase Commit)

### 改进点

3PC在2PC基础上增加了**预提交阶段**，并引入超时机制解决阻塞问题。

```
3PC 协调过程：

阶段1：CanCommit（询问阶段）
协调者 ──CanCommit?──▶ 所有参与者
协调者 ◀──Yes/No───── 所有参与者

阶段2：PreCommit（预提交阶段）
协调者 ──PreCommit──▶ 所有参与者（参与者预执行，不锁定）
协调者 ◀──ACK──────── 所有参与者

阶段3：DoCommit（提交阶段）
协调者 ──Commit─────▶ 所有参与者
协调者 ◀──ACK──────── 所有参与者

超时处理：
- 参与者在PreCommit后超时未收到DoCommit，可自动提交
- 解决2PC的阻塞问题
```

### 3PC优缺点

**优点：**
- 减少阻塞时间
- 引入超时机制
- 协调者宕机后可继续

**缺点：**
- 实现复杂度高
- 网络分区可能导致不一致
- 极端情况下仍可能不一致

## TCC模式 (Try-Confirm-Cancel)

### 概念

TCC是一种业务层面的分布式事务方案，将操作拆分为三个阶段：

```
TCC 模式：

┌─────────────────────────────────────────────────────────────┐
│                      TCC 三阶段                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Try阶段：预留资源，执行业务检查                              │
│  ┌──────────┐                                               │
│  │ 冻结库存  │  ← 不真正扣减，只是预留                       │
│  │ 校验余额  │  ← 检查是否足够                                │
│  └──────────┘                                               │
│                                                             │
│  Confirm阶段：确认执行，真正提交                              │
│  ┌──────────┐                                               │
│  │ 真正扣减  │  ← 将冻结转为实际扣减                         │
│  │ 完成扣款  │  ← 真正扣除余额                               │
│  └──────────┘                                               │
│                                                             │
│  Cancel阶段：取消执行，释放资源                               │
│  ┌──────────┐                                               │
│  │ 释放冻结  │  ← 解除库存预留                               │
│  │ 回滚余额  │  ← 返还预扣金额                               │
│  └──────────┘                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### TCC实现示例

```java
// TCC接口定义
public interface PaymentTccService {
    
    // Try阶段：预留资源
    @TwoPhaseBusinessAction(name = "paymentAction")
    boolean tryPayment(@BusinessActionContextParameter(paramName = "orderId") String orderId,
                       @BusinessActionContextParameter(paramName = "amount") BigDecimal amount);
    
    // Confirm阶段：确认执行
    boolean commitPayment(BusinessActionContext context);
    
    // Cancel阶段：取消执行
    boolean rollbackPayment(BusinessActionContext context);
}

// 实现类
@Service
public class PaymentTccServiceImpl implements PaymentTccService {
    
    @Autowired
    private AccountDao accountDao;
    
    @Autowired
    private FrozenRecordDao frozenRecordDao;
    
    @Override
    public boolean tryPayment(String orderId, BigDecimal amount) {
        // 1. 检查余额
        Account account = accountDao.selectByUserId(userId);
        if (account.getBalance().compareTo(amount) < 0) {
            throw new InsufficientBalanceException("余额不足");
        }
        
        // 2. 冻结金额
        accountDao.freezeBalance(userId, amount);
        
        // 3. 记录冻结日志
        FrozenRecord record = new FrozenRecord();
        record.setOrderId(orderId);
        record.setAmount(amount);
        record.setStatus("FROZEN");
        frozenRecordDao.insert(record);
        
        return true;
    }
    
    @Override
    public boolean commitPayment(BusinessActionContext context) {
        String orderId = context.getActionContext("orderId");
        BigDecimal amount = new BigDecimal(context.getActionContext("amount"));
        
        // 1. 扣减冻结金额
        accountDao.deductFrozen(userId, amount);
        
        // 2. 更新冻结记录状态
        frozenRecordDao.updateStatus(orderId, "CONFIRMED");
        
        return true;
    }
    
    @Override
    public boolean rollbackPayment(BusinessActionContext context) {
        String orderId = context.getActionContext("orderId");
        
        // 1. 查询冻结记录
        FrozenRecord record = frozenRecordDao.selectByOrderId(orderId);
        if (record == null || !"FROZEN".equals(record.getStatus())) {
            return true; // 已经处理或无需处理
        }
        
        // 2. 释放冻结金额
        accountDao.unfreezeBalance(userId, record.getAmount());
        
        // 3. 更新记录状态
        frozenRecordDao.updateStatus(orderId, "CANCELLED");
        
        return true;
    }
}
```

### TCC优缺点

**优点：**
- 性能较好，无全局锁
- 业务层面控制，灵活性强
- 适合互联网高并发场景

**缺点：**
- 业务侵入性强
- 实现复杂，需处理幂等性
- Confirm/Cancel需保证执行

## Saga模式

### 概念

Saga将长事务拆分为多个本地事务，每个本地事务提交后立即释放资源，通过补偿操作处理失败。

```
Saga 模式：

正向流程：
T1 ──▶ T2 ──▶ T3 ──▶ T4 ──▶ 完成
│       │       │       │
▼       ▼       ▼       ▼
成功    成功    成功    成功

失败回滚：
T1 ──▶ T2 ──▶ T3 ──X 失败
│       │       │
▼       ▼       ▼
C1 ◀── C2 ◀── C3
(补偿)  (补偿)  (补偿)
```

### Saga编排方式

#### 1. 编排式 (Choreography)

```
事件驱动，各服务自治：

订单服务        库存服务        支付服务
    │              │              │
    │ 订单创建     │              │
    ├─────────────▶│              │
    │              │              │
    │              │ 扣减库存     │
    │              ├─────────────▶│
    │              │              │
    │              │              │ 处理支付
    │              │◀─────────────┤
    │              │  (成功/失败) │
    │◀─────────────┤              │
    │  (继续/补偿) │              │
```

#### 2. 协调式 (Orchestration)

```
中央协调器控制流程：

              ┌──────────┐
              │ Saga     │
              │Orchestrator
              └────┬─────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌───────┐    ┌───────┐    ┌───────┐
│订单服务│    │库存服务│    │支付服务│
└───────┘    └───────┘    └───────┘

协调器按顺序调用服务，失败时按相反顺序调用补偿
```

### Saga实现示例

```java
// Saga编排示例
public class OrderSaga {
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private InventoryService inventoryService;
    
    @Autowired
    private PaymentService paymentService;
    
    public void execute(Order order) {
        Saga saga = Saga.start()
            .step("createOrder")
                .invoke(() -> orderService.create(order))
                .compensate(() -> orderService.cancel(order.getId()))
            .step("deductInventory")
                .invoke(() -> inventoryService.deduct(order.getItems()))
                .compensate(() -> inventoryService.restore(order.getItems()))
            .step("processPayment")
                .invoke(() -> paymentService.charge(order.getPayment()))
                .compensate(() -> paymentService.refund(order.getPayment()));
        
        try {
            saga.execute();
        } catch (SagaException e) {
            // Saga自动执行补偿
            log.error("Saga failed", e);
        }
    }
}
```

### Saga优缺点

**优点：**
- 一阶段提交，性能高
- 无全局锁，吞吐量大
- 适合长事务场景

**缺点：**
- 无隔离性，可能出现中间状态
- 补偿操作实现复杂
- 业务需支持补偿逻辑

## 分布式事务框架

### Seata

```java
// Seata AT模式（自动补偿）
@GlobalTransactional
public void purchase() {
    // 自动注册为全局事务分支
    orderService.createOrder();
    storageService.deduct();
    accountService.debit();
    // 提交或回滚由TC协调
}

// Seata TCC模式
@GlobalTransactional
public void purchaseTcc() {
    orderTccService.tryCreate();
    storageTccService.tryDeduct();
    accountTccService.tryDebit();
}
```

### RocketMQ事务消息

```java
// 事务消息实现最终一致性
@Service
public class OrderService {
    
    @Autowired
    private RocketMQTemplate rocketMQTemplate;
    
    public void createOrder(Order order) {
        // 1. 发送半消息
        TransactionSendResult result = rocketMQTemplate.sendMessageInTransaction(
            "order-topic",
            MessageBuilder.withPayload(order).build(),
            order
        );
    }
    
    // 本地事务执行
    @RocketMQTransactionListener
    class OrderTransactionListener implements RocketMQLocalTransactionListener {
        
        @Override
        public RocketMQLocalTransactionState executeLocalTransaction(Message msg, Object arg) {
            try {
                // 执行本地事务：创建订单
                orderDao.insert((Order) arg);
                return RocketMQLocalTransactionState.COMMIT;
            } catch (Exception e) {
                return RocketMQLocalTransactionState.ROLLBACK;
            }
        }
        
        @Override
        public RocketMQLocalTransactionState checkLocalTransaction(Message msg) {
            // 回查本地事务状态
            Order order = parseOrder(msg);
            if (orderDao.exist(order.getId())) {
                return RocketMQLocalTransactionState.COMMIT;
            }
            return RocketMQLocalTransactionState.ROLLBACK;
        }
    }
}
```

## 方案对比

| 特性 | 2PC | 3PC | TCC | Saga | 事务消息 |
|------|-----|-----|-----|------|----------|
| 一致性 | 强一致 | 强一致 | 最终一致 | 最终一致 | 最终一致 |
| 性能 | 低 | 低 | 高 | 高 | 高 |
| 复杂度 | 中 | 高 | 高 | 中 | 中 |
| 业务侵入 | 低 | 低 | 高 | 高 | 中 |
| 适用场景 | 传统金融 | 较少使用 | 电商支付 | 长事务 | 异步场景 |

## 最佳实践

### 选择指南

```
选择决策树：

是否需要强一致性？
    ├── 是 → 传统业务 → 2PC/3PC
    │         └── 可用性要求高？
    │               ├── 是 → 考虑3PC
    │               └── 否 → 2PC
    └── 否 → 互联网业务
              ├── 需要同步返回？
              │     ├── 是 → TCC
              │     └── 否 → Saga/事务消息
              └── 事务执行时间长？
                    ├── 是 → Saga
                    └── 否 → 事务消息
```

### 设计原则

1. **能不用分布式事务就不用**
   - 通过业务设计避免
   - 使用单服务内的事务

2. **最终一致性优先**
   - 大多数业务场景可接受
   - 性能更好，可用性更高

3. **幂等性设计**
   - 所有接口需支持幂等
   - 防止重复执行导致数据错误

4. **监控与告警**
   - 监控事务执行状态
   - 异常及时人工介入

## 面试要点

### 常见问题

**Q1: 2PC和3PC的区别？**
> 3PC增加了CanCommit预检查阶段，并引入超时机制。2PC参与者需一直锁定资源等待协调者指令；3PC在PreCommit后参与者可超时自动提交，减少阻塞。

**Q2: TCC和Saga的区别？**
> TCC是预留资源模式，Try阶段预留资源，Confirm/Cancel执行确认；Saga是直接执行本地事务，失败时执行补偿操作。TCC性能略低但隔离性好，Saga性能高但存在中间状态。

**Q3: 如何处理分布式事务的幂等性？**> 使用唯一事务ID，在数据库或缓存中记录已处理的事务。执行前检查是否已处理，已处理直接返回结果。补偿操作同样需要幂等设计。

**Q4: CAP定理对分布式事务的影响？**
> 分布式事务必须在CP和AP之间选择。强一致性方案（2PC/3PC）选择CP；最终一致性方案（TCC/Saga）在分区时选择可用性，事后达到一致。

## 相关概念

- [CAP定理](../distributed-systems/cap-theorem.md) - 分布式系统理论基础
- [一致性协议](../distributed-systems/consensus.md) - Raft/Paxos算法
- [事务与ACID](../databases/transaction-acid.md) - 单机事务特性

## 参考资料

1. "Distributed Systems: Concepts and Design" by Coulouris
2. Gray, J. & Reuter, A. "Transaction Processing: Concepts and Techniques"
3. Seata官方文档: https://seata.io
4. Wikipedia: [Distributed transaction](https://en.wikipedia.org/wiki/Distributed_transaction)
