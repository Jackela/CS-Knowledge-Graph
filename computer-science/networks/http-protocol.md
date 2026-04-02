# HTTP 协议 (HTTP Protocol)

HTTP（HyperText Transfer Protocol，超文本传输协议）是互联网上应用最广泛的协议，用于客户端和服务器之间的通信。HTTP/1.1 是当前最广泛使用的版本，HTTP/2 和 HTTP/3 则提供了更高的性能。

## 核心概念

### HTTP 基础

```
HTTP 通信模型：

客户端                                      服务器
   │                                          │
   │ ─────────── HTTP Request ─────────────▶ │
   │  GET /index.html HTTP/1.1               │
   │  Host: www.example.com                  │
   │  User-Agent: Mozilla/5.0                │
   │                                         │
   │ ◀────────── HTTP Response ───────────── │
   │  HTTP/1.1 200 OK                        │
   │  Content-Type: text/html                │
   │  Content-Length: 1234                   │
   │                                         │
   │  <html>...</html>                       │
   │                                          │

特点：
- 无状态：每个请求独立，服务器不保存会话信息
- 基于请求-响应：客户端发起，服务器响应
- 可扩展：通过 Header 扩展功能
```

### URL 结构

```
https://user:pass@www.example.com:8080/path/to/resource?key1=value1&key2=value2#fragment

├─┘   ├─────────────────────────────┤  ├──┘ ├─────────────────┤  ├──────────────┤  ├───────┤
│               │                           │                              │            │
协议          认证信息                      主机地址                      路径        查询参数    锚点
(Scheme)      (Authority)                 (Host:Port)                   (Path)      (Query)    (Fragment)
```

### HTTP 方法

| 方法 | 描述 | 幂等性 | 安全性 | 用途 |
|------|------|--------|--------|------|
| **GET** | 获取资源 | ✅ | ✅ | 读取数据 |
| **POST** | 创建资源 | ❌ | ❌ | 提交数据 |
| **PUT** | 完整更新 | ✅ | ❌ | 替换资源 |
| **PATCH** | 部分更新 | ❌ | ❌ | 修改部分 |
| **DELETE** | 删除资源 | ✅ | ❌ | 删除资源 |
| **HEAD** | 获取头部 | ✅ | ✅ | 检查资源 |
| **OPTIONS** | 查询支持 | ✅ | ✅ | CORS 预检 |

```
RESTful API 示例：

GET    /api/users          # 获取用户列表
GET    /api/users/123      # 获取特定用户
POST   /api/users          # 创建用户
PUT    /api/users/123      # 完整更新用户
PATCH  /api/users/123      # 部分更新用户
DELETE /api/users/123      # 删除用户
```

## HTTP 报文格式

### 请求报文

```http
POST /api/users HTTP/1.1                    ← 请求行 (方法 路径 协议)
Host: api.example.com                       ← 请求头
Content-Type: application/json              ← 请求头
Content-Length: 56                          ← 请求头
Authorization: Bearer token123              ← 请求头
Accept: application/json                    ← 请求头
                                            ← 空行
{"name": "John", "email": "john@example.com"}  ← 请求体
```

### 响应报文

```http
HTTP/1.1 201 Created                        ← 状态行 (协议 状态码 状态描述)
Content-Type: application/json              ← 响应头
Content-Length: 78                          ← 响应头
Server: nginx/1.18.0                        ← 响应头
Set-Cookie: session=abc123; HttpOnly        ← 响应头
                                            ← 空行
{"id": 123, "name": "John", "created": "2024-01-15"}  ← 响应体
```

### 状态码

| 类别 | 范围 | 说明 |
|------|------|------|
| **1xx** | 100-199 | 信息响应 |
| **2xx** | 200-299 | 成功 |
| **3xx** | 300-399 | 重定向 |
| **4xx** | 400-499 | 客户端错误 |
| **5xx** | 500-599 | 服务器错误 |

```
常用状态码：

200 OK              - 请求成功
201 Created         - 资源创建成功
204 No Content      - 成功但无返回内容

301 Moved Permanently  - 永久重定向
302 Found              - 临时重定向
304 Not Modified       - 缓存有效

400 Bad Request     - 请求格式错误
401 Unauthorized    - 未认证
403 Forbidden       - 无权限
404 Not Found       - 资源不存在
429 Too Many Requests - 请求过多

500 Internal Server Error - 服务器内部错误
502 Bad Gateway      - 网关错误
503 Service Unavailable - 服务不可用
```

## HTTP/2

### 主要改进

```
HTTP/1.1 vs HTTP/2：

HTTP/1.1 (串行)：                HTTP/2 (多路复用)：
┌─────┐                          ┌─────────────────┐
│ Req │─────────────────────────▶│ Req1 Req2 Req3  │
└─────┘                          └─────────────────┘
   │                                      │
   ▼                                      ▼
┌─────┐                          ┌─────────────────┐
│ Res │◀─────────────────────────│ Res1 Res2 Res3  │
└─────┘                          └─────────────────┘
   │                                      │
   ▼                                      ▼
┌─────┐                          ┌─────────────────┐
│ Req │─────────────────────────▶│ (单个连接)       │
└─────┘                          └─────────────────┘

HTTP/2 特性：
- 二进制分帧层
- 多路复用 (Multiplexing)
- 头部压缩 (HPACK)
- 服务器推送
- 流优先级
```

### 二进制分帧

```
HTTP/2 帧结构：

┌──────────────────────────────────────────────────────────┐
│                    HTTP/2 Frame                          │
├───────────┬───────────┬───────────┬──────────────────────┤
│ Length    │ Type      │ Flags     │ Reserved + Stream ID │
│ (24 bits) │ (8 bits)  │ (8 bits)  │ (1 + 31 bits)        │
├───────────┴───────────┴───────────┴──────────────────────┤
│                       Payload                            │
│                    (Length bytes)                        │
└──────────────────────────────────────────────────────────┘

帧类型：
- HEADERS   - 头部信息
- DATA      - 请求/响应体
- SETTINGS  - 连接设置
- PRIORITY  - 流优先级
- RST_STREAM - 流重置
- PING      - 心跳检测
- GOAWAY    - 连接终止
```

## HTTP/3

### 基于 QUIC

```
HTTP/3 架构：

HTTP/1.1:  HTTP ──▶ TCP ──▶ IP
HTTP/2:    HTTP ──▶ TCP ──▶ IP  
HTTP/3:    HTTP ──▶ QUIC ──▶ UDP ──▶ IP

QUIC 优势：
- 基于 UDP，避免 TCP 队头阻塞
- 内置 TLS 1.3（加密成为必需）
- 0-RTT 连接建立
- 连接迁移（IP 变化保持连接）
- 改进的拥塞控制
```

## 相关概念 (Related Concepts)

### 网络安全
- [HTTPS/TLS](./https-tls.md) - HTTP 安全传输
- [Web 安全](../../security/web-security.md) - Web 应用安全

### Web 技术
- [DNS](./dns.md) - 域名解析系统

### 性能优化
- [负载均衡](../distributed-systems/load-balancing.md) - 流量分发

## 参考资料

1. RFC 7230-7235 - HTTP/1.1 规范
2. RFC 7540 - HTTP/2 规范
3. RFC 9114 - HTTP/3 规范
4. RFC 9204 - QPACK 头部压缩
5. Ilya Grigorik - High Performance Browser Networking
