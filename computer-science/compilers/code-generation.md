# 代码生成 (Code Generation)

## 简介

**代码生成**是编译器的最后阶段，负责将经过语义分析的中间表示（AST 或 IR）转换为目标代码。目标代码可以是机器码、汇编代码或其他高级语言的代码。代码生成器需要处理寄存器分配、指令选择、内存布局等关键问题，直接影响生成代码的性能。

## 核心概念

| 概念 | 英文 | 说明 |
|------|------|------|
| **IR** | 中间表示 | 介于源代码和目标代码之间的表示形式 |
| **Three-Address Code** | 三地址码 | 每条指令最多三个操作数的中间表示 |
| **SSA** | 静态单赋值 | 每个变量只赋值一次的 IR 形式 |
| **Register Allocation** | 寄存器分配 | 将变量映射到有限的寄存器 |
| **Instruction Selection** | 指令选择 | 选择合适的机器指令 |
| **Peephole Optimization** | 窥孔优化 | 局部代码优化技术 |
| **Calling Convention** | 调用约定 | 函数调用的参数传递规则 |

## 实现方式

### 1. 三地址码生成

```python
# three_address_code.py
from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum, auto

class TACOp(Enum):
    # 算术运算
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    NEG = auto()
    # 比较
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    # 控制流
    GOTO = auto()
    IF_FALSE = auto()
    LABEL = auto()
    # 函数
    CALL = auto()
    RETURN = auto()
    PARAM = auto()
    # 内存
    ASSIGN = auto()
    LOAD = auto()
    STORE = auto()
    # 地址
    ADDR = auto()
    DEREF = auto()

@dataclass
class TACInstruction:
    op: TACOp
    result: Optional[str] = None
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    
    def __str__(self):\n        if self.op == TACOp.LABEL:\n            return f\"{self.result}:\"\n        elif self.op == TACOp.GOTO:\n            return f\"goto {self.result}\"\n        elif self.op == TACOp.IF_FALSE:\n            return f\"if_false {self.arg1} goto {self.result}\"\n        elif self.op == TACOp.ASSIGN:\n            return f\"{self.result} = {self.arg1}\"\n        elif self.op == TACOp.NEG:\n            return f\"{self.result} = -{self.arg1}\"\n        elif self.op in [TACOp.ADD, TACOp.SUB, TACOp.MUL, TACOp.DIV]:\n            op_str = {TACOp.ADD: '+', TACOp.SUB: '-', 
                     TACOp.MUL: '*', TACOp.DIV: '/'}[self.op]\n            return f\"{self.result} = {self.arg1} {op_str} {self.arg2}\"\n        elif self.op == TACOp.RETURN:\n            return f\"return {self.arg1}\"\n        elif self.op == TACOp.PARAM:\n            return f\"param {self.arg1}\"\n        elif self.op == TACOp.CALL:\n            return f\"{self.result} = call {self.arg1}, {self.arg2}\"\n        else:\n            return f\"{self.op} {self.result}, {self.arg1}, {self.arg2}\"\n
class TACGenerator:
    \"\"\"三地址码生成器\"\"\"\n    \n    def __init__(self):\n        self.instructions: List[TACInstruction] = []\n        self.temp_counter = 0\n        self.label_counter = 0\n    \n    def new_temp(self) -> str:\n        \"\"\"生成临时变量\"\"\"\n        self.temp_counter += 1\n        return f\"t{self.temp_counter}\"\n    \n    def new_label(self) -> str:\n        \"\"\"生成标签\"\"\"\n        self.label_counter += 1\n        return f\"L{self.label_counter}\"\n    \n    def emit(self, op: TACOp, result=None, arg1=None, arg2=None):\n        \"\"\"发射指令\"\"\"\n        self.instructions.append(TACInstruction(op, result, arg1, arg2))\n    \n    def generate_expression(self, node) -> str:\n        \"\"\"生成表达式代码\"\"\"\n        if isinstance(node, NumberNode):\n            return str(node.value)\n        \n        elif isinstance(node, VariableNode):\n            return node.name\n        \n        elif isinstance(node, BinaryOpNode):\n            left = self.generate_expression(node.left)\n            right = self.generate_expression(node.right)\n            result = self.new_temp()\n            \n            op_map = {\n                '+': TACOp.ADD,\n                '-': TACOp.SUB,\n                '*': TACOp.MUL,\n                '/': TACOp.DIV\n            }\n            self.emit(op_map[node.op], result, left, right)\n            return result\n        \n        elif isinstance(node, UnaryOpNode):\n            operand = self.generate_expression(node.operand)\n            result = self.new_temp()\n            self.emit(TACOp.NEG, result, operand)\n            return result\n    \n    def generate_statement(self, node):\n        \"\"\"生成语句代码\"\"\"\n        if isinstance(node, AssignmentNode):\n            value = self.generate_expression(node.value)\n            self.emit(TACOp.ASSIGN, node.name, value)\n        \n        elif isinstance(node, IfNode):\n            else_label = self.new_label()\n            end_label = self.new_label()\n            \n            # 计算条件\n            cond = self.generate_expression(node.condition)\n            self.emit(TACOp.IF_FALSE, else_label, cond)\n            \n            # then 分支\n            for stmt in node.then_body:\n                self.generate_statement(stmt)\n            self.emit(TACOp.GOTO, end_label)\n            \n            # else 分支\n            self.emit(TACOp.LABEL, else_label)\n            if node.else_body:\n                for stmt in node.else_body:\n                    self.generate_statement(stmt)\n            \n            self.emit(TACOp.LABEL, end_label)\n        \n        elif isinstance(node, WhileNode):\n            start_label = self.new_label()\n            end_label = self.new_label()\n            \n            self.emit(TACOp.LABEL, start_label)\n            cond = self.generate_expression(node.condition)\n            self.emit(TACOp.IF_FALSE, end_label, cond)\n            \n            for stmt in node.body:\n                self.generate_statement(stmt)\n            \n            self.emit(TACOp.GOTO, start_label)\n            self.emit(TACOp.LABEL, end_label)\n        \n        elif isinstance(node, ReturnNode):\n            value = self.generate_expression(node.value)\n            self.emit(TACOp.RETURN, arg1=value)\n    \n    def get_code(self) -> List[str]:\n        return [str(instr) for instr in self.instructions]\n\n# 示例节点定义\n@dataclass\nclass NumberNode:\n    value: float\n\n@dataclass\nclass VariableNode:\n    name: str\n\n@dataclass\nclass BinaryOpNode:\n    left: object\n    op: str\n    right: object\n\n@dataclass\nclass UnaryOpNode:\n    op: str\n    operand: object\n\n@dataclass\nclass AssignmentNode:\n    name: str\n    value: object\n\n@dataclass\nclass IfNode:\n    condition: object\n    then_body: List\n    else_body: Optional[List]\n\n@dataclass\nclass WhileNode:\n    condition: object\n    body: List\n\n@dataclass\nclass ReturnNode:\n    value: object\n\n# 使用示例\nif __name__ == '__main__':\n    gen = TACGenerator()\n    \n    # x = 10 + 20 * 3\n    expr = BinaryOpNode(\n        NumberNode(10),\n        '+',\n        BinaryOpNode(NumberNode(20), '*', NumberNode(3))\n    )\n    gen.generate_statement(AssignmentNode('x', expr))\n    \n    print(\"Generated TAC:\")\n    for line in gen.get_code():\n        print(f'  {line}')\n```

