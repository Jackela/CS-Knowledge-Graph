# 数据抽取转换加载 (ETL - Extract, Transform, Load)

## 简介

ETL 是数据工程中最核心的流程之一，用于将分散在不同数据源的数据提取(Extract)、转换(Transform)并加载(Load)到目标存储系统中，为数据分析和机器学习提供高质量的数据基础。

## 核心概念

### 1. 数据抽取 (Extract)
- **全量抽取**：一次性抽取全部数据
- **增量抽取**：只抽取新增或变更的数据
- **CDC (Change Data Capture)**：实时捕获数据变更
- **常见数据源**：关系型数据库、API、日志文件、消息队列

### 2. 数据转换 (Transform)
- **数据清洗**：处理缺失值、异常值、重复数据
- **数据标准化**：统一格式、编码、单位
- **数据聚合**：分组汇总、关联计算
- **数据丰富**：补充维度信息、外部数据关联

### 3. 数据加载 (Load)
- **批量加载 (Batch Load)**：定时批处理，适合大规模数据
- **流式加载 (Streaming Load)**：实时处理，低延迟场景
- **全量加载 vs 增量加载**：根据业务需求选择策略

### 4. 调度与编排
- **依赖管理**：任务间的执行顺序和依赖关系
- **错误处理**：重试机制、失败告警、断点续传
- **监控观测**：任务执行状态、性能指标追踪

## 实现方式

### Python ETL 示例 (使用 Pandas)

```python
import pandas as pd
from sqlalchemy import create_engine
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self, source_conn_str, target_conn_str):
        self.source_engine = create_engine(source_conn_str)
        self.target_engine = create_engine(target_conn_str)
    
    def extract(self, query):
        """从源数据库抽取数据"""
        logger.info("开始数据抽取...")
        df = pd.read_sql(query, self.source_engine)
        logger.info(f"抽取完成，共 {len(df)} 条记录")
        return df
    
    def transform(self, df):
        """数据清洗和转换"""
        logger.info("开始数据转换...")
        
        # 处理缺失值
        df = df.dropna(subset=['user_id', 'amount'])
        
        # 数据类型转换
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['amount'] = df['amount'].astype(float)
        
        # 数据标准化
        df['status'] = df['status'].str.lower().str.strip()
        
        # 添加计算字段
        df['year_month'] = df['created_at'].dt.to_period('M')
        
        # 去重
        df = df.drop_duplicates(subset=['order_id'], keep='first')
        
        logger.info(f"转换完成，剩余 {len(df)} 条记录")
        return df
    
    def load(self, df, table_name, if_exists='append'):
        """加载到目标数据库"""
        logger.info(f"开始加载数据到 {table_name}...")
        df.to_sql(
            table_name, 
            self.target_engine, 
            if_exists=if_exists,
            index=False,
            chunksize=10000
        )
        logger.info("加载完成")
    
    def run(self, query, target_table):
        """执行完整 ETL 流程"""
        try:
            df = self.extract(query)
            df = self.transform(df)
            self.load(df, target_table)
            logger.info("ETL 流程执行成功")
        except Exception as e:
            logger.error(f"ETL 执行失败: {str(e)}")
            raise

# 使用示例
if __name__ == "__main__":
    etl = ETLPipeline(
        source_conn_str="postgresql://user:pass@source/db",
        target_conn_str="postgresql://user:pass@target/dw"
    )
    etl.run(
        query="SELECT * FROM orders WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'",
        target_table="fact_orders"
    )
```

### Apache Airflow DAG 示例

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['data-team@company.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'daily_orders_etl',
    default_args=default_args,
    description='每日订单数据 ETL',
    schedule_interval='0 2 * * *',  # 每天凌晨2点执行
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'orders'],
) as dag:

    def extract_orders(**context):
        """抽取昨日订单数据"""
        pg_hook = PostgresHook(postgres_conn_id='source_db')
        sql = """
            SELECT order_id, user_id, product_id, amount, status, created_at
            FROM orders
            WHERE DATE(created_at) = DATE('{{ ds }}')
        """
        df = pg_hook.get_pandas_df(sql)
        df.to_csv('/tmp/orders_raw.csv', index=False)
        return f"抽取了 {len(df)} 条记录"

    def transform_orders(**context):
        """转换订单数据"""
        df = pd.read_csv('/tmp/orders_raw.csv')
        
        # 数据清洗
        df = df.dropna(subset=['user_id', 'amount'])
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # 添加日期维度
        df['order_date'] = df['created_at'].dt.date
        df['order_hour'] = df['created_at'].dt.hour
        
        # 计算字段
        df['is_high_value'] = df['amount'] > 1000
        
        df.to_csv('/tmp/orders_clean.csv', index=False)
        return f"清洗后剩余 {len(df)} 条记录"

    def load_orders(**context):
        """加载到数据仓库"""
        df = pd.read_csv('/tmp/orders_clean.csv')
        pg_hook = PostgresHook(postgres_conn_id='dw_db')
        
        # 先删除该日期已有数据（幂等性）
        pg_hook.run(f"""
            DELETE FROM fact_orders 
            WHERE order_date = '{{ ds }}'
        """)
        
        # 插入新数据
        df.to_sql('fact_orders', 
                  con=pg_hook.get_sqlalchemy_engine(),
                  if_exists='append',
                  index=False)
        return f"加载了 {len(df)} 条记录"

    extract_task = PythonOperator(
        task_id='extract_orders',
        python_callable=extract_orders,
    )

    transform_task = PythonOperator(
        task_id='transform_orders',
        python_callable=transform_orders,
    )

    load_task = PythonOperator(
        task_id='load_orders',
        python_callable=load_orders,
    )

    # 定义任务依赖
    extract_task >> transform_task >> load_task
