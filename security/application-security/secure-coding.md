# 安全编码实践 (Secure Coding Practices)

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、OWASP 指南及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**安全编码实践 (Secure Coding Practices)** 是一组在软件开发过程中遵循的原则、模式和具体技术，旨在从源代码层面消除安全漏洞。根据 OWASP 统计，约 70% 的安全漏洞源于编码阶段的不当实践。通过采用安全编码标准（如 OWASP ASVS、CERT C/C++ 编码标准）、代码审查和自动化安全测试，可以在开发早期发现和修复安全问题，大幅降低后期修复成本。

```
┌─────────────────────────────────────────────────────────────────┐
│                   安全软件开发生命周期 (SSDLC)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   需求          设计           编码           测试          部署  │
│    │            │             │             │            │    │
│    ▼            ▼             ▼             ▼            ▼    │
│  ┌────┐      ┌────┐       ┌────┐       ┌────┐       ┌────┐ │
│  │威胁│      │安全│       │安全│       │安全│       │安全│ │
│  │建模│─────▶│设计│──────▶│编码│──────▶│测试│──────▶│部署│ │
│  └────┘      └────┘       └────┘       └────┘       └────┘ │
│    │            │             │             │            │    │
│    ▼            ▼             ▼             ▼            ▼    │
│  STRIDE    安全架构审查   安全编码规范   SAST/DAST    安全配置 │
│  威胁分析    威胁建模     代码审查      渗透测试     漏洞扫描  │
│                                                                 │
│   安全左移：越早发现安全问题，修复成本越低                        │
│   生产环境修复成本 : 开发阶段修复成本 ≈ 100:1                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 安全编码原则

```
┌─────────────────────────────────────────────────────────────────┐
│                   安全编码核心原则                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. 最小权限原则 (Principle of Least Privilege)               │
│      • 只授予完成任务所需的最小权限                            │
│      • 及时回收不再需要的权限                                  │
│      • 默认拒绝，显式允许                                      │
│                                                                 │
│   2. 默认安全 (Secure by Default)                               │
│      • 安全是默认配置，而非可选项                              │
│      • 危险功能默认关闭                                        │
│      • 安全配置开箱即用                                        │
│                                                                 │
│   3. 纵深防御 (Defense in Depth)                                │
│      • 多层安全控制，单点失效不导致整体崩溃                    │
│      • 客户端 + 服务端 + 网络 + 物理多层防护                   │
│      • 不依赖单一安全机制                                      │
│                                                                 │
│   4.  fail-safe 默认 (Fail Secure)                              │
│      • 出错时进入安全状态                                      │
│      • 默认拒绝访问                                            │
│      • 详细的错误日志但不泄露敏感信息                          │
│                                                                 │
│   5. 不信任外部输入 (Never Trust Input)                         │
│      • 所有外部输入都可能是恶意的                              │
│      • 验证、清理、编码所有输入                                │
│      • 上下文感知的输出编码                                    │
│                                                                 │
│   6. 保持简单 (Keep it Simple)                                  │
│      • 复杂代码更容易隐藏漏洞                                  │
│      • 避免不必要的功能                                        │
│      • 清晰的安全关键代码                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 常见漏洞分类

| 漏洞类别 | CWE Top 25 排名 | 主要原因 | 典型后果 |
|----------|-----------------|----------|----------|
| **注入** | #1 | 未验证的用户输入直接拼接 | 数据泄露、服务器接管 |
| **越界写入** | #2 | 缺少边界检查 | 代码执行、崩溃 |
| **敏感数据泄露** | #3 | 未加密存储/传输 | 信息泄露 |
| **越界读取** | #4 | 缺少边界检查 | 信息泄露 |
| **空指针解引用** | #5 | 未验证指针有效性 | 拒绝服务 |
| **XSS** | #6 | 未编码的输出 | 会话劫持 |
| **路径遍历** | #8 | 未验证文件路径 | 未授权文件访问 |
| **不安全的反序列化** | #13 | 未验证的对象数据 | 远程代码执行 |
| **日志伪造** | #21 | 未清理的日志输入 | 日志污染 |

---

## 实现方式

### 1. 安全代码模式

