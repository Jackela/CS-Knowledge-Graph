# 数据库架构 (Database Architecture)

## 简介
数据库架构是数据库管理系统的整体组织结构，包括存储引擎、查询处理器、事务管理器等核心组件，决定了数据库的性能、可靠性和扩展性。

## 核心概念
- **存储引擎 (Storage Engine)**: 负责数据的物理存储和检索
- **缓冲池 (Buffer Pool)**: 内存中缓存数据页的池
- **预写日志 (WAL)**: 先写日志后写数据，保证持久性
- **MVCC**: 多版本并发控制，实现读写不阻塞

## 实现方式 / 工作原理

### 数据库系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    SQL Interface                        │
├─────────────────────────────────────────────────────────┤
│                  Parser & Analyzer                      │
│              (词法/语法分析 → 语义检查)                   │
├─────────────────────────────────────────────────────────┤
│                 Query Optimizer                         │
│              (逻辑优化 → 物理优化 → 代价估算)              │
├─────────────────────────────────────────────────────────┤
│                 Plan Executor                           │
│              (火山模型/向量化/代码生成)                    │
├─────────────────────────────────────────────────────────┤
│              Transaction Manager                        │
│         (ACID、并发控制、死锁检测、恢复管理)               │
├─────────────────────────────────────────────────────────┤
│              Storage Engine Layer                       │
│    ┌──────────┬──────────┬──────────┬──────────┐       │
│    │ Access   │ Buffer   │ Index    │ File     │       │
│    │ Methods  │ Manager  │ Manager  │ Manager  │       │
│    └──────────┴──────────┴──────────┴──────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 存储引擎对比

```python
class StorageEngine:
    """存储引擎基类"""
    pass

class BTreeEngine(StorageEngine):
    """B+树存储引擎 (InnoDB/MyISAM)"""
    def read_row(self, table_id, primary_key):
        # 通过B+树索引定位数据页
        page = self.buffer_pool.get_page(table_id, primary_key)
        return self.extract_row(page, primary_key)
    
    def write_row(self, table_id, row):
        # 1. 写WAL日志
        self.wal.append(LogEntry('INSERT', table_id, row))
        # 2. 修改缓冲池中的页
        page = self.buffer_pool.get_page_for_write(table_id, row.key)
        page.insert_row(row)
        # 3. 异步刷盘

class LSMTreeEngine(StorageEngine):
    """LSM-Tree存储引擎 (RocksDB/LevelDB)"""
    def write_row(self, row):
        # 1. 写入MemTable (内存中的有序结构)
        self.memtable.put(row.key, row.value)
        
        # 2. MemTable满后转为Immutable，生成SSTable
        if self.memtable.size > MEMTABLE_THRESHOLD:
            self.flush_memtable_to_sstable()
        
        # 3. 后台Compaction合并SSTable
        self.schedule_compaction()
    
    def read_row(self, key):
        # 1. 查MemTable
        if key in self.memtable:
            return self.memtable.get(key)
        # 2. 查Immutable MemTables
        for imm in self.immutable_memtables:
            if key in imm:
                return imm.get(key)
        # 3. 从SSTables中查找 (Bloom Filter优化)
        return self.search_sstables(key)
```

### 缓冲池管理

```python
class BufferPool:
    """缓冲池管理 - LRU改进版"""
    def __init__(self, size):
        self.size = size
        self.pages = {}  # page_id -> frame
        # 将LRU分为young和old区域
        self.young_list = LRUList(limit=size * 0.625)  # 5/8
        self.old_list = LRUList(limit=size * 0.375)    # 3/8
    
    def get_page(self, page_id):
        if page_id in self.pages:
            # 命中：移到young区头部
            self.move_to_young_head(page_id)
            return self.pages[page_id]
        
        # 未命中：从磁盘读取
        page = self.load_from_disk(page_id)
        self.add_to_old_list(page_id, page)
        return page
    
    def add_to_old_list(self, page_id, page):
        """新页加入old区，避免全表扫描污染缓冲池"""
        victim = self.old_list.evict_if_full()
        if victim:
            self.flush_if_dirty(victim)
            del self.pages[victim]
        self.old_list.add(page_id)
        self.pages[page_id] = page
```

## 应用场景
- **OLTP系统**: 行存储+InnoDB，高并发事务处理
- **OLAP系统**: 列存储+向量化执行，批量分析
- **HTAP系统**: 行列混存，同时支持事务和分析
- **NewSQL**: 分布式架构，水平扩展+强一致性

## 面试要点

1. **Q: B+树和LSM-Tree的优缺点对比？**  
   A: B+树读写均衡，适合读多写少和范围查询，但随机写性能差；LSM-Tree写放大低，顺序写入磁盘，适合写密集型场景，但读可能需要查多层，Compaction消耗资源。InnoDB用B+树，RocksDB用LSM-Tree。

2. **Q: 预写日志(WAL)的作用和实现？**  
   A: WAL保证事务持久性和原子性。实现：①事务提交前先将修改记录顺序写入日志文件；②日志落盘后返回提交成功；③后台异步将数据页刷盘；④崩溃恢复时重放日志。这样即使数据页未刷盘也能恢复。

3. **Q: 缓冲池的LRU优化有哪些？**  
   A: 传统LRU的问题是全表扫描会污染缓冲池。优化：①分区LRU（young/old区），新页先放old区，再次访问才提升；② midpoint insertion，新页插入中间位置；③ 自适应哈希索引，热点页建哈希索引加速访问。

4. **Q: 行存储和列存储的区别及适用场景？**  
   A: 行存储一行数据连续存储，适合OLTP点查和整行读取；列存储一列数据连续存储，适合OLAP批量聚合（只需读相关列，压缩率高）。HTAP系统通过行列转换或双存储引擎兼顾两者。

## 相关概念

### 数据结构
- [B+树](../data-structures/b-plus-tree.md)
- [LSM-Tree](../data-structures/lsm-tree.md)
- [跳表](../data-structures/skip-list.md)

### 算法
- [页面置换算法](../algorithms/page-replacement.md)
- [排序算法](../algorithms/sorting.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [查询优化](query-optimization.md)
- [事务管理](transaction-management.md)
