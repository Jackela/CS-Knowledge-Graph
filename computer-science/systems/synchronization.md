# 进程同步 (Process Synchronization)

## 简介

**进程同步**是协调多个进程/线程对共享资源访问的机制，确保数据一致性和正确性。同步问题源于并发执行的竞态条件（Race Condition）。

## 临界区问题

### 临界区（Critical Section）

访问共享资源的代码段。

```
进程结构:
┌─────────────┐
│   进入区     │ ← 请求进入临界区
├─────────────┤
│   临界区     │ ← 访问共享资源
├─────────────┤
│   退出区     │ ← 释放临界区
├─────────────┤
│   剩余区     │ ← 其他代码
└─────────────┘
```

### 同步要求

1. **互斥（Mutual Exclusion）**：任何时刻最多一个进程在临界区
2. **前进（Progress）**：无进程在临界区时，应允许请求进程进入
3. **有限等待（Bounded Waiting）**：进程等待进入临界区的时间有限

## 同步机制

### 1. 互斥锁（Mutex Lock）

```c
pthread_mutex_t lock;
pthread_mutex_init(&lock, NULL);

pthread_mutex_lock(&lock);    // 进入区
// 临界区
pthread_mutex_unlock(&lock);  // 退出区
```

### 2. 信号量（Semaphore）

```c
#include <semaphore.h>

// 二进制信号量（互斥）
sem_t mutex;
sem_init(&mutex, 0, 1);

sem_wait(&mutex);      // P操作，等待
// 临界区
sem_post(&mutex);      // V操作，信号

// 计数信号量（资源池）
sem_t resource;
sem_init(&resource, 0, N);  // N个资源
```

### 3. 管程（Monitor）

高级同步构造，封装共享变量和同步操作。

```java
// Java synchronized 是管程实现
public class Counter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
}
```

## 经典同步问题

### 1. 生产者-消费者问题

```python
from threading import Semaphore, Thread
import queue

buffer = queue.Queue(maxsize=10)
mutex = Semaphore(1)
empty = Semaphore(10)  # 空槽位
full = Semaphore(0)    # 满槽位

def producer():
    while True:
        item = produce()
        empty.acquire()
        mutex.acquire()
        buffer.put(item)
        mutex.release()
        full.release()

def consumer():
    while True:
        full.acquire()
        mutex.acquire()
        item = buffer.get()
        mutex.release()
        empty.release()
        consume(item)
```

### 2. 读者-写者问题

```python
import threading

mutex = threading.Semaphore(1)      # 保护read_count
write_lock = threading.Semaphore(1) # 写者互斥
read_count = 0

def reader():
    global read_count
    while True:
        mutex.acquire()
        read_count += 1
        if read_count == 1:
            write_lock.acquire()  # 第一个读者阻止写者
        mutex.release()
        
        read_data()
        
        mutex.acquire()
        read_count -= 1
        if read_count == 0:
            write_lock.release()  # 最后一个读者允许写者
        mutex.release()

def writer():
    while True:
        write_lock.acquire()
        write_data()
        write_lock.release()
```

### 3. 哲学家就餐问题

```python
import threading

forks = [threading.Semaphore(1) for _ in range(5)]

def philosopher(i):
    while True:
        think()
        
        # 预防死锁：按固定顺序获取叉子
        left, right = i, (i + 1) % 5
        if left > right:
            left, right = right, left
        
        forks[left].acquire()
        forks[right].acquire()
        
        eat()
        
        forks[right].release()
        forks[left].release()
```

## 原子操作

```c
// 测试并设置 (Test-and-Set)
int test_and_set(int *target) {
    int rv = *target;
    *target = 1;
    return rv;
}

// 比较并交换 (Compare-and-Swap)
int compare_and_swap(int *value, int expected, int new_value) {
    int temp = *value;
    if (temp == expected)
        *value = new_value;
    return temp;
}
```

## 死锁

见 [死锁](../systems/deadlock.md) 专题。

## 面试要点

### Q1: 信号量 vs 互斥锁

| 特性 | 互斥锁 | 信号量 |
|------|--------|--------|
| 取值 | 0或1 | 任意非负整数 |
| 所有权 | 有 | 无 |
| 使用 | 互斥 | 互斥+同步 |

### Q2: 如何避免死锁？

1. 互斥破坏（不可能）
2. 占有并等待破坏：一次性申请所有资源
3. 不可抢占：允许抢占
4. 循环等待：按序申请资源

## 相关概念

- [死锁](../systems/deadlock.md) - 同步的极端情况
- [线程](../systems/thread.md) - 同步对象
- [锁优化](https://en.wikipedia.org/wiki/Lock_(computer_science)) - 自旋锁、读写锁

## 参考资料

1. 《操作系统概念》第6章 - 同步工具
2. Inter-process communication - Wikipedia
