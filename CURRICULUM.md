# CS Knowledge Graph - Complete Curriculum Outline

> Comprehensive curriculum covering ALL computer science concepts, algorithms, and knowledge for graduate level and below.

## 📊 Curriculum Overview

### Core Areas (7 Major Domains)
1. **Computer Science Fundamentals** - Data Structures, Algorithms, Systems
2. **Software Engineering** - Design Patterns, Architecture, Testing
3. **Cloud & DevOps** - Infrastructure, CI/CD, Monitoring
4. **AI & Data Systems** - ML, LLM, RAG, Vector DBs
5. **Mathematics** - Linear Algebra, Probability, Graph Theory
6. **Security** - Cryptography, Network Security, Application Security
7. **Product Management** - BRD/PRD, Agile, Market Analysis

---

## 1️⃣ Computer Science Fundamentals

### 1.1 Data Structures (15+ topics)
**Basic Structures:**
- [x] Array - 连续内存存储，随机访问 O(1)
- [x] Linked List - 指针链式结构，动态扩容
- [x] Stack - LIFO，函数调用栈
- [x] Queue - FIFO，BFS基础
- [x] Hash Table - 散列映射，冲突解决

**Tree Structures:**
- [x] Binary Tree - 二叉树基础
- [x] BST (Binary Search Tree) - 二叉搜索树
- [x] AVL Tree - 自平衡二叉树
- [x] Red-Black Tree - 红黑树
- [x] B-Tree / B+ Tree - 多路平衡树，数据库索引
- [x] Trie - 前缀树，字符串检索
- [x] Segment Tree - 线段树，区间查询
- [x] Fenwick Tree (BIT) - 树状数组

**Advanced Structures:**
- [x] Heap / Priority Queue - 堆，优先队列
- [x] Graph - 图表示，邻接矩阵/表
- [x] Disjoint Set (Union-Find) - 并查集
- [x] Skip List - 跳表
- [x] Splay Tree - 伸展树

### 1.2 Algorithms (20+ topics)
**Sorting:**
- [x] Comparison Sorts: Quick Sort, Merge Sort, Heap Sort
- [x] Linear Sorts: Counting Sort, Radix Sort, Bucket Sort
- [x] Selection Algorithms: Quick Select, Median of Medians

**Searching:**
- [x] Binary Search - 二分查找及变种
- [ ] Interpolation Search - 插值查找
- [ ] Exponential Search - 指数搜索

**Graph Algorithms:**
- [x] Graph Traversal: BFS, DFS
- [x] Shortest Path: Dijkstra, Bellman-Ford, Floyd-Warshall
- [x] Minimum Spanning Tree: Prim, Kruskal
- [x] Topological Sort - 拓扑排序
- [x] Strongly Connected Components: Kosaraju, Tarjan
- [x] Network Flow: Ford-Fulkerson, Edmonds-Karp, Dinic
- [ ] Bipartite Matching: Hungarian Algorithm

**Dynamic Programming:**
- [x] DP Fundamentals - 状态定义、转移方程
- [x] Classic DP Problems
- [x] DP Optimization: Space Optimization, Monotone Queue
- [ ] Digit DP, State Compression DP

**String Algorithms:**
- [x] String Matching: KMP, Rabin-Karp
- [x] Suffix Array / Suffix Tree
- [ ] Manacher's Algorithm - 回文串
- [ ] Z-Algorithm

**Other Paradigms:**
- [x] Greedy Algorithms - 贪心策略
- [x] Divide and Conquer - 分治法
- [x] Recursion and Backtracking - 递归与回溯
- [ ] Branch and Bound - 分支限界

**Advanced Algorithms:**
- [x] Computational Geometry: Convex Hull, Line Intersection
- [x] Number Theory: GCD, LCM, Prime Sieve, Modular Arithmetic
- [x] Matrix Exponentiation

### 1.3 Systems (25+ topics)
**Operating Systems:**
- [x] Process Management - 进程概念、状态转换
- [x] Thread Management - 线程、线程池
- [x] Scheduling Algorithms - 调度算法
- [x] Synchronization - 同步机制
- [x] Deadlock - 死锁预防、检测、避免
- [x] Memory Management - 内存分配
- [x] Virtual Memory - 虚拟内存、页表
- [x] File Systems - 文件系统

