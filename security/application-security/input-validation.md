# 输入验证 (Input Validation)

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、OWASP 指南及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**输入验证 (Input Validation)** 是应用安全的第一道防线，用于确保应用程序接收的数据符合预期格式、类型和范围。几乎所有安全漏洞（SQL 注入、XSS、命令注入、路径遍历等）都源于对用户输入的不当处理。遵循"永远不要信任用户输入"的原则，对所有输入数据进行严格的验证、清理和编码，是构建安全应用的基础。

```
┌─────────────────────────────────────────────────────────────────┐
│                   输入验证安全模型                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   用户输入                                                       │
│      │                                                          │
│      ▼                                                          │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  1. 输入接收 (Input Reception)                          │  │
│   │     • HTTP 参数、Headers、Body                          │  │
│   │     • 文件上传、Cookie                                  │  │
│   │     • 第三方 API 响应                                   │  │
│   └─────────────────────────────────────────────────────────┘  │
│      │                                                          │
│      ▼                                                          │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  2. 验证策略 (Validation Strategy)                      │  │
│   │     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│   │     │ 白名单 (允许)│  │ 数据类型    │  │ 长度/范围   │  │  │
│   │     │ Whitelist   │  │ 检查        │  │ 限制        │  │  │
│   │     │ 优先使用    │  │             │  │             │  │  │
│   │     └─────────────┘  └─────────────┘  └─────────────┘  │  │
│   └─────────────────────────────────────────────────────────┘  │
│      │                                                          │
│      ▼                                                          │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  3. 清理与编码 (Sanitization & Encoding)                │  │
│   │     • HTML 编码 (防 XSS)                                │  │
│   │     • SQL 参数化 (防注入)                               │  │
│   │     • 路径规范化 (防遍历)                               │  │
│   └─────────────────────────────────────────────────────────┘  │
│      │                                                          │
│      ▼                                                          │
│   安全的数据 ──▶ 业务逻辑处理                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 安全原则

```
┌─────────────────────────────────────────────────────────────────┐
│                   输入验证核心原则                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. 零信任原则 (Never Trust User Input)                       │
│      • 所有外部输入都可能是恶意的                              │
│      • 验证发生在应用边界                                      │
│                                                                 │
│   2. 白名单优先 (Whitelist over Blacklist)                     │
│      • ✓ 只允许已知安全的输入                                  │
│      • ✗ 只拒绝已知危险的输入（黑名单总有遗漏）                │
│                                                                 │
│   3. 深度防御 (Defense in Depth)                               │
│      • 客户端验证 + 服务端验证                                 │
│      • 输入验证 + 输出编码                                     │
│      • 数据库参数化 + ORM 保护                                 │
│                                                                 │
│   4. 最小权限 (Fail Securely)                                  │
│      • 验证失败默认拒绝                                        │
│      • 不提供详细错误信息（防止信息泄露）                      │
│                                                                 │
│   5. 明确编码 (Canonicalization)                               │
│      • 规范化输入后再验证                                      │
│      • 处理 Unicode、编码变异                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 常见注入攻击类型

| 攻击类型 | 描述 | 典型载荷 | 影响 |
|----------|------|----------|------|
| **SQL 注入** | 注入恶意 SQL 语句 | `' OR '1'='1` | 数据泄露、篡改、删除 |
| **XSS** | 注入恶意脚本 | `<script>alert('xss')</script>` | 会话劫持、钓鱼 |
| **命令注入** | 注入系统命令 | `; rm -rf /` | 服务器接管 |
| **路径遍历** | 访问非授权路径 | `../../../etc/passwd` | 文件读取 |
| **LDAP 注入** | 注入 LDAP 查询 | `*)(uid=*` | 未授权访问 |
| **NoSQL 注入** | 注入 NoSQL 查询 | `{"$gt": ""}` | 数据操作 |
| **XML 注入** | 注入 XML 实体 | `<!ENTITY xxe SYSTEM ...>` | XXE 攻击 |

---

## 实现方式

### 1. SQL 注入防护

