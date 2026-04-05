# CPU架构 (CPU Architecture)

## 简介
CPU架构是计算机的核心设计，定义了指令集、寄存器组织、执行单元等硬件结构，决定了计算机的运算能力和能效表现。

## 核心概念
- **指令集架构 (ISA)**: 软件与硬件的接口，如x86、ARM、RISC-V
- **微架构**: ISA的具体实现方式
- **流水线 (Pipeline)**: 指令并行执行技术
- **乱序执行 (OoOE)**: 动态调度指令提高利用率

## 实现方式 / 工作原理

### CPU核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                      CPU Core                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Fetch     │───►│   Decode    │───►│   Execute   │     │
│  │   (取指)     │    │   (译码)     │    │   (执行)     │     │
│  └─────────────┘    └─────────────┘    └──────┬──────┘     │
│       ▲                                        │            │
│       │         ┌──────────────────────────────┘            │
│       │         │                                           │
│  ┌────┴─────────┴────┐    ┌─────────────────────────────┐  │
│  │   Branch Predictor │    │      Execution Units        │  │
│  │   (分支预测)        │    │  ┌─────────┐ ┌─────────┐   │  │
│  └────────────────────┘    │  │  ALU    │ │  FPU    │   │  │
│                            │  │ (整数)   │ │ (浮点)   │   │  │
│  ┌────────────────────┐    │  └─────────┘ └─────────┘   │  │
│  │   Register File    │    │  ┌─────────┐ ┌─────────┐   │  │
│  │   (寄存器堆)        │◄───┼──┤  Load   │ │  Store  │   │  │
│  │  R0-R31, PC, SP    │    │  │ (加载)   │ │ (存储)   │   │  │
│  └────────────────────┘    │  └─────────┘ └─────────┘   │  │
│                            └─────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Cache Hierarchy                    │  │
│  │  ┌─────────┐   ┌─────────┐   ┌────────────────────┐  │  │
│  │  │  L1-I$  │   │  L1-D$  │   │        L2$         │  │  │
│  │  │32-64KB  │   │32-64KB  │   │    256KB-1MB       │  │  │
│  │  └─────────┘   └─────────┘   └────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 指令执行周期

```python
class CPUCore:
    """CPU核心模拟"""
    
    def __init__(self):
        self.pc = 0           # 程序计数器
        self.registers = [0] * 32  # 通用寄存器
        self.pipeline = Pipeline(depth=5)
    
    def fetch(self):
        """取指阶段 (IF)"""
        # 从L1指令缓存取指令
        instruction = self.l1_icache.read(self.pc)
        # PC更新（考虑分支预测）
        predicted_pc = self.branch_predictor.predict(self.pc)
        self.pc = predicted_pc
        return instruction
    
    def decode(self, instruction):
        """译码阶段 (ID)"""
        # 解析操作码和操作数
        opcode = (instruction >> 26) & 0x3F
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        rd = (instruction >> 11) & 0x1F
        imm = instruction & 0xFFFF
        
        # 读取寄存器值
        reg_val1 = self.registers[rs]
        reg_val2 = self.registers[rt]
        
        return DecodedInst(opcode, rd, reg_val1, reg_val2, imm)
    
    def execute(self, decoded):
        """执行阶段 (EX)"""
        alu = ALU()
        
        if decoded.opcode == "ADD":
            result = alu.add(decoded.val1, decoded.val2)
        elif decoded.opcode == "SUB":
            result = alu.sub(decoded.val1, decoded.val2)
        elif decoded.opcode == "MUL":
            result = alu.mul(decoded.val1, decoded.val2)  # 多周期
        elif decoded.opcode == "LOAD":
            address = alu.add(decoded.val1, decoded.imm)
            return MemoryOp("LOAD", address, decoded.rd)
        
        return ExecutionResult(decoded.rd, result)
    
    def memory_access(self, mem_op):
        """访存阶段 (MEM)"""
        if mem_op.type == "LOAD":
            # 检查L1数据缓存
            data = self.l1_dcache.read(mem_op.address)
            return MemoryResult(mem_op.rd, data)
        elif mem_op.type == "STORE":
            self.l1_dcache.write(mem_op.address, mem_op.data)
            return None
    
    def writeback(self, result):
        """写回阶段 (WB)"""
        if result and result.rd != 0:  # R0通常是零寄存器
            self.registers[result.rd] = result.value
```

