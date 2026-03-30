# 虚拟专用网络 (VPN)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**虚拟专用网络 (VPN, Virtual Private Network)** 通过公用网络（如互联网）建立加密的专用通信通道，实现远程安全访问和站点互联。VPN的核心价值在于提供数据机密性、完整性和身份认证。

```
┌─────────────────────────────────────────────────────────────────┐
│                    VPN应用场景                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  场景1: 远程访问VPN (Remote Access)                              │
│                                                                 │
│   [远程员工] ──Internet──▶ [VPN网关] ──▶ [企业内网]              │
│   192.168.1.2    加密隧道    公网IP     10.0.0.0/8               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  场景2: 站点互联VPN (Site-to-Site)                               │
│                                                                 │
│   [分公司A] ──VPN隧道──▶ [总部] ──VPN隧道──▶ [分公司B]           │
│   172.16.0.0/16      Internet      10.0.0.0/8    192.168.0.0/16 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  场景3: 个人VPN (Consumer VPN)                                   │
│                                                                 │
│   [用户设备] ──加密隧道──▶ [VPN服务器] ──▶ [目标网站]            │
│             (隐藏真实IP)   (出口节点)                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## VPN协议

### IPsec (Internet Protocol Security)

工作在网络层，为IP通信提供加密和认证，是企业站点互联的标准协议。

```
IPsec架构：

┌─────────────────────────────────────────┐
│           应用层 (HTTP/FTP/SSH)          │
├─────────────────────────────────────────┤
│           传输层 (TCP/UDP)               │
├─────────────────────────────────────────┤
│      IPsec层 (ESP/AH)                   │
│  ┌─────────────────────────────────┐   │
│  │  ESP (Encapsulating Security    │   │
│  │      Payload)                   │   │
│  │  • 加密 (Confidentiality)       │   │
│  │  • 完整性 (Integrity)           │   │
│  │  • 抗重放 (Anti-replay)         │   │
│  ├─────────────────────────────────┤   │
│  │  AH (Authentication Header)     │   │
│  │  • 完整性 (Integrity)           │   │
│  │  • 认证 (Authentication)        │   │
│  │  • 无加密                       │   │
│  └─────────────────────────────────┘   │
├─────────────────────────────────────────┤
│           网络层 (IP)                    │
└─────────────────────────────────────────┘

IPsec模式：

传输模式 (Transport Mode):
┌────────┬────────┬────────┬────────────────┐
│ IP头   │ ESP头  │  TCP   │     数据       │
│(修改)  │        │  头    │   (加密)       │
└────────┴────────┴────────┴────────────────┘

隧道模式 (Tunnel Mode):
┌────────┬────────┬────────┬────────┬────────┐
│ 新IP头 │ ESP头  │ 原IP头 │  TCP头 │  数据  │
│        │        │        │        │(加密)  │
└────────┴────────┴────────┴────────┴────────┘
```

**IKE (Internet Key Exchange)**：用于自动协商安全关联 (SA) 和密钥交换，分为两阶段：
- IKE Phase 1：建立安全通道（ISAKMP SA）
- IKE Phase 2：协商IPsec SA

### SSL/TLS VPN

基于Web浏览器或专用客户端，工作在应用层，易于部署。

```
SSL VPN类型：

1. SSL Portal VPN (Web模式)
   ┌─────────────────────────────────────────┐
   │  用户通过浏览器访问VPN门户               │
   │  通过Web界面访问内部资源                 │
   │  无需安装客户端                          │
   └─────────────────────────────────────────┘

2. SSL Tunnel VPN (隧道模式)
   ┌─────────────────────────────────────────┐
   │  安装轻量级客户端                        │
   │  建立完整网络层隧道                      │
   │  可访问所有网络资源                      │
   └─────────────────────────────────────────┘
```

### WireGuard

新一代VPN协议，使用现代加密技术，代码精简，性能优异。

```
WireGuard特点：

┌─────────────────────────────────────────┐
│  协议栈对比                              │
├─────────────────────────────────────────┤
│  WireGuard         IPsec/OpenVPN        │
│  ├─ 4000行代码      数万行代码           │
│  ├─ 内核实现        用户空间/内核        │
│  ├─ 现代加密        多种算法兼容         │
│  ├─ 无状态设计      复杂状态机           │
│  └─ 简单配置        复杂配置             │
└─────────────────────────────────────────┘

