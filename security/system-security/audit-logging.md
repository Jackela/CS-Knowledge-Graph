# 审计日志 (Audit Logging)

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、合规标准及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**审计日志 (Audit Logging)** 是系统安全运营的核心组件，用于记录安全相关事件和用户活动。完整的审计日志不仅用于事后取证分析，还能支持实时安全监控、合规性报告和异常行为检测。审计日志系统需要平衡安全性、性能和隐私，确保日志的完整性、不可篡改性和可用性。

```
┌─────────────────────────────────────────────────────────────────┐
│                   审计日志系统架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   日志来源                                                       │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│   │ 应用日志 │ │ 系统日志 │ │ 安全日志 │ │ 网络日志 │ │ 数据库 │  │
│   │ 登录/操作│ │ 进程/文件│ │ 防火墙  │ │ 流量分析 │ │ 查询   │  │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
│        │           │           │           │           │       │
│        └───────────┴───────────┴───────────┴───────────┘       │
│                            │                                    │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  日志收集层 (Log Collection)                              │  │
│   │  • Fluentd/Fluent Bit • Logstash • Filebeat              │  │
│   │  • 日志解析、过滤、标准化                                 │  │
│   └─────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  日志传输层 (Log Transport)                               │  │
│   │  • 加密传输 (TLS) • 压缩 • 批处理 • 断点续传              │  │
│   └─────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  日志存储层 (Log Storage)                                 │  │
│   │  • Elasticsearch • Splunk • Loki • S3/GCS               │  │
│   │  • 冷热分层 • 压缩 • 备份                                │  │
│   └─────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  日志分析层 (Log Analysis)                                │  │
│   │  • 实时告警 • 关联分析 • 机器学习异常检测                │  │
│   │  • SIEM (Splunk, QRadar, Sentinel)                     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  可视化与报告 (Visualization)                             │  │
│   │  • Kibana • Grafana • 合规报告 • 取证分析                │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 审计日志原则

```
┌─────────────────────────────────────────────────────────────────┐
│                   审计日志核心原则                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. 完整性 (Integrity)                                         │
│      • 防止日志被篡改或删除                                    │
│      • 使用数字签名或哈希链                                    │
│      • WORM (Write Once Read Many) 存储                        │
│                                                                 │
│   2. 不可否认性 (Non-repudiation)                               │
│      • 唯一标识每个操作者                                      │
│      • 记录时间戳和会话信息                                    │
│      • 数字签名验证                                            │
│                                                                 │
│   3. 可追溯性 (Traceability)                                    │
│      • 完整记录操作上下文                                      │
│      • 支持跨系统关联分析                                      │
│      • 保留足够的历史数据                                      │
│                                                                 │
│   4. 及时性 (Timeliness)                                        │
│      • 实时或准实时采集                                        │
│      • 快速检索和分析                                          │
│      • 实时告警能力                                            │
│                                                                 │
│   5. 最小化 (Minimization)                                      │
│      • 只记录必要信息                                          │
│      • 敏感数据脱敏                                            │
│      • 遵守隐私法规 (GDPR/CCPA)                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 日志级别和分类

| 级别 | 描述 | 示例 | 保留时间 |
|------|------|------|----------|
| **DEBUG** | 调试信息 | 函数调用参数 | 7 天 |
| **INFO** | 一般信息 | 用户登录成功 | 30 天 |
| **NOTICE** | 重要信息 | 配置变更 | 90 天 |
| **WARNING** | 警告 | 权限提升尝试 | 1 年 |
| **ERROR** | 错误 | 认证失败 | 1 年 |
| **CRITICAL** | 严重 | 多次登录失败 | 3 年 |
| **ALERT** | 需立即处理 | 可能的入侵 | 3 年 |
| **EMERGENCY** | 系统不可用 | 安全事件 | 永久 |

---

## 实现方式

### 1. 结构化审计日志

