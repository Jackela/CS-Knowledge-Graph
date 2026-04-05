# RAG架构 (Retrieval-Augmented Generation Architecture)

## 简介
**RAG (Retrieval-Augmented Generation)** 是一种将信息检索与大语言模型生成能力结合的架构，通过检索外部知识库中的相关信息来增强模型回答的准确性和时效性，有效缓解大模型的幻觉问题。

## 核心概念

### 1. RAG架构演进
```
┌─────────────────────────────────────────────────────────────┐
│                   RAG架构演进                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Naive RAG (基础RAG)                                         │
│  查询 → 检索 → 生成                                          │
│  问题: 检索质量依赖查询表述，单次检索可能遗漏关键信息          │
│                                                             │
│  Advanced RAG (高级RAG)                                      │
│  ├── 查询重写/扩展: 优化检索query                            │
│  ├── 混合检索: 向量检索 + 关键词检索                         │
│  ├── 重排序(Rerank): 精排检索结果                            │
│  └── 上下文压缩: 精简上下文，减少噪声                        │
│                                                             │
│  Modular RAG (模块化RAG)                                     │
│  ├── 多路检索: 多个数据源并行检索                            │
│  ├── 主动检索: 根据中间结果决定是否需要再次检索              │
│  ├── 图RAG: 知识图谱增强检索                                 │
│  └── Agentic RAG: Agent自主决定检索策略                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 核心组件
| 组件 | 功能 | 技术要点 |
|------|------|----------|
| 文档处理 | 原始文档切分、清洗 | Chunk策略、重叠窗口、元数据保留 |
| 嵌入模型 | 文本向量化 | Embedding模型选择、维度、量化 |
| 向量存储 | 高效相似度检索 | 索引类型、近似最近邻、过滤 |
| 检索器 | 获取相关文档 | Top-K选择、混合检索、重排序 |
| 重排序器 | 精排检索结果 | Cross-encoder、ColBERT |
| 生成器 | 基于上下文生成回答 | Prompt工程、上下文压缩 |

### 3. Chunk策略对比
```
策略1: 固定长度切分
- 每500字符切分
- 优点: 简单、均匀
- 缺点: 可能切断语义

策略2: 语义切分
- 按句子/段落边界
- 优点: 语义完整
- 缺点: 长度不均

策略3: 层次切分
- 父chunk(大粒度) + 子chunk(小粒度)
- 检索子chunk，返回父chunk上下文
- 优点: 平衡精度和召回

策略4: 智能切分
- 使用LLM分析文档结构
- 按主题/章节切分
- 优点: 结构清晰
- 缺点: 成本高
```

## 实现方式

```python
# RAG系统完整实现
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader


class DocumentProcessor:
    """文档处理: 加载、切分、向量化"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
        
    def process_documents(self, file_paths: List[str]) -> List[Dict]:
        """处理文档并返回chunks"""
        all_chunks = []
        
        for path in file_paths:
            loader = TextLoader(path)
            documents = loader.load()
            
            chunks = self.splitter.split_documents(documents)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "id": f"{path}_{i}",
                    "content": chunk.page_content,
                    "metadata": {
                        "source": path,
                        "chunk_index": i,
                        **chunk.metadata
                    }
                })
        
        return all_chunks


class VectorStore:
    """向量存储与检索"""
    
    def __init__(self, collection_name: str = "documents"):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
        
    def add_documents(self, chunks: List[Dict]):
        """添加文档到向量库"""
        texts = [c["content"] for c in chunks]
        embeddings = self.embedding_model.encode(texts).tolist()
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=[c["metadata"] for c in chunks],
            ids=[c["id"] for c in chunks]
        )
        
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """向量检索"""
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        return [
            {
                "content": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]


class Reranker:
    """重排序: 提升检索精度"""
    
    def __init__(self):
        # 使用Cross-encoder进行重排序
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder('BAAI/bge-reranker-large')
        
    def rerank(self, query: str, documents: List[Dict], top_n: int = 3) -> List[Dict]:
        """对检索结果重排序"""
        pairs = [[query, doc["content"]] for doc in documents]
        scores = self.model.predict(pairs)
        
        # 按分数排序
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {**doc, "rerank_score": float(score)}
            for doc, score in scored_docs[:top_n]
        ]


class RAGPipeline:
    """完整RAG流程"""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.reranker = Reranker()
        self.llm = None  # 接入LLM API
        
    def index_documents(self, file_paths: List[str]):
        """索引文档"""
        chunks = self.doc_processor.process_documents(file_paths)
        self.vector_store.add_documents(chunks)
        print(f"Indexed {len(chunks)} chunks from {len(file_paths)} documents")
        
    def query(self, question: str, use_rerank: bool = True) -> Dict:
        """执行RAG查询"""
        # 1. 检索
        initial_results = self.vector_store.search(question, top_k=10)
        
        # 2. 重排序
        if use_rerank:
            retrieved_docs = self.reranker.rerank(question, initial_results, top_n=5)
        else:
            retrieved_docs = initial_results[:5]
        
        # 3. 构建上下文
        context = self._build_context(retrieved_docs)
        
        # 4. 生成回答
        answer = self._generate(question, context, retrieved_docs)
        
        return {
            "question": question,
            "answer": answer,
            "sources": [d["metadata"]["source"] for d in retrieved_docs],
            "context": context
        }
        
    def _build_context(self, documents: List[Dict]) -> str:
        """构建上下文字符串"""
        contexts = []
        for i, doc in enumerate(documents):
            contexts.append(f"[Document {i+1}]\n{doc['content']}\n")
        return "\n".join(contexts)
        
    def _generate(self, question: str, context: str, sources: List[Dict]) -> str:
        """调用LLM生成回答"""
        prompt = f"""基于以下参考文档回答问题。如果文档中没有相关信息，请明确说明。

