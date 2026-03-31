# 抽象数据类型 (Abstract Data Type, ADT)

**抽象数据类型 (ADT)** 是计算机科学中描述数据结构的数学模型，定义了数据的逻辑行为和操作，而不涉及具体实现细节。

## 核心概念

ADT 包含两个部分：

1. **数据值定义** - 数据可以取的值及其关系
2. **操作定义** - 可以在数据上执行的操作

### ADT 与具体实现的区别

| 抽象数据类型 (ADT) | 数据结构 (Data Structure) |
|-------------------|--------------------------|
| 逻辑定义 | 物理实现 |
| 关注"做什么" | 关注"怎么做" |
| 与语言无关 | 依赖具体编程语言 |
| 示例：栈、队列 | 示例：数组、链表 |

## 常见 ADT

### 线性 ADT

- **栈 (Stack)** - LIFO (后进先出)
- **队列 (Queue)** - FIFO (先进先出)
- **列表 (List)** - 有序元素集合
- **双端队列 (Deque)** - 两端都可操作的队列

### 非线性 ADT

- **集合 (Set)** - 无序唯一元素
- **映射/字典 (Map/Dictionary)** - 键值对集合
- **图 (Graph)** - 节点和边的集合
- **树 (Tree)** - 层次化节点结构

### 优先级 ADT

- **优先队列 (Priority Queue)** - 按优先级出队
- **堆 (Heap)** - 高效实现优先队列的树形结构

## ADT 操作示例

**栈 ADT 的操作：**

```
push(item)    - 将元素压入栈顶
pop()         - 移除并返回栈顶元素
peek()        - 返回栈顶元素但不移除
is_empty()    - 检查栈是否为空
size()        - 返回栈中元素数量
```

**队列 ADT 的操作：**

```
enqueue(item) - 将元素加入队尾
dequeue()     - 移除并返回队首元素
front()       - 返回队首元素但不移除
is_empty()    - 检查队列是否为空
size()        - 返回队列中元素数量
```

## ADT 的优势

1. **封装** - 隐藏实现细节，使用者只需了解接口
2. **模块化** - 可独立开发和测试
3. **可替换性** - 同一 ADT 可有多种实现（如栈可用数组或链表实现）
4. **正确性验证** - 可在抽象层面证明算法正确性

## 相关概念

- [数组](../computer-science/data-structures/array.md) - 基础数据结构
- [链表](../computer-science/data-structures/linked-list.md) - 线性数据结构
- [栈](../computer-science/data-structures/stack.md) - LIFO 结构
- [队列](../computer-science/data-structures/queue.md) - FIFO 结构
- [树](../computer-science/data-structures/tree.md) - 层次结构
- [图](../computer-science/data-structures/graph.md) - 网络结构
- [哈希表](../computer-science/data-structures/hash-table.md) - 映射结构
