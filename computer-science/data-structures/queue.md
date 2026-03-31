# 队列 (Queue)

## 简介

**队列（Queue）**是一种遵循**先进先出（FIFO, First In First Out）**原则的线性数据结构。与栈不同，队列在两端进行操作：一端（队尾 Rear）用于插入元素，另一端（队头 Front）用于删除元素。这种特性使其非常适合模拟现实世界中的排队场景。

```
        队头 (Front)          队尾 (Rear)
           ↓                     ↓
        ┌───┐    ┌───┐    ┌───┐    ┌───┐
出队 ←  │ A │ ←  │ B │ ←  │ C │ ←  │ D │  ← 入队
        └───┘    └───┘    └───┘    └───┘
         最先                    最后
         入队                    入队
         最先                    最后
         出队                    出队
```

从数学角度看，队列也是一个抽象数据类型（ADT），定义了在一端插入、另一端删除的操作接口。

## 原理 (Principles)

### FIFO 原理的数学描述

设队列 $Q$ 中的元素序列为 $(a_1, a_2, ..., a_n)$，其中 $a_1$ 为队头元素，$a_n$ 为队尾元素。

**入队操作（Enqueue）**：
$$Q' = Q \cup \{a_{n+1}\} = (a_1, a_2, ..., a_n, a_{n+1})$$

**出队操作（Dequeue）**：
$$Q' = Q \setminus \{a_1\} = (a_2, a_3, ..., a_n)$$

**约束条件**：若队列为空，则 Dequeue 操作产生**队列下溢（Queue Underflow）**错误。

### 核心操作详解

#### 1. Enqueue（入队）

将元素添加到队尾， rear 指针后移。

```
初始状态:        Enqueue(E) 后:
front           front
  ↓               ↓
┌───┐           ┌───┐
│ A │           │ A │
├───┤           ├───┤
│ B │           │ B │
├───┤           ├───┤
│ C │           │ C │
├───┤           ├───┤
│ D │ ← rear    │ D │
└───┘           ├───┤
                │ E │ ← rear (新增)
                └───┘
```

**时间复杂度**：$O(1)$

#### 2. Dequeue（出队）

从队头移除元素，front 指针后移。

```
初始状态:        Dequeue() 后:
front                front
  ↓                  ↓
┌───┐              ┌───┐
│ A │ ← 出队        │ B │
├───┤              ├───┤
│ B │              │ C │
├───┤              ├───┤
│ C │              │ D │
├───┤              ├───┤
│ D │ ← rear       │ D │ ← rear
└───┘              └───┘
```

**时间复杂度**：$O(1)$

#### 3. Peek/Front（查看队头）

返回队头元素但不移除。

**时间复杂度**：$O(1)$

#### 4. isEmpty（判空）

检查队列是否为空。

**时间复杂度**：$O(1)$

### 队列的数学性质

1. **顺序性**：元素保持插入顺序
2. **公平性**：先到达的元素先被处理
3. **有限性**（对于循环队列）：队列容量固定

## 实现 (Implementation)

### 1. 数组实现（Array-based）

使用固定大小的数组和两个指针（front 和 rear）。

```python
class ArrayQueue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = -1
        self.size = 0
    
    def enqueue(self, item):
        """入队操作"""
        if self.is_full():
            raise OverflowError("Queue is full")
        self.rear = (self.rear + 1) % self.capacity
        self.queue[self.rear] = item
        self.size += 1
    
    def dequeue(self):
        """出队操作"""
        if self.is_empty():
            raise IndexError("Queue is empty")
        item = self.queue[self.front]
        self.queue[self.front] = None  # 帮助垃圾回收
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return item
    
    def peek(self):
        """查看队头"""
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.queue[self.front]
    
    def is_empty(self):
        return self.size == 0
    
    def is_full(self):
        return self.size == self.capacity
```

#### 普通队列的问题：假溢出

```
出队 10 次后：
┌────┬────┬────┬────┬────┐
│null│null│null│null│null│  ← front 和 rear 都指向末尾
│    │    │    │    │    │    但数组前面有大量空闲空间！
└────┴────┴────┴────┴────┘
     ↑              ↑
   front          rear
```

