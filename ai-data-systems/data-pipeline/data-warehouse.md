# 数据仓库 (Data Warehouse)

## 简介

数据仓库是一个面向主题的、集成的、相对稳定的、反映历史变化的数据集合，用于支持管理决策和数据分析。它从多个异构数据源收集数据，经过清洗转换后，以优化的结构存储，为商业智能(BI)和数据分析提供基础。

## 核心概念

### 1. 数据仓库特性 (Inmon)
- **面向主题 (Subject-Oriented)**：围绕业务主题组织，而非应用功能
- **集成性 (Integrated)**：统一不同源系统的数据格式和编码
- **非易失性 (Non-volatile)**：数据一旦写入不轻易修改，支持历史追溯
- **时变性 (Time-Variant)**：包含时间维度，记录数据历史变化

### 2. 数据建模方法

#### 星型模型 (Star Schema)
- 一个中心事实表，周围连接多个维度表
- 维度表直接与事实表关联
- 查询简单高效，适合即席查询

```
    ┌─────────────┐
    │  dim_date   │
    └──────┬──────┘
           │
┌──────────┼──────────┐
│          │          │
▼          ▼          ▼
┌─────────┐    ┌──────────────┐    ┌─────────────┐
│dim_product│◄──┤  fact_sales  ├──►│  dim_store  │
└─────────┘    └──────────────┘    └─────────────┘
                      │
               ┌──────┴──────┐
               ▼             ▼
        ┌─────────────┐  ┌─────────────┐
        │  dim_customer│  │ dim_promotion│
        └─────────────┘  └─────────────┘
```

#### 雪花模型 (Snowflake Schema)
- 维度表进一步规范化，减少数据冗余
- 维度表之间存在层级关系
- 节省存储，但查询需要更多 JOIN

#### Data Vault 模型
- 面向企业级数据仓库的建模方法
- 包含 Hub（业务主键）、Link（关系）、Satellite（属性）
- 高度灵活，易于扩展和历史追踪

### 3. OLAP vs OLTP

| 特性 | OLAP (数据仓库) | OLTP (业务系统) |
|------|-----------------|-----------------|
| **目的** | 分析决策 | 业务交易处理 |
| **数据量** | TB-PB 级 | GB 级 |
| **查询模式** | 复杂聚合，大范围扫描 | 单条/少量记录读写 |
| **更新频率** | 批量加载，定期更新 | 实时事务处理 |
| **数据时效** | 历史数据，时变性 | 当前最新状态 |
| **设计目标** | 查询性能 | 事务一致性 |

### 4. 数据分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                      数据应用层 (ADS)                        │
│          面向具体业务场景的数据集市 (Data Mart)               │
├─────────────────────────────────────────────────────────────┤
│                      数据服务层 (DWS)                        │
│              主题宽表，轻度汇总，面向分析场景                  │
├─────────────────────────────────────────────────────────────┤
│                      数据明细层 (DWD)                        │
│           清洗后的明细数据，保持最细粒度                       │
├─────────────────────────────────────────────────────────────┤
│                      数据引入层 (ODS)                        │
│              原始数据镜像，与源系统结构一致                    │
├─────────────────────────────────────────────────────────────┤
│                    数据源 (Source Systems)                    │
│         业务数据库、日志、API、文件等                         │
└─────────────────────────────────────────────────────────────┘
```

### 5. 现代云数据仓库

| 产品 | 厂商 | 特点 |
|------|------|------|
| **Snowflake** | Snowflake | 存算分离、弹性扩展、零运维 |
| **BigQuery** | Google Cloud | 无服务器、PB 级分析、ML 集成 |
| **Redshift** | AWS | 与 AWS 生态深度集成、 Spectrum 查询 S3 |
| **Databricks** | Databricks | Lakehouse 架构、Spark 原生 |
| **ClickHouse** | 开源 | 列式存储、实时分析、高性能 |

## 实现方式

### 星型模型 SQL 实现

```sql
-- 创建时间维度表
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week TINYINT,
    day_of_month TINYINT,
    day_of_year SMALLINT,
    week_of_year TINYINT,
    month_number TINYINT,
    month_name VARCHAR(10),
    quarter TINYINT,
    year SMALLINT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_quarter TINYINT,
    fiscal_year SMALLINT
);