```python
"""
安全编码实践示例 - Python
涵盖常见安全场景的正确做法
"""

import os
import re
import hashlib
import secrets
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from dataclasses import dataclass


# ==================== 1. 输入验证 ====================

class InputValidator:
    """输入验证类"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and len(email) <= 254
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """验证用户名"""
        # 白名单：字母数字下划线，3-30字符
        if not 3 <= len(username) <= 30:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_]+$', username))
    
    @staticmethod
    def sanitize_filename(filename: str) -> Optional[str]:
        """安全文件名处理"""
        # 移除路径分隔符和危险字符
        dangerous = ['..', '/', '\\', '\x00', ';', '&', '|', '`']
        for char in dangerous:
            if char in filename:
                return None
        
        # 只允许安全的字符
        if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
            return None
        
        return filename
    
    @staticmethod
    def validate_integer(value: Any, min_val: int = None, 
                        max_val: int = None) -> Optional[int]:
        """安全的整数验证"""
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return None
            if max_val is not None and num > max_val:
                return None
            return num
        except (ValueError, TypeError):
            return None


# ==================== 2. 安全文件操作 ====================

class SecureFileOperations:
    """安全文件操作"""
    
    @staticmethod
    @contextmanager
    def safe_temp_file(suffix: str = '.tmp', prefix: str = 'tmp'):
        """安全创建临时文件"""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        try:
            os.close(fd)
            yield path
        finally:
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass
    
    @staticmethod
    def safe_file_read(filepath: str, max_size: int = 10 * 1024 * 1024) -> bytes:
        """安全读取文件"""
        # 验证路径
        resolved = Path(filepath).resolve()
        
        # 检查文件存在和权限
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if not resolved.is_file():
            raise ValueError(f"Not a file: {filepath}")
        
        # 检查文件大小
        size = resolved.stat().st_size
        if size > max_size:
            raise ValueError(f"File too large: {size} bytes")
        
        # 安全读取
        with open(resolved, 'rb') as f:
            return f.read()
    
    @staticmethod
    def safe_file_write(filepath: str, content: bytes, 
                       base_dir: str = None) -> None:
        """安全写入文件"""
        if base_dir:
            # 确保路径在基目录内
            base = Path(base_dir).resolve()
            target = (base / filepath).resolve()
            if not str(target).startswith(str(base)):
                raise ValueError("Path traversal attempt detected")
            filepath = str(target)
        
        # 原子写入：先写入临时文件再重命名
        dir_name = os.path.dirname(filepath) or '.'
        fd, temp_path = tempfile.mkstemp(dir=dir_name)
        try:
            os.write(fd, content)
            os.close(fd)
            os.replace(temp_path, filepath)
        except Exception:
            os.close(fd)
            os.unlink(temp_path)
            raise


# ==================== 3. 安全配置 ====================

@dataclass
class SecurityConfig:
    """安全配置类"""
    # 密码策略
    min_password_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    
    # 会话安全
    session_timeout: int = 3600
    max_login_attempts: int = 5
    lockout_duration: int = 900
    
    # 文件上传
    max_file_size: int = 10 * 1024 * 1024
    allowed_extensions: tuple = ('.jpg', '.png', '.pdf', '.txt')
    
    # 安全头部
    enable_hsts: bool = True
    enable_csp: bool = True
    
    @classmethod
    def from_environment(cls) -> 'SecurityConfig':
        """从环境变量加载配置"""
        config = cls()
        
        # 敏感配置从环境变量读取，不使用默认值
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            raise ValueError("SECRET_KEY must be set in environment")
        
        db_password = os.environ.get('DB_PASSWORD')
        if not db_password:
            raise ValueError("DB_PASSWORD must be set in environment")
        
        return config


# ==================== 4. 安全密码处理 ====================

