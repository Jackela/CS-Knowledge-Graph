# 代码优化 (Code Optimization)

## 简介

**代码优化**是编译器的重要阶段，负责改进中间代码或目标代码的性能，同时保持程序的语义不变。优化可以在多个层次进行：源代码级、中间代码级、目标代码级。好的优化能显著提升程序执行效率、减少内存占用和降低功耗。

## 核心概念

| 概念 | 英文 | 说明 |
|------|------|------|
| **Data Flow Analysis** | 数据流分析 | 分析程序中数据的流动和变化 |
| **Constant Folding** | 常量折叠 | 在编译时计算常量表达式 |
| **Dead Code Elimination** | 死代码消除 | 删除不会执行的代码 |
| **Common Subexpression** | 公共子表达式 | 消除重复计算 |
| **Loop Optimization** | 循环优化 | 针对循环的专门优化 |
| **Inlining** | 内联 | 将函数调用替换为函数体 |
| **Register Allocation** | 寄存器分配 | 高效使用 CPU 寄存器 |

## 优化层次

```
┌─────────────────────────────────────────┐
│  High-Level Optimization                │
│  (Loop transformation, Inlining)        │
├─────────────────────────────────────────┤
│  Machine-Independent Optimization       │
│  (Constant propagation, CSE)            │
├─────────────────────────────────────────┤
│  Machine-Dependent Optimization         │
│  (Instruction selection, Scheduling)    │
├─────────────────────────────────────────┤
│  Peephole Optimization                  │
│  (Local code improvement)               │
└─────────────────────────────────────────┘
```

## 实现方式

### 1. 常量传播和常量折叠

```python
# constant_folding.py
from ast import *

class ConstantFolder(NodeTransformer):
    \"\"\"常量折叠优化器\"\"\"\n    \n    def visit_BinOp(self, node):\n        self.generic_visit(node)\n        \n        # 如果两个操作数都是常量，进行折叠\n        if isinstance(node.left, Constant) and isinstance(node.right, Constant):\n            if isinstance(node.op, Add):\n                return Constant(value=node.left.value + node.right.value)\n            elif isinstance(node.op, Sub):\n                return Constant(value=node.left.value - node.right.value)\n            elif isinstance(node.op, Mult):\n                return Constant(value=node.left.value * node.right.value)\n            elif isinstance(node.op, Div) and node.right.value != 0:\n                return Constant(value=node.left.value / node.right.value)\n        \n        return node\n    \n    def visit_UnaryOp(self, node):\n        self.generic_visit(node)\n        \n        if isinstance(node.operand, Constant):\n            if isinstance(node.op, USub):\n                return Constant(value=-node.operand.value)\n            elif isinstance(node.op, UAdd):\n                return Constant(value=+node.operand.value)\n        \n        return node\n
# 使用示例\ncode = '''\nx = 10 + 20 * 3\ny = -5 + 8\nz = x * 2\n'''\n\ntree = parse(code)\noptimizer = ConstantFolder()\noptimized = optimizer.visit(tree)\n\nprint(dump(optimized, indent=2))\n```

### 2. 死代码消除

```python
# dead_code_elimination.py
from typing import Set, Dict

class BasicBlock:\n    def __init__(self, name):\n        self.name = name\n        self.instructions = []\n        self.predecessors = []\n        self.successors = []\n        self.defs = set()  # 本块定义的变量\n        self.uses = set()  # 本块使用的变量\n    \n    def add_instruction(self, inst):\n        self.instructions.append(inst)\n\ndef dead_code_elimination(blocks: list) -> list:\n    \"\"\"死代码消除\"\"\"\n    \n    # 计算活跃变量\n    changed = True\n    while changed:\n        changed = False\n        for block in reversed(blocks):\n            old_live_out = block.live_out.copy() if hasattr(block, 'live_out') else set()\n            \n            # live_out = 所有后继的 live_in 的并集\n            block.live_out = set()\n            for succ in block.successors:\n                if hasattr(succ, 'live_in'):\n                    block.live_out |= succ.live_in\n            \n            # live_in = uses ∪ (live_out - defs)\n            block.live_in = block.uses | (block.live_out - block.defs)\n            \n            if block.live_out != old_live_out:\n                changed = True\n    \n    # 删除死代码\n    for block in blocks:\n        live = block.live_out.copy()\n        new_instructions = []\n        \n        for inst in reversed(block.instructions):\n            # 如果指令结果不被使用，且无副作用，则删除\n            if inst['dest'] and inst['dest'] not in live and not inst.get('side_effect'):\n                continue\n            \n            new_instructions.insert(0, inst)\n            \n            # 更新活跃集合\n            if inst['dest']:\n                live.discard(inst['dest'])\n            live.update(inst.get('uses', []))\n        \n        block.instructions = new_instructions\n    \n    return blocks\n
# 示例\ndef example():\n    blocks = [BasicBlock(f'B{i}') for i in range(3)]\n    \n    # B0: x = 10; y = 20; z = x + y; w = 5\n    blocks[0].instructions = [\n        {'dest': 'x', 'uses': [], 'side_effect': False},\n        {'dest': 'y', 'uses': [], 'side_effect': False},\n        {'dest': 'z', 'uses': ['x', 'y'], 'side_effect': False},\n        {'dest': 'w', 'uses': [], 'side_effect': False},  # 死代码\n    ]\n    blocks[0].defs = {'x', 'y', 'z', 'w'}\n    blocks[0].uses = {'x', 'y'}\n    blocks[0].successors = [blocks[1]]\n    \n    # B1: return z\n    blocks[1].instructions = [\n        {'dest': None, 'uses': ['z'], 'side_effect': True},\n    ]\n    blocks[1].uses = {'z'}\n    blocks[1].predecessors = [blocks[0]]\n    \n    optimized = dead_code_elimination(blocks)\n    print(f\"B0 instructions after DCE: {len(optimized[0].instructions)}\")\n```