**Computer Networks:**
- [x] Network Layer - IP, ICMP, Routing
- [x] Transport Layer - TCP, UDP
- [x] Application Layer - HTTP/HTTPS, DNS
- [x] TLS/SSL - 握手过程、证书
- [x] Congestion Control - 拥塞控制算法
- [x] Network Security - 防火墙、NAT

**Databases:**
- [x] Relational Model - 关系模型
- [x] Normalization - 范式理论
- [x] Indexing - B+树索引、哈希索引
- [x] SQL Advanced - 复杂查询、优化
- [x] Concurrency Control - 并发控制、事务隔离
- [x] Query Optimization - 查询优化器
- [x] Database Architecture - 存储引擎

**Distributed Systems:**
- [x] Distributed Transactions - 分布式事务
- [x] Sharding - 数据分片
- [x] Load Balancing - 负载均衡
- [x] Consensus Algorithms - Raft, Paxos
- [x] CAP Theorem - CAP理论
- [x] Distributed Caching - 分布式缓存
- [x] Message Queues - Kafka, RabbitMQ

**Computer Architecture:**
- [x] CPU Architecture - 指令集、流水线
- [x] Memory Hierarchy - 缓存层次
- [x] Cache Coherence - 缓存一致性
- [x] Pipelining - 指令流水线
- [x] I/O Systems - 输入输出系统

**Compilers:**
- [x] Lexical Analysis - 词法分析
- [x] Parsing - 语法分析
- [x] Semantic Analysis - 语义分析
- [x] Code Generation - 代码生成
- [x] Optimization - 编译优化

---

## 2️⃣ Software Engineering

### 2.1 Design Patterns (15+ topics)
**Creational:**
- [x] Singleton - 单例模式
- [x] Factory / Abstract Factory - 工厂模式
- [x] Builder - 建造者模式
- [x] Prototype - 原型模式

**Structural:**
- [x] Adapter - 适配器模式
- [x] Bridge - 桥接模式
- [x] Composite - 组合模式
- [x] Decorator - 装饰器模式
- [x] Facade - 外观模式
- [x] Flyweight - 享元模式
- [x] Proxy - 代理模式

**Behavioral:**
- [x] Observer - 观察者模式
- [x] Strategy - 策略模式
- [x] Command - 命令模式
- [x] State - 状态模式
- [x] Template Method - 模板方法
- [x] Iterator - 迭代器模式

### 2.2 Software Architecture (10+ topics)
- [x] Monolithic Architecture - 单体架构
- [x] Microservices - 微服务架构
- [x] Event-Driven Architecture - 事件驱动
- [x] Layered Architecture - 分层架构
- [x] Clean Architecture - 整洁架构
- [x] Hexagonal Architecture - 六边形架构
- [x] CQRS - 命令查询分离
- [x] Event Sourcing - 事件溯源
- [x] Serverless - 无服务器架构
- [x] Service Mesh - 服务网格

### 2.3 Domain-Driven Design (10+ topics)
- [x] Domain Model - 领域模型
- [x] Bounded Context - 限界上下文
- [x] Entities and Value Objects - 实体与值对象
- [x] Aggregates - 聚合
- [x] Repositories - 仓库模式
- [x] Domain Services - 领域服务
- [x] Application Services - 应用服务
- [x] Domain Events - 领域事件
- [x] Anti-Corruption Layer - 防腐层
- [x] Ubiquitous Language - 通用语言

### 2.4 Testing (8+ topics)
- [x] Unit Testing - 单元测试
- [x] Integration Testing - 集成测试
- [x] E2E Testing - 端到端测试
- [x] TDD - 测试驱动开发
- [x] BDD - 行为驱动开发
- [x] Mocking - 模拟对象
- [x] Test Coverage - 测试覆盖
- [x] Performance Testing - 性能测试

---

## 3️⃣ Cloud & DevOps

### 3.1 Containerization (5+ topics)
- [x] Docker Fundamentals - 容器基础
- [x] Dockerfile Best Practices - 构建优化
- [x] Docker Compose - 多容器编排
- [ ] Container Networking - 容器网络
- [ ] Container Security - 容器安全

### 3.2 Orchestration (6+ topics)
- [x] Kubernetes Architecture - K8s架构
- [x] Pods and Deployments - 工作负载
- [x] Services and Ingress - 服务暴露
- [x] ConfigMaps and Secrets - 配置管理
- [ ] StatefulSets - 有状态应用
- [x] Helm - 包管理

