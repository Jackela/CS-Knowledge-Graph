# 循环神经网络 (Recurrent Neural Network, RNN)

## 简介
循环神经网络是专为序列数据设计的神经网络架构，通过循环连接记忆历史信息，能够处理变长输入，广泛应用于自然语言处理、时间序列预测等领域。

## 核心概念

### RNN基本结构
RNN在每个时间步接收输入 $x_t$ 和上一时刻的隐藏状态 $h_{t-1}$，输出当前隐藏状态 $h_t$：

$$h_t = f(W_{hh}h_{t-1} + W_{xh}x_t + b_h)$$

$$y_t = g(W_{hy}h_t + b_y)$$

其中 $f$ 通常是tanh或ReLU，$g$ 根据任务选择。

### 展开表示
将RNN按时间步展开，形成前馈结构，便于理解梯度流动：

$$h_t = f(W_{hh}h_{t-1} + W_{xh}x_t + b) = f(Uh_{t-1} + Wx_t + b)$$

### 梯度问题
**梯度消失**：长序列反向传播时梯度指数级衰减，导致远距离依赖难以学习。

**梯度爆炸**：梯度指数级增长，导致参数更新不稳定。

### LSTM（长短期记忆网络）
通过门控机制解决梯度消失问题：

**遗忘门**：$f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$

**输入门**：$i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)$

**候选记忆**：$\tilde{C}_t = \tanh(W_C \cdot [h_{t-1}, x_t] + b_C)$

**细胞状态更新**：$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$

**输出门**：$o_t = \sigma(W_o \cdot [h_{t-1}, x_t] + b_o)$

**隐藏状态**：$h_t = o_t \odot \tanh(C_t)$

### GRU（门控循环单元）
LSTM的简化版本，合并细胞状态和隐藏状态：

**更新门**：$z_t = \sigma(W_z \cdot [h_{t-1}, x_t])$

**重置门**：$r_t = \sigma(W_r \cdot [h_{t-1}, x_t])$

**候选隐藏状态**：$\tilde{h}_t = \tanh(W \cdot [r_t \odot h_{t-1}, x_t])$

**隐藏状态**：$h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t$

## 实现方式

```python
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# ===== 基础RNN实现 =====
class BasicRNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(BasicRNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, 
                          batch_first=True, dropout=0.5 if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        # 初始化隐藏状态
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # RNN前向传播
        out, _ = self.rnn(x, h0)  # out: (batch_size, seq_length, hidden_size)
        
        # 取最后一个时间步的输出
        out = self.fc(out[:, -1, :])
        return out

# ===== LSTM实现 =====
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes, 
                 bidirectional=False):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, dropout=0.5 if num_layers > 1 else 0,
                            bidirectional=bidirectional)
        
        fc_input_size = hidden_size * self.num_directions
        self.fc = nn.Linear(fc_input_size, num_classes)
    
    def forward(self, x):
        # 初始化隐藏状态和细胞状态
        h0 = torch.zeros(self.num_layers * self.num_directions, 
                        x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers * self.num_directions, 
                        x.size(0), self.hidden_size).to(x.device)
        
        # LSTM前向传播
        out, _ = self.lstm(x, (h0, c0))
        
        # 双向LSTM：拼接两个方向的最后输出
        if self.bidirectional:
            # 分别取前向和后向的最后输出
            out_forward = out[:, -1, :self.hidden_size]
            out_backward = out[:, 0, self.hidden_size:]
            out = torch.cat((out_forward, out_backward), dim=1)
        else:
            out = out[:, -1, :]
        
        out = self.fc(out)
        return out

# ===== GRU实现 =====
class GRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(GRUModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.gru = nn.GRU(input_size, hidden_size, num_layers,
                         batch_first=True, dropout=0.5 if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.gru(x, h0)
        out = self.fc(out[:, -1, :])
        return out

# ===== 序列到序列（Seq2Seq）示例 =====
class Encoder(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers=1):
        super(Encoder, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers, batch_first=True)
    
    def forward(self, x):
        embedded = self.embedding(x)
        outputs, (hidden, cell) = self.lstm(embedded)
        return outputs, hidden, cell

# 测试模型
input_size = 28  # 如MNIST图像宽度
sequence_length = 28  # 如MNIST图像高度
hidden_size = 128
num_layers = 2
num_classes = 10
batch_size = 64

model = LSTMModel(input_size, hidden_size, num_layers, num_classes, bidirectional=True)
x = torch.randn(batch_size, sequence_length, input_size)
output = model(x)
print(f"输入形状: {x.shape}")
print(f"输出形状: {output.shape}")
print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")
```

## 应用场景
- **机器翻译**：Seq2Seq模型实现语言间翻译
- **文本生成**：生成文章、诗歌、代码
- **语音识别**：将语音转换为文字
- **时间序列预测**：股票价格、天气预测
- **情感分析**：分析文本情感倾向
- **命名实体识别**：识别人名、地名等实体

## 面试要点

1. **Q: RNN为什么会出现梯度消失/爆炸？如何解决？**
   A: RNN反向传播时梯度要乘以权重矩阵的转置多次，导致梯度指数级衰减或增长。解决方法：使用LSTM/GRU的门控机制、梯度裁剪、跳跃连接、使用ReLU激活函数。

2. **Q: LSTM和GRU的区别？**
   A: LSTM有遗忘门、输入门、输出门和独立的细胞状态，结构复杂但表达能力强；GRU将遗忘门和输入门合并为更新门，没有独立的细胞状态，参数量少，训练更快。实践中两者效果相近，GRU稍快。

3. **Q: 双向RNN的作用？**
   A: 双向RNN同时考虑过去和未来的上下文信息。前向LSTM捕捉历史信息，后向LSTM捕捉未来信息，两者输出拼接后用于预测，在序列标注、情感分析等任务中效果显著。

4. **Q: RNN和Transformer的比较？**
   A: RNN顺序处理序列，难以并行，长距离依赖能力有限；Transformer使用自注意力机制，可并行计算，长距离依赖能力强，但计算复杂度高。Transformer已成为NLP主流，RNN在某些资源受限场景仍有优势。

## 相关概念

### AI & Data Systems
- [神经网络基础](./neural-networks.md)
- [注意力机制](./attention.md)
- [Transformer架构](./transformers.md)
- [序列到序列学习](./seq2seq.md)
- [词嵌入](./word-embeddings.md)
- [文本分类](./text-classification.md)

### 数学基础
- [线性代数](../../mathematics/linear-algebra.md)
- [微积分](../../mathematics/calculus.md)
- [随机过程](../../mathematics/stochastic-processes.md)
- [时间序列分析](../../mathematics/time-series-analysis.md)
