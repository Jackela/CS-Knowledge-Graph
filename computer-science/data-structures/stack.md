# 栈 (Stack)

## 简介

**栈（Stack）**是一种遵循**后进先出（LIFO, Last In First Out）**原则的线性数据结构。想象一叠盘子：你只能从顶部取走盘子，也只能将新盘子放在顶部。这种简单却强大的约束使栈成为计算机科学中最基础且应用广泛的数据结构之一。

从数学角度看，栈是一个抽象数据类型（ADT, Abstract Data Type），定义了一组允许的操作接口，而不限定具体的实现方式。栈的本质在于其对访问顺序的严格限制：只有最近被添加的元素才能被访问或移除。

```
        栈顶 (Top) ← 唯一可操作端
        ┌───┐
        │ D │  ← 最后入栈，最先出栈
        ├───┤
        │ C │
        ├───┤
        │ B │
        ├───┤
        │ A │  ← 最先入栈，最后出栈
        └───┘
        栈底 (Bottom)
```

## 原理 (Principles)

### LIFO 原理的数学描述

设栈 $S$ 中的元素序列为 $(a_1, a_2, ..., a_n)$，其中 $a_n$ 为栈顶元素。

**入栈操作（Push）**：
$$S' = S \cup \{a_{n+1}\} = (a_1, a_2, ..., a_n, a_{n+1})$$

**出栈操作（Pop）**：
$$S' = S \setminus \{a_n\} = (a_1, a_2, ..., a_{n-1})$$

**约束条件**：若栈为空，则 Pop 操作产生**栈下溢（Stack Underflow）**错误。

### 核心操作详解

#### 1. Push（入栈）

将元素添加到栈顶，栈指针（Stack Pointer）上移。

```
初始状态:        Push(E) 后:
┌───┐           ┌───┐
│ D │ ← top     │ E │ ← top (SP + 1)
├───┤           ├───┤
│ C │           │ D │
├───┤           ├───┤
│ B │           │ C │
├───┤           ├───┤
│ A │           │ B │
└───┘           ├───┤
                │ A │
                └───┘
```

#### 2. Pop（出栈）

移除并返回栈顶元素，栈指针下移。

```
初始状态:        Pop() 后:
┌───┐           ┌───┐
│ D │ ← top     │ C │ ← top (SP - 1)
├───┤           ├───┤
│ C │           │ B │
├───┤           ├───┤
│ B │           │ A │
├───┤           └───┘
│ A │
└───┘
```

#### 3. Peek / Top（查看栈顶）

仅返回栈顶元素而不移除，栈状态不变。

### 栈指针（Stack Pointer）

栈指针是一个关键概念，它是一个寄存器或变量，始终指向当前栈顶元素的位置（或下一个可用位置，取决于具体实现）。

**数组实现中的栈指针**：
- 通常使用整数索引 `top` 表示栈顶位置
- 空栈时：`top = -1` 或 `top = 0`（视约定而定）
- 满栈时：`top = capacity - 1`

**链表实现中的栈指针**：
- 使用头指针 `head` 指向链表头部（栈顶）
- 每次 Push 在头部插入新节点
- 每次 Pop 从头部移除节点

### 边界情况

#### 栈溢出（Stack Overflow）

当栈的存储空间已满但仍尝试执行 Push 操作时发生。

**常见场景**：
- 递归调用过深，函数调用栈耗尽
- 固定大小的数组实现栈，未做容量检查
- 无限循环中的元素累积

**防御策略**：
- 使用动态扩容的数组实现
- 设置合理的递归深度限制
- 入栈前检查容量（`is_full()`）

#### 栈下溢（Stack Underflow）

当栈为空但仍尝试执行 Pop 或 Peek 操作时发生。

**防御策略**：
- 操作前检查栈是否为空（`is_empty()`）
- 异常处理机制捕获空栈操作

## 复杂度分析 (Complexity Analysis)

### 时间复杂度

