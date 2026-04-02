# 冲突解决 (Collision Resolution)

## 概念

**冲突（Collision）** 是哈希表中不同键映射到相同位置的现象。由于哈希函数将无限输入空间映射到有限输出空间，冲突不可避免。

> **核心思想**: 设计策略在冲突发生时找到替代位置。

---

## 冲突解决方法

### 1. 链地址法（Separate Chaining）

每个槽位维护一个链表，冲突元素加入链表。

```python
class HashTableChaining:
    def __init__(self, size: int = 10):
        self.size = size
        self.table = [[] for _ in range(size)]
    
    def _hash(self, key: str) -> int:
        return hash(key) % self.size
    
    def insert(self, key: str, value: any):
        index = self._hash(key)
        # 检查是否已存在
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return
        self.table[index].append((key, value))
    
    def search(self, key: str) -> any:
        index = self._hash(key)
        for k, v in self.table[index]:
            if k == key:
                return v
        return None
    
    def delete(self, key: str):
        index = self._hash(key)
        self.table[index] = [(k, v) for k, v in self.table[index] if k != key]

# 图示：
# 索引    链表
#  0  →   None
#  1  →   ("a", 1) → ("k", 11)
#  2  →   ("b", 2)
#  ...
```

**优点**: 实现简单、表满也能插入  
**缺点**: 需要额外空间、缓存不友好

---

### 2. 开放寻址法（Open Addressing）

冲突时按某种探测序列寻找下一个空槽。

#### 线性探测

```python
def linear_probe(hash_val: int, i: int, size: int) -> int:
    """线性探测: h(k, i) = (h(k) + i) % m"""
    return (hash_val + i) % size

# 探测序列: h, h+1, h+2, h+3, ...
# 问题: 聚集现象（Primary Clustering）
```

#### 二次探测

```python
def quadratic_probe(hash_val: int, i: int, size: int) -> int:
    """二次探测: h(k, i) = (h(k) + c1*i + c2*i²) % m"""
    c1, c2 = 1, 3  # 常用常数
    return (hash_val + c1 * i + c2 * i * i) % size

# 探测序列: h, h+1, h+4, h+9, ...
# 缓解聚集问题，但仍有二次聚集
```

#### 双重哈希

```python
def double_hash(hash1: int, hash2: int, i: int, size: int) -> int:
    """双重哈希: h(k, i) = (h1(k) + i * h2(k)) % m"""
    return (hash1 + i * hash2) % size

# 第二个哈希函数必须满足:
# - 结果不为0
# - 与表大小互质
# h2(k) = R - (k % R), R为小于m的素数
```

### 完整实现

```python
class HashTableOpenAddressing:
    def __init__(self, size: int = 11):  # 素数
        self.size = size
        self.table = [None] * size
        self.deleted = object()  # 标记删除
    
    def _hash1(self, key: str) -> int:
        return hash(key) % self.size
    
    def _hash2(self, key: str) -> int:
        # 第二个哈希函数
        R = 7  # 小于size的素数
        return R - (hash(key) % R)
    
    def _probe(self, key: str, i: int) -> int:
        # 双重哈希
        h1 = self._hash1(key)
        h2 = self._hash2(key)
        return (h1 + i * h2) % self.size
    
    def insert(self, key: str, value: any):
        for i in range(self.size):
            index = self._probe(key, i)
            if self.table[index] is None or self.table[index] is self.deleted:
                self.table[index] = (key, value)
                return
            elif self.table[index][0] == key:
                self.table[index] = (key, value)  # 更新
                return
        raise Exception("哈希表已满")
    
    def search(self, key: str) -> any:
        for i in range(self.size):
            index = self._probe(key, i)
            if self.table[index] is None:
                return None  # 未找到
            if self.table[index] is not self.deleted and self.table[index][0] == key:
                return self.table[index][1]
        return None
```

---

## 方法比较

| 特性 | 链地址法 | 开放寻址法 |
|------|---------|-----------|
| 空间利用 | 需要额外指针空间 | 仅需数组 |
| 缓存性能 | 较差（链表跳跃）| 较好（连续访问）|
| 装载因子 | 可大于1 | 必须小于1（通常<0.75）|
| 删除操作 | 简单 | 复杂（需要标记）|
| 适用场景 | 频繁增删 | 查找为主、数据固定 |

---

## 面试要点

1. **聚集问题**: 线性探测的聚集更严重
2. **装载因子**: α = n/m，开放寻址建议α < 0.75
3. **再哈希**: 表满时扩容并重新哈希所有元素

---

## 相关概念

### 数据结构
- [哈希表](../data-structures/hash-table.md) - 哈希表基础
- [哈希函数](./hash-functions.md) - 冲突的根本原因

### 算法
- [字符串匹配](./string-matching.md) - 哈希在字符串匹配中的应用
- [布隆过滤器](../data-structures/bloom-filter.md) - 多重哈希的应用

### 系统实现
- [数据库索引](../databases/indexing.md) - 哈希索引的冲突处理
