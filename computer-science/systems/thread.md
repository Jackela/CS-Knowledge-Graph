# 线程 (Thread)

## 简介

**线程（Thread）**是进程内的独立执行流，是CPU调度的基本单位。同一进程内的线程共享进程的地址空间和资源，但拥有独立的程序计数器、寄存器和栈。

```
进程内的线程:
┌─────────────────────────────────────────┐
│              进程地址空间                 │
│  ┌─────────────────────────────────┐   │
│  │ 线程1: 代码、数据、堆 (共享)      │   │
│  │       PC、寄存器、栈 (私有)       │   │
│  ├─────────────────────────────────┤   │
│  │ 线程2: PC、寄存器、栈 (私有)      │   │
│  │       代码、数据、堆 (共享)       │   │
│  ├─────────────────────────────────┤   │
│  │ 线程3: PC、寄存器、栈 (私有)      │   │
│  │       代码、数据、堆 (共享)       │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 线程模型

### 用户级线程 vs 内核级线程

| 特性 | 用户级线程 | 内核级线程 |
|------|-----------|-----------|
| 管理 | 用户空间库 | 操作系统内核 |
| 切换开销 | 小（无需内核） | 大（需要内核） |
| 阻塞影响 | 整个进程阻塞 | 仅该线程阻塞 |
| 多核利用 | 否 | 是 |
| 例子 | Green threads | Native threads |

### 多线程模型

```
多对一模型:              一对一模型:

进程                     进程
 ├─ 用户线程1            ├─ 线程1 ←──→ 内核线程1
 ├─ 用户线程2   → 映射    ├─ 线程2 ←──→ 内核线程2
 └─ 用户线程3            └─ 线程3 ←──→ 内核线程3
       ↓
    内核线程

多对多模型:
进程
 ├─ 用户线程1 ──┐
 ├─ 用户线程2 ──┼──→ 多个内核线程
 └─ 用户线程3 ──┘
```

## POSIX线程 (pthreads)

### 基本操作

```c
#include <pthread.h>

// 创建线程
pthread_t thread;
int rc = pthread_create(&thread, NULL, thread_function, arg);

// 线程函数
void* thread_function(void* arg) {
    // 线程执行的代码
    pthread_exit(NULL);
}

// 等待线程结束
pthread_join(thread, NULL);

// 分离线程
pthread_detach(thread);
```

### 线程同步

```c
// 互斥锁
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

pthread_mutex_lock(&mutex);
// 临界区
pthread_mutex_unlock(&mutex);

// 条件变量
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
pthread_cond_wait(&cond, &mutex);
pthread_cond_signal(&cond);
```

## 线程池

预先创建一组线程，避免频繁创建销毁的开销。

```python
from concurrent.futures import ThreadPoolExecutor

# Python线程池示例
def task(n):
    return n * n

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(task, range(10))
```

## 线程安全

### 线程安全问题

1. **竞态条件**：多个线程访问共享数据
2. **死锁**：互相等待资源
3. **活锁**：不断改变状态但无进展

### 线程安全方案

- 互斥锁
- 读写锁
- 原子操作
- Thread-local存储

## 面试要点

### Q1: 线程 vs 进程

见 [进程](../systems/process.md) 的对比表。

### Q2: 协程 vs 线程

| 特性 | 协程 | 线程 |
|------|------|------|
| 调度 | 用户态 | 内核态 |
| 切换 | 协作式 | 抢占式 |
| 内存 | 极小 | MB级 |
| 并发 | 非真正并行 | 真正并行 |

## 相关概念 (Related Concepts)

### 数据结构
- [队列](../data-structures/queue.md)：线程就绪队列的实现
- [栈](../data-structures/stack.md)：线程栈的实现

### 算法
- [调度](./scheduling.md)：线程调度算法
- [进程同步](./synchronization.md)：线程协作与同步机制

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：线程切换的时间开销
- [空间复杂度](../../references/space-complexity.md)：线程栈的内存占用

### 系统实现
- [进程](./process.md)：线程的容器与资源持有者
- [内存管理](./memory-management.md)：线程的内存访问
- [并发编程](../../references/concurrency.md)：多线程编程模型

- [进程](../systems/process.md) - 线程的容器
- [进程同步](../systems/synchronization.md) - 线程协作
- [调度](../systems/scheduling.md) - 线程调度

## 参考资料

1. 《操作系统概念》第4章 - 线程
2. Thread (computing) - Wikipedia