| 操作 | 基于数组 | 基于链表 | 说明 |
|------|----------|----------|------|
| Push | $O(1)$ | $O(1)$ | 直接在栈顶添加 |
| Pop | $O(1)$ | $O(1)$ | 直接移除栈顶 |
| Peek/Top | $O(1)$ | $O(1)$ | 直接访问栈顶 |
| is_empty | $O(1)$ | $O(1)$ | 检查指针位置 |
| Size | $O(1)$ | $O(n)$ | 数组维护计数器，链表需遍历 |

**重要说明**：
- 数组实现的 Push 在需要扩容时，单次操作最坏情况为 $O(n)$，但均摊时间复杂度仍为 $O(1)$
- 所有核心操作（Push、Pop、Peek）的时间复杂度都是常数时间，这是栈的核心优势

### 空间复杂度

| 场景 | 空间复杂度 | 说明 |
|------|------------|------|
| 存储 $n$ 个元素 | $O(n)$ | 存储所有元素所需空间 |
| 辅助空间（操作本身） | $O(1)$ | 不使用额外数据结构 |

## 实现示例 (Implementation)

### 基于数组的实现

数组实现的栈具有缓存友好、访问快速的优点。现代 CPU 的缓存预取机制使得连续内存访问效率极高。

```python
class ArrayStack:
    """
    基于动态数组实现的栈
    支持自动扩容和缩容
    """
    
    def __init__(self, capacity: int = 10):
        """
        初始化栈
        Args:
            capacity: 初始容量
        """
        self._capacity = capacity
        self._data = [None] * capacity
        self._top = -1  # 栈顶指针，-1 表示空栈
        self._size = 0
    
    def push(self, item) -> None:
        """
        入栈操作
        时间复杂度: O(1) 均摊
        """
        if self._is_full():
            self._resize(2 * self._capacity)
        
        self._top += 1
        self._data[self._top] = item
        self._size += 1
    
    def pop(self):
        """
        出栈操作
        时间复杂度: O(1) 均摊
        Raises:
            IndexError: 栈为空时
        """
        if self.is_empty():
            raise IndexError("栈下溢: 无法从空栈弹出元素")
        
        item = self._data[self._top]
        self._data[self._top] = None  # 帮助垃圾回收
        self._top -= 1
        self._size -= 1
        
        # 动态缩容：当使用率低于 1/4 时，容量减半
        if 0 < self._size < self._capacity // 4 and self._capacity > 10:
            self._resize(self._capacity // 2)
        
        return item
    
    def peek(self):
        """
        查看栈顶元素（不移除）
        时间复杂度: O(1)
        Raises:
            IndexError: 栈为空时
        """
        if self.is_empty():
            raise IndexError("无法查看空栈的栈顶")
        return self._data[self._top]
    
    def is_empty(self) -> bool:
        """检查栈是否为空"""
        return self._top == -1
    
    def _is_full(self) -> bool:
        """检查栈是否已满"""
        return self._top == self._capacity - 1
    
    def size(self) -> int:
        """返回栈中元素数量"""
        return self._size
    
    def _resize(self, new_capacity: int) -> None:
        """
        调整数组容量
        时间复杂度: O(n)
        """
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity
    
    def __str__(self) -> str:
        """返回栈的字符串表示"""
        items = [str(self._data[i]) for i in range(self._size)]
        return f"栈(底→顶): {' → '.join(items)}"


# 使用示例
if __name__ == "__main__":
    stack = ArrayStack()
    
    # 入栈
    for i in range(5):
        stack.push(i)
    print(stack)  # 栈(底→顶): 0 → 1 → 2 → 3 → 4
    
    # 查看栈顶
    print(f"栈顶: {stack.peek()}")  # 栈顶: 4
    
    # 出栈
    print(f"弹出: {stack.pop()}")   # 弹出: 4
    print(f"弹出: {stack.pop()}")   # 弹出: 3
    print(stack)  # 栈(底→顶): 0 → 1 → 2
```

### 基于链表的实现

链表实现的栈无需预先分配固定空间，理论上可以无限扩展（受限于系统内存）。每个节点除了存储数据外，还需存储指向下一个节点的指针。