```

### dbt (Data Build Tool) 示例

```yaml
-- models/staging/stg_orders.sql
with source as (
    select * from {{ source('raw', 'orders') }}
),

cleaned as (
    select
        order_id,
        user_id,
        product_id,
        
        -- 金额标准化
        cast(amount as decimal(18,2)) as amount,
        
        -- 状态标准化
        lower(trim(status)) as status,
        
        -- 时间处理
        cast(created_at as timestamp) as created_at,
        date(created_at) as order_date,
        
        -- 数据质量标记
        case 
            when amount < 0 then 'invalid_amount'
            when user_id is null then 'missing_user'
            else 'valid'
        end as data_quality_flag
        
    from source
    where order_id is not null
)

select * from cleaned
```

```yaml
-- models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    partition_by={
      "field": "order_date",
      "data_type": "date",
      "granularity": "day"
    }
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
    where data_quality_flag = 'valid'
),

users as (
    select * from {{ ref('dim_users') }}
)

select
    o.order_id,
    o.user_id,
    u.user_segment,
    o.product_id,
    o.amount,
    o.status,
    o.created_at,
    o.order_date,
    
    -- 业务指标
    case when o.amount >= 1000 then 'high_value' else 'normal' end as value_tier
    
from orders o
left join users u on o.user_id = u.user_id

{% if is_incremental() %}
where o.order_date >= (select max(order_date) from {{ this }})
{% endif %}
```

### SQL ETL 示例 (批量加载)

```sql
-- 创建临时表存储增量数据
CREATE TEMP TABLE tmp_orders_incremental AS
SELECT 
    order_id,
    user_id,
    product_id,
    CAST(amount AS DECIMAL(18,2)) as amount,
    LOWER(TRIM(status)) as status,
    CAST(created_at AS TIMESTAMP) as created_at,
    DATE(created_at) as order_date
FROM source_orders
WHERE created_at >= CURRENT_DATE - INTERVAL '1 day';

-- 删除已存在的数据（实现幂等性）
DELETE FROM fact_orders
WHERE order_date >= CURRENT_DATE - INTERVAL '1 day';

-- 插入转换后的数据
INSERT INTO fact_orders (
    order_id, user_id, product_id, amount, 
    status, created_at, order_date, etl_timestamp
)
SELECT 
    order_id,
    user_id,
    product_id,
    amount,
    status,
    created_at,
    order_date,
    CURRENT_TIMESTAMP as etl_timestamp
FROM tmp_orders_incremental
WHERE amount >= 0  -- 数据质量检查
  AND user_id IS NOT NULL;

-- 更新元数据表
INSERT INTO etl_audit_log (table_name, run_date, records_processed, status)
VALUES ('fact_orders', CURRENT_DATE, (SELECT COUNT(*) FROM tmp_orders_incremental), 'success');

-- 清理临时表
DROP TABLE tmp_orders_incremental;
```

## 示例

### 实时流式 ETL (Kafka + Flink)

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

# 创建流处理环境
env = StreamExecutionEnvironment.get_execution_environment()
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
t_env = StreamTableEnvironment.create(env, settings)

# 定义 Kafka 源表
t_env.execute_sql("""
    CREATE TABLE kafka_orders (
        order_id STRING,
        user_id STRING,
        amount DECIMAL(18,2),
        status STRING,
        event_time TIMESTAMP(3),
        WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'orders-topic',
        'properties.bootstrap.servers' = 'kafka:9092',
        'format' = 'json'
    )
""")

# 定义目标表
t_env.execute_sql("""
    CREATE TABLE fact_orders (
        order_id STRING,
        user_id STRING,
        amount DECIMAL(18,2),
        status STRING,
        event_time TIMESTAMP(3),
        processed_at TIMESTAMP(3)
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://dw:5432/analytics',
        'table-name' = 'fact_orders'
    )
""")

# 实时转换和加载
t_env.execute_sql("""
    INSERT INTO fact_orders
    SELECT 
        order_id,
        user_id,
        amount,
        UPPER(status) as status,
        event_time,
        CURRENT_TIMESTAMP as processed_at
    FROM kafka_orders
    WHERE amount > 0
""")
```

