# 负载均衡 (Load Balancing)

## 简介

**负载均衡 (Load Balancing)** 是将传入的网络流量分配到多台服务器的技术，旨在优化资源使用、最大化吞吐量、减少响应时间并避免单点故障。

```
┌─────────────────────────────────────────────────────────────┐
│                   负载均衡的作用                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                      ┌──────────┐                          │
│                      │  用户    │                          │
│                      └────┬─────┘                          │
│                           │                                │
│                           ▼                                │
│                    ┌──────────────┐                        │
│                    │  负载均衡器   │  ← 流量分发中心         │
│                    │ Load Balancer│                        │
│                    └──────┬───────┘                        │
│                           │                                │
│           ┌───────────────┼───────────────┐                │
│           ▼               ▼               ▼                │
│      ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│      │Server 1 │    │Server 2 │    │Server 3 │            │
│      │  20%    │    │  50%    │    │  30%    │            │
│      └─────────┘    └─────────┘    └─────────┘            │
│                                                             │
│   功能：流量分发 · 故障转移 · 会话保持 · SSL终结 · 健康检查  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 负载均衡层次

### DNS负载均衡

```
DNS负载均衡：

用户 ──▶ DNS服务器 ──┬──▶ 1.1.1.1 (Server A)
                    ├──▶ 1.1.1.2 (Server B)
                    └──▶ 1.1.1.3 (Server C)

轮询DNS配置：
example.com.  IN  A  1.1.1.1
example.com.  IN  A  1.1.1.2
example.com.  IN  A  1.1.1.3

优点：简单、无单点
缺点：DNS缓存、无法感知服务器状态
```

### 四层负载均衡 (L4)

```
四层负载均衡（传输层）：

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  基于：IP地址 + 端口号 (TCP/UDP)                             │
│                                                             │
│  用户请求                    后端服务器                      │
│  192.168.1.1:80  ────────▶  10.0.0.1:8080                  │
│                                    │                        │
│  负载均衡器只做转发，不解析内容      │                        │
│                                    ▼                        │
│                            ┌────────────┐                   │
│                            │ 应用服务器  │                   │
│                            └────────────┘                   │
│                                                             │
│  代表：LVS、HAProxy（四层模式）、AWS NLB                      │
│  性能：高（内核态处理）                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 七层负载均衡 (L7)

```
七层负载均衡（应用层）：

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  基于：HTTP头、URL、Cookie、内容等                           │
│                                                             │
│  HTTP请求                                                   │
│  GET /api/users HTTP/1.1                                   │
│  Host: api.example.com                                     │
│  Cookie: session=xxx                                       │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐   路由规则                                 │
│  │  L7 LB      │   /api/* ──▶ API服务器                     │
│  │             │   /static/* ──▶ 静态服务器                  │
│  │  解析HTTP   │   *.jpg ──▶ 图片服务器                      │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│    ┌──────────┐                                             │
│    │ 后端服务  │                                             │
│    └──────────┘                                             │
│                                                             │
│  代表：Nginx、HAProxy、AWS ALB、Envoy                       │
│  功能：URL路由、SSL终结、缓存、压缩                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 负载均衡算法

### 1. 轮询 (Round Robin)

```
轮询算法：

请求1 ───────▶ Server 1
请求2 ──────────────▶ Server 2
请求3 ───────────────────▶ Server 3
请求4 ───────▶ Server 1
请求5 ──────────────▶ Server 2
...

优点：简单、均匀
缺点：不考虑服务器性能差异
```

### 2. 加权轮询 (Weighted Round Robin)

```
加权轮询：

Server 1: 权重3 (性能高)
Server 2: 权重2 (性能中)
Server 3: 权重1 (性能低)

分发序列：1, 1, 1, 2, 2, 3, 1, 1, 1, 2, 2, 3, ...

按权重比例分配流量
```

### 3. 最少连接 (Least Connections)

```
最少连接算法：

当前连接数：
Server 1: 50 connections
Server 2: 20 connections  ← 新请求分发到这里
Server 3: 35 connections

新请求 ────────▶ Server 2

适用于：长连接场景（WebSocket、数据库连接）
```

### 4. 加权最少连接 (Weighted Least Connections)

```
加权最少连接：

Server 1: 权重5, 连接10 → 有效负载 = 10/5 = 2
Server 2: 权重3, 连接9  → 有效负载 = 9/3 = 3
Server 3: 权重2, 连接4  → 有效负载 = 4/2 = 2  ← 选择

考虑服务器性能和处理能力的差异
```

### 5. IP哈希 (IP Hash)

```
IP哈希算法：

server = hash(client_ip) % server_count

客户端IP: 192.168.1.100
hash(192.168.1.100) = 123456
server = 123456 % 3 = 0 → Server 1

同一IP总是路由到同一服务器
用途：会话保持（Session Stickiness）
```

### 6. 一致性哈希 (Consistent Hashing)

```
一致性哈希：

