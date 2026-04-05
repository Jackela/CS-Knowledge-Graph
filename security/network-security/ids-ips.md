# 入侵检测与防护系统 (IDS/IPS)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**入侵检测系统 (IDS, Intrusion Detection System)** 和 **入侵防护系统 (IPS, Intrusion Prevention System)** 是网络安全的核心组件，用于监控网络流量或系统活动，识别恶意行为并发出警报或自动阻断。

```
┌─────────────────────────────────────────────────────────────────┐
│                IDS vs IPS 架构对比                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   IDS (检测模式)                                                 │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                    │
│   │  流量   │───▶│  分析   │───▶│  告警   │                    │
│   │  镜像   │    │  引擎   │    │  SIEM   │                    │
│   └─────────┘    └─────────┘    └─────────┘                    │
│        ▲                                           人工响应      │
│   [SPAN端口]                                                     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   IPS (防护模式)                                                 │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                    │
│   │  流量   │───▶│  分析   │───▶│  阻断   │───▶ [丢弃/重置]    │
│   │  直联   │    │  引擎   │    │  动作   │                    │
│   └─────────┘    └─────────┘    └─────────┘                    │
│   [在线部署]                                      自动响应      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 检测方法

### 基于签名的检测 (Signature-based Detection)

通过匹配已知攻击的特征码（签名）来识别威胁，类似杀毒软件的病毒库机制。

```
签名检测原理：

攻击特征数据库
┌─────────────────────────────────────────┐
│ Signature ID │ Pattern                  │
├──────────────┼──────────────────────────┤
│ SID:1000001  │ alert tcp any any -> any │
│              │ 80 (msg:"SQL Injection"; │
│              │ content:"union select";  │
│              │ sid:1000001;)            │
├──────────────┼──────────────────────────┤
│ SID:1000002  │ alert tcp any any -> any │
│              │ 22 (msg:"SSH Brute";     │
│              │ flow:to_server;           │
│              │ content:"SSH";            │
│              │ detection_filter:track    │
│              │ by_src, count 5, seconds │
│              │ 60; sid:1000002;)        │
└──────────────┴──────────────────────────┘
         │
         ▼
    流量匹配引擎
         │
    ┌────┴────┐
    ▼         ▼
  匹配      不匹配
  (告警)    (放行)
```

**优点**：准确率高、误报率低、可识别具体攻击类型
**缺点**：无法检测未知威胁 (0-day)、需要频繁更新签名库

### 基于异常的检测 (Anomaly-based Detection)

建立正常行为基线 (Baseline)，偏离基线的行为被标记为异常。

```
异常检测流程：

Phase 1: 学习阶段
┌─────────────────────────────────────────┐
│  收集正常流量数据                        │
│  ├── 流量模式 (流量大小、频率)           │
│  ├── 协议行为 (标准协议使用)             │
│  ├── 时间模式 (工作时间访问)             │
│  └── 连接模式 (正常连接数)               │
│                                         │
│  生成正常行为基线                        │
└─────────────────────────────────────────┘
              │
              ▼
Phase 2: 检测阶段
┌─────────────────────────────────────────┐
│  实时流量    基线模型    偏差计算        │
│  ─────────▶  ───────▶   ───────▶       │
│                                         │
│  偏差值 > 阈值 ?                        │
│       ├── Yes → 告警 (异常)             │
│       └── No  → 正常                    │
└─────────────────────────────────────────┘
```

**优点**：可检测未知攻击、0-day漏洞利用
**缺点**：误报率高、需要大量训练数据、难以确定攻击类型

---

## 部署架构

### 网络IDS/IPS (NIDS/NIPS)

```
NIDS镜像部署：

[Internet] ──▶ [防火墙] ──▶ [交换机] ──▶ [内部网络]
                                │
                           [SPAN端口]
                                │
                                ▼
                           [NIDS传感器]
                                │
                           [管理控制台]

NIPS直联部署：

