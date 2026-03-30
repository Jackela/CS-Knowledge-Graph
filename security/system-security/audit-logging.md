# 审计与日志 (Audit & Logging)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、NIST标准及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**审计与日志 (Audit & Logging)** 是安全运营的基础组件，通过记录系统活动实现安全监控、事件响应、合规报告和取证分析。

```
┌─────────────────────────────────────────────────────────────────┐
│                   日志管理架构                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   日志生命周期:                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  生成  ─────▶  收集  ─────▶  存储  ─────▶  分析  ─────▶ │   │
│   │ 应用/系统    日志代理      存储系统      SIEM       告警 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   日志类型:                                                       │
│   ├─ 系统日志: /var/log/syslog, journald                        │
│   ├─ 认证日志: /var/log/auth.log, /var/log/secure               │
│   ├─ 应用日志: Web服务器、数据库、业务应用                      │
│   ├─ 审计日志: auditd, Windows Event Log                        │
│   ├─ 网络日志: 防火墙、IDS/IPS、NetFlow                         │
│   └─ 云日志: CloudTrail, Azure Monitor                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Linux Audit (auditd)

auditd 是Linux内核审计框架，可详细记录系统调用和文件访问。

```
┌─────────────────────────────────────────────────────────────────┐
│                   auditd 架构                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Kernel Audit Framework                                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Kernel Component (kauditd)                              │   │
│   │  • 拦截系统调用                                          │   │
│   │  • 根据规则匹配                                          │   │
│   │  • 生成审计记录                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│   User Space                                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  auditd (守护进程)                                       │   │
│   │  • 接收内核审计消息                                      │   │
│   │  • 写入日志文件                                          │   │
│   │  • 管理日志轮转                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   审计规则类型:                                                   │
│   ├─ Control Rules    - 修改审计系统行为                        │
│   ├─ File Watch Rules - 监控文件访问                            │
│   └─ System Call Rules- 监控系统调用                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**auditd 配置示例：**

```bash
# 安装auditd
$ sudo apt-get install auditd audispd-plugins

# 添加临时规则
$ sudo auditctl -w /etc/sudoers -p wa -k sudoers_changes
$ sudo auditctl -w /etc/passwd -p wa -k identity_changes

# 配置持久化规则 (/etc/audit/rules.d/audit.rules)
-D                      # 删除所有现有规则
-b 8192                 # 设置缓冲区大小

# 监控关键文件
-w /etc/passwd -p wa -k identity_changes
-w /etc/shadow -p wa -k identity_changes
-w /etc/sudoers -p wa -k sudoers_changes
-w /etc/ssh/sshd_config -p wa -k ssh_config_changes

# 监控特权命令
-a always,exit -F arch=b64 -S setuid -S setgid -k privilege_changes

# 重新加载规则
$ sudo augenrules --load

# 搜索审计日志
$ sudo ausearch -k sudoers_changes
$ sudo ausearch -ts today -k identity_changes

# 生成审计报告
$ sudo aureport --login --summary
```

---

## Windows Event Log

Windows 事件日志是Windows系统的核心审计机制。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Windows Event Log                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   日志类型:                                                       │
│   ├─ System Log       - 系统事件                               │
│   ├─ Application Log  - 应用程序事件                           │
│   ├─ Security Log     - 安全事件 (登录、对象访问)              │
│   └─ Forwarded Events - 从其他机器转发的事件                   │
│                                                                 │
│   安全日志关键事件ID:                                             │
│   ├─ 4624  - 登录成功                                           │
│   ├─ 4625  - 登录失败                                           │
│   ├─ 4634  - 注销                                               │
│   ├─ 4672  - 特权登录 (管理员)                                  │
│   ├─ 4720  - 创建用户                                           │
│   ├─ 4726  - 删除用户                                           │
│   └─ 7045  - 服务安装                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**PowerShell 日志管理：**

```powershell
# 获取事件日志列表
Get-WinEvent -ListLog *

# 查看安全日志
Get-WinEvent -LogName Security -MaxEvents 10

# 查找特定事件ID
Get-WinEvent -FilterHashtable @{
    LogName = "Security"
    ID = 4624, 4625
    StartTime = (Get-Date).AddDays(-1)
}

# 配置高级审计策略
auditpol /set /subcategory:"Process Creation" /success:enable

# 导出安全日志
wevtutil epl Security C:\\logs\\security_backup.evtx
```

---

## 集中式日志管理

```
┌─────────────────────────────────────────────────────────────────┐
│                   集中式日志架构                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Web服务器 ────┐                                                 │
│   数据库    ────┼──▶ Logstash ──▶ Elasticsearch ──▶ Kibana/SIEM │
│   防火墙    ────┘        (解析)         (存储)          (可视化) │
│                                                                 │
│   关键技术栈:                                                     │
│   • ELK Stack (Elasticsearch, Logstash, Kibana)                │
│   • Splunk                                                      │
│   • Fluentd/Fluent Bit                                          │
│   • Graylog                                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Filebeat 配置示例：**

```yaml
# /etc/filebeat/filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/auth.log
    - /var/log/secure
  fields:
    log_type: auth

