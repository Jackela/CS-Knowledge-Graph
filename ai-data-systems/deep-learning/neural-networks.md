# 神经网络基础 (Neural Networks Basics)

## 简介
神经网络是受生物神经系统启发的计算模型，通过多层相互连接的神经元学习复杂的非线性映射，是深度学习的基石。

## 核心概念

### 神经元模型
单个神经元接收输入 $\mathbf{x}$，计算加权和并通过激活函数输出：

$$z = \sum_{i=1}^{n} w_i x_i + b = \mathbf{w}^T\mathbf{x} + b$$

$$a = f(z)$$

其中 $f$ 是激活函数，$w$ 是权重，$b$ 是偏置。

### 激活函数

**Sigmoid**：$\sigma(z) = \frac{1}{1 + e^{-z}}$，输出(0,1)

**Tanh**：$\tanh(z) = \frac{e^z - e^{-z}}{e^z + e^{-z}}$，输出(-1,1)

**ReLU**：$ReLU(z) = \max(0, z)$，计算高效，缓解梯度消失

**Leaky ReLU**：$f(z) = \max(\alpha z, z)$，解决ReLU死亡问题

**Softmax**：$\sigma(z_i) = \frac{e^{z_i}}{\sum_{j}e^{z_j}}$，多分类输出层

### 前向传播
输入通过网络层逐层计算输出：

$$\mathbf{z}^{[l]} = \mathbf{W}^{[l]}\mathbf{a}^{[l-1]} + \mathbf{b}^{[l]}$$

$$\mathbf{a}^{[l]} = f(\mathbf{z}^{[l]})$$

### 反向传播
使用链式法则计算梯度并更新参数：

$$\frac{\partial L}{\partial W^{[l]}} = \frac{\partial L}{\partial a^{[l]}} \cdot \frac{\partial a^{[l]}}{\partial z^{[l]}} \cdot \frac{\partial z^{[l]}}{\partial W^{[l]}}$$

### 损失函数
- **回归**：MSE = $\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2$
- **二分类**：二元交叉熵 = $-\frac{1}{n}\sum_{i}[y_i\log(\hat{y}_i) + (1-y_i)\log(1-\hat{y}_i)]$
- **多分类**：交叉熵 = $-\frac{1}{n}\sum_{i}\sum_{c}y_{i,c}\log(\hat{y}_{i,c})$

## 实现方式

```python
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ===== PyTorch实现 =====
# 生成数据
X, y = make_moons(n_samples=1000, noise=0.2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 转换为Tensor
X_train_tensor = torch.FloatTensor(X_train)
y_train_tensor = torch.LongTensor(y_train)
X_test_tensor = torch.FloatTensor(X_test)
y_test_tensor = torch.LongTensor(y_test)

# 定义神经网络
class NeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNetwork, self).__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.layer2 = nn.Linear(hidden_size, hidden_size)
        self.layer3 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.layer2(x)
        x = self.relu(x)
        x = self.layer3(x)
        return x

# 初始化模型
model = NeuralNetwork(input_size=2, hidden_size=64, num_classes=2)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 训练
num_epochs = 100
for epoch in range(num_epochs):
    # 前向传播
    outputs = model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    
    # 反向传播
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    if (epoch + 1) % 20 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# 评估
model.eval()
with torch.no_grad():
    test_outputs = model(X_test_tensor)
    _, predicted = torch.max(test_outputs, 1)
    accuracy = (predicted == y_test_tensor).float().mean()
    print(f'\n测试准确率: {accuracy:.4f}')

# ===== NumPy实现 (前向+反向传播) =====
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

# 简单2层神经网络
class SimpleNN:
    def __init__(self, input_size, hidden_size, output_size):
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
    
    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = sigmoid(self.z2)
        return self.a2
    
    def backward(self, X, y, learning_rate=0.1):
        m = X.shape[0]
        
        # 输出层梯度
        dz2 = self.a2 - y
        dW2 = np.dot(self.a1.T, dz2) / m
        db2 = np.sum(dz2, axis=0, keepdims=True) / m
        
        # 隐藏层梯度
        dz1 = np.dot(dz2, self.W2.T) * sigmoid_derivative(self.a1)
        dW1 = np.dot(X.T, dz1) / m
        db1 = np.sum(dz1, axis=0, keepdims=True) / m
        
        # 更新参数
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1

print("\nNumPy实现训练完成")
```

## 应用场景
- **图像识别**：物体检测、人脸识别
- **自然语言处理**：文本分类、机器翻译
- **语音识别**：语音转文字、说话人识别
- **推荐系统**：协同过滤、内容推荐
- **游戏AI**：AlphaGo、游戏机器人

## 面试要点

1. **Q: 为什么需要激活函数？**
   A: 激活函数引入非线性，使网络能学习复杂模式。没有激活函数，多层网络等价于单层线性变换，无法解决非线性问题。

2. **Q: 梯度消失和梯度爆炸是什么？如何解决？**
   A: 梯度消失：深层网络反向传播时梯度逐层衰减，浅层难以学习。梯度爆炸：梯度逐层增大导致参数更新过大。解决方法：使用ReLU、批归一化、残差连接、梯度裁剪、更好的权重初始化。

3. **Q: ReLU的优点和缺点？**
   A: 优点：计算简单，缓解梯度消失，加速收敛。缺点：可能导致"神经元死亡"（负梯度永远为0），可使用Leaky ReLU或ELU改进。

4. **Q: 权重初始化为什么重要？**
   A: 不良初始化会导致梯度消失/爆炸或对称性问题。常用方法：Xavier初始化（适合tanh/sigmoid）、He初始化（适合ReLU），确保前向和反向传播时方差保持一致。

## 相关概念

### AI & Data Systems
- [反向传播算法](./backpropagation.md)
- [卷积神经网络](./cnn.md)
- [循环神经网络](./rnn.md)
- [优化算法](./optimization-algorithms.md)
- [正则化方法](./regularization.md)
- [Transformer架构](./transformers.md)

### 数学基础
- [线性代数](../../mathematics/linear-algebra.md)
- [微积分](../../mathematics/calculus.md)
- [概率论与统计](../../mathematics/probability-statistics.md)
- [最优化方法](../../mathematics/optimization.md)
