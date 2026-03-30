# SQL高级 (Advanced SQL)

## 子查询

### 相关子查询 vs 非相关子查询

```sql
-- 非相关子查询（独立执行一次）
SELECT * FROM 员工
WHERE 部门ID IN (SELECT 部门ID FROM 部门 WHERE 城市 = '北京');

-- 相关子查询（每行执行一次）
SELECT * FROM 员工 e
WHERE 工资 > (SELECT AVG(工资) FROM 员工 WHERE 部门ID = e.部门ID);
```

### EXISTS

```sql
-- 有下属的员工
SELECT * FROM 员工 e
WHERE EXISTS (
    SELECT 1 FROM 员工 
    WHERE 经理ID = e.员工ID
);
```

## 窗口函数

### 排名函数

```sql
-- 部门内工资排名
SELECT 
    姓名,
    部门,
    工资,
    ROW_NUMBER() OVER (PARTITION BY 部门 ORDER BY 工资 DESC) AS 排名,
    RANK() OVER (PARTITION BY 部门 ORDER BY 工资 DESC) AS 并列排名,
    DENSE_RANK() OVER (PARTITION BY 部门 ORDER BY 工资 DESC) AS 密集排名
FROM 员工;

-- ROW_NUMBER(): 1,2,3,4
-- RANK():      1,2,2,4 (并列跳号)
-- DENSE_RANK():1,2,2,3 (并列不跳号)
```

### 聚合窗口函数

```sql
-- 累计求和
SELECT 
    日期,
    销售额,
    SUM(销售额) OVER (ORDER BY 日期) AS 累计销售额,
    AVG(销售额) OVER (ORDER BY 日期 ROWS 6 PRECEDING) AS 7日平均
FROM 销售表;

-- 偏移函数
SELECT 
    日期,
    销售额,
    LAG(销售额, 1) OVER (ORDER BY 日期) AS 昨日销售额,
    LEAD(销售额, 1) OVER (ORDER BY 日期) AS 明日销售额
FROM 销售表;
```

## CTE（公共表表达式）

### 基本CTE

```sql
WITH 北京员工 AS (
    SELECT * FROM 员工 WHERE 城市 = '北京'
),
  高工资员工 AS (
    SELECT * FROM 北京员工 WHERE 工资 > 10000
)
SELECT * FROM 高工资员工;
```

### 递归CTE

```sql
-- 查询员工及其所有下属（层级）
WITH RECURSIVE 下属层级 AS (
    -- 锚成员：顶级经理
    SELECT 员工ID, 姓名, 经理ID, 0 AS 层级
    FROM 员工
    WHERE 经理ID IS NULL
    
    UNION ALL
    
    -- 递归成员
    SELECT e.员工ID, e.姓名, e.经理ID, 层级 + 1
    FROM 员工 e
    JOIN 下属层级 h ON e.经理ID = h.员工ID
)
SELECT * FROM 下属层级;
```

## 高级JOIN

```sql
-- 自连接
SELECT e.姓名 AS 员工, m.姓名 AS 经理
FROM 员工 e
LEFT JOIN 员工 m ON e.经理ID = m.员工ID;

-- 交叉连接（笛卡尔积）
SELECT * FROM 表A CROSS JOIN 表B;

-- 自然连接（按同名列连接）
SELECT * FROM 表A NATURAL JOIN 表B;
```

## 集合操作

```sql
-- 并集（去重）
SELECT 姓名 FROM 员工A
UNION
SELECT 姓名 FROM 员工B;

-- 并集（保留重复）
SELECT 姓名 FROM 员工A
UNION ALL
SELECT 姓名 FROM 员工B;

-- 交集
SELECT 姓名 FROM 员工A
INTERSECT
SELECT 姓名 FROM 员工B;

-- 差集
SELECT 姓名 FROM 员工A
EXCEPT
SELECT 姓名 FROM 员工B;
```

## 透视与逆透视

```sql
-- 行转列（透视）
SELECT 
    年份,
    SUM(CASE WHEN 季度 = 'Q1' THEN 销售额 ELSE 0 END) AS Q1,
    SUM(CASE WHEN 季度 = 'Q2' THEN 销售额 ELSE 0 END) AS Q2,
    SUM(CASE WHEN 季度 = 'Q3' THEN 销售额 ELSE 0 END) AS Q3,
    SUM(CASE WHEN 季度 = 'Q4' THEN 销售额 ELSE 0 END) AS Q4
FROM 销售表
GROUP BY 年份;
```

## 性能优化

### 执行计划

```sql
-- 查看执行计划
EXPLAIN SELECT * FROM 员工 WHERE 部门ID = 5;

-- 分析统计
EXPLAIN ANALYZE SELECT * FROM 员工 WHERE 部门ID = 5;
```

### 优化技巧

```sql
-- 避免SELECT *
SELECT 姓名, 工资 FROM 员工;

-- 使用索引
CREATE INDEX idx_部门 ON 员工(部门ID);

-- 批量操作
INSERT INTO 员工 VALUES (...), (...), (...);

-- 使用LIMIT限制结果
SELECT * FROM 员工 LIMIT 10;
```

## 相关概念

- [SQL基础](../databases/sql-basics.md)
- [索引](../databases/indexing.md) - 查询优化
- [规范化](../databases/normalization.md) - 数据库设计

## 参考资料

1. 《SQL学习指南》
2. PostgreSQL/MySQL 官方文档