### 超标量与乱序执行

```python
class SuperscalarCore:
    """超标量乱序执行核心"""
    
    def __init__(self, issue_width=4):
        self.issue_width = issue_width  # 每周期发射指令数
        self.reservation_station = []   # 保留站
        self.reorder_buffer = ROB(size=128)  # 重排序缓冲区
        self.reg_rename_table = {}      # 寄存器重命名表
    
    def dispatch(self, instructions):
        """指令分发到保留站"""
        for inst in instructions[:self.issue_width]:
            # 寄存器重命名解决WAR/WAW冲突
            renamed_inst = self.rename_registers(inst)
            
            # 加入保留站等待操作数就绪
            entry = ReservationEntry(
                op=renamed_inst.opcode,
                dest=renamed_inst.rd,
                src1=renamed_inst.rs,
                src2=renamed_inst.rt,
                rob_entry=self.reorder_buffer.allocate()
            )
            self.reservation_station.append(entry)
    
    def issue(self):
        """发射就绪指令"""
        ready_instructions = [
            e for e in self.reservation_station
            if self.operand_ready(e.src1) and self.operand_ready(e.src2)
        ]
        
        for entry in ready_instructions[:self.issue_width]:
            # 发射到功能单元执行
            fu = self.get_functional_unit(entry.op)
            fu.execute(entry)
            self.reservation_station.remove(entry)
    
    def complete(self):
        """执行完成并写回"""
        for fu in self.functional_units:
            if fu.completed():
                result = fu.get_result()
                # 写回重排序缓冲区，不按程序顺序
                self.reorder_buffer.write(result.rob_entry, result)
                # 广播到保留站
                self.broadcast_result(result)
    
    def commit(self):
        """按程序顺序提交"""
        while self.reorder_buffer.head_ready():
            entry = self.reorder_buffer.pop_head()
            # 真正更新架构状态
            self.arch_registers[entry.dest] = entry.value
```

## 应用场景
- **数据中心**: x86服务器，高主频、大缓存处理复杂负载
- **移动设备**: ARM架构，高能效比延长续航
- **嵌入式**: RISC-V，模块化可定制
- **AI加速**: GPU/TPU，并行处理张量运算

## 面试要点

1. **Q: CISC和RISC的区别？**  
   A: CISC（如x86）指令复杂、变长，微码实现，目标是最小化程序大小；RISC（如ARM）指令简单、定长，硬件直接执行，目标是单周期执行。现代CPU融合两者：x86内部译码为RISC-like微操作，ARM也有复杂指令扩展。

2. **Q: 分支预测为什么重要？如何实现？**  
   A: 流水线越深，分支预测失败的代价越大（清空流水线）。实现方式：①静态预测（总是/从不跳转）；②动态预测：1位/2位饱和计数器、分支目标缓冲区(BTB)、返回地址栈(RAS)；③高级：TAGE、神经网络预测器。现代CPU预测准确率>95%。

3. **Q: 缓存失效的三种类型？**  
   A: ①强制性失效（Compulsory）：首次访问必然失效，预取可缓解；②容量失效（Capacity）：缓存不够大容纳工作集；③冲突失效（Conflict）：组相联映射导致不同块映射到同一组，全相联可避免。

4. **Q: 超标量和超线程的区别？**  
   A: 超标量：单核心每周期发射多条指令，需要多套执行单元；超线程（SMT）：单核心模拟多个逻辑核心，共享执行单元但分离寄存器和PC，利用指令级并行填充流水线气泡，提高资源利用率。

## 相关概念

### 数据结构
- [队列](../data-structures/queue.md)
- [栈](../data-structures/stack.md)

### 算法
- [分支预测算法](../algorithms/branch-prediction.md)
- [流水线调度](../algorithms/pipeline-scheduling.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [指令流水线](pipelining.md)
- [内存层次](memory-hierarchy.md)
