# API设计 (API Design)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自RESTful API设计规范、gRPC官方文档及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 定义

**API (Application Programming Interface)** 是软件组件之间交互的接口定义。良好的API设计是系统可维护性和开发者体验的关键。

---

## API风格对比

| 风格 | 协议 | 特点 | 适用场景 |
|------|------|------|----------|
| **REST** | HTTP | 资源导向，无状态 | Web服务，移动后端 |
| **GraphQL** | HTTP | 客户端指定查询 | 复杂数据需求，聚合服务 |
| **gRPC** | HTTP/2 | 高性能，强类型 | 微服务内部通信 |
| **WebSocket** | WS | 全双工，实时 | 实时应用，聊天，游戏 |
| **Webhooks** | HTTP | 事件驱动，回调 | 异步通知，集成 |

---

## RESTful API设计

### 资源URI设计

```
资源命名规范：

✅ 正确：
GET    /users              # 获取用户列表
GET    /users/123          # 获取特定用户
POST   /users              # 创建用户
PUT    /users/123          # 全量更新用户
PATCH  /users/123          # 部分更新用户
DELETE /users/123          # 删除用户
GET    /users/123/orders   # 获取用户的订单

❌ 错误：
GET    /getUsers           # 不需要动词
GET    /users/get/123      # 不需要get
POST   /users/create       # POST已表示创建
GET    /deleteUser?id=123  # 使用DELETE方法
```

### HTTP状态码

| 类别 | 状态码 | 含义 | 使用场景 |
|------|--------|------|----------|
| 成功 | 200 | OK | 标准成功响应 |
| 成功 | 201 | Created | 资源创建成功 |
| 成功 | 204 | No Content | 删除成功，无返回体 |
| 客户端错误 | 400 | Bad Request | 请求参数错误 |
| 客户端错误 | 401 | Unauthorized | 未[认证](../security/authentication.md) |
| 客户端错误 | 403 | Forbidden | 无[权限](../security/authorization.md) |
| 客户端错误 | 404 | Not Found | 资源不存在 |
| 客户端错误 | 409 | Conflict | 资源冲突 |
| 客户端错误 | 422 | Unprocessable | 验证失败 |
| 服务器错误 | 500 | Internal Error | 服务器内部错误 |
| 服务器错误 | 502 | Bad Gateway | 网关错误 |
| 服务器错误 | 503 | Service Unavailable | 服务不可用 |

### 请求/响应格式

```json
// 成功响应示例
{
  "id": "123",
  "name": "张三",
  "email": "zhangsan@example.com",
  "created_at": "2024-01-15T08:30:00Z",
  "_links": {
    "self": { "href": "/users/123" },
    "orders": { "href": "/users/123/orders" }
  }
}

// 错误响应示例
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "邮箱格式不正确",
    "details": [
      {
        "field": "email",
        "message": "必须是有效的邮箱地址"
      }
    ]
  }
}

// 列表响应示例
{
  "data": [
    { "id": "1", "name": "用户1" },
    { "id": "2", "name": "用户2" }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5
  },
  "_links": {
    "self": { "href": "/users?page=1" },
    "next": { "href": "/users?page=2" },
    "last": { "href": "/users?page=5" }
  }
}
```

### 版本控制

```
URL版本（推荐）：
/api/v1/users
/api/v2/users

Header版本：
Accept: application/vnd.api.v1+json

Query参数版本（不推荐）：
/api/users?version=1
```

---

## gRPC设计

### Protocol Buffers定义

```protobuf
syntax = "proto3";

package user;

// 用户服务
service UserService {
  // 获取用户
  rpc GetUser(GetUserRequest) returns (User);
  
  // 创建用户
  rpc CreateUser(CreateUserRequest) returns (User);
  
  // 列出用户
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  
  // 流式获取用户更新
  rpc StreamUsers(StreamUsersRequest) returns (stream User);
}

// 消息定义
message User {
  string id = 1;
  string name = 2;
  string email = 3;
  google.protobuf.Timestamp created_at = 4;
  UserStatus status = 5;
}

enum UserStatus {
  UNKNOWN = 0;
  ACTIVE = 1;
  INACTIVE = 2;
  SUSPENDED = 3;
}

message GetUserRequest {
  string id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}
```