```python
class ListNode:
    """链表节点"""
    def __init__(self, val):
        self.val = val
        self.next = None


class LinkedListStack:
    """
    基于链表实现的栈
    使用头插法，头部作为栈顶
    """
    
    def __init__(self):
        """初始化空栈"""
        self._head = None  # 栈顶指针
        self._size = 0
    
    def push(self, item) -> None:
        """
        入栈操作（头插法）
        时间复杂度: O(1)
        """
        new_node = ListNode(item)
        new_node.next = self._head
        self._head = new_node
        self._size += 1
    
    def pop(self):
        """
        出栈操作
        时间复杂度: O(1)
        Raises:
            IndexError: 栈为空时
        """
        if self.is_empty():
            raise IndexError("栈下溢: 无法从空栈弹出元素")
        
        item = self._head.val
        self._head = self._head.next
        self._size -= 1
        return item
    
    def peek(self):
        """
        查看栈顶元素
        时间复杂度: O(1)
        Raises:
            IndexError: 栈为空时
        """
        if self.is_empty():
            raise IndexError("无法查看空栈的栈顶")
        return self._head.val
    
    def is_empty(self) -> bool:
        """检查栈是否为空"""
        return self._head is None
    
    def size(self) -> int:
        """返回栈中元素数量"""
        return self._size
    
    def __str__(self) -> str:
        """返回栈的字符串表示"""
        items = []
        current = self._head
        while current:
            items.append(str(current.val))
            current = current.next
        return f"栈(顶→底): {' → '.join(items)}"


# 使用示例
if __name__ == "__main__":
    stack = LinkedListStack()
    
    # 入栈
    for char in "ABC":
        stack.push(char)
    print(stack)  # 栈(顶→底): C → B → A
    
    # 出栈
    while not stack.is_empty():
        print(f"弹出: {stack.pop()}")  # C, B, A
```

### 两种实现的对比

| 特性 | 数组实现 | 链表实现 |
|------|----------|----------|
| 内存分配 | 预分配，可能存在浪费 | 按需分配，无浪费 |
| 缓存性能 | 好（连续内存） | 较差（离散内存） |
| 扩容成本 | $O(n)$ 但均摊 $O(1)$ | 无扩容成本 |
| 额外空间 | 无 | 每个元素需额外指针空间 |
| 实现复杂度 | 简单 | 稍复杂 |
| 适用场景 | 已知最大容量，频繁访问 | 容量不确定，频繁增删 |

## 应用场景 (Applications)

### 1. 函数调用栈（Call Stack）

这是栈最重要的应用之一。程序执行时，每次函数调用都会将返回地址、参数、局部变量压入调用栈；函数返回时则从栈中弹出这些信息。

```
调用 main():
┌─────────────┐
│   main()    │ ← 栈底
└─────────────┘

调用 funcA():
┌─────────────┐
│   funcA()   │ ← 栈顶
├─────────────┤
│   main()    │
└─────────────┘

调用 funcB():
┌─────────────┐
│   funcB()   │ ← 栈顶
├─────────────┤
│   funcA()   │
├─────────────┤
│   main()    │
└─────────────┘

funcB() 返回:
┌─────────────┐
│   funcA()   │ ← 栈顶
├─────────────┤
│   main()    │
└─────────────┘
```

**栈溢出示例**（递归过深）：
```python
def infinite_recursion(n):
    return infinite_recursion(n + 1)

# 运行将导致 RecursionError: maximum recursion depth exceeded
```

### 2. 表达式求值

栈是解析和计算数学表达式的核心工具。

**中缀表达式转后缀表达式（逆波兰表达式）**：
```
中缀: 3 + 4 * 2 / (1 - 5) ^ 2 ^ 3
后缀: 3 4 2 * 1 5 - 2 3 ^ ^ / +
```

