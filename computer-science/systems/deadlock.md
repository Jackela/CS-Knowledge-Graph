# 死锁 (Deadlock)

## 简介

**死锁（Deadlock）**是一组进程中，每个进程都持有至少一个资源，并等待获取被组内其他进程持有的资源，导致所有进程都无法继续执行的状态。

```
死锁示例:

进程P1          进程P2
  │               │
  ▼               ▼
持有R1          持有R2
  │               │
  ▼               ▼
请求R2 ←──────→ 请求R1
  │               │
  └───────┬───────┘
          ▼
        死锁！
```

## 死锁的必要条件

四个条件**同时满足**才会发生死锁：

1. **互斥（Mutual Exclusion）**：资源非共享
2. **占有并等待（Hold and Wait）**：持有资源同时等待其他资源
3. **不可抢占（No Preemption）**：资源不能被强制释放
4. **循环等待（Circular Wait）**：进程-资源形成环

## 死锁处理策略

### 1. 死锁预防

破坏四个必要条件之一：

| 条件 | 破坏方法 | 缺点 |
|------|---------|------|
| 互斥 | 使资源可共享 | 并非所有资源都能共享 |
| 占有并等待 | 一次性申请所有资源 | 资源利用率低 |
| 不可抢占 | 允许抢占 | 某些资源不能抢占 |
| 循环等待 | 按序申请资源 | 需要全局排序 |

### 2. 死锁避免

**银行家算法**（Banker's Algorithm）：

```
安全检查算法:

1. Work = Available, Finish = [false, ..., false]
2. 寻找进程Pi，使得
   - Finish[i] == false
   - Need[i] <= Work
3. 如果找到:
   - Work = Work + Allocation[i]
   - Finish[i] = true
   - 回到步骤2
4. 如果所有Finish都是true，系统安全
```

### 3. 死锁检测与恢复

**等待图（Wait-for Graph）**：

```
资源分配图简化:

资源分配图:          等待图:
P1 → R1 → P2         P1 → P2
P2 → R2 → P1         P2 → P1

检测环即检测死锁
```

**恢复方法**：
- 进程终止：终止一个或多个死锁进程
- 资源抢占：抢占资源分配给其他进程

### 4. 死锁忽略

**鸵鸟算法**：忽略死锁，重启系统（如UNIX）。

## 银行家算法实现

```python
class BankersAlgorithm:
    def __init__(self, n, m):
        """
        n: 进程数
        m: 资源类型数
        """
        self.n = n
        self.m = m
        self.available = [0] * m
        self.maximum = [[0] * m for _ in range(n)]
        self.allocation = [[0] * m for _ in range(n)]
        self.need = [[0] * m for _ in range(n)]
    
    def is_safe(self):
        """安全性检查"""
        work = self.available[:]
        finish = [False] * self.n
        safe_sequence = []
        
        while len(safe_sequence) < self.n:
            found = False
            for i in range(self.n):
                if not finish[i] and all(self.need[i][j] <= work[j] 
                                          for j in range(self.m)):
                    # 模拟执行完毕释放资源
                    for j in range(self.m):
                        work[j] += self.allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(i)
                    found = True
            
            if not found:
                return False, []
        
        return True, safe_sequence
    
    def request_resources(self, process, request):
        """
        进程请求资源
        request: [r1, r2, ..., rm]
        """
        # 检查请求是否超过声明的最大需求
        if any(request[i] > self.need[process][i] for i in range(self.m)):
            return False, "请求超过最大需求"
        
        # 检查资源是否足够
        if any(request[i] > self.available[i] for i in range(self.m)):
            return False, "资源不足，进程等待"
        
        # 试分配
        for i in range(self.m):
            self.available[i] -= request[i]
            self.allocation[process][i] += request[i]
            self.need[process][i] -= request[i]
        
        # 安全性检查
        safe, _ = self.is_safe()
        
        if safe:
            return True, "资源分配成功"
        else:
            # 回滚
            for i in range(self.m):
                self.available[i] += request[i]
                self.allocation[process][i] -= request[i]
                self.need[process][i] += request[i]
            return False, "不安全状态，拒绝分配"
```

## 面试要点

### Q1: 死锁 vs 饥饿 vs 活锁

| 特性 | 死锁 | 饥饿 | 活锁 |
|------|------|------|------|
| 状态 | 都阻塞 | 某进程无限等待 | 都在运行但无进展 |
| 原因 | 循环等待 | 调度不公平 | 持续改变状态 |

### Q2: 哲学家就餐问题的死锁解决

1. **最多4个哲学家同时就餐**
2. **按顺序获取叉子**（奇数先左后右，偶数先右后左）
3. **同时获取两个叉子**（原子操作）
4. **超时放弃**：获取一个叉子后超时放弃

## 相关概念

### 数据结构
- [图](../data-structures/graph.md) - 等待图的表示
- [队列](../data-structures/queue.md) - 资源等待队列
- [树](../data-structures/tree.md) - 资源分配层次

### 算法
- [银行家算法](#银行家算法实现) - 死锁避免经典算法
- [图遍历](../algorithms/graph-traversal.md) - 环路检测
- [拓扑排序](../algorithms/topological-sort.md) - 依赖关系分析

### 复杂度分析
- [时间复杂度分析](../../references/time-complexity.md) - 安全序列检测复杂度
- [空间复杂度](../../references/time-complexity.md) - 资源分配矩阵存储

### 系统实现
- [进程](../systems/process.md) - 资源竞争主体
- [线程](../systems/thread.md) - 锁竞争
- [同步](../systems/synchronization.md) - 互斥与信号量
- [内存管理](../systems/memory-management.md) - 内存资源分配

- [进程同步](../systems/synchronization.md) - 死锁的前提
- [银行家算法](https://en.wikipedia.org/wiki/Banker%27s_algorithm) - 经典避免算法

## 参考资料

1. 《操作系统概念》第7章 - 死锁
2. Deadlock - Wikipedia