### 2. 简单汇编生成器

```python
# assembly_generator.py
from dataclasses import dataclass
from typing import List

class AssemblyGenerator:
    \"\"\"简单 x86-64 汇编生成器\"\"\"\n    \n    def __init__(self):\n        self.code = []\n        self.data_section = []\n        self.label_counter = 0\n    \n    def new_label(self, prefix=\"L\"):\n        self.label_counter += 1\n        return f\"{prefix}{self.label_counter}\"\n    \n    def emit(self, instruction, *args):\n        if args:\n            self.code.append(f\"  {instruction} {', '.join(args)}\")\n        else:\n            self.code.append(f\"  {instruction}\")\n    \n    def emit_label(self, label):\n        self.code.append(f\"{label}:\")\n    \n    def generate_prologue(self, locals_size=0):\n        \"\"\"函数序言\"\"\"\n        self.emit(\"push\", \"rbp\")\n        self.emit(\"mov\", \"rbp\", \"rsp\")\n        if locals_size > 0:\n            self.emit(\"sub\", \"rsp\", str(locals_size))\n    \n    def generate_epilogue(self):\n        \"\"\"函数结尾\"\"\"\n        self.emit(\"mov\", \"rsp\", \"rbp\")\n        self.emit(\"pop\", \"rbp\")\n        self.emit(\"ret\")\n    \n    def generate_expression(self, tac_instr):\n        \"\"\"从三地址码生成汇编\"\"\"\n        op = tac_instr.op\n        \n        if op.name in ['ADD', 'SUB', 'MUL', 'DIV']:\n            # 加载操作数\n            if tac_instr.arg1.isdigit():\n                self.emit(\"mov\", \"eax\", tac_instr.arg1)\n            else:\n                self.emit(\"mov\", \"eax\", f\"[{tac_instr.arg1}]\")\n            \n            # 执行运算\n            if tac_instr.arg2.isdigit():\n                operand = tac_instr.arg2\n            else:\n                operand = f\"[{tac_instr.arg2}]\"\n            \n            if op.name == 'ADD':\n                self.emit(\"add\", \"eax\", operand)\n            elif op.name == 'SUB':\n                self.emit(\"sub\", \"eax\", operand)\n            elif op.name == 'MUL':\n                self.emit(\"imul\", \"eax\", operand)\n            elif op.name == 'DIV':\n                self.emit(\"cdq\")  # 扩展符号位\n                if tac_instr.arg2.isdigit():\n                    self.emit(\"mov\", \"ecx\", operand)\n                    self.emit(\"idiv\", \"ecx\")\n                else:\n                    self.emit(\"idiv\", \"dword\" + operand)\n            \n            # 存储结果\n            self.emit(\"mov\", f\"[{tac_instr.result}]\", \"eax\")\n        \n        elif op.name == 'ASSIGN':\n            self.emit(\"mov\", \"eax\", tac_instr.arg1 if tac_instr.arg1.isdigit() else f\"[{tac_instr.arg1}]\")\n            self.emit(\"mov\", f\"[{tac_instr.result}]\", \"eax\")\n        \n        elif op.name == 'RETURN':\n            if tac_instr.arg1:\n                self.emit(\"mov\", \"eax\", tac_instr.arg1 if tac_instr.arg1.isdigit() else f\"[{tac_instr.arg1}]\")\n            self.generate_epilogue()\n        \n        elif op.name == 'LABEL':\n            self.emit_label(tac_instr.result)\n        \n        elif op.name == 'GOTO':\n            self.emit(\"jmp\", tac_instr.result)\n        \n        elif op.name == 'IF_FALSE':\n            self.emit(\"mov\", \"eax\", f\"[{tac_instr.arg1}]\")\n            self.emit(\"test\", \"eax\", \"eax\")\n            self.emit(\"jz\", tac_instr.result)\n    \n    def generate_function(self, name, tac_code, locals_size=0):\n        \"\"\"生成函数汇编代码\"\"\"\n        self.code.append(f\".global {name}\")\n        self.code.append(f\"{name}:\")\n        \n        self.generate_prologue(locals_size)\n        \n        for instr in tac_code:\n            self.generate_expression(instr)\n        \n        if not any(instr.op.name == 'RETURN' for instr in tac_code):\n            self.generate_epilogue()\n    \n    def add_data(self, name, value):\n        \"\"\"添加数据段\"\"\"\n        self.data_section.append(f\"{name}: .long {value}\")\n    \n    def get_assembly(self):\n        result = [\".section .data\"]\n        result.extend(self.data_section)\n        result.append(\".section .text\")\n        result.extend(self.code)\n        return '\\n'.join(result)\n\n# 使用示例\nif __name__ == '__main__':\n    from three_address_code import TACGenerator, TACOp, TACInstruction\n    \n    # 生成 TAC\n    tac_gen = TACGenerator()\n    tac_gen.emit(TACOp.ADD, 'result', 'a', 'b')\n    tac_gen.emit(TACOp.RETURN, arg1='result')\n    \n    # 生成汇编\n    asm_gen = AssemblyGenerator()\n    asm_gen.add_data('a', '10')\n    asm_gen.add_data('b', '20')\n    asm_gen.add_data('result', '0')\n    \n    asm_gen.generate_function('add_numbers', tac_gen.instructions)\n    \n    print(asm_gen.get_assembly())\n```

