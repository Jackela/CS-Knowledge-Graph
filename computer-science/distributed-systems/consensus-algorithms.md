# 共识算法 (Consensus Algorithms)

## 简介
共识算法是分布式系统中让多个节点就某一值达成一致的算法，是构建高可用、强一致性分布式系统的核心基础。

## 核心概念
- **一致性 (Agreement)**: 所有正确节点达成相同决定
- **有效性 (Validity)**: 决定的值必须来自提议的值
- **终止性 (Termination)**: 正确节点最终能做出决定
- **容错性 (Fault Tolerance)**: 容忍部分节点故障

## 实现方式 / 工作原理

### Raft算法

```python
class RaftNode:
    def __init__(self, node_id, peers):
        self.id = node_id
        self.peers = peers
        self.state = "FOLLOWER"  # FOLLOWER/CANDIDATE/LEADER
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader状态
        self.next_index = {}   # 每个节点的下一个日志索引
        self.match_index = {}  # 每个节点已复制的日志索引
    
    def start_election(self):
        """候选人发起选举"""
        self.state = "CANDIDATE"
        self.current_term += 1
        self.voted_for = self.id
        votes = 1  # 给自己投票
        
        # 并行请求投票
        for peer in self.peers:
            response = self.request_vote(peer, {
                'term': self.current_term,
                'candidate_id': self.id,
                'last_log_index': len(self.log) - 1,
                'last_log_term': self.log[-1].term if self.log else 0
            })
            if response.vote_granted:
                votes += 1
        
        # 获得多数票成为Leader
        if votes > len(self.peers) // 2:
            self.become_leader()
    
    def become_leader(self):
        """成为Leader后的初始化"""
        self.state = "LEADER"
        for peer in self.peers:
            self.next_index[peer] = len(self.log)
            self.match_index[peer] = 0
        # 启动心跳和日志复制
        self.start_heartbeat_timer()
    
    def replicate_log(self, command):
        """Leader复制日志到Followers"""
        entry = LogEntry(term=self.current_term, command=command)
        self.log.append(entry)
        
        for peer in self.peers:
            self.send_append_entries(peer, {
                'term': self.current_term,
                'leader_id': self.id,
                'prev_log_index': self.next_index[peer] - 1,
                'prev_log_term': self.log[self.next_index[peer]-1].term,
                'entries': self.log[self.next_index[peer]:],
                'leader_commit': self.commit_index
            })
```

### Paxos算法

```python
class PaxosAcceptor:
    """Paxos接受者"""
    def __init__(self):
        self.promised_ballot = None  # 承诺的最高提案号
        self.accepted_ballot = None  # 已接受的提案号
        self.accepted_value = None   # 已接受的值
    
    def handle_prepare(self, ballot):
        """Phase 1a/b: Prepare阶段"""
        if self.promised_ballot is None or ballot > self.promised_ballot:
            self.promised_ballot = ballot
            return Promise(ballot, self.accepted_ballot, self.accepted_value)
        return Reject(self.promised_ballot)
    
    def handle_accept(self, ballot, value):
        """Phase 2a/b: Accept阶段"""
        if ballot >= self.promised_ballot:
            self.promised_ballot = ballot
            self.accepted_ballot = ballot
            self.accepted_value = value
            return Accepted(ballot)
        return Reject(self.promised_ballot)

class PaxosProposer:
    """Paxos提议者"""
    def propose(self, value):
        ballot = self.generate_ballot()
        
        # Phase 1: Prepare
        promises = self.broadcast_prepare(ballot)
        if len(promises) <= self.majority:
            return False  # 无法获得多数承诺
        
        # 如果有已接受的值，必须采用该值
        for p in promises:
            if p.accepted_value is not None:
                value = p.accepted_value
                break
        
        # Phase 2: Accept
        accepts = self.broadcast_accept(ballot, value)
        return len(accepts) > self.majority
```

### 算法对比

| 特性 | Paxos | Raft | ZAB |
|------|-------|------|-----|
| 可读性 | 难以理解 | 易于理解 | 中等 |
| 领导者 | 多提议者 | 单领导者 | 单领导者 |
| 日志复制 | 两阶段 | 追加复制 | 追加复制 |
| 成员变更 | 复杂 | 联合共识 | 动态配置 |
| 应用 | Chubby | etcd/Consul | ZooKeeper |

## 应用场景
- **分布式KV存储**: etcd、Consul配置管理和服务发现
- **分布式协调**: ZooKeeper分布式锁和队列
- **数据库复制**: MySQL Group Replication、TiKV
- **区块链**: 拜占庭容错共识（PBFT、HotStuff）

## 面试要点

1. **Q: Raft如何保证安全性（Safety）？**  
   A: ①选举安全：每届最多一个Leader（通过term保证）；②领导者只追加：Leader从不修改/删除日志；③日志匹配：相同index和term的日志内容相同；④领导者完整性：已提交日志在后续任期必存在；⑤状态机安全：已提交日志所有节点以相同顺序应用。

2. **Q: 脑裂（Split Brain）问题如何解决？**  
   A: Raft通过term机制和多数派原则解决。①网络分区时，小分区无法获得多数票，保持FOLLOWER状态；②大分区正常运作；③恢复后，小分区节点发现自己的term落后，自动降级并同步日志。确保任何时刻只有一个有效Leader。

3. **Q: Paxos和Raft的主要区别？**  
   A: ①Paxos允许并发提议，无明确Leader阶段；Raft强Leader模型，日志只能从Leader流向Follower。②Paxos理论更优雅但难以实现；Raft将问题分解为领导者选举、日志复制、安全性三个子问题，更易理解和实现。③Paxos两阶段，Raft类似但整合为日志复制。

4. **Q: 如何处理日志不一致（Log Inconsistency）？**  
   A: Raft采用强制Follower复制Leader日志的策略。Leader维护next_index， AppendEntries失败时递减next_index重试，直到找到共同祖先，然后覆盖Follower后续不一致日志。简化了日志恢复但牺牲了一些灵活性。

## 相关概念

### 数据结构
- [日志](../data-structures/log.md)
- [状态机](../data-structures/state-machine.md)

### 算法
- [拜占庭容错](../algorithms/byzantine-fault-tolerance.md)
- [两阶段提交](../algorithms/two-phase-commit.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [CAP定理](cap-theorem.md)
- [分布式缓存](distributed-caching.md)