哈希环：0 ────────────────────────────────────── 2^32-1
              ● Server 1 (hash=1000)
        ● Server 2 (hash=800)
                              ● Server 3 (hash=2500)
              ↑
        客户端请求 (hash=1200)
        
路由规则：顺时针找到第一个服务器
hash(1200) → Server 1

扩容影响：添加Server 4只影响相邻节点的数据
```

### 7. 最少响应时间 (Least Response Time)

```
最少响应时间：

监控指标：
Server 1: 平均响应时间 50ms
Server 2: 平均响应时间 120ms
Server 3: 平均响应时间 30ms  ← 新请求分发到这里

动态根据服务器响应速度调整
```

## 算法对比

| 算法 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 轮询 | 简单、均匀 | 不考虑负载 | 服务器性能相同 |
| 加权轮询 | 考虑性能差异 | 配置复杂 | 异构服务器 |
| 最少连接 | 动态适应 | 需要跟踪连接 | 长连接应用 |
| IP哈希 | 会话保持 | 可能不均 | 需要会话保持 |
| 一致性哈希 | 平滑扩容 | 实现复杂 | 缓存分片 |
| 最少响应时间 | 最优性能 | 监控开销 | 对延迟敏感 |

## 健康检查

### 主动健康检查

```
主动检查：

负载均衡器 ──Health Check──▶ Server 1
          │
          ├──Health Check──▶ Server 2
          │
          └──Health Check──▶ Server 3

检查方式：
- TCP连接检查
- HTTP GET请求
- 自定义脚本

频率：每5秒检查一次
超时：3秒无响应视为失败
阈值：连续3次失败标记为down
```

### 被动健康检查

```
被动检查：

监控实际请求响应：
- 5xx错误率超过阈值
- 响应时间超过阈值
- 连接超时次数

自动将异常服务器移出池
```

## 会话保持

### 基于Cookie的会话保持

```
Cookie插入模式：

客户端      负载均衡器      服务器
  │            │            │
  │──请求────▶│            │
  │           │──请求─────▶│
  │           │◀─响应──────│
  │◀─响应─────│ (插入Cookie: SERVERID=1)
  │            │            │
  │──请求+Cookie──────▶    │
  │   SERVERID=1           │
  │           │───────────▶│
  │           │   (根据Cookie路由)
```

### 基于IP哈希的会话保持

```
IP哈希：

client_ip: 192.168.1.100
hash(192.168.1.100) % 3 = 1

所有来自192.168.1.100的请求 → Server 1

缺点：
- NAT场景下多个用户共享IP
- 无法处理IP变化（移动网络）
```

## 实现方案

### Nginx配置

```nginx
# 四层负载均衡（stream模块）
stream {
    upstream backend {
        least_conn;  # 最少连接算法
        server 10.0.0.1:3306 weight=5;
        server 10.0.0.2:3306 weight=5;
        server 10.0.0.3:3306 backup;  # 备份服务器
    }
    
    server {
        listen 3306;
        proxy_pass backend;
    }
}

# 七层负载均衡（http模块）
http {
    upstream backend {
        # 负载均衡算法
        # round_robin;  # 默认轮询
        # least_conn;   # 最少连接
        ip_hash;        # IP哈希
        
        server 10.0.0.1:8080 weight=3 max_fails=3 fail_timeout=30s;
        server 10.0.0.2:8080 weight=3 max_fails=3 fail_timeout=30s;
        server 10.0.0.3:8080 weight=2 backup;
        
        keepalive 32;  # 连接池
    }
    
    server {
        listen 80;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            
            # 健康检查（nginx_plus）
            health_check interval=5s fails=3 passes=2;
        }
        
        # 基于URL路由
        location /api/ {
            proxy_pass http://api_backend;
        }
        
        location /static/ {
            proxy_pass http://static_backend;
        }
    }
}
```

### HAProxy配置

```haproxy
global
    maxconn 4096

defaults
    mode http
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    option httpchk GET /health

# 前端配置
frontend http_frontend
    bind *:80
    
    # ACL规则
    acl is_api path_beg /api
    acl is_static path_end .jpg .png .css .js
    
    use_backend api_servers if is_api
    use_backend static_servers if is_static
    default_backend app_servers

# 后端配置
backend app_servers
    balance roundrobin  # 轮询算法
    # balance leastconn  # 最少连接
    # balance source     # 源IP哈希
    
    server app1 10.0.0.1:8080 check weight 3
    server app2 10.0.0.2:8080 check weight 3
    server app3 10.0.0.3:8080 check weight 2 backup

backend api_servers
    balance roundrobin
    server api1 10.0.0.4:8080 check
    server api2 10.0.0.5:8080 check

backend static_servers
    balance roundrobin
    server static1 10.0.0.6:8080 check
```

### LVS (Linux Virtual Server)

```bash
# LVS NAT模式配置
# Director（调度器）配置

