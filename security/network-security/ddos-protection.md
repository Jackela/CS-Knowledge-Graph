# DDoS防护 (DDoS Protection)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**分布式拒绝服务攻击 (DDoS, Distributed Denial of Service)** 通过大量恶意流量淹没目标系统资源，使其无法为正常用户提供服务。DDoS防护需要多层次的防御策略，从网络边界到应用层的全面保护。

```
┌─────────────────────────────────────────────────────────────────┐
│                   DDoS攻击类型分层                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  应用层 (L7)                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ HTTP Flood | Slowloris | CC攻击 | 恶意爬虫              │   │
│  │ 目标：Web服务器、API网关、应用服务                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  传输层 (L4)                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ SYN Flood | ACK Flood | UDP Flood | Connection Flood    │   │
│  │ 目标：TCP/UDP服务、负载均衡器                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  网络层 (L3)                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ICMP Flood | Smurf | Ping of Death | IP Fragment        │   │
│  │ 目标：网络带宽、路由器、防火墙                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  基础设施层                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ DNS放大 | NTP放大 | SSDP放大 | Memcached放大             │   │
│  │ 目标：带宽耗尽                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 攻击类型详解

### 容量型攻击 (Volumetric Attacks)

消耗目标网络带宽，使其无法处理正常流量。

```
反射放大攻击原理：

┌──────────┐        ┌──────────┐        ┌──────────┐
│ 攻击者    │        │ 反射服务器 │        │ 受害者    │
│ (Botnet) │        │ (开放服务) │        │          │
└────┬─────┘        └────┬─────┘        └────┬─────┘
     │                   │                   │
     │ 1. 伪造源IP发送小请求                  │
     │──────────────────▶│                   │
     │   (src: 受害者IP)  │                   │
     │                   │                   │
     │                   │ 2. 发送大响应      │
     │                   │──────────────────▶│
     │                   │   (放大100-500倍)  │
     │                   │                   │
     │  (重复数千次)                              │

常见放大攻击：
┌──────────┬───────────────┬──────────────┐
│ 协议      │ 放大倍数       │ 端口         │
├──────────┼───────────────┼──────────────┤
│ DNS       │ 28-54x        │ 53           │
│ NTP       │ 556x          │ 123          │
│ SSDP      │ 30-35x        │ 1900         │
│ Memcached │ 10,000-51,000x│ 11211        │
│ CharGen   │ 359x          │ 19           │
└──────────┴───────────────┴──────────────┘
```

### 协议攻击 (Protocol Attacks)

消耗服务器连接表或中间设备资源。

```
SYN Flood攻击：

正常TCP三次握手：
Client          Server
  │    SYN      │
  │────────────▶│
  │   SYN+ACK   │
  │◀────────────│
  │    ACK      │
  │────────────▶│
  │ 连接建立     │

SYN Flood攻击：
Client(Bot)     Server
  │    SYN      │
  │────────────▶│ 创建半开连接 (SYN队列)
  │   SYN+ACK   │
  │◀────────────│
  │  (不回复ACK) │
  │             │
  │    SYN      │
  │────────────▶│ 创建更多半开连接
  │   SYN+ACK   │
  │◀────────────│
  │  (不回复ACK) │
  │             │
  ▼             ▼
SYN队列耗尽，无法处理新连接
```

### 应用层攻击 (Application Layer Attacks)

模拟合法用户请求，消耗应用资源。

```
HTTP Flood攻击：

┌─────────┐      ┌─────────┐      ┌─────────┐
│  Botnet │      │   CDN   │      │  Origin │
│ (1000+  │─────▶│ / WAF   │─────▶│ Server  │
│  bots)  │      │         │      │         │
└─────────┘      └─────────┘      └─────────┘
     │
     ▼
GET /api/search?q=test HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0...
(看起来像正常请求)

攻击特点：
• 使用真实IP（代理池）
• 模仿真实浏览器行为
• 请求计算密集型页面
• 绕过简单频率检测

Slowloris攻击：
发送不完整的HTTP请求，保持连接打开
┌─────────────────────────────────────┐
│ GET /page HTTP/1.1\r\n              │
│ Host: target.com\r\n                │
│ (等待...)                           │
│ User-Agent: ...\r\n                 │
│ (等待...)                           │
│ (永不发送最后的\r\n\r\n)              │
└─────────────────────────────────────┘
```

---

## 防护架构

### 分层防御模型

```
DDoS防护架构：

