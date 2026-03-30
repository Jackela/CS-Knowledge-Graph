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
- [ ] Segment Tree - 线段树，区间查询
- [ ] Fenwick Tree (BIT) - 树状数组

**Advanced Structures:**
- [x] Heap / Priority Queue - 堆，优先队列
- [x] Graph - 图表示，邻接矩阵/表
- [x] Disjoint Set (Union-Find) - 并查集
- [ ] Skip List - 跳表
- [ ] Splay Tree - 伸展树

### 1.2 Algorithms (20+ topics)
**Sorting:**
- [x] Comparison Sorts: Quick Sort, Merge Sort, Heap Sort
- [x] Linear Sorts: Counting Sort, Radix Sort, Bucket Sort
- [ ] Selection Algorithms: Quick Select, Median of Medians

**Searching:**
- [x] Binary Search - 二分查找及变种
- [ ] Interpolation Search - 插值查找
- [ ] Exponential Search - 指数搜索

**Graph Algorithms:**
- [x] Graph Traversal: BFS, DFS
- [x] Shortest Path: Dijkstra, Bellman-Ford, Floyd-Warshall
- [x] Minimum Spanning Tree: Prim, Kruskal
- [x] Topological Sort - 拓扑排序
- [ ] Strongly Connected Components: Kosaraju, Tarjan
- [ ] Network Flow: Ford-Fulkerson, Edmonds-Karp, Dinic
- [ ] Bipartite Matching: Hungarian Algorithm

**Dynamic Programming:**
- [x] DP Fundamentals - 状态定义、转移方程
- [x] Classic DP Problems
- [ ] DP Optimization: Space Optimization, Monotone Queue
- [ ] Digit DP, State Compression DP

**String Algorithms:**
- [x] String Matching: KMP, Rabin-Karp
- [ ] Suffix Array / Suffix Tree
- [ ] Manacher's Algorithm - 回文串
- [ ] Z-Algorithm

**Other Paradigms:**
- [x] Greedy Algorithms - 贪心策略
- [x] Divide and Conquer - 分治法
- [x] Recursion and Backtracking - 递归与回溯
- [ ] Branch and Bound - 分支限界

**Advanced Algorithms:**
- [ ] Computational Geometry: Convex Hull, Line Intersection
- [ ] Number Theory: GCD, LCM, Prime Sieve, Modular Arithmetic
- [ ] Matrix Exponentiation

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
- [ ] Congestion Control - 拥塞控制算法
- [ ] Network Security - 防火墙、NAT

**Databases:**
- [x] Relational Model - 关系模型
- [x] Normalization - 范式理论
- [x] Indexing - B+树索引、哈希索引
- [x] SQL Advanced - 复杂查询、优化
- [x] Concurrency Control - 并发控制、事务隔离
- [ ] Query Optimization - 查询优化器
- [ ] Database Architecture - 存储引擎

**Distributed Systems:**
- [x] Distributed Transactions - 分布式事务
- [x] Sharding - 数据分片
- [x] Load Balancing - 负载均衡
- [ ] Consensus Algorithms - Raft, Paxos
- [ ] CAP Theorem - CAP理论
- [ ] Distributed Caching - 分布式缓存
- [ ] Message Queues - Kafka, RabbitMQ

**Computer Architecture:**
- [ ] CPU Architecture - 指令集、流水线
- [ ] Memory Hierarchy - 缓存层次
- [ ] Cache Coherence - 缓存一致性
- [ ] Pipelining - 指令流水线
- [ ] I/O Systems - 输入输出系统

**Compilers:**
- [ ] Lexical Analysis - 词法分析
- [ ] Parsing - 语法分析
- [ ] Semantic Analysis - 语义分析
- [ ] Code Generation - 代码生成
- [ ] Optimization - 编译优化

---

## 2️⃣ Software Engineering

### 2.1 Design Patterns (15+ topics)
**Creational:**
- [ ] Singleton - 单例模式
- [ ] Factory / Abstract Factory - 工厂模式
- [ ] Builder - 建造者模式
- [ ] Prototype - 原型模式

**Structural:**
- [ ] Adapter - 适配器模式
- [ ] Bridge - 桥接模式
- [ ] Composite - 组合模式
- [ ] Decorator - 装饰器模式
- [ ] Facade - 外观模式
- [ ] Flyweight - 享元模式
- [ ] Proxy - 代理模式

**Behavioral:**
- [ ] Observer - 观察者模式
- [ ] Strategy - 策略模式
- [ ] Command - 命令模式
- [ ] State - 状态模式
- [ ] Template Method - 模板方法
- [ ] Iterator - 迭代器模式

### 2.2 Software Architecture (10+ topics)
- [ ] Monolithic Architecture - 单体架构
- [ ] Microservices - 微服务架构
- [ ] Event-Driven Architecture - 事件驱动
- [ ] Layered Architecture - 分层架构
- [ ] Clean Architecture - 整洁架构
- [ ] Hexagonal Architecture - 六边形架构
- [ ] CQRS - 命令查询分离
- [ ] Event Sourcing - 事件溯源
- [ ] Serverless - 无服务器架构
- [ ] Service Mesh - 服务网格

