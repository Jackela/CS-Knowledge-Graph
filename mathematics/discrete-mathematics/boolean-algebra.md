# 布尔代数 (Boolean Algebra)

## 简介

布尔代数（Boolean Algebra）是处理二元值（真/假、0/1）的代数系统，由乔治·布尔（George Boole）在19世纪中叶创立。布尔代数是数字逻辑、计算机电路设计和程序逻辑的基础，在现代计算机科学中具有核心地位。

## 核心概念

### 基本运算

```python
class BooleanAlgebra:
    """布尔代数基本运算"""
    
    @staticmethod
    def AND(a, b):
        """与运算：仅当两者都为真时结果为真"""
        return a and b
    
    @staticmethod
    def OR(a, b):
        """或运算：任一者为真时结果为真"""
        return a or b
    
    @staticmethod
    def NOT(a):
        """非运算：取反"""
        return not a
    
    @staticmethod
    def XOR(a, b):
        """异或运算：两者不同时结果为真"""
        return a != b
    
    @staticmethod
    def NAND(a, b):
        """与非运算：AND后取反"""
        return not (a and b)
    
    @staticmethod
    def NOR(a, b):
        """或非运算：OR后取反"""
        return not (a or b)

# 真值表生成
def generate_truth_table(operation, name):
    """生成真值表"""
    print(f"\n{name} Truth Table:")
    print("A | B | Result")
    print("-" * 15)
    for a in [False, True]:
        for b in [False, True]:
            result = operation(a, b)
            print(f"{int(a)} | {int(b)} | {int(result)}")

generate_truth_table(BooleanAlgebra.AND, "AND")
generate_truth_table(BooleanAlgebra.OR, "OR")
generate_truth_table(BooleanAlgebra.XOR, "XOR")
```

### 布尔代数定律

```python
class BooleanLaws:
    """布尔代数基本定律验证"""
    
    @staticmethod
    def verify_all():
        """验证所有布尔代数定律"""
        values = [False, True]
        
        for a in values:
            for b in values:
                for c in values:
                    # 交换律
                    assert (a and b) == (b and a), "AND Commutative"
                    assert (a or b) == (b or a), "OR Commutative"
                    
                    # 结合律
                    assert ((a and b) and c) == (a and (b and c))
                    assert ((a or b) or c) == (a or (b or c))
                    
                    # 分配律
                    assert (a and (b or c)) == ((a and b) or (a and c))
                    assert (a or (b and c)) == ((a or b) and (a or c))
                    
                    # 德摩根定律
                    assert (not (a and b)) == ((not a) or (not b))
                    assert (not (a or b)) == ((not a) and (not b))
                    
                    # 同一律
                    assert (a and True) == a
                    assert (a or False) == a
                    
                    # 零律
                    assert (a and False) == False
                    assert (a or True) == True
                    
                    # 互补律
                    assert (a and (not a)) == False
                    assert (a or (not a)) == True
                    
                    # 双重否定
                    assert (not (not a)) == a
        
        print("All Boolean laws verified!")

BooleanLaws.verify_all()
```

## 实现方式

### 位运算实现

```python
class BitOperations:
    """位运算操作"""
    
    @staticmethod
    def set_bit(n, pos):
        """设置第pos位为1"""
        return n | (1 << pos)
    
    @staticmethod
    def clear_bit(n, pos):
        """清除第pos位（设为0）"""
        return n & ~(1 << pos)
    
    @staticmethod
    def toggle_bit(n, pos):
        """翻转第pos位"""
        return n ^ (1 << pos)
    
    @staticmethod
    def get_bit(n, pos):
        """获取第pos位的值"""
        return (n >> pos) & 1
    
    @staticmethod
    def count_set_bits(n):
        """计算置位位数（汉明重量）"""
        count = 0
        while n:
            count += n & 1
            n >>= 1
        return count
    
    @staticmethod
    def is_power_of_two(n):
        """检查是否为2的幂"""
        return n > 0 and (n & (n - 1)) == 0
    
    @staticmethod
    def lowest_set_bit(n):
        """获取最低位的置位位置"""
        if n == 0:
            return -1
        return (n & -n).bit_length() - 1

# 示例
bits = BitOperations()
n = 0b10110  # 22
print(bin(bits.set_bit(n, 0)))      # 0b10111
print(bin(bits.clear_bit(n, 1)))    # 0b10100
print(bits.count_set_bits(n))       # 3
print(bits.is_power_of_two(16))     # True
```

### 布尔表达式化简

