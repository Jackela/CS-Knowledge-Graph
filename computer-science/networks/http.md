# HTTP 协议

## 简介

**HTTP（HyperText Transfer Protocol，超文本传输协议）** 是Web应用的基础通信协议，用于客户端和服务器之间的请求-响应交互。

---

## HTTP 版本演进

### HTTP/1.0 (1996)
- 短连接：每个请求建立新TCP连接
- 无状态协议

### HTTP/1.1 (1997)
- **持久连接**（Keep-Alive）
- **管道化**（Pipelining）
- **分块传输**（Chunked Transfer）
- **缓存控制**

### HTTP/2 (2015)
- **二进制分帧**
- **多路复用**（Multiplexing）
- **头部压缩**（HPACK）
- **服务器推送**

### HTTP/3 (2022)
- 基于 **QUIC/UDP**
- 解决队头阻塞
- 更快连接建立

---

## 请求报文结构

```
GET /api/users HTTP/1.1          ← 请求行
Host: example.com                ← 请求头
Accept: application/json
Authorization: Bearer token
Content-Type: application/json
Content-Length: 45
                                 ← 空行
{"name": "John", "age": 30}      ← 请求体
```

### 常见请求方法

| 方法 | 描述 | 幂等性 |
|------|------|--------|
| GET | 获取资源 | ✓ |
| POST | 创建资源 | ✗ |
| PUT | 全量更新 | ✓ |
| PATCH | 部分更新 | ✗ |
| DELETE | 删除资源 | ✓ |
| HEAD | 获取头部 | ✓ |
| OPTIONS | 预检请求 | ✓ |

---

## 响应报文结构

```
HTTP/1.1 200 OK                  ← 状态行
Content-Type: application/json   ← 响应头
Content-Length: 123
Cache-Control: max-age=3600
                                 ← 空行
{"id": 1, "name": "John"}        ← 响应体
```

### 状态码分类

| 范围 | 类别 |
|------|------|
| 1xx | 信息响应 |
| 2xx | 成功 |
| 3xx | 重定向 |
| 4xx | 客户端错误 |
| 5xx | 服务器错误 |

### 常见状态码

| 代码 | 含义 | 场景 |
|------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 301 | Moved Permanently | 永久重定向 |
| 304 | Not Modified | 缓存有效 |
| 400 | Bad Request | 请求格式错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务不可用 |

---

## 头部字段

### 通用头部

```
Cache-Control: no-cache, no-store
Connection: keep-alive
Date: Mon, 23 May 2023 22:38:34 GMT
```

### 请求头部

```
Accept: text/html, application/json
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: session=abc123
User-Agent: Mozilla/5.0
```

### 响应头部

```
Content-Encoding: gzip
Content-Type: application/json; charset=utf-8
ETag: "33a64df5"
Last-Modified: Wed, 21 Oct 2015 07:28:00 GMT
Set-Cookie: session=xyz789; HttpOnly; Secure
```

---

## 缓存机制

### 缓存控制策略

```
Cache-Control: no-store        # 不缓存
Cache-Control: no-cache        # 协商缓存
Cache-Control: max-age=3600    # 强缓存1小时
Cache-Control: private         # 仅浏览器缓存
Cache-Control: public          # 共享缓存
```

### 协商缓存

```
客户端                     服务器
  │  GET /resource         │
  │  If-None-Match: "abc"  │
  ├───────────────────────→│
  │  304 Not Modified      │
  │  (使用本地缓存)         │
  │←───────────────────────┤
```

---

## 面试要点

### Q1: GET vs POST
- GET幂等、可缓存、参数在URL
- POST非幂等、不可缓存、参数在Body

### Q2: HTTP/1.1 vs HTTP/2
- HTTP/2二进制、多路复用、头部压缩
- HTTP/1.1文本、串行、重复头部

### Q3: 幂等性
- 多次执行结果相同：GET、PUT、DELETE
- 非幂等：POST、PATCH

---

## 相关概念

### 安全
- [HTTPS](./https-tls.md) - HTTP的安全版本
- [Web安全](../../security/web-security.md) - Web应用安全

### 网络
- [DNS](./dns.md) - 域名解析
- [传输层](./transport-layer.md) - TCP/UDP
- [网络层](./network-layer.md) - IP协议

### 架构
- [REST API](../../software-engineering/api-design.md) - 基于HTTP的API设计
- [API网关](../../software-engineering/architecture-patterns/api-gateway.md) - HTTP请求路由