```python
import json
import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class AuditEventType(Enum):
    """审计事件类型"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    ADMIN_ACTION = "admin_action"
    SECURITY_EVENT = "security_event"
    SYSTEM_EVENT = "system_event"

class AuditSeverity(Enum):
    """审计严重级别"""
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    ALERT = "alert"
    EMERGENCY = "emergency"

@dataclass
class AuditEvent:
    """审计事件结构"""
    # 基本信息
    event_id: str
    timestamp: str
    event_type: str
    severity: str
    
    # 主体信息
    actor_type: str  # user, service, system
    actor_id: str
    actor_name: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # 操作信息
    action: str  # create, read, update, delete, login, logout
    resource_type: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    
    # 结果
    status: str  # success, failure, denied, error
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    
    # 上下文
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # 变更详情（用于数据修改）
    before_value: Optional[Dict] = None
    after_value: Optional[Dict] = None
    changed_fields: Optional[List[str]] = None
    
    # 元数据
    application: Optional[str] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, secret_key: str, app_name: str = "app", 
                 environment: str = "production"):
        self.secret_key = secret_key
        self.app_name = app_name
        self.environment = environment
        self.log_buffer: List[AuditEvent] = []
        self.buffer_size = 100
    
    def _generate_event_id(self) -> str:
        """生成唯一事件 ID"""
        return str(uuid.uuid4())
    
    def _sign_event(self, event: AuditEvent) -> str:
        """
        对事件进行数字签名
        用于后续验证日志完整性
        """
        event_data = event.to_json()
        signature = hmac.new(
            self.secret_key.encode(),
            event_data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def log(self, event_type: AuditEventType, severity: AuditSeverity,
            action: str, resource_type: str, status: str,
            actor_type: str = "user", actor_id: str = None,
            **kwargs) -> AuditEvent:
        """
        记录审计事件
        
        示例:
            audit.log(
                event_type=AuditEventType.AUTHENTICATION,
                severity=AuditSeverity.INFO,
                action="login",
                resource_type="system",
                status="success",
                actor_id="user123",
                ip_address="192.168.1.100"
            )
        """
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.utcnow().isoformat() + 'Z',
            event_type=event_type.value,
            severity=severity.value,
            actor_type=actor_type,
            actor_id=actor_id or "anonymous",
            action=action,
            resource_type=resource_type,
            status=status,
            application=self.app_name,
            environment=self.environment,
            **kwargs
        )
        
        # 添加到缓冲区
        self.log_buffer.append(event)
        
        # 批量刷新
        if len(self.log_buffer) >= self.buffer_size:
            self.flush()
        
        # 立即输出关键事件
        if severity in (AuditSeverity.CRITICAL, AuditSeverity.ALERT, 
                       AuditSeverity.EMERGENCY):
            self._output_event(event)
        
        return event
    
    def flush(self):
        """刷新日志缓冲区"""
        for event in self.log_buffer:
            self._output_event(event)
        self.log_buffer.clear()
    
    def _output_event(self, event: AuditEvent):
        """输出事件（实际应发送到日志系统）"""
        # 添加签名
        signature = self._sign_event(event)
        
        log_entry = {
            **event.to_dict(),
            '_signature': signature
        }
        
        # 输出到 stdout（实际应发送到 ELK/Splunk 等）
        print(json.dumps(log_entry, ensure_ascii=False, default=str))
    
    def verify_log_integrity(self, log_entry: Dict) -> bool:
        """验证日志条目的完整性"""
        signature = log_entry.pop('_signature', None)
        if not signature:
            return False
        
        event_data = json.dumps(log_entry, ensure_ascii=False, default=str, 
                               sort_keys=True)
        expected = hmac.new(
            self.secret_key.encode(),
            event_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)


# 装饰器：自动审计
from functools import wraps

def audit_log(action: str, resource_type: str, 
              event_type: AuditEventType = AuditEventType.DATA_ACCESS):
    """审计装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取当前用户信息（实际应从上下文获取）
            actor_id = kwargs.get('user_id', 'unknown')
            
            try:
                result = func(*args, **kwargs)
                
                # 记录成功
                audit_logger.log(
                    event_type=event_type,
                    severity=AuditSeverity.INFO,
                    action=action,
                    resource_type=resource_type,
                    status="success",
                    actor_id=actor_id
                )
                
                return result
            except Exception as e:
                # 记录失败
                audit_logger.log(
                    event_type=event_type,
                    severity=AuditSeverity.ERROR,
                    action=action,
                    resource_type=resource_type,
                    status="error",
                    actor_id=actor_id,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator


# 初始化审计日志记录器
audit_logger = AuditLogger(
    secret_key=secrets.token_hex(32),
    app_name="myapp",
    environment="production"
)
```

### 2. 安全事件检测规则

