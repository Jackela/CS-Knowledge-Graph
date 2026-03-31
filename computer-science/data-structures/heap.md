# 堆 (Heap / Priority Queue)

堆是一种基于完全二叉树的数据结构，其核心特性是堆性质 (heap property)：父节点的键值与子节点的键值保持特定的序关系。堆常作为优先队列 (priority queue) 的高效实现，能够高效地获取和删除极值元素。

---

## 原理 (Principles)

### 完全二叉树的结构基础

堆在逻辑上是一棵**完全二叉树** (complete binary tree)，在物理上通常用[数组](./array.md)实现。对于数组索引从 0 开始的堆：

- 节点 i 的左子节点：2i + 1
- 节点 i 的右子节点：2i + 2
- 节点 i 的父节点：⌊(i-1)/2⌋

这种连续存储结构消除了指针开销，利用缓存局部性提升访问效率。

### 最大堆与最小堆 (Max-Heap vs Min-Heap)

| 类型 | 堆性质 | 极值位置 |
|------|--------|----------|
| **最大堆 (Max-Heap)** | 任意节点的值 ≥ 其子节点的值 | 根节点为最大值 |
| **最小堆 (Min-Heap)** | 任意节点的值 ≤ 其子节点的值 | 根节点为最小值 |

堆性质仅约束父子关系，不约束兄弟节点间的顺序。因此，堆不保证全局有序，仅保证从根到叶子的路径上元素按序排列。

### 堆化操作 (Heapify Operations)

#### 上浮 (Sift-Up / Bubble-Up)

当在堆尾插入新元素后，可能需要将其向上调整以恢复堆性质。

```
Sift-Up(A, i):
    while i > 0 and A[Parent(i)] < A[i]:    // 最大堆情况
        swap A[i] with A[Parent(i)]
        i = Parent(i)
```

时间复杂度：O(log n)，最坏情况需从叶子上浮至根。

#### 下沉 (Sift-Down / Bubble-Down)

当移除堆顶或用新值替换堆顶后，需要将根节点向下调整。

```
Sift-Down(A, i, n):
    largest = i
    left = 2*i + 1
    right = 2*i + 2
    
    if left < n and A[left] > A[largest]:
        largest = left
    if right < n and A[right] > A[largest]:
        largest = right
    
    if largest ≠ i:
        swap A[i] with A[largest]
        Sift-Down(A, largest, n)
```

时间复杂度：O(log n)，每层只需一次比较和可能的交换。

### 建堆的两种策略

#### 策略一：逐个插入 (Insert One by One)

从一个空堆开始，依次插入 n 个元素，每次插入后执行上浮。

```
Build-Heap-Insert(A):
    heap = []
    for x in A:
        heap.append(x)
        Sift-Up(heap, heap.size - 1)
```

#### 策略二：原地堆化 (Heapify All) - Floyd 算法

将数组视为无序的完全二叉树，从最后一个非叶子节点开始，自底向上执行下沉。

```
Build-Max-Heap(A):
    n = A.length
    for i = ⌊n/2⌋ - 1 downto 0:
        Max-Heapify(A, i, n)
```

这是建堆的最优方法，其时间复杂度分析见下节。

---

## 复杂度分析 (Complexity Analysis)

### 建堆复杂度的数学证明

**定理**：使用 Floyd 建堆算法，对 n 个元素建堆的时间复杂度为 O(n)，而非 O(n log n)。

**证明**：

考虑高度为 h 的节点数量及其调整代价。

1. **堆的高度分析**：
   - 高度为 h 的节点最多有 ⌈n / 2^(h+1)⌉ 个
   - 堆的总高度 H = ⌊log₂ n⌋

2. **总时间复杂度**：
   $$
   T(n) = \sum_{h=0}^{\lfloor\log_2 n\rfloor} \left\lceil\frac{n}{2^{h+1}}\right\rceil \cdot O(h)
   $$

3. **上界估计**：
   $$
   T(n) \leq n \cdot \sum_{h=0}^{\infty} \frac{h}{2^{h+1}}
   $$

4. **利用级数求和**：
   
   已知级数 $\sum_{h=0}^{\infty} h \cdot x^h = \frac{x}{(1-x)^2}$，令 x = 1/2：
   
   $$
   \sum_{h=0}^{\infty} \frac{h}{2^{h+1}} = \frac{1/2}{(1-1/2)^2} \cdot \frac{1}{2} = 1
   $$

因此：
$$
T(n) \leq n \cdot O(1) = O(n)
$$

**直观理解**：
- 大多数节点位于堆的底层，高度小，调整代价低
- 仅有少数节点位于顶层，调整代价高但数量少
- 形成几何级数衰减，总和收敛于线性

