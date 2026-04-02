# 行为驱动开发 (Behavior-Driven Development / BDD)

## 简介

行为驱动开发（BDD）是一种敏捷软件开发方法，它鼓励开发人员、测试人员和业务人员之间的协作，通过使用自然语言描述软件的行为，确保所有人对需求的理解一致。BDD由Dan North在2003年提出，它扩展了测试驱动开发（TDD）的理念，将关注点从"测试"转向"行为"。

BDD的核心思想是用业务语言编写可执行的规格说明，这些规格说明既能作为需求文档，又能作为自动化测试，实现"活文档"（Living Documentation）的目标。

## 核心概念

### BDD的三大原则

1. **业务价值导向**：任何功能都应交付可衡量的业务价值
2. **足够就好**：只实现所需的最小功能
3. **统一语言**：使用领域通用语言（Ubiquitous Language）沟通

### BDD的工作流程

```
发现需求 → 明确验收标准 → 编写可执行规格 → 实现功能 → 验证行为
    ↓           ↓              ↓            ↓          ↓
  研讨会    Given-When-Then   .feature    编写代码    运行测试
```

### 统一语言（Ubiquitous Language）

BDD强调使用业务领域的术语来描述行为，消除技术术语和业务术语之间的隔阂。

```
技术术语                    业务术语
─────────────────────────────────────────
UserService.register()  →  用户注册
OrderRepository.save()  →  下单
PaymentGateway.charge() →  收款
```

### Given-When-Then格式

BDD使用特定的结构来描述场景：

```gherkin
Feature: 用户登录
  为了访问个人账户
  作为一个已注册用户
  我需要能够使用邮箱和密码登录

  Scenario: 使用有效凭据登录成功
    Given 用户 "张三" 已注册
    And 用户的邮箱是 "zhangsan@example.com"
    And 用户的密码是 "Password123"
    When 用户使用邮箱 "zhangsan@example.com" 和密码 "Password123" 登录
    Then 用户应该看到欢迎页面
    And 用户应该看到 "欢迎回来，张三"
```

| 关键字 | 含义 | 作用 |
|--------|------|------|
| **Given** | 前置条件 | 设置场景上下文 |
| **When**  | 触发事件 | 描述用户操作 |
| **Then**  | 预期结果 | 验证业务规则 |
| **And/But** | 连接词 | 扩展上述任一条件 |

## 实现方式

### 1. Gherkin语法

Gherkin是一种业务可读的领域特定语言，用于描述软件行为。

#### 基本结构

```gherkin
# 注释以#开头
Feature: 功能描述
  作为一个[角色]
  我想要[功能]
  以便于[业务价值]

  Background: 每个场景的共同前置条件
    Given 系统处于初始状态

  Scenario: 具体场景描述
    Given 前置条件
    When 操作
    Then 预期结果

  Scenario Outline: 参数化场景
    Given <输入条件>
    When <操作>
    Then <预期结果>

    Examples:
      | 输入条件 | 操作 | 预期结果 |
      | 值1     | 操作1 | 结果1   |
      | 值2     | 操作2 | 结果2   |
```

#### 完整示例

```gherkin
Feature: 购物车管理
  作为一个在线购物者
  我想要管理我的购物车
  以便于我可以整理要购买的商品

  Background:
    Given 以下商品可购买:
      | 商品名称   | 价格  | 库存 |
      | iPhone 15 | 6999 | 10  |
      | AirPods   | 1299 | 20  |
      | iPad Pro  | 8999 | 5   |

  Scenario: 添加商品到购物车
    Given 用户已登录
    And 购物车是空的
    When 用户将 "iPhone 15" 添加到购物车
    Then 购物车应该包含 1 件商品
    And 购物车总价应该是 ¥6999

  Scenario: 添加多个相同商品
    Given 用户已登录
    When 用户将 "AirPods" 添加到购物车
    And 用户将 "AirPods" 添加到购物车
    Then 购物车中 "AirPods" 的数量应该是 2
    And 购物车总价应该是 ¥2598

  Scenario Outline: 库存不足时添加商品
    Given 用户已登录
    And "<商品>" 的库存是 <库存>
    When 用户尝试添加 <数量> 个 "<商品>" 到购物车
    Then 应该显示错误 "库存不足"
    And 购物车中 "<商品>" 的数量应该是 0

    Examples:
      | 商品     | 库存 | 数量 |
      | iPad Pro | 5    | 10   |
      | AirPods  | 3    | 5    |

  Scenario: 从购物车移除商品
    Given 用户已登录
    And 购物车中有以下商品:
      | 商品名称   | 数量 | 单价  |
      | iPhone 15 | 1    | 6999 |
      | AirPods   | 2    | 1299 |
    When 用户从购物车移除 "iPhone 15"
    Then 购物车应该包含 1 件商品
    And 购物车总价应该是 ¥2598

  @smoke @checkout
  Scenario: 购物车结算
    Given 用户已登录
    And 购物车中有以下商品:
      | 商品名称   | 数量 | 单价  |
      | iPhone 15 | 1    | 6999 |
    When 用户点击结算按钮
    Then 应该跳转到结算页面
    And 订单金额应该是 ¥6999
```