[Internet] ──▶ [防火墙] ──▶ [NIPS] ──▶ [交换机] ──▶ [内部网络]
                                (直联模式，在线阻断)
```

### 主机IDS (HIDS)

部署在单个主机上，监控系统调用、文件完整性、日志等。

```
HIDS组件：
┌─────────────────────────────────────────┐
│            主机操作系统                  │
│  ┌─────────────────────────────────┐   │
│  │         HIDS Agent               │   │
│  │  ┌─────────┐ ┌─────────┐        │   │
│  │  │文件完整性│ │日志监控 │        │   │
│  │  │监控(FIM)│ │(Log)    │        │   │
│  │  └─────────┘ └─────────┘        │   │
│  │  ┌─────────┐ ┌─────────┐        │   │
│  │  │系统调用 │ │rootkit  │        │   │
│  │  │监控     │ │检测     │        │   │
│  │  └─────────┘ └─────────┘        │   │
│  │           │                     │   │
│  │           ▼                     │   │
│  │  ┌─────────────────┐            │   │
│  │  │   安全事件聚合   │            │   │
│  │  │   & 告警发送    │            │   │
│  │  └─────────────────┘            │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## SNORT / Suricata

### SNORT规则示例

```bash
# SNORT规则格式：
# action protocol source_ip source_port -> dest_ip dest_port (options)

# 检测SQL注入攻击
alert tcp any any -> $HOME_NET 80 (
    msg:"SQL Injection - Union Select Detected";
    flow:to_server,established;
    content:"union";
    nocase;
    content:"select";
    nocase;
    distance:0;
    within:20;
    classtype:web-application-attack;
    sid:1000001;
    rev:1;
)

# 检测SSH暴力破解
alert tcp any any -> $HOME_NET 22 (
    msg:"SSH Brute Force Attempt";
    flow:to_server,established;
    content:"SSH-";
    depth:4;
    detection_filter:track by_src, count 5, seconds 60;
    classtype:attempted-admin;
    sid:1000002;
    rev:1;
)

# 检测端口扫描
alert tcp any any -> $HOME_NET any (
    msg:"NMAP TCP Scan";
    flags:S;
    detection_filter:track by_src, count 20, seconds 10;
    classtype:attempted-recon;
    sid:1000003;
    rev:1;
)
```

### Suricata配置

```yaml
# suricata.yaml 配置片段
%YAML 1.1
---
vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"
    EXTERNAL_NET: "!$HOME_NET"

af-packet:
  - interface: eth0
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes

# 规则文件路径
default-rule-path: /etc/suricata/rules
rule-files:
  - emerging-threats.rules
  - local.rules

# 输出配置
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      types:
        - alert
        - http
        - dns
        - tls
        - files
```

---

## 蜜罐 (Honeypots)

蜜罐是故意设置的诱饵系统，用于吸引和监控攻击者行为。

```
蜜罐部署架构：

┌─────────────────────────────────────────┐
│           生产网络                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ 服务器A │ │ 服务器B │ │ 服务器C │   │
│  └────┬────┘ └────┬────┘ └────┬────┘   │
│       └───────────┼───────────┘        │
│                   │                    │
│              [交换机]                   │
│                   │                    │
│            [VLAN隔离]                   │
│                   │                    │
│       ┌───────────┴───────────┐        │
│       ▼                       ▼        │
│  ┌─────────┐             ┌─────────┐   │
│  │  低交互蜜罐 │             │ 高交互蜜罐 │   │
│  │ (Honeyd) │             │ (真实系统)│   │
│  │ 模拟服务  │             │ 完整OS   │   │
│  └────┬────┘             └────┬────┘   │
│       │                       │        │
│       └───────┬───────────────┘        │
│               ▼                        │
│         [数据收集服务器]                 │
└─────────────────────────────────────────┘
```

**低交互蜜罐**：模拟服务，风险低，信息有限
**高交互蜜罐**：真实系统，风险高，信息丰富

---

## SIEM集成