### 操作复杂度汇总

| 操作 | 时间复杂度 | 空间复杂度 | 说明 |
|------|-----------|-----------|------|
| **建堆 (Floyd)** | O(n) | O(1) | 原地堆化，最优 |
| **建堆 (逐插)** | O(n log n) | O(1) | 逐个上浮 |
| **插入 (Insert)** | O(log n) | O(1) | 尾插 + 上浮 |
| **提取极值 (Extract)** | O(log n) | O(1) | 首尾交换 + 下沉 |
| **查看极值 (Peek)** | O(1) | O(1) | 直接访问根 |
| **堆排序 (Heap Sort)** | O(n log n) | O(1) | 原地排序 |

---

## 实现示例 (Implementation)

### Python 完整堆实现

```python
class MaxHeap:
    """
    最大堆的完整实现，支持动态增删和堆排序。
    使用数组存储，索引 0 为根节点。
    """
    
    def __init__(self):
        self.heap = []
    
    def parent(self, i: int) -> int:
        return (i - 1) // 2
    
    def left_child(self, i: int) -> int:
        return 2 * i + 1
    
    def right_child(self, i: int) -> int:
        return 2 * i + 2
    
    def size(self) -> int:
        return len(self.heap)
    
    def is_empty(self) -> bool:
        return len(self.heap) == 0
    
    def peek(self):
        """查看最大值，O(1)"""
        if self.is_empty():
            raise IndexError("Heap is empty")
        return self.heap[0]
    
    def push(self, value):
        """插入元素，O(log n)"""
        self.heap.append(value)
        self._sift_up(len(self.heap) - 1)
    
    def pop(self):
        """提取最大值，O(log n)"""
        if self.is_empty():
            raise IndexError("Heap is empty")
        
        # 交换根与最后一个元素
        self.heap[0], self.heap[-1] = self.heap[-1], self.heap[0]
        max_val = self.heap.pop()
        
        # 下沉调整
        if self.heap:
            self._sift_down(0)
        
        return max_val
    
    def _sift_up(self, i: int):
        """上浮操作，恢复堆性质"""
        parent = self.parent(i)
        while i > 0 and self.heap[parent] < self.heap[i]:
            self.heap[parent], self.heap[i] = self.heap[i], self.heap[parent]
            i = parent
            parent = self.parent(i)
    
    def _sift_down(self, i: int):
        """下沉操作，恢复堆性质"""
        largest = i
        left = self.left_child(i)
        right = self.right_child(i)
        n = len(self.heap)
        
        if left < n and self.heap[left] > self.heap[largest]:
            largest = left
        if right < n and self.heap[right] > self.heap[largest]:
            largest = right
        
        if largest != i:
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            self._sift_down(largest)
    
    def build_heap(self, arr: list):
        """Floyd 建堆算法，O(n)"""
        self.heap = arr[:]
        n = len(self.heap)
        # 从最后一个非叶子节点开始下沉
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(i)
    
    def heap_sort(self, arr: list) -> list:
        """
        堆排序：先建堆，然后反复提取最大值
        时间复杂度：O(n log n)，空间复杂度：O(1)（原地）
        """
        self.build_heap(arr)
        sorted_arr = []
        while self.heap:
            sorted_arr.append(self.pop())
        return sorted_arr[::-1]  # 最大堆输出是降序，反转得升序


# ============ 使用示例 ============

if __name__ == "__main__":
    # 基本操作演示
    heap = MaxHeap()
    
    # 插入元素
    for x in [3, 1, 4, 1, 5, 9, 2, 6]:
        heap.push(x)
    
    print(f"堆顶（最大值）: {heap.peek()}")  # 9
    print(f"堆大小: {heap.size()}")          # 8
    
    # 提取元素（降序）
    result = []
    while not heap.is_empty():
        result.append(heap.pop())
    print(f"弹出顺序: {result}")  # [9, 6, 5, 4, 3, 2, 1, 1]
    
    # 堆排序
    arr = [64, 34, 25, 12, 22, 11, 90]
    sorted_arr = heap.heap_sort(arr)
    print(f"堆排序结果: {sorted_arr}")  # [11, 12, 22, 25, 34, 64, 90]
```

### 使用 Python 内置 heapq 模块