┌─────────────────────────────────────────────────────────────────┐
│                         边缘层                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Cloudflare │  │  AWS Shield  │  │  阿里高防   │            │
│  │   Akamai    │  │  Azure DDoS  │  │  腾讯BGP    │            │
│  │   Fastly    │  │  Protection  │  │  清洗中心   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│        │                 │                 │                   │
│        └─────────────────┼─────────────────┘                   │
│                          ▼                                     │
│                    流量清洗 (Scrubbing)                         │
│                    恶意流量丢弃，干净流量转发                     │
├─────────────────────────────────────────────────────────────────┤
│                         网络层                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • 黑洞路由 (Blackhole) / 空路由 (Null-route)             │   │
│  │ • BGP Flowspec 流量过滤                                  │   │
│  │ • 速率限制 (Rate Limiting)                               │   │
│  │ • Anycast 分布式分散攻击流量                             │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                         主机层                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • SYN Cookies (防SYN Flood)                              │   │
│  │ • 连接数限制                                              │   │
│  │ • 防火墙规则                                              │   │
│  │ • 负载均衡健康检查                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                        应用层                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • WAF规则                                                │   │
│  │ • 挑战机制 (CAPTCHA/JS Challenge)                        │   │
│  │ • 行为分析/人机识别                                       │   │
│  │ • 限流/熔断                                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 防护技术

### 速率限制 (Rate Limiting)

```nginx
# Nginx速率限制配置
http {
    # 定义限流区域
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # 连接数限制
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    
    server {
        location /api/ {
            # 漏桶算法限流
            limit_req zone=api burst=20 nodelay;
            limit_conn addr 10;
            
            proxy_pass http://backend;
        }
        
        location /login {
            # 登录接口更严格限制
            limit_req zone=login burst=5 nodelay;
            
            proxy_pass http://auth_backend;
        }
    }
}
```

### SYN Cookies

```
SYN Cookies机制：

传统SYN队列：              SYN Cookies：
┌─────────────┐           ┌─────────────┐
│ 队列有限     │           │ 无队列       │
│ 内存消耗    │           │ 编码到序列号  │
│ 队列满即拒绝 │           │ 始终可接受    │
└─────────────┘           └─────────────┘

实现方式：
当SYN队列满时，不保存连接状态
将连接信息编码到ISN (Initial Sequence Number)
收到ACK后验证Cookie，重建连接

Linux启用：
echo 1 > /proc/sys/net/ipv4/tcp_syncookies
```

---

## 云服务防护

### Cloudflare DDoS防护

```
Cloudflare防护层级：

Layer 3/4 (网络层):
┌─────────────────────────────────────────┐
│ • 自动流量分析                          │
│ • 任播网络分散攻击                      │
│ • 95 Tbps+ 网络容量                     │
│ • 自动缓解 (Unmetered)                  │
└─────────────────────────────────────────┘

Layer 7 (应用层):
┌─────────────────────────────────────────┐
│ • Managed Rules (OWASP)                 │
│ • Rate Limiting                         │
│ • Bot Management                        │
│ • CAPTCHA/JS Challenge                  │
│ • 自定义防火墙规则                       │
└─────────────────────────────────────────┘
```

### AWS Shield

```yaml
# AWS Shield配置
# Shield Standard: 自动防护所有AWS客户（免费）
# Shield Advanced: 额外保护和费用保障（付费）

# WAF + Shield 规则组
Resources:
  WebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: DDoSProtectedACL
      Scope: REGIONAL
      DefaultAction:
        Allow: {}
      Rules:
        # AWS托管规则 - DDoS防护
        - Name: AWSManagedRulesCommonRuleSet
          Priority: 1
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesCommonRuleSet
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: AWSManagedRulesCommonRuleSetMetric
        
        # 速率限制规则
        - Name: RateLimitRule
          Priority: 2
          Statement:
            RateBasedStatement:
              Limit: 2000
              AggregateKeyType: IP
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: RateLimitRuleMetric

  # Shield Advanced保护
  ShieldProtection:
    Type: AWS::Shield::Protection
    Properties:
      Name: ALBProtection
      ResourceArn: !Ref ApplicationLoadBalancer
```

---

## 应急响应

