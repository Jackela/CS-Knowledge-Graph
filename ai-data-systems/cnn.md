# 卷积神经网络 (CNN - Convolutional Neural Network)

## 简介

**卷积神经网络 (Convolutional Neural Network, CNN)** 是一种专门用于处理具有网格结构数据（如图像）的深度学习模型。CNN通过卷积运算自动提取特征，在计算机视觉任务中取得了巨大成功。

```
┌─────────────────────────────────────────────────────────────┐
│                   CNN 核心思想                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   传统图像处理：              CNN特征学习：                   │
│                                                             │
│   人工设计特征                 自动学习特征                  │
│   ┌──────────┐                ┌──────────┐                 │
│   │边缘检测器 │                │  卷积层   │                 │
│   │角点检测器 │────▶          │   +      │────▶ 高层特征    │
│   │SIFT/HOG  │                │  池化层   │                 │
│   └──────────┘                └──────────┘                 │
│                                                             │
│   特征工程（人工）            表示学习（自动）               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 卷积运算

### 基本卷积操作

```
卷积运算：

输入图像 (5×5)              卷积核 (3×3)
┌──┬──┬──┬──┬──┐           ┌──┬──┬──┐
│ 1│ 1│ 1│ 0│ 0│           │ 1│ 0│ 1│
├──┼──┼──┼──┼──┤           ├──┼──┼──┤
│ 0│ 1│ 1│ 1│ 0│    *      │ 0│ 1│ 0│
├──┼──┼──┼──┼──┤           ├──┼──┼──┤
│ 0│ 0│ 1│ 1│ 1│           │ 1│ 0│ 1│
├──┼──┼──┼──┼──┤           └──┴──┴──┘
│ 0│ 0│ 0│ 1│ 1│
├──┼──┼──┼──┼──┤
│ 0│ 0│ 0│ 0│ 1│
└──┴──┴──┴──┴──┘

计算过程（stride=1）：

位置(0,0): 1×1 + 1×0 + 1×1 + 0×0 + 1×1 + 1×0 + 0×1 + 0×0 + 1×1 = 4
位置(0,1): 1×1 + 1×0 + 0×1 + 1×0 + 1×1 + 1×0 + 0×1 + 1×0 + 1×1 = 3
...

输出特征图 (3×3):
┌──┬──┬──┐
│ 4│ 3│ 4│
├──┼──┼──┤
│ 2│ 4│ 3│
├──┼──┼──┤
│ 2│ 3│ 4│
└──┴──┴──┘
```

### 卷积参数

```python
import torch
import torch.nn as nn

# 卷积层定义
conv = nn.Conv2d(
    in_channels=3,      # 输入通道数（RGB图像=3）
    out_channels=64,    # 输出通道数（卷积核数量）
    kernel_size=3,      # 卷积核大小 3×3
    stride=1,           # 步长
    padding=1,          # 填充（保持尺寸）
    dilation=1,         # 空洞率
    groups=1,           # 分组卷积
    bias=True           # 是否使用偏置
)

# 参数计算
# 权重参数 = out_channels × in_channels × kernel_size²
#          = 64 × 3 × 3 × 3 = 1728
# 偏置参数 = out_channels = 64
# 总参数 = 1728 + 64 = 1792
```

## CNN核心组件

### 1. 卷积层 (Convolutional Layer)

```
卷积层作用：提取局部特征

输入: (Batch, Channel, Height, Width) = (N, C_in, H, W)
输出: (N, C_out, H', W')

其中：
H' = (H - K + 2P) / S + 1
W' = (W - K + 2P) / S + 1

K = kernel_size, P = padding, S = stride

特征图可视化：

输入图像          卷积核1          卷积核2          卷积核3
┌────────┐       ┌────────┐       ┌────────┐       ┌────────┐
│  猫咪  │  ──▶  │ 边缘   │       │ 纹理   │       │ 形状   │
│  照片  │       │ 特征   │       │ 特征   │       │ 特征   │
└────────┘       └────────┘       └────────┘       └────────┘
                     │                │                │
                     └────────────────┴────────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │  特征图堆叠   │
                              │  (多通道)     │
                              └───────────────┘
```

### 2. 激活函数

```python
# ReLU (Rectified Linear Unit)
# f(x) = max(0, x)

     f(x)
      │
      │      /
      │     /
   0 ─┼────●──────────▶ x
      │   /
      │  /
      │ /

relu = nn.ReLU()
# 优点：计算简单、缓解梯度消失、稀疏激活
# 缺点：负数区域梯度为0（死亡ReLU）

# Leaky ReLU
# f(x) = max(αx, x), α通常=0.01
leaky_relu = nn.LeakyReLU(negative_slope=0.01)

# 解决死亡ReLU问题
```

### 3. 池化层 (Pooling Layer)

```
最大池化 (Max Pooling)：

2×2 池化，stride=2

┌───┬───┐
│ 1 │ 3 │      max(1,3,2,4) = 4
├───┼───┤  ──▶  ┌───┐
│ 2 │ 4 │       │ 4 │
└───┴───┘       └───┘