### 3.3 CI/CD (6+ topics)
- [x] CI/CD Fundamentals - 持续集成/交付
- [x] GitHub Actions - 工作流自动化
- [ ] Jenkins - 自动化服务器
- [ ] GitLab CI - 集成CI/CD
- [x] ArgoCD - GitOps
- [ ] Feature Flags - 功能开关

### 3.4 Monitoring & Observability (6+ topics)
- [x] Monitoring Fundamentals - 监控基础
- [x] Prometheus - 指标收集
- [x] Grafana - 可视化
- [x] ELK Stack - 日志分析
- [x] Distributed Tracing - 分布式追踪
- [ ] Alerting - 告警机制

### 3.5 Infrastructure (8+ topics)
- [ ] Infrastructure as Code - IaC
- [x] Terraform - 基础设施编排
- [x] Ansible - 配置管理
- [ ] AWS Core Services - EC2, S3, RDS
- [x] GCP Fundamentals - 谷歌云平台
- [ ] Azure Basics - 微软云
- [ ] Serverless Computing - Lambda, Functions
- [ ] Edge Computing - 边缘计算

---

## 4️⃣ AI & Data Systems

### 4.1 Machine Learning (12+ topics)
**Fundamentals:**
- [x] ML Overview - 机器学习概述
- [x] Supervised Learning - 监督学习
- [x] Unsupervised Learning - 无监督学习
- [ ] Reinforcement Learning - 强化学习

**Algorithms:**
- [x] Linear Regression - 线性回归
- [x] Logistic Regression - 逻辑回归
- [x] Decision Trees - 决策树
- [ ] Random Forest - 随机森林
- [x] SVM - 支持向量机
- [ ] K-Means - K均值聚类
- [x] Neural Networks Basics - 神经网络基础

**Deep Learning:**
- [x] CNN - 卷积神经网络
- [x] RNN / LSTM - 循环神经网络
- [x] Transformers - 注意力机制
- [x] GANs - 生成对抗网络
- [ ] Autoencoders - 自编码器

**Practical:**
- [ ] Feature Engineering - 特征工程
- [ ] Model Evaluation - 模型评估
- [ ] Hyperparameter Tuning - 超参调优
- [ ] MLOps - ML工程化

### 4.2 Large Language Models (8+ topics)
- [x] LLM Fundamentals - 大模型基础
- [ ] Transformer Architecture - 深入理解
- [ ] Pre-training - 预训练
- [x] Fine-tuning - 微调
- [x] Prompt Engineering - 提示工程
- [ ] LLM Evaluation - 模型评估
- [ ] Model Quantization - 模型量化
- [ ] LLM Deployment - 部署优化

### 4.3 RAG Systems (6+ topics)
- [x] RAG Fundamentals - 检索增强生成
- [ ] Document Chunking - 文档分块
- [x] Embedding Models - 嵌入模型
- [ ] Retrieval Strategies - 检索策略
- [ ] Re-ranking - 重排序
- [ ] RAG Evaluation - 评估指标

### 4.4 Vector Databases (5+ topics)
- [x] Vector DB Overview - 向量数据库
- [ ] Similarity Search - 相似度搜索
- [ ] ANN Algorithms - 近似最近邻
- [ ] Indexing Strategies - 索引策略
- [ ] Vector DB Comparison - 产品对比

### 4.5 Data Engineering (8+ topics)
- [ ] Data Pipeline - 数据管道
- [x] ETL / ELT - 数据转换
- [x] Data Warehousing - 数据仓库
- [ ] Data Lake - 数据湖
- [ ] Stream Processing - 流处理
- [ ] Batch Processing - 批处理
- [ ] Data Quality - 数据质量
- [ ] Data Governance - 数据治理

### 4.6 Experimentation (4+ topics)
- [x] A/B Testing - AB测试
- [ ] Multi-armed Bandit - 多臂老虎机
- [ ] Statistical Significance - 统计显著性
- [ ] Experiment Design - 实验设计

---

## 5️⃣ Mathematics

### 5.1 Linear Algebra (8+ topics)
- [x] Vectors and Matrices - 向量与矩阵
- [x] Matrix Operations - 矩阵运算
- [x] Eigenvalues / Eigenvectors - 特征值与特征向量
- [x] Matrix Decomposition - 矩阵分解
- [x] Vector Spaces - 向量空间
- [x] Linear Transformations - 线性变换
- [x] SVD - 奇异值分解
- [x] Applications in CS - 计算机应用

