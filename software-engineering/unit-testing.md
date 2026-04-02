# 单元测试 (Unit Testing)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自《单元测试的艺术》、xUnit测试模式及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 定义

单元测试是[代码质量](./code-quality.md)的基础保障。

---

## 测试原则

### FIRST原则

| 字母 | 原则 | 说明 |
|------|------|------|
| **F** | Fast (快速) | 测试应该快速执行，毫秒级 |
| **I** | Independent (独立) | 测试之间相互独立，不依赖执行顺序 |
| **R** | Repeatable (可重复) | 在任何环境都能稳定运行 |
| **S** | Self-validating (自验证) | 测试结果明确通过或失败 |
| **T** | Timely (及时) | 与生产代码同步编写 |

### AAA模式

```python
def test_calculator_add():
    # Arrange (准备)
    calculator = Calculator()
    a, b = 2, 3
    
    # Act (执行)
    result = calculator.add(a, b)
    
    # Assert (断言)
    assert result == 5
```

---

## 测试框架

### Python (pytest)

```python
# 安装: pip install pytest pytest-mock

# 基本测试
import pytest
from calculator import Calculator

class TestCalculator:
    @pytest.fixture
    def calculator(self):
        """测试夹具"""
        return Calculator()
    
    def test_add(self, calculator):
        """测试加法"""
        assert calculator.add(2, 3) == 5
        assert calculator.add(-1, 1) == 0
    
    def test_divide_by_zero(self, calculator):
        """测试除零异常"""
        with pytest.raises(ZeroDivisionError):
            calculator.divide(10, 0)
    
    @pytest.mark.parametrize("a,b,expected", [
        (2, 3, 5),
        (0, 0, 0),
        (-1, -1, -2),
    ])
    def test_add_parametrized(self, calculator, a, b, expected):
        """参数化测试"""
        assert calculator.add(a, b) == expected

# Mock测试
from unittest.mock import Mock, patch, MagicMock

def test_fetch_user_data():
    """测试外部依赖"""
    with patch('module.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"name": "张三"}
        
        result = fetch_user_data(1)
        
        assert result["name"] == "张三"
        mock_get.assert_called_once_with("https://api.example.com/users/1")
```

### Java (JUnit 5)

```java
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@DisplayName("计算器测试")
class CalculatorTest {
    
    private Calculator calculator;
    
    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }
    
    @Test
    @DisplayName("加法测试")
    void testAdd() {
        assertEquals(5, calculator.add(2, 3));
        assertEquals(0, calculator.add(-1, 1));
    }
    
    @ParameterizedTest
    @CsvSource({"2, 3, 5", "0, 0, 0", "-1, -1, -2"})
    @DisplayName("参数化加法测试")
    void testAddParameterized(int a, int b, int expected) {
        assertEquals(expected, calculator.add(a, b));
    }
    
    @Test
    @DisplayName("除零异常测试")
    void testDivideByZero() {
        assertThrows(ArithmeticException.class, () -> {
            calculator.divide(10, 0);
        });
    }
    
    // Mock测试
    @Test
    @DisplayName("Mock依赖测试")
    void testWithMock() {
        UserRepository mockRepo = mock(UserRepository.class);
        when(mockRepo.findById(1L)).thenReturn(new User("张三"));
        
        UserService service = new UserService(mockRepo);
        User user = service.getUser(1L);
        
        assertEquals("张三", user.getName());
        verify(mockRepo).findById(1L);
    }
}
```

### JavaScript (Jest)

```javascript
// 安装: npm install --save-dev jest

// calculator.test.js
const Calculator = require('./calculator');

describe('Calculator', () => {
    let calculator;
    
    beforeEach(() => {
        calculator = new Calculator();
    });
    
    test('adds two numbers', () => {
        expect(calculator.add(2, 3)).toBe(5);
        expect(calculator.add(-1, 1)).toBe(0);
    });
    
    test('throws on divide by zero', () => {
        expect(() => calculator.divide(10, 0))
            .toThrow('Cannot divide by zero');
    });
    
    // 参数化测试
    test.each([
        [2, 3, 5],
        [0, 0, 0],
        [-1, -1, -2],
    ])('add(%i, %i) returns %i', (a, b, expected) => {
        expect(calculator.add(a, b)).toBe(expected);
    });
    
    // Mock测试
    test('fetches user data', async () => {
        const mockFetch = jest.fn()
            .mockResolvedValue({
                json: () => Promise.resolve({ name: '张三' })
            });
        global.fetch = mockFetch;
        
        const result = await fetchUserData(1);
        
        expect(result.name).toBe('张三');
        expect(mockFetch).toHaveBeenCalledWith(
            'https://api.example.com/users/1'
        );
    });
});
```

