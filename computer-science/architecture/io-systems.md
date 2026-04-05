# IO系统 (I/O Systems)

## 简介
I/O系统是计算机与外部设备交互的桥梁，涵盖设备控制器、驱动程序、中断机制等，直接影响系统的响应速度和吞吐量。

## 核心概念
- **中断 (Interrupt)**: 设备通知CPU事件完成的机制
- **DMA**: 直接内存访问，无需CPU介入传输数据
- **设备驱动**: 操作系统控制硬件的软件接口
- **缓冲 (Buffering)**: 缓解速度不匹配的数据暂存区

## 实现方式 / 工作原理

### I/O系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      User Space                             │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Application    │  │  System Calls   │                   │
│  │  (read/write)   │  │  (read/write)   │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
└───────────┼────────────────────┼────────────────────────────┘
            │                    │
┌───────────┼────────────────────┼────────────────────────────┐
│           │     Kernel Space   │                            │
│           │    ┌───────────────┴──────────┐                 │
│           │    │    VFS (Virtual FS)      │                 │
│           │    │  (统一文件抽象接口)        │                 │
│           │    └─────────────┬────────────┘                 │
│           │                  │                               │
│           │    ┌─────────────┼─────────────┐                 │
│           │    │             │             │                 │
│           │    ▼             ▼             ▼                 │
│           │ ┌──────┐   ┌──────────┐  ┌──────────┐          │
│           │ │ ext4 │   │  Page    │  │  Device  │          │
│           │ │ xfs  │   │  Cache   │  │  Driver  │          │
│           │ └──────┘   └──────────┘  └────┬─────┘          │
│           │                               │                 │
│           └───────────────────────────────┘                 │
│                                           │                 │
│    ┌──────────────────────────────────────┘                 │
│    │   Block I/O Layer                                       │
│    │   (I/O Scheduler: CFQ/Deadline/NOOP)                    │
│    └──────────────────────────┬──────────────────────────────┘
└───────────────────────────────┼──────────────────────────────┘
                                │
┌───────────────────────────────┼──────────────────────────────┐
│                               │     Hardware                 │
│    ┌──────────────────────────┘                              │
│    │   Host Controller Adapter (HCA)                         │
│    │   ┌─────────┬─────────┬─────────┐                       │
│    └───┤  SATA   │  NVMe   │  SCSI   │                       │
│        │Controller│Controller│Controller│                       │
│        └────┬────┴────┬────┴────┬────┘                       │
│             │         │         │                            │
│        ┌────┴────┐ ┌──┴────┐ ┌──┴────┐                       │
│        │   HDD   │ │  SSD  │ │  Disk │                       │
│        │         │ │ NVMe  │ │ Array │                       │
│        └─────────┘ └───────┘ └───────┘                       │
└──────────────────────────────────────────────────────────────┘
```

### 中断与DMA机制

```python
class IOController:
    """I/O控制器模拟"""
    
    def __init__(self):
        self.dma_controller = DMAController()
        self.interrupt_controller = InterruptController()
    
    def programmed_io(self, device, buffer, size):
        """程序控制I/O：CPU全程参与"""
        for i in range(size):
            # 轮询设备状态
            while not device.status.ready:
                pass  # 忙等待，浪费CPU
            
            # CPU逐字节传输
            data = device.read_register(DATA_REG)
            buffer[i] = data
            
        return size
    
    def interrupt_driven_io(self, device, buffer, size):
        """中断驱动I/O：设备就绪后通知CPU"""
        self.current_transfer = {
            'device': device,
            'buffer': buffer,
            'size': size,
            'completed': 0
        }
        
        # 启动设备，设置中断使能
        device.command.start = True
        device.control.interrupt_enable = True
        
        # CPU可以继续执行其他任务
        return PENDING  # 异步操作
    
    def handle_interrupt(self, irq):
        """中断处理"""
        device = self.get_device_by_irq(irq)
        transfer = self.current_transfer
        
        if device.status.error:
            self.handle_error(device)
            return
        
        # 读取数据
        data = device.read_register(DATA_REG)
        transfer['buffer'][transfer['completed']] = data
        transfer['completed'] += 1
        
        if transfer['completed'] >= transfer['size']:
            # 传输完成，唤醒等待进程
            self.wakeup_process(transfer)
            device.control.interrupt_enable = False
    
    def dma_transfer(self, device, buffer, size, direction='read'):
        """DMA传输：无需CPU介入"""
        # 1. 配置DMA控制器
        self.dma_controller.setup(
            source=device.data_port if direction == 'read' else buffer.address,
            dest=buffer.address if direction == 'read' else device.data_port,
            count=size,
            direction=direction
        )
        
        # 2. 启动DMA，CPU继续执行
        self.dma_controller.start()
        
        # 3. DMA完成中断
        return PENDING
    
    def handle_dma_complete(self):
        """DMA完成中断处理"""
        # 只需唤醒进程，数据已在内存
        self.wakeup_process(self.current_transfer)

