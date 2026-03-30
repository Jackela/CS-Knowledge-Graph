# RNN与LSTM (Recurrent Neural Networks)

## 简介

**循环神经网络 (Recurrent Neural Network, RNN)** 是专门用于处理序列数据的神经网络架构。与传统神经网络不同，RNN具有记忆能力，能够利用先前的信息影响当前的输出。

```
┌─────────────────────────────────────────────────────────────┐
│                   RNN 核心思想                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   传统神经网络：              RNN：                          │
│                                                             │
│   输入1 ──▶ 输出1            输入1 ──▶ 输出1                │
│   输入2 ──▶ 输出2            输入2 ──▶ 输出2                │
│   输入3 ──▶ 输出3            输入3 ──▶ 输出3                │
│                                                             │
│   样本独立                   样本间有依赖关系                 │
│                                                             │
│   RNN通过隐藏状态传递信息：                                  │
│   h_t = f(h_{t-1}, x_t)                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## RNN基本结构

### 展开图

```
RNN展开（时间步展开）：

        x₁        x₂        x₃        x₄
        │         │         │         │
        ▼         ▼         ▼         ▼
    ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
    │  RNN  │ │  RNN  │ │  RNN  │ │  RNN  │
    │ 单元  │▶│ 单元  │▶│ 单元  │▶│ 单元  │
    └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
        │         │         │         │
        ▼         ▼         ▼         ▼
        y₁        y₂        y₃        y₄
        
        ◀──────── 时间 ────────▶
        
共享参数：每个时间步使用相同的权重
```

### 数学表达

```
RNN前向传播：

隐藏状态：h_t = tanh(W_{hh} · h_{t-1} + W_{xh} · x_t + b_h)

输出：y_t = W_{hy} · h_t + b_y

其中：
- x_t: 时刻t的输入
- h_{t-1}: 上一时刻的隐藏状态
- h_t: 当前时刻的隐藏状态
- y_t: 当前时刻的输出
- W: 权重矩阵（所有时间步共享）
- b: 偏置
```

## RNN变体

### 1. 多对一 (Many-to-One)

```
应用场景：情感分析、文本分类

输入序列          输出
"这部电影很棒"  ──▶  正面

结构：
    x₁    x₂    x₃    x₄    x₅
    │     │     │     │     │
    ▼     ▼     ▼     ▼     ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ RNN │▶│ RNN │▶│ RNN │▶│ RNN │▶│ RNN │
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │       │
   └───────┴───────┴───────┴───────┘
                   │
                   ▼
                 分类结果
```

### 2. 一对多 (One-to-Many)

```
应用场景：图像描述生成

输入图片        输出序列
[图片]    ──▶  "一只猫坐在沙发上"

结构：
        x
        │
        ▼
    ┌─────┐
    │ RNN │──▶ y₁ ──▶ y₂ ──▶ y₃ ──▶ ...
    └──┬──┘
       │
       └──────┬──────┬──────┘
              │      │
            (y₁作为下一时刻输入)
```

### 3. 多对多 (Many-to-Many)

```
应用场景：机器翻译、语音识别

输入："Hello world"
输出："你好世界"

结构（Seq2Seq）：

编码器：                解码器：
x₁─▶x₂─▶x₃            y₁─▶y₂─▶y₃
│   │   │              ▲   ▲   ▲
▼   ▼   ▼              │   │   │
RNN─▶RNN─▶[context]──▶RNN─▶RNN─▶RNN
                │
              上下文向量
```

## 梯度问题

### 梯度消失与爆炸

```
RNN的梯度传播：

∂L/∂W = Σ (∂L/∂h_t) · (∂h_t/∂h_{t-1}) · ... · (∂h_1/∂W)

其中：∂h_t/∂h_{t-1} 包含 tanh'(x) · W

梯度消失：
- tanh导数 ≤ 1
- 长期依赖的信号逐渐消失
- 难以学习长距离关系

梯度爆炸：
- W > 1时，连乘导致梯度指数增长
- 参数更新过大，训练不稳定

可视化：
时间步1: 梯度 = 0.8
时间步2: 梯度 = 0.8 × 0.8 = 0.64
时间步3: 梯度 = 0.8 × 0.8 × 0.8 = 0.512
...
时间步10: 梯度 ≈ 0.1（几乎消失）
```

## LSTM (Long Short-Term Memory)

### 核心思想

LSTM通过门控机制控制信息的流动，解决梯度消失问题，能够学习长期依赖关系。

```
LSTM单元结构：

        c_{t-1} (细胞状态)
           │
           ├──▶ ⊕ ◀── 遗忘门 ───┐
           │                     │
           ├──▶ ⊕ ◀── 输入门 ───┤
           │                     │
           ▼                     │
           c_t                   │
           │                     │
           ├──▶ tanh             │
           │                     │
           ▼                     │
    ┌──────┴──────┐              │
    │   输出门    │◀─────────────┘
    └──────┬──────┘
           │
           ▼
           h_t

