# Embedding模型 (Embedding Models)

## 简介
**Embedding模型**是将文本、图像等非结构化数据转换为固定维度稠密向量的模型，使得语义相似的数据在向量空间中距离相近。它是现代NLP和RAG系统的基石，决定了语义检索的质量上限。

## 核心概念

### 1. Embedding基本原理
```
┌─────────────────────────────────────────────────────────────┐
│                   Embedding原理示意                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  文本空间                    向量空间 (高维)                   │
│                                                             │
│  "机器学习"  ──Embedding──>  [0.23, -0.45, 0.89, ...]       │
│       ↓                                                      │
│  "Machine Learning" ──->    [0.25, -0.43, 0.87, ...]  ←相近  │
│       ↓                                                      │
│  "深度学习"  ──Embedding──>  [0.31, -0.38, 0.82, ...]  ←相近  │
│       ↓                                                      │
│  "苹果派"    ──Embedding──>  [-0.12, 0.67, -0.23, ...] ←远离  │
│                                                             │
│  语义相似 → 向量距离小 (余弦相似度高)                         │
│  语义无关 → 向量距离大                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Embedding模型架构演进
| 模型 | 架构 | 特点 | 适用场景 |
|------|------|------|----------|
| **Word2Vec** | 浅层神经网络 | 静态词向量，无上下文 | 传统NLP、资源受限 |
| **GloVe** | 共现矩阵分解 | 结合全局统计信息 | 词级别分析 |
| **ELMo** | 双向LSTM | 动态上下文表示 | 早期上下文嵌入 |
| **BERT** | Transformer Encoder | 双向上下文，句向量 | 理解任务 |
| **Sentence-BERT** | Siamese BERT | 专门为句子相似度优化 | 语义搜索 |
| **OpenAI Embedding** | Transformer | API服务，效果好 | 通用场景 |
| **E5/BGE** | 现代Encoder | 开源SOTA，多语言 | 生产环境 |

### 3. 嵌入模型选择维度
```
选择维度:

1. 语言支持
   - 英文: OpenAI, E5, GTE
   - 中文: BGE, M3E, BCE
   - 多语言: LaBSE, Multilingual-E5

2. 向量维度
   - 小维度(256-512): 资源受限，速度快
   - 中等(768-1024): 平衡选择
   - 大维度(1536-4096): 精度优先

3. 上下文长度
   - 512 tokens: 短文本
   - 2048 tokens: 中等文档
   - 8192+ tokens: 长文档

4. 使用方式
   - API服务: OpenAI, Cohere
   - 开源本地: BGE, E5
   - 自训练: 领域数据微调
```

### 4. 相似度度量方法
| 度量 | 公式 | 适用场景 |
|------|------|----------|
| 余弦相似度 | cos(θ) = A·B/(\|A\|\|B\|) | 方向相似性，最常用 |
| 欧氏距离 | \|A-B\| | 绝对距离，配合归一化 |
| 点积 | A·B | 快速计算，需归一化 |
| 曼哈顿距离 | Σ\|Ai-Bi\| | 稀疏向量 |

## 实现方式

```python
# Embedding模型使用实践
import numpy as np
from typing import List, Union
import torch