WireGuard加密套件：
• Curve25519 (ECDH密钥交换)
• ChaCha20-Poly1305 (AEAD加密)
• BLAKE2s (哈希)
• SipHash (MAC)
```

### OpenVPN

开源SSL VPN解决方案，基于OpenSSL，高度可配置。

```
OpenVPN架构：

传输层选项：
┌─────────────────────────────────────────┐
│  UDP模式 (默认)                          │
│  • 更好的NAT穿越能力                     │
│  • 更低的延迟                             │
│  • 更高效                                 │
├─────────────────────────────────────────┤
│  TCP模式                                 │
│  • 更好的防火墙穿透                       │
│  • TCP over TCP性能问题                   │
│  • 可靠性更高                             │
└─────────────────────────────────────────┘

OpenVPN模式：
• TUN模式：路由IP层数据包
• TAP模式：桥接以太网帧
```

---

## 隧道技术

### 隧道封装原理

```
VPN隧道封装过程：

原始数据包：
┌────────┬────────┬────────────────┐
│ IP头   │ TCP头  │     数据       │
│10.0.0.2│        │                │
└────────┴────────┴────────────────┘
      │
      ▼ 加密 + 封装
┌────────┬────────┬────────┬────────┐
│ 新IP头 │ VPN头  │ 加密IP │ 加密   │
│公网IP  │        │ 头     │ 数据   │
└────────┴────────┴────────┴────────┘
      │
      ▼ 通过公共网络传输

解封装过程相反
```

---

## 加密与认证

### 加密算法

```
VPN加密组件：

对称加密 (数据传输)：
┌─────────────────────────────────────────┐
│ 算法          密钥长度    性能          │
├─────────────────────────────────────────┤
│ AES-GCM       128/256    高 (硬件加速)  │
│ ChaCha20      256        高 (软件优化)  │
│ AES-CBC       128/256    中             │
└─────────────────────────────────────────┘

非对称加密 (密钥交换)：
┌─────────────────────────────────────────┐
│ 算法          用途                      │
├─────────────────────────────────────────┤
│ RSA           密钥交换/签名             │
│ ECDH          密钥交换 (PFS)            │
│ ECDSA         数字签名                  │
└─────────────────────────────────────────┘
```

### 完全前向保密 (PFS, Perfect Forward Secrecy)

```
PFS工作原理：

无PFS：
长期密钥泄露 ──▶ 所有历史会话可被解密

有PFS (使用临时DH密钥交换)：
每次会话生成临时密钥对
长期密钥仅用于认证
会话密钥泄露不影响其他会话

IPsec中：使用DH组 (Diffie-Hellman Groups)
OpenVPN中：tls-dh配置
WireGuard中：内置Curve25519临时密钥
```

---

## 分离隧道 (Split Tunneling)

```
分离隧道模式对比：

全隧道 (Full Tunnel)：
┌─────────────────────────────────────────┐
│  所有流量 ──▶ VPN ──▶ 企业网络           │
│                                         │
│  [用户] ──┬── 工作流量 ──▶ [公司资源]    │
│          └── 上网流量 ──▶ [公司出口]     │
│               (增加延迟，消耗带宽)        │
└─────────────────────────────────────────┘

分离隧道 (Split Tunnel)：
┌─────────────────────────────────────────┐
│  工作流量 ──▶ VPN ──▶ 企业网络           │
│  其他流量 ──▶ 直连 ──▶ 互联网            │
│                                         │
│  [用户] ──┬── 10.0.0.0/8 ──▶ [VPN]      │
│          └── 其他 ─────────▶ [直连]     │
│               (更好的性能，较低的安全)    │
└─────────────────────────────────────────┘
```

---

## 配置示例

### WireGuard配置

```bash
# 服务端配置 (/etc/wireguard/wg0.conf)
[Interface]
PrivateKey = <服务器私钥>
Address = 10.200.200.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
DNS = 8.8.8.8