### 2. Cucumber实现（Java）

```java
// features/shopping_cart.feature
// 上面的Gherkin示例

// stepdefinitions/ShoppingCartSteps.java
package stepdefinitions;

import io.cucumber.java.en.*;
import io.cucumber.datatable.DataTable;
import static org.junit.Assert.*;

public class ShoppingCartSteps {
    
    private ShoppingCart cart;
    private ProductCatalog catalog;
    private User currentUser;
    private String errorMessage;
    
    @Given("以下商品可购买:")
    public void setupProductCatalog(DataTable dataTable) {
        catalog = new ProductCatalog();
        dataTable.asMaps().forEach(row -> {
            Product product = new Product(
                row.get("商品名称"),
                Double.parseDouble(row.get("价格")),
                Integer.parseInt(row.get("库存"))
            );
            catalog.addProduct(product);
        });
    }
    
    @Given("用户已登录")
    public void userIsLoggedIn() {
        currentUser = new User("testuser", "Test User");
        cart = new ShoppingCart(currentUser);
    }
    
    @Given("购物车是空的")
    public void cartIsEmpty() {
        assertTrue(cart.isEmpty());
    }
    
    @When("用户将 {string} 添加到购物车")
    public void addProductToCart(String productName) {
        Product product = catalog.findByName(productName);
        cart.addItem(product, 1);
    }
    
    @Then("购物车应该包含 {int} 件商品")
    public void verifyCartItemCount(int count) {
        assertEquals(count, cart.getItemCount());
    }
    
    @Then("购物车总价应该是 ¥{int}")
    public void verifyCartTotal(int expectedTotal) {
        assertEquals(expectedTotal, cart.getTotal(), 0.01);
    }
    
    @Given("{string} 的库存是 {int}")
    public void setProductStock(String productName, int stock) {
        catalog.updateStock(productName, stock);
    }
    
    @When("用户尝试添加 {int} 个 {string} 到购物车")
    public void tryAddProductToCart(int quantity, String productName) {
        try {
            Product product = catalog.findByName(productName);
            cart.addItem(product, quantity);
        } catch (InsufficientStockException e) {
            errorMessage = e.getMessage();
        }
    }
    
    @Then("应该显示错误 {string}")
    public void verifyErrorMessage(String expectedError) {
        assertEquals(expectedError, errorMessage);
    }
    
    @Given("购物车中有以下商品:")
    public void setupCartWithItems(DataTable dataTable) {
        cart = new ShoppingCart(currentUser);
        dataTable.asMaps().forEach(row -> {
            Product product = new Product(
                row.get("商品名称"),
                Double.parseDouble(row.get("单价")),
                100
            );
            cart.addItem(product, Integer.parseInt(row.get("数量")));
        });
    }
    
    @When("用户从购物车移除 {string}")
    public void removeProductFromCart(String productName) {
        cart.removeItem(productName);
    }
}

// ShoppingCart.java
public class ShoppingCart {
    private User user;
    private List<CartItem> items = new ArrayList<>();
    
    public void addItem(Product product, int quantity) {
        if (product.getStock() < quantity) {
            throw new InsufficientStockException("库存不足");
        }
        
        Optional<CartItem> existing = items.stream()
            .filter(i -> i.getProduct().getName().equals(product.getName()))
            .findFirst();
            
        if (existing.isPresent()) {
            existing.get().addQuantity(quantity);
        } else {
            items.add(new CartItem(product, quantity));
        }
    }
    
    public double getTotal() {
        return items.stream()
            .mapToDouble(i -> i.getProduct().getPrice() * i.getQuantity())
            .sum();
    }
    // ... 其他方法
}
```