### gRPC vs REST

| 特性 | gRPC | REST |
|------|------|------|
| 协议 | HTTP/2 | HTTP/1.1或HTTP/2 |
| 格式 | Protobuf (二进制) | JSON/XML (文本) |
| 性能 | 高（二进制+压缩） | 中 |
| 浏览器支持 | 需gRPC-Web | 原生支持 |
| 可读性 | 低（需解码） | 高 |
| 强类型 | 是 | 否 |
| 流式 | 双向流 | 需额外协议 |

---

## GraphQL设计

### Schema定义

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
  createdAt: String!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  published: Boolean!
}

type Query {
  user(id: ID!): User
  users(limit: Int = 10, offset: Int = 0): [User!]!
  post(id: ID!): Post
  posts(filter: PostFilter): [Post!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}

input CreateUserInput {
  name: String!
  email: String!
}

input PostFilter {
  published: Boolean
  authorId: ID
}
```

### 查询示例

```graphql
# 客户端精确指定需要的数据
query GetUserWithPosts {
  user(id: "123") {
    name
    email
    posts(limit: 5) {
      title
      published
    }
  }
}

# 一次请求获取多个资源
query GetDashboardData {
  user(id: "123") {
    name
  }
  posts(limit: 10) {
    title
    author {
      name
    }
  }
}
```

---

## API安全

### 认证与授权

```
□ 使用[HTTPS](../computer-science/networks/https-tls.md)传输
□ 实现[身份认证](../security/authentication.md)
  - API Key：内部服务
  - JWT：用户认证
  - OAuth 2.0：第三方集成
□ 实现[权限控制](../security/authorization.md)
  - RBAC（基于角色）
  - ABAC（基于属性）
```

### 防护措施

```
□ 限流 (Rate Limiting)
  - 防止暴力破解
  - 防止资源耗尽
  
□ 输入验证
  - 参数类型检查
  - SQL注入防护
  - XSS防护
  
□ 敏感数据处理
  - 加密存储
  - 日志脱敏
  - 最小权限原则
```

---

## API文档

### OpenAPI (Swagger)示例

```yaml
openapi: 3.0.0
info:
  title: 用户管理API
  version: 1.0.0
  description: 用户管理系统的RESTful API

paths:
  /users:
    get:
      summary: 获取用户列表
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
    
    post:
      summary: 创建用户
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: 创建成功

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
    
    UserList:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/User'
        pagination:
          type: object
```

---

## 最佳实践

```
□ 设计优先：先设计API，再实现
□ 向后兼容：避免破坏性变更
□ 幂等性：PUT/DELETE应该幂等
□ 分页：列表接口必须分页
□ 过滤/排序：支持常见查询需求
□ 异步操作：耗时操作返回任务ID
□ 健康检查：提供/health端点
□ 指标监控：集成[监控](../cloud-devops/monitoring/prometheus.md)
```

---

## 相关概念

- [身份认证](../security/authentication.md) - API安全基础
- [授权](../security/authorization.md) - 权限控制
- [Web安全](../security/web-security.md) - 安全威胁防护
- [微服务](./architecture-patterns/microservices.md) - API架构风格
- [版本控制](../CONTRIBUTING.md) - API演进管理
- [时间复杂度](../references/time-complexity.md) - API性能分析
- [线性代数](../mathematics/linear-algebra.md) - 推荐系统API设计
- [授权](../security/authorization.md) - 权限控制
- [Web安全](../security/web-security.md) - 安全威胁防护
- [微服务](./architecture-patterns/microservices.md) - API架构风格
- [版本控制](../CONTRIBUTING.md) - API演进管理

---

## 参考资料

1. "RESTful Web APIs" by Leonard Richardson
2. [Google API Design Guide](https://cloud.google.com/apis/design)
3. [Microsoft REST API Guidelines](https://github.com/Microsoft/api-guidelines)
4. [gRPC官方文档](https://grpc.io/docs/)
5. [GraphQL官方文档](https://graphql.org/learn/)

---

*最后更新：2024年*
