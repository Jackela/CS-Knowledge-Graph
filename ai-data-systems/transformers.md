# Transformer

## 简介

**Transformer** 是一种基于自注意力机制（Self-Attention）的深度学习架构，由Vaswani等人在2017年论文《Attention Is All You Need》中提出。Transformer彻底改变了自然语言处理领域，成为GPT、BERT等大语言模型的基础架构。

```
┌─────────────────────────────────────────────────────────────┐
│              Transformer 核心创新                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   RNN/LSTM:                   Transformer:                   │
│                                                             │
│   序列处理，逐步计算            并行计算，全局依赖              │
│                                                             │
│   x₁→x₂→x₃→x₄                x₁  x₂  x₃  x₄                │
│   │  │  │  │                  │  │  │  │                    │
│   ▼  ▼  ▼  ▼                  ▼  ▼  ▼  ▼                    │
│   ○→○→○→○                    ○  ○  ○  ○                    │
│   │  │  │  │                  │  │  │  │                    │
│   ▼  ▼  ▼  ▼                  ▼  ▼  ▼  ▼                    │
│   y₁ y₂ y₃ y₄                y₁ y₂ y₃ y₄                   │
│                                                             │
│   O(n) 串行                   O(1) 并行（自注意力）           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 整体架构

```
Transformer 完整架构：

输入                                    输出
  │                                       ▲
  ▼                                       │
┌─────────────┐                    ┌─────────────┐
│  Input      │                    │  Output     │
│  Embedding  │                    │  Embedding  │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       ▼                                  ▼
┌─────────────┐                    ┌─────────────┐
│ Positional  │                    │ Positional  │
│ Encoding    │                    │ Encoding    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       ▼                                  ▼
┌─────────────────────────┐        ┌─────────────────────────┐
│                         │        │      Decoder            │
│      Encoder            │        │  ┌─────────────────┐    │
│  ┌─────────────────┐    │        │  │ Masked Multi-Head │   │
│  │  Multi-Head     │    │        │  │ Self-Attention    │   │
│  │  Self-Attention │    │        │  └────────┬────────┘    │
│  └────────┬────────┘    │        │           │              │
│           │             │        │           ▼              │
│           ▼             │        │  ┌─────────────────┐    │
│  ┌─────────────────┐    │        │  │ Multi-Head       │    │
│  │  Add & Norm     │    │        │  │ Cross-Attention  │◀───┼── 编码器输出
│  └────────┬────────┘    │        │  └────────┬────────┘    │
│           │             │        │           │              │
│           ▼             │        │           ▼              │
│  ┌─────────────────┐    │        │  ┌─────────────────┐    │
│  │  Feed Forward   │    │        │  │ Feed Forward    │    │
│  └────────┬────────┘    │        │  └────────┬────────┘    │
│           │             │        │           │              │
│           ▼             │        │           ▼              │
│  ┌─────────────────┐    │        │  ┌─────────────────┐    │
│  │  Add & Norm     │    │        │  │ Add & Norm      │    │
│  └─────────────────┘    │        │  └─────────────────┘    │
│         × N 层          │        │         × N 层          │
└─────────────────────────┘        └─────────────────────────┘
              │                                  │
              └────────────────┬─────────────────┘
                               ▼
                        ┌─────────────┐
                        │ Linear +    │
                        │ Softmax     │
                        └─────────────┘
```

## 核心组件

### 1. 自注意力机制 (Self-Attention)

```
自注意力计算过程：

输入: X (序列长度 × 维度)

     X                    X                    X
     │                    │                    │
     ▼                    ▼                    ▼
┌─────────┐         ┌─────────┐         ┌─────────┐
│ W_Q     │         │ W_K     │         │ W_V     │
└────┬────┘         └────┬────┘         └────┬────┘
     │                    │                    │
     ▼                    ▼                    ▼
     Q                    K                    V
   (Query)              (Key)               (Value)

注意力分数计算：
Attention(Q, K, V) = softmax(QK^T / √d_k) · V