```python
from typing import List, Dict, Callable
from datetime import datetime, timedelta
import re

class SecurityRule:
    """安全检测规则"""
    
    def __init__(self, name: str, description: str, 
                 severity: str, condition: Callable):
        self.name = name
        self.description = description
        self.severity = severity
        self.condition = condition


class SecurityRuleEngine:
    """安全规则引擎"""
    
    def __init__(self):
        self.rules: List[SecurityRule] = []
        self.recent_events: List[Dict] = []
        self.window_size = timedelta(minutes=5)
    
    def add_rule(self, rule: SecurityRule):
        """添加检测规则"""
        self.rules.append(rule)
    
    def process_event(self, event: Dict) -> List[Dict]:
        """
        处理事件并返回触发的告警
        """
        # 添加到事件窗口
        self.recent_events.append(event)
        self._cleanup_old_events()
        
        alerts = []
        for rule in self.rules:
            if rule.condition(event, self.recent_events):
                alerts.append({
                    'rule_name': rule.name,
                    'description': rule.description,
                    'severity': rule.severity,
                    'event': event,
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return alerts
    
    def _cleanup_old_events(self):
        """清理过期事件"""
        cutoff = datetime.utcnow() - self.window_size
        self.recent_events = [
            e for e in self.recent_events 
            if datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) > cutoff
        ]


# 预定义安全规则
SECURITY_RULES = [
    SecurityRule(
        name="multiple_failed_logins",
        description="5分钟内3次登录失败",
        severity="warning",
        condition=lambda event, history: (
            event.get('event_type') == 'authentication' and
            event.get('action') == 'login' and
            event.get('status') == 'failure' and
            sum(1 for e in history 
                if e.get('actor_id') == event.get('actor_id') and
                e.get('event_type') == 'authentication' and
                e.get('status') == 'failure') >= 3
        )
    ),
    
    SecurityRule(
        name="privilege_escalation",
        description="权限提升尝试",
        severity="critical",
        condition=lambda event, history: (
            event.get('event_type') == 'authorization' and
            event.get('action') == 'escalate' and
            event.get('status') == 'attempt'
        )
    ),
    
    SecurityRule(
        name="unusual_access_hours",
        description="非工作时间访问",
        severity="notice",
        condition=lambda event, history: (
            event.get('event_type') in ['authentication', 'data_access'] and
            (datetime.utcnow().hour < 6 or datetime.utcnow().hour > 22)
        )
    ),
    
    SecurityRule(
        name="sensitive_data_access",
        description="敏感数据访问",
        severity="warning",
        condition=lambda event, history: (
            event.get('resource_type') in ['ssn', 'credit_card', 'health_record'] and
            event.get('action') == 'read'
        )
    ),
    
    SecurityRule(
        name="impossible_travel",
        description="不可能的旅行（短时间内异地登录）",
        severity="alert",
        condition=lambda event, history: (
            event.get('event_type') == 'authentication' and
            event.get('action') == 'login' and
            any(
                e.get('actor_id') == event.get('actor_id') and
                e.get('ip_address') != event.get('ip_address') and
                abs((datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')) -
                     datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00'))).total_seconds()) < 3600
                for e in history
            )
        )
    ),
]

# 初始化规则引擎
rule_engine = SecurityRuleEngine()
for rule in SECURITY_RULES:
    rule_engine.add_rule(rule)
```

### 3. 日志完整性保护

```python
import hashlib
import json
from typing import List, Dict
from datetime import datetime

class LogIntegrityChain:
    """
    日志完整性保护
    使用区块链类似的哈希链技术
    """
    
    def __init__(self):
        self.chain: List[Dict] = []
        self.previous_hash = "0" * 64
    
    def add_block(self, log_entries: List[Dict]) -> Dict:
        """
        添加日志块到链
        """
        block = {
            'index': len(self.chain),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'logs': log_entries,
            'previous_hash': self.previous_hash,
        }
        
        # 计算当前块哈希
        block_hash = self._calculate_hash(block)
        block['hash'] = block_hash
        
        # 更新链
        self.chain.append(block)
        self.previous_hash = block_hash
        
        return block
    
    def _calculate_hash(self, block: Dict) -> str:
        """计算块哈希"""
        block_string = json.dumps(block, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def verify_chain(self) -> bool:
        """
        验证链的完整性
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # 验证当前块哈希
            if current['hash'] != self._calculate_hash({
                'index': current['index'],
                'timestamp': current['timestamp'],
                'logs': current['logs'],
                'previous_hash': current['previous_hash']
            }):
                return False
            
            # 验证链的连接
            if current['previous_hash'] != previous['hash']:
                return False
        
        return True
    
    def get_tampered_blocks(self) -> List[int]:
        """检测被篡改的块"""
        tampered = []
        
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            if current['previous_hash'] != previous['hash']:
                tampered.append(i)
        
        return tampered


# 远程日志发送（防篡改）
class SecureLogShipper:
    """安全日志发送器"""
    
    def __init__(self, remote_endpoint: str, api_key: str):
        self.endpoint = remote_endpoint
        self.api_key = api_key
    
    def ship_logs(self, logs: List[Dict]) -> bool:
        """
        发送日志到远程服务器
        包含完整性签名
        """
        import requests
        
        # 添加签名
        payload = {
            'logs': logs,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'sender': 'audit-system'
        }
        
        signature = hmac.new(
            self.api_key.encode(),
            json.dumps(payload, sort_keys=True, default=str).encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'X-Signature': signature,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            # 发送失败，保存到本地重试队列
            self._queue_for_retry(logs)
            return False
    
    def _queue_for_retry(self, logs: List[Dict]):
        """添加到重试队列"""
        # 实际实现应持久化到磁盘
        pass
```