```python
import re
import sqlite3
from typing import List, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass

class SQLInjectionPrevention:
    """SQL 注入防护实现"""
    
    # 危险的 SQL 关键字（用于检测，不应仅依赖黑名单）
    DANGEROUS_KEYWORDS = [
        'union', 'select', 'insert', 'update', 'delete', 'drop',
        'truncate', 'exec', 'execute', 'script', 'shutdown'
    ]
    
    @staticmethod
    def validate_identifier(identifier: str) -> bool:
        """
        验证 SQL 标识符（表名、列名）
        只允许字母数字和下划线
        """
        if not identifier:
            return False
        # 白名单：只允许字母开头，后跟字母数字下划线
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, identifier))
    
    @staticmethod
    def sanitize_order_by(order_by: str, allowed_columns: List[str]) -> str:
        """
        安全处理 ORDER BY 子句
        只允许预定义的列名和方向
        """
        parts = order_by.strip().split()
        column = parts[0]
        direction = parts[1].upper() if len(parts) > 1 else 'ASC'
        
        # 验证列名在白名单中
        if column not in allowed_columns:
            raise ValueError(f"Invalid order column: {column}")
        
        # 验证方向
        if direction not in ('ASC', 'DESC'):
            direction = 'ASC'
        
        # 返回安全的、已验证的字符串
        return f"{column} {direction}"
    
    @staticmethod
    def validate_search_term(term: str, max_length: int = 100) -> str:
        """
        验证搜索关键词
        移除危险字符，限制长度
        """
        if not term:
            return ""
        
        # 截断长度
        term = term[:max_length]
        
        # 转义特殊 SQL 字符
        # 注意：这不能替代参数化查询，只是额外的一层保护
        dangerous_chars = ['%', '_', '[', ']', '^', '{', '}']
        for char in dangerous_chars:
            term = term.replace(char, f'\\{char}')
        
        return term


# 正确的参数化查询示例
class SecureDatabaseAccess:
    """安全的数据库访问层"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """
        安全的查询：使用参数化查询
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # ✓ 正确：使用参数化查询
            cursor.execute(
                "SELECT id, username, email FROM users WHERE id = ?",
                (user_id,)  # 参数作为元组传递
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def search_users(self, username_pattern: str, 
                    status: str = 'active',
                    order_by: str = 'id') -> List[dict]:
        """
        安全的搜索：参数化 + 白名单验证
        """
        # 验证并清理输入
        validator = SQLInjectionPrevention()
        
        # 允许的排序列
        allowed_columns = ['id', 'username', 'email', 'created_at']
        safe_order = validator.sanitize_order_by(order_by, allowed_columns)
        
        # 验证状态（枚举值）
        allowed_status = ['active', 'inactive', 'pending']
        if status not in allowed_status:
            status = 'active'  # 默认值
        
        # 转义搜索模式中的特殊字符
        safe_pattern = validator.validate_search_term(username_pattern)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 注意：safe_order 已经过白名单验证，可以拼接
            # 其他参数仍使用参数化
            query = f"""
                SELECT id, username, email, status 
                FROM users 
                WHERE username LIKE ? ESCAPE '\\'
                AND status = ?
                ORDER BY {safe_order}
                LIMIT 100
            """
            
            cursor.execute(query, (f'%{safe_pattern}%', status))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_data_dynamic(self, table_name: str, 
                             user_id: int) -> Optional[dict]:
        """
        动态表名查询：必须使用白名单验证
        """
        validator = SQLInjectionPrevention()
        
        # 验证表名（白名单）
        allowed_tables = ['users', 'profiles', 'preferences']
        if table_name not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        
        # 表名不能参数化，但已通过白名单验证
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM {table_name} WHERE user_id = ?"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def execute_raw_sql(self, user_sql: str) -> None:
        """
        危险：永远不要让用户输入直接执行
        如果需要，实施严格的控制
        """
        # 禁止直接执行用户输入的 SQL
        raise NotImplementedError(
            "Direct SQL execution from user input is not allowed"
        )


# 使用 SQLAlchemy ORM 的安全示例
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import select

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    role = Column(String(20), default='user')


class ORMSecureAccess:
    """使用 ORM 的安全数据库访问"""
    
    def __init__(self, db_url: str):
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def get_user_safe(self, user_id: int) -> Optional[User]:
        """安全的 ORM 查询"""
        # ORM 自动使用参数化查询
        return self.session.query(User).filter(User.id == user_id).first()
    
    def search_users_safe(self, username: str) -> List[User]:
        """安全的模糊查询"""
        # ORM 自动转义 LIKE 模式
        return self.session.query(User).filter(
            User.username.like(f'%{username}%')
        ).limit(100).all()
    
    def raw_query_unsafe_demo(self, user_input: str) -> None:
        """
        危险：不安全的原始查询示例
        展示错误做法
        """
        # ❌ 错误：直接拼接用户输入
        # result = self.session.execute(f"SELECT * FROM users WHERE name = '{user_input}'")
        
        # ✓ 正确：使用参数化
        result = self.session.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {'username': user_input}
        )
        return result.fetchall()


# 批量插入安全示例
def batch_insert_users(users_data: List[dict]) -> None:
    """安全的批量插入"""
    db = SecureDatabaseAccess("app.db")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # 使用 executemany 进行参数化批量插入
        cursor.executemany(
            """
            INSERT INTO users (username, email, role)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                email = excluded.email
            """,
            [(u['username'], u['email'], u.get('role', 'user')) 
             for u in users_data]
        )
```