作用：
1. 降低特征图尺寸，减少参数量
2. 提供平移不变性
3. 保留最显著特征

平均池化 (Average Pooling)：
取区域内平均值，保留更多背景信息
```

### 4. 批归一化 (Batch Normalization)

```python
# Batch Normalization
# 对每个mini-batch进行归一化

bn = nn.BatchNorm2d(num_features=64)

# 计算：
# μ_B = (1/m) Σx_i       # mini-batch均值
# σ²_B = (1/m) Σ(x_i - μ_B)²  # mini-batch方差
# x̂_i = (x_i - μ_B) / √(σ²_B + ε)  # 归一化
# y_i = γx̂_i + β  # 缩放和平移（可学习参数）

# 优点：
# - 加速训练收敛
# - 允许使用更大学习率
# - 减少对初始化的依赖
# - 轻微正则化效果
```

### 5. Dropout

```python
# Dropout：随机丢弃神经元，防止过拟合

dropout = nn.Dropout(p=0.5)  # 50%概率丢弃

训练时：
┌─────┐     ┌─────┐     ┌─────┐
│  ○  │────▶│  ✕  │────▶│  ○  │   随机丢弃
└─────┘     └─────┘     └─────┘

测试时：
┌─────┐     ┌─────┐     ┌─────┐
│  ○  │────▶│  ○  │────▶│  ○  │   使用所有神经元，权重缩放
└─────┘     └─────┘     └─────┘
```

## 经典CNN架构

### LeNet-5 (1998)

```
LeNet-5 结构（手写数字识别）：

Input (32×32×1)
    │
    ▼
Conv1: 6@5×5, stride=1  ──▶  28×28×6
    │
    ▼
Avg Pool: 2×2, stride=2  ──▶  14×14×6
    │
    ▼
Conv2: 16@5×5, stride=1  ──▶  10×10×16
    │
    ▼
Avg Pool: 2×2, stride=2  ──▶  5×5×16
    │
    ▼
FC: 120
    │
    ▼
FC: 84
    │
    ▼
Output: 10 (数字类别)
```

### AlexNet (2012)

```
AlexNet 结构（ImageNet冠军）：

创新点：
- ReLU激活函数
- GPU并行训练
- Dropout正则化
- 数据增强

结构：
Input (227×227×3)
    │
    ├──▶ Conv1: 96@11×11, stride=4  ──▶  55×55×96
    │      MaxPool 3×3, stride=2
    │
    ├──▶ Conv2: 256@5×5, pad=2  ──▶  27×27×256
    │      MaxPool 3×3, stride=2
    │
    ├──▶ Conv3: 384@3×3, pad=1  ──▶  13×13×384
    │
    ├──▶ Conv4: 384@3×3, pad=1  ──▶  13×13×384
    │
    ├──▶ Conv5: 256@3×3, pad=1  ──▶  13×13×256
    │      MaxPool 3×3, stride=2
    │
    ├──▶ FC: 4096
    │      Dropout(0.5)
    │
    ├──▶ FC: 4096
    │      Dropout(0.5)
    │
    └──▶ Output: 1000

参数量：约6000万
```

### VGGNet (2014)

```
VGG 核心思想：使用小卷积核 (3×3) 堆叠

VGG-16 配置：

Input (224×224×3)
    │
    ├──▶ Conv3-64 ×2   ──▶ 224×224×64   ──▶ MaxPool
    │
    ├──▶ Conv3-128 ×2  ──▶ 112×112×128  ──▶ MaxPool
    │
    ├──▶ Conv3-256 ×3  ──▶ 56×56×256    ──▶ MaxPool
    │
    ├──▶ Conv3-512 ×3  ──▶ 28×28×512    ──▶ MaxPool
    │
    ├──▶ Conv3-512 ×3  ──▶ 14×14×512    ──▶ MaxPool
    │
    ├──▶ FC-4096
    │
    ├──▶ FC-4096
    │
    └──▶ FC-1000

特点：
- 3×3卷积核，padding=1保持尺寸
- 2×2 MaxPool，stride=2减半尺寸
- 规律：卷积层数增加 → 通道数翻倍

参数量：约1.38亿
```

### ResNet (2015)

```
ResNet 核心：残差连接 (Residual Connection)

基本残差块：

         x
         │
    ┌────┴────┐
    │         │
    ▼         │
┌───────┐     │
│Conv   │     │
│3×3,64 │     │
└───┬───┘     │
    ▼         │
┌───────┐     │
│Conv   │     │
│3×3,64 │     │
└───┬───┘     │
    │         │
    ▼         │
   (+) ◀──────┘    # 跳跃连接 (Skip Connection)
    │
    ▼
  ReLU

为什么有效？
- 解决深层网络梯度消失问题
- 学习残差映射 F(x) = H(x) - x 比学习恒等映射容易
- 可以训练非常深的网络（ResNet-152, ResNet-1000+）
```

### 架构演进

```
CNN架构演进时间线：