```python
class BooleanExpression:
    """布尔表达式处理"""
    
    def __init__(self, variables, minterms):
        """
        variables: 变量列表
        minterms: 最小项列表（真值表结果为1的行号）
        """
        self.variables = variables
        self.minterms = minterms
    
    def to_canonical_sop(self):
        """转换为标准和之积（Sum of Products）"""
        terms = []
        for m in self.minterms:
            term = []
            for i, var in enumerate(self.variables):
                if m & (1 << (len(self.variables) - 1 - i)):
                    term.append(var)
                else:
                    term.append(f"~{var}")
            terms.append("*".join(term))
        return " + ".join(terms)
    
    @staticmethod
    def simplify_karnaugh(variables, truth_table):
        """
        使用卡诺图简化布尔表达式
        （简化实现，仅演示概念）
        """
        # 卡诺图简化逻辑较复杂，此处为概念演示
        ones = [i for i, v in enumerate(truth_table) if v == 1]
        return f"Minterms: {ones}"

# 示例：半加器
# A B | Sum Carry
# 0 0 |  0   0
# 0 1 |  1   0
# 1 0 |  1   0
# 1 1 |  0   1

sum_expr = BooleanExpression(['A', 'B'], [1, 2])
print("Sum:", sum_expr.to_canonical_sop())  # ~A*B + A*~B

carry_expr = BooleanExpression(['A', 'B'], [3])
print("Carry:", carry_expr.to_canonical_sop())  # A*B
```

## 示例

### 逻辑门电路模拟

```python
class LogicGate:
    """逻辑门模拟"""
    
    def __init__(self, gate_type, inputs):
        self.gate_type = gate_type
        self.inputs = inputs
    
    def evaluate(self):
        if self.gate_type == "AND":
            return all(self.inputs)
        elif self.gate_type == "OR":
            return any(self.inputs)
        elif self.gate_type == "NOT":
            return not self.inputs[0]
        elif self.gate_type == "XOR":
            return sum(self.inputs) % 2 == 1
        elif self.gate_type == "NAND":
            return not all(self.inputs)
        elif self.gate_type == "NOR":
            return not any(self.inputs)

class Circuit:
    """逻辑电路"""
    
    def __init__(self):
        self.gates = []
    
    def add_gate(self, gate):
        self.gates.append(gate)
    
    def simulate(self):
        """模拟电路"""
        results = []
        for gate in self.gates:
            results.append(gate.evaluate())
        return results

# 全加器电路
class FullAdder:
    """全加器实现"""
    
    @staticmethod
    def add(a, b, carry_in):
        """
        全加器：计算 a + b + carry_in
        返回 (sum, carry_out)
        """
        # 和 = A XOR B XOR Cin
        sum_bit = a ^ b ^ carry_in
        
        # 进位 = (A AND B) OR (Cin AND (A XOR B))
        carry_out = (a and b) or (carry_in and (a ^ b))
        
        return sum_bit, carry_out

# 多位加法器
class RippleCarryAdder:
    """行波进位加法器"""
    
    @staticmethod
    def add(a, b, n_bits):
        """n位二进制加法"""
        carry = 0
        result = 0
        
        for i in range(n_bits):
            a_bit = (a >> i) & 1
            b_bit = (b >> i) & 1
            
            sum_bit, carry = FullAdder.add(a_bit, b_bit, carry)
            result |= (sum_bit << i)
        
        return result, carry  # 结果和最终进位

# 示例
adder = RippleCarryAdder()
result, final_carry = adder.add(5, 3, 4)  # 0101 + 0011
print(f"5 + 3 = {result}, carry = {final_carry}")  # 8, 0
```

## 应用场景

### 布尔代数在计算机科学中的应用

1. **数字电路设计**：逻辑门、组合电路、时序电路
2. **程序逻辑**：条件判断、布尔表达式优化
3. **数据库查询**：SQL WHERE子句优化
4. **搜索引擎**：布尔查询（AND/OR/NOT）
5. **数据压缩**：位图索引、布隆过滤器

## 面试要点

**Q: 德摩根定律的内容和应用？**
A: 德摩根定律：
- ¬(A ∧ B) = ¬A ∨ ¬B
- ¬(A ∨ B) = ¬A ∧ ¬B

应用：简化复杂条件、逻辑电路优化、软件中的条件取反。

**Q: 如何用位运算实现状态压缩？**
A: 使用二进制位表示布尔状态：
- 设置状态：flags |= (1 << n)
- 清除状态：flags &= ~(1 << n)
- 检查状态：flags & (1 << n)
- 切换状态：flags ^= (1 << n)

**Q: 为什么计算机使用二进制？**
A: 主要原因：
- 物理实现简单（高低电压）
- 布尔代数的数学基础
- 抗干扰能力强
- 逻辑运算与算术运算统一

## 相关概念

### 数据结构
- [位图](../computer-science/data-structures/bitmap.md) - 位运算应用
- [布隆过滤器](../computer-science/data-structures/bloom-filter.md) - 概率数据结构

### 算法
- [位运算技巧](../computer-science/algorithms/bit-manipulation.md) - 高级位操作

### 复杂度分析
- [电路复杂度](../computer-science/algorithms/circuit-complexity.md) - 布尔电路分析

### 系统实现
- [数字逻辑](../computer-science/architecture/digital-logic.md) - 硬件实现
- [布尔查询](../computer-science/databases/boolean-query.md) - 数据库应用
