# 向量数据库 (Vector Databases)

## 简介
**向量数据库 (Vector Database)** 是专门设计用于存储和高效检索高维向量数据的数据库系统。通过近似最近邻(ANN)算法，它能在海量向量中快速找到与查询向量最相似的向量，是RAG系统、推荐系统、图像搜索等AI应用的核心基础设施。

## 核心概念

### 1. 向量数据库 vs 传统数据库
```
┌─────────────────────────────────────────────────────────────┐
│               向量数据库 vs 传统关系型数据库                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  传统数据库                                                    │
│  ├── 查询: 精确匹配 (WHERE id = 123)                         │
│  ├── 索引: B-Tree、Hash索引                                  │
│  └── 适用: 结构化数据、事务处理                               │
│                                                             │
│  向量数据库                                                    │
│  ├── 查询: 相似度搜索 (最相似的Top-K)                         │
│  ├── 索引: HNSW、IVF、PQ等ANN索引                            │
│  └── 适用: 语义搜索、多模态检索、RAG                          │
│                                                             │
│  核心差异:                                                    │
│  传统: 精确匹配 (相等/范围/模糊)                              │
│  向量: 近似匹配 (余弦相似度/欧氏距离)                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 近似最近邻(ANN)算法
| 算法 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **Flat/暴力搜索** | 计算与所有向量的距离 | 100%召回 | O(n)复杂度，慢 |
| **IVF (倒排文件)** | 聚类后搜索最近簇 | 速度快 | 召回率中等 |
| **HNSW (分层导航小世界)** | 多层图结构 | 速度快、召回高 | 内存占用大 |
| **PQ (乘积量化)** | 向量压缩编码 | 内存省 | 精度损失 |
| **LSH (局部敏感哈希)** | 哈希桶分桶 | 理论保证 | 高维效果差 |

### 3. HNSW算法详解
```
HNSW (Hierarchical Navurable Small World)

结构:
Layer 2:      ●───────●              (稀疏层 - 长连接)
             /         \
Layer 1:   ●───●───●───●───●        (中等密度)
           │   │   │   │   │
Layer 0: ●─●─●─●─●─●─●─●─●─●─●─●   (密集层 - 所有节点)

搜索过程:
1. 从顶层随机节点开始
2. 在当前层贪婪搜索最近邻
3. 找到最近点后下降到下一层
4. 重复直到最底层
5. 在底层精确搜索Top-K

时间复杂度: O(log n)
空间复杂度: O(n × M)  M为每个节点的连接数
```

### 4. 主流向量数据库对比
| 特性 | Pinecone | Milvus | Chroma | Qdrant | Weaviate | pgvector |
|------|----------|--------|--------|--------|----------|----------|
| 部署 | 托管SaaS | 自托管/K8s | 轻量本地 | 自托管 | 自托管/云 | PostgreSQL扩展 |
| 规模 | 海量 | 超大规模 | 中小规模 | 中大规模 | 中大规模 | 中等规模 |
| 特性 | 简单 | 功能最全 | 易用 | 高性能 | GraphQL | SQL兼容 |
| 适用 | 快速启动 | 生产级 | 原型开发 | 高性能需求 | 复杂查询 | 已有PG环境 |

## 实现方式

```python
# 向量数据库使用示例 - 多平台对比
import numpy as np


