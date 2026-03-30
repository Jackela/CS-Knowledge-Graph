# 递归 (Recursion)

## 简介

**递归（Recursion）**是指函数在执行过程中**调用自身**的编程技巧。递归将复杂问题分解为相似的子问题，通过解决子问题来解决原问题。它是计算机科学中最基本、最强大的思想之一。

```
递归的核心思想:

大问题 f(n) ────────┐
                    │ 分解
                    ↓
子问题 f(n-1) ──────┤
                    │ 递归
                    ↓
子问题 f(n-2) ──────┤
                    │
                    ↓
       ...          │
                    ↓
基准情况 f(0) ←─────┘
```

经典递归例子：阶乘、斐波那契数列、汉诺塔、树的遍历。

## 原理 (Principles)

### 递归的两个要素

1. **基准情况（Base Case）**：递归终止条件，防止无限递归
2. **递归情况（Recursive Case）**：将问题分解为更小的子问题

```python
def factorial(n):
    # 基准情况
    if n == 0 or n == 1:
        return 1
    
    # 递归情况
    return n * factorial(n - 1)
```

### 调用栈（Call Stack）

递归通过系统调用栈实现，每次递归调用都会压栈，返回时弹栈。

```
调用 factorial(3):

Call Stack:
|           |
| factorial(0) | ← 返回 1
| factorial(1) | ← 返回 1 * 1 = 1
| factorial(2) | ← 返回 2 * 1 = 2
| factorial(3) | ← 返回 3 * 2 = 6
|___main____|
```

### 递归的数学描述

递归函数常可用**递推关系**描述：

**阶乘**：
$$F(n) = \begin{cases} 1 & n = 0 \\ n \cdot F(n-1) & n > 0 \end{cases}$$

**斐波那契**：
$$F(n) = \begin{cases} 0 & n = 0 \\ 1 & n = 1 \\ F(n-1) + F(n-2) & n > 1 \end{cases}$$

## 递归类型

### 1. 直接递归

函数直接调用自身。

```python
def direct(n):
    if n <= 0: return
    direct(n - 1)  # 直接调用自己
```

### 2. 间接递归

函数通过其他函数间接调用自身。

```python
def A(n):
    if n <= 0: return
    B(n - 1)

def B(n):
    if n <= 0: return
    A(n - 1)  # 间接调用A
```

### 3. 尾递归（Tail Recursion）

递归调用是函数的最后一个操作。

```python
def tail_factorial(n, acc=1):
    if n == 0:
        return acc
    return tail_factorial(n - 1, n * acc)  # 尾递归
```

**优势**：可被编译器优化为迭代，避免栈溢出。

## 经典递归问题

### 1. 阶乘

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# 追踪 factorial(3):
# factorial(3) = 3 * factorial(2)
#              = 3 * (2 * factorial(1))
#              = 3 * (2 * 1)
#              = 6
```

### 2. 斐波那契数列

```python
def fibonacci(n):
    if n <= 0: return 0
    if n == 1: return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
```

**时间复杂度**：$O(2^n)$ — 大量重复计算

**优化 - 记忆化**：

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
# 时间复杂度: O(n)
```

### 3. 汉诺塔

```python
def hanoi(n, source, target, auxiliary):
    """
    将n个盘子从source移动到target
    auxiliary为辅助柱子
    """
    if n == 1:
        print(f"将盘子 1 从 {source} 移到 {target}")
        return
    
    # 1. 将n-1个盘子从source移到auxiliary
    hanoi(n - 1, source, auxiliary, target)
    
    # 2. 将第n个盘子从source移到target
    print(f"将盘子 {n} 从 {source} 移到 {target}")
    
    # 3. 将n-1个盘子从auxiliary移到target
    hanoi(n - 1, auxiliary, target, source)

# 移动次数: 2^n - 1
```

### 4. 树的遍历

```python
def preorder(root):
    if not root:
        return
    print(root.val)      # 访问根
    preorder(root.left)  # 遍历左子树
    preorder(root.right) # 遍历右子树
```

## 递归转迭代

### 为什么转换？

- 避免栈溢出（Stack Overflow）
- 提高性能（减少函数调用开销）

### 转换方法

**使用显式栈**：

```python
def preorder_iterative(root):
    if not root:
        return
    
    stack = [root]
    while stack:
        node = stack.pop()
        print(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
```

**尾递归优化**：

```python
# 尾递归形式
def tail_sum(n, acc=0):
    if n == 0:
        return acc
    return tail_sum(n - 1, acc + n)

# 优化为迭代
def sum_iterative(n):
    acc = 0
    while n > 0:
        acc += n
        n -= 1
    return acc
```

## 复杂度分析

| 问题 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 阶乘 | $O(n)$ | $O(n)$ 栈空间 |
| 斐波那契(朴素) | $O(2^n)$ | $O(n)$ |
| 斐波那契(记忆化) | $O(n)$ | $O(n)$ |
| 汉诺塔 | $O(2^n)$ | $O(n)$ |
| 二叉树遍历 | $O(n)$ | $O(h)$ |

## 应用场景

1. **树的遍历**：天然递归结构
2. **图的DFS**：深度优先搜索
3. **分治算法**：归并排序、快速排序
4. **回溯算法**：八皇后、全排列
5. **动态规划**：记忆化搜索

## 常见错误

### 1. 缺少基准情况

```python
def bad_recursion(n):
    return bad_recursion(n - 1)  # 无限递归！
```

### 2. 递归不收敛

```python
def infinite(n):
    if n == 0:
        return 0
    return infinite(n)  # n 不变，永不终止
```

### 3. 栈溢出

```python
# Python默认递归深度限制约1000
def deep(n):
    if n == 0:
        return 0
    return 1 + deep(n - 1)

deep(10000)  # RecursionError!
```

**解决**：增加递归限制或改用迭代

```python
import sys
sys.setrecursionlimit(10000)
```

## 面试要点

### Q1: 什么时候用递归？

- 问题可分解为相似的子问题
- 数据结构是递归的（树、图）
- 需要回溯搜索
- 代码更清晰易懂

### Q2: 递归vs迭代如何选择？

| 递归 | 迭代 |
|------|------|
| 代码简洁 | 性能更好 |
| 易实现 | 无栈溢出风险 |
| 适合树/图 | 适合线性问题 |

### Q3: 尾递归优化

尾递归可被编译器优化为迭代形式，避免栈增长。但**Python不支持尾递归优化**。

## 相关概念

- [分治](../algorithms/divide-conquer.md) - 递归的重要应用
- [动态规划](../algorithms/dynamic-programming.md) - 递归 + 记忆化
- [回溯](../algorithms/backtracking.md) - 递归搜索
- [二叉树](../data-structures/binary-tree.md) - 递归遍历

## 参考资料

1. 《算法导论》递归与分治
2. 《具体数学》递推关系
3. Recursion (computer science) - Wikipedia
