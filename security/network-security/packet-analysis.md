# 数据包分析 (Packet Analysis)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**数据包分析 (Packet Analysis)** 是通过捕获和解析网络流量来诊断问题、分析行为和检测威胁的技术。作为网络工程师和安全分析师的核心技能，数据包分析在故障排查、安全取证和性能优化中具有不可替代的价值。

```
┌─────────────────────────────────────────────────────────────────┐
│                   数据包分析应用场景                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  网络故障   │  │  安全取证   │  │  性能分析   │             │
│  │  排查       │  │  分析       │  │  优化       │             │
│  │             │  │             │  │             │             │
│  │ • 连接超时  │  │ • 恶意流量  │  │ • 延迟分析  │             │
│  │ • 丢包分析  │  │ • 数据泄露  │  │ • 吞吐瓶颈  │             │
│  │ • DNS问题   │  │ • 入侵痕迹  │  │ • 协议效率  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  应用调试   │  │  合规审计   │  │  协议学习   │             │
│  │             │  │             │  │             │             │
│  │ • API调试   │  │ • 流量记录  │  │ • 协议实现  │             │
│  │ • 认证流程  │  │ • 行为审计  │  │ • 标准验证  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## TCP/IP数据包结构

### 以太网帧结构

```
以太网帧 (Ethernet Frame):

┌─────────┬─────────┬─────────┬──────────┬─────────┬─────────┐
│ 目的MAC  │ 源MAC   │  类型   │   数据    │  填充   │  校验   │
│  6字节  │  6字节  │ 2字节  │ 46-1500  │  可选   │ 4字节  │
│         │         │0x0800=IP│   字节   │         │  (FCS)  │
└─────────┴─────────┴─────────┴──────────┴─────────┴─────────┘

类型字段:
0x0800 = IPv4
0x86DD = IPv6
0x0806 = ARP
0x8100 = VLAN
```

### IP数据包结构

```
IPv4头部 (20-60字节):

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┤
│Version│  IHL  │Type of Service│          Total Length         │
├───────┴───────┴───────────────┴───────────────────────────────┤
│         Identification        │Flags│      Fragment Offset    │
├───────────────────────────────┴─────┴─────────────────────────┤
│  Time to Live │    Protocol   │         Header Checksum       │
├───────────────────────────────┴───────────────────────────────┤
│                       Source IP Address                       │
├───────────────────────────────────────────────────────────────┤
│                    Destination IP Address                     │
├───────────────────────────────────────────────────────────────┤
│                    Options (if IHL > 5)                       │
└───────────────────────────────────────────────────────────────┘

关键字段:
- Version: 4 (IPv4)
- IHL: 头部长度 (5 = 20字节)
- TTL: 生存时间 (每跳减1)
- Protocol: 6=TCP, 17=UDP, 1=ICMP
```

### TCP段结构

```
TCP头部 (20-60字节):

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├───────────────────────────────┬───────────────────────────────┤
│       Source Port             │       Destination Port        │
├───────────────────────────────┴───────────────────────────────┤
│                        Sequence Number                        │
├───────────────────────────────────────────────────────────────┤
│                    Acknowledgment Number                      │
├───────┴─┬─────┴───────────────┴───────────────────────────────┤
│  Data   │ Res │U|A|P|R|S|F│                               │
│ Offset  │ erv │R|C|S|S|Y|I│        Window Size              │
│         │     │G|K|H|T|N|N│                               │
├─────────┴─────┴─┴─┴─┴─┴─┴─┴───────────────────────────────────┤
│         Checksum              │         Urgent Pointer        │
├───────────────────────────────┴───────────────────────────────┤
│                    Options (optional)                         │
└───────────────────────────────────────────────────────────────┘

标志位 (Flags):
URG - 紧急指针有效
ACK - 确认号有效
PSH - 推送数据
RST - 重置连接
SYN - 同步序列号
FIN - 结束连接
```

---

## Wireshark使用

### 界面与过滤

```
Wireshark界面布局:

┌───────────────────────────────────────────────────────────────┐
│ 菜单栏  File Edit View Capture Analyze Statistics Help       │
├───────────────────────────────────────────────────────────────┤
│ 主工具栏 (开始/停止捕获、过滤器、着色等)                      │
├───────────────────────────────────────────────────────────────┤
│ 显示过滤器: [tcp.port == 80 && ip.addr == 192.168.1.1]       │
├───────────────────────────────────────────────────────────────┤
│ 数据包列表面板 (No.  Time  Source  Destination  Protocol Info)│
│ ┌─────┬──────────┬───────────┬───────────┬──────┬───────────┐ │
│ │  1  │ 0.000000 │ 192.168.1.1│ 93.184.216│ TCP  │ 80 → 443 [SYN]│ │
│ │  2  │ 0.045234 │ 93.184.216│ 192.168.1.1│ TCP  │ 443 → 80 [SYN, ACK]│ │
│ └─────┴──────────┴───────────┴───────────┴──────┴───────────┘ │
├───────────────────────────────────────────────────────────────┤
│ 数据包详情面板 (协议树)                                        │
│ ▼ Frame 1: 74 bytes on wire                                   │
│ ▼ Ethernet II, Src: ... Dst: ...                              │
│ ▼ Internet Protocol Version 4, Src: 192.168.1.1               │
│ ▼ Transmission Control Protocol, Src Port: 54321, Dst: 443    │
│   ▶ Transport Layer Security                                  │
├───────────────────────────────────────────────────────────────┤
│ 数据包字节面板 (原始十六进制和ASCII)                          │
│ 0000  00 50 56 c0 00 08 00 0c  29 3a 5b 4c 08 00 45 00   .PV.....):[L..E.│
│ 0010  00 3c 00 00 40 00 40 06  b5 4e c0 a8 01 01 5d b8   .<..@.@..N....].│
└───────────────────────────────────────────────────────────────┘
```

### 显示过滤器

```
Wireshark显示过滤器语法:

# 比较操作符
ip.addr == 192.168.1.1    # 等于
tcp.port != 80            # 不等于
tcp.window_size > 1000    # 大于
frame.len >= 100          # 大于等于

# 逻辑操作符
ip.addr == 192.168.1.1 && tcp.port == 80    # AND
ip.addr == 192.168.1.1 || ip.addr == 10.0.0.1  # OR
!tcp.port == 22                               # NOT

# 常用过滤器
ip.addr == 192.168.1.1          # 特定IP
tcp.port == 80                  # 特定端口
tcp.flags.syn == 1              # SYN包
tcp.flags.fin == 1              # FIN包
tcp.analysis.retransmission     # TCP重传
dns.qry.name contains "google"  # DNS查询包含
tpft                            # 慢HTTP
http.response.code == 404       # HTTP 404错误
ssl.handshake.type == 1         # SSL Client Hello
frame contains "password"       # 包含特定字符串

# 高级过滤器
tcp.stream eq 0                 # 特定TCP流
http.request.method == "POST"   # POST请求
icmp.type == 3                  # ICMP目的不可达
```

### 捕获过滤器

```
Tcpdump/Wireshark捕获过滤器语法 (BPF):

# 基本过滤
host 192.168.1.1                # 特定主机
net 192.168.1.0/24              # 特定网络
port 80                         # 特定端口
portrange 1000-2000             # 端口范围

# 协议过滤
tcp                             # TCP协议
udp                             # UDP协议
icmp                            # ICMP协议
not arp                         # 排除ARP

# 方向过滤
src host 192.168.1.1            # 源地址
dst port 443                    # 目的端口

# 组合过滤
tcp port 80 and host 192.168.1.1
tcp port 80 or tcp port 443
not port 22
src host 192.168.1.1 and dst port 80

# 高级用法
tcp[tcpflags] & tcp-syn != 0    # SYN包
tcp[13] & 0x02 != 0             # SYN (原始字节)
icmp[icmptype] == icmp-echo     # ICMP echo (ping)
```

---

## 协议分析

### HTTP分析

```
HTTP请求/响应示例:

请求:
GET /index.html HTTP/1.1\r\n
Host: www.example.com\r\n
User-Agent: Mozilla/5.0\r\n
Accept: text/html\r\n
Connection: keep-alive\r\n
\r\n

响应:
HTTP/1.1 200 OK\r\n
Date: Mon, 23 May 2023 22:38:34 GMT\r\n
Content-Type: text/html; charset=UTF-8\r\n
Content-Length: 138\r\n
\r\n
<html>...</html>