### 3. pytest-bdd实现（Python）

```python
# features/shopping_cart.feature
# 与Cucumber相同的Gherkin

# test_shopping_cart.py
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# 加载feature文件
scenarios('shopping_cart.feature')

# Fixtures
@pytest.fixture
def catalog():
    """商品目录"""
    return ProductCatalog()

@pytest.fixture
def cart(user):
    """购物车"""
    return ShoppingCart(user)

@pytest.fixture
def user():
    """当前用户"""
    return User("testuser", "Test User")

# Step Definitions
@given(parsers.parse('以下商品可购买:\n{data_table}'))
def setup_catalog(catalog, data_table):
    """设置商品目录"""
    for row in parse_data_table(data_table):
        product = Product(
            name=row['商品名称'],
            price=float(row['价格']),
            stock=int(row['库存'])
        )
        catalog.add_product(product)
    return catalog

@given('用户已登录')
def user_logged_in(user):
    """确保用户已登录"""
    return user

@given('购物车是空的')
def empty_cart(cart):
    """确保购物车为空"""
    cart.clear()
    return cart

@when(parsers.parse('用户将 "{product_name}" 添加到购物车'))
def add_product_to_cart(cart, catalog, product_name):
    """添加商品到购物车"""
    product = catalog.find_by_name(product_name)
    cart.add_item(product, 1)

@then(parsers.parse('购物车应该包含 {count:d} 件商品'))
def verify_cart_count(cart, count):
    """验证购物车商品数量"""
    assert cart.get_item_count() == count

@then(parsers.parse('购物车总价应该是 ¥{total:d}'))
def verify_cart_total(cart, total):
    """验证购物车总价"""
    assert cart.get_total() == total

@when(parsers.parse('用户尝试添加 {quantity:d} 个 "{product_name}" 到购物车'))
def try_add_product(cart, catalog, quantity, product_name):
    """尝试添加商品（可能失败）"""
    product = catalog.find_by_name(product_name)
    try:
        cart.add_item(product, quantity)
    except InsufficientStockError as e:
        pytest.error_message = str(e)

@then(parsers.parse('应该显示错误 "{expected_error}"'))
def verify_error_message(expected_error):
    """验证错误消息"""
    assert pytest.error_message == expected_error
```

### 4. SpecFlow实现（C#）

```csharp
// Features/ShoppingCart.feature
// 与上面相同的Gherkin

// StepDefinitions/ShoppingCartSteps.cs
using TechTalk.SpecFlow;
using Xunit;

[Binding]
public class ShoppingCartSteps
{
    private readonly ScenarioContext _context;
    private ProductCatalog _catalog;
    private ShoppingCart _cart;
    private User _currentUser;
    private string _errorMessage;

    public ShoppingCartSteps(ScenarioContext context)
    {
        _context = context;
    }

    [Given(@"以下商品可购买:")]
    public void Given以下商品可购买(Table table)
    {
        _catalog = new ProductCatalog();
        foreach (var row in table.Rows)
        {
            var product = new Product(
                row["商品名称"],
                double.Parse(row["价格"]),
                int.Parse(row["库存"])
            );
            _catalog.AddProduct(product);
        }
    }

    [Given(@"用户已登录")]
    public void Given用户已登录()
    {
        _currentUser = new User("testuser", "Test User");
        _cart = new ShoppingCart(_currentUser);
    }

    [When(@"用户将 "(.*)" 添加到购物车")]
    public void When用户将商品添加到购物车(string productName)
    {
        var product = _catalog.FindByName(productName);
        _cart.AddItem(product, 1);
    }

    [Then(@"购物车应该包含 (\d+) 件商品")]
    public void Then购物车应该包含件商品(int expectedCount)
    {
        Assert.Equal(expectedCount, _cart.GetItemCount());
    }

    [Then(@"购物车总价应该是 ¥(\d+)")]
    public void Then购物车总价应该是(double expectedTotal)
    {
        Assert.Equal(expectedTotal, _cart.GetTotal(), precision: 2);
    }
}
```

