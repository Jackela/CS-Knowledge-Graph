# 网络扫描 (Network Scanning)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**网络扫描 (Network Scanning)** 是探测目标网络以发现存活主机、开放端口、运行服务和潜在漏洞的技术。作为安全评估的基础环节，网络扫描在渗透测试、资产发现和网络安全审计中发挥关键作用。

```
┌─────────────────────────────────────────────────────────────────┐
│                    网络扫描类型                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  发现扫描 (Discovery)                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • 主机发现 (Ping Sweep)                                   │   │
│  │ • 端口扫描 (Port Scanning)                                │   │
│  │ • 服务识别 (Service Detection)                            │   │
│  │ • 操作系统指纹 (OS Fingerprinting)                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  安全扫描 (Security Assessment)                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • 漏洞扫描 (Vulnerability Scanning)                       │   │
│  │ • 配置审计 (Configuration Audit)                          │   │
│  │ • 合规检查 (Compliance Check)                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 端口扫描技术

### TCP扫描方法

```
TCP扫描类型对比：

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  SYN扫描 (-sS)  半开扫描                                     │
│  ┌─────────┐        ┌─────────┐                            │
│  │ Scanner │──SYN──▶│ Target  │                            │
│  │         │◀─SYN/ACK│ :80    │ ← 开放                      │
│  │         │──RST──▶│         │  (不完成握手，隐蔽)          │
│  └─────────┘        └─────────┘                            │
│                                                             │
│  Connect扫描 (-sT) 全连接扫描                                │
│  ┌─────────┐        ┌─────────┐                            │
│  │ Scanner │──SYN──▶│ Target  │                            │
│  │         │◀─SYN/ACK        │                            │
│  │         │──ACK──▶│         │  完成三次握手               │
│  │         │──RST──▶│         │  易被日志记录               │
│  └─────────┘        └─────────┘                            │
│                                                             │
│  NULL/FIN/Xmas扫描 隐蔽扫描                                  │
│  ┌─────────┐        ┌─────────┐                            │
│  │ Scanner │──FIN──▶│ Target  │  发送异常标志位             │
│  │         │◀──RST──│ :80     │  ← 关闭端口返回RST         │
│  │         │(无响应)│         │  ← 开放端口无响应           │
│  └─────────┘        └─────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘

ACK扫描 (-sA): 用于检测防火墙规则，判断端口是否被过滤
Window扫描 (-sW): 类似ACK扫描，利用窗口大小判断状态
```

### UDP扫描

```
UDP扫描原理：

开放端口:                   关闭端口:
┌─────────┐                ┌─────────┐
│ Scanner │──UDP──▶        │ Scanner │──UDP──▶
│         │                │         │
│         │◀─UDP响应       │         │◀─ICMP不可达
│         │  (如DNS响应)   │         │  (Type 3, Code 3)
└─────────┘                └─────────┘

注意: UDP扫描速度慢，因为ICMP响应有速率限制
```

---

## Nmap扫描技术

### 基础扫描命令

```bash
# 主机发现 (Ping Sweep)
nmap -sn 192.168.1.0/24
nmap -sn 10.0.0.1-254

# TCP SYN扫描 (半开扫描，需要root)
sudo nmap -sS -p 1-65535 192.168.1.1

# TCP Connect扫描 (普通用户可用)
nmap -sT -p 22,80,443 192.168.1.1

# UDP扫描
sudo nmap -sU -p 53,161,162 192.168.1.1

# 操作系统识别
sudo nmap -O 192.168.1.1

# 服务版本检测
nmap -sV -p 22,80,443 192.168.1.1

# 综合扫描 (OS + 版本 + 脚本)
sudo nmap -A 192.168.1.1
```

### NSE脚本扫描

```bash
# Nmap Scripting Engine (NSE)

# 漏洞扫描脚本
nmap --script=vuln 192.168.1.1

# 特定漏洞检查
nmap --script=smb-vuln-ms17-010 192.168.1.1
nmap --script=http-shellshock --script-args uri=/cgi-bin/test.cgi 192.168.1.1

# 信息收集脚本
nmap --script=banner 192.168.1.1
nmap --script=dns-brute domain.com
nmap --script=http-enum 192.168.1.1

# 认证检查
nmap --script=ssh-auth-methods 192.168.1.1
nmap --script=mysql-empty-password 192.168.1.1

# 性能优化
nmap -T4 --min-rate 1000 -p- 192.168.1.1  # 快速全端口扫描
nmap -sS -Pn -n --open 192.168.1.0/24     # 跳过DNS和Ping
```

### Nmap输出格式

```bash
# 多种输出格式
nmap -oN normal.txt    # 普通文本
nmap -oX xml.xml       # XML格式
nmap -oG grep.txt      # Grepable格式
nmap -oA results       # 所有格式 (results.nmap, results.xml, results.gnmap)

