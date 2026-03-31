# 防火墙 (Firewalls)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**防火墙 (Firewall)** 是网络安全的基础设施，用于监控和控制进出网络的数据包流量。作为网络的第一道防线，防火墙基于预定义的安全规则决定允许或拒绝特定的网络连接。

```
┌─────────────────────────────────────────────────────────────────┐
│                     防火墙部署架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│     Internet                                                    │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐                  │
│   │  边界防火墙  │────▶│  DMZ区  │────▶│ 内部网络 │                  │
│   │ (Perimeter)│     │(隔离区) │     │(LAN)    │                  │
│   └─────────┘     └─────────┘     └─────────┘                  │
│        │           [Web服务器]      [数据库]                     │
│        │           [DNS服务器]      [应用服务器]                  │
│        ▼                                                        │
│   [入侵检测/防护系统 IDS/IPS]                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 防火墙类型

### 包过滤防火墙 (Packet Filtering)

基于网络层和传输层头部信息（IP地址、端口、协议）进行过滤，是最高效的防火墙类型。

```
包过滤决策流程：

数据包到达
     │
     ▼
┌─────────────────┐
│ 检查源IP/目标IP  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 检查源端口/目标端口│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 检查协议 (TCP/UDP/ICMP) │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
  允许      拒绝
  (ACCEPT)  (DROP/REJECT)
```

### 状态检测防火墙 (Stateful Inspection)

不仅检查单个数据包，还跟踪连接状态，维护状态表 (State Table) 来识别合法会话。

```
状态表示例：

┌────────────┬────────────┬───────────┬───────────┬────────────┐
│  协议      │  源地址     │  源端口   │  目标地址  │  目标端口  │
├────────────┼────────────┼───────────┼───────────┼────────────┤
│  TCP       │ 192.168.1.5│  54321    │ 93.184.216│  443       │
│  TCP       │ 192.168.1.7│  54322    │ 172.217.16│  80        │
│  UDP       │ 192.168.1.3│  5353     │ 224.0.0.251│  5353     │
└────────────┴────────────┴───────────┴───────────┴────────────┘

TCP连接状态跟踪：
NONE → SYN_SENT → ESTABLISHED → FIN_WAIT → CLOSED
```

### 应用层防火墙 (Application Layer Firewall / Proxy Firewall)

工作在OSI模型的应用层，深度检查应用协议内容，可理解HTTP、FTP、DNS等协议。

### Web应用防火墙 (WAF)

专门保护Web应用，防护SQL注入、XSS、CSRF等攻击。

```
WAF部署模式：

┌────────────────────────────────────────────────────────────┐
│                                                            │
│   模式1: 反向代理模式 (Reverse Proxy)                      │
│                                                            │
│   Client ──▶ WAF ──▶ Web Server                           │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   模式2: 透明代理模式 (Transparent)                        │
│                                                            │
│   Client ──┬──▶ Web Server                                │
│            │                                               │
│           WAF (流量镜像/桥接)                              │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   模式3: 云WAF (Cloud-based)                               │
│                                                            │
│   Client ──▶ CDN/WAF ──▶ Origin Server                    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 防火墙规则配置

### iptables 配置示例

```bash
#!/bin/bash
# iptables防火墙脚本示例

# 清空现有规则
iptables -F
iptables -X
iptables -Z

# 默认策略: 拒绝所有入站，允许所有出站
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 允许本地回环
iptables -A INPUT -i lo -j ACCEPT

# 允许已建立的连接
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 允许SSH (限制速率)
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 允许HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 允许特定IP访问MySQL
iptables -A INPUT -p tcp -s 10.0.0.0/8 --dport 3306 -j ACCEPT

# 记录并丢弃其他入站连接
iptables -A INPUT -j LOG --log-prefix "IPTABLES-DROP: "
iptables -A INPUT -j DROP

# 保存规则
iptables-save > /etc/iptables/rules.v4
```

### nftables 配置示例

```bash
#!/bin/bash
# nftables (iptables successor) 配置示例

cat > /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        
        # 允许本地回环
        iif "lo" accept
        
        # 允许已建立的连接
        ct state established,related accept
        
        # 丢弃无效连接
        ct state invalid drop
        
        # 允许ICMP (ping)
        ip protocol icmp accept
        ip6 nexthdr icmpv6 accept
        
        # 允许SSH (带速率限制)
        tcp dport 22 ct state new limit rate 5/minute accept
        
        # 允许HTTP/HTTPS
        tcp dport { 80, 443 } accept
        
        # 允许DNS
        udp dport 53 accept
        tcp dport 53 accept
        
        # 日志并计数
        counter log prefix "nftables-drop: " drop
    }
    
    chain forward {
        type filter hook forward priority 0; policy drop;
    }
    
    chain output {
        type filter hook output priority 0; policy accept;
    }
}
EOF

# 应用配置
nft -f /etc/nftables.conf
```