### 3. 公共子表达式消除

```python
# common_subexpression_elimination.py
from typing import Dict, Tuple

class CSEOptimizer:\n    \"\"\"公共子表达式消除\"\"\"\n    \n    def __init__(self):\n        self.available_expressions: Dict[Tuple, str] = {}\n        self.temp_counter = 0\n    \n    def new_temp(self) -> str:\n        self.temp_counter += 1\n        return f't{self.temp_counter}'\n    \n    def optimize(self, instructions: list) -> list:\n        optimized = []\n        \n        for inst in instructions:\n            if inst['op'] in ['+', '-', '*', '/']:\n                # 创建表达式签名\n                expr = (inst['op'], inst['arg1'], inst['arg2'])\n                \n                if expr in self.available_expressions:\n                    # 发现公共子表达式\n                    temp = self.available_expressions[expr]\n                    optimized.append({\n                        'op': '=',\n                        'dest': inst['dest'],\n                        'arg1': temp\n                    })\n                else:\n                    # 新的表达式\n                    self.available_expressions[expr] = inst['dest']\n                    optimized.append(inst)\n            else:\n                # 非表达式指令，可能使表达式无效\n                if inst['op'] == '=':\n                    # 如果变量被重新赋值，移除包含该变量的表达式\n                    self._invalidate_expressions(inst['dest'])\n                optimized.append(inst)\n        \n        return optimized\n    \n    def _invalidate_expressions(self, var: str):\n        \"\"\"当变量被修改时，使包含该变量的表达式无效\"\"\"\n        to_remove = []\n        for expr, temp in self.available_expressions.items():\n            if var in expr[1:] or temp == var:\n                to_remove.append(expr)\n        \n        for expr in to_remove:\n            del self.available_expressions[expr]\n
# 示例\nif __name__ == '__main__':\n    instructions = [\n        {'op': '*', 'dest': 't1', 'arg1': 'a', 'arg2': 'b'},\n        {'op': '*', 'dest': 't2', 'arg1': 'a', 'arg2': 'b'},  # CSE!\n        {'op': '+', 'dest': 't3', 'arg1': 't1', 'arg2': 't2'},\n        {'op': '=', 'dest': 'a', 'arg1': '10'},  # 使表达式失效\n        {'op': '*', 'dest': 't4', 'arg1': 'a', 'arg2': 'b'},  # 新的表达式\n    ]\n    \n    optimizer = CSEOptimizer()\n    result = optimizer.optimize(instructions)\n    \n    for inst in result:\n        print(inst)\n```

### 4. 循环优化