1998  LeNet-5        8层，手写数字识别
      
2012  AlexNet        8层，ReLU+Dropout，ImageNet冠军
      
2014  VGGNet         16-19层，小卷积核堆叠
      
2014  GoogLeNet      22层，Inception模块，1×1卷积降维
      
2015  ResNet         152+层，残差连接，可训练极深网络
      
2016  DenseNet       密集连接，特征重用
      
2017  SENet          通道注意力机制
      
2019  EfficientNet   复合缩放，效率最优
      
2020  Vision Transformer  注意力机制取代卷积
```

## PyTorch实现CNN

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN(nn.Module):
    def __init__(self, num_classes=10):
        super(CNN, self).__init__()
        
        # 卷积层1: 3 -> 32
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        
        # 卷积层2: 32 -> 64
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        
        # 卷积层3: 64 -> 128
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        # 池化层
        self.pool = nn.MaxPool2d(2, 2)
        
        # Dropout
        self.dropout = nn.Dropout(0.5)
        
        # 全连接层
        # 输入32×32，经过3次池化后: 32/2/2/2 = 4
        self.fc1 = nn.Linear(128 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, num_classes)
    
    def forward(self, x):
        # 卷积块1: 32×32 -> 16×16
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        
        # 卷积块2: 16×16 -> 8×8
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        
        # 卷积块3: 8×8 -> 4×4
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        
        # 展平
        x = x.view(x.size(0), -1)
        
        # 全连接
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x

# 训练循环
def train(model, train_loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        # 前向传播
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        
        # 反向传播
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
    
    return running_loss / len(train_loader)

# 使用示例
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = CNN(num_classes=10).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
```

## 应用案例

### 图像分类

```python
# 使用预训练模型进行图像分类
import torchvision.models as models
from torchvision import transforms
from PIL import Image

# 加载预训练ResNet
model = models.resnet50(pretrained=True)
model.eval()

# 图像预处理
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# 推理
image = Image.open('cat.jpg')
input_tensor = transform(image).unsqueeze(0)

with torch.no_grad():
    output = model(input_tensor)
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    predicted_class = probabilities.argmax().item()
```

### 目标检测

```
目标检测架构：

Two-Stage (R-CNN系列)：
R-CNN → Fast R-CNN → Faster R-CNN

1. 生成候选区域 (Region Proposal)
2. 对每个区域分类和回归

One-Stage (YOLO/SSD)：
直接预测边界框和类别
- YOLO: You Only Look Once
- SSD: Single Shot MultiBox Detector
```

## 面试要点

### 常见问题

**Q1: 卷积层相比全连接层的优势？**
> 1. 参数共享：同一卷积核在整个输入上滑动，大幅减少参数量
> 2. 局部连接：只连接局部区域，捕捉局部特征
> 3. 平移不变性：相同模式在不同位置都能被检测

**Q2: 卷积核大小为什么选择奇数（3×3, 5×5）？**
> 1. 有明确的中心点，便于定位特征位置
> 2. 对称填充（same padding）更容易实现
> 3. 两个3×3卷积的感受野等于一个5×5，但参数更少（18 vs 25）

**Q3: 什么是感受野（Receptive Field）？**
> 感受野是特征图上的一个点对应原始输入图像的区域大小。深层网络通过堆叠卷积层增大感受野，捕捉更大范围的上下文信息。

**Q4: 1×1卷积的作用？**
> 1. 降维/升维：改变通道数而不改变空间尺寸
> 2. 增加非线性：在保持尺寸的同时增加网络深度
> 3. 跨通道信息融合：计算通道间的线性组合
> 4. 减少参数量：在Inception模块中广泛使用

**Q5: Batch Normalization为什么有效？**
> 1. 减少内部协变量偏移（Internal Covariate Shift）
> 2. 允许使用更大学习率，加速收敛
> 3. 具有轻微正则化效果
> 4. 减少对初始化的敏感性

## 相关概念

### 机器学习基础
### 机器学习基础
- [机器学习概述](./ml-overview.md) - 机器学习基础概念
- [线性代数](../mathematics/linear-algebra.md) - 卷积的矩阵运算视角

### 神经网络架构
- [RNN与LSTM](./rnn-lstm.md) - 序列建模网络
- [Transformer](./transformers.md) - 注意力机制与视觉Transformer

### 数学基础
- [图论](../mathematics/graph-theory.md) - 特征图的图结构分析

### 数据结构
- [数组](../computer-science/data-structures/array.md)：图像张量表示
- [队列](../computer-science/data-structures/queue.md)：批量数据加载

### 算法

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：卷积计算复杂度
- [空间复杂度](../references/space-complexity.md)：特征图内存占用

### 系统实现



## 参考资料

1. "Deep Learning" by Goodfellow, Bengio, and Courville
2. "Convolutional Neural Networks for Visual Recognition" (CS231n)
3. ResNet论文: "Deep Residual Learning for Image Recognition"
4. PyTorch官方教程
5. Papers with Code: https://paperswithcode.com