```python
import heapq

# heapq 实现的是最小堆
min_heap = []

# 插入元素，O(log n)
heapq.heappush(min_heap, 3)
heapq.heappush(min_heap, 1)
heapq.heappush(min_heap, 4)

# 查看最小值，O(1)
min_val = min_heap[0]

# 提取最小值，O(log n)
min_val = heapq.heappop(min_heap)

# 从列表建堆，O(n)
data = [3, 1, 4, 1, 5, 9, 2, 6]
heapq.heapify(data)

# 堆排序技巧
sorted_data = [heapq.heappop(data) for _ in range(len(data))]

# 最大 k 个元素（Top-K 问题）
nums = [3, 1, 4, 1, 5, 9, 2, 6]
largest_3 = heapq.nlargest(3, nums)  # [9, 6, 5]
smallest_3 = heapq.nsmallest(3, nums)  # [1, 1, 2]

# 实现最大堆的技巧：存储负数
max_heap = []
heapq.heappush(max_heap, -10)
heapq.heappush(max_heap, -5)
max_val = -heapq.heappop(max_heap)  # 10
```

---

## 应用场景 (Applications)

### 1. 优先队列 (Priority Queue)

堆是优先队列的标准实现方式。相比基于有序数组或链表的实现：

| 实现方式 | 插入 | 提取极值 | 空间 |
|---------|------|---------|------|
| 有序数组 | O(n) | O(1) | O(n) |
| 有序链表 | O(n) | O(1) | O(n) |
| **二叉堆** | **O(log n)** | **O(log n)** | **O(n)** |
| [二叉搜索树](./binary-search-tree.md) | O(log n) | O(log n) | O(n) |

堆在插入和提取操作上达到平衡，且实现简单，常数因子小。

### 2. 堆排序 (Heap Sort)

堆排序是[排序算法](../algorithms/sorting.md)中唯一具有 O(n log n) 最坏时间复杂度且原地排序 (in-place) 的算法。

**算法步骤**：
1. 建最大堆，O(n)
2. 重复 n-1 次：
   - 将堆顶（最大值）与末尾交换
   - 堆大小减 1
   - 对新的堆顶执行下沉，O(log n)

**复杂度分析**：
- 时间：O(n log n)，最坏、平均、最好情况一致
- 空间：O(1)，原地排序
- 稳定性：不稳定（交换破坏相等元素的相对顺序）

**堆排序 vs 快速排序**：
- 快速排序平均更快（缓存友好，常数因子小）
- 堆排序保证 O(n log n) 最坏情况
- 堆排序适合内存受限或需要稳定最坏性能的场景

### 3. Top K 问题

**问题描述**：从 n 个元素中找出第 k 大（或小）的元素，或前 k 个最大（小）元素。

**解决方案**：

| 方法 | 时间复杂度 | 空间复杂度 | 适用场景 |
|------|-----------|-----------|----------|
| 排序后取前 k | O(n log n) | O(1) 或 O(n) | k 接近 n |
| **最小堆法（找前 k 大）** | **O(n log k)** | **O(k)** | **k << n，推荐** |
| 快速选择 (Quickselect) | O(n) 平均 | O(1) | 只需第 k 个，不需前 k 个 |

**最小堆法求前 k 大元素**：
```python
def top_k(nums: list, k: int) -> list:
    """使用大小为 k 的最小堆找前 k 大元素"""
    min_heap = []
    for num in nums:
        if len(min_heap) < k:
            heapq.heappush(min_heap, num)
        elif num > min_heap[0]:  # 当前元素比堆顶大
            heapq.heapreplace(min_heap, num)  # 替换堆顶
    return sorted(min_heap, reverse=True)
```

时间复杂度分析：
- 遍历 n 个元素，每个元素最多一次堆操作
- 堆大小恒为 k，每次操作 O(log k)
- 总复杂度：O(n log k)，当 k << n 时远优于 O(n log n)

### 4. 其他经典应用

- **任务调度**：操作系统优先级调度、[定时器](../systems/timer.md)管理
- **图算法**：[Dijkstra 最短路径](./dijkstra.md)、[Prim 最小生成树](./prim.md)
- **数据流处理**：中位数维护、滑动窗口极值
- **外部排序**：K 路归并的多路选择

---

## 面试要点 (Interview Questions)

### Q1: 为什么建堆的复杂度是 O(n) 而不是 O(n log n)？

**答案要点**：

大多数节点位于堆的底层。高度为 h 的节点数约为 n/2^(h+1)，调整代价为 O(h)。总代价为：

$$
T(n) = \sum_{h=0}^{\log n} \frac{n}{2^{h+1}} \cdot h = O(n)
$$

几何级数收敛，而非每层都付出 log n 代价。

---

### Q2: 如何用堆实现一个支持 O(log n) 删除任意元素的数据结构？

**答案要点**：

标准堆不支持高效删除任意位置元素，需要扩展：

