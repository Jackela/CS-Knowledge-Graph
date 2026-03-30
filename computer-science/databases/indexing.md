# 索引 (Indexing)

## 简介

**索引 (Index)** 是数据库中用于加速数据查询的数据结构。类似于书籍的目录，索引允许数据库快速定位数据而不需要扫描整个表。

```
┌─────────────────────────────────────────────────────────────┐
│                    索引的作用                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   无索引查询（全表扫描）        有索引查询（快速定位）         │
│                                                             │
│   ┌─────────┐                  ┌─────────┐                 │
│   │ Record1 │                  │ 索引    │                 │
│   ├─────────┤                  ├─────────┤                 │
│   │ Record2 │ ──┐              │ A → R10 │                 │
│   ├─────────┤   │              │ B → R5  │                 │
│   │ Record3 │   │  逐行扫描    │ C → R12 │──▶ 直接访问     │
│   ├─────────┤   │              │ ...     │                 │
│   │ ...     │◀──┘              └─────────┘                 │
│   ├─────────┤                                               │
│   │ RecordN │                                               │
│   └─────────┘                                               │
│                                                             │
│   时间复杂度: O(N)             时间复杂度: O(log N)         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 索引的优缺点

### 优点
- **加速查询**：减少数据扫描量，提高查询速度
- **加速排序**：利用索引有序性避免排序操作
- **加速连接**：提高JOIN操作的效率
- **强制唯一性**：唯一索引保证数据唯一性

### 缺点
- **存储开销**：索引需要额外的存储空间
- **维护成本**：数据变更时需要维护索引
- **写性能下降**：INSERT/UPDATE/DELETE变慢

```
┌─────────────────────────────────────────────────────────────┐
│                   索引的空间-时间权衡                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    写操作频率                                               │
│         ▲                                                   │
│         │    减少索引                                       │
│    高   │         ╲                                        │
│         │          ╲                                       │
│         │           ╲  平衡点                              │
│         │            ╲                                    │
│    低   │             ╲  增加索引                          │
│         │                                                 │
│         └──────────────────────────────► 读操作频率        │
│                   低                高                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 索引类型

### 1. B-Tree 索引

#### 结构

```
B+树索引结构：

                    ┌─────┐
                    │ 50  │
                    └──┬──┘
           ┌───────────┴───────────┐
       ┌───┴───┐               ┌───┴───┐
       │ 20 40 │               │ 70 90 │
       └───┬───┘               └───┬───┘
      ┌────┼────┐            ┌────┼────┐
   ┌──┴┐ ┌─┴─┐ ┌┴┐        ┌─┴─┐ ┌─┴─┐ ┌─┴─┐
   │10 │ │30 │ │45│        │60 │ │80 │ │100│
   └───┘ └───┘ └─┘        └───┘ └───┘ └───┘
     │     │    │           │     │     │
   数据   数据  数据       数据   数据   数据
   
特点：
- 所有数据存储在叶子节点
- 叶子节点通过链表连接
- 支持范围查询和排序
- 默认索引类型
```

#### 适用场景
- 等值查询：`WHERE id = 100`
- 范围查询：`WHERE age BETWEEN 20 AND 30`
- 排序：`ORDER BY name`
- 前缀匹配：`WHERE name LIKE 'John%'`

```sql
-- 创建B-Tree索引（默认）
CREATE INDEX idx_name ON users(name);

-- 复合索引
CREATE INDEX idx_name_age ON users(name, age);

-- 唯一索引
CREATE UNIQUE INDEX idx_email ON users(email);
```

### 2. 哈希索引 (Hash Index)

#### 结构

```
哈希索引结构：

哈希函数：h(key) = key % 4

┌─────────────┐     ┌─────────┐
│  哈希表     │     │  数据   │
├─────────────┤     ├─────────┤
│ 0 │  ───────┼────▶│ RecordA │
├───┤         │     ├─────────┤
│ 1 │  ──┐    │     │ RecordB │
├───┤    │    │     ├─────────┤
│ 2 │◀───┼────┘     │ RecordC │
├───┤    │          ├─────────┤
│ 3 │◀───┘          │ RecordD │
└───┘               └─────────┘

特点：
- O(1) 等值查询
- 不支持范围查询
- 不支持排序
- 可能发生哈希冲突
```

#### 适用场景
- 精确匹配查询
- 内存数据库
- 等值连接

```sql
-- MySQL Memory引擎支持哈希索引
CREATE TABLE cache (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT
) ENGINE=MEMORY;

CREATE INDEX idx_hash USING HASH ON cache(key);
```

### 3. 全文索引 (Full-Text Index)

```
全文索引结构（倒排索引）：

文档集合：
D1: "数据库索引优化技巧"
D2: "MySQL索引设计"
D3: "数据库性能调优"

倒排索引：
┌─────────┬─────────────────┐
│  词项   │   文档列表       │
├─────────┼─────────────────┤
│ 数据库  │  D1, D3         │
│ 索引    │  D1, D2         │
│ 优化    │  D1             │
│ 技巧    │  D1             │
│ MySQL   │  D2             │
│ 设计    │  D2             │
│ 性能    │  D3             │
│ 调优    │  D3             │
└─────────┴─────────────────┘
```