---

## 云防火墙

### AWS Security Groups

```yaml
# AWS Security Group (Terraform配置示例)
resource "aws_security_group" "web_server" {
  name        = "web-server-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  # 入站规则
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from anywhere"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP from anywhere"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # 仅允许内网
    description = "SSH from internal"
  }

  # 出站规则
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "web-server-sg"
  }
}
```

### Azure Network Security Groups (NSG)

```json
{
  "type": "Microsoft.Network/networkSecurityGroups",
  "name": "web-nsg",
  "location": "eastus",
  "properties": {
    "securityRules": [
      {
        "name": "AllowHTTPS",
        "properties": {
          "protocol": "TCP",
          "sourcePortRange": "*",
          "destinationPortRange": "443",
          "sourceAddressPrefix": "Internet",
          "destinationAddressPrefix": "*",
          "access": "Allow",
          "priority": 100,
          "direction": "Inbound"
        }
      },
      {
        "name": "AllowSSH",
        "properties": {
          "protocol": "TCP",
          "sourcePortRange": "*",
          "destinationPortRange": "22",
          "sourceAddressPrefix": "VirtualNetwork",
          "destinationAddressPrefix": "*",
          "access": "Allow",
          "priority": 110,
          "direction": "Inbound"
        }
      },
      {
        "name": "DenyAllInbound",
        "properties": {
          "protocol": "*",
          "sourcePortRange": "*",
          "destinationPortRange": "*",
          "sourceAddressPrefix": "*",
          "destinationAddressPrefix": "*",
          "access": "Deny",
          "priority": 4096,
          "direction": "Inbound"
        }
      }
    ]
  }
}
```

---

## 防火墙最佳实践

```
防火墙规则设计原则：

1. 默认拒绝 (Default Deny)
   - 没有明确允许的流量一律拒绝
   - 白名单优于黑名单

2. 最小权限原则 (Principle of Least Privilege)
   - 仅开放必要的端口和服务
   - 限制源IP范围

3. 规则排序
   - 最具体的规则在前
   - 通用的允许/拒绝规则在后

4. 定期审计
   - 清理无用规则
   - 检查日志分析异常

5. 分层防御
   - 网络边界防火墙
   - 子网级ACL
   - 主机级防火墙
   - 应用级防火墙
```

---

## 面试要点

**Q1: 包过滤防火墙和状态检测防火墙的区别？**
> 包过滤防火墙仅基于单个数据包的头部信息（IP、端口）做决策，无状态感知；状态检测防火墙维护连接状态表，跟踪TCP握手和连接生命周期，能识别伪造的连接或非法的ACK包，安全性更高。

**Q2: iptables和nftables的区别？**
> nftables是iptables的继任者，使用统一的语法（取代iptables/ip6tables/arptables），支持动态规则更新，性能更好，语法更清晰。nftables使用表(table)、链(chain)、规则(rule)的层级结构，支持集合(set)和映射(map)简化配置。

**Q3: Security Group和NACL的区别？**
> Security Group是实例级别的有状态防火墙，只能设置允许规则，自动允许返回流量；NACL (Network ACL)是子网级别的无状态防火墙，支持允许和拒绝规则，需要显式配置入站和出站规则。

**Q4: WAF和传统防火墙的区别？**
> 传统防火墙工作在网络层和传输层，基于IP和端口过滤；WAF工作在应用层，理解HTTP协议，能检测SQL注入、XSS等应用层攻击，可基于请求内容做决策。

**Q5: 如何防止防火墙规则被绕过？**
> 分层防御：边界防火墙+主机防火墙；默认拒绝策略；定期审计规则；监控日志；限制管理接口访问；保持防火墙软件更新；使用IPS检测绕过尝试。

---

## 相关概念

- [IDS/IPS](./ids-ips.md) - 入侵检测与防护系统
- [VPN](./vpn.md) - 虚拟专用网络
- [DDoS防护](./ddos-protection.md) - 分布式拒绝服务攻击防护
- [网络扫描](./network-scanning.md) - 网络探测技术
- [网络层](../../computer-science/networks/network-layer.md) - 防火墙L3层操作
- [传输层](../../computer-science/networks/transport-layer.md) - 端口过滤基础
---

## 参考资料

1. "Network Security with nftables" by Steve Suehring
2. NIST Guidelines on Firewalls and Firewall Policy (SP 800-41)
3. AWS Security Groups Documentation
4. Azure Network Security Groups Best Practices
5. OWASP Web Application Firewall Best Practices
