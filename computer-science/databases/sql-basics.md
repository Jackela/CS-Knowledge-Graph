# SQL基础 (SQL Basics)

## 简介

**SQL（Structured Query Language，结构化查询语言）**是用于管理和操作关系型数据库的标准语言。它提供了数据查询、数据定义、数据操纵和数据控制四大功能，是数据库开发和管理的核心技能。

## SQL分类

### DQL - 数据查询语言（Data Query Language）
```sql
SELECT * FROM users WHERE age > 18;
```

### DDL - 数据定义语言（Data Definition Language）
```sql
CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));
ALTER TABLE users ADD COLUMN email VARCHAR(100);
DROP TABLE users;
```

### DML - 数据操纵语言（Data Manipulation Language）
```sql
INSERT INTO users (id, name) VALUES (1, '张三');
UPDATE users SET name = '李四' WHERE id = 1;
DELETE FROM users WHERE id = 1;
```

### DCL - 数据控制语言（Data Control Language）
```sql
GRANT SELECT ON users TO user1;
REVOKE INSERT ON users FROM user1;
```

## 核心概念

- **表（Table）**：数据的二维组织形式
- **行（Row）**：一条记录
- **列（Column）**：字段/属性
- **主键（Primary Key）**：唯一标识每条记录
- **外键（Foreign Key）**：表之间的关联关系
- **索引（Index）**：加速查询的数据结构

## 常用查询

```sql
-- 条件查询
SELECT * FROM employees WHERE salary > 5000;

-- 排序
SELECT * FROM products ORDER BY price DESC;

-- 分组聚合
SELECT department, AVG(salary) FROM employees GROUP BY department;

-- 多表连接
SELECT e.name, d.name FROM employees e JOIN departments d ON e.dept_id = d.id;
```

## 相关概念

- [SQL高级](./sql-advanced.md) - 复杂查询与优化
- [关系模型](./relational-model.md) - SQL的理论基础
- [索引](./indexing.md) - 查询优化技术
- [事务与并发控制](./concurrency-control.md) - 数据一致性保障
- [规范化](./normalization.md) - 数据库设计原则