class VectorDBDemo:
    """向量数据库使用演示"""
    
    @staticmethod
    def chroma_example():
        """Chroma - 轻量级本地向量库"""
        import chromadb
        from sentence_transformers import SentenceTransformer
        
        # 初始化
        client = chromadb.Client()
        collection = client.create_collection("documents")
        
        # 嵌入模型
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 添加数据
        texts = [
            "机器学习是人工智能的一个分支",
            "深度学习使用神经网络",
            "Python是流行的编程语言"
        ]
        embeddings = model.encode(texts)
        
        collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            ids=["doc1", "doc2", "doc3"],
            metadatas=[{"category": "AI"}, {"category": "AI"}, {"category": "programming"}]
        )
        
        # 搜索
        query_embedding = model.encode(["神经网络学习"])
        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=2,
            where={"category": "AI"}  # 元数据过滤
        )
        
        return results
    
    @staticmethod
    def milvus_example():
        """Milvus - 生产级向量数据库"""
        from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
        
        # 连接
        connections.connect("default", host="localhost", port="19530")
        
        # 定义schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
        ]
        schema = CollectionSchema(fields, "Document collection")
        
        # 创建集合
        collection = Collection("documents", schema)
        
        # 创建索引
        index_params = {
            "metric_type": "L2",  # 欧氏距离
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 200}
        }
        collection.create_index("embedding", index_params)
        
        # 插入数据
        entities = [
            [1, 2, 3],  # id
            np.random.randn(3, 768).tolist(),  # embeddings
            ["text1", "text2", "text3"]  # text
        ]
        collection.insert(entities)
        collection.flush()
        
        # 加载并搜索
        collection.load()
        search_params = {"metric_type": "L2", "params": {"ef": 64}}
        results = collection.search(
            data=[np.random.randn(768).tolist()],
            anns_field="embedding",
            param=search_params,
            limit=3
        )
        
        return results
    
    @staticmethod
    def qdrant_example():
        """Qdrant - 高性能Rust实现"""
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
        
        client = QdrantClient(host="localhost", port=6333)
        
        # 创建集合
        client.create_collection(
            collection_name="documents",
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
        
        # 插入点
        points = [
            PointStruct(
                id=1,
                vector=np.random.randn(768).tolist(),
                payload={"text": "document 1", "category": "tech"}
            ),
            PointStruct(
                id=2,
                vector=np.random.randn(768).tolist(),
                payload={"text": "document 2", "category": "science"}
            )
        ]
        client.upsert(collection_name="documents", points=points)
        
        # 搜索 + 过滤
        results = client.search(
            collection_name="documents",
            query_vector=np.random.randn(768).tolist(),
            query_filter={
                "must": [{"key": "category", "match": {"value": "tech"}}]
            },
            limit=5
        )
        
        return results
    
    @staticmethod
    def pgvector_example():
        """pgvector - PostgreSQL扩展"""
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            database="vectordb",
            user="user",
            password="password"
        )
        
        with conn.cursor() as cur:
            # 启用扩展
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # 创建表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector(768)
                )
            """)
            
            # 创建HNSW索引
            cur.execute("""
                CREATE INDEX ON documents 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)
            
            # 插入
            embedding = np.random.randn(768)
            cur.execute(
                "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
                ("Sample document", embedding.tolist())
            )
            
            # 相似度搜索
            cur.execute("""
                SELECT content, embedding <=> %s as distance
                FROM documents
                ORDER BY embedding <=> %s
                LIMIT 5
            """, (embedding.tolist(), embedding.tolist()))
            
            results = cur.fetchall()
        
        conn.commit()
        return results


# 向量数据库设计最佳实践
class VectorDBDesign:
    """向量数据库设计指南"""
    
    @staticmethod
    def embedding_dimension_guide():
        """嵌入维度选择"""
        return {
            "OpenAI text-embedding-3-small": 1536,
            "OpenAI text-embedding-3-large": 3072,
            "BGE-Large": 1024,
            "Sentence-T5": 768,
            "M3E-Base": 768,
            "CLIP": 512,  # 多模态
        }
    
    @staticmethod
    def index_config_guide():
        """索引配置建议"""
        return {
            "小规模 (<1M)": {
                "index": "FLAT",  # 暴力搜索
                "reason": "数据量少，精确搜索足够快"
            },
            "中规模 (1M-10M)": {
                "index": "HNSW",
                "M": 16,
                "efConstruction": 200,
                "ef": 128,
                "reason": "平衡速度和召回"
            },
            "大规模 (>10M)": {
                "index": "IVF_HNSW",  # 或IVF_PQ
                "nlist": 4096,
                "M": 16,
                "reason": "降低内存，提高吞吐量"
            }
        }
    
    @staticmethod
    def partitioning_strategy():
        """分区策略"""
        return """
        按业务分区:
        - 用户ID哈希分区: 隔离用户数据
        - 时间分区: 按月份/年份分表
        - 类别分区: 不同业务线独立集合
        
        好处:
        - 提高查询效率
        - 方便数据管理
        - 支持冷热分离
        """