### 2. 循环队列（Circular Queue）

通过取模运算实现空间的循环利用。

```
循环队列示意（capacity=5）:

初始:   [A,B,C,D,_]    enqueue(E):
        front=0        [A,B,C,D,E]
        rear=3         front=0
                       rear=4 (满)

dequeue():  dequeue() 再 enqueue(F):
[_,B,C,D,E]    →    [F,B,C,D,E]
front=1             front=1
rear=4              rear=0 (循环!)
```

```cpp
// C++ 循环队列实现
template<typename T>
class CircularQueue {
private:
    T* data;
    int front, rear;
    int capacity;
    int count;

public:
    CircularQueue(int size) : capacity(size) {
        data = new T[capacity];
        front = 0;
        rear = -1;
        count = 0;
    }
    
    void enqueue(T item) {
        if (isFull()) {
            throw std::runtime_error("Queue is full");
        }
        rear = (rear + 1) % capacity;
        data[rear] = item;
        count++;
    }
    
    T dequeue() {
        if (isEmpty()) {
            throw std::runtime_error("Queue is empty");
        }
        T item = data[front];
        front = (front + 1) % capacity;
        count--;
        return item;
    }
    
    T peek() {
        if (isEmpty()) throw std::runtime_error("Queue is empty");
        return data[front];
    }
    
    bool isEmpty() { return count == 0; }
    bool isFull() { return count == capacity; }
    int size() { return count; }
};
```

### 3. 链表实现（Linked List）

使用单向链表，头节点为 front，尾节点为 rear。

```java
// Java 链表队列实现
public class LinkedQueue<T> {
    private class Node {
        T data;
        Node next;
        Node(T data) { this.data = data; }
    }
    
    private Node front;
    private Node rear;
    private int size;
    
    public void enqueue(T item) {
        Node newNode = new Node(item);
        if (isEmpty()) {
            front = rear = newNode;
        } else {
            rear.next = newNode;
            rear = newNode;
        }
        size++;
    }
    
    public T dequeue() {
        if (isEmpty()) throw new NoSuchElementException();
        T item = front.data;
        front = front.next;
        if (front == null) rear = null;
        size--;
        return item;
    }
    
    public T peek() {
        if (isEmpty()) throw new NoSuchElementException();
        return front.data;
    }
    
    public boolean isEmpty() { return size == 0; }
}
```

## 变体 (Variants)

### 1. 双端队列（Deque - Double Ended Queue）

在两端都可以进行插入和删除操作。

```
   前端                      后端
    ↓                        ↓
┌───┬───┬───┬───┬───┬───┬───┐
│   │   │   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┘
    ↑                        ↑
  push_front              push_back
   pop_front               pop_back
```

**应用场景**：
- 滑动窗口问题
- 回文检查
- 任务调度（高优先级从一端，普通从另一端）

### 2. 优先队列（Priority Queue）

元素带有优先级，优先级高的先出队。

```
普通队列:          优先队列:
A(1) → B(2)        C(3) → B(2) → A(1)
出队: A            出队: C (优先级最高)
```

**实现方式**：
- 堆（Heap）：插入 $O(\log n)$，取出 $O(\log n)$
- 有序数组：插入 $O(n)$，取出 $O(1)$

详见 [堆](./heap.md)

### 3. 单调队列（Monotonic Queue）

维护队列内元素的单调性（递增或递减）。

```
维护递减队列，新元素 5 入队:

原队列: [9, 7, 3]    新元素: 5
        
移除所有小于 5 的元素 (只有 3):
新队列: [9, 7, 5]

队头 9 永远是最大值！
```

## 复杂度分析

| 操作 | 数组实现 | 链表实现 | 循环队列 |
|------|---------|---------|---------|
| Enqueue | $O(1)$ | $O(1)$ | $O(1)$ |
| Dequeue | $O(n)$* | $O(1)$ | $O(1)$ |
| Peek | $O(1)$ | $O(1)$ | $O(1)$ |
| isEmpty | $O(1)$ | $O(1)$ | $O(1)$ |
| 空间 | $O(n)$ | $O(n)$ | $O(n)$ |

\* 普通数组实现需要移动元素，循环队列为 $O(1)$

