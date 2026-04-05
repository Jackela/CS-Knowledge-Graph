# 特征存储 (Feature Store)

## 简介

特征存储 (Feature Store) 是 MLOps 中的核心基础设施，用于统一管理机器学习特征的生命周期。它解决了特征工程中的重复计算、训练-服务偏差、特征一致性等关键问题，实现特征的共享和复用。

## 核心概念

### 特征存储架构

```
┌─────────────────────────────────────────────────────────┐
│                    Feature Store                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐        ┌──────────────┐              │
│  │ Offline Store│◄──────►│Feature Registry│            │
│  │  (离线存储)   │        │  (特征注册表)   │            │
│  │  - Data Lake │        │  - 元数据管理   │            │
│  │  - Data Ware │        │  - 版本控制    │            │
│  └──────┬───────┘        └──────┬───────┘              │
│         │                       │                      │
│         ▼                       ▼                      │
│  ┌──────────────┐        ┌──────────────┐              │
│  │ Online Store │        │  Feature     │              │
│  │  (在线存储)   │        │  Pipeline    │              │
│  │  - Redis     │        │  (特征管道)   │              │
│  │  - DynamoDB  │        │  - ETL/流处理  │             │
│  └──────┬───────┘        └──────────────┘              │
│         │                                              │
│         ▼                                              │
│  ┌─────────────────────────────────────────┐           │
│  │        Training / Serving                │           │
│  │    训练 (批处理)    服务 (实时)          │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

### 存储类型对比

| 特性 | Offline Store | Online Store |
|------|---------------|--------------|
| **用途** | 训练数据、批量推理 | 实时预测、在线服务 |
| **数据规模** | TB-PB 级 | GB 级（热特征）|
| **延迟要求** | 分钟-小时级 | 毫秒级 |
| **存储系统** | S3、HDFS、BigQuery | Redis、DynamoDB、Aerospike |
| **数据更新** | 批量写入 | 实时/准实时写入 |
| **一致性** | 最终一致 | 强一致 |

### 关键概念

| 概念 | 定义 |
|------|------|
| **Feature Group** | 相关特征的集合，通常对应一个数据源 |
| **Feature View** | 用于特定模型训练或服务的特征子集 |
| **Point-in-time Correctness** | 确保训练时特征值不泄露未来信息 |
| **Training-Serving Skew** | 训练和服务时特征计算不一致 |

## 实现方式

### 1. Feast 特征存储

```python
# feature_definitions.py
from feast import Entity, Feature, FeatureView, ValueType
from feast.types import Float32, Int64, String
from datetime import timedelta

# 定义实体
user = Entity(
    name="user_id",
    value_type=ValueType.INT64,
    description="用户ID"
)

# 定义特征视图
user_features = FeatureView(
    name="user_features",
    entities=["user_id"],
    ttl=timedelta(days=1),
    features=[
        Feature(name="age", dtype=Int64),
        Feature(name="income", dtype=Float32),
        Feature(name="city", dtype=String),
        Feature(name="registration_days", dtype=Int64),
        Feature(name="total_purchases", dtype=Float32),
        Feature(name="avg_order_value", dtype=Float32),
    ],
    online=True,
    source=user_source,  # 数据源定义
    tags={"team": "recommendation"}
)

# 交易特征
transaction_stats = FeatureView(
    name="transaction_stats",
    entities=["user_id"],
    ttl=timedelta(hours=6),
    features=[
        Feature(name="last_7d_amount", dtype=Float32),
        Feature(name="last_30d_transactions", dtype=Int64),
        Feature(name="preferred_category", dtype=String),
    ],
    online=True,
    source=transaction_source
)
```

```python
# feast_config.yaml
project: my_ml_project
registry: s3://my-bucket/registry.db
provider: aws
online_store:
    type: redis
    connection_string: localhost:6379
offline_store:
    type: redshift
    host: redshift-cluster.region.redshift.amazonaws.com
    port: 5439
    database: feast
    schema: public
```

```python
# 使用 Feast
from feast import FeatureStore
import pandas as pd

store = FeatureStore(repo_path=".")

# 获取历史特征用于训练
train_df = store.get_historical_features(
    entity_df=pd.DataFrame({
        "user_id": [1, 2, 3],
        "event_timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"]
    }),
    features=[
        "user_features:age",
        "user_features:income",
        "transaction_stats:last_7d_amount"
    ]
).to_df()

# 获取在线特征用于实时预测
online_features = store.get_online_features(
    features=[
        "user_features:age",
        "user_features:total_purchases"
    ],
    entity_rows=[{"user_id": 1}]
).to_dict()

# 物化特征到在线存储
store.materialize(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31)
)
```

### 2. 自定义特征存储

```python
# feature_store.py
import redis
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class FeatureDefinition:
    name: str
    dtype: str
    description: str
    owner: str
    tags: List[str]