### 2.3 Domain-Driven Design (10+ topics)
- [ ] Domain Model - 领域模型
- [ ] Bounded Context - 限界上下文
- [ ] Entities and Value Objects - 实体与值对象
- [ ] Aggregates - 聚合
- [ ] Repositories - 仓库模式
- [ ] Domain Services - 领域服务
- [ ] Application Services - 应用服务
- [ ] Domain Events - 领域事件
- [ ] Anti-Corruption Layer - 防腐层
- [ ] Ubiquitous Language - 通用语言

### 2.4 Testing (8+ topics)
- [ ] Unit Testing - 单元测试
- [ ] Integration Testing - 集成测试
- [ ] E2E Testing - 端到端测试
- [ ] TDD - 测试驱动开发
- [ ] BDD - 行为驱动开发
- [ ] Mocking - 模拟对象
- [ ] Test Coverage - 测试覆盖
- [ ] Performance Testing - 性能测试

---

## 3️⃣ Cloud & DevOps

### 3.1 Containerization (5+ topics)
- [x] Docker Fundamentals - 容器基础
- [x] Dockerfile Best Practices - 构建优化
- [ ] Docker Compose - 多容器编排
- [ ] Container Networking - 容器网络
- [ ] Container Security - 容器安全

### 3.2 Orchestration (6+ topics)
- [x] Kubernetes Architecture - K8s架构
- [x] Pods and Deployments - 工作负载
- [ ] Services and Ingress - 服务暴露
- [ ] ConfigMaps and Secrets - 配置管理
- [ ] StatefulSets - 有状态应用
- [ ] Helm - 包管理

### 3.3 CI/CD (6+ topics)
- [x] CI/CD Fundamentals - 持续集成/交付
- [ ] GitHub Actions - 工作流自动化
- [ ] Jenkins - 自动化服务器
- [ ] GitLab CI - 集成CI/CD
- [ ] ArgoCD - GitOps
- [ ] Feature Flags - 功能开关

### 3.4 Monitoring & Observability (6+ topics)
- [x] Monitoring Fundamentals - 监控基础
- [ ] Prometheus - 指标收集
- [ ] Grafana - 可视化
- [ ] ELK Stack - 日志分析
- [ ] Distributed Tracing - 分布式追踪
- [ ] Alerting - 告警机制

### 3.5 Infrastructure (8+ topics)
- [ ] Infrastructure as Code - IaC
- [ ] Terraform - 基础设施编排
- [ ] Ansible - 配置管理
- [ ] AWS Core Services - EC2, S3, RDS
- [ ] GCP Fundamentals - 谷歌云平台
- [ ] Azure Basics - 微软云
- [ ] Serverless Computing - Lambda, Functions
- [ ] Edge Computing - 边缘计算

---

## 4️⃣ AI & Data Systems

### 4.1 Machine Learning (12+ topics)
**Fundamentals:**
- [x] ML Overview - 机器学习概述
- [ ] Supervised Learning - 监督学习
- [ ] Unsupervised Learning - 无监督学习
- [ ] Reinforcement Learning - 强化学习

**Algorithms:**
- [ ] Linear Regression - 线性回归
- [ ] Logistic Regression - 逻辑回归
- [ ] Decision Trees - 决策树
- [ ] Random Forest - 随机森林
- [ ] SVM - 支持向量机
- [ ] K-Means - K均值聚类
- [ ] Neural Networks Basics - 神经网络基础

**Deep Learning:**
- [x] CNN - 卷积神经网络
- [x] RNN / LSTM - 循环神经网络
- [x] Transformers - 注意力机制
- [ ] GANs - 生成对抗网络
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
- [ ] Fine-tuning - 微调
- [ ] Prompt Engineering - 提示工程
- [ ] LLM Evaluation - 模型评估
- [ ] Model Quantization - 模型量化
- [ ] LLM Deployment - 部署优化

### 4.3 RAG Systems (6+ topics)
- [x] RAG Fundamentals - 检索增强生成
- [ ] Document Chunking - 文档分块
- [ ] Embedding Models - 嵌入模型
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
- [ ] ETL / ELT - 数据转换
- [ ] Data Warehousing - 数据仓库
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
- [ ] Matrix Operations - 矩阵运算
- [ ] Eigenvalues / Eigenvectors - 特征值与特征向量
- [ ] Matrix Decomposition - 矩阵分解
- [ ] Vector Spaces - 向量空间
- [ ] Linear Transformations - 线性变换
- [ ] SVD - 奇异值分解
- [ ] Applications in CS - 计算机应用

### 5.2 Probability & Statistics (12+ topics)
- [x] Probability Basics - 概率基础
- [ ] Random Variables - 随机变量
- [ ] Distributions - 概率分布
- [ ] Expectation and Variance - 期望与方差
- [ ] Conditional Probability - 条件概率
- [ ] Bayes' Theorem - 贝叶斯定理
- [ ] Hypothesis Testing - 假设检验
- [ ] Confidence Intervals - 置信区间
- [ ] Correlation and Regression - 相关与回归
- [ ] Maximum Likelihood - 最大似然估计
- [ ] Bayesian Inference - 贝叶斯推断
- [ ] Markov Chains - 马尔可夫链