## 应用场景

| 场景 | 特点 | 技术选型 |
|------|------|----------|
| **数据仓库建设** | 大规模批处理，复杂的维度建模 | Airflow + dbt + Snowflake/BigQuery |
| **实时报表** | 低延迟，秒级更新 | Kafka + Flink/Spark Streaming |
| **机器学习数据准备** | 特征工程，数据版本控制 | TFX, Feast, MLflow |
| **数据迁移** | 一次性或周期性全量迁移 | AWS DMS, Airbyte, Fivetran |
| **数据湖构建** | 原始数据存储，Schema-on-read | Spark + Delta Lake/Iceberg |

## 面试要点

**Q: ETL 和 ELT 有什么区别？各自的适用场景是什么？**

A: 
- **ETL**：先转换后加载，适合数据质量要求高、需要清洗敏感数据的场景
- **ELT**：先加载后转换，利用数据仓库的计算能力，适合大数据量、灵活分析的场景
- 云数据仓库（如 Snowflake、BigQuery）的普及使 ELT 越来越流行

**Q: 如何保证 ETL 任务的幂等性？**

A:
- 使用 `UPSERT` 或 `MERGE` 语句处理重复数据
- 加载前删除目标表中该批次的数据
- 使用唯一键约束防止重复插入
- 记录已处理的批次 ID 或时间戳
- 事务性操作：成功则提交，失败则回滚

**Q: Batch ETL 和 Streaming ETL 如何选择？**

A:
- **Batch**：数据量大、对延迟不敏感、复杂的聚合计算、成本敏感
- **Streaming**：实时性要求高、持续数据流、需要即时决策
- **Lambda 架构**：同时支持批处理和流处理，但维护成本高
- **Kappa 架构**：纯流式架构，用流处理解决所有问题

**Q: 如何处理 ETL 中的数据质量问题？**

A:
- **事前预防**：Schema 约束、数据类型检查、业务规则验证
- **事中处理**：脏数据隔离、默认值填充、异常告警
- **事后监控**：数据质量仪表板、异常检测、SLA 监控
- **数据血缘**：追踪问题数据来源和影响范围

**Q: Airflow 中的 DAG 设计最佳实践有哪些？**

A:
- 任务粒度适中，便于重试和并行
- 使用 `depends_on_past` 控制依赖关系
- 配置合理的重试策略和超时设置
- 实现任务的幂等性
- 使用 Connections 和 Variables 管理配置
- 监控任务执行时间和资源使用

## 相关概念

### 数据结构
- [哈希表](../../computer-science/data-structures/hash-table.md) - 用于数据去重和快速查找
- [B树/B+树](../../computer-science/data-structures/b-tree.md) - 数据库索引结构
- [队列](../../computer-science/data-structures/queue.md) - 消息队列基础

### 算法
- [排序算法](../../computer-science/algorithms/sorting.md) - 数据排序和分区
- [MapReduce](../../computer-science/algorithms/mapreduce.md) - 大规模数据处理
- [一致性哈希](../../computer-science/algorithms/consistent-hashing.md) - 数据分片

### 复杂度分析
- 时间复杂度：ETL 任务的性能优化
- 空间复杂度：大数据处理时的内存管理
- I/O 复杂度：数据库读写优化

### 系统实现
- [数据库索引](../../computer-science/databases/indexing.md) - 源数据和目标数据查询优化
- [事务管理](../../computer-science/databases/transactions.md) - ETL 数据一致性
- [分片策略](../../computer-science/databases/sharding.md) - 大规模数据处理
- [消息队列](../../distributed-systems/message-queue.md) - 实时数据流
- [分布式计算](../../distributed-systems/distributed-computing.md) - Spark/Flink 集群
- [数据一致性](../../distributed-systems/consistency-models.md) - 分布式 ETL 一致性
- [机器学习数据准备](../ml-fundamentals/data-preprocessing.md) - ML 特征工程
- [AWS S3](../../cloud-devops/aws/s3.md) - 数据湖存储
- [AWS RDS](../../cloud-devops/aws/rds.md) - 托管数据库服务