## 应用场景

### 1. 编译器后端
- 从 AST 生成目标代码
- 寄存器分配优化
- 指令选择
- 窥孔优化

### 2. JIT 编译器
- 运行时代码生成
- 热点代码优化
- 动态类型特化

### 3. 代码转换工具
- 源到源翻译
- 跨平台移植
- 代码混淆

### 4. 虚拟机
- 字节码生成
- 解释器实现
- 即时编译

## 面试要点

**Q: 什么是中间表示（IR）？为什么要使用 IR？**\nA: IR 是介于源代码和目标代码之间的表示形式。使用 IR 的好处：1) 分离前端和后端，支持多种源语言和目标平台；2) 便于实现与机器无关的优化；3) 简化代码生成过程。常见的 IR 有三地址码、SSA、LLVM IR 等。

**Q: 寄存器分配的基本方法有哪些？**\nA: 1) **图着色**：将寄存器分配建模为图着色问题，变量作为节点，冲突（同时活跃）作为边；2) **线性扫描**：按顺序分配寄存器，简单快速但质量较差；3) **优先级分配**：根据变量使用频率分配。现代编译器通常使用改进的图着色算法。

**Q: 三地址码的特点是什么？**\nA: 三地址码每条指令最多有三个地址（一个结果，两个操作数），形式为 `x = y op z`。特点：1) 类似汇编但独立于具体机器；2) 便于优化；3) 易于转换为目标代码；4) 可以表示控制流（跳转、条件分支）。

