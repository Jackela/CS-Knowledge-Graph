# 缓存一致性 (Cache Coherence)

## 简介
缓存一致性是多核处理器中保证多个核心缓存数据一致性的机制，确保任何时刻各核心看到的数据符合程序顺序要求。

## 核心概念
- **一致性 (Coherence)**: 同一地址的读操作返回最新写入值
- **一致性域 (Coherence Domain)**: 参与一致性协议的缓存集合
- **写传播 (Write Propagation)**: 写入值传播到其他缓存
- **写串行化 (Write Serialization)**: 所有核心看到相同写入顺序

## 实现方式 / 工作原理

### MESI协议

```
MESI协议状态转换图

        ┌──────────┐
        │  INVALID │ ◄── 无效状态
        └────┬─────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐
│MODIFIED│ │EXCLUSIVE│ │SHARED │
└───┬────┘ └────┬────┘ └───┬────┘
    │           │          │
    │           │          │
    └───────────┴──────────┘
            │
            ▼
        ┌───────┐
        │OWNED  │ ◄── MOESI扩展
        └───────┘

状态定义：
- M (Modified): 已修改，独占，与内存不一致
- E (Exclusive): 独占，与内存一致
- S (Shared): 共享，只读，多缓存可能有
- I (Invalid): 无效
- O (Owned): 已修改，其他缓存可共享读取
```

```python
class MESICacheController:
    """MESI缓存控制器模拟"""
    
    def __init__(self, cache_id, bus):
        self.cache_id = cache_id
        self.cache = {}  # address -> CacheLine
        self.bus = bus
    
    def read(self, address):
        """本地读操作"""
        if address in self.cache:
            line = self.cache[address]
            if line.state in ['M', 'E', 'S']:
                return line.data  # 命中
        
        # 未命中或无效，需要总线事务
        return self.handle_read_miss(address)
    
    def handle_read_miss(self, address):
        """读未命中处理"""
        # 1. 发送BusRd请求
        responses = self.bus.broadcast('BusRd', address, self.cache_id)
        
        # 2. 检查其他缓存是否有该数据
        other_has_modified = False
        other_has_clean = False
        provider_data = None
        
        for resp in responses:
            if resp.state == 'M':
                other_has_modified = True
                provider_data = resp.data
                # 修改者降级为Shared
                resp.controller.downgrade_to_shared(address)
            elif resp.state in ['E', 'S']:
                other_has_clean = True
                provider_data = resp.data
        
        # 3. 确定新状态
        if other_has_modified or other_has_clean:
            new_state = 'S'  # 其他缓存有，变为Shared
        else:
            new_state = 'E'  # 只有我有，变为Exclusive
        
        # 4. 获取数据（从其他缓存或内存）
        data = provider_data if provider_data else self.read_memory(address)
        
        # 5. 填入缓存
        self.cache[address] = CacheLine(data, new_state)
        return data
    
    def write(self, address, data):
        """本地写操作"""
        if address in self.cache:
            line = self.cache[address]
            if line.state in ['M', 'E']:
                # 独占状态，直接写
                line.data = data
                line.state = 'M'
                return
            elif line.state == 'S':
                # 共享状态，需要升级为M
                self.handle_write_hit_shared(address, data)
                return
        
        # 未命中
        self.handle_write_miss(address, data)
    
    def handle_write_hit_shared(self, address, data):
        """写命中Shared状态"""
        # 发送BusUpgr使其他缓存失效
        self.bus.broadcast('BusUpgr', address, self.cache_id)
        
        # 升级为Modified
        self.cache[address].data = data
        self.cache[address].state = 'M'
    
    def handle_write_miss(self, address, data):
        """写未命中处理"""
        # 发送BusRdX请求（读并独占）
        responses = self.bus.broadcast('BusRdX', address, self.cache_id)
        
        # 使其他缓存失效
        for resp in responses:
            if resp.state in ['M', 'E', 'S']:
                resp.controller.invalidate(address)
        
        # 填入Modified状态
        self.cache[address] = CacheLine(data, 'M')
    
    def on_bus_request(self, request):
        """监听总线请求并响应"""
        address = request.address
        
        if address not in self.cache:
            return None  # 不涉及我
        
        line = self.cache[address]
        
        if request.type == 'BusRd':
            # 其他核读取
            if line.state == 'M':
                # 修改的数据需要写回
                self.writeback(address, line.data)
                line.state = 'S'
                return BusResponse('M', line.data, self)
            elif line.state == 'E':
                line.state = 'S'
                return BusResponse('E', line.data, self)
            elif line.state == 'S':
                return BusResponse('S', line.data, self)
        
        elif request.type in ['BusRdX', 'BusUpgr']:
            # 其他核要写，我失效
            if line.state == 'M':
                self.writeback(address, line.data)
            line.state = 'I'
        
        return None
```