```
DDoS应急响应流程：

┌─────────────────────────────────────────────────────────────┐
│ 1. 检测 (Detection)                                          │
│    • 监控告警阈值                                             │
│    • 流量异常分析                                             │
│    • 用户投诉确认                                             │
├─────────────────────────────────────────────────────────────┤
│ 2. 分类 (Classification)                                     │
│    • 攻击类型识别                                             │
│    • 攻击规模评估                                             │
│    • 目标资产确认                                             │
├─────────────────────────────────────────────────────────────┤
│ 3. 缓解 (Mitigation)                                         │
│    • 启用清洗中心                                             │
│    • 调整防护策略                                             │
│    • 必要时黑洞路由                                           │
├─────────────────────────────────────────────────────────────┤
│ 4. 恢复 (Recovery)                                           │
│    • 监控业务恢复                                             │
│    • 逐步解除限制                                             │
│    • 验证服务可用性                                           │
├─────────────────────────────────────────────────────────────┤
│ 5. 复盘 (Post-Incident)                                      │
│    • 攻击源分析                                               │
│    • 防护效果评估                                             │
│    • 策略优化                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 面试要点

**Q1: SYN Flood攻击原理及防护方法？**
> SYN Flood通过发送大量SYN包但不完成三次握手，耗尽服务器SYN队列。防护方法：启用SYN Cookies（无状态连接处理）、增加SYN队列大小、限制每IP连接数、使用防火墙过滤异常SYN包、部署专业DDoS防护设备。

**Q2: 什么是反射放大攻击？如何防护？**
> 反射放大攻击利用开放的第三方服务（DNS、NTP等），伪造受害者IP发送小请求，服务返回大响应给受害者，实现流量放大。防护：入口过滤(BCP38)防止源IP伪造、关闭不必要的UDP服务、限制响应大小、使用DDoS清洗服务。

**Q3: L7 DDoS与传统DDoS的区别？**
> L7 DDoS针对应用层，模拟合法HTTP请求，消耗CPU/数据库资源，难以用传统流量清洗识别。需用WAF、行为分析、挑战机制(CAPTCHA)、设备指纹等技术，结合速率限制和熔断保护。

**Q4: 黑洞路由是什么？何时使用？**
> 黑洞路由(Blackhole/Null-route)是将攻击流量路由到空接口丢弃，保护上游网络。当攻击流量超过防护容量时使用，代价是业务完全不可用。通常与清洗中心配合，先黑洞再引流清洗。

**Q5: 如何设计一个抗DDoS的架构？**
> 分层防御：边缘CDN/高防清洗、Anycast分散流量、网络层ACL限速、主机层SYN Cookies/连接限制、应用层WAF/限流/熔断。准备DDoS响应计划，与云服务商合作，定期演练。

---

## 相关概念

### 网络安全 (Network Security)
- [防火墙](./firewalls.md) - 网络流量过滤与访问控制
- [IDS/IPS](./ids-ips.md) - 入侵检测与入侵防护系统
- [VPN](./vpn.md) - 虚拟专用网络
- [网络扫描](./network-scanning.md) - 网络探测与漏洞扫描
- [包分析](./packet-analysis.md) - 网络流量抓包分析

### 计算机网络 (Computer Networks)
- [网络层](../../computer-science/networks/network-layer.md) - IP协议与路由
- [传输层](../../computer-science/networks/transport-layer.md) - TCP/UDP协议
- [DNS](../../computer-science/networks/dns.md) - 域名系统与DNS放大攻击
- [HTTPS/TLS](../../computer-science/networks/https-tls.md) - 传输层安全

### 分布式系统 (Distributed Systems)
- [负载均衡](../../computer-science/distributed-systems/load-balancing.md) - 流量分发与后端保护
- [CAP定理](../../computer-science/distributed-systems/cap-theorem.md) - 分布式一致性理论
- [分片](../../computer-science/distributed-systems/sharding.md) - 数据分片与分布式架构
- [分布式事务](../../computer-science/distributed-systems/distributed-transactions.md) - 跨服务一致性

### 云与监控 (Cloud & Monitoring)
- [Prometheus监控](../../cloud-devops/monitoring/prometheus.md) - 指标监控与告警
- [CI/CD](../../cloud-devops/cicd/github-actions.md) - 自动化部署与防护
---

## 参考资料

1. "DDoS Attacks: Evolution, Detection, Prevention" by Sanjay Rawat
2. AWS DDoS Response Guide
3. Cloudflare DDoS Threat Report
4. M3AAWG DDoS Mitigation Best Practices
5. NIST SP 800-189: Resilient Interdomain Traffic Exchange