# 性能优化示例
class VectorDBOptimization:
    """向量数据库性能优化"""
    
    @staticmethod
    def hybrid_search(query_vector, query_text, alpha=0.7):
        """混合搜索: 向量相似度 + 关键词匹配"""
        # 向量检索Top-K
        vector_results = vector_search(query_vector, k=100)
        
        # BM25关键词检索
        keyword_results = bm25_search(query_text, k=100)
        
        # RRF融合
        scores = {}
        for rank, doc in enumerate(vector_results):
            scores[doc.id] = scores.get(doc.id, 0) + alpha / (rank + 60)
        
        for rank, doc in enumerate(keyword_results):
            scores[doc.id] = scores.get(doc.id, 0) + (1-alpha) / (rank + 60)
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    
    @staticmethod
    def quantization_benchmark():
        """量化效果基准"""
        return """
        量化类型对比:
        
        FP32 (原始): 100% 精度, 4字节/维度
        FP16: ~99% 精度, 2字节/维度, 50%存储
        INT8: ~95% 精度, 1字节/维度, 75%存储
        PQ (乘积量化): ~90% 精度, 0.25字节/维度, 93%存储
        
        推荐:
        - 内存敏感: PQ + IVF
        - 精度优先: FP16 + HNSW
        - 平衡方案: INT8 + HNSW
        """
```

## 应用场景

- **RAG系统**: 语义检索外部知识库
- **推荐系统**: 基于用户/物品向量相似度推荐
- **图像搜索**: 以图搜图、多模态检索
- **异常检测**: 发现与正常模式偏离的向量
- **去重系统**: 相似内容检测与去重
- **多语言搜索**: 跨语言语义匹配

## 面试要点

1. **Q: HNSW为什么比暴力搜索快?时间复杂度是多少?**  
   A: HNSW通过多层图结构实现近似O(log n)搜索。顶层稀疏图快速定位大致区域，逐层下沉精确搜索，避免扫描全部向量。

2. **Q: 余弦相似度和欧氏距离在什么情况下等价?**  
   A: 当向量被归一化为单位长度时，余弦相似度和欧氏距离单调相关。此时最小化欧氏距离等价于最大化余弦相似度。

3. **Q: 向量数据库如何处理数据更新(增删改)?**  
   A: 新增直接插入；删除通常标记软删除或重建索引；修改=删除+新增。部分数据库支持增量索引更新，但大规模修改建议重建索引。

4. **Q: 如何选择向量数据库?**  
   A: 考虑: 1) 数据规模 2) 延迟要求 3) 团队技术栈 4) 部署环境 5) 预算。小规模用Chroma，生产级用Milvus/Qdrant，已有PG用pgvector。

5. **Q: 向量量化(PQ)的原理和权衡?**  
   A: PQ将高维向量分割为子向量，对每个子空间聚类编码。用聚类中心近似原向量，大幅降低存储(至1/4~1/32)，但损失部分精度。

## 相关概念

### AI & Data Systems
- [RAG架构](./rag-architecture.md) - 向量数据库的核心应用
- [Embedding模型](./embedding-models.md) - 向量生成
- [向量数据库概览](../vector-db.md) - 项目已有向量DB内容

### 系统实现
- [B-Tree索引](../../references/indexing.md) - 索引原理基础
- [数据库系统](../../computer-science/systems/file-systems.md) - 存储系统基础
- [分布式系统](../../computer-science/networks/network-layer.md) - 分布式向量库
