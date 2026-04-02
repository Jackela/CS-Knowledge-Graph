# 指令流水线 (Pipelining)

## 简介
指令流水线是将指令执行分解为多个阶段，使多条指令重叠执行的技术，可显著提高指令吞吐率而不减少单条指令延迟。

## 核心概念
- **流水线阶段 (Stage)**: 指令执行的一个步骤
- **吞吐率 (Throughput)**: 单位时间完成的指令数
- **流水线冒险 (Hazard)**: 阻止流水线连续执行的情况
- **气泡 (Bubble)**: 流水线中的停顿周期

## 实现方式 / 工作原理

### 经典5级流水线

```
时钟周期 ─►  1     2     3     4     5     6     7     8     9
           │     │     │     │     │     │     │     │     │
Instr1:    IF   ID    EX    MEM   WB
                │     │     │     │
Instr2:          IF   ID    EX    MEM   WB
                      │     │     │     │
Instr3:                IF   ID    EX    MEM   WB
                            │     │     │     │
Instr4:                      IF   ID    EX    MEM   WB
                                  │     │     │     │
Instr5:                            IF   ID    EX    MEM   WB

IF: Instruction Fetch  (取指)
ID: Instruction Decode (译码)
EX: Execute            (执行)
MEM: Memory Access     (访存)
WB: Write Back         (写回)

理想CPI = 1 (每周期完成一条指令)
```

```python
class PipelineCPU:
    """5级流水线CPU模拟"""
    
    def __init__(self):
        self.pipeline_stages = {
            'IF': PipelineRegister(),
            'ID': PipelineRegister(),
            'EX': PipelineRegister(),
            'MEM': PipelineRegister(),
            'WB': PipelineRegister()
        }
        self.pc = 0
        self.registers = [0] * 32
        self.memory = {}
        self.cycle = 0
        self.instructions_completed = 0
    
    def cycle(self):
        """执行一个时钟周期（反向推进避免数据竞争）"""
        self.cycle += 1
        
        # WB阶段（最后阶段先执行）
        if self.pipeline_stages['MEM'].valid:
            self.stage_wb(self.pipeline_stages['MEM'])
            self.pipeline_stages['MEM'].valid = False
        
        # MEM阶段
        if self.pipeline_stages['EX'].valid:
            result = self.stage_mem(self.pipeline_stages['EX'])
            self.pipeline_stages['MEM'].load(result)
            self.pipeline_stages['EX'].valid = False
        
        # EX阶段
        if self.pipeline_stages['ID'].valid:
            result = self.stage_ex(self.pipeline_stages['ID'])
            self.pipeline_stages['EX'].load(result)
            self.pipeline_stages['ID'].valid = False
        
        # ID阶段
        if self.pipeline_stages['IF'].valid:
            result = self.stage_id(self.pipeline_stages['IF'])
            self.pipeline_stages['ID'].load(result)
            self.pipeline_stages['IF'].valid = False
        
        # IF阶段
        instruction = self.fetch_instruction(self.pc)
        self.pipeline_stages['IF'].load({
            'pc': self.pc,
            'instruction': instruction
        })
        self.pc += 4  # 默认PC+4，分支会修正
    
    def stage_ex(self, decoded):
        """执行阶段"""
        opcode = decoded['opcode']
        
        if opcode == 'ADD':
            result = decoded['val1'] + decoded['val2']
        elif opcode == 'SUB':
            result = decoded['val1'] - decoded['val2']
        elif opcode == 'LOAD':
            result = {
                'type': 'LOAD',
                'address': decoded['val1'] + decoded['imm'],
                'dest': decoded['dest']
            }
        elif opcode == 'BRANCH':
            # 分支在EX阶段计算目标地址
            taken = self.evaluate_condition(decoded['condition'])
            if taken != decoded['predicted']:
                # 分支预测错误！清空流水线
                self.flush_pipeline()
                self.pc = decoded['target'] if taken else decoded['pc'] + 4
            return {'type': 'NOP'}
        
        return {'type': 'ALU', 'dest': decoded['dest'], 'value': result}
```

### 流水线冒险处理