-- 创建产品维度表
CREATE TABLE dim_product (
    product_key INT PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(200),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    brand VARCHAR(100),
    supplier_id VARCHAR(50),
    unit_cost DECIMAL(18,2),
    unit_price DECIMAL(18,2),
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    
    INDEX idx_product_id (product_id),
    INDEX idx_category (category)
);

-- 创建客户维度表 (SCD Type 2)
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(50),
    address VARCHAR(500),
    city VARCHAR(100),
    country VARCHAR(100),
    segment VARCHAR(50),
    registration_date DATE,
    effective_date DATE,
    expiry_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    
    INDEX idx_customer_id (customer_id),
    INDEX idx_segment (segment)
);

-- 创建销售事实表
CREATE TABLE fact_sales (
    sale_key BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- 外键关联维度表
    date_key INT NOT NULL,
    product_key INT NOT NULL,
    customer_key INT NOT NULL,
    store_key INT NOT NULL,
    promotion_key INT,
    
    -- 退化维度
    order_id VARCHAR(50),
    order_line_number INT,
    
    -- 度量值
    quantity INT,
    unit_price DECIMAL(18,2),
    unit_cost DECIMAL(18,2),
    sales_amount DECIMAL(18,2),
    cost_amount DECIMAL(18,2),
    profit_amount DECIMAL(18,2),
    discount_amount DECIMAL(18,2),
    
    -- 外键约束
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    
    -- 分区键
    INDEX idx_date_key (date_key),
    INDEX idx_product_key (product_key),
    INDEX idx_customer_key (customer_key)
) PARTITION BY RANGE (date_key);
```

### Python 数据分析示例

```python
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

class DataWarehouseAnalyzer:
    def __init__(self, warehouse_conn_str):
        self.engine = create_engine(warehouse_conn_str)
    
    def get_sales_summary(self, start_date, end_date):
        """获取销售汇总分析"""
        query = """
        SELECT 
            d.year,
            d.month_name,
            p.category,
            c.segment,
            SUM(f.sales_amount) as total_sales,
            SUM(f.profit_amount) as total_profit,
            SUM(f.quantity) as total_quantity,
            COUNT(DISTINCT f.order_id) as order_count,
            AVG(f.unit_price) as avg_unit_price
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_product p ON f.product_key = p.product_key
        JOIN dim_customer c ON f.customer_key = c.customer_key
        WHERE d.full_date BETWEEN %(start)s AND %(end)s
        GROUP BY d.year, d.month_name, p.category, c.segment
        ORDER BY d.year, d.month_name, total_sales DESC
        """
        return pd.read_sql(query, self.engine, 
                          params={'start': start_date, 'end': end_date})
    
    def get_top_customers(self, n=10):
        """获取 Top N 客户"""
        query = f"""
        SELECT 
            c.customer_name,
            c.segment,
            c.city,
            SUM(f.sales_amount) as total_spent,
            SUM(f.profit_amount) as total_profit,
            COUNT(DISTINCT f.order_id) as order_count,
            AVG(f.sales_amount) as avg_order_value
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        WHERE c.is_current = TRUE
        GROUP BY c.customer_key, c.customer_name, c.segment, c.city
        ORDER BY total_spent DESC
        LIMIT {n}
        """
        return pd.read_sql(query, self.engine)
    
    def get_monthly_trend(self, year):
        """获取月度趋势"""
        query = """
        SELECT 
            d.month_number,
            d.month_name,
            SUM(f.sales_amount) as monthly_sales,
            SUM(f.profit_amount) as monthly_profit,
            LAG(SUM(f.sales_amount)) OVER (ORDER BY d.month_number) as prev_month_sales,
            (SUM(f.sales_amount) - LAG(SUM(f.sales_amount)) OVER (ORDER BY d.month_number)) 
                / NULLIF(LAG(SUM(f.sales_amount)) OVER (ORDER BY d.month_number), 0) * 100 
                as mom_growth_pct
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.year = %(year)s
        GROUP BY d.month_number, d.month_name
        ORDER BY d.month_number
        """
        return pd.read_sql(query, self.engine, params={'year': year})
    
    def get_product_performance(self, category=None):
        """产品绩效分析"""
        where_clause = "WHERE p.category = %(category)s" if category else ""
        params = {'category': category} if category else {}
        
        query = f"""
        SELECT 
            p.category,
            p.sub_category,
            p.product_name,
            SUM(f.sales_amount) as total_sales,
            SUM(f.quantity) as units_sold,
            SUM(f.profit_amount) as total_profit,
            ROUND(SUM(f.profit_amount) / NULLIF(SUM(f.sales_amount), 0) * 100, 2) as profit_margin_pct,
            RANK() OVER (PARTITION BY p.category ORDER BY SUM(f.sales_amount) DESC) as sales_rank
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        {where_clause}
        GROUP BY p.product_key, p.category, p.sub_category, p.product_name
        ORDER BY total_sales DESC
        """
        return pd.read_sql(query, self.engine, params=params)