三个门：
- 遗忘门：决定丢弃什么信息
- 输入门：决定存储什么新信息
- 输出门：决定输出什么信息
```

### 门控机制详解

```
LSTM数学公式：

遗忘门：f_t = σ(W_f · [h_{t-1}, x_t] + b_f)
       决定从细胞状态中丢弃什么信息
       
输入门：i_t = σ(W_i · [h_{t-1}, x_t] + b_i)
       决定什么新信息存入细胞状态
       
候选状态：C̃_t = tanh(W_C · [h_{t-1}, x_t] + b_C)
       新候选值的向量
       
更新细胞状态：C_t = f_t ⊙ C_{t-1} + i_t ⊙ C̃_t
       遗忘旧信息 + 添加新信息
       
输出门：o_t = σ(W_o · [h_{t-1}, x_t] + b_o)
       
隐藏状态：h_t = o_t ⊙ tanh(C_t)
       基于细胞状态决定输出

其中：
- σ: sigmoid函数 (0-1之间)
- ⊙: 逐元素乘法
- W, b: 可学习的参数
```

### 门控作用可视化

```
遗忘门示例：

句子："我住在法国，我会说法语。"
处理到"法语"时：

细胞状态内容：
[我, 住, 法国, 会, 说] ← 需要记住"法国"

遗忘门：
[0.1, 0.1, 0.9, 0.1, 0.1] ← 保留"法国"

输入门：
[0, 0, 0, 0, 0, 0.9] ← 加入"法语"

更新后状态：
[我, 住, 法国, 会, 说, 法语]
```

## GRU (Gated Recurrent Unit)

### 简化版LSTM

```
GRU结构（两个门）：

        h_{t-1}
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
 更新门       重置门
   z_t         r_t
    │           │
    ▼           ▼
    ⊕ ◀── tanh ◀── ⊙
    │              │
    │              └── (r_t ⊙ h_{t-1})
    │
    └──▶ h_t

GRU公式：
z_t = σ(W_z · [h_{t-1}, x_t])
r_t = σ(W_r · [h_{t-1}, x_t])
h̃_t = tanh(W · [r_t ⊙ h_{t-1}, x_t])
h_t = (1 - z_t) ⊙ h_{t-1} + z_t ⊙ h̃_t

与LSTM对比：
- 合并细胞状态和隐藏状态
- 只有更新门和重置门
- 参数更少，训练更快
- 效果与LSTM相近
```

## PyTorch实现

### 基础RNN

```python
import torch
import torch.nn as nn

class BasicRNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(BasicRNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # RNN层
        self.rnn = nn.RNN(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,  # 输入格式: (batch, seq, feature)
            nonlinearity='tanh'
        )
        
        # 全连接层
        self.fc = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        # 初始化隐藏状态
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # 前向传播
        out, _ = self.rnn(x, h0)  # out: (batch, seq, hidden)
        
        # 取最后一个时间步
        out = out[:, -1, :]
        
        # 分类
        out = self.fc(out)
        return out
```

### LSTM实现

```python
class LSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_size, num_classes):
        super(LSTMClassifier, self).__init__()
        
        # 词嵌入层
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # LSTM层
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_size,
            num_layers=2,
            batch_first=True,
            dropout=0.5,  # 多层时使用
            bidirectional=True  # 双向LSTM
        )
        
        # 双向LSTM，隐藏状态维度×2
        self.fc = nn.Linear(hidden_size * 2, num_classes)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        # x: (batch, seq_len)
        
        # 嵌入: (batch, seq_len, embed_dim)
        embedded = self.dropout(self.embedding(x))
        
        # LSTM: (batch, seq_len, hidden*2)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # 双向：拼接两个方向的最后一层隐藏状态
        # hidden: (num_layers*2, batch, hidden)
        hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        
        # 分类
        out = self.fc(self.dropout(hidden))
        return out
```

### GRU实现

```python
class GRUClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(GRUClassifier, self).__init__()
        
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3
        )
        
        self.fc = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.gru(x, h0)
        out = self.fc(out[:, -1, :])
        return out
