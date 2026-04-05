# 内存层次 (Memory Hierarchy)

## 简介
内存层次是计算机系统中从寄存器到磁盘的多级存储结构，利用局部性原理平衡速度、容量和成本，隐藏不同存储介质的速度差异。

## 核心概念
- **时间局部性**: 最近访问的数据很可能再次被访问
- **空间局部性**: 相邻数据很可能被连续访问
- **命中 (Hit)**: 数据在目标层级找到
- **缺失 (Miss)**: 数据不在目标层级，需从下层获取

## 实现方式 / 工作原理

### 内存层次金字塔

```
         ┌─────────┐
         │Register │ ◄── 最快，1周期，~1KB
         └────┬────┘
              │  1ns
         ┌────┴────┐
         │   L1$   │ ◄── 4周期，32-64KB
         └────┬────┘
              │  2ns
         ┌────┴────┐
         │   L2$   │ ◄── 10周期，256KB-1MB
         └────┬────┘
              │  5ns
         ┌────┴────┐
         │   L3$   │ ◄── 40周期，8-64MB
         └────┬────┘
              │  20ns
         ┌────┴────┐
         │  Main   │ ◄── 100ns，16-512GB
         │  Memory │
         └────┬────┘
              │  10μs
         ┌────┴────┐
         │   SSD   │ ◄── 100μs，TB级
         └────┬────┘
              │  1ms
         ┌────┴────┐
         │   HDD   │ ◄── 10ms，TB级
         └─────────┘
         
速度递减 ─────────────────────────►
容量递增 ─────────────────────────►
成本递减 ─────────────────────────►
```

### 缓存地址映射

```python
class CacheSimulator:
    """缓存模拟器 - 展示三种映射方式"""
    
    def __init__(self, cache_size, block_size, associativity):
        """
        cache_size: 缓存总大小
        block_size: 缓存块大小
        associativity: 相联度 (1=直接映射, n=n路组相联, all=全相联)
        """
        self.block_size = block_size
        self.num_blocks = cache_size // block_size
        self.associativity = associativity
        self.num_sets = self.num_blocks // associativity
        
        # 地址划分
        self.offset_bits = (block_size - 1).bit_length()
        self.index_bits = (self.num_sets - 1).bit_length()
        self.tag_bits = 64 - self.offset_bits - self.index_bits
    
    def parse_address(self, address):
        """解析地址为tag、index、offset"""
        offset = address & ((1 << self.offset_bits) - 1)
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = address >> (self.offset_bits + self.index_bits)
        return tag, index, offset
    
    def direct_mapped_access(self, address):
        """直接映射：每个内存块只能放到固定缓存位置"""
        tag, index, offset = self.parse_address(address)
        
        cache_line = self.cache[index]
        if cache_line.valid and cache_line.tag == tag:
            return "HIT"  # 命中
        else:
            # 未命中，替换（只有一个选择）
            cache_line.tag = tag
            cache_line.valid = True
            return "MISS"
    
    def set_associative_access(self, address):
        """组相联：每个内存块可放到组内任意位置"""
        tag, index, offset = self.parse_address(address)
        
        cache_set = self.cache[index]  # 一组有n个cache line
        for line in cache_set:
            if line.valid and line.tag == tag:
                line.lru_counter = 0  # 更新LRU
                return "HIT"
        
        # 未命中，LRU替换
        victim = max(cache_set, key=lambda x: x.lru_counter)
        victim.tag = tag
        victim.valid = True
        victim.lru_counter = 0
        return "MISS"
    
    def fully_associative_access(self, address):
        """全相联：内存块可放到缓存任意位置"""
        tag = address >> self.offset_bits
        
        for line in self.cache:
            if line.valid and line.tag == tag:
                return "HIT"
        
        # 未命中，全局LRU替换
        victim = self.find_global_lru()
        victim.tag = tag
        victim.valid = True
        return "MISS"
```

### TLB与虚拟内存