### 2. XSS 防护

```python
import html
import re
from typing import Optional, List, Dict
from urllib.parse import quote, unquote
import bleach
from markupsafe import Markup, escape

class XSSPrevention:
    """XSS 防护实现"""
    
    # HTML 危险标签黑名单
    DANGEROUS_TAGS = [
        'script', 'iframe', 'object', 'embed', 'form',
        'input', 'textarea', 'button', 'link', 'meta',
        'base', 'style', 'applet', 'frame', 'frameset'
    ]
    
    # 危险属性
    DANGEROUS_ATTRS = [
        'onerror', 'onload', 'onclick', 'onmouseover',
        'onmouseout', 'onfocus', 'onblur', 'onchange',
        'onsubmit', 'onreset', 'onselect', 'onunload',
        'javascript:', 'data:', 'vbscript:', 'mhtml:'
    ]
    
    @staticmethod
    def html_encode(text: str) -> str:
        """
        HTML 实体编码
        将特殊字符转换为 HTML 实体
        """
        if not text:
            return ""
        
        # 使用标准库进行编码
        return html.escape(text, quote=True)
    
    @staticmethod
    def html_encode_attribute(value: str) -> str:
        """
        属性值编码（更严格）
        用于 HTML 属性值
        """
        if not value:
            return ""
        
        # 除了标准编码外，还需处理更多字符
        encoded = ""
        for char in value:
            if char == '"':
                encoded += '&quot;'
            elif char == "'":
                encoded += '&#x27;'
            elif char == '/':
                encoded += '&#x2F;'
            elif ord(char) < 32:
                encoded += f'&#x{ord(char):02X};'
            else:
                encoded += html.escape(char, quote=False)
        
        return encoded
    
    @staticmethod
    def javascript_encode(text: str) -> str:
        """
        JavaScript 字符串编码
        用于在 JS 字符串中插入动态内容
        """
        if not text:
            return ""
        
        # Unicode 转义
        result = ""
        for char in text:
            if char in ['\\', '"', "'"]:
                result += '\\' + char
            elif char == '\n':
                result += '\\n'
            elif char == '\r':
                result += '\\r'
            elif ord(char) < 32 or ord(char) > 126:
                result += f'\\u{ord(char):04x}'
            else:
                result += char
        
        return result
    
    @staticmethod
    def url_encode(text: str) -> str:
        """URL 编码"""
        return quote(text, safe='')
    
    @staticmethod
    def css_encode(value: str) -> str:
        """
        CSS 值编码
        防止 CSS 注入
        """
        if not value:
            return ""
        
        # 只允许安全的 CSS 值
        # 移除危险字符
        sanitized = re.sub(r'[<>"\'\\;{}()]', '', value)
        return sanitized


class RichTextSanitizer:
    """富文本内容清理"""
    
    # 允许的标签白名单
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3',
        'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote',
        'a', 'img', 'code', 'pre', 'span', 'div'
    ]
    
    # 允许的属性白名单
    ALLOWED_ATTRIBUTES = {
        '*': ['class', 'id'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'span': ['style'],
    }
    
    # 允许的 CSS 样式
    ALLOWED_STYLES = [
        'color', 'background-color', 'font-weight', 'font-style',
        'text-decoration', 'text-align', 'font-size'
    ]
    
    @classmethod
    def sanitize(cls, html_content: str) -> str:
        """
        清理富文本内容
        移除危险标签和属性
        """
        if not html_content:
            return ""
        
        # 使用 bleach 库进行清理
        cleaned = bleach.clean(
            html_content,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            styles=cls.ALLOWED_STYLES,
            strip=True,  # 移除不允许的标签而非转义
            protocols=['http', 'https', 'mailto']  # 允许的 URL 协议
        )
        
        return cleaned
    
    @classmethod
    def sanitize_link(cls, url: str) -> Optional[str]:
        """
        验证和清理链接 URL
        防止 javascript: 等伪协议
        """
        if not url:
            return None
        
        url = url.strip().lower()
        
        # 拒绝危险协议
        dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
        for protocol in dangerous_protocols:
            if url.startswith(protocol):
                return None
        
        # 只允许 http 和 https
        if not (url.startswith('http://') or url.startswith('https://') or 
                url.startswith('/') or url.startswith('#') or
                url.startswith('mailto:')):
            return None
        
        return url


# Flask 应用中的 XSS 防护示例
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)
xss_prevention = XSSPrevention()

# 模板中使用自动转义
@app.route('/user/<username>')
def user_profile(username: str):
    """
    Flask Jinja2 模板默认自动转义
    但仍需注意 |safe 过滤器的使用
    """
    # 验证用户名格式
    if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', username):
        return "Invalid username", 400
    
    # 模板会自动转义 username
    template = '''
    <!DOCTYPE html>
    <html>
    <head><title>{{ username }} 的个人资料</title></head>
    <body>
        <h1>欢迎, {{ username }}!</h1>
        
        <!-- 安全的属性使用 -->
        <div data-username="{{ username | e }}">用户信息</div>
        
        <!-- JavaScript 中使用 -->
        <script>
            // 安全地嵌入到 JS 中
            var username = {{ username | tojson }};
            console.log('User: ' + username);
        </script>
    </body>
    </html>
    '''
    
    return render_template_string(template, username=username)


@app.route('/api/search')
def api_search():
    """API 响应中的 XSS 防护"""
    query = request.args.get('q', '')
    
    # 验证输入长度
    if len(query) > 100:
        query = query[:100]
    
    # 返回 JSON（自动转义）
    results = [
        {'title': f'Result for {query}', 'url': '/result/1'}
    ]
    
    return jsonify({
        'query': query,  # 客户端需要自行处理
        'results': results
    })


@app.route('/post-comment', methods=['POST'])
def post_comment():
    """处理用户评论（富文本）"""
    content = request.form.get('content', '')
    
    # 限制长度
    if len(content) > 5000:
        return "Content too long", 400
    
    # 清理富文本
    sanitizer = RichTextSanitizer()
    safe_content = sanitizer.sanitize(content)
    
    # 存储 safe_content（已清理）
    # save_to_database(safe_content)
    
    return jsonify({'status': 'success', 'content': safe_content})


# CSP (内容安全策略) 头部设置
@app.after_request
def set_security_headers(response):
    """设置安全头部防止 XSS"""
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'nonce-{nonce}'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    ).format(nonce='random_nonce_here')
    
    # XSS Protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response


# DOM-based XSS 防护（前端）
DOM_XSS_PROTECTION_JS = '''
/**
 * DOM-based XSS 防护工具
 * 用于客户端 JavaScript
 */

const XSSProtection = {
    /**
     * 安全的 HTML 插入
     * 使用 textContent 而非 innerHTML
     */
    setTextContent(element, text) {
        element.textContent = text;
    },
    
    /**
     * HTML 实体编码
     */
    htmlEncode(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    /**
     * 安全的 URL 验证
     */
    isSafeUrl(url) {
        if (!url) return false;
        
        const dangerous = ['javascript:', 'data:', 'vbscript:'];
        const lower = url.toLowerCase().trim();
        
        return !dangerous.some(proto => lower.startsWith(proto));
    },
    
    /**
     * 安全的动态脚本加载
     */
    loadScript(src) {
        if (!this.isSafeUrl(src)) {
            throw new Error('Dangerous script source');
        }
        
        const script = document.createElement('script');
        script.src = src;
        document.head.appendChild(script);
    }
};

// 使用示例
// 危险：element.innerHTML = userInput;
// 安全：XSSProtection.setTextContent(element, userInput);
'''

print("DOM XSS Protection JavaScript prepared")
```