```

## 双向RNN

```
双向RNN结构：

输入序列: x₁ → x₂ → x₃ → x₄

正向LSTM: ──▶ ──▶ ──▶ ──▶
          h₁  h₂  h₃  h₄

反向LSTM: ◀── ◀── ◀── ◀──
          h'₄ h'₃ h'₂ h'₁

          │   │   │   │
          ▼   ▼   ▼   ▼
        [h₁;h'₁] ... [h₄;h'₄]  # 拼接

优势：同时利用过去和未来的上下文信息
应用：命名实体识别、语音识别
```

## 应用案例

### 情感分析

```python
# 情感分析完整示例
import torch
from torchtext.data import Field, LabelField, TabularDataset, BucketIterator

# 定义字段
TEXT = Field(tokenize='spacy', lower=True, include_lengths=True)
LABEL = LabelField(dtype=torch.float)

# 加载数据
train_data, test_data = TabularDataset.splits(
    path='data',
    train='train.csv',
    test='test.csv',
    format='csv',
    fields=[('text', TEXT), ('label', LABEL)]
)

# 构建词表
TEXT.build_vocab(train_data, max_size=25000, vectors="glove.6B.100d")
LABEL.build_vocab(train_data)

# 创建模型
class SentimentLSTM(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=2, 
                           bidirectional=True, dropout=0.5)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)
        
    def forward(self, text, text_lengths):
        embedded = self.embedding(text)
        packed = nn.utils.rnn.pack_padded_sequence(embedded, text_lengths)
        packed_output, (hidden, cell) = self.lstm(packed)
        hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        return self.fc(hidden)

# 训练
model = SentimentLSTM(len(TEXT.vocab), 100, 256, 1)
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.BCEWithLogitsLoss()
```

### 文本生成

```python
# 字符级文本生成
class CharRNN(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super().__init__()
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        if hidden is None:
            lstm_out, hidden = self.lstm(embedded)
        else:
            lstm_out, hidden = self.lstm(embedded, hidden)
        output = self.fc(lstm_out)
        return output, hidden
    
    def generate(self, start_str, char2idx, idx2char, length=200):
        self.eval()
        input_eval = torch.tensor([char2idx[c] for c in start_str])
        hidden = None
        
        generated = list(start_str)
        
        with torch.no_grad():
            # 预热隐藏状态
            for i in range(len(start_str) - 1):
                _, hidden = self.forward(
                    input_eval[i:i+1].unsqueeze(0), hidden
                )
            
            input_eval = input_eval[-1:].unsqueeze(0)
            
            for _ in range(length):
                output, hidden = self.forward(input_eval, hidden)
                probs = torch.softmax(output.squeeze(), dim=0)
                next_char_idx = torch.multinomial(probs, 1).item()
                generated.append(idx2char[next_char_idx])
                input_eval = torch.tensor([[next_char_idx]])
        
        return ''.join(generated)
```

## 面试要点

### 常见问题

**Q1: RNN与CNN的区别？**
> RNN适合序列数据，有记忆能力，参数共享在时间维度；CNN适合网格数据（图像），参数共享在空间维度，无记忆能力。

**Q2: LSTM如何解决梯度消失？**
> LSTM通过细胞状态和门控机制，允许信息在细胞状态中不变地传递（加法更新而非乘法），避免了梯度在反向传播时的指数级衰减或增长。

**Q3: LSTM和GRU的区别？**> LSTM有三个门（遗忘、输入、输出），细胞状态和隐藏状态分离；GRU有两个门（更新、重置），合并了细胞状态和隐藏状态。GRU参数更少，训练更快，效果相近。

**Q4: 双向RNN的优势和局限？**> 优势：利用前后文信息，提高理解准确性。局限：需要完整序列才能处理，不适用于实时流式数据；参数量翻倍。

**Q5: 为什么使用tanh和sigmoid作为激活函数？**> tanh输出范围(-1,1)，均值为0，有利于梯度传播；sigmoid输出(0,1)，适合门控机制（表示比例）。两者导数在0附近较大，避免梯度消失。

## 相关概念

- [机器学习概述](./ml-overview.md) - 机器学习基础
- [CNN](./cnn.md) - 卷积神经网络
- [Transformer](./transformers.md) - 注意力机制模型

## 参考资料

1. "Deep Learning" by Goodfellow et al.
2. "Understanding LSTM Networks" by Christopher Olah
3. Original LSTM paper: Hochreiter & Schmidhuber (1997)
4. GRU paper: Cho et al. (2014)
5. PyTorch RNN文档