class SimpleFeatureStore:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.online_store = redis.Redis(
            host=redis_host, port=redis_port, decode_responses=True
        )
        self.feature_registry = {}
        self.offline_store_path = "/data/features"
    
    def register_feature(self, feature: FeatureDefinition):
        """注册特征元数据"""
        self.feature_registry[feature.name] = feature
        print(f"Registered feature: {feature.name}")
    
    def _get_key(self, entity_type: str, entity_id: str, feature_name: str) -> str:
        """生成 Redis key"""
        return f"feature:{entity_type}:{entity_id}:{feature_name}"
    
    def write_online(self, entity_type: str, entity_id: str, 
                     features: Dict[str, any], ttl: int = 86400):
        """写入在线特征"""
        key_prefix = f"feature:{entity_type}:{entity_id}"
        
        # 使用 Hash 存储多个特征
        self.online_store.hset(key_prefix, mapping=features)
        self.online_store.expire(key_prefix, ttl)
    
    def read_online(self, entity_type: str, entity_id: str, 
                    feature_names: List[str]) -> Dict[str, any]:
        """读取在线特征"""
        key = f"feature:{entity_type}:{entity_id}"
        features = self.online_store.hmget(key, feature_names)
        return {name: val for name, val in zip(feature_names, features) if val}
    
    def batch_read_online(self, entity_type: str, entity_ids: List[str],
                         feature_names: List[str]) -> pd.DataFrame:
        """批量读取在线特征"""
        pipe = self.online_store.pipeline()
        
        for entity_id in entity_ids:
            key = f"feature:{entity_type}:{entity_id}"
            pipe.hmget(key, feature_names)
        
        results = pipe.execute()
        
        data = []
        for entity_id, features in zip(entity_ids, results):
            row = {"entity_id": entity_id}
            row.update({name: val for name, val in zip(feature_names, features)})
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_training_features(self, entity_df: pd.DataFrame, 
                             feature_names: List[str],
                             point_in_time_column: str = "timestamp") -> pd.DataFrame:
        """获取时序正确的训练特征（Point-in-time Join）"""
        # 从离线存储（如 Parquet 文件）读取
        feature_data = []
        
        for feature_name in feature_names:
            df = pd.read_parquet(f"{self.offline_store_path}/{feature_name}.parquet")
            
            # 时序 Join：取 entity_df 时间点之前的最新值
            merged = pd.merge_asof(
                entity_df.sort_values(point_in_time_column),
                df.sort_values("timestamp"),
                on=point_in_time_column,
                by="entity_id",
                direction="backward"
            )
            feature_data.append(merged[["entity_id", feature_name]])
        
        # 合并所有特征
        result = entity_df
        for feat_df in feature_data:
            result = result.merge(feat_df, on="entity_id", how="left")
        
        return result

# 使用示例
store = SimpleFeatureStore()

# 注册特征
store.register_feature(FeatureDefinition(
    name="user_age",
    dtype="int",
    description="用户年龄",
    owner="data-team",
    tags=["user", "demographic"]
))

# 写入在线特征
store.write_online("user", "12345", {
    "age": 28,
    "gender": "M",
    "city": "Beijing"
})

# 实时预测时读取
features = store.read_online("user", "12345", ["age", "gender"])
```

### 3. 特征管道 (Feature Pipeline)

```python
# feature_pipeline.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window

class FeaturePipeline:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("FeaturePipeline") \
            .getOrCreate()
    
    def build_user_features(self, transactions_df, users_df):
        """构建用户聚合特征"""
        
        # 时间窗口定义
        window_7d = Window.partitionBy("user_id") \
            .orderBy("timestamp") \
            .rangeBetween(-7*86400, 0)
        
        window_30d = Window.partitionBy("user_id") \
            .orderBy("timestamp") \
            .rangeBetween(-30*86400, 0)
        
        # 计算滚动窗口特征
        features = transactions_df \
            .withColumn("amount_7d", sum("amount").over(window_7d)) \
            .withColumn("count_7d", count("*").over(window_7d)) \
            .withColumn("amount_30d", sum("amount").over(window_30d)) \
            .withColumn("count_30d", count("*").over(window_30d)) \
            .withColumn("avg_amount_7d", col("amount_7d") / col("count_7d")) \
            .withColumn("days_since_last", 
                (current_timestamp() - max("timestamp").over(
                    Window.partitionBy("user_id"))) / 86400)
        
        # 加入用户基础信息
        user_features = users_df.join(
            features.groupBy("user_id").agg(
                last("amount_7d").alias("last_7d_amount"),
                last("count_7d").alias("last_7d_count"),
                last("amount_30d").alias("last_30d_amount"),
                avg("amount").alias("avg_transaction_amount"),
                stddev("amount").alias("std_transaction_amount")
            ),
            "user_id",
            "left"
        )
        
        return user_features
    
    def run_batch(self, output_path: str):
        """运行批量特征计算"""
        # 读取数据
        transactions = self.spark.read.parquet("s3://data/transactions/")
        users = self.spark.read.parquet("s3://data/users/")
        
        # 计算特征
        features = self.build_user_features(transactions, users)
        
        # 写入离线存储
        features.write \
            .mode("overwrite") \
            .partitionBy("date") \
            .parquet(output_path)
        
        print(f"Features written to {output_path}")

