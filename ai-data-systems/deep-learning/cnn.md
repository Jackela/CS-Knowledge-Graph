# 卷积神经网络 (Convolutional Neural Network, CNN)

## 简介
卷积神经网络是专门设计用于处理具有网格结构数据（如图像）的深度学习模型，通过卷积层自动提取空间层次特征，在计算机视觉领域取得了革命性突破。

## 核心概念

### 卷积操作
卷积核（滤波器）在输入上滑动进行元素乘积求和：

$$(I * K)(i, j) = \sum_{m}\sum_{n} I(i+m, j+n) \cdot K(m, n)$$

其中 $I$ 是输入，$K$ 是卷积核。

### 关键超参数
- **卷积核大小**（Kernel Size）：通常为3×3、5×5、7×7
- **步长**（Stride）：卷积核移动的步幅，控制输出尺寸
- **填充**（Padding）：在输入边缘补充0，控制输出尺寸
- **通道数**（Channels）：卷积核数量，决定输出特征图深度

### 输出尺寸计算
$$Output = \lfloor \frac{Input - Kernel + 2 \times Padding}{Stride} \rfloor + 1$$

### 池化层
降低特征图空间维度，减少计算量，提供平移不变性：
- **最大池化**（Max Pooling）：取区域内最大值
- **平均池化**（Average Pooling）：取区域内平均值

### 典型架构组件
1. **卷积层**：提取局部特征
2. **激活层**：引入非线性（ReLU常用）
3. **批归一化**（BatchNorm）：加速训练，稳定梯度
4. **池化层**：降采样
5. **全连接层**：分类输出
6. **Dropout**：防止过拟合

## 实现方式

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms

# ===== 定义CNN架构 (类似LeNet-5) =====
class CNN(nn.Module):
    def __init__(self, num_classes=10):
        super(CNN, self).__init__()
        # 第一层卷积: 1x28x28 -> 6x28x28 -> 6x14x14
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=6, 
                               kernel_size=5, padding=2)
        self.bn1 = nn.BatchNorm2d(6)
        
        # 第二层卷积: 6x14x14 -> 16x10x10 -> 16x5x5
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=16, 
                               kernel_size=5)
        self.bn2 = nn.BatchNorm2d(16)
        
        # 全连接层
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, num_classes)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        # 卷积层1 + ReLU + 池化
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)
        
        # 卷积层2 + ReLU + 池化
        x = self.conv2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)
        
        # 展平
        x = x.view(x.size(0), -1)
        
        # 全连接层
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# ===== 使用预训练模型 (ResNet18) =====
from torchvision import models

# 加载预训练ResNet18
resnet = models.resnet18(pretrained=True)

# 冻结所有层
for param in resnet.parameters():
    param.requires_grad = False

# 修改最后一层进行迁移学习
num_features = resnet.fc.in_features
resnet.fc = nn.Linear(num_features, 10)  # 10个类别

print("CNN模型定义完成")
print(f"ResNet18参数数量: {sum(p.numel() for p in resnet.parameters()):,}")
print(f"可训练参数数量: {sum(p.numel() for p in resnet.parameters() if p.requires_grad):,}")

# ===== 手动卷积操作演示 =====
import numpy as np

# 输入图像 (5x5)
image = np.array([
    [1, 1, 1, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 1, 1],
    [0, 0, 1, 1, 0],
    [0, 1, 1, 0, 0]
])

# 卷积核 (3x3)
kernel = np.array([
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
])

# 简单卷积 (无填充，步长1)
def simple_convolve(image, kernel):
    h, w = image.shape
    kh, kw = kernel.shape
    output_h, output_w = h - kh + 1, w - kw + 1
    output = np.zeros((output_h, output_w))
    
    for i in range(output_h):
        for j in range(output_w):
            output[i, j] = np.sum(image[i:i+kh, j:j+kw] * kernel)
    return output

result = simple_convolve(image, kernel)
print(f"\n卷积输入尺寸: {image.shape}")
print(f"卷积核尺寸: {kernel.shape}")
print(f"卷积输出尺寸: {result.shape}")
```

## 应用场景
- **图像分类**：ImageNet图像识别、医学影像诊断
- **目标检测**：YOLO、Faster R-CNN检测图像中的物体
- **语义分割**：FCN、U-Net进行像素级分类
- **人脸识别**：FaceNet、DeepFace识别身份
- **风格迁移**：将艺术风格迁移到普通照片
- **OCR识别**：文字检测与识别

## 面试要点

1. **Q: 卷积层相比全连接层的优势？**
   A: 1) 参数共享：同一卷积核在整个输入上共享权重；2) 局部连接：只连接局部区域；3) 平移不变性：能识别不同位置的相同特征。大幅减少参数量，提高训练效率。

2. **Q: 1×1卷积的作用？**
   A: 1) 降维/升维：改变特征图通道数；2) 引入非线性：增加网络深度；3) 跨通道信息融合；4) 减少计算量（如Inception模块）。

3. **Q: 为什么CNN适合图像处理？**
   A: 图像具有局部相关性（像素与邻近像素相关）和平移不变性（物体位置变化但类别不变）。CNN的局部连接、权重共享和池化操作天然契合这些特性。

4. **Q: Batch Normalization的作用？**
   A: 1) 加速训练收敛；2) 允许使用更大学习率；3) 减少对初始化的依赖；4) 有一定正则化效果。通过对每层输入进行标准化（均值为0，方差为1），解决内部协变量偏移问题。

## 相关概念

### AI & Data Systems
- [神经网络基础](./neural-networks.md)
- [循环神经网络](./rnn.md)
- [残差网络](./resnet.md)
- [目标检测](./object-detection.md)
- [图像分割](./image-segmentation.md)
- [注意力机制](./attention.md)

### 数学基础
- [线性代数](../../mathematics/linear-algebra.md)
- [张量运算](../../mathematics/tensor-operations.md)
- [信号处理](../../mathematics/signal-processing.md)