```python
class VirtualMemorySystem:
    """虚拟内存系统模拟"""
    
    def __init__(self):
        self.page_size = 4096  # 4KB页
        self.tlb = TLB(entries=64)  # 快表
        self.page_table = {}  # 页表
        self.physical_memory = PhysicalMemory(size=8*1024*1024*1024)  # 8GB
    
    def translate_address(self, virtual_addr):
        """虚拟地址转物理地址"""
        vpn = virtual_addr // self.page_size  # 虚拟页号
        offset = virtual_addr % self.page_size  # 页内偏移
        
        # 1. 查TLB
        ppn = self.tlb.lookup(vpn)
        if ppn is not None:
            # TLB命中
            return ppn * self.page_size + offset
        
        # 2. TLB未命中，查页表
        if vpn in self.page_table:
            entry = self.page_table[vpn]
            if entry.valid:
                ppn = entry.physical_page
                # 回填TLB
                self.tlb.insert(vpn, ppn)
                return ppn * self.page_size + offset
            else:
                # 页在磁盘，触发缺页异常
                raise PageFault(vpn)
        else:
            # 未分配，段错误
            raise SegmentationFault()
    
    def handle_page_fault(self, vpn):
        """缺页异常处理"""
        # 1. 找空闲物理页或页面置换
        ppn = self.physical_memory.allocate_page()
        if ppn is None:
            ppn = self.page_replacement()
        
        # 2. 从磁盘加载页面
        self.disk.read_page(vpn, self.physical_memory.get_address(ppn))
        
        # 3. 更新页表
        self.page_table[vpn] = PageTableEntry(ppn=ppn, valid=True)
        
        # 4. 回填TLB
        self.tlb.insert(vpn, ppn)
    
    def page_replacement(self):
        """页面置换算法"""
        # LRU实现
        victim = min(self.page_table.items(), 
                    key=lambda x: x[1].last_access_time)
        victim_vpn = victim[0]
        victim_ppn = victim[1].physical_page
        
        # 如果脏页，写回磁盘
        if victim[1].dirty:
            self.disk.write_page(victim_vpn, 
                               self.physical_memory.get_address(victim_ppn))
        
        # 标记原页表项为无效
        self.page_table[victim_vpn].valid = False
        
        return victim_ppn
```

## 应用场景
- **数据库缓存**: 缓冲池管理，减少磁盘I/O
- **Web缓存**: CDN边缘节点缓存静态资源
- **操作系统**: 页面缓存、文件系统缓存
- **GPU显存**: 纹理缓存、共享内存层次

## 面试要点

1. **Q: 为什么需要内存层次结构？**  
   A: 因为速度快的存储器成本高、容量小，速度慢的成本低、容量大。通过层次结构，将最常访问的数据放在最快的存储器，利用局部性原理，使得平均访问时间接近最快层级，而平均成本接近最慢层级。

2. **Q: 缓存命中率如何计算？如何提升？**  
   A: 命中率 = 命中次数 / 总访问次数。提升方法：①增大缓存容量（成本和功耗增加）；②提高相联度（减少冲突失效）；③优化替换算法（LRU、LFU）；④增大块大小（利用空间局部性，但会增加失效惩罚）；⑤预取技术（硬件/软件预取）。

3. **Q: 写直达(Write-through)和写回(Write-back)的区别？**  
   A: 写直达同时写缓存和内存，实现简单但写速度慢；写回只写缓存，替换时才写回内存，速度快但数据不一致风险高。现代CPU缓存多用写回，配合MESI协议保证一致性。

4. **Q: 虚拟内存的作用是什么？页表过大如何解决？**  
   A: 虚拟内存作用：①隔离进程地址空间；②使用比物理内存更大的地址空间；③简化内存管理（统一抽象）。页表过大解决：①多级页表（按需分配）；②倒排页表（物理页为索引）；③大页（减少页表项）；④TLB缓存最近翻译。

## 相关概念

### 数据结构
- [哈希表](../data-structures/hash-table.md)
- [链表](../data-structures/linked-list.md)

### 算法
- [页面置换算法](../algorithms/page-replacement.md)
- [LRU缓存](../algorithms/lru-cache.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [CPU架构](cpu-architecture.md)
- [缓存一致性](cache-coherence.md)