## 示例

### 示例故事映射（Story Mapping）

```
用户登录功能
├── 主干活动：用户认证
│   ├── 注册新账户
│   │   ├── 使用邮箱注册
│   │   ├── 使用手机号注册
│   │   └── 使用第三方账号注册
│   ├── 登录账户
│   │   ├── 邮箱密码登录
│   │   ├── 手机验证码登录
│   │   └── 第三方快捷登录
│   ├── 找回密码
│   │   ├── 邮箱找回
│   │   └── 手机找回
│   └── 账户安全
│       ├── 修改密码
│       └── 绑定/解绑手机
└── 发布优先级
    ├── MVP（必须）
    │   ├── 邮箱密码登录
    │   └── 邮箱找回密码
    ├── 迭代2（重要）
    │   └── 注册新账户
    └── 迭代3（可选）
        └── 第三方登录
```

### 完整BDD项目结构

```
project/
├── features/                    # Gherkin特性文件
│   ├── authentication/
│   │   ├── login.feature
│   │   ├── register.feature
│   │   └── forgot_password.feature
│   ├── shopping/
│   │   ├── browse_products.feature
│   │   ├── shopping_cart.feature
│   │   └── checkout.feature
│   └── order/
│       ├── create_order.feature
│       ├── track_order.feature
│       └── cancel_order.feature
├── step_definitions/            # 步骤定义
│   ├── auth_steps.py
│   ├── product_steps.py
│   ├── cart_steps.py
│   └── order_steps.py
├── support/                     # 支持代码
│   ├── hooks.py                # 生命周期钩子
│   ├── world.py                # 共享状态
│   └── env.py                  # 环境配置
├── src/                         # 业务代码
│   ├── domain/
│   ├── application/
│   └── infrastructure/
└── reports/                     # 测试报告
```

### 三一律示例（Rule of Three）

```gherkin
Feature: 账户注册

  Rule: 密码必须满足安全要求
    为了保护用户账户安全
    系统要求密码必须符合最小复杂度

    Example: 密码太短
      Given 用户在注册页面
      When 用户输入密码 "123"
      Then 应该显示错误 "密码长度至少8位"

    Example: 密码缺少数字
      Given 用户在注册页面
      When 用户输入密码 "password"
      Then 应该显示错误 "密码必须包含数字"

    Example: 有效密码
      Given 用户在注册页面
      When 用户输入密码 "Secure123"
      Then 密码应该被接受

  Rule: 邮箱必须唯一
    为了防止重复注册
    系统不允许使用已注册的邮箱

    Example: 使用已注册邮箱
      Given 邮箱 "user@example.com" 已被注册
      When 新用户尝试使用 "user@example.com" 注册
      Then 应该显示错误 "该邮箱已被注册"
      And 应该提供 "忘记密码" 链接
```

## 应用场景

### 1. 需求澄清工作坊（Three Amigos）

```
参与者：业务分析师 + 开发人员 + 测试人员

流程：
1. 业务分析师：描述用户故事和验收标准
2. 开发人员：提出技术可行性问题
3. 测试人员：识别边界情况和异常场景
4. 共同：编写Gherkin场景
5. 确认：所有场景覆盖需求

输出：可执行的Gherkin特性文件
```

### 2. 活文档（Living Documentation）

```
传统文档                    BDD活文档
─────────────────────────────────────────
需求文档（静态）      →    feature文件（可执行）
测试用例（单独维护）  →    场景定义（与代码同步）
用户手册（易过时）    →    自动生成文档
```

### 3. 持续集成中的BDD

```yaml
# .github/workflows/bdd.yml
name: BDD Tests

on: [push, pull_request]

jobs:
  bdd:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Cucumber Tests
        run: mvn test -Dcucumber.options="--tags @smoke"
      
      - name: Generate Living Documentation
        run: mvn cluecumber-report:reporting
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: bdd-report
          path: target/cluecumber-report/
```

### 4. 验收测试驱动开发（ATDD）