其中：
- QK^T: 计算Query和Key的相似度
- √d_k: 缩放因子，防止softmax梯度消失
- softmax: 转换为概率分布
- ·V: 加权求和Value
```

#### 注意力计算示例

```python
import torch
import torch.nn as nn
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q, K, V: (batch, seq_len, d_k)
    """
    d_k = Q.size(-1)
    
    # 计算注意力分数: (batch, seq_len, seq_len)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    
    # 应用mask（解码器用）
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    # Softmax归一化
    attn_weights = torch.softmax(scores, dim=-1)
    
    # 加权求和
    output = torch.matmul(attn_weights, V)
    
    return output, attn_weights

# 示例
batch_size = 2
seq_len = 4
d_k = 64

Q = torch.randn(batch_size, seq_len, d_k)
K = torch.randn(batch_size, seq_len, d_k)
V = torch.randn(batch_size, seq_len, d_k)

output, weights = scaled_dot_product_attention(Q, K, V)
print(f"输出形状: {output.shape}")  # [2, 4, 64]
print(f"注意力权重形状: {weights.shape}")  # [2, 4, 4]
```

### 2. 多头注意力 (Multi-Head Attention)

```
多头注意力：并行计算多组注意力

输入 X
  │
  ├──▶ Head 1: Q₁K₁V₁ ──▶ Attention₁ ──┐
  │                                      │
  ├──▶ Head 2: Q₂K₂V₂ ──▶ Attention₂ ──┤
  │                                      ├──▶ Concat ──▶ Linear ──▶ 输出
  ├──▶ Head 3: Q₃K₃V₃ ──▶ Attention₃ ──┤
  │                                      │
  └──▶ Head h: QₕKₕVₕ ──▶ Attentionₕ ──┘

优势：
- 不同头关注不同方面的信息
- 增强模型表达能力
- 类似CNN的多通道

数学表达：
MultiHead(Q, K, V) = Concat(head₁, ..., headₕ)W^O
where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)
    
    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)
        
        # 线性变换并分头: (batch, seq, heads, d_k) -> (batch, heads, seq, d_k)
        Q = self.W_Q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_K(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_V(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # 计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attn = torch.softmax(scores, dim=-1)
        context = torch.matmul(attn, V)
        
        # 合并头: (batch, heads, seq, d_k) -> (batch, seq, d_model)
        context = context.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model
        )
        
        return self.W_O(context)
```

### 3. 位置编码 (Positional Encoding)

```
位置编码：为模型提供序列位置信息

Transformer没有递归或卷积，需要显式注入位置信息。

正弦位置编码：
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

其中：
- pos: 位置
- i: 维度索引
- d_model: 模型维度

可视化：
位置 ↓
  0 │████████████████████
  1 │██████████████████░░
  2 │█████████████████░░░
  3 │████████████████░░░░
  4 │███████████████░░░░░
    └─────────────────────▶ 维度
    
特点：
- 每个位置有唯一编码
- 可以处理任意长度序列
- 相对位置可通过线性变换得到
```

```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * 
            (-math.log(10000.0) / d_model)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        self.register_buffer('pe', pe.unsqueeze(0))
    
    def forward(self, x):
        return x + self.pe[:, :x.size(1)]
```

### 4. 前馈网络 (Feed Forward Network)

```
位置前馈网络：

FFN(x) = max(0, xW₁ + b₁)W₂ + b₂
       = ReLU(xW₁ + b₁)W₂ + b₂

或者使用GELU激活（BERT等）：
GELU(x) = x · Φ(x)  # Φ是标准正态分布的CDF

结构：
x ──▶ Linear ──▶ ReLU/GELU ──▶ Linear ──▶ 输出
     (d_model      (d_ff)           (d_model)
      -> d_ff)                       -> d_model)

d_ff 通常 = 4 × d_model
```

```python
class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()  # 或 nn.ReLU()
    
    def forward(self, x):
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        return x
```

### 5. 层归一化 (Layer Normalization)

```
层归一化：稳定训练，加速收敛

LayerNorm(x) = γ · (x - μ) / √(σ² + ε) + β

其中：
- μ: 均值
- σ: 标准差
- γ, β: 可学习参数
- ε: 数值稳定性常数

与Batch Norm对比：
- BN: 对batch维度归一化（不适合变长序列）
- LN: 对特征维度归一化（适合序列）

Add & Norm结构：
x ──▶ SubLayer ──┐
│                ├──▶ (+) ──▶ LayerNorm ──▶ 输出
└────────────────┘
（残差连接 + 层归一化）
```

## 编码器 (Encoder)

```python
class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # 自注意力子层
        attn_out = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))
        
        # 前馈子层
        ff_out = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_out))
        
        return x

class TransformerEncoder(nn.Module):
    def __init__(self, num_layers, d_model, num_heads, d_ff, vocab_size, max_len):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len)
        self.layers = nn.ModuleList([
            TransformerEncoderLayer(d_model, num_heads, d_ff)
            for _ in range(num_layers)
        ])
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, x, mask=None):
        x = self.embedding(x)
        x = self.pos_encoding(x)
        x = self.dropout(x)
        
        for layer in self.layers:
            x = layer(x, mask)
        
        return x
```

## 解码器 (Decoder)

### Masked Self-Attention

```
解码器自注意力需要mask，防止看到未来信息：

注意力矩阵（无mask）：      注意力矩阵（有mask）：
                          
    我  爱  北京  天安门       我  爱  北京  天安门
我  ●   ●   ●    ●        我  ●   ✕   ✕    ✕
爱  ●   ●   ●    ●        爱  ●   ●   ✕    ✕
北京 ●   ●   ●    ●        北京 ●   ●   ●    ✕
天安门●   ●   ●    ●        天安门●   ●   ●    ●

Mask是一个上三角为0的矩阵，确保位置i只能看到≤i的位置
```

```python
class TransformerDecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads)
        self.cross_attn = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, encoder_output, src_mask=None, tgt_mask=None):
        # Masked Self-Attention
        attn_out = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn_out))
        
        # Cross-Attention (编码器-解码器注意力)
        attn_out = self.cross_attn(
            x, encoder_output, encoder_output, src_mask
        )
        x = self.norm2(x + self.dropout(attn_out))
        
        # Feed Forward
        ff_out = self.feed_forward(x)
        x = self.norm3(x + self.dropout(ff_out))
        
        return x
```

## 完整Transformer

```python
class Transformer(nn.Module):
    def __init__(self, src_vocab_size, tgt_vocab_size, 
                 d_model=512, num_heads=8, num_layers=6, 
                 d_ff=2048, max_len=5000, dropout=0.1):
        super().__init__()
        
        self.encoder = TransformerEncoder(
            num_layers, d_model, num_heads, d_ff, 
            src_vocab_size, max_len
        )
        self.decoder = TransformerDecoder(
            num_layers, d_model, num_heads, d_ff,
            tgt_vocab_size, max_len
        )
        self.linear = nn.Linear(d_model, tgt_vocab_size)
    
    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        encoder_output = self.encoder(src, src_mask)
        decoder_output = self.decoder(tgt, encoder_output, src_mask, tgt_mask)
        output = self.linear(decoder_output)
        return output
    
    def generate_mask(self, src, tgt):
        # Source mask (padding mask)
        src_mask = (src != 0).unsqueeze(1).unsqueeze(2)
        
        # Target mask (padding + look-ahead)
        tgt_pad_mask = (tgt != 0).unsqueeze(1).unsqueeze(3)
        tgt_len = tgt.size(1)
        tgt_look_ahead = torch.tril(
            torch.ones(tgt_len, tgt_len)
        ).bool().to(tgt.device)
        tgt_mask = tgt_pad_mask & tgt_look_ahead
        
        return src_mask, tgt_mask
```

## Transformer变体

### BERT (Encoder-only)

```
BERT: 双向编码器表示

架构：只使用Transformer Encoder

预训练任务：
1. MLM (Masked Language Model)
   输入: "我 [MASK] 北京 天安门"
   预测: "爱"

2. NSP (Next Sentence Prediction)
   判断句子B是否是句子A的下一句

应用：文本分类、NER、问答、句子相似度
```

### GPT (Decoder-only)

```
GPT: 生成式预训练

架构：只使用Transformer Decoder

特点：
- 自回归生成
- 从左到右单向注意力
- 适合文本生成

GPT-1 → GPT-2 → GPT-3 → GPT-4
参数：117M → 1.5B → 175B → ?
```

### T5 (Encoder-Decoder)

```
T5: Text-to-Text Transfer Transformer

所有任务统一为文本到文本：
- 翻译: "translate English to German: Hello" → "Hallo"
- 摘要: "summarize: [article]" → [summary]
- 分类: "classify: [text]" → "positive"

采用完整的Encoder-Decoder结构
```

## 注意力可视化

```
注意力权重可视化：

输入: "The animal didn't cross the street because it was too tired"

问: "it" 指代什么？

"it" 行的注意力权重：
The:     ██░░░░░░░░░░░░░░░░░░
animal:  ██████████████████░
didn't:  ░░░░░░░░░░░░░░░░░░░░
cross:   ░░░░░░░░░░░░░░░░░░░░
the:     ░░░░░░░░░░░░░░░░░░░░
street:  ░░░░░░░░░░░░░░░░░░░░
because: ░░░░░░░░░░░░░░░░░░░░
it:      ░░░░░░░░░░░░░░░░░░░░
was:     ░░░░░░░░░░░░░░░░░░░░
too:     ░░░░░░░░░░░░░░░░░░░░
tired:   ░░░░░░░░░░░░░░░░░░░░

"it" 主要关注 "animal"，说明模型理解了指代关系
```

## 复杂度分析

| 层类型 | 复杂度 | 顺序操作 | 最大路径长度 |
|--------|--------|----------|--------------|
| Self-Attention | O(n²·d) | O(1) | O(1) |
| Recurrent | O(n·d²) | O(n) | O(n) |
| Convolutional | O(k·n·d²) | O(1) | O(logₖn) |

其中 n=序列长度, d=维度, k=卷积核大小

## 面试要点

### 常见问题

**Q1: 为什么Transformer比RNN快？**
> Transformer可以并行计算所有位置的注意力，而RNN必须顺序处理。虽然自注意力的复杂度是O(n²)，但可以充分利用GPU并行能力。

**Q2: 为什么需要多头注意力？**
> 不同的注意力头可以关注不同的信息：语法关系、语义关系、指代关系等。多头机制增强了模型的表达能力。

**Q3: 位置编码的作用是什么？**> Transformer没有内置的顺序概念，位置编码为模型提供序列中每个位置的绝对或相对位置信息，使模型能够利用顺序信息。

**Q4: 为什么需要缩放因子√d_k？**> 当d_k较大时，QK^T的点积结果会很大，导致softmax进入梯度极小的区域。缩放可以稳定梯度和训练。

**Q5: BERT和GPT的区别？**> BERT使用Encoder，双向注意力，适合理解任务；GPT使用Decoder，单向注意力，适合生成任务。BERT用MLM预训练，GPT用自回归预训练。

## 相关概念

### 机器学习基础
### 机器学习基础
- [机器学习概述](./ml-overview.md) - 机器学习基础
- [CNN](./cnn.md) - 卷积神经网络对比
- [RNN与LSTM](./rnn-lstm.md) - 循环神经网络演进
- [LLM](./llm.md) - 大语言模型

### 数学基础
- [线性代数](../mathematics/linear-algebra.md) - 注意力机制的矩阵运算

### 数据结构
- [数组](../computer-science/data-structures/array.md)：词嵌入与注意力矩阵
- [树](../computer-science/data-structures/tree.md)：语法树与结构化注意力

### 算法

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：注意力计算O(n²)复杂度

### 系统实现


## 参考资料

1. "Attention Is All You Need" - Vaswani et al. (2017)
2. "BERT: Pre-training of Deep Bidirectional Transformers"
3. "Language Models are Few-Shot Learners" (GPT-3)
4. "The Illustrated Transformer" by Jay Alammar
5. "Natural Language Processing with Transformers" by Lewis Tunstall