class EmbeddingService:
    """Embedding模型服务封装"""
    
    def __init__(self, model_name: str = "BAAI/bge-large-zh-v1.5"):
        """
        支持模型:
        - BAAI/bge-large-zh-v1.5 (中文SOTA)
        - BAAI/bge-large-en-v1.5 (英文SOTA)
        - sentence-transformers/all-MiniLM-L6-v2 (轻量)
        - thenlper/gte-large (高性能)
        """
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
    def encode(
        self, 
        texts: Union[str, List[str]], 
        normalize: bool = True,
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """编码文本为向量"""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        if normalize:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings
    
    def similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        embeddings = self.encode([text1, text2])
        return float(np.dot(embeddings[0], embeddings[1]))
    
    def batch_similarity(
        self, 
        queries: List[str], 
        candidates: List[str]
    ) -> np.ndarray:
        """批量计算相似度矩阵"""
        query_emb = self.encode(queries)
        cand_emb = self.encode(candidates)
        return query_emb @ cand_emb.T


class OpenAIEmbedding:
    """OpenAI Embedding API封装"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """调用OpenAI API获取embedding"""
        if isinstance(texts, str):
            texts = [texts]
        
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        
        return [item.embedding for item in response.data]


class MultilingualEmbedding:
    """多语言Embedding处理"""
    
    def __init__(self):
        # LaBSE: Language-agnostic BERT Sentence Embedding
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer('sentence-transformers/LaBSE')
        
    def cross_lingual_similarity(
        self, 
        text_zh: str, 
        text_en: str
    ) -> float:
        """计算跨语言相似度"""
        embeddings = self.model.encode([text_zh, text_en])
        return float(np.dot(embeddings[0], embeddings[1]))


# 领域自适应微调
class DomainAdaptiveEmbedding:
    """领域自适应Embedding训练"""
    
    def __init__(self, base_model: str):
        from sentence_transformers import SentenceTransformer, InputExample
        from torch.utils.data import DataLoader
        self.model = SentenceTransformer(base_model)
        self.InputExample = InputExample
        self.DataLoader = DataLoader
        
    def prepare_training_data(self, pairs: List[dict]) -> List:
        """准备训练数据
        
        pairs格式: [
            {"sentence1": "...", "sentence2": "...", "label": 0.8},
            ...
        ]
        """
        examples = []
        for pair in pairs:
            examples.append(self.InputExample(
                texts=[pair["sentence1"], pair["sentence2"]],
                label=float(pair["label"])
            ))
        return examples
    
    def train(
        self,
        train_examples: List,
        output_path: str,
        epochs: int = 3,
        batch_size: int = 16
    ):
        """微调模型"""
        from sentence_transformers import losses
        
        train_dataloader = self.DataLoader(
            train_examples, 
            shuffle=True, 
            batch_size=batch_size
        )
        
        train_loss = losses.CosineSimilarityLoss(self.model)
        
        self.model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=epochs,
            warmup_steps=100,
            output_path=output_path
        )


# Embedding质量评估
class EmbeddingEvaluator:
    """Embedding模型评估"""
    
    @staticmethod
    def evaluate_retrieval(
        model,
        queries: List[str],
        corpus: List[str],
        relevant_docs: List[List[int]]
    ) -> dict:
        """评估检索性能"""
        # 编码
        query_emb = model.encode(queries)
        corpus_emb = model.encode(corpus)
        
        # 相似度矩阵
        similarity = query_emb @ corpus_emb.T
        
        # 计算MRR和Recall@K
        mrr_sum = 0
        recall_at_1 = 0
        recall_at_5 = 0
        recall_at_10 = 0
        
        for i, rel_docs in enumerate(relevant_docs):
            scores = similarity[i]
            ranked_indices = np.argsort(scores)[::-1]
            
            # MRR
            for rank, idx in enumerate(ranked_indices):
                if idx in rel_docs:
                    mrr_sum += 1 / (rank + 1)
                    break
            
            # Recall@K
            top_1 = set(ranked_indices[:1])
            top_5 = set(ranked_indices[:5])
            top_10 = set(ranked_indices[:10])
            
            recall_at_1 += len(top_1 & set(rel_docs)) > 0
            recall_at_5 += len(top_5 & set(rel_docs)) / len(rel_docs)
            recall_at_10 += len(top_10 & set(rel_docs)) / len(rel_docs)
        
        n = len(queries)
        return {
            "MRR": mrr_sum / n,
            "Recall@1": recall_at_1 / n,
            "Recall@5": recall_at_5 / n,
            "Recall@10": recall_at_10 / n
        }
    
    @staticmethod
    def evaluate_classification(
        model,
        texts: List[str],
        labels: List[int]
    ) -> dict:
        """评估分类性能（使用KNN）"""
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.model_selection import cross_val_score
        
        embeddings = model.encode(texts)
        
        knn = KNeighborsClassifier(n_neighbors=5, metric='cosine')
        scores = cross_val_score(knn, embeddings, labels, cv=5)
        
        return {
            "accuracy_mean": scores.mean(),
            "accuracy_std": scores.std()
        }


# 生产优化
class EmbeddingOptimizer:
    """Embedding推理优化"""
    
    @staticmethod
    def onnx_export(model, output_path: str):
        """导出ONNX格式加速推理"""
        # 使用optimum库导出ONNX
        from optimum.onnxruntime import ORTModelForFeatureExtraction
        
        model.save_pretrained(output_path)
        # 自动转换为ONNX格式
        
    @staticmethod
    def quantize_embeddings(embeddings: np.ndarray, bits: int = 8) -> np.ndarray:
        """量化embedding减少存储"""
        if bits == 8:
            # INT8量化
            min_val = embeddings.min()
            max_val = embeddings.max()
            scale = (max_val - min_val) / 255
            quantized = ((embeddings - min_val) / scale).astype(np.uint8)
            return quantized, (min_val, scale)  # 返回量化参数用于反量化
        
        elif bits == 1:
            # 二进制量化 (签名)
            return np.where(embeddings >= 0, 1, 0).astype(np.int8)
        
        return embeddings
    
    @staticmethod
    def binary_similarity(query: np.ndarray, corpus: np.ndarray) -> np.ndarray:
        """汉明距离快速相似度 (二进制embedding)"""
        # 使用XOR和popcount快速计算
        xor_result = np.bitwise_xor(query, corpus)
        # 计算1的个数
        hamming_dist = np.unpackbits(xor_result).sum(axis=-1)
        return 1 - hamming_dist / query.shape[-1] / 8


# 常见模型对比
EMBEDDING_MODELS_COMPARISON = """
模型对比 (Massive Text Embedding Benchmark - MTEB):

英文模型:
| 模型 | 维度 | 平均得分 | 速度 | 开源 |
|------|------|----------|------|------|
| text-embedding-3-large | 3072 | 64.6 | API | 否 |
| gte-large | 1024 | 63.1 | 快 | 是 |
| e5-large-v2 | 1024 | 62.2 | 快 | 是 |
| bge-large-en-v1.5 | 1024 | 64.2 | 快 | 是 |
| all-MiniLM-L6-v2 | 384 | 56.3 | 很快 | 是 |

中文模型:
| 模型 | 维度 | 特点 |
|------|------|------|
| bge-large-zh-v1.5 | 1024 | 中文SOTA |
| m3e-base | 768 | 轻量高效 |
| bce-embedding-base | 768 | 中英双优 |
| piccolo-base-zh | 512 | 中文优化 |
"""
```

## 应用场景

- **语义搜索**: 基于意思而非关键词的文档检索
- **RAG系统**: 为检索组件提供语义编码
- **推荐系统**: 用户/物品兴趣向量化匹配
- **聚类分析**: 文本自动分类与主题发现
- **去重检测**: 相似内容识别
- **零样本分类**: 无需训练的文本分类

## 面试要点

1. **Q: BERT和Sentence-BERT生成embedding的区别?**  
   A: BERT输出token级向量，需池化(pooling)得句向量，且原生不适合语义相似度。Sentence-BERT使用孪生网络，直接用对比学习优化句子相似度。

2. **Q: 为什么Embedding需要归一化?**  
   A: 归一化后向量长度为1，点积等价于余弦相似度，简化计算且使相似度有界[-1,1]。同时避免长文本因向量长度大而误判为高相似度。

3. **Q: 如何选择embedding维度?维度越高越好吗?**  
   A: 不是。更高维度有更多表达能力，但增加存储和计算成本。实践中768-1024维通常足够，边际收益随维度增加递减。

4. **Q: 领域数据如何微调embedding模型?**  
   A: 1) 准备领域内的相似/不相似文本对 2) 使用对比学习(SimCSE)或有监督学习 3) 在领域测试集评估 4) 冻结部分层减少过拟合。

5. **Q: Embedding模型的bias问题如何处理?**  
   A: Embedding可能继承训练数据的偏见(如性别-职业关联)。处理：1) 去偏训练数据 2) 后处理去偏算法 3) 多维度评估 4) 应用场景警示。

## 相关概念

### AI & Data Systems
- [向量数据库](./vector-databases.md) - Embedding的存储和检索
- [RAG架构](./rag-architecture.md) - Embedding的核心应用场景
- [Transformer](../transformers.md) - Embedding模型的架构基础

### 系统实现
- [矩阵运算](../../mathematics/linear-algebra/matrix-operations.md) - Embedding计算的数学基础
- [向量空间](../../mathematics/linear-algebra/vector-spaces.md) - Embedding的几何解释
- [缓存策略](../../computer-science/systems/cache.md) - Embedding结果缓存