## 应用场景

### 1. BFS 广度优先搜索

队列是 BFS 的核心数据结构。

```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        node = queue.popleft()  # 出队
        print(node)  # 处理节点
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)  # 入队
```

### 2. 任务调度

操作系统使用队列管理进程：
- 就绪队列（Ready Queue）
- 等待队列（Waiting Queue）
- 打印队列（Print Queue）

### 3. 缓冲区与缓存

- IO 缓冲区
- 消息队列（如 RabbitMQ, Kafka）
- 网络数据包缓冲

### 4. 滑动窗口问题

```python
def max_sliding_window(nums, k):
    """滑动窗口最大值 - 使用单调队列"""
    from collections import deque
    result = []
    window = deque()  # 存储索引
    
    for i, num in enumerate(nums):
        # 移除窗口外的元素
        while window and window[0] <= i - k:
            window.popleft()
        
        # 维护单调递减
        while window and nums[window[-1]] <= num:
            window.pop()
        
        window.append(i)
        
        # 记录结果
        if i >= k - 1:
            result.append(nums[window[0]])
    
    return result
```

## 面试要点

### Q1: 如何用栈实现队列？

使用两个栈：一个用于入队，一个用于出队。

```python
class QueueUsingStacks:
    def __init__(self):
        self.stack_in = []   # 入队栈
        self.stack_out = []  # 出队栈
    
    def enqueue(self, x):
        self.stack_in.append(x)
    
    def dequeue(self):
        if not self.stack_out:
            while self.stack_in:
                self.stack_out.append(self.stack_in.pop())
        return self.stack_out.pop()
```

**均摊时间复杂度**：
- Enqueue: $O(1)$
- Dequeue: $O(1)$ 均摊

### Q2: 循环队列如何判断空和满？

1. **牺牲一个空间**：`(rear + 1) % capacity == front` 表示满
2. **使用计数器**：维护 size 变量
3. **使用标记位**：额外布尔变量

### Q3: 队列和栈的应用场景区别？

| 场景 | 数据结构 | 原因 |
|------|---------|------|
| 函数调用 | 栈 | 后调用的先返回 |
| BFS | 队列 | 按层次遍历 |
| 浏览器历史 | 栈 | 后进先出 |
| 打印机任务 | 队列 | 先来先服务 |
| 撤销操作 | 栈 | 撤销最近的操作 |
| 消息缓冲 | 队列 | 按顺序处理 |

### Q4: 线程安全的队列如何实现？

```python
import threading
from collections import deque

class ThreadSafeQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
        self.capacity = 100
    
    def put(self, item):
        with self.not_full:
            while len(self.queue) >= self.capacity:
                self.not_full.wait()
            self.queue.append(item)
            self.not_empty.notify()
    
    def get(self):
        with self.not_empty:
            while not self.queue:
                self.not_empty.wait()
            item = self.queue.popleft()
            self.not_full.notify()
            return item
```

## 相关概念 (Related Concepts)

### 数据结构
- [栈](./stack.md)：LIFO 数据结构，与队列形成对比
- [链表](./linked-list.md)：队列的底层实现方式
- [堆](./heap.md)：优先队列的实现基础
- [双端队列（Deque）](./deque.md)：两端均可操作的队列变体

### 算法
- [广度优先搜索（BFS）](../algorithms/graph-traversal.md)：使用队列实现图遍历
- [图遍历](../algorithms/graph-traversal.md)：队列在层序遍历中的应用

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：分析队列操作的时间效率
- [空间复杂度](./space-complexity.md)：评估队列的内存占用
- [空间复杂度](../../references/space-complexity.md)：评估队列的内存占用

### 系统实现
- [进程调度](../systems/scheduling.md)：队列在 OS 中的应用
- [内存管理](../systems/memory-management.md)：缓冲区与队列实现
- [线程](../systems/thread.md)：线程安全队列的实现

- [抽象数据类型](../../references/adt.md) - 队列的 ADT 定义
## 参考资料

1. 《算法导论》第10章 - 基本数据结构
2. 《数据结构（C语言版）》严蔚敏
3. Queue (abstract data type) - Wikipedia
4. Python collections.deque 文档
