# 贪心算法 (Greedy Algorithm)

贪心算法（Greedy Algorithm）是一种在每一步选择中都采取在当前状态下最好或最优（即最有利）的选择，从而希望导致结果是全局最好或最优的算法。

## 原理

### 贪心选择性质

贪心算法的核心思想是**贪心选择性质**（Greedy Choice Property）：一个全局最优解可以通过一系列局部最优选择来达到。

### 算法框架

```
function greedy(问题):
    初始化结果为空
    while 还有未处理的选择:
        选择当前最优的选项
        如果该选项可行:
            加入结果
            更新问题状态
    return 结果
```

### 关键性质

1. **贪心选择性质**：局部最优能导致全局最优
2. **最优子结构**：问题的最优解包含子问题的最优解

## 复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 贪心选择 | 取决于排序/选择 | O(1) - O(n) |
| 整体算法 | O(n log n) 通常 | O(n) |

## 实现示例

### 活动选择问题

```python
def activity_selection(activities):
    """
    活动选择问题：选择最多不重叠的活动
    activities: [(start, end), ...]
    """
    # 按结束时间排序
    activities.sort(key=lambda x: x[1])
    
    selected = [activities[0]]
    last_end = activities[0][1]
    
    for i in range(1, len(activities)):
        if activities[i][0] >= last_end:  # 开始时间 >= 上次结束
            selected.append(activities[i])
            last_end = activities[i][1]
    
    return selected

# 示例
activities = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 8), (5, 9), (6, 10), (8, 11)]
result = activity_selection(activities)
print(f"选中活动: {result}")  # [(1, 4), (5, 7), (8, 11)]
```

### 分数背包问题

```python
def fractional_knapsack(items, capacity):
    """
    分数背包问题
    items: [(weight, value), ...]
    """
    # 计算单位重量价值并排序
    n = len(items)
    ratio = [(items[i][1] / items[i][0], items[i][0], items[i][1]) 
             for i in range(n)]
    ratio.sort(reverse=True)  # 按单位价值降序
    
    total_value = 0
    for r, weight, value in ratio:
        if capacity >= weight:
            # 全部装入
            total_value += value
            capacity -= weight
        else:
            # 装入部分
            total_value += r * capacity
            break
    
    return total_value

# 示例
items = [(10, 60), (20, 100), (30, 120)]  # (weight, value)
capacity = 50
print(f"最大价值: {fractional_knapsack(items, capacity)}")  # 240
```

### Huffman编码

```python
import heapq
from collections import defaultdict

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

def huffman_encoding(text):
    """构建Huffman树并生成编码"""
    # 统计频率
    freq = defaultdict(int)
    for char in text:
        freq[char] += 1
    
    # 构建最小堆
    heap = [HuffmanNode(char, f) for char, f in freq.items()]
    heapq.heapify(heap)
    
    # 构建Huffman树
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        
        heapq.heappush(heap, merged)
    
    # 生成编码
    root = heap[0]
    codes = {}
    
    def generate_codes(node, code=""):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = code
            return
        generate_codes(node.left, code + "0")
        generate_codes(node.right, code + "1")
    
    generate_codes(root)
    return codes

# 示例
text = "hello world"
codes = huffman_encoding(text)
print("Huffman编码:")
for char, code in sorted(codes.items()):
    print(f"  '{char}': {code}")
```

## 应用场景

| 应用场景 | 说明 |
|----------|------|
| **最小生成树** | Kruskal、Prim算法 |
| **最短路径** | Dijkstra算法 |
| **Huffman编码** | 数据压缩 |
| **活动选择** | 区间调度问题 |
| **分数背包** | 资源分配问题 |
| **任务调度** | 贪心调度策略 |

## 面试要点

**Q1: 贪心算法和动态规划的区别？**
> - 贪心：局部最优，不回溯，每一步都选择当前最优
> - DP：全局最优，考虑所有子问题，可能回溯
> - 贪心更快但不一定最优，DP较慢但保证最优

**Q2: 如何证明贪心算法的正确性？**
> 1. 贪心选择性质：证明存在最优解包含贪心选择
> 2. 最优子结构：证明贪心选择后，子问题仍有最优解
> 3. 数学归纳法：证明贪心选择 + 子问题最优 = 全局最优

**Q3: 贪心算法什么时候会失败？**
> - 当局部最优不能导致全局最优时
> - 典型例子：0-1背包问题（贪心不能得到最优解）
> - 需要全局考虑的NP难问题

**Q4: Dijkstra算法是贪心吗？为什么？**
> 是的。每次选择距离源点最近的未访问顶点，这是贪心选择。
> 之所以能工作，是因为边的权重非负，贪心选择不会错过更短路径。

**Q5: 活动选择问题为什么贪心有效？**
> 选择最早结束的活动，为后续留下最多时间。
> 证明：设最优解的第一个活动为a，如果a不是最早结束的，
> 可以用最早结束的活动替换a，解仍然可行且不减少活动数量。

## 相关概念

- [动态规划](./dynamic-programming.md) - 另一种优化方法
- [最短路径](./shortest-path.md) - Dijkstra贪心算法
- [最小生成树](../data-structures/mst.md) - Kruskal、Prim算法
- [活动选择](./activity-selection.md) - 经典贪心问题

## 参考资料

- 《算法导论》第16章 - 贪心算法
- [Greedy Algorithms - GeeksforGeeks](https://www.geeksforgeeks.org/greedy-algorithms/)
- [Huffman Coding - Wikipedia](https://en.wikipedia.org/wiki/Huffman_coding)