class SecurePasswordManager:
    """安全密码管理"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """使用 bcrypt 安全哈希密码"""
        import bcrypt
        
        # 生成盐并哈希
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)  # 成本因子 12
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        import bcrypt
        
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple:
        """验证密码强度"""
        errors = []
        
        if len(password) < 12:
            errors.append("Password must be at least 12 characters")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Must contain uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Must contain lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Must contain digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Must contain special character")
        
        # 检查常见密码
        common_passwords = {'password123', 'qwerty', '123456'}
        if password.lower() in common_passwords:
            errors.append("Password too common")
        
        return (len(errors) == 0, errors)


# ==================== 5. 安全随机数 ====================

class SecureRandom:
    """安全随机数生成"""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """生成安全随机令牌"""
        # 使用 secrets 模块，而不是 random
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_password(length: int = 16) -> str:
        """生成随机密码"""
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            # 确保满足基本要求
            if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
                return password


# ==================== 6. 安全 HTTP 客户端 ====================

import requests
from urllib.parse import urlparse

class SecureHTTPClient:
    """安全 HTTP 客户端"""
    
    # 禁止访问的内部地址
    BLOCKED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
    BLOCKED_PREFIXES = ['10.', '172.16.', '192.168.', '169.254.']
    
    @staticmethod
    def is_safe_url(url: str) -> bool:
        """检查 URL 是否安全（防止 SSRF）"""
        try:
            parsed = urlparse(url)
            
            # 检查协议
            if parsed.scheme not in ('http', 'https'):
                return False
            
            # 检查主机
            hostname = parsed.hostname
            if not hostname:
                return False
            
            # 检查黑名单
            if hostname in SecureHTTPClient.BLOCKED_HOSTS:
                return False
            
            for prefix in SecureHTTPClient.BLOCKED_PREFIXES:
                if hostname.startswith(prefix):
                    return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def safe_get(url: str, timeout: int = 10, max_size: int = 1024 * 1024) -> requests.Response:
        """安全的 HTTP GET 请求"""
        if not SecureHTTPClient.is_safe_url(url):
            raise ValueError("Unsafe URL")
        
        # 限制响应大小
        response = requests.get(url, timeout=timeout, stream=True)
        
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > max_size:
            raise ValueError("Response too large")
        
        return response


# ==================== 7. 安全日志记录 ====================

import logging
import copy

class SecureLogger:
    """安全日志记录"""
    
    # 敏感字段，日志中应过滤
    SENSITIVE_FIELDS = {
        'password', 'passwd', 'pwd', 'secret', 'token',
        'api_key', 'apikey', 'private_key', 'credit_card',
        'ssn', 'social_security'
    }
    
    @staticmethod
    def sanitize_for_logging(data: Dict) -> Dict:
        """清理数据以安全记录"""
        if not isinstance(data, dict):
            return data
        
        # 深拷贝避免修改原数据
        sanitized = copy.deepcopy(data)
        
        for key in sanitized:
            if any(sensitive in key.lower() for sensitive in SecureLogger.SENSITIVE_FIELDS):
                sanitized[key] = '***REDACTED***'
        
        return sanitized
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict, user_id: str = None):
        """记录安全事件"""
        logger = logging.getLogger('security')
        
        event = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'details': SecureLogger.sanitize_for_logging(details)
        }
        
        logger.warning(json.dumps(event))


# ==================== 8. 并发安全 ====================

import threading
from concurrent.futures import ThreadPoolExecutor

class ThreadSafeCounter:
    """线程安全的计数器"""
    
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value
    
    def get(self) -> int:
        with self._lock:
            return self._value


class RateLimiter:
    """线程安全的速率限制器"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = {}
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        now = time.time()
        
        with self._lock:
            # 清理过期请求
            if key in self._requests:
                self._requests[key] = [
                    req_time for req_time in self._requests[key]
                    if now - req_time < self.window_seconds
                ]
            else:
                self._requests[key] = []
            
            # 检查是否超过限制
            if len(self._requests[key]) >= self.max_requests:
                return False
            
            # 记录请求
            self._requests[key].append(now)
            return True


# ==================== 9. 错误处理安全 ====================

class SecureErrorHandler:
    """安全的错误处理"""
    
    @staticmethod
    def handle_exception(exception: Exception, is_production: bool = True) -> Dict:
        """
        安全地处理异常
        生产环境不暴露敏感信息
        """
        # 始终记录完整错误日志
        logging.error(f"Exception occurred: {exception}", exc_info=True)
        
        if is_production:
            # 生产环境：通用错误消息
            return {
                'error': 'An error occurred',
                'error_code': 'INTERNAL_ERROR',
                'reference_id': secrets.token_hex(8)  # 用于日志关联
            }
        else:
            # 开发环境：详细错误信息
            import traceback
            return {
                'error': str(exception),
                'type': type(exception).__name__,
                'traceback': traceback.format_exc()
            }


# ==================== 10. 安全反序列化 ====================

import json
import pickle

class SecureDeserialization:
    """安全反序列化"""
    
    @staticmethod
    def safe_json_loads(data: str, max_depth: int = 10) -> Any:
        """安全的 JSON 解析"""
        # 限制嵌套深度防止 DOS
        def check_depth(obj, depth=0):
            if depth > max_depth:
                raise ValueError("JSON nesting too deep")
            if isinstance(obj, dict):
                for v in obj.values():
                    check_depth(v, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, depth + 1)
        
        parsed = json.loads(data)
        check_depth(parsed)
        return parsed
    
    @staticmethod
    def safe_pickle_loads(data: bytes, allowed_classes: List[str] = None) -> Any:
        """
        限制性的 pickle 反序列化
        警告：pickle 不安全，尽量避免使用
        """
        if allowed_classes is None:
            allowed_classes = []
        
        class RestrictedUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                full_name = f"{module}.{name}"
                if full_name not in allowed_classes:
                    raise pickle.UnpicklingError(f"Class {full_name} not allowed")
                return super().find_class(module, name)
        
        return RestrictedUnpickler(io.BytesIO(data)).load()