### 伪共享与缓存行对齐

```python
import ctypes

class FalseSharingExample:
    """伪共享示例及解决方案"""
    
    def __init__(self):
        # 问题：counter1和counter2在同一缓存行
        # 两个核心分别修改时，会相互触发缓存失效
        self.counter1 = 0
        self.counter2 = 0
    
    # 解决方案1：填充使变量位于不同缓存行（通常64字节）
    class PaddedCounter:
        _padding_before = b'\x00' * 0
        value = 0
        _padding_after = b'\x00' * (64 - 8)  # 64字节对齐
    
    # 解决方案2：使用@cache_aligned装饰器（部分语言支持）
    # 解决方案3：使用原子操作合并更新

# Python中使用多进程避免GIL，但要注意共享内存对齐
from multiprocessing import shared_memory

def create_aligned_shared_array(size, dtype):
    """创建缓存行对齐的共享数组"""
    itemsize = ctypes.sizeof(ctypes.c_double)
    alignment = 64  # 缓存行大小
    
    # 分配额外空间用于对齐
    total_size = size * itemsize + alignment
    shm = shared_memory.SharedMemory(create=True, size=total_size)
    
    # 计算对齐后的起始地址
    offset = (alignment - shm.buf.ctypes.data % alignment) % alignment
    return shm, offset
```

### 内存一致性模型

| 模型 | 特点 | 代表 |
|------|------|------|
| 顺序一致性 | 所有操作按程序顺序执行 | 理论模型 |
| TSO (x86) | Store-Load可重排序 | x86/x64 |
| PSO | Store-Store可重排序 | SPARC |
| WMO (ARM) | 任意重排序，需显式屏障 | ARM/RISC-V |

```c
// 内存屏障示例（伪代码）
// TSO模型下：
Store A;    // 写A
Load B;     // 读B - 可能与上面重排序！

// 需要屏障保证顺序
Store A;
MFENCE;     // 全屏障
Load B;

// ARM弱内存模型需要更多屏障
Store A;
DMB SY;     // 数据内存屏障
Load B;
```

## 应用场景
- **多核处理器**: 核心间数据共享
- **分布式缓存**: Redis Cluster、Memcached节点间
- **GPU计算**: 线程块间数据一致
- **数据库**: 缓冲池多实例一致性

## 面试要点

1. **Q: MESI协议中各状态的含义？**  
   A: M(Modified): 独占且已修改，与内存不一致；E(Exclusive): 独占且与内存一致；S(Shared): 多缓存共享，只读；I(Invalid): 无效。状态转换由本地操作和总线监听事件触发，确保写传播和写串行化。

2. **Q: 什么是伪共享(False Sharing)？如何避免？**  
   A: 伪共享是两个无关变量在同一缓存行，被不同核心频繁修改导致缓存行在核心间来回"乒乓"的现象。避免：①缓存行填充（Padding），使热点变量独占缓存行；②按核心分配独立数据结构；③编译器/运行时对齐指令。

3. **Q: 强内存模型和弱内存模型的区别？**  
   A: 强内存模型（如x86-TSO）限制重排序，保证大多数操作按程序顺序执行，编程简单但性能受限；弱内存模型（如ARM）允许更多重排序，需显式内存屏障保证顺序，编程复杂但可挖掘更多并行性。现代编译器和原子库抽象了这些差异。

4. **Q: 目录协议(Directory)和嗅探协议(Snooping)的区别？**  
   A: 嗅探协议（MESI）通过广播总线监听，实现简单但扩展性差（总线带宽瓶颈）；目录协议维护共享数据的分布信息，点对点通信，可扩展性好但延迟更高、实现复杂。多核用嗅探，多处理器/NUMA用目录。

## 相关概念

### 数据结构
- [状态机](../data-structures/state-machine.md)
- [哈希表](../data-structures/hash-table.md)

### 算法
- [缓存替换算法](../algorithms/cache-replacement.md)
- [并发控制算法](../algorithms/concurrency-control.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [CPU架构](cpu-architecture.md)
- [内存层次](memory-hierarchy.md)