# 使用示例
if __name__ == "__main__":
    dw = DataWarehouseAnalyzer("postgresql://user:pass@localhost/dw")
    
    # 销售汇总
    summary = dw.get_sales_summary('2024-01-01', '2024-12-31')
    print("销售汇总:", summary.head())
    
    # Top 客户
    top_customers = dw.get_top_customers(10)
    print("Top 客户:", top_customers)
    
    # 月度趋势
    trend = dw.get_monthly_trend(2024)
    print("月度趋势:", trend)
```

### dbt 数据仓库建模

```yaml
# dbt_project.yml
name: 'data_warehouse'
version: '1.0.0'

models:
  data_warehouse:
    staging:
      +materialized: view
      +schema: staging
    marts:
      +materialized: table
      +schema: marts
      core:
        +materialized: incremental
        +unique_key: 'sale_key'
```

```sql
-- models/staging/stg_orders.sql
with source as (
    select * from {{ source('raw', 'orders') }}
),

staged as (
    select
        order_id,
        customer_id,
        product_id,
        store_id,
        quantity::int as quantity,
        unit_price::decimal(18,2) as unit_price,
        discount::decimal(18,2) as discount,
        order_date::date as order_date,
        status,
        created_at::timestamp as created_at
    from source
    where order_id is not null
)

