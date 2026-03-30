# DNS (Domain Name System)

## 简介

**DNS（Domain Name System）**是互联网的"电话簿"，将人类可读的域名（如 www.example.com）转换为机器可读的IP地址（如 93.184.216.34）。

## 域名结构

```
域名的层次结构（从右到左）:

www.example.com.
│    │      │   │
│    │      │   └── 根域 (.)
│    │      └────── 顶级域 (TLD: com, org, net)
│    └───────────── 二级域 (example)
└────────────────── 主机名 (www)

完全限定域名（FQDN）: 以点结尾
```

### 顶级域分类

```
通用TLD (gTLD):
- .com: 商业
- .org: 组织
- .net: 网络
- .edu: 教育
- .gov: 政府

国家TLD (ccTLD):
- .cn: 中国
- .uk: 英国
- .jp: 日本

新gTLD:
- .app, .dev, .blog, .shop
```

## DNS查询过程

### 递归查询

```
用户 → 本地DNS → 根DNS → 顶级域DNS → 权威DNS
        ↑←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←┘

示例: 查询 www.example.com

1. 用户向本地DNS（ISP提供或8.8.8.8）查询
2. 本地DNS向根DNS查询 .com
3. 根DNS返回 .com TLD服务器地址
4. 本地DNS向 .com TLD查询 example.com
5. TLD返回 example.com 权威DNS地址
6. 本地DNS向权威DNS查询 www
7. 权威DNS返回 IP 93.184.216.34
8. 本地DNS缓存并返回给用户
```

### DNS记录类型

| 类型 | 名称 | 用途 |
|------|------|------|
| A | 地址记录 | 域名 → IPv4 |
| AAAA | IPv6地址 | 域名 → IPv6 |
| CNAME | 别名 | 域名 → 域名 |
| MX | 邮件交换 | 邮件服务器 |
| NS | 名称服务器 | 指定DNS服务器 |
| TXT | 文本 | 验证、SPF等 |
| SOA | 授权起始 | 区域管理信息 |
| PTR | 指针 | IP → 域名（反向） |

### 记录示例

```
example.com.    IN  A       93.184.216.34
example.com.    IN  AAAA    2606:2800:220:1:248:1893:25c8:1946
example.com.    IN  MX  10  mail.example.com.
example.com.    IN  NS      ns1.example.com.
www.example.com. IN CNAME   example.com.
example.com.    IN  TXT     "v=spf1 include:_spf.google.com ~all"
```

## DNS缓存

```
缓存层级:

1. 浏览器缓存
2. 操作系统缓存
3. 本地DNS服务器缓存
4. 上游DNS缓存

TTL (Time To Live): 缓存有效期
- 由权威服务器设置
- 到期后重新查询
```

## DNS安全

### DNS劫持

```
攻击方式:
1. 篡改本地hosts文件
2. 攻击路由器DNS设置
3. 污染DNS缓存
4. 中间人攻击

防护:
- DNS over HTTPS (DoH)
- DNS over TLS (DoT)
- DNSSEC
```

### DNSSEC

**DNS Security Extensions**：为DNS提供身份验证和完整性保护。

```
原理:
- 使用数字签名验证DNS响应
- 公钥基础设施（PKI）
- 防止缓存投毒

记录类型:
- RRSIG: 数字签名
- DNSKEY: 公钥
- DS: 委托签名者
```

## 常用工具

```bash
# dig - DNS查询工具
dig www.example.com
dig @8.8.8.8 www.example.com A
dig +trace www.example.com

# nslookup
nslookup www.example.com

# host
host www.example.com
host -t MX example.com
```

## 面试要点

### Q1: DNS使用什么传输层协议？

- **UDP**: 标准查询，端口53，速度快
- **TCP**: 区域传输、大响应（>512字节）、DNSSEC

### Q2: 为什么需要DNS而不是直接用hosts文件？

1. 分布式管理，无需每台机器配置
2. 支持动态更新
3. 可扩展性
4. 负载均衡（一个域名多个IP）

### Q3: CDN如何利用DNS？

```
用户查询 cdn.example.com

智能DNS根据:
- 用户地理位置
- 服务器负载
- 网络状况

返回最优的CDN节点IP
```

## 相关概念

- [HTTP协议](../networks/http-protocol.md) - 使用DNS解析
- [网络层](../networks/network-layer.md) - IP地址
- [负载均衡](../distributed-systems/load-balancing.md) - DNS负载均衡

## 参考资料

1. 《计算机网络：自顶向下方法》第2章 - 应用层
2. Domain Name System - Wikipedia
