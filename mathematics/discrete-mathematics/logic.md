# 逻辑 (Logic)

## 简介

**逻辑 (Logic)** 是研究推理有效性的数学分支，为计算机科学提供形式化推理的基础。在编程语言设计、硬件电路、人工智能、数据库查询和形式验证等领域，逻辑都扮演着核心角色。理解逻辑有助于写出正确的程序、设计可靠的系统和进行严谨的推理。

```
┌─────────────────────────────────────────────────────────────┐
│                   逻辑核心内容                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │ 命题逻辑 │  │ 谓词逻辑 │  │ 逻辑等价 │  │ 范式     │   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │ 推理规则 │  │ 归结原理 │  │ 模态逻辑 │  │ 时序逻辑 │   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 核心概念

### 命题逻辑 (Propositional Logic)

```
命题 (Proposition)：能判断真假的陈述句

基本联结词：
- ¬  (非/NOT)：¬p 为真当且仅当 p 为假
- ∧  (合取/AND)：p ∧ q 为真当且仅当 p,q 都为真
- ∨  (析取/OR)：p ∨ q 为真当且仅当 p,q 至少一个为真
- →  (蕴含/IMPLIES)：p → q 为假当且仅当 p真q假
- ↔  (等价/IFF)：p ↔ q 为真当且仅当 p,q 同真假

真值表示例：
┌───┬───┬─────┬─────┬─────┬─────┐
│ p │ q │ ¬p  │p∧q  │p∨q  │p→q  │
├───┼───┼─────┼─────┼─────┼─────┤
│ T │ T │  F  │  T  │  T  │  T  │
│ T │ F │  F  │  F  │  T  │  F  │
│ F │ T │  T  │  F  │  T  │  T  │
│ F │ F │  T  │  F  │  F  │  T  │
└───┴───┴─────┴─────┴─────┴─────┘

注意：p → q 只在 p真q假时为假（善意推定原则）
       假命题蕴含任何命题都为真
```

### 逻辑等价 (Logical Equivalence)

```
两个命题公式等价：在所有赋值下真值相同，记作 A ≡ B

重要等价式：
- 双重否定：¬(¬p) ≡ p
- 德摩根律：¬(p ∧ q) ≡ ¬p ∨ ¬q
            ¬(p ∨ q) ≡ ¬p ∧ ¬q
- 分配律：p ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r)
          p ∨ (q ∧ r) ≡ (p ∨ q) ∧ (p ∨ r)
- 结合律：(p ∧ q) ∧ r ≡ p ∧ (q ∧ r)
          (p ∨ q) ∨ r ≡ p ∨ (q ∨ r)
- 交换律：p ∧ q ≡ q ∧ p
          p ∨ q ≡ q ∨ p
- 蕴含等价：p → q ≡ ¬p ∨ q
            p → q ≡ ¬q → ¬p (逆否命题)
- 吸收律：p ∨ (p ∧ q) ≡ p
          p ∧ (p ∨ q) ≡ p
```

```python
# 逻辑等价验证
def evaluate(expr, values):
    """计算命题公式的真值"""
    # values = {'p': True, 'q': False, ...}
    return eval(expr, {"__builtins__": {}}, values)