**后缀表达式求值**：
```python
def evaluate_rpn(tokens):
    """
    计算逆波兰表达式（后缀表达式）
    示例: ["2", "1", "+", "3", "*"] → (2+1)*3 = 9
    """
    stack = []
    operators = {'+', '-', '*', '/'}
    
    for token in tokens:
        if token not in operators:
            stack.append(int(token))
        else:
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                stack.append(int(a / b))
    
    return stack[0]
```

### 3. 括号匹配

编译器使用栈来检查代码中的括号是否平衡。

```python
def is_valid_parentheses(s: str) -> bool:
    """
    检查括号字符串是否有效
    示例: "{[()]}" → True, "{[(])}" → False
    """
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in pairs.values():  # 左括号
            stack.append(char)
        elif char in pairs:  # 右括号
            if not stack or stack.pop() != pairs[char]:
                return False
    
    return len(stack) == 0
```

### 4. 浏览器前进/后退

浏览器使用两个栈来实现页面的前进和后退功能：
- **后退栈**：存储已访问的页面
- **前进栈**：存储已后退的页面

```
访问 A → B → C:
后退栈: [A, B, C]  前进栈: []

点击后退:
后退栈: [A, B]     前进栈: [C]

点击后退:
后退栈: [A]        前进栈: [C, B]

点击前进:
后退栈: [A, B]     前进栈: [C]

访问新页面 D:
后退栈: [A, B, D]  前进栈: []  (清空前进栈)
```

### 5. 撤销操作（Undo）

编辑器中的撤销功能通常使用栈实现，每次操作被记录在栈中，撤销时弹出最近的操作。

### 6. 回溯算法

深度优先搜索（DFS）、迷宫求解、八皇后问题等都使用栈来保存路径状态。

```python
def dfs_stack(graph, start):
    """使用栈实现深度优先搜索"""
    visited = set()
    stack = [start]
    
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            print(node)  # 处理节点
            # 将邻接节点压栈
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)
```

### 7. 内存管理

操作系统使用栈来管理局部变量和函数调用的上下文。与堆（Heap）不同，栈的内存分配和释放是自动且高效的。

## 面试要点 (Interview Questions)

### 1. 如何用栈实现队列？

**问题**：给定两个栈，实现队列的 enqueue 和 dequeue 操作。

**解答**：
使用两个栈 `input_stack` 和 `output_stack`：
- **入队**：直接将元素压入 `input_stack`，时间复杂度 $O(1)$
- **出队**：如果 `output_stack` 为空，将 `input_stack` 所有元素倒入 `output_stack`，然后从 `output_stack` 弹出，时间复杂度均摊 $O(1)$

```python
class QueueUsingStacks:
    def __init__(self):
        self.input_stack = []
        self.output_stack = []
    
    def enqueue(self, x):
        self.input_stack.append(x)
    
    def dequeue(self):
        if not self.output_stack:
            while self.input_stack:
                self.output_stack.append(self.input_stack.pop())
        return self.output_stack.pop()
```

**关键点**：均摊分析，元素最多移动两次（入 `input` 和入 `output`）。

---

### 2. 设计一个支持 O(1) 时间获取最小值的栈

**问题**：实现一个栈，支持 push、pop、top 操作，并能在常数时间内检索最小元素。

**解答**：使用辅助栈存储每个状态下的最小值。

```python
class MinStack:
    def __init__(self):
        self.stack = []      # 主栈
        self.min_stack = []  # 辅助栈，存储当前最小值
    
    def push(self, val: int) -> None:
        self.stack.append(val)
        # 辅助栈存储当前最小值
        min_val = val if not self.min_stack else min(val, self.min_stack[-1])
        self.min_stack.append(min_val)
    
    def pop(self) -> None:
        self.stack.pop()
        self.min_stack.pop()
    
    def top(self) -> int:
        return self.stack[-1]
    
    def get_min(self) -> int:
        return self.min_stack[-1]
```

**空间优化版本**：当新值等于当前最小值时才入辅助栈。

---

### 3. 有效括号问题

**问题**：给定一个只包含 `'('`、`')'`、`'{'`、`'}'`、`'['`、`']'` 的字符串，判断字符串是否有效。