### 3. 其他注入攻击防护

```python
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import List, Optional

class CommandInjectionPrevention:
    """命令注入防护"""
    
    DANGEROUS_CHARS = [';', '&', '|', '`', '$', '(', ')', '{', '}', '<', '>', '\\', '\n']
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        验证文件名（防止路径遍历和命令注入）
        """
        if not filename:
            return False
        
        # 拒绝路径分隔符和危险字符
        dangerous = ['..', '/', '\\', '\x00', ';', '&', '|', '`']
        for char in dangerous:
            if char in filename:
                return False
        
        # 只允许安全的文件名
        if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
            return False
        
        return True
    
    @staticmethod
    def sanitize_path(user_path: str, base_dir: str) -> Optional[str]:
        """
        安全的路径处理（防止路径遍历）
        """
        try:
            # 规范化路径
            base_path = Path(base_dir).resolve()
            target_path = (base_path / user_path).resolve()
            
            # 确保目标路径在基目录内
            if not str(target_path).startswith(str(base_path)):
                return None
            
            return str(target_path)
        except Exception:
            return None
    
    @staticmethod
    def safe_command execution(cmd: List[str]) -> subprocess.CompletedProcess:
        """
        安全的命令执行
        使用列表而非字符串，避免 shell 解析
        """
        # ✓ 正确：使用列表，不通过 shell
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False,  # 关键：不使用 shell
            timeout=30
        )
    
    @staticmethod
    def dangerous_command_demo(user_input: str) -> None:
        """
        危险的命令执行示例（错误做法）
        """
        # ❌ 危险：字符串拼接
        # os.system(f"echo {user_input}")
        
        # ❌ 危险：使用 shell=True
        # subprocess.run(f"cat {user_input}", shell=True)
        
        # ✓ 正确：参数化列表
        # subprocess.run(['cat', user_input], shell=False)
        pass


class LDAPInjectionPrevention:
    """LDAP 注入防护"""
    
    LDAP_SPECIAL_CHARS = {
        '\\': '\\5c',
        '*': '\\2a',
        '(': '\\28',
        ')': '\\29',
        '\x00': '\\00',
    }
    
    @staticmethod
    def escape_filter(filter_str: str) -> str:
        """
        转义 LDAP 过滤器中的特殊字符
        """
        result = filter_str
        for char, escaped in LDAPInjectionPrevention.LDAP_SPECIAL_CHARS.items():
            result = result.replace(char, escaped)
        return result
    
    @staticmethod
    def build_safe_filter(username: str, base_dn: str) -> str:
        """
        构建安全的 LDAP 过滤器
        """
        safe_username = LDAPInjectionPrevention.escape_filter(username)
        # 使用括号包围确保结构正确
        return f"(&(objectClass=user)(cn={safe_username}))"


class NoSQLInjectionPrevention:
    """NoSQL 注入防护"""
    
    @staticmethod
    def validate_mongodb_query(query: dict) -> bool:
        """
        验证 MongoDB 查询是否安全
        防止操作符注入
        """
        dangerous_operators = ['$where', '$eval', '$ne', '$gt', '$gte', '$lt', '$lte']
        
        def check_dict(d):
            for key, value in d.items():
                # 检查键是否以 $ 开头（操作符）
                if isinstance(key, str) and key.startswith('$'):
                    if key in dangerous_operators:
                        return False
                
                # 递归检查值
                if isinstance(value, dict):
                    if not check_dict(value):
                        return False
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and not check_dict(item):
                            return False
            return True
        
        return check_dict(query)
    
    @staticmethod
    def safe_mongodb_find(collection, field: str, value: str):
        """
        安全的 MongoDB 查询
        """
        # 验证字段名（只允许字母数字下划线）
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', field):
            raise ValueError(f"Invalid field name: {field}")
        
        # 值作为字符串字面量处理
        # 不使用 $where 等危险操作符
        return collection.find_one({field: value})


# XML 和 XXE 防护
class XXEPrevention:
    """XXE (XML External Entity) 防护"""
    
    @staticmethod
    def safe_xml_parse(xml_string: str):
        """
        安全的 XML 解析
        禁用外部实体和 DTD
        """
        from xml.etree import ElementTree as ET
        
        # 使用 defusedxml 替代标准库
        try:
            import defusedxml.ElementTree as DefusedET
            return DefusedET.fromstring(xml_string)
        except ImportError:
            # 如果不可用，使用安全的解析器配置
            parser = ET.XMLParser()
            parser.entity_declaration_handler = lambda *args: None
            parser.external_entity_ref_handler = lambda *args: 1
            return ET.fromstring(xml_string, parser=parser)
    
    @staticmethod
    def validate_xml_against_schema(xml_string: str, schema_path: str) -> bool:
        """
        使用 XSD 验证 XML
        额外的安全检查层
        """
        from lxml import etree
        
        try:
            with open(schema_path, 'rb') as f:
                schema_root = etree.XML(f.read())
            schema = etree.XMLSchema(schema_root)
            
            parser = etree.XMLParser(schema=schema, resolve_entities=False)
            etree.fromstring(xml_string.encode(), parser)
            return True
        except Exception:
            return False
```

---

## 应用场景

### 场景 1: 多层验证架构

```
┌─────────────────────────────────────────────────────────────────┐
│                   多层输入验证架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   客户端层（用户体验）                                           │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  • 即时格式验证（JavaScript）                            │  │
│   │  • 长度限制                                              │  │
│   │  • 类型检查                                              │  │
│   │  ⚠️ 仅用于用户体验，不可信                               │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   API 网关层                                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  • 请求大小限制                                          │  │
│   │  • 速率限制                                              │  │
│   │  • 基本格式验证                                          │  │
│   │  • WAF 规则检查                                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   应用服务层（核心验证）                                         │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  • 严格的类型验证                                        │  │
│   │  • 业务规则验证                                          │  │
│   │  • 白名单验证                                            │  │
│   │  • 参数化查询                                            │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   数据访问层                                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  • ORM/参数化查询                                        │  │
│   │  • 存储过程（可选）                                      │  │
│   │  • 转义/编码                                             │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   输出层                                                       │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  • 上下文感知编码（HTML/JS/URL）                         │  │
│   │  • CSP 头部                                              │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 场景 2: 常见漏洞防护对照表

```
┌─────────────────────────────────────────────────────────────────┐
│              OWASP Top 10 输入相关漏洞防护                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  A03:2021 – Injection（注入）                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ SQL 注入       │ 参数化查询、ORM、输入验证               │   │
│  │ NoSQL 注入     │ 验证操作符、使用参数化                  │   │
│  │ 命令注入       │ 避免 shell、使用列表传参                │   │
│  │ LDAP 注入      │ 转义特殊字符                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  A03:2021 – XSS（跨站脚本）                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 反射型 XSS     │ 输出编码、输入验证                      │   │
│  │ 存储型 XSS     │ 富文本清理、CSP                         │   │
│  │ DOM 型 XSS     │ 安全的 DOM 操作                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  A01:2021 – Broken Access Control                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ IDOR           │ 验证用户资源所有权                      │   │
│  │ 路径遍历       │ 规范化路径、基目录检查                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  A05:2021 – Security Misconfiguration                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 错误信息泄露   │ 通用错误消息                            │   │
│  │ 调试信息       │ 生产环境禁用调试                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

### Q1: 白名单和黑名单验证的区别？为什么优先使用白名单？

**A:**

| 特性 | 白名单 (Whitelist) | 黑名单 (Blacklist) |
|------|-------------------|-------------------|
| 定义 | 只允许已知安全的输入 | 只拒绝已知危险的输入 |
| 安全性 | 高，默认拒绝未知 | 低，新攻击方式无法防御 |
| 维护 | 需要更新允许列表 | 需要持续更新黑名单 |
| 误报 | 可能拒绝合法输入 | 可能允许恶意输入 |
| 适用 | 固定格式数据（邮箱、手机号） | 复杂场景辅助手段 |

**为什么优先白名单:**
- 攻击者总能发现新的绕过方式
- 白名单明确知道什么是安全的
- 符合"最小权限"原则

**示例:**
```python
# 白名单 - 只允许数字
if re.match(r'^[0-9]+$', user_input):
    process(user_input)

# 黑名单 - 试图拒绝危险字符（容易被绕过）
if '<script>' not in user_input.lower():  # 可绕过: <SCRIPT>, <scr ipt>
    process(user_input)
```

### Q2: 参数化查询如何防止 SQL 注入？

**A:**

参数化查询通过将数据和命令分离来防止注入：

```
传统字符串拼接:
query = "SELECT * FROM users WHERE name = '" + username + "'"
输入: ' OR '1'='1
结果: SELECT * FROM users WHERE name = '' OR '1'='1'  -- 永远为真

参数化查询:
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (username,))
输入被视为纯数据，不是 SQL 的一部分
```

**原理:**
1. SQL 语句先被解析、编译
2. 用户输入作为参数绑定，不参与解析
3. 数据库区分代码和数据

### Q3: 存储型 XSS 和反射型 XSS 的区别？如何防护？

**A:**

| 特性 | 反射型 XSS | 存储型 XSS |
|------|-----------|-----------|
| 存储位置 | URL 参数，不存储 | 数据库，永久存储 |
| 触发方式 | 点击恶意链接 | 访问包含恶意内容的页面 |
| 危害范围 | 单个用户 | 所有访问用户 |
| 发现难度 | 较易 | 较难 |

**防护措施:**

**反射型:**
- 输入验证
- 输出编码
- CSP 头部

**存储型:**
- 富文本清理 (bleach)
- 严格的输出编码
- 内容安全策略
- 审核机制

### Q4: 如何安全地处理文件上传？

**A:**

```python
def secure_file_upload(file, user_id):
    # 1. 验证文件大小
    max_size = 10 * 1024 * 1024  # 10MB
    if file.content_length > max_size:
        raise ValueError("File too large")
    
    # 2. 验证文件类型（不要依赖 Content-Type）
    allowed_extensions = {'.jpg', '.png', '.pdf'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise ValueError("Invalid file type")
    
    # 3. 验证魔术数字（Magic Number）
    magic = file.read(4)
    file.seek(0)
    valid_magic = {
        b'\xff\xd8\xff': 'jpg',
        b'\x89PNG': 'png',
        b'%PDF': 'pdf'
    }
    if not any(magic.startswith(m) for m in valid_magic):
        raise ValueError("File content doesn't match extension")
    
    # 4. 生成安全文件名（不保留原始文件名）
    import uuid
    safe_filename = f"{uuid.uuid4()}{ext}"
    
    # 5. 保存到非 Web 可访问目录
    upload_path = f"/secure/uploads/{user_id}/{safe_filename}"
    
    # 6. 可选：病毒扫描
    # scan_for_virus(file)
    
    # 7. 设置文件权限
    os.chmod(upload_path, 0o640)
    
    return safe_filename
```

---

## 相关概念

### 数据结构
- [字符串](../computer-science/data-structures/string.md)：输入数据的处理和编码
- [正则表达式](../computer-science/algorithms/string-matching.md)：模式匹配和验证

### 算法
- [编码算法](../computer-science/algorithms/encoding.md)：HTML、URL、Base64 编码
- [哈希算法](../cryptography/hash-functions.md)：输入完整性验证

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：输入验证算法的性能
- [正则表达式性能](../references/regex-performance.md)：ReDoS 防护

### 系统实现
- [Web 安全](./web-security.md)：Web 应用安全概述
- [安全编码](./secure-coding.md)：安全编码实践
- [会话管理](./session-management.md)：会话安全
- [身份认证](./authentication.md)：输入验证与认证

### 安全领域
- [SQL 注入](../application-security/sql-injection.md)：详细的 SQL 注入防护
- [CSRF](../application-security/csrf.md)：跨站请求伪造防护
- [密码学基础](../cryptography-basics.md)：加密与编码

---

## 参考资料

1. [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
2. [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
3. [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
4. [OWASP Top 10:2021](https://owasp.org/Top10/)
5. [Google Web Fundamentals - Security](https://developers.google.com/web/fundamentals/security)