# 流式特征管道
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

class StreamingFeaturePipeline:
    def __init__(self, feature_store):
        self.spark = SparkSession.builder \
            .appName("StreamingFeatures") \
            .getOrCreate()
        self.feature_store = feature_store
    
    def start(self):
        """启动流式特征计算"""
        schema = StructType([
            StructField("user_id", StringType(), True),
            StructField("amount", DoubleType(), True),
            StructField("category", StringType(), True),
            StructField("timestamp", StringType(), True)
        ])
        
        # 读取 Kafka
        stream = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", "transactions") \
            .load()
        
        # 解析 JSON
        parsed = stream \
            .select(from_json(col("value").cast("string"), schema).alias("data")) \
            .select("data.*")
        
        # 聚合计算
        agg_features = parsed \
            .groupBy(window("timestamp", "5 minutes"), "user_id") \
            .agg(
                sum("amount").alias("recent_amount"),
                count("*").alias("recent_count"),
                collect_list("category").alias("categories")
            )
        
        # 写入在线存储
        def write_to_online_store(batch_df, batch_id):
            for row in batch_df.collect():
                self.feature_store.write_online(
                    "user", 
                    row.user_id,
                    {
                        "recent_5m_amount": row.recent_amount,
                        "recent_5m_count": row.recent_count
                    }
                )
        
        query = agg_features \
            .writeStream \
            .foreachBatch(write_to_online_store) \
            .outputMode("update") \
            .start()
        
        return query
```

### 4. Tecton 风格特征定义

```python
# tecton_style_features.py
from tecton import *
from datetime import datetime, timedelta

# 批处理特征
@batch_feature_view(
    sources=[user_transactions],
    entities=[user],
    mode="spark_sql",
    online=True,
    offline=True,
    feature_start_time=datetime(2023, 1, 1),
    ttl=timedelta(days=7)
)
def user_transaction_stats(user_transactions):
    return f"""
        SELECT
            user_id,
            timestamp,
            SUM(amount) as total_amount_7d,
            COUNT(*) as transaction_count_7d,
            AVG(amount) as avg_amount_7d,
            MAX(amount) as max_amount_7d
        FROM {user_transactions}
        WHERE timestamp >= timestamp_sub(current_timestamp(), 7)
        GROUP BY user_id, timestamp
    """

# 流式特征
@stream_feature_view(
    sources=[transaction_stream],
    entities=[user],
    mode="pyspark",
    online=True,
    feature_start_time=datetime(2023, 1, 1),
    ttl=timedelta(hours=1)
)
def user_recent_activity(transaction_stream):
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window
    
    window = Window.partitionBy("user_id").orderBy("timestamp")
    
    return transaction_stream \
        .withColumn("time_since_last", 
            F.unix_timestamp("timestamp") - 
            F.lag("timestamp").over(window)) \
        .select(
            "user_id",
            "timestamp",
            "time_since_last",
            F.sum("amount").over(Window.partitionBy("user_id")) \
                .alias("session_amount")
        )

# 实时聚合特征
@on_demand_feature_view(
    sources=[user_transaction_stats, user_recent_activity],
    mode="python",
    output_schema=FeatureSchema([
        Field("current_risk_score", Float64)
    ])
)
def user_risk_score(user_transaction_stats, user_recent_activity):
    """实时计算风险分数"""
    if user_recent_activity["transaction_count_7d"] > 10:
        return {"current_risk_score": 0.8}
    
    score = min(1.0, user_transaction_stats["avg_amount_7d"] / 1000)
    return {"current_risk_score": score}
```

## 示例

### 完整的特征工程工作流

```python
# workflow.py
from feast import FeatureStore
import pandas as pd
from sklearn.model_selection import train_test_split