# 客户端配置
[Peer]
PublicKey = <客户端公钥>
AllowedIPs = 10.200.200.2/32

# 客户端配置 (/etc/wireguard/wg0.conf)
[Interface]
PrivateKey = <客户端私钥>
Address = 10.200.200.2/24
DNS = 8.8.8.8

[Peer]
PublicKey = <服务器公钥>
Endpoint = vpn.example.com:51820
AllowedIPs = 10.200.200.0/24, 172.16.0.0/16
PersistentKeepalive = 25
```

### OpenVPN配置

```bash
# 服务端配置 (server.conf)
port 1194
proto udp
dev tun

ca ca.crt
cert server.crt
key server.key
dh dh.pem

topology subnet
server 10.8.0.0 255.255.255.0
push "route 172.16.0.0 255.255.0.0"
push "dhcp-option DNS 8.8.8.8"

# 启用TLS认证和PFS
tls-auth ta.key 0
cipher AES-256-GCM
auth SHA256
tls-version-min 1.2
tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384

# 保持连接
keepalive 10 120

# 权限下降
user nobody
group nogroup

# 日志
status openvpn-status.log
verb 3

# 客户端配置 (client.ovpn)
client
dev tun
proto udp
remote vpn.example.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun

ca ca.crt
cert client.crt
key client.key
remote-cert-tls server
tls-auth ta.key 1
cipher AES-256-GCM
auth SHA256

verb 3
```

### IPsec配置 (strongSwan)

```bash
# /etc/ipsec.conf
conn site-to-site
    type=tunnel
    auto=start
    keyexchange=ikev2
    
    # 本地配置
    left=203.0.113.1
    leftsubnet=10.0.0.0/8
    leftcert=serverCert.pem
    leftid="CN=vpn.example.com"
    
    # 远程配置
    right=198.51.100.1
    rightsubnet=192.168.0.0/16
    rightid="CN=remote.example.com"
    
    # 认证
    authby=rsasig
    
    # 加密配置
    ike=aes256-sha256-modp2048!
    esp=aes256-sha256!
    
    # DPD (Dead Peer Detection)
    dpddelay=30
    dpdtimeout=90
    dpdaction=restart
```

---

## 面试要点

**Q1: IPsec的传输模式和隧道模式有什么区别？**
> 传输模式只加密数据部分，保留原始IP头，适用于端到端通信；隧道模式封装整个原始数据包并添加新IP头，适用于VPN网关之间通信，隐藏内部网络拓扑。

**Q2: 什么是完全前向保密 (PFS)？**
> PFS确保即使长期私钥泄露，也无法解密历史会话数据。通过每次会话使用临时DH密钥交换实现，会话密钥仅用于该次会话，不会存储或重复使用。

**Q3: WireGuard相比OpenVPN有什么优势？**
> WireGuard代码精简（约4000行 vs 数万行），易于审计；使用现代加密算法（Curve25519、ChaCha20-Poly1305）；内核实现性能更高；无状态设计简化配置；连接建立更快。

**Q4: SSL VPN和IPsec VPN各自的优缺点？**
> SSL VPN：易于部署（基于浏览器）、NAT穿透好、细粒度访问控制，但性能略低；IPsec：网络层透明、标准化程度高、站点互联成熟，但配置复杂、NAT穿越困难。

**Q5: 什么是分离隧道？有什么安全考虑？**
> 分离隧道允许部分流量走VPN、部分直连。优点是降低延迟、节省带宽；安全风险是用户设备可能成为内外网之间的桥梁，需要配合端点安全策略（EDR、防火墙）使用。

---

## 相关概念

- [防火墙](./firewalls.md) - 网络边界防护
- [IDS/IPS](./ids-ips.md) - 入侵检测与防护
- [数据包分析](./packet-analysis.md) - 网络流量分析

---

## 参考资料

1. "OpenVPN 2 Cookbook" by Jan Just Keijser
2. WireGuard Official Documentation: https://www.wireguard.com/
3. NIST SP 800-77: Guide to IPsec VPNs
4. RFC 4301 - Security Architecture for the Internet Protocol
5. RFC 8446 - The Transport Layer Security (TLS) Protocol Version 1.3
