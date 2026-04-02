# 空间复杂度 (Space Complexity)

空间复杂度衡量算法执行过程中所需的额外内存空间，是算法效率分析的重要维度，与时间复杂度共同决定算法的实际可行性。

## 核心概念

### 空间复杂度表示
使用大O记号表示，关注随着输入规模n增长的额外空间需求：
- **O(1)**：常数空间，不随n变化
- **O(log n)**：对数空间
- **O(n)**：线性空间
- **O(n²)**：平方空间（常见于二维数组）

### 空间组成

1. **指令空间**：存储程序代码
2. **数据空间**：存储变量和常量
3. **栈空间**：函数调用和递归
4. **堆空间**：动态分配的内存

## 常见模式

| 算法类型 | 空间复杂度 | 示例 |
|---------|-----------|------|
| 迭代算法 | O(1) | 简单的循环遍历 |
| 递归算法 | O(n) | 递归深度为n |
| 分治算法 | O(log n) | 归并排序的递归栈 |
| 动态规划 | O(n) ~ O(n²) | 状态表格存储 |
| 图算法 | O(V+E) | 邻接表存储 |

## 空间优化技术

### 1. 原地算法 (In-place)
- 输入数据上直接修改，O(1)额外空间
- 示例：冒泡排序、快速排序（平均）

### 2. 滚动数组
- 只保存必要的状态，降低DP空间
- 将O(n²)降至O(n)

### 3. 状态压缩
- 使用位运算压缩布尔状态
- 示例：位图、状态压缩DP

### 4. 惰性计算
- 按需计算，不预存所有结果

## 空间-时间权衡

经典权衡场景：
- **缓存**：用空间换时间
- **预计算**：存储结果避免重复计算
- **压缩**：用时间换空间

## 相关概念

### 算法
- [时间复杂度](./time-complexity.md) - 空间与时间的权衡
- [动态规划](../computer-science/algorithms/dynamic-programming.md) - 典型的高空间消耗算法
- [递归](../computer-science/algorithms/recursion.md) - 栈空间消耗

### 数据结构
- [数组](../computer-science/data-structures/array.md) - 连续内存空间
- [链表](../computer-science/data-structures/linked-list.md) - 额外指针空间
- [树](../computer-science/data-structures/tree.md) - 节点指针开销

### 系统
- [内存管理](../computer-science/systems/memory-management.md) - 内存分配策略
- [虚拟内存](../computer-science/systems/virtual-memory.md) - 空间抽象机制
- [缓存](../computer-science/systems/virtual-memory.md) - 空间换时间的极致

### AI/数据系统
- [LLM](../ai-data-systems/llm.md) - 大模型的内存占用
- [向量数据库](../ai-data-systems/vector-db.md) - 高维向量存储

## 面试要点

1. **递归的空间复杂度**：等于递归深度，注意栈溢出
2. **斐波那契数列**：
   - 递归：O(n)栈空间
   - DP：O(n)数组空间
   - 滚动优化：O(1)空间
3. **图的表示**：邻接矩阵O(V²) vs 邻接表O(V+E)
4. **大对象处理**：内存受限环境下的算法设计