# 1. 启用IP转发
echo 1 > /proc/sys/net/ipv4/ip_forward

# 2. 配置VIP（虚拟IP）
ipvsadm -A -t 192.168.1.100:80 -s rr  # 轮询算法

# 3. 添加真实服务器
ipvsadm -a -t 192.168.1.100:80 -r 10.0.0.1:80 -m  # NAT模式
ipvsadm -a -t 192.168.1.100:80 -r 10.0.0.2:80 -m
ipvsadm -a -t 192.168.1.100:80 -r 10.0.0.3:80 -m

# 查看配置
ipvsadm -Ln

# LVS模式对比：
# - NAT：修改目标IP，服务器网关指向Director
# - DR（直接路由）：修改MAC地址，服务器需配置VIP
# - TUN（隧道）：IP封装，服务器可在不同网络
# - FULLNAT：修改源IP和目标IP，跨网段部署
```

## 高可用架构

### 负载均衡器主备

```
主备模式（Active-Standby）：

     ┌─────────┐
     │   VIP   │◀──── 虚拟IP浮动
     └────┬────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───┴───┐
│ LB-1  │   │ LB-2  │
│Master │   │Backup │
│  VRRP │◀─▶│  VRRP │
└───┬───┘   └───────┘
    │
    ▼
  后端服务器

Keepalived配置：
- 主备通过VRRP协议通信
- VIP随主节点漂移
- 主节点故障，备节点自动接管
```

### 负载均衡器集群

```
Anycast模式：

              用户
               │
     ┌─────────┼─────────┐
     │         │         │
┌────▼───┐ ┌───▼────┐ ┌──▼─────┐
│ LB-北京 │ │ LB-上海 │ │ LB-广州 │
│(同VIP) │ │(同VIP) │ │(同VIP) │
└────┬───┘ └───┬────┘ └──┬─────┘
     │         │         │
     └─────────┼─────────┘
               ▼
            后端池

BGP Anycast将用户路由到最近的LB
```

## 云负载均衡

### AWS ELB

```
AWS负载均衡服务：

┌─────────────────────────────────────────┐
│           Application Load Balancer     │
│           (Layer 7)                     │
│  - 基于内容路由                          │
│  - WebSocket支持                         │
│  - 容器支持                              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           Network Load Balancer         │
│           (Layer 4)                     │
│  - 超高性能                              │
│  - 静态IP                                │
│  - TCP/UDP                               │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           Gateway Load Balancer         │
│           (Layer 3)                     │
│  - 第三方安全设备                        │
│  - 透明流量检查                          │
└─────────────────────────────────────────┘
```

## 面试要点

### 常见问题

**Q1: 四层和七层负载均衡的区别？**
> 四层基于IP和端口转发，不解析内容，性能高；七层基于HTTP等应用层协议，可解析URL、Header等，功能丰富但性能略低。

**Q2: 负载均衡算法有哪些？**
> 轮询、加权轮询、最少连接、IP哈希、一致性哈希、最少响应时间等。轮询最简单，最少连接适合长连接，IP哈希用于会话保持。

**Q3: 会话保持有哪些实现方式？**
> 1. Cookie插入：LB插入SERVERID Cookie
> 2. Cookie重写：使用应用Cookie
> 3. IP哈希：同一IP路由到同一服务器
> 4. 会话复制：服务器间同步会话
> 5. 集中存储：Redis等存储会话

**Q4: LVS的三种模式区别？**
> NAT：修改目标IP，适合小规模；DR：修改MAC，性能最好，需同网段；TUN：IP封装，可跨机房；FULLNAT：修改源目IP，适合复杂网络。

## 相关概念

### 同目录概念
- [分片](./sharding.md) - 数据分片策略
- [CAP定理](./cap-theorem.md) - 分布式系统理论
- [分布式事务](./distributed-transactions.md) - 跨服务事务

### 跨领域概念
- [DNS](../networks/dns.md) - DNS负载均衡
- [传输层](../networks/transport-layer.md) - 四层负载均衡基础
- [HTTPS/TLS](../networks/https-tls.md) - SSL终结
- [进程](../systems/process.md) - 进程调度与资源分配
- [调度](../systems/scheduling.md) - 调度算法与负载均衡
- [并发控制](../databases/concurrency-control.md) - 连接池与并发管理
- [DDoS防护](../../security/network-security/ddos-protection.md) - 负载均衡器的安全防护作用

- [分片](./sharding.md) - 数据分片策略
- [CAP定理](./cap-theorem.md) - 分布式系统理论
- [分布式事务](./distributed-transactions.md) - 跨服务事务

## 参考资料

1. Nginx官方文档
2. HAProxy官方文档
3. Linux Virtual Server项目
4. AWS Load Balancer文档
5. Wikipedia: [Load balancing](https://en.wikipedia.org/wiki/Load_balancing_(computing))