```
SIEM数据流：

┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  防火墙  │   │  IDS/IPS │   │  服务器  │   │  终端   │
│  日志   │   │  告警   │   │  日志   │   │  日志   │
└────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │             │             │             │
     └─────────────┴──────┬──────┴─────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │    日志收集代理      │
              │  (Filebeat/Fluentd) │
              └─────────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │    消息队列         │
              │  (Kafka/Redis)      │
              └─────────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │    SIEM平台         │
              │ (Splunk/ELK/QRadar) │
              │                     │
              │ • 关联分析           │
              │ • 威胁情报           │
              │ • 可视化             │
              │ • 告警管理           │
              └─────────────────────┘
```

---

## 面试要点

**Q1: IDS和IPS的主要区别？**
> IDS是旁路检测模式，通过流量镜像分析，发现威胁后告警但不阻断；IPS是在线部署，串联在网络中，可实时阻断恶意流量。IDS重在"检测"，IPS重在"防护"。

**Q2: 签名检测和异常检测的优缺点？**
> 签名检测准确率高、误报低，但无法检测0-day攻击，依赖频繁更新特征库；异常检测可发现未知攻击，但误报率高，需要大量训练数据建立基线，且难以确定具体攻击类型。

**Q3: 如何减少IDS/IPS的误报？**
> 方法包括：精细调整签名阈值、使用上下文关联（如结合源IP信誉）、白名单机制、定期基线更新（异常检测）、多源确认（结合防火墙日志）、机器学习和行为分析。

**Q4: 蜜罐的作用是什么？有哪些类型？**
> 蜜罐用于吸引攻击者、收集攻击情报、研究攻击手法、分散攻击者注意力。类型：低交互蜜罐（模拟服务，风险低）、高交互蜜罐（真实系统，信息丰富但风险高）、研究型蜜罐（学术研究）、生产型蜜罐（企业防护）。

**Q5: SIEM在入侵检测中的作用？**
> SIEM (Security Information and Event Management) 收集多源安全日志，进行关联分析、模式识别、威胁情报匹配，提供统一的安全视图，帮助识别跨系统的复杂攻击链，满足合规审计要求。

---

## 相关概念

### 网络安全 (Network Security)

- [防火墙](./firewalls.md) - 网络流量过滤与访问控制
- [VPN](./vpn.md) - 虚拟专用网络加密通信
- [DDoS防护](./ddos-protection.md) - 拒绝服务攻击防护
- [网络扫描](./network-scanning.md) - 网络探测与发现技术
- [数据包分析](./packet-analysis.md) - 网络流量深度分析

### 密码学 (Cryptography)

- [哈希函数](../cryptography/hash-functions.md) - 用于日志完整性校验
- [对称加密](../cryptography/symmetric-encryption.md) - 流量加密基础
- [非对称加密](../cryptography/asymmetric-encryption.md) - 数字签名与密钥交换

### 计算机网络 (Computer Networks)

- [网络层](../../computer-science/networks/network-layer.md) - IP协议与路由分析
- [传输层](../../computer-science/networks/transport-layer.md) - TCP/UDP连接监控
- [HTTPS/TLS](../../computer-science/networks/https-tls.md) - 加密流量检测
- [DNS](../../computer-science/networks/dns.md) - 域名解析安全监控

### 系统与监控 (Systems & Monitoring)

- [进程](../../computer-science/systems/process.md) - 主机进程监控
- [文件系统](../../computer-science/systems/file-systems.md) - 文件完整性监控(FIM)
- [内存管理](../../computer-science/systems/memory-management.md) - 异常内存行为检测

---

## 参考资料

1. "Snort Intrusion Detection and Prevention Toolkit" by Brian Caswell
2. NIST SP 800-94: Guide to Intrusion Detection and Prevention Systems
3. Suricata Documentation: https://suricata.readthedocs.io/
4. "The Honeynet Project" - honeynet.org
5. MITRE ATT&CK Framework for intrusion analysis