### 5.3 Graph Theory (6+ topics)
- [x] Graph Basics - 图基础
- [ ] Graph Representations - 图表示
- [ ] Graph Traversal - 图遍历
- [ ] Shortest Paths - 最短路径
- [ ] Minimum Spanning Trees - 最小生成树
- [ ] Network Flow - 网络流

### 5.4 Combinatorics (4+ topics)
- [x] Counting Principles - 计数原理
- [ ] Permutations and Combinations - 排列组合
- [ ] Pigeonhole Principle - 鸽巢原理
- [ ] Inclusion-Exclusion - 容斥原理

### 5.5 Calculus (6+ topics)
- [ ] Limits and Continuity - 极限与连续
- [ ] Derivatives - 导数
- [ ] Integrals - 积分
- [ ] Multivariable Calculus - 多元微积分
- [ ] Gradient Descent - 梯度下降
- [ ] Optimization - 优化方法

### 5.6 Discrete Mathematics (6+ topics)
- [ ] Set Theory - 集合论
- [ ] Logic - 逻辑
- [ ] Relations - 关系
- [ ] Functions - 函数
- [ ] Number Theory - 数论
- [ ] Boolean Algebra - 布尔代数

---

## 6️⃣ Security

### 6.1 Cryptography (8+ topics)
- [ ] Symmetric Encryption - 对称加密
- [ ] Asymmetric Encryption - 非对称加密
- [ ] Hash Functions - 哈希函数
- [ ] Digital Signatures - 数字签名
- [ ] PKI - 公钥基础设施
- [ ] SSL/TLS - 传输层安全
- [ ] Blockchain Basics - 区块链基础
- [ ] Zero-Knowledge Proofs - 零知识证明

### 6.2 Network Security (6+ topics)
- [ ] Firewalls - 防火墙
- [ ] IDS/IPS - 入侵检测
- [ ] VPN - 虚拟专用网
- [ ] DDoS Protection - DDoS防护
- [ ] Network Scanning - 网络扫描
- [ ] Packet Analysis - 数据包分析

### 6.3 Application Security (8+ topics)
- [ ] OWASP Top 10 - 常见漏洞
- [ ] SQL Injection - SQL注入
- [ ] XSS - 跨站脚本
- [ ] CSRF - 跨站请求伪造
- [ ] Authentication - 身份认证
- [ ] Authorization - 权限控制
- [ ] Secure Coding - 安全编码
- [ ] Vulnerability Assessment - 漏洞评估

### 6.4 System Security (6+ topics)
- [ ] Access Control - 访问控制
- [ ] Sandboxing - 沙箱
- [ ] Secure Boot - 安全启动
- [ ] Memory Safety - 内存安全
- [ ] Privilege Escalation - 权限提升
- [ ] Audit Logging - 审计日志

---

## 7️⃣ Product Management

### 7.1 Product Documentation (4+ topics)
- [x] BRD - 商业需求文档
- [x] PRD - 产品需求文档
- [x] SRS - 软件需求规格
- [ ] User Stories - 用户故事

### 7.2 Product Strategy (6+ topics)
- [x] MVP - 最小可行产品
- [ ] Product Roadmap - 产品路线图
- [ ] Feature Prioritization - 功能优先级
- [ ] Go-to-Market - 上市策略
- [ ] Product Metrics - 产品指标
- [ ] User Research - 用户研究

### 7.3 Market Analysis (4+ topics)
- [x] Market Analysis - 市场分析
- [ ] Competitive Analysis - 竞争分析
- [ ] SWOT Analysis - SWOT分析
- [ ] TAM/SAM/SOM - 市场规模

### 7.4 Project Management (6+ topics)
- [x] Agile - 敏捷开发
- [ ] Scrum - Scrum框架
- [ ] Kanban - 看板方法
- [ ] Waterfall - 瀑布模型
- [ ] PMBOK - 项目管理知识体系
- [ ] Risk Management - 风险管理

---

## 📈 Progress Summary

| Area | Topics | Completed | Coverage |
|------|--------|-----------|----------|
| Data Structures | 15 | 12 | 80% |
| Algorithms | 20 | 14 | 70% |
| Systems | 25 | 18 | 72% |
| Software Engineering | 43 | 0 | 0% |
| Cloud & DevOps | 31 | 9 | 29% |
| AI & Data Systems | 47 | 10 | 21% |
| Mathematics | 42 | 8 | 19% |
| Security | 28 | 0 | 0% |
| Product Management | 20 | 8 | 40% |
| **Total** | **271** | **87** | **32%** |

---

## 🎯 Next Steps

1. Initialize git repository with GitHub workflow
2. Create feature branches for each major area
3. Complete missing content following the file specification
4. Ensure cross-references between related topics
5. Merge all branches following PR best practices

---

*Generated for CS Knowledge Graph Project*
