# 分布式缓存 (Distributed Caching)

## 简介
分布式缓存是将热点数据存储在内存中，通过分布式部署提供高并发、低延迟的数据访问，显著提升系统性能和可扩展性。

## 核心概念
- **缓存穿透 (Cache Penetration)**: 查询不存在的数据，绕过缓存直达数据库
- **缓存击穿 (Cache Breakdown)**: 热点key过期，大量请求直达数据库
- **缓存雪崩 (Cache Avalanche)**: 大量key同时过期，数据库压力骤增
- **缓存一致性 (Cache Consistency)**: 缓存与数据库数据同步问题

## 实现方式 / 工作原理

### 一致性哈希分片

```python
import hashlib
import bisect

class ConsistentHashRing:
    """一致性哈希环 - 解决数据分布和节点伸缩"""
    
    def __init__(self, replicas=150):
        self.replicas = replicas  # 虚拟节点数
        self.ring = {}  # hash -> node
        self.sorted_keys = []
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node):
        """添加节点，创建虚拟节点"""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)
    
    def remove_node(self, node):
        """移除节点"""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)
    
    def get_node(self, key):
        """获取key对应的节点"""
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, hash_key)
        
        if idx == len(self.sorted_keys):
            idx = 0
        
        return self.ring[self.sorted_keys[idx]]
    
    def get_nodes(self, key, n=3):
        """获取key的N个副本节点"""
        nodes = set()
        hash_key = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, hash_key)
        
        while len(nodes) < n and len(nodes) < len(set(self.ring.values())):
            node = self.ring[self.sorted_keys[idx % len(self.sorted_keys)]]
            nodes.add(node)
            idx += 1
        
        return list(nodes)
```

### 缓存策略实现

```python
import threading
import time
from enum import Enum

class CacheStrategy(Enum):
    CACHE_ASIDE = "Cache-Aside"      # 旁路缓存
    READ_THROUGH = "Read-Through"    # 读穿透
    WRITE_THROUGH = "Write-Through"  # 写穿透
    WRITE_BEHIND = "Write-Behind"    # 异步写

class DistributedCache:
    """分布式缓存客户端"""
    
    def __init__(self, strategy=CacheStrategy.CACHE_ASIDE):
        self.strategy = strategy
        self.local_cache = {}  # L1本地缓存
        self.redis_client = None  # L2分布式缓存
        self.db_client = None
        self.lock = threading.RLock()
        
    def get(self, key):
        """Cache-Aside读取策略"""
        # L1: 本地缓存
        if key in self.local_cache:
            return self.local_cache[key]
        
        # L2: Redis
        value = self.redis_client.get(key)
        if value:
            self.local_cache[key] = value  # 回填L1
            return value
        
        # DB: 数据库（防击穿）
        return self.load_from_db_with_lock(key)
    
    def load_from_db_with_lock(self, key):
        """防缓存击穿：互斥锁重建"""
        lock_key = f"lock:{key}"
        
        # 尝试获取分布式锁
        if self.redis_client.set(lock_key, "1", nx=True, ex=10):
            try:
                # 双重检查
                value = self.redis_client.get(key)
                if value:
                    return value
                
                # 查DB并写入缓存
                value = self.db_client.query(key)
                if value:
                    self.redis_client.setex(key, 3600, value)
                else:
                    # 防穿透：缓存空值
                    self.redis_client.setex(key, 60, "__NULL__")
                return value
            finally:
                self.redis_client.delete(lock_key)
        else:
            # 等待后重试
            time.sleep(0.1)
            return self.get(key)
    
    def set(self, key, value):
        """写入策略"""
        if self.strategy == CacheStrategy.WRITE_THROUGH:
            # 同时写缓存和DB
            self.db_client.update(key, value)
            self.redis_client.set(key, value)
        
        elif self.strategy == CacheStrategy.WRITE_BEHIND:
            # 先写缓存，异步写DB
            self.redis_client.set(key, value)
            self.async_write_queue.put((key, value))
        
        else:  # CACHE_ASIDE
            # 先写DB，再删缓存（非更新）
            self.db_client.update(key, value)
            self.invalidate_cache(key)
```

### 多级缓存架构

```
┌─────────────────────────────────────────────────────────┐
│                      应用层                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │  L1: 本地缓存 (Caffeine/Guava)                   │   │
│  │  - 命中率最高，访问速度最快                       │   │
│  │  - 容量小，需要过期策略                          │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │  L2: 分布式缓存 (Redis Cluster)                  │   │
│  │  - 大容量，支持复杂数据结构                       │   │
│  │  - 一致性哈希分片，主从复制                      │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐   │
│  │  L3: 远程缓存 (CDN/边缘节点)                     │   │
│  │  - 地理位置就近访问                              │   │
│  │  - 静态资源缓存                                  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 应用场景
- **Web加速**: 页面片段缓存、Session存储
- **数据库减压**: 热点数据缓存，QPS提升10-100倍
- **分布式锁**: Redis实现互斥锁、信号量
- **实时排行榜**: Sorted Set实现TopN排行

## 面试要点

1. **Q: 缓存穿透、击穿、雪崩的区别及解决方案？**  
   A: 穿透：查询不存在数据，用布隆过滤器或缓存空值解决；击穿：热点key过期，用互斥锁或永不过期解决；雪崩：大量key同时过期，用随机过期时间或熔断降级解决。

2. **Q: 一致性哈希的优点是什么？**  
   A: ①单调性：添加/删除节点只影响相邻节点，其他节点映射关系不变；②平衡性：虚拟节点使数据分布均匀；③分散性：相同key总映射到相同节点。适合分布式缓存动态扩缩容场景。

3. **Q: Cache-Aside和Read-Through的区别？**  
   A: Cache-Aside由应用控制缓存逻辑，灵活但代码侵入；Read-Through由缓存层自动加载，透明但依赖缓存实现。Cache-Aside更常用，更新时用"删缓存"而非"更新缓存"避免并发问题。

4. **Q: 如何保证缓存与数据库的一致性？**  
   A: ①先更新数据库，再删缓存（延迟双删）；② Canal订阅binlog异步删缓存；③ 设置合理过期时间兜底；④ 强一致性场景用分布式锁串行化。避免先删缓存再更新数据库（可能读到旧数据）。

## 相关概念

### 数据结构
- [哈希表](../data-structures/hash-table.md)
- [布隆过滤器](../data-structures/bloom-filter.md)
- [跳表](../data-structures/skip-list.md)

### 算法
- [LRU缓存](../algorithms/lru-cache.md)
- [一致性哈希](../algorithms/consistent-hashing.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [消息队列](message-queues.md)
- [CAP定理](cap-theorem.md)