# 使用示例
if __name__ == "__main__":
    # 验证输入
    print(InputValidator.validate_email("test@example.com"))
    
    # 密码哈希
    hashed = SecurePasswordManager.hash_password("MySecureP@ss123")
    print(SecurePasswordManager.verify_password("MySecureP@ss123", hashed))
    
    # 生成安全令牌
    token = SecureRandom.generate_token()
    print(f"Generated token: {token}")
```

### 2. 安全编码检查清单

```python
"""
安全编码检查清单 - 开发前必读
"""

SECURE_CODING_CHECKLIST = """
┌─────────────────────────────────────────────────────────────────┐
│                   安全编码检查清单                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  输入验证                                                       │
│  □ 所有外部输入都经过验证（用户、文件、网络、数据库）           │
│  □ 使用白名单而非黑名单验证                                     │
│  □ 验证数据类型、长度、格式、范围                               │
│  □ 路径遍历防护（规范化路径、基目录检查）                       │
│  □ 文件上传：验证类型、大小、扩展名、魔术数字                   │
│                                                                 │
│  输出编码                                                       │
│  □ HTML 输出使用上下文感知编码                                  │
│  □ JavaScript 动态内容使用 JSON 编码                            │
│  □ SQL 查询使用参数化查询                                       │
│  □ URL 参数使用 URL 编码                                        │
│  □ 命令执行避免 shell，使用列表参数                             │
│                                                                 │
│  认证与授权                                                     │
│  □ 使用强密码策略（长度、复杂度）                               │
│  □ 使用 bcrypt/Argon2 存储密码                                  │
│  □ 实现登录失败锁定和速率限制                                   │
│  □ 会话 ID 安全随机生成                                         │
│  □ Cookie 设置 Secure、HttpOnly、SameSite                       │
│  □ 权限检查在每个端点执行                                       │
│  □ 水平越权检查（用户只能访问自己的数据）                       │
│                                                                 │
│  敏感数据处理                                                   │
│  □ 敏感数据加密存储（AES-256-GCM）                              │
│  □ 传输使用 TLS 1.2+                                            │
│  □ 密钥使用 HSM 或密钥管理服务                                  │
│  □ 日志中不包含敏感信息                                         │
│  □ 内存中敏感数据使用后立即清除                                 │
│                                                                 │
│  安全配置                                                       │
│  □ 安全配置从环境变量读取，代码中无硬编码密钥                   │
│  □ 默认安全配置（禁用调试、删除默认账户）                       │
│  □ 安全头部配置（HSTS、CSP、X-Frame-Options）                   │
│  □ 错误处理不泄露敏感信息（堆栈、路径、SQL）                    │
│                                                                 │
│  依赖管理                                                       │
│  □ 定期扫描依赖漏洞（Snyk、OWASP Dependency-Check）             │
│  □ 及时更新存在漏洞的依赖                                       │
│  □ 最小化依赖，移除未使用的依赖                                 │
│  □ 锁定依赖版本（requirements.txt 指定哈希）                    │
│                                                                 │
│  并发与资源                                                     │
│  □ 线程安全的数据结构                                           │
│  □ 资源使用限制（超时、大小、数量）                             │
│  □ 防止竞态条件（原子操作、锁）                                 │
│  □ 限制递归深度和循环次数                                       │
│                                                                 │
│  代码质量                                                       │
│  □ 静态代码分析（SonarQube、Bandit、ESLint Security）           │
│  □ 同行代码审查（重点关注安全关键代码）                         │
│  □ 单元测试覆盖安全场景                                         │
│  □ 安全测试（SAST、DAST、渗透测试）                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""
```

---

## 应用场景

### 场景 1: 安全 API 设计

```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# 安全中间件
@app.before_request
def security_checks():
    """请求前安全检查"""
    # 检查 Content-Type
    if request.method in ['POST', 'PUT', 'PATCH']:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415
    
    # 检查请求大小
    if request.content_length and request.content_length > 10 * 1024 * 1024:
        return jsonify({'error': 'Request too large'}), 413


# 安全的 API 端点
@app.route('/api/users/<user_id>', methods=['GET'])
@require_auth
@rate_limit(max_requests=100, window=60)
def get_user(user_id: str):
    """获取用户信息 - 安全实现"""
    
    # 1. 输入验证
    if not InputValidator.validate_integer(user_id):
        return jsonify({'error': 'Invalid user_id'}), 400
    
    # 2. 授权检查
    current_user = get_current_user()
    if current_user.id != int(user_id) and not current_user.is_admin:
        # 记录未授权访问尝试
        SecureLogger.log_security_event(
            'UNAUTHORIZED_ACCESS_ATTEMPT',
            {'target_user': user_id},
            current_user.id
        )
        return jsonify({'error': 'Forbidden'}), 403
    
    # 3. 查询数据
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    
    # 4. 输出过滤（不返回敏感字段）
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        # 不包含: password_hash, api_keys, private_notes
    })
```

---

## 面试要点

### Q1: 什么是纵深防御？如何在代码中实现？

**A:**

纵深防御是设置多层安全控制，确保单点失效不会导致整体安全崩溃。

**代码实现示例:**

```python
# 多层防御示例：文件上传

def upload_file(file):
    # 第1层：输入大小限制（Web服务器/Nginx）
    # client_max_body_size 10M;
    
    # 第2层：应用层大小检查
    if file.content_length > 10 * 1024 * 1024:
        raise ValueError("File too large")
    
    # 第3层：扩展名白名单
    allowed = {'.jpg', '.png', '.pdf'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise ValueError("Extension not allowed")
    
    # 第4层：魔术数字验证
    magic = file.read(4)
    file.seek(0)
    if not is_valid_magic_number(magic, ext):
        raise ValueError("File type mismatch")
    
    # 第5层：存储到非Web目录
    save_path = f"/var/secure_uploads/{uuid.uuid4()}{ext}"
    
    # 第6层：病毒扫描
    if scan_virus(file):
        raise ValueError("Virus detected")
    
    # 第7层：文件权限
    os.chmod(save_path, 0o640)
```

### Q2: 如何避免硬编码密钥？

**A:**

```python
# ❌ 错误：硬编码密钥
API_KEY = "sk-1234567890abcdef"

# ✓ 正确：从环境变量读取
import os
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

# ✓ 更好：使用密钥管理服务
from aws_secretsmanager import get_secret
API_KEY = get_secret('production/api_key')

# 开发环境使用 .env 文件（不提交到版本控制）
# .env 文件加入 .gitignore
from dotenv import load_dotenv
load_dotenv()
```

### Q3: 如何安全地记录日志？

**A:**

```python
# ❌ 危险：记录敏感信息
logging.info(f"User login: {username}, password: {password}")

# ✓ 正确：过滤敏感字段
def sanitize_sensitive_data(data):
    sensitive = {'password', 'token', 'credit_card', 'ssn'}
    return {k: '***' if k in sensitive else v for k, v in data.items()}

logging.info(f"User login: {sanitize_sensitive_data(user_data)}")

# ✓ 更好：结构化日志
import structlog
logger = structlog.get_logger()
logger.info("user_login", user_id=user_id, ip_address=ip)  # 不记录密码
```

---

## 相关概念

### 数据结构
- [字符串](../computer-science/data-structures/string.md)：安全的字符串处理
- [哈希表](../computer-science/data-structures/hash-table.md)：安全数据存储

### 算法
- [加密算法](../cryptography/symmetric-encryption.md)：数据加密
- [哈希算法](../cryptography/hash-functions.md)：密码哈希

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：安全算法性能
- [空间复杂度](../references/space-complexity.md)：内存安全

### 系统实现
- [输入验证](./input-validation.md)：安全输入处理
- [身份认证](./authentication.md)：安全认证实现
- [会话管理](./session-management.md)：安全会话
- [Web 安全](./web-security.md)：Web 安全基础

### 安全领域
- [OWASP Top 10](../common-vulnerabilities.md)：常见漏洞
- [代码审计](./code-audit.md)：安全代码审查
- [DevSecOps](./devsecops.md)：安全开发流程

---

## 参考资料

1. [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
2. [SEI CERT Coding Standards](https://wiki.sei.cmu.edu/confluence/display/seccode/SEI+CERT+Coding+Standards)
3. [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
4. [CWE Top 25](https://cwe.mitre.org/top25/)
