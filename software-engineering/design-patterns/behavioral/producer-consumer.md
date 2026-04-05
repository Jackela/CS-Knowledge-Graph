# 生产者消费者模式 (Producer-Consumer Pattern)

生产者消费者模式是一种**并发设计模式**，用于解决多线程间数据传递和协作的问题，通过缓冲区解耦生产者和消费者。

## 核心概念

### 模式结构

```
生产者消费者模式：

┌─────────────────────────────────────────────────────────────┐
│                  生产者消费者模式                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐      缓冲区/队列      ┌─────────────┐    │
│   │  Producer   │ ───────────────────▶ │  Consumer   │    │
│   │  (生产者)    │                      │  (消费者)    │    │
│   │             │    ┌──────────┐      │             │    │
│   │ 生成数据     │───▶│  Queue   │─────▶│ 消费数据     │    │
│   │             │    │ (阻塞队列)│      │             │    │
│   └─────────────┘    └──────────┘      └─────────────┘    │
│                                                             │
│   特点：                                                     │
│   • 生产者和消费者解耦                                       │
│   • 通过缓冲区平衡速度差异                                    │
│   • 支持多生产者、多消费者                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 实现示例

### Python 实现

```python
import threading
import queue
import time

# 创建阻塞队列
buffer = queue.Queue(maxsize=10)

class Producer(threading.Thread):
    def __init__(self, buffer, name):
        super().__init__()
        self.buffer = buffer
        self.name = name
    
    def run(self):
        for i in range(5):
            item = f"产品-{self.name}-{i}"
            self.buffer.put(item)  # 阻塞直到有空间
            print(f"生产者 {self.name} 生产了: {item}")
            time.sleep(0.1)

class Consumer(threading.Thread):
    def __init__(self, buffer, name):
        super().__init__()
        self.buffer = buffer
        self.name = name
    
    def run(self):
        while True:
            try:
                item = self.buffer.get(timeout=1)  # 阻塞直到有数据
                print(f"消费者 {self.name} 消费了: {item}")
                self.buffer.task_done()
            except queue.Empty:
                break

# 启动生产者和消费者
producers = [Producer(buffer, f"P{i}") for i in range(2)]
consumers = [Consumer(buffer, f"C{i}") for i in range(3)]

for p in producers:
    p.start()
for c in consumers:
    c.start()

for p in producers:
    p.join()
buffer.join()  # 等待所有项目被处理
```

### Java 实现

```java
import java.util.concurrent.*;

public class ProducerConsumer {
    private static BlockingQueue<String> buffer = 
        new ArrayBlockingQueue<>(10);
    
    static class Producer implements Runnable {
        public void run() {
            try {
                for (int i = 0; i < 5; i++) {
                    String item = "产品-" + i;
                    buffer.put(item);  // 阻塞直到有空间
                    System.out.println("生产: " + item);
                    Thread.sleep(100);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    static class Consumer implements Runnable {
        public void run() {
            try {
                while (true) {
                    String item = buffer.take();  // 阻塞直到有数据
                    System.out.println("消费: " + item);
                    Thread.sleep(200);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    public static void main(String[] args) {
        new Thread(new Producer()).start();
        new Thread(new Consumer()).start();
    }
}
```

## 应用场景

### 1. 消息队列

```
订单系统 ──▶ 消息队列 ──▶ 库存系统
            (缓冲区)
            ──▶ 支付系统
            ──▶ 物流系统
```

### 2. 线程池

```python
from concurrent.futures import ThreadPoolExecutor

# 线程池内部使用生产者消费者模式
with ThreadPoolExecutor(max_workers=4) as executor:
    # 提交任务（生产）
    futures = [executor.submit(task, i) for i in range(10)]
    # 获取结果（消费）
    results = [f.result() for f in futures]
```

### 3. 日志系统

```
应用线程 ──▶ 日志缓冲区 ──▶ 日志写入线程
           （内存队列）      （磁盘IO）
```

## 关键问题

### 线程安全

```python
# 使用线程安全的队列
from queue import Queue          # 线程安全
from multiprocessing import Queue # 进程安全

# 避免使用非线程安全结构
# buffer = []  # ❌ 不安全的列表操作
```

### 防止死锁

```python
# 确保正确调用 task_done()
class Consumer(threading.Thread):
    def run(self):
        while True:
            item = self.buffer.get()
            if item is None:  # 毒丸对象
                break
            self.process(item)
            self.buffer.task_done()  # 重要！
```

## 优缺点

| 优点 | 缺点 |
|------|------|
| 解耦生产者和消费者 | 增加系统复杂度 |
| 平衡速度差异 | 需要处理同步问题 |
| 支持并发处理 | 缓冲区可能溢出 |
| 提高吞吐量 | 增加延迟 |

## 相关概念

- [消息队列](./message-queue.md) - 分布式生产者消费者

## 参考资料

1. "Java Concurrency in Practice" - Brian Goetz
2. Python concurrent.futures 文档