---

## 应用场景

### 场景 1: 合规审计报告

```python
class ComplianceReporter:
    """合规报告生成器"""
    
    COMPLIANCE_REQUIREMENTS = {
        'SOX': {
            'data_retention_days': 2555,  # 7年
            'required_events': ['data_modification', 'admin_action'],
            'immutable_storage': True
        },
        'GDPR': {
            'data_retention_days': 365,
            'required_events': ['data_access', 'data_deletion'],
            'pii_masking': True
        },
        'PCI_DSS': {
            'data_retention_days': 365,
            'required_events': ['authentication', 'authorization'],
            'tamper_protection': True
        },
        'HIPAA': {
            'data_retention_days': 2555,
            'required_events': ['phi_access', 'phi_modification'],
            'encryption_at_rest': True
        }
    }
    
    def generate_report(self, compliance_type: str, 
                       start_date: datetime, 
                       end_date: datetime) -> Dict:
        """
        生成合规报告
        """
        requirements = self.COMPLIANCE_REQUIREMENTS.get(compliance_type)
        if not requirements:
            raise ValueError(f"Unknown compliance type: {compliance_type}")
        
        # 查询相关事件
        events = self._query_events(
            event_types=requirements['required_events'],
            start=start_date,
            end=end_date
        )
        
        # 验证完整性
        integrity_check = self._verify_log_integrity(events)
        
        report = {
            'compliance_type': compliance_type,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': len(events),
                'unique_users': len(set(e['actor_id'] for e in events)),
                'security_incidents': len([e for e in events if e['severity'] in ['critical', 'alert']])
            },
            'integrity': {
                'verified': integrity_check,
                'chain_valid': True
            },
            'events': events
        }
        
        return report
```

---

## 面试要点

### Q1: 审计日志和安全日志的区别？

**A:**

| 特性 | 审计日志 (Audit Log) | 安全日志 (Security Log) |
|------|---------------------|------------------------|
| 范围 | 所有用户活动和系统事件 | 仅安全相关事件 |
| 目的 | 合规、审计、追溯 | 威胁检测、响应 |
| 保留 | 长期（多年） | 中期（数月） |
| 内容 | 详细的业务上下文 | 攻击指标(IOCs) |
| 用户 | 审计员、合规官 | 安全分析师、SOC |

### Q2: 如何保证日志不被篡改？

**A:**

**技术措施:**
1. **哈希链**: 每个日志条目包含前一个条目的哈希
2. **数字签名**: 对日志块进行 HMAC 签名
3. **WORM 存储**: 一次写入多次读取的存储介质
4. **远程日志**: 实时发送到只读的远程 SIEM
5. **区块链**: 分布式验证

**管理措施:**
1. 分离日志管理权限
2. 定期完整性检查
3. 多副本存储

### Q3: 日志中如何保护敏感数据？

**A:**

```python
# 脱敏策略
SENSITIVE_PATTERNS = {
    'ssn': (r'\d{3}-\d{2}-\d{4}', 'XXX-XX-XXXX'),
    'credit_card': (r'\d{4}-\d{4}-\d{4}-\d{4}', 'XXXX-XXXX-XXXX-XXXX'),
    'email': (r'(\w{2})\w+@(\w+\.\w+)', r'\1***@\2'),
    'password': (r'"password":\s*"[^"]*"', '"password": "***"')
}

def sanitize_log(log_entry: Dict) -> Dict:
    """日志脱敏"""
    log_str = json.dumps(log_entry)
    
    for pattern_name, (pattern, replacement) in SENSITIVE_PATTERNS.items():
        log_str = re.sub(pattern, replacement, log_str)
    
    return json.loads(log_str)
```

---

## 相关概念

### 数据结构
- [队列](../computer-science/data-structures/queue.md)：日志缓冲和批处理
- [哈希表](../computer-science/data-structures/hash-table.md)：日志索引

### 算法
- [哈希算法](../cryptography/hash-functions.md)：日志完整性验证
- [签名算法](../cryptography/digital-signatures.md)：日志签名

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：日志查询性能

### 系统实现
- [日志系统](../computer-science/systems/logging.md)：分布式日志
- [监控告警](../cloud-devops/monitoring.md)：日志监控

### 安全领域
- [身份认证](../application-security/authentication.md)：认证审计
- [访问控制](./access-control.md)：权限审计
- [入侵检测](./intrusion-detection.md)：安全事件检测

---

## 参考资料

1. [NIST SP 800-92 - Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
2. [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
3. [PCI DSS Logging Requirements](https://www.pcisecuritystandards.org/)
4. [GDPR Logging Guidelines](https://gdpr.eu/article-30-records-of-processing/)