```sql
-- MySQL全文索引
CREATE FULLTEXT INDEX idx_content ON articles(content);

-- 全文搜索
SELECT * FROM articles 
WHERE MATCH(content) AGAINST('数据库索引' IN NATURAL LANGUAGE MODE);

-- 布尔模式搜索
SELECT * FROM articles 
WHERE MATCH(content) AGAINST('+MySQL -Oracle' IN BOOLEAN MODE);
```

### 4. 空间索引 (Spatial Index)

```sql
-- MySQL空间索引（R-Tree）
CREATE TABLE locations (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    location POINT NOT NULL,
    SPATIAL INDEX idx_location(location)
);

-- 空间查询
SELECT * FROM locations 
WHERE MBRContains(
    GeomFromText('Polygon((0 0, 10 0, 10 10, 0 10, 0 0))'),
    location
);
```

## 索引数据结构详解

### B+树 vs B树

```
B树：                        B+树：
┌────┐                      ┌────┐
│10  │                      │10  │
├────┤                      ├────┤
│数据│                      │指针│
└────┘                      └────┘
  │                           │
┌─┴─┐                       ┌─┴─┐
│5  │                       │5  │
├────┤                      ├────┤
│数据│                      │指针│
└────┘                      └────┘

区别：
1. B+树数据只在叶子节点，B树数据在所有节点
2. B+树叶子节点有链表连接，支持顺序访问
3. B+树更适合范围查询和排序
4. B+树非叶子节点更小，可容纳更多键
```

### LSM-Tree (Log-Structured Merge-Tree)

```
LSM-Tree 结构：

写入路径：
写入 ──▶ MemTable（内存，有序）──▶ 达到阈值
                                          │
                                          ▼
                              刷写到 SSTable（磁盘，不可变）
                                          │
                                          ▼
                              后台合并（Compaction）

SSTable层级：
Level 0: [SST1] [SST2] [SST3]  ← 最近数据，可能有重叠
Level 1: [    SST4    ]        ← 合并后，无重叠
Level 2: [      SST5       ]   ← 更大文件，更旧数据

读取路径：
查询 ──▶ MemTable ──▶ Level 0 ──▶ Level 1 ──▶ Level 2
                          │
                    Bloom Filter 过滤
                          │
                    减少磁盘IO

适用：写密集型场景（HBase, Cassandra, RocksDB）
```

## 索引优化策略

### 1. 最左前缀原则

```sql
-- 复合索引 (a, b, c) 的有效使用：

✅ 有效查询：
WHERE a = 1
WHERE a = 1 AND b = 2
WHERE a = 1 AND b = 2 AND c = 3
WHERE a = 1 AND c = 3  -- b缺失，但a有效
WHERE a = 1 AND b > 2 AND c = 3  -- b范围后c无效

❌ 无效查询：
WHERE b = 2  -- 缺少最左列a
WHERE b = 2 AND c = 3  -- 缺少最左列a
WHERE c = 3  -- 缺少最左列a
```

### 2. 覆盖索引

```sql
-- 覆盖索引：查询所需字段都在索引中
CREATE INDEX idx_name_age ON users(name, age);

-- 覆盖索引查询（不需要回表）
SELECT name, age FROM users WHERE name = 'Alice';
-- 索引包含name和age，直接返回结果

-- 非覆盖索引查询（需要回表）
SELECT name, age, email FROM users WHERE name = 'Alice';
-- 索引不包含email，需要回表查询
```

### 3. 索引选择性与Cardinality

```sql
-- 查看索引统计信息
SHOW INDEX FROM users;

-- Cardinality：索引列的唯一值数量
-- 选择性 = Cardinality / 总行数
-- 选择性越高，索引效果越好

-- 高选择性（适合索引）
email: 100万行，100万唯一值，选择性 = 1.0

-- 低选择性（不适合索引）
gender: 100万行，2个唯一值，选择性 = 0.000002
```

### 4. 索引失效场景

```sql
-- 1. 对索引列进行运算
WHERE YEAR(created_at) = 2023  -- ❌ 索引失效
WHERE created_at >= '2023-01-01' AND created_at < '2024-01-01'  -- ✅ 有效

-- 2. 类型隐式转换
WHERE user_id = '123'  -- ❌ user_id是INT类型，索引可能失效
WHERE user_id = 123    -- ✅ 有效

-- 3. 前导通配符
WHERE name LIKE '%John%'  -- ❌ 索引失效
WHERE name LIKE 'John%'   -- ✅ 有效

-- 4. OR条件使用不当
WHERE id = 1 OR name = 'Alice'  -- ❌ 可能失效（除非都有索引）
UNION 代替 OR

-- 5. 不等于操作
WHERE status != 'inactive'  -- ❌ 可能失效
WHERE status IN ('active', 'pending')  -- ✅ 可能更好

-- 6. IS NULL / IS NOT NULL
WHERE email IS NULL  -- 取决于数据分布和统计信息
```