```
1. 讨论（Discuss）
   └── 与业务方确认验收标准
   
2. 提炼（Distill）
   └── 将验收标准转化为可执行场景
   
3. 开发（Develop）
   └── 编写代码使场景通过
   
4. 演示（Demonstrate）
   └── 向业务方展示可工作的软件
```

## 面试要点

### 常见问题

**Q1: BDD和TDD有什么区别和联系？**

| 方面 | TDD | BDD |
|------|-----|-----|
| 出发点 | 技术实现 | 业务行为 |
| 受众 | 开发人员 | 全员参与 |
| 描述语言 | 编程语言 | 业务语言 |
| 关注点 | 代码正确性 | 业务价值 |
| 输出 | 测试代码 | 可执行规格 |

**联系**：BDD是TDD的扩展，继承了测试先行的思想，但强调用业务语言描述行为。

**Q2: 什么是好的BDD场景？**

- **具体（Concrete）**：使用真实数据而非抽象概念
- **有价值（Valuable）**：每个场景都验证业务价值
- **自治（Self-contained）**：场景之间相互独立
- **简短（Small）**：聚焦单一业务规则
- **可测试（Testable）**：能够自动化验证

```gherkin
# 不好的示例（太抽象）
Scenario: 用户购买商品
  Given 用户已登录
  When 用户购买商品
  Then 购买成功

# 好的示例（具体）
Scenario: VIP用户购买打折商品享受折上折
  Given 用户"张三"是VIP会员
  And "iPhone 15"原价¥6999，当前促销价¥5999
  When 用户购买"iPhone 15"
  Then 订单金额应该是¥5399（VIP额外9折）
```

**Q3: 如何避免BDD场景成为维护负担？**

1. **业务语言优先**：避免技术细节泄露到Gherkin
2. **DRY原则**：使用Background和Scenario Outline减少重复
3. **粒度控制**：场景描述"做什么"而非"怎么做"
4. **定期重构**：像对待代码一样重构特性文件
5. **团队协作**：确保业务方参与场景编写

**Q4: BDD中的反模式有哪些？**

```gherkin
# 反模式1：技术细节泄露
When 用户点击id为"submit-btn"的按钮  # 坏：提到技术实现
When 用户提交表单                   # 好：使用业务语言

# 反模式2：场景之间相互依赖
Scenario: 场景A
  Given 场景B已经完成               # 坏：依赖其他场景

# 反模式3：过度使用Scenario Outline
# 坏：所有场景都用参数化，降低可读性
# 好：只在真正需要数据变化时使用

# 反模式4：UI操作细节
When 用户在搜索框输入"手机"         # 相对好
When 用户在id为"search-input"的元素输入"手机"  # 坏：太技术
```

**Q5: 如何说服团队采用BDD？**

- **从痛点出发**：解决需求理解不一致的问题
- **小步尝试**：从一个用户故事开始
- **展示价值**：活文档、减少返工
- **工具支持**：选择团队熟悉的技术栈
- **持续培训**：组织Three Amigos工作坊

## 相关概念

### 相关开发方法

- [TDD（测试驱动开发）](tdd.md) - BDD的基础
- [ATDD（验收测试驱动开发）](atdd.md) - BDD的实践形式
- [领域驱动设计](ddd.md) - 统一语言概念来源
- [实例化需求](specification-by-example.md) - 需求澄清方法

### 相关工具框架

| 语言 | 工具 | 说明 |
|------|------|------|
| Java | Cucumber-JVM, JBehave | 主流BDD框架 |
| Python | pytest-bdd, behave | Python生态 |
| JavaScript | Cucumber.js, CodeceptJS | Node.js环境 |
| C# | SpecFlow | .NET首选 |
| Ruby | Cucumber | 起源语言 |
| Go | Godog | Go实现 |

### 设计原则

- **INVEST原则**：用户故事的特性
- **SMART原则**：验收标准的要求
- **3A模式**：Arrange-Act-Assert
- **Given-When-Then**：场景描述结构

### 协作实践

- **Three Amigos**：需求澄清会议
- **Example Mapping**：场景识别工作坊
- **Impact Mapping**：影响地图规划
- **Story Mapping**：故事地图梳理
