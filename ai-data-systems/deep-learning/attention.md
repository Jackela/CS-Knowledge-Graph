# 注意力机制 (Attention Mechanism)

## 简介
注意力机制是深度学习中一种让模型动态关注输入序列不同部分的技术，通过计算查询（Query）与键（Key）的相似度来分配权重，显著提升了序列建模能力，是现代NLP和视觉模型的核心组件。

## 核心概念

### 注意力基本思想
给定查询 $q$ 和一组键值对 $\{(k_1, v_1), ..., (k_n, v_n)\}$，计算注意力输出：

$$Attention(q, K, V) = \sum_{i=1}^{n} \alpha_i v_i$$

其中 $\alpha_i$ 是注意力权重，表示对第 $i$ 个值的关注程度。

### 注意力权重计算
**加性注意力**：$score(q, k) = w^T \tanh(W_q q + W_k k)$

**点积注意力**：$score(q, k) = q^T k$

**缩放点积注意力**：$score(q, k) = \frac{q^T k}{\sqrt{d_k}}$

权重通过softmax归一化：

$$\alpha_i = \frac{\exp(score(q, k_i))}{\sum_{j} \exp(score(q, k_j))}$$

### 自注意力（Self-Attention）
Query、Key、Value来自同一输入序列的不同线性变换：

$$Attention(Q, K, V) = softmax(\frac{QK^T}{\sqrt{d_k}})V$$

其中：
- $Q = XW^Q$（查询矩阵）
- $K = XW^K$（键矩阵）
- $V = XW^V$（值矩阵）

### 多头注意力（Multi-Head Attention）
并行计算多组注意力，捕捉不同子空间的信息：

$$MultiHead(Q, K, V) = Concat(head_1, ..., head_h)W^O$$

$$head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)$$

### 注意力类型
- **Soft Attention**：可微分，权重连续分布
- **Hard Attention**：不可微分，只关注一个位置
- **Local Attention**：只关注查询位置附近的窗口
- **Global Attention**：关注整个序列

## 实现方式

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

# ===== 缩放点积注意力 =====
class ScaledDotProductAttention(nn.Module):
    def __init__(self, dropout=0.1):
        super(ScaledDotProductAttention, self).__init__()
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, Q, K, V, mask=None):
        """
        Q, K, V: (batch_size, num_heads, seq_len, d_k)
        """
        d_k = Q.size(-1)
        
        # 计算注意力分数: Q @ K^T / sqrt(d_k)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
        
        # 应用mask（可选）
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        # Softmax归一化
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # 加权求和
        output = torch.matmul(attn_weights, V)
        
        return output, attn_weights

# ===== 多头注意力 =====
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads, dropout=0.1):
        super(MultiHeadAttention, self).__init__()
        assert d_model % num_heads == 0, "d_model必须能被num_heads整除"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # 线性投影层
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)
        
        self.attention = ScaledDotProductAttention(dropout)
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)
    
    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)
        
        # 线性投影并分头
        # (batch_size, seq_len, d_model) -> (batch_size, num_heads, seq_len, d_k)
        Q = self.W_Q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_K(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_V(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # 计算注意力
        attn_output, attn_weights = self.attention(Q, K, V, mask)
        
        # 拼接多头
        # (batch_size, num_heads, seq_len, d_k) -> (batch_size, seq_len, d_model)
        attn_output = attn_output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model)
        
        # 最终线性变换
        output = self.W_O(attn_output)
        output = self.dropout(output)
        
        return output, attn_weights

# ===== 简化版注意力（用于理解） =====
class SimpleAttention(nn.Module):
    def __init__(self, hidden_size):
        super(SimpleAttention, self).__init__()
        self.hidden_size = hidden_size
        self.attn = nn.Linear(hidden_size * 2, hidden_size)
        self.v = nn.Parameter(torch.rand(hidden_size))
        
    def forward(self, hidden, encoder_outputs):
        """
        hidden: (batch_size, hidden_size) - 解码器当前状态
        encoder_outputs: (batch_size, seq_len, hidden_size) - 编码器所有输出
        """
        seq_len = encoder_outputs.size(1)
        batch_size = encoder_outputs.size(0)
        
        # 重复hidden以匹配encoder_outputs
        hidden = hidden.unsqueeze(1).repeat(1, seq_len, 1)
        
        # 计算能量分数
        energy = torch.tanh(self.attn(torch.cat((hidden, encoder_outputs), dim=2)))
        
        # 计算注意力权重
        energy = energy.permute(0, 2, 1)  # (batch_size, hidden_size, seq_len)
        v = self.v.repeat(batch_size, 1).unsqueeze(1)  # (batch_size, 1, hidden_size)
        attn_weights = torch.bmm(v, energy).squeeze(1)  # (batch_size, seq_len)
        
        return F.softmax(attn_weights, dim=1)

# ===== 测试 =====
batch_size = 2
seq_len = 10
d_model = 512
num_heads = 8

# 创建输入
x = torch.randn(batch_size, seq_len, d_model)

# 多头注意力
mha = MultiHeadAttention(d_model, num_heads)
output, weights = mha(x, x, x)

print(f"输入形状: {x.shape}")
print(f"输出形状: {output.shape}")
print(f"注意力权重形状: {weights.shape}")
print(f"参数量: {sum(p.numel() for p in mha.parameters()):,}")
```

## 应用场景
- **机器翻译**：关注源语言中与当前翻译相关的词
- **文本摘要**：识别原文中的关键信息
- **图像描述生成**：关注图像的相关区域
- **语音识别**：对齐音频帧与文字
- **Transformer模型**：BERT、GPT等核心组件
- **计算机视觉**：视觉Transformer(ViT)、DETR

## 面试要点

1. **Q: 为什么需要缩放点积注意力（除以√d_k）？**
   A: 当d_k较大时，点积值会变得很大，导致softmax函数进入梯度很小的饱和区。缩放因子√d_k将方差控制在1左右，避免梯度消失，加速收敛。

2. **Q: 自注意力机制和注意力机制的区别？**
   A: 注意力机制中Q、K、V通常来自不同来源（如解码器Query，编码器Key/Value）；自注意力中Q、K、V都来自同一序列，计算序列中每个位置与其他所有位置的依赖关系。

3. **Q: 多头注意力的作用是什么？**
   A: 多头机制允许模型同时关注来自不同表示子空间的信息。不同头可以学习不同类型的依赖关系（如语法关系、指代关系、语义关系等），增强模型表达能力。

4. **Q: 注意力机制的时间复杂度？如何优化？**
   A: 标准自注意力是O(n²d)，n为序列长度。优化方法：稀疏注意力（Sparse Attention）、线性注意力（Linear Attention）、局部窗口注意力、Flash Attention优化内存访问。

## 相关概念

### AI & Data Systems
- [Transformer架构](./transformers.md)
- [循环神经网络](./rnn.md)
- [BERT](./bert.md)
- [GPT](./gpt.md)
- [视觉Transformer](./vision-transformer.md)
- [序列到序列学习](./seq2seq.md)

### 数学基础
- [线性代数](../../mathematics/linear-algebra.md)
- [概率论与统计](../../mathematics/probability-statistics.md)
- [信息论](../../mathematics/information-theory.md)
- [矩阵分解](../../mathematics/matrix-decomposition.md)
