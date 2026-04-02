# 查询优化 (Query Optimization)

## 简介
查询优化是数据库系统通过选择最优执行计划来最小化查询成本的过程，直接影响数据库性能和响应时间。

## 核心概念
- **执行计划 (Execution Plan)**: 查询的具体执行步骤和顺序
- **代价模型 (Cost Model)**: 估算不同执行策略的资源消耗
- **选择率 (Selectivity)**: 谓词过滤后剩余记录比例
- **基数估计 (Cardinality Estimation)**: 估算中间结果集大小

## 实现方式 / 工作原理

### 查询优化器架构

```python
class QueryOptimizer:
    def optimize(self, sql_ast):
        """
        查询优化流程：
        1. 语法解析 -> AST
        2. 逻辑优化（重写）
        3. 物理优化（选择算子实现）
        4. 生成执行计划
        """
        # 逻辑优化：重写SQL
        logical_plan = self.logical_optimize(sql_ast)
        
        # 物理优化：选择具体算法
        physical_plans = self.generate_physical_plans(logical_plan)
        
        # 代价估算，选择最优
        best_plan = min(physical_plans, 
                       key=lambda p: self.estimate_cost(p))
        
        return best_plan
    
    def logical_optimize(self, ast):
        """逻辑优化规则"""
        rules = [
            self.push_down_predicates,   # 谓词下推
            self.eliminate_subqueries,    # 子查询展开
            self.merge_projections,       # 投影合并
            self.reorder_joins,           # 连接重排序
        ]
        for rule in rules:
            ast = rule(ast)
        return ast
    
    def estimate_cost(self, plan):
        """基于统计信息的代价估算"""
        cost = 0
        for op in plan.operators:
            if op.type == "SEQ_SCAN":
                cost += op.table_pages * IO_COST
            elif op.type == "INDEX_SCAN":
                cost += op.index_pages * IO_COST + op.result_rows * CPU_COST
            elif op.type == "HASH_JOIN":
                cost += self.hash_join_cost(op)
        return cost
```

### 连接算法选择

```python
class JoinOptimizer:
    def choose_join_algorithm(self, left_table, right_table, join_condition):
        """
        根据表大小和索引选择最优连接算法
        """
        left_size = self.get_table_stats(left_table).row_count
        right_size = self.get_table_stats(right_table).row_count
        has_index = self.has_index(join_condition)
        
        # 嵌套循环连接：小表作为外表
        if left_size < 1000 or right_size < 1000:
            return NestedLoopJoin(left_table, right_table)
        
        # 索引连接：有合适索引时
        if has_index:
            return IndexNestedLoopJoin(left_table, right_table, join_condition)
        
        # 哈希连接：等值连接，中等大小表
        if join_condition.is_equality() and left_size < 100000:
            return HashJoin(left_table, right_table)
        
        # 归并连接：有序数据或大表
        return MergeJoin(left_table, right_table)
```

### 索引选择策略

```sql
-- 单列索引 vs 复合索引选择
-- 查询：WHERE a = 1 AND b = 2 AND c > 3

-- 最优索引：(a, b, c)
-- 原因：等值列在前，范围列在后

-- 索引下推示例
SELECT * FROM orders 
WHERE status = 'shipped' 
  AND created_at > '2024-01-01';

-- 索引：(status, created_at)
-- 存储引擎先在索引层过滤status和created_at
-- 减少回表次数
```

## 应用场景
- **OLAP系统**: 复杂分析查询优化，星型/雪花模型连接优化
- **高并发OLTP**: 短查询快速执行，预编译计划缓存
- **分库分表**: 跨分片查询的路由和聚合优化
- **实时数仓**: 向量化执行、代码生成优化

## 面试要点

1. **Q: 数据库优化器如何选择最优执行计划？**  
   A: 优化器通过以下步骤：①解析SQL生成AST；②逻辑优化（谓词下推、子查询展开等）；③物理优化（选择算子实现、连接顺序）；④基于统计信息估算各计划代价；⑤选择代价最小的执行计划。代价模型通常考虑I/O、CPU和网络成本。

2. **Q: 谓词下推是什么？有什么好处？**  
   A: 谓词下推是将WHERE条件尽可能推到查询计划底层（接近数据源）的优化。好处是减少中间结果集大小，降低数据传输和处理开销。例如先过滤再连接，而非先连接再过滤。

3. **Q: 连接算法有哪些？各自适用场景？**  
   A: ①嵌套循环连接：适合小表连接，简单实现；②哈希连接：适合等值连接，中等大小表，需要内存构建哈希表；③归并连接：适合有序数据或大表，内存占用稳定；④索引嵌套循环：外表小且有索引时最优。

4. **Q: 为什么统计信息对优化器很重要？**  
   A: 统计信息（行数、数据分布、直方图）用于基数估计和选择率计算，直接影响代价估算准确性。错误的统计信息会导致优化器选择次优计划，如该用索引却全表扫描。

## 相关概念

### 数据结构
- [B+树](../data-structures/b-plus-tree.md)
- [哈希表](../data-structures/hash-table.md)

### 算法
- [排序算法](../algorithms/sorting.md)
- [连接算法](../algorithms/join-algorithms.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [数据库架构](database-architecture.md)
- [事务管理](transaction-management.md)