**解答**：使用栈进行匹配，遇到左括号入栈，遇到右括号检查栈顶是否匹配。

```python
def is_valid(s: str) -> bool:
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:  # 右括号
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:  # 左括号
            stack.append(char)
    
    return not stack
```

---

### 4. 栈的逆序

**问题**：不使用额外数据结构（除了函数调用栈），将一个栈中的元素逆序。

**解答**：使用递归，利用函数调用栈作为辅助存储。

```python
def reverse_stack(stack):
    """递归逆序栈"""
    if not stack:
        return
    
    # 取出栈底元素
    bottom = get_and_remove_bottom(stack)
    
    # 递归逆序剩余元素
    reverse_stack(stack)
    
    # 将栈底元素压入（此时已在栈顶）
    stack.append(bottom)

def get_and_remove_bottom(stack):
    """移除并返回栈底元素"""
    result = stack.pop()
    if not stack:
        return result
    else:
        bottom = get_and_remove_bottom(stack)
        stack.append(result)
        return bottom
```

---

### 5. 接雨水问题（Trapping Rain Water）

**问题**：给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子下雨之后能接多少雨水。

**解答**：使用单调栈维护递减序列。

```python
def trap(height):
    """
    单调栈解法
    时间复杂度: O(n), 空间复杂度: O(n)
    """
    stack = []  # 存储索引，维护递减栈
    water = 0
    
    for i, h in enumerate(height):
        # 当前高度大于栈顶，可以形成凹槽
        while stack and height[stack[-1]] < h:
            bottom = stack.pop()
            if not stack:
                break
            # 计算水量
            left = stack[-1]
            width = i - left - 1
            bounded_height = min(height[left], h) - height[bottom]
            water += width * bounded_height
        
        stack.append(i)
    
    return water
```

**关键点**：单调栈用于找到每个位置左右两边的更高柱子。

## 相关概念 (Related Concepts)

### 数据结构
- [数组](./array.md)：栈最常见的底层实现方式
- [链表](./linked-list.md)：另一种栈实现方式，支持动态扩容
- [队列](./queue.md)：与栈相对的 FIFO 数据结构
- [双端队列（Deque）](./deque.md)：两端均可操作，可同时实现栈和队列的语义

### 算法
- [递归](../../references/recursion.md)：函数调用本质上是栈的操作
- [深度优先搜索（DFS）](../algorithms/graph-traversal.md)：使用栈实现图和树的遍历
- [回溯算法](../algorithms/backtracking.md)：利用栈保存搜索状态
- [排序](../algorithms/sorting.md)：部分排序算法使用栈辅助

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：分析栈操作的时间效率
- [空间复杂度](../../references/space-complexity.md)：评估栈的内存占用

### 系统实现
- [函数调用栈](../../references/call-stack.md)：程序执行的底层机制
- [堆与栈](../../references/heap-vs-stack.md)：内存管理的两种主要方式
- [进程](../systems/process.md)：进程内存布局中的栈区
- [内存管理](../systems/memory-management.md)：操作系统栈空间管理
## 参考资料 (References)

1. **教材**：
   - 《算法导论》（Introduction to Algorithms）- Cormen 等著，第 10.1 章
   - 《数据结构与算法分析：C 语言描述》- Mark Allen Weiss

2. **在线资源**：
   - [Stack Data Structure - GeeksforGeeks](https://www.geeksforgeeks.org/stack-data-structure/)
   - [Stack (abstract data type) - Wikipedia](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))

3. **经典题目**：
   - LeetCode 20: Valid Parentheses
   - LeetCode 155: Min Stack
   - LeetCode 42: Trapping Rain Water
   - LeetCode 232: Implement Queue using Stacks

4. **扩展阅读**：
   - 单调栈（Monotonic Stack）及其应用
   - 栈虚拟机（Stack-based VM）设计原理
   - 尾递归优化与栈帧复用
- [抽象数据类型](../../references/adt.md) - 栈的 ADT 定义