### 5.2 Probability & Statistics (12+ topics)
- [x] Probability Basics - 概率基础
- [x] Random Variables - 随机变量
- [x] Distributions - 概率分布
- [ ] Expectation and Variance - 期望与方差
- [ ] Conditional Probability - 条件概率
- [ ] Bayes' Theorem - 贝叶斯定理
- [x] Hypothesis Testing - 假设检验
- [x] Confidence Intervals - 置信区间
- [x] Correlation and Regression - 相关与回归
- [ ] Maximum Likelihood - 最大似然估计
- [ ] Bayesian Inference - 贝叶斯推断
- [ ] Markov Chains - 马尔可夫链

### 5.3 Graph Theory (6+ topics)
- [x] Graph Representations - 图表示
- [x] Graph Traversal - 图遍历
- [x] Shortest Paths - 最短路径
- [x] Minimum Spanning Trees - 最小生成树
- [x] Network Flow - 网络流
- [x] Graph Algorithms - 图算法
### 5.4 Combinatorics (4+ topics)
- [x] Counting Principles - 计数原理
- [ ] Permutations and Combinations - 排列组合
- [ ] Pigeonhole Principle - 鸽巢原理
- [ ] Inclusion-Exclusion - 容斥原理

### 5.5 Calculus (6+ topics)
- [x] Limits and Continuity - 极限与连续
- [x] Derivatives - 导数
- [x] Integrals - 积分
- [x] Multivariable Calculus - 多元微积分
- [x] Gradient Descent - 梯度下降
- [x] Optimization - 优化方法

### 5.6 Discrete Mathematics (6+ topics)
- [x] Set Theory - 集合论
- [x] Logic - 逻辑
- [x] Relations - 关系
- [x] Functions - 函数
- [x] Number Theory - 数论
- [x] Boolean Algebra - 布尔代数

---

## 6️⃣ Security

### 6.1 Cryptography (8+ topics)
- [x] Symmetric Encryption - 对称加密
- [x] Asymmetric Encryption - 非对称加密
- [x] Hash Functions - 哈希函数
- [x] Digital Signatures - 数字签名
- [ ] PKI - 公钥基础设施
- [ ] SSL/TLS - 传输层安全
- [ ] Blockchain Basics - 区块链基础
- [ ] Zero-Knowledge Proofs - 零知识证明

### 6.2 Network Security (6+ topics)
- [x] Firewalls - 防火墙
- [x] IDS/IPS - 入侵检测
- [x] VPN - 虚拟专用网
- [x] DDoS Protection - DDoS防护
- [x] Network Scanning - 网络扫描
- [x] Packet Analysis - 数据包分析

### 6.3 Application Security (8+ topics)
- [x] OWASP Top 10 - 常见漏洞
- [x] SQL Injection - SQL注入
- [x] XSS - 跨站脚本
- [x] CSRF - 跨站请求伪造
- [x] Authentication - 身份认证
- [x] Authorization - 权限控制
- [x] Secure Coding - 安全编码
- [ ] Vulnerability Assessment - 漏洞评估

### 6.4 System Security (6+ topics)
- [x] Access Control - 访问控制
- [x] Sandboxing - 沙箱
- [x] Secure Boot - 安全启动
- [x] Memory Safety - 内存安全
- [x] Privilege Escalation - 权限提升
- [x] Audit Logging - 审计日志

---

## 7️⃣ Product Management

### 7.1 Product Documentation (4+ topics)
- [x] BRD - 商业需求文档
- [x] PRD - 产品需求文档
- [x] SRS - 软件需求规格
- [x] User Stories - 用户故事

### 7.2 Product Strategy (6+ topics)
- [x] MVP - 最小可行产品
- [x] Product Roadmap - 产品路线图
- [x] Feature Prioritization - 功能优先级
- [x] Go-to-Market - 上市策略
- [x] Product Metrics - 产品指标
- [x] User Research - 用户研究

### 7.3 Market Analysis (4+ topics)
- [x] Market Analysis - 市场分析
- [x] Competitive Analysis - 竞争分析
- [x] SWOT Analysis - SWOT分析
- [x] TAM/SAM/SOM - 市场规模