Wireshark分析要点:
- 检查HTTP方法 (GET/POST/PUT/DELETE)
- 查看状态码分布 (2xx/3xx/4xx/5xx)
- 分析请求/响应时间
- 检查Cookie和Session
- 识别异常User-Agent
- 检测明文传输的敏感信息
```

### DNS分析

```
DNS查询/响应:

查询:
┌─────────────────────────────────────────┐
│ Transaction ID: 0x1234                │
│ Flags: 0x0100 (Standard query)         │
│ Questions: 1                           │
│ Query: www.example.com, Type A, Class IN│
└─────────────────────────────────────────┘

响应:
┌─────────────────────────────────────────┐
│ Transaction ID: 0x1234                │
│ Flags: 0x8180 (Standard response)      │
│ Questions: 1                           │
│ Answer RRs: 1                          │
│ Answer: www.example.com A 93.184.216.34│
└─────────────────────────────────────────┘

DNS问题排查:
- 检查查询类型 (A/AAAA/MX/TXT)
- 查看响应码 (NOERROR/NXDOMAIN/SERVFAIL)
- 分析响应时间
- 检查TTL值
- 识别DNS劫持/污染
```

### TLS/SSL分析

```
TLS握手流程:

Client                           Server
  │ ───── ClientHello ─────────▶ │
  │   [支持的版本、密码套件、随机数]  │
  │                              │
  │ ◀──── ServerHello ────────── │
  │   [选定的版本、密码套件、随机数]  │
  │ ◀──── Certificate ────────── │
  │   [服务器证书链]              │
  │ ◀──── ServerKeyExchange ──── │
  │   [密钥交换参数]              │
  │ ◀──── ServerHelloDone ────── │
  │                              │
  │ ───── ClientKeyExchange ───▶ │
  │   [预主密钥加密]              │
  │ ───── ChangeCipherSpec ────▶ │
  │ ───── Finished ────────────▶ │
  │                              │
  │ ◀──── ChangeCipherSpec ───── │
  │ ◀──── Finished ───────────── │
  │                              │
  │ ═════ 加密应用数据 ═════════ │

Wireshark TLS分析:
- 解密TLS (需提供私钥或会话密钥)
- 检查证书链完整性
- 验证密码套件安全性
- 分析TLS版本 (1.0/1.1/1.2/1.3)
- 检测弱加密算法
```

---

## 故障排查场景

### TCP连接问题

```
连接超时分析:

正常三次握手:              连接超时:
Client    Server          Client    Server
  │ ─SYN─▶│               │ ─SYN─▶│
  │◀-SYN/ACK              │ (无响应)│
  │ -ACK─▶│               │ ─SYN──▶│ (重传1)
                           │ (无响应)│
                           │ ─SYN──▶│ (重传2)
                           │ (超时)  │

排查要点:
1. 检查SYN是否到达服务端
2. 检查是否有SYN/ACK返回
3. 检查中间防火墙是否拦截
4. 检查服务端是否监听端口
5. 检查回程路由是否正常

Wireshark过滤器: tcp.flags.syn == 1 && tcp.analysis.retransmission
```

### 慢速网络分析

```
性能问题诊断:

高延迟:                    丢包/重传:
┌─────────┐               ┌─────────┐
│  数据   │               │  Seq=1  │──▶
│  Seq=1  │──▶            │         │  (丢失)
│         │   等待ACK     │  Seq=1  │──▶ (重传)
│         │   (延迟高)    │◀─ACK=1001
│◀─ACK    │               │         │
└─────────┘               └─────────┘

Wireshark分析:
- Statistics -> TCP Stream Graphs -> Round Trip Time Graph
- tcp.analysis.ack_rtt > 0.1    # 高延迟ACK
- tcp.analysis.retransmission   # 重传包
- tcp.analysis.duplicate_ack    # 重复ACK
- tcp.analysis.lost_segment     # 丢失段
```

---

## 安全分析

### 恶意流量检测

```
攻击特征识别:

端口扫描:                  SYN Flood:
┌─────────┐               ┌─────────┐
│ SYN to  │               │ SYN     │──▶
│  port 1 │               │ SYN     │──▶
│ SYN to  │               │ SYN     │──▶
│  port 2 │               │ SYN     │──▶
│ ...     │               │ (无ACK) │
└─────────┘               └─────────┘
检测: 短时间内多端口SYN     检测: 大量SYN无完成握手

数据泄露检测:
- 异常大的出站流量
- 非工作时间的大量传输
- 连接到可疑IP/域名
- DNS隧道 (长域名查询)
- ICMP隧道
```

### 取证分析

```
网络取证要点:

1. 证据收集
   - 完整数据包捕获 (PCAP)
   - 时间戳同步 (NTP)
   - 链式 custody

2. 时间线重建
   - 按时间排序所有事件
   - 识别攻击入口点
   - 追踪横向移动

3. 关键证据提取
   - 恶意IP地址
   - C2通信模式
   - 下载的恶意文件
   - 窃取的数据

4. 报告生成
   - 原始PCAP保存
   - 关键包导出
   - 分析过程记录
```

---

## 面试要点

**Q1: TCP三次握手和四次挥手的过程？**
> 三次握手：SYN → SYN+ACK → ACK，建立双向连接；四次挥手：FIN → ACK → FIN → ACK，关闭双向连接。挥手需要四次因为被动关闭方可能还有数据要发送。

**Q2: Wireshark显示过滤器和捕获过滤器的区别？**
> 捕获过滤器在抓包前过滤，使用BPF语法，效率高但功能有限；显示过滤器在抓包后过滤，使用Wireshark语法，功能丰富可基于协议字段过滤，但处理全部流量。

**Q3: 如何使用Wireshark解密HTTPS流量？**
> 方法1：提供服务器私钥 (仅限RSA密钥交换，不支持ECDHE)；方法2：导出浏览器会话密钥 (SSLKEYLOGFILE环境变量)，Wireshark导入后解密，支持所有密钥交换算法。

**Q4: 如何排查网络延迟问题？**
> 使用Wireshark TCP Stream Graphs分析RTT；检查TCP重传和乱序包；分析窗口大小变化；对比客户端和服务端抓包确定延迟位置；检查DNS解析时间。

**Q5: 什么是TCP窗口缩放？为什么需要它？**
> TCP窗口缩放(Window Scale)是RFC 1323选项，解决标准TCP窗口字段16位(最大64KB)在高速网络中的瓶颈。通过缩放因子(0-14)将窗口扩展到1GB，适应高带宽延迟积网络。

---

## 相关概念

### 网络安全
- [入侵检测与防护系统 (IDS/IPS)](./ids-ips.md) - 实时监控与威胁检测
- [网络扫描](./network-scanning.md) - 主动网络探测技术
- [防火墙](./firewalls.md) - 网络流量访问控制
- [DDoS防护](./ddos-protection.md) - 分布式拒绝服务攻击防护
- [VPN](./vpn.md) - 虚拟专用网络加密通信
- [Web安全](../web-security.md) - Web应用数据包分析

### 计算机网络
- [网络层](./../../computer-science/networks/network-layer.md) - IP协议与路由原理
- [传输层](./../../computer-science/networks/transport-layer.md) - TCP/UDP协议详解
- [DNS协议](./../../computer-science/networks/dns.md) - 域名系统解析
- [HTTPS/TLS](./../../computer-science/networks/https-tls.md) - 传输层安全协议

### 协议分析
- [DNS分析](./../../computer-science/networks/dns.md) - 域名查询与响应分析
- [TCP/UDP协议](./../../computer-science/networks/transport-layer.md) - 传输层协议工作机制
- [TLS/SSL握手](./../../computer-science/networks/https-tls.md) - 安全连接建立过程

### 安全取证
- [哈希函数](./../cryptography/hash-functions.md) - 数据完整性校验
- [对称加密](./../cryptography/symmetric-encryption.md) - 数据加密保护
- [非对称加密](./../cryptography/asymmetric-encryption.md) - 公钥密码学应用
---

## 参考资料

1. "Wireshark Network Analysis" by Laura Chappell
2. "TCP/IP Illustrated, Volume 1" by W. Richard Stevens
3. Wireshark User Guide: https://www.wireshark.org/docs/
4. RFC 793 - Transmission Control Protocol
5. SANS Packet Analysis Cheat Sheet