---

## 测试替身 (Test Doubles)

```
┌─────────────────────────────────────────────────────────────┐
│                    测试替身类型                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Dummy (假对象)                                             │
│  └── 仅填充参数，不会被使用                                  │
│                                                             │
│  Fake (伪造对象)                                            │
│  └── 有功能的简化实现，如内存数据库                          │
│                                                             │
│  Stub (桩对象)                                              │
│  └── 预设返回值，用于指定场景                                │
│                                                             │
│  Mock (模拟对象)                                            │
│  └── 验证交互行为，检查调用次数/参数                         │
│                                                             │
│  Spy (间谍对象)                                             │
│  └── 记录调用信息，用于事后验证                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 测试覆盖率

| 类型 | 定义 | 目标 |
|------|------|------|
| **行覆盖** (Line) | 执行的代码行比例 | > 80% |
| **分支覆盖** (Branch) | 执行的分支比例 | > 70% |
| **函数覆盖** (Function) | 调用的函数比例 | > 90% |
| **语句覆盖** (Statement) | 执行的语句比例 | > 80% |

```
⚠️ 注意：
- 高覆盖率 ≠ 高质量测试
- 100%覆盖率也可能有bug
- 关注测试质量，而非仅追求数字
```

---

## TDD (测试驱动开发)

```
TDD循环（红-绿-重构）：

    ┌─────────────┐
    │  1. 写一个  │
    │  失败的测试  │
    │   (Red)     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  2. 写最少  │
    │  代码使测试  │
    │  通过(Green)│
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  3. 重构    │
    │  (Refactor) │
    └──────┬──────┘
           │
           └──────▶ 回到步骤1

好处：
- 确保测试可运行
- 聚焦需求
- 产生可测试的代码
- 安全重构
```

---

## 测试策略

### 测试金字塔

```
        /\
       /  \
      / E2E\          ← 端到端测试 (少量)
     /────────\         慢、昂贵、脆弱
    /          \
   / Integration \     ← 集成测试 (中等)
  /────────────────\      测试组件交互
 /                  \
/     Unit Tests     \  ← 单元测试 (大量)
────────────────────────   快、廉价、稳定

比例建议：
- 单元测试: 70%
- 集成测试: 20%
- E2E测试: 10%
```

---

## 常见反模式

```python
# ❌ 测试过多实现细节
def test_user_creation():
    user = User("张三")
    assert user._name == "张三"  # 测试私有属性

# ✅ 测试行为
def test_user_get_name():
    user = User("张三")
    assert user.get_name() == "张三"

# ❌ 测试之间互相依赖
def test_create():
    global user_id
    user_id = create_user()
    assert user_id is not None

def test_update():  # 依赖test_create
    update_user(user_id)  # 可能失败

# ✅ 每个测试独立
def test_create_user():
    user_id = create_user()
    assert user_id is not None

def test_update_user():
    user_id = create_user()
    result = update_user(user_id)
    assert result is True

# ❌ 逻辑复杂的测试
def test_complex():
    for i in range(100):
        if i % 2 == 0:
            assert foo(i) == i * 2
        else:
            assert foo(i) == i + 1

# ✅ 使用参数化测试
@pytest.mark.parametrize("input,expected", [
    (0, 0), (2, 4), (4, 8),
    (1, 2), (3, 4), (5, 6),
])
def test_foo(input, expected):
    assert foo(input) == expected
```

---

## 相关概念

- [代码审查](../software-engineering/code-review.md) - 检查测试质量
- [重构](../software-engineering/refactoring.md) - 测试是重构的安全网
- [TDD](./testing/tdd.md) - 测试驱动开发方法论
- [CI/CD](../cloud-devops/cicd/github-actions.md) - 自动化测试执行
- [代码覆盖率](./testing/code-coverage.md) - 测试完整性度量


---

## 参考资料

1. "Unit Testing Principles, Practices, and Patterns" by Vladimir Khorikov
2. "Test Driven Development: By Example" by Kent Beck
3. "xUnit Test Patterns" by Gerard Meszaros
4. [pytest文档](https://docs.pytest.org/)
5. [JUnit 5文档](https://junit.org/junit5/docs/current/user-guide/)

---

*最后更新：2024年*
