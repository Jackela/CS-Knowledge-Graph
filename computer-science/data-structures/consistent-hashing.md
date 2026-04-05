# 一致性哈希 (Consistent Hashing)

一致性哈希是一种特殊的哈希算法，当哈希表大小改变时，平均只需要重新映射 K/n 个键（K为键数，n为槽数），而传统哈希需要重新映射几乎所有键。

## 核心问题

传统哈希在服务器增减时导致大量缓存失效：
```
传统哈希: hash(key) % N
- N=4时，key映射到 server[hash(key)%4]
- N=5时，大部分key映射到不同服务器
```

## 一致性哈希原理

### 哈希环
```
将哈希空间 [0, 2^32-1] 组织成环形：

     2^32-1     0
         ↘   ↗
    server3 ← server1
    ↗           ↘
server2 ←───→ server4

key1 → hash(key1) = 100 → 顺时针找到最近的server1
key2 → hash(key2) = 5000 → 顺时针找到最近的server3
```

### 虚拟节点
为解决数据倾斜问题，每个物理节点映射多个虚拟节点：
```
物理节点A → virtual_A_1, virtual_A_2, ... virtual_A_150
物理节点B → virtual_B_1, virtual_B_2, ... virtual_B_150

每个虚拟节点均匀分布在环上，提高负载均衡性
```

## 操作复杂度

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| 查找节点 | O(log n) | 使用平衡树存储节点 |
| 添加节点 | O(log n) | 仅需迁移相邻区间的数据 |
| 删除节点 | O(log n) | 仅需迁移该节点的数据 |

## 应用场景

### 1. 分布式缓存
- **Memcached**: 使用一致性哈希分配键到服务器
- **Redis Cluster**: 哈希槽实现类似思想

### 2. 负载均衡
- **Nginx**: 一致性哈希负载均衡策略
- **Dubbo**: 基于一致哈希的负载均衡

### 3. 分布式存储
- **Cassandra**: 分区键使用一致性哈希
- **Amazon Dynamo**: 最早使用一致性哈希的存储系统

## 相关概念

### 分布式系统
- [缓存](../systems/cache.md) - 缓存系统的数据分布
- [负载均衡](../distributed-systems/load-balancing.md) - 请求分配策略

### 数据结构与算法
- [哈希表](./hash-table.md) - 基础哈希结构
- [哈希函数](../algorithms/hash-functions.md) - 哈希算法选择
- [布隆过滤器](./bloom-filter.md) - 另一种概率型数据结构