# 与Metasploit集成
nmap -oX scan.xml 192.168.1.0/24
db_import scan.xml     # 导入Metasploit
```

---

## 服务识别与OS指纹

### 服务检测原理

```
服务指纹识别：

┌─────────────────────────────────────────┐
│ 1. 默认端口映射                          │
│    Port 22 → SSH                         │
│    Port 80 → HTTP                        │
│    Port 443 → HTTPS                      │
│    Port 3306 → MySQL                     │
├─────────────────────────────────────────┤
│ 2. Banner抓取                            │
│    连接后读取欢迎信息                     │
│    SSH-2.0-OpenSSH_8.2p1                 │
│    220 mail.example.com ESMTP Postfix    │
├─────────────────────────────────────────┤
│ 3. 协议探测                              │
│    发送协议特定请求                       │
│    分析响应特征                           │
├─────────────────────────────────────────┤
│ 4. 行为分析                              │
│    分析响应时间、错误消息                 │
│    识别具体版本和配置                     │
└─────────────────────────────────────────┘
```

### 操作系统指纹识别

```
TCP/IP栈指纹识别：

┌─────────────────────────────────────────┐
│ 探测特征：                               │
├─────────────────────────────────────────┤
│ • Initial TTL值                          │
│   - Windows: 128                         │
│   - Linux: 64                            │
│   - Cisco: 255                           │
│                                          │
│ • TCP窗口大小 (Window Size)              │
│   - 不同的OS有不同的默认值                │
│                                          │
│ • TCP选项 (TCP Options)                  │
│   - MSS, SACK, Timestamp, Window Scale   │
│   - 各OS实现不同                         │
│                                          │
│ • DF位 (Don't Fragment)                  │
│   - 不同OS对分片的处理方式                │
└─────────────────────────────────────────┘
```

---

## 漏洞扫描

### 漏洞扫描流程

```
┌─────────────────────────────────────────────────────────────┐
│                    漏洞扫描流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: 发现                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • 网络发现、端口扫描、服务识别                        │   │
│  │ • 生成目标资产清单                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  Phase 2: 评估                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • 版本匹配已知漏洞                                    │   │
│  │ • 配置审计 (弱密码、默认配置)                         │   │
│  │ • 漏洞验证 (安全测试)                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  Phase 3: 报告                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • 风险评级 (CVSS评分)                                 │   │
│  │ • 修复建议                                            │   │
│  │ • 复测验证                                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 常用扫描工具

```bash
# OpenVAS / Greenbone (综合漏洞扫描)
# 安装: sudo apt install openvas
sudo gvm-start
gvm-cli socket --xml "<get_configs/>"

# Nessus (商业扫描器)
# 专业版提供合规检查和配置审计

# Nikto (Web漏洞扫描)
nikto -h http://target.com
nikto -h 192.168.1.1 -p 80,443

# SQLMap (SQL注入检测)
sqlmap -u "http://target.com/page.php?id=1"
sqlmap -u "http://target.com/login" --data="user=1&pass=1"

# Dirb/Dirbuster (目录爆破)
dirb http://target.com /usr/share/wordlists/dirb/common.txt
gobuster dir -u http://target.com -w wordlist.txt

# Masscan (高速端口扫描)
sudo masscan -p1-65535 192.168.1.0/24 --rate=1000
```

---

## 授权扫描最佳实践

### 法律与合规

```
扫描授权检查清单：

□ 书面授权
  □ 明确扫描范围 (IP范围、系统列表)
  □ 扫描时间窗口
  □ 测试类型限制 (是否允许破坏性测试)
  □ 联系人信息

□ 风险评估
  □ 生产系统扫描风险
  □ 备份确认
  □ 回滚计划

□ 保密协议
  □ 数据保护
  □ 结果分发限制
```

### 扫描策略

```bash
# 减少影响的扫描选项

# 1. 限速扫描
nmap --max-rate 100 -T2 192.168.1.1

# 2. 避开关键时段
# 使用cron安排在维护窗口执行

# 3. 渐进式扫描
# 先扫描少量端口，确认无影响后再扩大范围
nmap -p 22,80,443 192.168.1.1      # 先扫描关键端口
nmap -p- --exclude-ports 1-1024    # 再扫描高端口

# 4. 避免破坏性脚本
nmap --script="safe and default" 192.168.1.1
# 避免: exploit, dos, intrusive类别

# 5. 通知与监控
# 扫描前通知运维团队
# 监控被扫描系统负载
```

---

## 防御扫描

```
检测与防御扫描：

┌─────────────────────────────────────────────────────────────┐
│ 1. 入侵检测 (IDS)                                            │
│    ┌─────────────────────────────────────────────────────┐   │
│    │ • Snort/Suricata规则检测扫描特征                      │   │
│    │ • 多次连接尝试告警                                      │   │
│    │ • 异常TCP标志组合检测                                   │   │
│    └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│ 2. 防火墙策略                                                │
│    ┌─────────────────────────────────────────────────────┐   │
│    │ • 限制连接速率                                          │   │
│    │ • 丢弃异常TCP包 (NULL, Xmas)                          │   │
│    │ • 端口敲门 (Port Knocking)                            │   │
│    └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│ 3. 欺骗与误导                                                │
│    ┌─────────────────────────────────────────────────────┐   │
│    │ • 所有端口开放 (浪费攻击者时间)                        │   │
│    │ • 蜜罐服务 (诱捕分析)                                  │   │
│    │ • 动态端口分配                                         │   │
│    └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│ 4. 减少信息泄露                                              │
│    ┌─────────────────────────────────────────────────────┐   │
│    │ • 修改默认Banner                                       │   │
│    │ • 禁用不必要的服务                                     │   │
│    │ • 统一TTL值 (防止OS识别)                               │   │
│    └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 面试要点

**Q1: SYN扫描和Connect扫描的区别？**
> SYN扫描发送SYN包后不完成三次握手，收到SYN/ACK即判定端口开放，更隐蔽且速度快；Connect扫描完成完整TCP连接，会被系统日志记录，但不需要root权限。

**Q2: 如何识别目标操作系统？**
> 通过TCP/IP栈指纹：Initial TTL值（Linux 64, Windows 128）、TCP窗口大小、TCP选项支持（MSS、SACK、Timestamp）、DF位设置等。Nmap使用这些特征匹配指纹数据库。

**Q3: 为什么要进行授权扫描？**
> 未经授权的扫描可能违反《网络安全法》等法规，属于违法行为。授权扫描明确范围和责任，保护测试人员和被测试组织，确保有应急联系人处理意外情况。

**Q4: UDP扫描为什么比TCP扫描慢？**
> UDP是无连接协议，开放端口可能无响应，扫描器需等待超时才能确定状态；ICMP端口不可达消息有速率限制(限速1秒/条)，大量关闭端口会显著减慢扫描速度。

**Q5: 如何防御端口扫描？**
> 部署IDS检测扫描行为；防火墙限制连接速率；使用端口敲门隐藏服务；修改默认Banner减少信息泄露；部署蜜罐分散注意力；实施最小开放端口原则。

---

## 相关概念

### 网络安全 (Network Security)
- [防火墙](../network-security/firewalls.md) - 网络流量控制与访问管理
- [IDS/IPS](../network-security/ids-ips.md) - 入侵检测与入侵防护系统
- [数据包分析](../network-security/packet-analysis.md) - 网络流量深度分析
- [DDoS防护](../network-security/ddos-protection.md) - 拒绝服务攻击防护策略
- [VPN](../network-security/vpn.md) - 虚拟专用网络

### 计算机网络 (Computer Networks)
- [网络层](../computer-science/networks/network-layer.md) - IP协议与路由原理
- [传输层](../computer-science/networks/transport-layer.md) - TCP/UDP协议基础
- [DNS](../computer-science/networks/dns.md) - 域名系统解析
- [HTTPS/TLS](../computer-science/networks/https-tls.md) - 安全传输协议

### 应用安全 (Application Security)
- [OWASP Top 10](../application-security/owasp-top-10.md) - 十大Web安全风险
- [SQL注入](../application-security/sql-injection.md) - 数据库注入攻击与防护
- [Web安全](../web-security.md) - Web应用安全防护
- [常见漏洞](../common-vulnerabilities.md) - 安全漏洞类型与分析

### 系统安全 (System Security)
- [访问控制](../system-security/access-control.md) - 身份认证与权限管理
- [权限提升](../system-security/privilege-escalation.md) - 提权攻击与防御
- [安全审计日志](../system-security/audit-logging.md) - 日志记录与审计
---

## 参考资料

1. "Nmap Network Scanning" by Gordon Lyon (Fyodor)
2. Nmap Official Documentation: https://nmap.org/book/
3. OWASP Testing Guide - Information Gathering
4. "The Art of Port Scanning" by Fyodor (Phrack Magazine)
5. CVE (Common Vulnerabilities and Exposures) Database
