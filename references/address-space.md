# 地址空间

是系统可[寻址](./memory-addressing.md)的全部位置的集合。

每个地址对应一个唯一存储单元（或虚拟单元），并具有寻址范围和分辨率。

不同层次的系统（硬件、进程、虚拟内存）都有自己的地址空间。

- 物理地址空间
- 虚拟地址空间
- [线性地址空间](./linear-address-space.md)

### 安全启动与地址空间

[安全启动](../security/system-security/secure-boot.md)机制在系统启动时建立可信的地址空间环境，防止恶意代码在地址空间初始化阶段植入。

## 相关概念

- [虚拟内存](../computer-science/systems/virtual-memory.md) - 虚拟地址空间管理