### 7.4 Project Management (6+ topics)
- [x] Agile - 敏捷开发
- [x] Scrum - Scrum框架
- [x] Kanban - 看板方法
- [x] Waterfall - 瀑布模型
- [ ] PMBOK - 项目管理知识体系
- [ ] Risk Management - 风险管理

---

## 📈 Progress Summary

| Area | Topics | Completed | Coverage |
|------|--------|-----------|----------|
| Data Structures | 18 | 18 | 100% |
| Algorithms | 20 | 18 | 90% |
| Systems | 25 | 25 | 100% |
| Software Engineering | 43 | 28 | 65% |
| Cloud & DevOps | 31 | 20 | 65% |
| AI & Data Systems | 47 | 19 | 40% |
| Mathematics | 42 | 20 | 48% |
| Security | 28 | 23 | 82% |
| Product Management | 20 | 20 | 100% |
| **Total** | **274** | **211** | **77%** |

---

## 🎯 Next Steps

1. Initialize git repository with GitHub workflow
2. Create feature branches for each major area
3. Complete missing content following the file specification
4. Ensure cross-references between related topics
5. Merge all branches following PR best practices

## 🔗 相关概念

跨领域知识互联，建立完整的计算机科学知识体系：

### 数据结构 (Data Structures)

- [数组](./computer-science/data-structures/array.md) - 连续内存存储，随机访问 O(1)
- [链表](./computer-science/data-structures/linked-list.md) - 指针链式结构，动态扩容
- [哈希表](./computer-science/data-structures/hash-table.md) - 散列映射，冲突解决
- [树](./computer-science/data-structures/tree.md) - 层次结构，递归遍历
- [红黑树](./computer-science/data-structures/red-black-tree.md) - 自平衡二叉搜索树
- [前缀树](./computer-science/data-structures/trie.md) - 字符串检索与自动补全

### 算法 (Algorithms)

- [排序算法](./computer-science/algorithms/sorting.md) - 快速排序、归并排序、堆排序
- [二分查找](./computer-science/algorithms/binary-search.md) - 有序序列的高效查找
- [图遍历](./computer-science/algorithms/graph-traversal.md) - BFS、DFS 及应用
- [最短路径](./computer-science/algorithms/shortest-path.md) - Dijkstra、Bellman-Ford、Floyd-Warshall
- [最小生成树](./computer-science/algorithms/minimum-spanning-tree.md) - Prim、Kruskal 算法
- [贪心算法](./computer-science/algorithms/greedy.md) - 局部最优策略
- [动态规划](./computer-science/algorithms/dynamic-programming.md) - 状态定义与转移方程

### 系统基础 (Systems Fundamentals)

- [进程管理](./computer-science/systems/process.md) - 进程概念、状态转换与调度
- [线程与并发](./computer-science/systems/thread.md) - 线程模型与线程池
- [内存管理](./computer-science/systems/memory-management.md) - 内存分配与回收策略
- [虚拟内存](./computer-science/systems/virtual-memory.md) - 页表、缺页中断、置换算法
- [数据库索引](./computer-science/databases/indexing.md) - B+树索引、哈希索引原理
- [事务与并发控制](./computer-science/databases/concurrency-control.md) - ACID、隔离级别
- [负载均衡](./computer-science/distributed-systems/load-balancing.md) - 分发策略与健康检查
- [CAP定理](./computer-science/distributed-systems/cap-theorem.md) - 一致性、可用性、分区容错性

### 工程实践 (Engineering Practice)

- [设计模式](./software-engineering/design-patterns.md) - 创建型、结构型、行为型模式
- [单例模式](./software-engineering/design-patterns/creational/singleton.md) - 全局唯一实例控制
- [观察者模式](./software-engineering/design-patterns/behavioral/observer.md) - 发布订阅机制
- [微服务架构](./software-engineering/architecture-patterns/microservices.md) - 服务拆分与治理
- [Web安全](./security/web-security.md) - OWASP、常见漏洞与防护
- [身份认证](./security/authentication.md) - 认证机制与实现

---

## 🎯 Next Steps

1. Initialize git repository with GitHub workflow
2. Create feature branches for each major area
3. Complete missing content following the file specification
4. Ensure cross-references between related topics
5. Merge all branches following PR best practices

---

*Generated for CS Knowledge Graph Project*