## 执行计划分析

### MySQL EXPLAIN

```sql
EXPLAIN SELECT * FROM users WHERE age > 25;

-- 输出解读：
-- id: 查询标识符
-- select_type: SIMPLE, PRIMARY, SUBQUERY等
-- table: 访问的表
-- type: 访问类型（system > const > eq_ref > ref > range > index > ALL）
-- possible_keys: 可能使用的索引
-- key: 实际使用的索引
-- key_len: 使用的索引长度
-- ref: 与索引比较的列
-- rows: 估计扫描的行数
-- Extra: 额外信息（Using index, Using where, Using filesort等）
```

### 访问类型优化目标

```
访问类型效率排序：

system > const > eq_ref > ref > fulltext > ref_or_null > 
index_merge > unique_subquery > index_subquery > 
range > index > ALL

目标：至少达到 range，最好是 ref 或更高

system: 表只有一行（系统表）
const: 通过主键或唯一索引一次就找到
eq_ref: 连接中使用主键或唯一索引
ref: 使用非唯一索引
range: 索引范围扫描
index: 全索引扫描
ALL: 全表扫描（避免）
```

## 索引维护

### 1. 索引碎片整理

```sql
-- MySQL
OPTIMIZE TABLE users;

-- PostgreSQL
REINDEX INDEX idx_name;

-- 或使用VACUUM
VACUUM ANALYZE users;
```

### 2. 统计信息更新

```sql
-- MySQL
ANALYZE TABLE users;

-- PostgreSQL
ANALYZE users;

-- SQL Server
UPDATE STATISTICS users;
```

### 3. 监控索引使用

```sql
-- MySQL：查看未使用的索引
SELECT * FROM sys.schema_unused_indexes;

-- PostgreSQL：查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

## 特殊索引技术

### 1. 部分索引 (Partial Index)

```sql
-- PostgreSQL
-- 只为活跃用户创建索引，减少索引大小
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- 查询时利用部分索引
SELECT * FROM users WHERE email = 'alice@example.com' AND status = 'active';
```

### 2. 表达式索引

```sql
-- PostgreSQL
-- 对表达式创建索引
CREATE INDEX idx_name_lower ON users(LOWER(name));

-- 查询时使用相同表达式
SELECT * FROM users WHERE LOWER(name) = 'alice';
```

### 3. 降序索引

```sql
-- MySQL 8.0+
CREATE INDEX idx_created_desc ON users(created_at DESC);

-- 优化倒序查询
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;
```

## 索引设计检查清单

```
┌─────────────────────────────────────────────────────────────┐
│                    索引设计检查清单                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  □ WHERE子句中的列是否有索引？                              │
│  □ JOIN条件中的外键是否有索引？                             │
│  □ ORDER BY列是否有索引？                                   │
│  □ 是否存在重复或冗余索引？                                 │
│  □ 索引选择性是否足够高？                                   │
│  □ 是否遵循最左前缀原则？                                   │
│  □ 是否有覆盖索引优化空间？                                 │
│  □ 写操作性能是否在可接受范围？                             │
│  □ 索引是否定期维护？                                       │
│  □ 是否有未使用的索引可以删除？                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 面试要点

### 常见问题

**Q1: B+树和B树的区别？**
> B+树所有数据都在叶子节点，非叶子节点只存储键值；叶子节点通过链表连接。B树数据分布在所有节点。B+树更适合范围查询和顺序访问，磁盘IO更稳定。

**Q2: 什么情况下索引会失效？**
> 1. 对索引列进行函数运算
> 2. 类型隐式转换
> 3. LIKE前导通配符
> 4. 不等于操作
> 5. OR条件使用不当
> 6. 违反最左前缀原则

**Q3: 聚簇索引和非聚簇索引的区别？**
> 聚簇索引：数据行和索引存储在一起，一个表只能有一个（InnoDB主键索引）。非聚簇索引：索引和数据分开存储，查询需要回表（除非覆盖索引）。

**Q4: 如何优化慢查询？**
> 1. 使用EXPLAIN分析执行计划
> 2. 添加或优化索引
> 3. 优化SQL写法
> 4. 考虑覆盖索引
> 5. 避免SELECT *
> 6. 控制返回数据量

## 相关概念

- [SQL基础](./sql-basics.md) - SQL查询优化
- [数据库范式](./normalization.md) - 表结构设计
- [并发控制](./concurrency-control.md) - 索引对并发的影响
- [事务与ACID](./transaction-acid.md) - 事务与索引的关系

## 参考资料

1. "High Performance MySQL" by Baron Schwartz
2. "SQL Performance Explained" by Markus Winand
3. MySQL Documentation: Optimization and Indexes
4. PostgreSQL Documentation: Indexes
5. Wikipedia: [Database index](https://en.wikipedia.org/wiki/Database_index)