- type: log
  enabled: true
  paths:
    - /var/log/audit/audit.log
  fields:
    log_type: audit

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "filebeat-%{[agent.version]}-%{+yyyy.MM.dd}"
```

---

## 日志保留与合规

```
┌─────────────────────────────────────────────────────────────────┐
│                   日志保留策略                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   保留要求 (按合规标准):                                          │
│   ┌────────────────────┬─────────────────┬──────────────────┐   │
│   │  标准              │ 最低保留期      │ 特殊要求          │   │
│   ├────────────────────┼─────────────────┼──────────────────┤   │
│   │  PCI DSS           │ 1年             │ 在线3个月         │   │
│   │  HIPAA             │ 6年             │ 审计追踪不可改    │   │
│   │  SOX               │ 7年             │ 财务相关日志      │   │
│   │  GDPR              │ 数据生命周期    │ 可应要求删除      │   │
│   │  网络安全法(中国)   │ 不少于6个月     │ 境内存储          │   │
│   └────────────────────┴─────────────────┴──────────────────┘   │
│                                                                 │
│   存储策略:                                                       │
│   ├─ 热存储 (Hot):   SSD存储，最近7-30天                        │
│   ├─ 温存储 (Warm):  标准磁盘，1-3个月                          │
│   ├─ 冷存储 (Cold):  对象存储，3个月-1年                        │
│   └─ 归档 (Archive): 磁带/Glacier，1年以上                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**日志轮转配置：**

```bash
# /etc/logrotate.d/custom
/var/log/application/*.log {
    daily                    # 每天轮转
    rotate 90               # 保留90个备份
    compress                # 压缩旧日志
    delaycompress           # 延迟压缩
    missingok               # 日志不存在不报错
    notifempty              # 空日志不轮转
    create 0644 appuser appgroup
}
```

---

## 日志防篡改

```
┌─────────────────────────────────────────────────────────────────┐
│                   日志完整性保护                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   技术措施:                                                       │
│   ├─ 只追加文件系统 (chattr +a)                                 │
│   ├─ 实时远程转发到SIEM                                         │
│   ├─ 数字签名 (rsyslog-gnutls)                                  │
│   ├─ WORM存储 (AWS S3 Glacier)                                  │
│   └─ 区块链/分布式存储                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## SIEM 集成

```
┌─────────────────────────────────────────────────────────────────┐
│                   SIEM 功能架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   主要SIEM产品:                                                   │
│   ┌────────────────────┬─────────────────────────────────────┐   │
│   │  商业产品          │  开源/免费                          │   │
│   ├────────────────────┼─────────────────────────────────────┤   │
│   │  Splunk            │  ELK Stack                         │   │
│   │  IBM QRadar        │  Wazuh                             │   │
│   │  Microsoft Sentinel│  Graylog                           │   │
│   │  ArcSight          │  OSSIM                             │   │
│   └────────────────────┴─────────────────────────────────────┘   │
│                                                                 │
│   核心功能:                                                       │
│   ├─ 日志收集和归一化                                            │
│   ├─ 实时事件关联分析                                            │
│   ├─ 安全告警和工单生成                                          │
│   ├─ 长期存储和合规报告                                          │
│   └─ 威胁情报集成                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Splunk SPL 查询示例：**

```spl
# 检测暴力破解攻击
index=auth (failed OR "4625")
| stats count by src_ip, user
| where count > 5
| eval severity=case(count>20,"high", count>10,"medium", true(), "low")

# 检测异常的sudo使用
index=linux key="privilege_escalation"
| eval hour=strftime(_time, "%H")
| where hour < 6 OR hour > 22
| stats count by user, command
```

---

## 面试要点

**Q1: auditd和普通系统日志有什么区别？**
> auditd基于内核审计框架，可记录详细的系统调用级别信息（文件访问、权限变更、进程执行），而syslog主要记录应用级别的事件。auditd提供更细粒度的安全审计，支持文件监控、系统调用追踪。

**Q2: 如何确保日志不被攻击者篡改？**
> 1) 实时转发到远程日志服务器或SIEM；2) 使用append-only文件属性(chattr +a)；3) 数字签名日志块；4) 使用WORM存储介质；5) 限制日志文件访问权限；6) 监控日志文件本身的访问和修改。

**Q3: 什么是SIEM？核心功能有哪些？**
> SIEM (Security Information and Event Management) 是安全信息和事件管理平台。核心功能：1) 集中收集各类日志；2) 日志归一化和丰富化；3) 实时事件关联分析；4) 安全告警和工单生成；5) 长期存储和合规报告；6) 威胁情报集成。

**Q4: PCI DSS对日志有什么要求？**
> PCI DSS要求：1) 记录所有系统组件的访问；2) 审计记录包含用户ID、事件类型、日期时间、结果、来源；3) 系统时钟同步(NTP)；4) 日志在线可用至少3个月；5) 日志保留至少1年；6) 文件完整性监控。

---

## 参考资料

1. NIST SP 800-92: Guide to Computer Security Log Management
2. PCI DSS Requirements and Security Assessment Procedures
3. Linux Audit Framework Documentation
4. Microsoft Security Auditing Overview
5. Splunk Documentation
6. Sigma Rules Repository: https://github.com/SigmaHQ/sigma