**Q: 什么是窥孔优化？**\nA: 窥孔优化是在代码的局部窗口（窥孔）上进行的优化，扫描生成的代码，寻找可以改进的模式。常见优化：1) 冗余指令消除；2) 常量折叠；3) 代数化简；4) 死代码消除；5) 控制流优化。

**Q: SSA（静态单赋值）形式的优势？**\nA: SSA 要求每个变量只被赋值一次。优势：1) 简化数据流分析；2) 便于实现某些优化（如常量传播、死代码消除）；3) 清晰的 def-use 链；4) 现代编译器（LLVM、GCC）广泛使用。

## 相关概念

### 数据结构
- [图](../data-structures/graph.md) - 寄存器分配\n- [栈](../data-structures/stack.md) - 调用约定\n- [哈希表](../data-structures/hash-table.md) - 符号映射

### 算法
- [图着色](../algorithms/graph-coloring.md) - 寄存器分配\n- [活跃变量分析](../algorithms/data-flow-analysis.md) - 优化基础
- [动态规划](../algorithms/dynamic-programming.md) - 指令选择

### 复杂度分析
- **寄存器分配**: NP-完全（图着色）\n- **指令选择**: O(n) - 模式匹配\n- **窥孔优化**: O(n) - 线性扫描

### 系统实现\n- [语义分析](./semantic-analysis.md) - 前一阶段\n- [LLVM](https://llvm.org/) - 现代编译器基础设施\n- [GCC](https://gcc.gnu.org/) - GNU 编译器集合\n