select * from staged
```

```sql
-- models/marts/core/fct_sales.sql
{{ config(
    materialized='incremental',
    unique_key='sale_id',
    partition_by={
      "field": "order_date",
      "data_type": "date",
      "granularity": "month"
    }
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

products as (
    select * from {{ ref('dim_products') }}
),

customers as (
    select * from {{ ref('dim_customers') }}
),

dates as (
    select * from {{ ref('dim_dates') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['o.order_id', 'o.product_id']) }} as sale_id,
        o.order_id,
        d.date_key,
        p.product_key,
        c.customer_key,
        
        o.quantity,
        o.unit_price,
        o.discount,
        o.quantity * o.unit_price as gross_sales,
        o.quantity * o.unit_price * (1 - o.discount) as net_sales,
        o.quantity * p.unit_cost as cost_amount,
        (o.quantity * o.unit_price * (1 - o.discount)) - (o.quantity * p.unit_cost) as profit_amount,
        
        o.order_date,
        o.status,
        current_timestamp() as loaded_at
        
    from orders o
    left join products p on o.product_id = p.product_id and p.is_current = true
    left join customers c on o.customer_id = c.customer_id and c.is_current = true
    left join dates d on o.order_date = d.full_date
    
    {% if is_incremental() %}
    where o.order_date >= (select max(order_date) from {{ this }})
    {% endif %}
)

select * from final
```

## 示例

### Snowflake 数据仓库实现

```sql
-- 创建 Warehouse（计算资源）
CREATE WAREHOUSE analytics_wh
    WITH
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;

-- 创建数据库和 Schema
CREATE DATABASE sales_dw;
CREATE SCHEMA sales_dw.marts;

-- 创建存储集成（连接 AWS S3）
CREATE STORAGE INTEGRATION s3_integration
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789:role/SnowflakeS3Role'
    STORAGE_ALLOWED_LOCATIONS = ('s3://data-lake/raw/');

-- 创建 Stage
CREATE STAGE raw_data_stage
    URL = 's3://data-lake/raw/orders/'
    STORAGE_INTEGRATION = s3_integration
    FILE_FORMAT = (TYPE = 'JSON');

-- 创建外部表（数据湖查询）
CREATE EXTERNAL TABLE ext_orders (
    order_id STRING AS (VALUE:order_id::STRING),
    customer_id STRING AS (VALUE:customer_id::STRING),
    amount NUMBER(18,2) AS (VALUE:amount::NUMBER(18,2)),
    order_date DATE AS (VALUE:order_date::DATE)
)
LOCATION = @raw_data_stage
FILE_FORMAT = (TYPE = 'JSON');

-- 物化视图（自动刷新）
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT 
    order_date,
    COUNT(*) as order_count,
    SUM(amount) as total_sales
FROM ext_orders
GROUP BY order_date;

-- 创建任务（定时 ETL）
CREATE TASK load_fact_sales
    WAREHOUSE = analytics_wh
    SCHEDULE = 'USING CRON 0 2 * * * UTC'  -- 每天凌晨2点
AS
    INSERT INTO fact_sales
    SELECT 
        d.date_key,
        p.product_key,
        c.customer_key,
        e.amount,
        current_timestamp()
    FROM ext_orders e
    JOIN dim_date d ON e.order_date = d.full_date
    JOIN dim_product p ON e.product_id = p.product_id
    JOIN dim_customer c ON e.customer_id = c.customer_id
    WHERE e.order_date >= CURRENT_DATE - 1;

-- 启动作业
ALTER TASK load_fact_sales RESUME;
```

### BigQuery 分区表优化

```sql
-- 创建分区表（按日期分区）
CREATE TABLE sales_dw.fact_sales (
    sale_id STRING,
    order_id STRING,
    date_key INT64,
    product_key INT64,
    customer_key INT64,
    quantity INT64,
    unit_price NUMERIC,
    sales_amount NUMERIC,
    profit_amount NUMERIC,
    order_date DATE
)
PARTITION BY order_date
CLUSTER BY product_key, customer_key;

-- 分区裁剪查询示例
SELECT 
    product_key,
    SUM(sales_amount) as total_sales
FROM sales_dw.fact_sales
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'  -- 只扫描1个分区
GROUP BY product_key;

-- 物化视图
CREATE MATERIALIZED VIEW sales_dw.mv_monthly_sales AS
SELECT 
    DATE_TRUNC(order_date, MONTH) as month,
    product_key,
    COUNT(*) as order_count,
    SUM(sales_amount) as total_sales,
    AVG(profit_amount) as avg_profit
FROM sales_dw.fact_sales
GROUP BY 1, 2;
```

## 应用场景

| 场景 | 描述 | 典型技术栈 |
|------|------|------------|
| **商业智能报表** | 企业级 Dashboard、管理报表 | Tableau + Snowflake |
| **自助分析** | 业务人员自助数据探索 | Looker + BigQuery |
| **数据科学** | ML 特征工程、数据挖掘 | Databricks + MLflow |
| **实时分析** | 实时监控、运营大屏 | ClickHouse + Superset |
| **湖仓一体** | 统一批流、存储计算分离 | Delta Lake + Spark |

## 面试要点

**Q: 星型模型和雪花模型有什么区别？如何选择？**

A:
- **星型模型**：维度表直接关联事实表，去规范化设计，查询性能好，适合即席查询和 BI 报表
- **雪花模型**：维度表进一步规范化，减少冗余，节省存储，但查询需要更多 JOIN，适合数据量大、存储成本敏感的场景
- **选择建议**：大多数场景推荐使用星型模型，简单高效；当维度表数据量巨大且有明显层级关系时考虑雪花模型

**Q: 什么是缓慢变化维(SCD)？如何处理？**

A:
- **SCD Type 0**：保留原始值，不更新
- **SCD Type 1**：直接覆盖，不保留历史
- **SCD Type 2**：新增记录，保留历史（使用 effective_date/expiry_date/is_current 标记）
- **SCD Type 3**：新增字段保存部分历史（如前值）
- **SCD Type 4**：单独的历史表
- 实践中 Type 2 最常用，通过增加代理键实现历史追踪

**Q: 数据仓库分层架构有什么优势？**

A:
- **ODS 层**：原始数据备份，方便问题追溯和数据重跑
- **DWD 层**：清洗后的明细数据，统一数据口径，支持多场景复用
- **DWS 层**：轻度汇总，减少重复计算，提升查询性能
- **ADS 层**：面向具体应用，提供业务友好的数据接口
- 分层实现了数据解耦，提高可维护性和可扩展性

**Q: 云数据仓库与传统数据仓库的主要区别是什么？**

A:
- **存算分离**：存储和计算独立扩展，成本更优
- **弹性扩展**：按需自动扩缩容，无需预先规划
- **无服务器**：无需管理基础设施，降低运维成本
- **数据共享**：跨组织数据共享能力
- **零拷贝克隆**：快速创建数据副本，支持开发测试
- 代表产品：Snowflake、BigQuery、Redshift Serverless

**Q: 如何优化数据仓库的查询性能？**

A:
- **分区策略**：按时间或其他高频过滤条件分区，实现分区裁剪
- **分桶/聚类**：对常用 JOIN 或过滤列进行聚类
- **物化视图**：预计算常用聚合查询
- **列式存储**：减少 I/O，提高压缩率
- **结果缓存**：利用查询结果缓存
- **统计信息**：保持表统计信息更新，优化器生成最优执行计划
- **索引优化**：合理使用排序键、主键

## 相关概念

### 数据结构
- [B树/B+树](../../computer-science/data-structures/b-tree.md) - 数据仓库索引结构
- [位图索引](../../computer-science/data-structures/bitmap-index.md) - 低基数列优化
- [列式存储](../../computer-science/data-structures/column-store.md) - OLAP 存储格式

### 算法
- [MapReduce](../../computer-science/algorithms/mapreduce.md) - 大规模数据处理
- [排序算法](../../computer-science/algorithms/sorting.md) - 数据排序和分区
- [压缩算法](../../computer-science/algorithms/compression.md) - 列式存储压缩

### 复杂度分析
- 查询复杂度：JOIN 操作、聚合计算的性能分析
- 存储复杂度：分区、压缩对存储的影响
- 网络 I/O：分布式数据仓库的数据传输优化

### 系统实现
- [数据库索引](../../computer-science/databases/indexing.md) - 数据仓库查询优化
- [查询优化器](../../computer-science/databases/query-optimizer.md) - 执行计划生成
- [事务管理](../../computer-science/databases/transactions.md) - ETL 加载一致性
- [分片策略](../../computer-science/databases/sharding.md) - 大规模数据分布
- [消息队列](../../distributed-systems/message-queue.md) - 实时数据摄入
- [分布式计算](../../distributed-systems/distributed-computing.md) - MPP 架构
- [数据一致性](../../distributed-systems/consistency-models.md) - 最终一致性保证
- [机器学习特征工程](../ml-fundamentals/feature-engineering.md) - ML 数据准备
- [AWS S3](../../cloud-devops/aws/s3.md) - 数据湖存储层
- [AWS RDS](../../cloud-devops/aws/rds.md) - 源数据系统