class MLWorkflow:
    def __init__(self):
        self.store = FeatureStore(repo_path=".")
    
    def prepare_training_data(self, entity_df: pd.DataFrame) -> pd.DataFrame:
        """准备训练数据"""
        # 获取历史特征
        feature_df = self.store.get_historical_features(
            entity_df=entity_df,
            features=[
                "user_features:age",
                "user_features:income",
                "user_features:city",
                "transaction_stats:last_7d_amount",
                "transaction_stats:last_30d_transactions",
                "user_transaction_stats:avg_amount_7d",
            ]
        ).to_df()
        
        # 特征编码
        feature_df = pd.get_dummies(feature_df, columns=["city"])
        
        # 填充缺失值
        feature_df = feature_df.fillna({
            "last_7d_amount": 0,
            "last_30d_transactions": 0,
            "avg_amount_7d": feature_df["avg_amount_7d"].median()
        })
        
        return feature_df
    
    def deploy_features(self):
        """部署特征到在线存储"""
        # 物化特征
        self.store.materialize_incremental(
            end_date=datetime.now()
        )
        print("Features materialized to online store")
    
    def predict(self, user_id: int) -> dict:
        """实时预测"""
        # 获取在线特征
        features = self.store.get_online_features(
            features=[
                "user_features:age",
                "user_features:income",
                "transaction_stats:last_7d_amount",
                "user_transaction_stats:avg_amount_7d"
            ],
            entity_rows=[{"user_id": user_id}]
        ).to_dict()
        
        # 模型预测
        # prediction = model.predict([features["age"], ...])
        
        return {
            "user_id": user_id,
            "features": features,
            # "prediction": prediction
        }

# 执行工作流
workflow = MLWorkflow()

# 1. 准备训练数据
train_entities = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "event_timestamp": pd.date_range("2024-01-01", periods=5),
    "label": [0, 1, 0, 1, 0]
})
train_df = workflow.prepare_training_data(train_entities)

# 2. 训练模型
X = train_df.drop(["label", "event_timestamp"], axis=1)
y = train_df["label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 3. 部署特征
workflow.deploy_features()

# 4. 实时预测
result = workflow.predict(user_id=123)
```

## 应用场景

| 场景 | 特征类型 | 存储策略 |
|------|----------|----------|
| **实时推荐** | 用户画像、物品特征 | Redis 在线 + S3 离线 |
| **反欺诈** | 交易序列、设备指纹 | 内存在线 + 时序数据库 |
| **搜索排序** | 查询特征、文档特征 | 多级缓存 |
| **定价策略** | 市场特征、竞争特征 | 混合存储 |
| **用户增长** | 行为特征、社交特征 | 批流一体 |

## 面试要点

Q: 特征存储解决了什么问题？
A: 核心问题：
   - **特征重复计算**: 不同团队重复开发相同特征
   - **训练-服务偏差**: 训练和服务时特征逻辑不一致
   - **特征发现**: 难以找到已存在的特征
   - **特征版本管理**: 特征变更追踪困难
   - **时序正确性**: 避免数据泄露

Q: Online Store 和 Offline Store 的区别？
A: 关键区别：
   - **Online**: 低延迟(ms)、小数据量、热数据、实时更新
   - **Offline**: 高吞吐、大数据量、历史数据、批量更新
   - **双写策略**: 通常离线批量计算写入离线存储，实时流写入在线存储

Q: 什么是 Point-in-time Correctness？为什么重要？
A: 含义：训练时使用的特征值必须是在预测时刻之前已知的
   重要性：防止数据泄露，确保模型评估的真实性
   实现方式：特征存储通过时序 Join 确保每个样本使用正确的历史特征值

Q: 如何处理特征缺失值？
A: 策略：
   - **在线服务**: 使用默认值、特征回填、从离线存储查询
   - **离线训练**: 中位数/均值填充、前向填充、模型预测填充
   - **特征注册**: 在特征定义中指定默认填充策略

Q: Feast 的核心组件有哪些？
A: 核心组件：
   - **Feature View**: 特征定义和元数据
   - **Entity**: 特征关联的实体
   - **Source**: 特征数据源
   - **Registry**: 特征元数据存储
   - **Online Store**: 低延迟特征读取
   - **Offline Store**: 大规模特征存储

## 相关概念

### 数据结构
- [数据仓库](../ml-fundamentals/data-processing.md) - 离线存储基础
- [Redis](../../cloud-devops/redis.md) - 在线存储常用方案
- [数据流](../ml-fundamentals/data-processing.md) - 实时特征计算

### 算法
- [特征工程](../ml-fundamentals/feature-engineering.md) - 特征构建方法
- [时序分析](../mathematics/statistics/time-series.md) - 时间窗口特征

### 复杂度分析
- **在线读取**: $O(1)$ - Hash 查询
- **批量读取**: $O(n)$ - n 为实体数量
- **离线 Join**: $O(n \log n)$ - 排序后合并
- **特征计算**: 取决于聚合复杂度

### 系统实现
- [Spark](../ml-fundamentals/distributed-ml.md) - 批量特征计算
- [Flink/Kafka](../ml-fundamentals/data-processing.md) - 流式特征
- [Kubernetes](../../cloud-devops/kubernetes/README.md) - 特征服务部署
- [模型监控](./model-monitoring.md) - 特征漂移监控