```python
# loop_optimization.py

class LoopOptimizer:\n    \"\"\"循环优化器\"\"\"\n    \n    @staticmethod\n    def loop_invariant_code_motion(loop):\n        \"\"\"循环不变量外提\"\"\"\n        moved = []\n        remaining = []\n        \n        for inst in loop.body:\n            # 检查指令是否依赖循环变量\n            if not LoopOptimizer._depends_on_loop_vars(inst, loop.induction_vars):\n                moved.append(inst)\n            else:\n                remaining.append(inst)\n        \n        loop.preheader.extend(moved)\n        loop.body = remaining\n        \n        return loop\n    \n    @staticmethod\n    def strength_reduction(loop):\n        \"\"\"强度削弱 (如将乘法改为加法)\"\"\"\n        for inst in loop.body:\n            if inst['op'] == '*' and inst['arg2'] in loop.induction_vars:\n                # i * c → 使用归纳变量\n                if 'reduction_var' not in loop.__dict__:\n                    loop.reduction_var = f'{inst["arg2"]}_reduced'\n                    loop.preheader.append({\n                        'op': '=',\n                        'dest': loop.reduction_var,\n                        'arg1': '0'\n                    })\n                \n                # 替换乘法为加法\n                inst['op'] = '+'\n                inst['arg2'] = loop.reduction_var\n                \n                # 在循环尾部增加归纳变量\n                loop.latch.append({\n                    'op': '+',\n                    'dest': loop.reduction_var,\n                    'arg1': loop.reduction_var,\n                    'arg2': inst.get('multiplier', 'c')\n                })\n        \n        return loop\n    \n    @staticmethod\n    def _depends_on_loop_vars(inst, loop_vars):\n        \"\"\"检查指令是否依赖循环变量\"\"\"\n        for arg in [inst.get('arg1'), inst.get('arg2')]:\n            if arg in loop_vars:\n                return True\n        return False\n
# 示例\nclass Loop:\n    def __init__(self):\n        self.preheader = []\n        self.body = []\n        self.latch = []\n        self.induction_vars = {'i'}\n\nif __name__ == '__main__':\n    loop = Loop()\n    loop.body = [\n        {'op': '*', 'dest': 't1', 'arg1': 'i', 'arg2': '4'},\n        {'op': '*', 'dest': 't2', 'arg1': 'n', 'arg2': '5'},  # 循环不变量\n        {'op': '+', 'dest': 'sum', 'arg1': 'sum', 'arg2': 't2'},\n    ]\n    \n    optimizer = LoopOptimizer()\n    optimized = optimizer.loop_invariant_code_motion(loop)\n    \n    print(f\"Preheader: {optimized.preheader}\")\n    print(f\"Body: {optimized.body}\")\n```

## 应用场景

### 1. 编译器后端
- GCC、LLVM 的多级优化
- JIT 编译器的实时优化
- AOT 编译的预优化

### 2. 数据库查询优化
- SQL 查询重写
- 执行计划优化
- 索引选择

### 3. 移动和嵌入式开发
- 代码体积优化
- 功耗优化
- 实时性优化

## 面试要点

**Q: 编译器优化的基本原则是什么？**
A: 1) **正确性优先**：优化不能改变程序语义；2) **性价比**：优化开销要小于收益；3) **局部性**：大部分优化是局部的；4) **可预测性**：优化行为应可预期。

**Q: 常量传播和常量折叠的区别？**
A: **常量折叠**是在编译时计算常量表达式的值（如 `2 + 3` → `5`）。**常量传播**是将已知的常量值传播到使用该变量的地方（如 `x = 5; y = x + 1` → `y = 5 + 1`）。两者常结合使用。

**Q: 什么是 SSA 形式？为什么有助于优化？**
A: SSA（Static Single Assignment）要求每个变量只被赋值一次。优势：1) 简化了 def-use 链分析；2) 便于常量传播、死代码消除；3) 清晰的值流关系。φ 函数用于合并不同路径的值。

**Q: 循环优化的主要技术有哪些？**
A: 1) **循环不变量外提**：将不依赖循环变量的计算移到循环外；2) **强度削弱**：将乘法改为加法；3) **循环展开**：减少循环开销；4) **归纳变量优化**：简化循环变量计算。

**Q: 死代码消除如何判断代码是否"死亡"？**
A: 通过**活跃变量分析**：如果变量在定义后不被使用，且该定义没有副作用，则可以删除。需要数据流分析确定变量的活跃范围。

## 相关概念

### 数据结构
- [图](../data-structures/graph.md) - 控制流图
- [集合](../data-structures/set.md) - 数据流分析

### 算法
- [图遍历](../algorithms/graph-traversal.md) - 控制流分析
- [动态规划](../algorithms/dynamic-programming.md) - 指令选择

### 复杂度分析
- **常量折叠**: O(n)
- **死代码消除**: O(n²) - 需要迭代数据流分析
- **公共子表达式**: O(n)

### 系统实现
- [LLVM](https://llvm.org/) - 现代优化编译器
- [GCC](https://gcc.gnu.org/) - GNU 编译器优化
- [代码生成](./code-generation.md) - 相关阶段