参考文档：
{context}

问题：{question}

请提供详细、准确的回答，并在回答末尾列出参考的文档编号。"""
        
        # 调用LLM API
        # return self.llm.generate(prompt)
        return "[LLM生成的回答...]"


# 高级RAG: 查询重写
class QueryRewriter:
    """查询优化与扩展"""
    
    def __init__(self, llm):
        self.llm = llm
        
    def rewrite(self, query: str, strategy: str = "expansion") -> List[str]:
        """重写查询"""
        if strategy == "expansion":
            # 生成多个相关查询
            prompt = f"""生成3个与以下问题相关的查询，帮助更全面检索信息：
问题：{query}

相关查询："""
            response = self.llm.generate(prompt)
            queries = [q.strip() for q in response.split("\n") if q.strip()]
            return [query] + queries
            
        elif strategy == "hyde":
            # HyDE: 生成假设性回答再嵌入
            prompt = f"""基于问题生成一个假设性回答（不需要准确）：
问题：{query}

假设性回答："""
            hypothetical_answer = self.llm.generate(prompt)
            return [hypothetical_answer]
            
        return [query]


# 混合检索
class HybridRetriever:
    """向量检索 + BM25关键词检索"""
    
    def __init__(self, vector_store, documents: List[str]):
        self.vector_store = vector_store
        
        # 初始化BM25
        from rank_bm25 import BM25Okapi
        tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        self.documents = documents
        
    def search(self, query: str, top_k: int = 5, alpha: float = 0.5) -> List[Dict]:
        """混合检索并融合结果"""
        # 向量检索
        vector_results = self.vector_store.search(query, top_k=top_k*2)
        
        # BM25检索
        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_top_indices = np.argsort(bm25_scores)[-top_k*2:][::-1]
        
        # 结果融合 (RRF - Reciprocal Rank Fusion)
        scores = {}
        
        # 向量检索得分
        for rank, result in enumerate(vector_results):
            doc_id = result["metadata"]["source"]
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + 60)
            
        # BM25得分
        for rank, idx in enumerate(bm25_top_indices):
            doc_id = f"doc_{idx}"
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + 60)
        
        # 排序返回
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_docs[:top_k]
```

## 应用场景

- **企业知识库**: 内部文档问答、政策查询、技术支持
- **客服系统**: 基于产品手册的自动问答
- **法律咨询**: 法规检索与案例分析
- **医疗诊断**: 医学文献检索与辅助诊断
- **代码助手**: 基于代码库的上下文感知编程帮助

## 面试要点

1. **Q: RAG如何解决大模型的幻觉问题?**  
   A: RAG通过检索外部知识作为生成依据，将回答锚定在真实文档上。即使模型本身知识过时或不准确，也能基于检索到的真实内容生成回答。

2. **Q: Chunk大小如何选择?有什么权衡?**  
   A: 小chunk(100-200)精度高但可能丢失上下文；大chunk(1000+)上下文完整但可能引入噪声。通常用重叠窗口(20%)和层次chunk策略平衡。

3. **Q: 向量检索和关键词检索(BM25)如何选择?**  
   A: 向量检索擅长语义匹配(同义词、概念相关)，BM25擅长精确匹配(专有名词、ID)。实际常使用混合检索+RRF融合获得最佳效果。

4. **Q: 重排序(Rerank)的作用是什么?**  
   A: 向量检索使用bi-encoder快速召回候选，但精度有限。重排序用cross-encoder精确计算查询-文档相关性，通常能显著提升Top-K准确率。

5. **Q: 如何评估RAG系统效果?**  
   A: 1) 检索评估: Recall@K、MRR、NDCG 2) 生成评估: 回答相关性、忠实度、完整性 3) 端到端: 人工评估、A/B测试 4) 使用RAGAS等专门评估框架。

## 相关概念

### AI & Data Systems
- [向量数据库](./vector-databases.md) - RAG的检索基础设施
- [Embedding模型](./embedding-models.md) - 语义向量化
- [提示工程](./prompt-engineering.md) - RAG的Prompt设计
- [大语言模型](../llm.md) - RAG的生成组件

### 系统实现
- [数据库索引](../../computer-science/systems/file-systems.md) - 索引原理基础
- [缓存策略](../../computer-science/systems/cache.md) - 检索结果缓存
- [API设计](../../computer-science/networks/http-protocol.md) - RAG服务接口
