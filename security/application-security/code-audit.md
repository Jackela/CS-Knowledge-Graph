# 代码审计 (Code Audit)

## 概念

代码审计（Code Audit）是对软件源代码进行系统性检查的过程，旨在发现安全漏洞、质量缺陷、合规问题和性能隐患。它是保障软件安全和质量的重要手段。

## 审计类型

| 类型 | 关注点 | 工具/方法 |
|------|--------|-----------|
| **安全审计** | 发现安全漏洞 | SAST、DAST、人工审查 |
| **质量审计** | 代码规范、设计质量 | SonarQube、CodeClimate |
| **合规审计** | 许可证、标准遵循 | FOSSology、合规扫描 |
| **性能审计** | 性能瓶颈、资源泄漏 | Profiler、静态分析 |

## 安全审计重点

### 常见漏洞检查

```
┌─────────────────────────────────────────┐
│           OWASP Top 10 审计点            │
├─────────────────────────────────────────┤
│                                         │
│   1. 注入攻击 (SQL/NoSQL/Command)        │
│   2. 失效的身份认证                       │
│   3. 敏感数据暴露                         │
│   4. XML外部实体                          │
│   5. 失效的访问控制                       │
│   6. 安全配置错误                         │
│   7. 跨站脚本 (XSS)                      │
│   8. 不安全的反序列化                     │
│   9. 使用已知漏洞组件                     │
│  10. 不足的日志监控                       │
│                                         │
└─────────────────────────────────────────┘
```

### 审计检查清单

#### 输入验证
- [ ] 所有用户输入都经过验证
- [ ] 使用白名单而非黑名单
- [ ] 参数化查询防止SQL注入
- [ ] 输出编码防止XSS

#### 认证与会话
- [ ] 强密码策略
- [ ] 多因素认证
- [ ] 安全的会话管理
- [ ] 防止暴力破解

#### 敏感数据
- [ ] 加密存储敏感信息
- [ ] 传输层加密 (TLS)
- [ ] 密钥安全存储
- [ ] 数据脱敏

## 审计流程

```
1. 准备阶段
   ├── 确定审计范围
   ├── 收集文档和代码
   └── 制定审计计划

2. 执行阶段
   ├── 自动扫描
   ├── 人工审查
   └── 漏洞验证

3. 报告阶段
   ├── 分类分级
   ├── 修复建议
   └── 审计报告

4. 修复验证
   ├── 开发修复
   ├── 验证修复
   └── 回归测试
```

## 自动化工具

### 静态应用安全测试 (SAST)

| 工具 | 语言支持 | 特点 |
|------|----------|------|
| SonarQube | 多语言 | 全面的质量和安全扫描 |
| Checkmarx | 多语言 | 企业级SAST |
| Fortify | 多语言 | HP企业方案 |
| Semgrep | 多语言 | 轻量级、规则灵活 |
| Bandit | Python | Python专用 |
| ESLint Security | JavaScript | JS/TS安全规则 |

### 动态应用安全测试 (DAST)

- OWASP ZAP
- Burp Suite
- Netsparker

## 人工审计技巧

### 高风险代码模式

```python
# 危险: 命令注入
def run_command(user_input):
    os.system(f"ping {user_input}")  # 危险!

# 安全: 使用参数化命令
import subprocess
def run_command_safe(host):
    subprocess.run(["ping", "-c", "4", host])  # 安全
```

```python
# 危险: SQL注入
def get_user(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    
# 安全: 参数化查询
def get_user_safe(username):
    query = "SELECT * FROM users WHERE name = ?"
    cursor.execute(query, (username,))
```

## 审计报告模板

```
# 代码审计报告

## 项目信息
- 项目名称:
- 审计日期:
- 审计人员:
- 代码版本:

## 执行摘要
- 总体评级: [严重/高/中/低]
- 发现漏洞数:
- 建议优先级:

## 详细发现

### 高危漏洞
1. [标题]
   - 位置: 文件路径:行号
   - 描述: 漏洞详情
   - 影响: 潜在风险
   - 修复建议: 具体修复方案

### 中危漏洞
...

### 低危问题
...

## 合规性检查
- 许可证合规: [通过/失败]
- 编码规范: [通过/失败]

## 修复计划
| 优先级 | 问题 | 负责人 | 截止日期 |
|--------|------|--------|----------|
| P0     | ...  | ...    | ...      |
```

## 相关概念

### 安全
- [常见漏洞](../common-vulnerabilities.md) - OWASP Top 10详解
- [Web安全](../web-security.md) - Web应用安全
- [DevSecOps](../application-security/devsecops.md) - 安全左移

### 代码质量
- [代码质量](../../software-engineering/code-quality.md) - 代码质量维度
- [代码审查](../../software-engineering/code-review.md) - 人工代码检查
- [单元测试](../../software-engineering/unit-testing.md) - 自动化验证

### 合规
- [Secrets管理](../application-security/secrets-management.md) - 密钥安全管理

## 参考资料

1. OWASP Code Review Guide
2. "The Art of Software Security Assessment" by Mark Dowd
3. "Secure Coding in C and C++" by Robert Seacord
4. CWE/SANS Top 25 Most Dangerous Software Errors
