# 消息队列 (Message Queues)

## 简介
消息队列是分布式系统中实现异步通信、解耦组件和流量削峰的中间件，通过生产-消费模式实现可靠的消息传递。

## 核心概念
- **生产者 (Producer)**: 消息发送方
- **消费者 (Consumer)**: 消息接收方
- **队列 (Queue)**: 消息的缓冲区
- **主题 (Topic)**: 发布订阅模式的消息分类
- **ACK确认**: 消息消费确认机制

## 实现方式 / 工作原理

### 消息队列模型

```
┌────────────────────────────────────────────────────────────┐
│                    点对点模式 (Queue)                       │
│                                                            │
│  Producer ──► Queue ──► Consumer1 (一个消息只被消费一次)    │
│              (FIFO)   ──► Consumer2                        │
│                                                            │
│  特性：负载均衡，每条消息只有一个消费者                      │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                   发布订阅模式 (Topic)                      │
│                                                            │
│           ┌──────► Subscriber1                             │
│  Publisher┼──────► Subscriber2 (消息广播给所有订阅者)       │
│           └──────► Subscriber3                             │
│                                                            │
│  特性：解耦生产者和消费者，支持多播                         │
└────────────────────────────────────────────────────────────┘
```

### Kafka架构实现

```python
class KafkaProducer:
    """Kafka生产者"""
    
    def __init__(self, bootstrap_servers):
        self.metadata = self.fetch_metadata(bootstrap_servers)
        self.batch_size = 16384  # 批量发送大小
        self.linger_ms = 5       # 批量等待时间
        self.buffer = {}  # topic-partition -> message batch
    
    def send(self, topic, key, value):
        """发送消息"""
        # 分区选择策略
        partition = self.partition(topic, key)
        
        # 加入批次
        if partition not in self.buffer:
            self.buffer[partition] = MessageBatch()
        self.buffer[partition].append(Message(key, value))
        
        # 批次满或超时则发送
        if (self.buffer[partition].size >= self.batch_size or 
            self.should_flush()):
            self.flush_partition(partition)
    
    def partition(self, topic, key):
        """分区策略"""
        num_partitions = self.metadata.partitions(topic)
        
        if key is None:
            # 轮询策略
            return self.round_robin_partition(num_partitions)
        else:
            # 哈希策略：相同key进入同一分区，保证顺序
            return hash(key) % num_partitions

class KafkaConsumer:
    """Kafka消费者 - 消费者组"""
    
    def __init__(self, group_id, topics):
        self.group_id = group_id
        self.topics = topics
        self.coordinator = None
        self.assignments = {}  # partition -> position
    
    def subscribe(self):
        """加入消费者组，获取分区分配"""
        # 1. 找Coordinator
        self.coordinator = self.find_coordinator()
        
        # 2. Join Group
        response = self.coordinator.join_group({
            'group_id': self.group_id,
            'member_id': self.member_id,
            'protocol': 'range'  # 或 'roundrobin'
        })
        
        # 3. 同步分配结果
        if response.leader:
            assignments = self.perform_assignment(response.members)
            self.coordinator.sync_group(assignments)
        
        # 4. 开始消费分配的分区
        self.assignments = response.assignments
    
    def poll(self, timeout_ms=1000):
        """拉取消息"""
        for partition, position in self.assignments.items():
            messages = self.fetch(partition, position)
            for msg in messages:
                yield msg
                # 更新消费位置
                self.assignments[partition] = msg.offset + 1
        
        # 提交offset（自动或手动）
        self.commit_offsets()
```

### 消息可靠性保障

```python
class ReliableMessageQueue:
    """可靠消息队列实现"""
    
    def __init__(self):
        self.message_log = WriteAheadLog()  # WAL保证持久化
        self.message_store = {}
    
    def produce_with_ack(self, message, ack_level="all"):
        """
        ACK级别：
        - 0: 不等待确认，最高吞吐
        - 1: 等待leader确认
        - all: 等待所有ISR副本确认
        """
        # 1. 写入WAL
        log_entry = self.message_log.append(message)
        
        # 2. 复制到副本
        if ack_level in ["1", "all"]:
            self.replicate_to_followers(message, ack_level)
        
        # 3. 等待确认
        if ack_level == "all":
            self.wait_for_all_isr()
        
        return MessageMetadata(log_entry.offset)
    
    def consume_with_exactly_once(self, consumer_id, partition):
        """Exactly-Once语义实现"""
        # 使用事务保证生产和消费的原子性
        with self.transaction_manager.begin():
            # 读取消息
            message = self.read(partition, self.committed_offset[partition])
            
            # 处理消息（用户业务逻辑）
            result = self.process(message)
            
            # 生产输出消息 + 提交消费位置（原子操作）
            self.produce_to_output_topic(result)
            self.update_consumer_offset(consumer_id, partition, message.offset)
            
            # 事务提交
            self.transaction_manager.commit()
```

### 主流消息队列对比

| 特性 | Kafka | RabbitMQ | RocketMQ | Pulsar |
|------|-------|----------|----------|--------|
| 架构 | 分布式日志 | 传统MQ | 分布式 | 存算分离 |
| 吞吐量 | 百万级/秒 | 万级/秒 | 十万级/秒 | 百万级/秒 |
| 延迟 | ms级 | μs级 | ms级 | ms级 |
| 消息持久化 | 磁盘顺序写 | 内存+磁盘 | 磁盘 | 分层存储 |
| 复制机制 | ISR | 镜像队列 | 同步双写 | BookKeeper |
| 适用场景 | 日志/流处理 | 企业集成 | 金融事务 | 多租户云原生 |

## 应用场景
- **异步处理**: 发送邮件、短信等非实时任务
- **流量削峰**: 秒杀活动缓冲突发流量
- **日志收集**: 集中收集分布式系统日志
- **事件驱动**: 微服务间解耦通信
- **流处理**: 实时数据处理管道

## 面试要点

1. **Q: 如何保证消息不丢失？**  
   A: ①Producer：使用ACK=all，失败重试；②Broker：WAL持久化，多副本同步；③Consumer：手动提交offset，处理完再提交。RocketMQ还支持事务消息保证生产和业务操作的原子性。

2. **Q: 如何保证消息顺序消费？**  
   A: ①单分区单消费者：绝对顺序但性能受限；②相同key进同一分区：利用分区有序性；③内存队列排序：消费端按业务key缓存排序。Kafka保证分区有序，RocketMQ支持全局有序（性能低）和分区有序。

3. **Q: 消息积压如何处理？**  
   A: ①扩容消费者（Kafka可扩容分区）；②跳过非关键消息；③消息转移（移到新的topic临时处理）；④优化消费逻辑；⑤批量消费提升吞吐。RocketMQ支持消费位点重置重新消费。

4. **Q: Exactly-Once语义如何实现？**  
   A: 需要三端配合：①Producer幂等（PID+序列号去重）；②Broker事务支持（原子性提交多分区）；③Consumer事务消费（两阶段提交或事务消息）。Kafka 0.11+通过幂等Producer+事务API支持Exactly-Once。

## 相关概念

### 数据结构
- [队列](../data-structures/queue.md)
- [日志](../data-structures/log.md)

### 算法
- [轮询算法](../algorithms/round-robin.md)
- [一致性哈希](../algorithms/consistent-hashing.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [分布式缓存](distributed-caching.md)
- [共识算法](consensus-algorithms.md)
