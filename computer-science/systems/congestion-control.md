# 拥塞控制 (Congestion Control)

## 简介
拥塞控制是网络传输层的核心机制，用于防止过多数据注入网络导致性能下降，确保网络在高负载下仍能稳定运行。

## 核心概念
- **拥塞窗口 (Congestion Window, cwnd)**: 发送方维护的窗口大小，限制未确认数据量
- **慢启动阈值 (Slow Start Threshold, ssthresh)**: 区分慢启动和拥塞避免的临界值
- **往返时间 (RTT)**: 数据包从发送到确认的时间
- **丢包检测**: 通过超时或重复ACK识别网络拥塞

## 实现方式 / 工作原理

### TCP拥塞控制算法

```python
class CongestionControl:
    def __init__(self):
        self.cwnd = 1  # 初始拥塞窗口
        self.ssthresh = 64  # 慢启动阈值
        self.state = "SLOW_START"  # 初始状态
    
    def on_ack_received(self):
        """收到ACK时的处理"""
        if self.state == "SLOW_START":
            self.cwnd *= 2  # 指数增长
            if self.cwnd >= self.ssthresh:
                self.state = "CONGESTION_AVOIDANCE"
        else:  # CONGESTION_AVOIDANCE
            self.cwnd += 1  # 线性增长
    
    def on_timeout(self):
        """超时时的处理"""
        self.ssthresh = self.cwnd // 2
        self.cwnd = 1
        self.state = "SLOW_START"
    
    def on_duplicate_ack(self, dup_ack_count):
        """快速重传/恢复"""
        if dup_ack_count == 3:
            self.ssthresh = self.cwnd // 2
            self.cwnd = self.ssthresh + 3
            self.state = "FAST_RECOVERY"
```

### 四种经典算法

| 算法 | 描述 | 触发条件 |
|------|------|----------|
| 慢启动 (Slow Start) | cwnd指数增长 | 连接建立或超时后 |
| 拥塞避免 (Congestion Avoidance) | cwnd线性增长 | cwnd ≥ ssthresh |
| 快速重传 (Fast Retransmit) | 立即重传丢失包 | 收到3个重复ACK |
| 快速恢复 (Fast Recovery) | 保持cwnd不降为1 | 快速重传后 |

## 应用场景
- **Web服务**: HTTP/HTTPS连接确保稳定传输
- **视频流媒体**: 自适应比特率控制避免卡顿
- **文件传输**: FTP、SFTP大文件可靠传输
- **数据库复制**: 主从同步流量控制

## 面试要点

1. **Q: 慢启动和拥塞避免的区别是什么？**  
   A: 慢启动阶段cwnd指数增长（每RTT翻倍），目的是快速探测网络容量；拥塞避免阶段cwnd线性增长（每RTT加1），目的是缓慢接近网络极限避免拥塞。

2. **Q: 快速重传为什么设置阈值为3个重复ACK？**  
   A: 因为网络可能乱序，1-2个重复ACK可能是乱序导致，3个重复ACK大概率是真的丢包。这个值是经验值，平衡了检测灵敏度和误判率。

3. **Q: TCP Tahoe和Reno的区别？**  
   A: Tahoe在超时或3个重复ACK时都将cwnd降为1；Reno引入快速恢复，3个重复ACK时cwnd降为ssthresh而非1，保持管道充盈。

4. **Q: BBR算法与传统拥塞控制的区别？**  
   A: BBR基于带宽和RTT建模，不依赖丢包判断拥塞，能充分利用带宽；传统算法以丢包为拥塞信号，在 shallow buffer 网络中性能受限。

## 相关概念

### 数据结构
- [滑动窗口](../data-structures/sliding-window.md)
- [队列](../data-structures/queue.md)

### 算法
- [TCP算法](../algorithms/tcp-algorithms.md)
- [流量控制](../algorithms/flow-control.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [网络协议栈](network-protocol-stack.md)
- [网络安全](network-security.md)