```python
class HazardUnit:
    """冒险检测与处理单元"""
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
    
    def detect_data_hazard(self, current_inst):
        """检测数据冒险"""
        hazards = []
        
        # 检查RAW (Read After Write)
        current_sources = current_inst.get_source_registers()
        
        for stage_name, stage_reg in [
            ('EX', self.pipeline.stages['EX']),
            ('MEM', self.pipeline.stages['MEM'])
        ]:
            if not stage_reg.valid:
                continue
            
            dest = stage_reg.get_destination_register()
            if dest in current_sources:
                hazards.append({
                    'type': 'RAW',
                    'source': stage_name,
                    'register': dest
                })
        
        return hazards
    
    def resolve_data_hazard(self, hazards):
        """解决数据冒险"""
        for hazard in hazards:
            if hazard['type'] == 'RAW':
                # 方案1: 停顿（插入气泡）
                # self.pipeline.insert_bubble('ID')
                
                # 方案2: 数据前递（Forwarding/Bypassing）
                if hazard['source'] == 'EX':
                    # EX/MEM阶段结果前递到EX输入
                    forward_value = self.pipeline.get_ex_result()
                    self.pipeline.set_forwarding_mux('ALU', forward_value)
                elif hazard['source'] == 'MEM':
                    # MEM/WB阶段结果前递
                    forward_value = self.pipeline.get_mem_result()
                    self.pipeline.set_forwarding_mux('ALU', forward_value)
    
    def detect_control_hazard(self, instruction):
        """控制冒险：分支指令"""
        return instruction.is_branch()
    
    def resolve_control_hazard(self, branch_inst):
        """分支预测减少控制冒险影响"""
        prediction = self.branch_predictor.predict(branch_inst.pc)
        
        if prediction == 'TAKEN':
            # 预测跳转，提前取目标地址
            self.pipeline.set_next_pc(branch_inst.target)
        else:
            # 预测不跳转，顺序取指
            self.pipeline.set_next_pc(branch_inst.pc + 4)
        
        # 标记为推测执行
        self.pipeline.set_speculative(True)
```

### 超标量流水线

```python
class SuperscalarPipeline:
    """双发射超标量流水线"""
    
    def __init__(self, width=2):
        self.width = width  # 每周期发射指令数
        self.fetch_queue = []
        self.dispatch_queue = []
    
    def fetch_stage(self):
        """取指阶段：每周期取多条指令"""
        for _ in range(self.width):
            inst = self.icache.read(self.pc)
            self.fetch_queue.append(FetchedInst(inst, self.pc))
            self.pc += 4
    
    def decode_dispatch(self):
        """译码分发：动态调度"""
        ready_instructions = []
        
        for inst in self.fetch_queue[:self.width]:
            decoded = self.decode(inst)
            
            # 检查功能单元可用性和操作数就绪
            if (self.functional_unit_available(decoded.fu_type) and
                self.operands_ready(decoded)):
                ready_instructions.append(decoded)
        
        # 发射就绪指令
        for inst in ready_instructions[:self.width]:
            fu = self.allocate_functional_unit(inst.fu_type)
            fu.accept(inst)
            self.fetch_queue.remove(inst.source)
    
    def execute_out_of_order(self):
        """乱序执行"""
        # 保留站中操作数就绪的指令可以乱序执行
        for rs in self.reservation_stations:
            if rs.is_ready() and not rs.executing:
                fu = self.get_free_functional_unit(rs.fu_type)
                if fu:
                    rs.start_execution(fu)
        
        # 每周期推进执行
        for fu in self.functional_units:
            if fu.busy:
                fu.tick()
                if fu.completed():
                    result = fu.get_result()
                    # 写回重排序缓冲区
                    self.rob.write_result(result)
```

## 应用场景
- **现代CPU**: Intel、AMD、ARM处理器的核心设计
- **GPU**: 数千个简单流水线并行执行
- **网络处理器**: 包处理流水线
- **AI加速器**: 矩阵运算流水线

## 面试要点

1. **Q: 流水线CPI和加速比如何计算？**  
   A: 理想CPI = 1。实际CPI = 1 + 停顿周期/指令数。k级流水线处理n条指令时间 = (k + n - 1) * 周期。加速比 ≈ k（当n很大时）。流水线深度受限于：①阶段均衡性；②冒险处理开销；③功耗（ deeper pipeline = 更多寄存器 + 更高频率功耗）。

2. **Q: 数据冒险有哪些类型？如何解决？**  
   A: RAW（写后读）：最常见，可用停顿或前递解决；WAR（读后写）：乱序执行时出现，用寄存器重命名解决；WAW（写后写）：同样用重命名解决。前递（Forwarding）将ALU结果直接送到下条指令输入，避免停顿。

3. **Q: 分支预测失败的代价有多大？如何降低？**  
   A: k级流水线中，分支在EX阶段确定，预测失败需清空2条指令(IF,ID)，代价2周期。现代深度流水线（20级+）代价更大。降低方法：①更早计算分支（ID阶段）；②静态/动态分支预测（BHT、BTB）；③延迟槽；④谓词执行。

4. **Q: 超流水线和超标量的区别？**  
   A: 超流水线（Superpipelining）：增加流水线深度，减少每周期工作时间，提高时钟频率；超标量（Superscalar）：增加流水线宽度，每周期发射多条指令，需要多套执行单元。两者可结合使用，现代CPU通常是超流水线+超标量+乱序执行。

## 相关概念

### 数据结构
- [队列](../data-structures/queue.md)
- [栈](../data-structures/stack.md)

### 算法
- [分支预测算法](../algorithms/branch-prediction.md)
- [指令调度算法](../algorithms/instruction-scheduling.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [CPU架构](cpu-architecture.md)
- [缓存一致性](cache-coherence.md)