1. **哈希表 + 堆**：维护元素到堆索引的映射
2. **延迟删除**：标记删除而非立即移除，堆顶被标记时再清理
3. **索引堆 (Index Heap)**：存储索引而非值，通过辅助数组追踪位置

Python 示例（延迟删除）：
```python
class LazyHeap:
    def __init__(self):
        self.heap = []
        self.deleted = set()
    
    def push(self, val, id):
        heapq.heappush(self.heap, (val, id))
    
    def pop(self):
        while self.heap:
            val, id = heapq.heappop(self.heap)
            if id not in self.deleted:
                return val
        raise IndexError("Empty")
    
    def remove(self, id):
        self.deleted.add(id)  # O(1) 标记删除
```

---

### Q3: 堆排序为什么不稳定？能否改进？

**答案要点**：

不稳定的原因：交换操作破坏相等元素的相对顺序。例如 [2a, 1, 2b]：
- 建堆后可能变为 [2b, 1, 2a]
- 排序输出 [1, 2b, 2a]，2b 和 2a 的相对顺序改变

**改进方案**：
- 存储 (值, 原始索引) 二元组，比较时先比值再比索引
- 空间代价 O(n)，时间代价不变

---

### Q4: 在已有最小堆中，如何高效地将某个元素的值减小？

**答案要点**：

减小元素的值可能破坏堆性质（该元素可能小于其父节点）。解决方案：

1. 找到该元素（需要哈希表辅助，否则 O(n) 查找）
2. 修改值
3. 对该节点执行**上浮**操作

时间复杂度：O(log n)（查找若用哈希表为 O(1)）

应用场景：[Dijkstra 算法](./dijkstra.md)中的距离更新、[Prim 算法](./prim.md)中的边松弛。

---

### Q5: 堆与二叉搜索树 (BST) 作为优先队列实现的对比？

**答案要点**：

| 特性 | 二叉堆 | [二叉搜索树](./binary-search-tree.md) |
|------|--------|--------------------------------------|
| 极值访问 | O(1) | O(log n) 或 O(h) |
| 插入 | O(log n) | O(log n) 平均 |
| 删除极值 | O(log n) | O(log n) |
| 删除任意值 | O(n) | O(log n) |
| 查找任意值 | O(n) | O(log n) |
| 空间 | O(n)，数组连续 | O(n)，指针离散 |
| 实现复杂度 | 简单 | 较复杂（需平衡） |

**选择建议**：
- 仅需优先队列语义（取极值、插入）：用堆
- 需要查找、删除任意元素：用平衡 BST（如 AVL树、红黑树）
- Python/Java 中的 `PriorityQueue` 通常基于堆；`TreeSet`/`SortedSet` 基于 BST

---

## 相关概念 (Related Concepts)

### 数据结构
- [二叉树](./binary-tree.md)：堆的逻辑结构基础
- [数组](./array.md)：堆的物理存储实现
- [完全二叉树](./complete-binary-tree.md)：堆的树形约束
- [数组](./array.md)：堆的物理存储实现
- [二叉搜索树](./binary-search-tree.md)：另一种有序数据结构

### 算法
- [排序](../algorithms/sorting.md)：堆排序算法详解
- [最短路径](../algorithms/shortest-path.md)：Dijkstra 算法中堆的应用
- [贪心算法](../algorithms/greedy.md)：堆在贪心策略中的应用
- [最短路径](../algorithms/shortest-path.md)：Dijkstra 算法中堆的应用
- [贪心算法](../algorithms/greedy.md)：堆在贪心策略中的应用

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：复杂度分析理论
- [空间复杂度](./space-complexity.md)：空间效率评估

- [内存管理](../systems/memory-management.md)：堆内存与栈内存的对比
- [优先队列](./priority-queue.md)：堆的主要抽象接口
- [定时器](../systems/timer.md)：堆在任务调度中的应用
- [内存管理](../systems/memory-management.md)：堆内存与栈内存的对比
---

## 参考资料 (References)

1. **CLRS** - *Introduction to Algorithms* (4th Ed.), Chapter 6: Heapsort
   - 建堆复杂度的严格数学证明
   - 堆性质与堆操作的完整分析

2. **Sedgewick & Wayne** - *Algorithms* (4th Ed.), Chapter 2.4: Priority Queues
   - 索引堆、多叉堆等扩展实现
   - 实际应用场景与性能测试

3. **Knuth** - *The Art of Computer Programming*, Vol. 3: Sorting and Searching
   - 堆的历史起源与变体
   - 堆排序的稳定性分析

4. **在线资源**：
   - [Visualgo - Heap](https://visualgo.net/en/heap)：交互式可视化演示
   - [Python heapq 文档](https://docs.python.org/3/library/heapq.html)：标准库实现细节