def check_equivalence(expr1, expr2, variables):
    """检查两个公式是否逻辑等价"""
    from itertools import product
    
    for values in product([True, False], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        if evaluate(expr1, assignment) != evaluate(expr2, assignment):
            return False, assignment
    return True, None

# 验证德摩根律
print("验证 ¬(p ∧ q) ≡ ¬p ∨ ¬q:")
equiv, counter = check_equivalence("not (p and q)", "(not p) or (not q)", ["p", "q"])
print(f"  等价: {equiv}")

# 验证蕴含等价
print("\n验证 p → q ≡ ¬p ∨ q:")
equiv, counter = check_equivalence("(not p) or q", "(not p) or q", ["p", "q"])
print(f"  等价: {equiv}")

# 真值表生成器
def truth_table(expr, variables):
    """生成真值表"""
    from itertools import product
    
    print(f"{' '.join(variables)} | 结果")
    print("-" * (2 * len(variables) + 5))
    
    for values in product([True, False], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        result = evaluate(expr, assignment)
        vals = ' '.join('T' if v else 'F' for v in values)
        print(f"{vals} | {'T' if result else 'F'}")

print("\np → q 的真值表:")
truth_table("(not p) or q", ["p", "q"])
```

### 范式 (Normal Forms)

```
合取范式 (CNF)：子句的合取
- 形式：(A₁ ∨ A₂ ∨ ...) ∧ (B₁ ∨ B₂ ∨ ...) ∧ ...
- 每个子句是文字的析取
- 示例：(p ∨ ¬q) ∧ (¬p ∨ q ∨ r) ∧ ¬r

析取范式 (DNF)：短语的析取
- 形式：(A₁ ∧ A₂ ∧ ...) ∨ (B₁ ∧ B₂ ∧ ...) ∨ ...
- 每个短语是文字的合取
- 示例：(p ∧ ¬q) ∨ (¬p ∧ q ∧ r) ∨ ¬r

转换为CNF的步骤：
1. 消去 ↔：A ↔ B ≡ (A → B) ∧ (B → A)
2. 消去 →：A → B ≡ ¬A ∨ B
3. 内移 ¬：应用德摩根律
4. 分配 ∨ 到 ∧：A ∨ (B ∧ C) ≡ (A ∨ B) ∧ (A ∨ C)
```

```python
def to_cnf(formula):
    """
    将公式转换为合取范式（简化版）
    使用真值表法：对于使公式为假的每一行，生成一个子句
    """
    from itertools import product
    
    # 解析变量
    variables = sorted(set(c for c in formula if c.isalpha()))
    
    clauses = []
    for values in product([True, False], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        if not evaluate(formula, assignment):
            # 这一行使公式为假，生成子句
            clause = []
            for var, val in zip(variables, values):
                clause.append(var if not val else f"¬{var}")
            clauses.append(f"({' ∨ '.join(clause)})")
    
    if not clauses:
        return "True（永真式）"
    return " ∧ ".join(clauses)

# 示例
def evaluate_simple(formula, values):
    """简化版求值"""
    # 替换变量
    for var, val in values.items():
        formula = formula.replace(var, str(val))
    # 求值
    return eval(formula)

# (p ∧ q) → r 的CNF
# ≡ ¬(p ∧ q) ∨ r ≡ ¬p ∨ ¬q ∨ r
print("(p ∧ q) → r 的CNF:")
print("  手工计算: ¬p ∨ ¬q ∨ r")
```

### 谓词逻辑 (Predicate Logic)

```
谓词 (Predicate)：P(x)，表示x具有性质P
量词 (Quantifiers)：
- ∀  (全称量词/For All)：∀x P(x) 表示所有x都满足P
- ∃  (存在量词/Exists)：∃x P(x) 表示存在x满足P

量词否定：
- ¬∀x P(x) ≡ ∃x ¬P(x)
- ¬∃x P(x) ≡ ∀x ¬P(x)

量词分配：
- ∀x (P(x) ∧ Q(x)) ≡ ∀x P(x) ∧ ∀x Q(x)
- ∃x (P(x) ∨ Q(x)) ≡ ∃x P(x) ∨ ∃x Q(x)
- 注意：∀对∨、∃对∧不分配

示例：
- ∀x (Human(x) → Mortal(x))：所有人都是会死的
- ∃x (Student(x) ∧ Smart(x))：存在聪明的学生
```

```python
# 谓词逻辑的Python模拟
class Predicate:
    """谓词逻辑模拟"""
    
    def __init__(self, domain):
        self.domain = domain  # 论域
    
    def forall(self, predicate):
        """全称量词 ∀ """
        return all(predicate(x) for x in self.domain)
    
    def exists(self, predicate):
        """存在量词 ∃ """
        return any(predicate(x) for x in self.domain)

# 示例：数学性质
numbers = range(1, 11)
logic = Predicate(numbers)

# ∀x (x > 0)
is_positive = logic.forall(lambda x: x > 0)
print(f"∀x∈[1,10] (x > 0): {is_positive}")

# ∃x (x是偶数)
is_even = lambda x: x % 2 == 0
has_even = logic.exists(is_even)
print(f"∃x∈[1,10] (x是偶数): {has_even}")

# ∀x (偶数 → 可被2整除)
implies = lambda p, q: (not p) or q
even_implies_div2 = logic.forall(
    lambda x: implies(x % 2 == 0, x % 2 == 0)
)
print(f"∀x (Even(x) → DivisibleBy2(x)): {even_implies_div2}")
```

### 推理规则 (Inference Rules)

```
基本推理规则：

假言推理 (Modus Ponens)：
  p → q
  p
  ─────
  ∴ q

拒取式 (Modus Tollens)：
  p → q
  ¬q
  ─────
  ∴ ¬p

假言三段论：
  p → q
  q → r
  ─────
  ∴ p → r

析取三段论：
  p ∨ q
  ¬p
  ─────
  ∴ q

合取引入：
  p
  q
  ─────
  ∴ p ∧ q

合取消除：
  p ∧ q
  ─────
  ∴ p  (或 ∴ q)
```

```python
# 推理验证器
class InferenceEngine:
    """简单推理引擎"""
    
    @staticmethod
    def modus_ponens(implies, premise):
        """假言推理: (p→q, p) ⊢ q """
        if implies[0] == premise:
            return implies[1]
        return None
    
    @staticmethod
    def modus_tollens(implies, neg_conclusion):
        """拒取式: (p→q, ¬q) ⊢ ¬p """
        if implies[1] == f"not {neg_conclusion.replace('not ', '')}".strip():
            return f"not {implies[0]}"
        return None
    
    @staticmethod
    def hypothetical_syllogism(imp1, imp2):
        """假言三段论: (p→q, q→r) ⊢ p→r """
        if imp1[1] == imp2[0]:
            return (imp1[0], imp2[1])
        return None
    
    @staticmethod
    def disjunctive_syllogism(disjunction, neg_premise):
        """析取三段论: (p∨q, ¬p) ⊢ q """
        p, q = disjunction
        if f"not {p}" == neg_premise:
            return q
        if f"not {q}" == neg_premise:
            return p
        return None

# 示例推理
engine = InferenceEngine()

# 假言推理
result = engine.modus_ponens(("下雨", "地湿"), "下雨")
print(f"假言推理: 下雨→地湿, 下雨 ⊢ {result}")

# 拒取式
result = engine.modus_tollens(("下雨", "地湿"), "not 地湿")
print(f"拒取式: 下雨→地湿, ¬地湿 ⊢ {result}")

# 假言三段论
result = engine.hypothetical_syllogism(("是人", "会死"), ("会死", "怕死"))
print(f"假言三段论: 是人→会死, 会死→怕死 ⊢ {result[0]}→{result[1]}")
```

### 归结原理 (Resolution)

```
归结：从两个子句推导出新子句的推理规则

规则：
  (A ∨ L)    (B ∨ ¬L)
  ────────────────────
       (A ∨ B)

其中 L 是互补文字（一个正文字，一个负文字）

归结证明过程：
1. 将所有前提转换为子句形式（CNF）
2. 将结论的否定加入子句集
3. 反复应用归结规则
4. 如果得到空子句（矛盾），则证明成立

示例：
前提1：p ∨ q
前提2：¬p ∨ r
前提3：¬q
结论：r

证明：
1. p ∨ q       （前提）
2. ¬p ∨ r      （前提）
3. ¬q          （前提）
4. ¬r          （结论的否定）
5. p           （1,3归结）
6. r           （2,5归结）
7. □（空子句）  （4,6归结，矛盾！）
```

```python
class ResolutionProver:
    """基于归结原理的简单定理证明器"""
    
    def __init__(self):
        self.clauses = []
    
    def add_clause(self, clause):
        """添加子句（文字集合）"""
        self.clauses.append(set(clause))
    
    def resolve(self, c1, c2):
        """对两个子句进行归结"""
        new_clauses = []
        for lit1 in c1:
            for lit2 in c2:
                # 检查是否互补
                if (lit1.startswith('¬') and lit1[1:] == lit2) or \
                   (lit2.startswith('¬') and lit2[1:] == lit1):
                    # 归结
                    resolvent = (c1 - {lit1}) | (c2 - {lit2})
                    new_clauses.append(resolvent)
        return new_clauses
    
    def prove(self, goal):
        """尝试证明目标"""
        # 添加目标的否定
        neg_goal = f"¬{goal}" if not goal.startswith('¬') else goal[1:]
        self.add_clause([neg_goal])
        
        clauses = self.clauses[:]
        new = []
        
        while True:
            for i in range(len(clauses)):
                for j in range(i + 1, len(clauses)):
                    resolvents = self.resolve(clauses[i], clauses[j])
                    for r in resolvents:
                        if not r:  # 空子句
                            return True
                        if r not in clauses and r not in new:
                            new.append(r)
            
            if not new:
                return False
            
            clauses.extend(new)
            new = []

# 示例证明
prover = ResolutionProver()
prover.add_clause(['p', 'q'])       # p ∨ q
prover.add_clause(['¬p', 'r'])      # ¬p ∨ r
prover.add_clause(['¬q'])           # ¬q

result = prover.prove('r')
print(f"证明 r: {'成功' if result else '失败'}")
```

## 实现方式

### SAT求解器基础

```python
class DPLLSolver:
    """
    DPLL算法：经典的SAT求解算法
    基于回溯搜索和单元传播
    """
    
    def __init__(self):
        self.assignments = {}
    
    def dpll(self, clauses, variables):
        """DPLL算法主函数"""
        # 简化子句集
        clauses = self.simplify(clauses)
        
        # 检查是否可满足
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        
        # 单元传播
        unit = self.find_unit(clauses)
        while unit:
            var, val = unit
            self.assignments[var] = val
            clauses = self.propagate(clauses, var, val)
            
            if not clauses:
                return True
            if any(len(c) == 0 for c in clauses):
                return False
            
            unit = self.find_unit(clauses)
        
        # 选择变量进行分支
        var = self.select_variable(clauses, variables)
        
        # 尝试True和False
        return (self.dpll(clauses + [[(var, True)]], variables) or
                self.dpll(clauses + [[(var, False)]], variables))
    
    def simplify(self, clauses):
        """根据当前赋值简化子句"""
        result = []
        for clause in clauses:
            new_clause = []
            satisfied = False
            for var, val in clause:
                if var in self.assignments:
                    if self.assignments[var] == val:
                        satisfied = True
                        break
                else:
                    new_clause.append((var, val))
            if not satisfied:
                result.append(new_clause)
        return result
    
    def find_unit(self, clauses):
        """查找单元子句"""
        for clause in clauses:
            if len(clause) == 1:
                return clause[0]
        return None
    
    def propagate(self, clauses, var, val):
        """单元传播"""
        result = []
        for clause in clauses:
            new_clause = []
            skip = False
            for v, tv in clause:
                if v == var:
                    if tv == val:
                        skip = True  # 子句满足
                        break
                    # 否则该文字为假，跳过
                else:
                    new_clause.append((v, tv))
            if not skip:
                result.append(new_clause)
        return result
    
    def select_variable(self, clauses, variables):
        """选择分支变量（启发式）"""
        for clause in clauses:
            for var, _ in clause:
                if var not in self.assignments:
                    return var
        return None
```

## 示例

### 逻辑谜题求解

```python
def solve_logic_puzzle():
    """
    三扇门谜题：
    门1、2、3后分别有车、山羊、山羊
    每扇门上的陈述：
    - 门1："车在门1后"
    - 门2："车不在门2后"
    - 门3："车在门1后"
    已知只有一条陈述为真，求车在哪个门后？
    """
    
    for car_door in [1, 2, 3]:
        # 计算每个陈述的真值
        stmt1 = (car_door == 1)  # 门1说：车在门1
        stmt2 = (car_door != 2)  # 门2说：车不在门2
        stmt3 = (car_door == 1)  # 门3说：车在门1
        
        true_count = sum([stmt1, stmt2, stmt3])
        
        print(f"假设车在门{car_door}后:")
        print(f"  陈述1为真: {stmt1}")
        print(f"  陈述2为真: {stmt2}")
        print(f"  陈述3为真: {stmt3}")
        print(f"  真陈述数: {true_count}")
        
        if true_count == 1:
            print(f"  ✓ 符合条件！车在门{car_door}后\n")
        else:
            print(f"  ✗ 不符合条件\n")

solve_logic_puzzle()
```

### 电路设计验证

```python
class CircuitVerifier:
    """数字电路逻辑验证"""
    
    def __init__(self):
        self.gates = {}
    
    def add_and(self, name, input1, input2):
        self.gates[name] = ('AND', input1, input2)
    
    def add_or(self, name, input1, input2):
        self.gates[name] = ('OR', input1, input2)
    
    def add_not(self, name, input1):
        self.gates[name] = ('NOT', input1)
    
    def evaluate(self, inputs):
        """计算电路输出"""
        values = inputs.copy()
        
        for name, (gate, *args) in self.gates.items():
            if gate == 'AND':
                values[name] = values[args[0]] and values[args[1]]
            elif gate == 'OR':
                values[name] = values[args[0]] or values[args[1]]
            elif gate == 'NOT':
                values[name] = not values[args[0]]
        
        return values
    
    def verify_property(self, property_fn, num_inputs):
        """验证电路是否满足某性质（对所有输入）"""
        from itertools import product
        
        input_names = [f'i{i}' for i in range(num_inputs)]
        
        for values in product([True, False], repeat=num_inputs):
            inputs = dict(zip(input_names, values))
            result = self.evaluate(inputs)
            
            if not property_fn(inputs, result):
                print(f"反例: {inputs}")
                return False
        
        return True

# 验证半加器
circuit = CircuitVerifier()
circuit.add_and('carry', 'a', 'b')  # 进位 = a AND b
# 和 = a XOR b = (a AND NOT b) OR (NOT a AND b)
circuit.add_not('not_a', 'a')
circuit.add_not('not_b', 'b')
circuit.add_and('term1', 'a', 'not_b')
circuit.add_and('term2', 'not_a', 'b')
circuit.add_or('sum', 'term1', 'term2')

# 验证半加器的正确性
def check_half_adder(inputs, outputs):
    a, b = inputs['a'], inputs['b']
    expected_sum = a ^ b
    expected_carry = a and b
    return outputs['sum'] == expected_sum and outputs['carry'] == expected_carry

result = circuit.verify_property(check_half_adder, 2)
print(f"半加器验证: {'通过' if result else '失败'}")
```

## 应用场景

```
1. 编程语言类型系统
   - 类型推导和检查
   - 泛型约束求解
   - 模式匹配穷尽性检查

2. 硬件验证
   - 电路正确性验证
   - 形式化验证方法
   - 等价性检验

3. 人工智能
   - 知识表示与推理
   - 自动规划
   - 约束满足问题(CSP)

4. 数据库系统
   - SQL查询优化
   - 视图更新问题
   - 完整性约束检查

5. 软件工程
   - 程序规格说明
   - 形式化方法
   - 模型检测

6. 信息安全
   - 访问控制策略
   - 密码协议验证
   - 漏洞检测
```

## 面试要点

**Q1: 命题逻辑和谓词逻辑的主要区别？**
> 命题逻辑处理完整的命题（有确定的真值），不能分析命题内部结构；谓词逻辑引入谓词和量词，可以表达"所有"、"存在"等量化的陈述，能表示更复杂的逻辑关系。

**Q2: 为什么蕴含式 p→q 在p为假时总为真？**
> 这是实质蕴涵的定义，遵循"善意推定"原则：只有确实观察到p真而q假时，才能否定"p蕴含q"。在日常语言中，假前提的蕴含式被认为是空虚真（vacuously true）。

**Q3: 什么是SAT问题？为什么它是NP完全的？**
> SAT（可满足性）问题：给定一个命题公式，判断是否存在使其为真的赋值。Cook-Levin定理证明了SAT是NP完全的——所有NP问题都可以在多项式时间内归约到SAT。尽管最坏情况下指数复杂度，现代SAT求解器通过启发式和优化能高效处理实际问题。

**Q4: 归结原理为什么是正确的？**
> 归结基于反证法：假设结论的否定，如果与前提一起推出矛盾，则原结论成立。归结本身保持可满足性：如果两个子句可满足，其归结式也可满足；反之如果归结式不可满足，则至少一个父句不可满足。

**Q5: 一阶逻辑和命题逻辑的表达能力差异？**
> 一阶逻辑可以表达关于对象及其性质的陈述（如"所有人都是会死的"），而命题逻辑只能处理完整的命题。一阶逻辑是不可判定的（不存在通用算法判定任意公式的有效性），但命题逻辑是可判定的。

**Q6: 量词顺序的重要性？**
> ∀x∃y P(x,y) 和 ∃y∀x P(x,y) 含义不同。前者表示"对每个x都存在y"（y可依赖于x），后者表示"存在一个y对所有x都成立"（y是固定的）。例如：∀x∃y(x<y)为真，但∃y∀x(x<y)为假。

## 相关概念

### 数据结构
- [二叉树](../computer-science/data-structures/tree.md) - 决策树的逻辑结构
- [图](../computer-science/data-structures/graph.md) - Kripke语义模型

### 算法
- [回溯算法](../computer-science/algorithms/backtracking.md) - SAT求解的搜索策略
- [动态规划](../computer-science/algorithms/dynamic-programming.md) - 模型检测中的状态压缩
- [分支定界](../computer-science/algorithms/branch-and-bound.md) - 约束求解优化

### 复杂度分析
- [NP完全性](../references/np-completeness.md) - SAT问题的计算复杂度
- [时间复杂度](../references/time-complexity.md) - 逻辑推理的复杂度分析

### 系统实现
- [编译器原理](../computer-science/systems/compiler.md) - 类型系统和控制流分析
- [形式化验证](../security/formal-verification.md) - 程序正确性证明

### 相关数学
- [集合论](set-theory.md) - 逻辑与集合的对应关系
- [布尔代数](boolean-algebra.md) - 命题逻辑的代数结构
- [关系](relations.md) - 谓词逻辑的语义基础

---

1. "Logic in Computer Science" by Huth & Ryan
2. "Mathematical Logic for Computer Science" by Ben-Ari
3. "Handbook of Satisfiability" by Biere et al.
4. Stanford Encyclopedia of Philosophy: [Classical Logic](https://plato.stanford.edu/entries/logic-classical/)