class DMAController:
    """DMA控制器"""
    
    def __init__(self):
        self.channels = [DMAChannel(i) for i in range(8)]
    
    def setup(self, channel_id, source, dest, count):
        channel = self.channels[channel_id]
        channel.source_addr = source
        channel.dest_addr = dest
        channel.count = count
        channel.status = 'READY'
    
    def start(self, channel_id):
        """开始DMA传输"""
        channel = self.channels[channel_id]
        
        while channel.count > 0:
            # 占用内存总线一个周期
            data = self.memory_bus.read(channel.source_addr)
            self.memory_bus.write(channel.dest_addr, data)
            
            channel.source_addr += 1
            channel.dest_addr += 1
            channel.count -= 1
        
        # 传输完成，发送中断
        self.interrupt_controller.send_interrupt(channel.irq)
```

### I/O调度算法

```python
class IOScheduler:
    """磁盘I/O调度器"""
    
    def __init__(self, algorithm='CFQ'):
        self.algorithm = algorithm
        self.request_queue = []
        self.current_head = 0  # 磁头当前位置
    
    def fcfs_schedule(self, requests):
        """FCFS：先来先服务"""
        # 简单但会导致磁头大幅摆动
        return requests
    
    def sstf_schedule(self, requests):
        """SSTF：最短寻道时间优先"""
        sorted_requests = []
        current = self.current_head
        remaining = requests[:]
        
        while remaining:
            # 找最近的请求
            nearest = min(remaining, 
                         key=lambda r: abs(r.lba - current))
            sorted_requests.append(nearest)
            current = nearest.lba
            remaining.remove(nearest)
        
        return sorted_requests
    
    def scan_schedule(self, requests, direction='up'):
        """SCAN/电梯算法"""
        # 磁头像电梯一样单向扫描
        up_requests = [r for r in requests if r.lba >= self.current_head]
        down_requests = [r for r in requests if r.lba < self.current_head]
        
        up_requests.sort(key=lambda r: r.lba)
        down_requests.sort(key=lambda r: r.lba, reverse=True)
        
        if direction == 'up':
            return up_requests + down_requests
        else:
            return down_requests + up_requests
    
    def cscan_schedule(self, requests):
        """C-SCAN：循环扫描"""
        # 只向一个方向扫描，到达边界后快速返回
        up_requests = [r for r in requests if r.lba >= self.current_head]
        down_requests = [r for r in requests if r.lba < self.current_head]
        
        up_requests.sort(key=lambda r: r.lba)
        down_requests.sort(key=lambda r: r.lba)
        
        return up_requests + down_requests  # 单向循环
    
    def deadline_schedule(self, requests):
        """Deadline调度：兼顾公平和效率"""
        # 读请求优先级高于写（异步写可延迟）
        # 防止请求饿死，设置截止期限
        read_requests = [r for r in requests if r.type == 'READ']
        write_requests = [r for r in requests if r.type == 'WRITE']
        
        # 按截止时间排序
        read_requests.sort(key=lambda r: r.deadline)
        
        # 合并相邻请求
        return self.merge_adjacent(read_requests + write_requests)
```

### 零拷贝技术

```python
class ZeroCopyTechniques:
    """零拷贝技术实现"""
    
    def traditional_file_send(self, fd, socket, count):
        """传统方式：4次拷贝，4次上下文切换"""
        # 1. 磁盘 -> 内核页缓存 (DMA)
        buffer = kmalloc(count)
        read(fd, buffer, count)      # 用户态 -> 内核态
        
        # 2. 内核页缓存 -> 用户缓冲区 (CPU拷贝)
        # 3. 用户缓冲区 -> 内核socket缓冲区 (CPU拷贝)
        write(socket, buffer, count) # 用户态 -> 内核态
        
        # 4. socket缓冲区 -> 网卡 (DMA)
        kfree(buffer)
    
    def mmap_sendfile(self, fd, socket, count):
        """mmap + sendfile：减少用户态拷贝"""
        # 1. 磁盘 -> 内核页缓存 (DMA)
        addr = mmap(NULL, count, PROT_READ, MAP_PRIVATE, fd, 0)
        
        # 2. 页缓存 -> socket缓冲区 (CPU拷贝)
        write(socket, addr, count)
        
        munmap(addr, count)
        # 减少了一次用户态<->内核态拷贝
    
    def sendfile_zero_copy(self, fd, socket, count):
        """sendfile系统调用：2次拷贝"""
        # Linux 2.1+: 数据不经过用户态
        # 1. 磁盘 -> 内核页缓存 (DMA)
        # 2. 页缓存 -> socket缓冲区 (CPU拷贝/分散-聚集DMA)
        sendfile(socket, fd, NULL, count)
    
    def splice_zero_copy(self, fd_in, fd_out, count):
        """splice：管道零拷贝"""
        # Linux 2.6.17+: 管道缓冲区作为中间媒介
        # 完全在内核空间传输，无需CPU拷贝
        pipefd = pipe()
        splice(fd_in, NULL, pipefd[1], NULL, count, SPLICE_F_MOVE)
        splice(pipefd[0], NULL, fd_out, NULL, count, SPLICE_F_MOVE)
    
    def dma_gather_copy(self, fd, socket, count):
        """DMA Gather Copy：真正的零拷贝"""
        # 网卡支持Gather DMA
        # 1. 磁盘 -> 页缓存 (DMA)
        # 2. 页缓存直接 -> 网卡 (Gather DMA，无需CPU)
        # 需要网卡支持分散-聚集I/O
        sendfile(socket, fd, NULL, count)  # 带SPLICE_F_GIFT标志
```

## 应用场景
- **数据库系统**: 异步I/O提升并发处理能力
- **Web服务器**: 零拷贝加速静态文件传输
- **存储系统**: I/O调度优化SSD/HDD混合部署
- **虚拟化**: SR-IOV设备直通减少开销

## 面试要点

1. **Q: 中断和轮询的区别？适用场景？**  
   A: 轮询：CPU定期检查设备状态，简单但浪费CPU；中断：设备就绪通知CPU，高效但上下文切换有开销。适用：①低速设备用中断（键盘、鼠标）；②高速设备用轮询或混合（网卡NAPI：中断触发，轮询收包）；③批量传输用DMA+中断。

2. **Q: DMA的工作原理和优点？**  
   A: DMA控制器直接在设备和内存间传输数据，无需CPU逐字节搬运。过程：CPU设置DMA参数（源、目的、大小），DMA控制器接管总线传输，完成后中断CPU。优点：释放CPU执行其他任务，传输速度快。缺点：DMA期间CPU可能无法访问内存（总线竞争）。

3. **Q: 零拷贝是什么？如何实现？**  
   A: 零拷贝避免数据在内核态和用户态间重复拷贝。实现：①mmap：文件映射到用户空间，减少一次拷贝；②sendfile：内核态直接文件到socket；③splice：管道在内核间传输；④DMA Gather：页缓存直接DMA到网卡。效果：减少CPU拷贝、上下文切换、内存带宽压力。

4. **Q: SSD和传统HDD的I/O调度有何不同？**  
   A: HDD需要寻道和旋转，调度算法关注最小化磁头移动（SCAN、C-SCAN）；SSD无机械部件，随机访问快，调度目标不同：①并行化（SSD多通道）；②磨损均衡；③垃圾回收友好；④通常用NOOP或Deadline调度器，而非CFQ。

## 相关概念

### 数据结构
- [队列](../data-structures/queue.md)
- [红黑树](../data-structures/red-black-tree.md)

### 算法
- [磁盘调度算法](../algorithms/disk-scheduling.md)
- [页面置换算法](../algorithms/page-replacement.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [内存层次](memory-hierarchy.md)
- [缓存一致性](cache-coherence.md)
