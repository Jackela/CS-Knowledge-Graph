# Transformer架构 (Transformer Architecture)

## 简介
Transformer是2017年由Google提出的革命性神经网络架构，完全基于注意力机制，摒弃了循环结构，实现了高效的并行计算，成为现代自然语言处理和计算机视觉的基础架构。

## 核心概念

### 整体架构
Transformer由编码器（Encoder）和解码器（Decoder）组成：
- **编码器**：将输入序列映射为连续表示，由N个相同层堆叠
- **解码器**：基于编码器输出生成目标序列，由N个相同层堆叠

### 编码器层结构
每个编码器层包含两个子层：
1. **多头自注意力**（Multi-Head Self-Attention）
2. **前馈神经网络**（Position-wise Feed-Forward Network）

每个子层后使用残差连接和层归一化：
$$Output = LayerNorm(x + Sublayer(x))$$

### 解码器层结构
每个解码器层包含三个子层：
1. **带掩码的多头自注意力**（Masked Multi-Head Self-Attention）
2. **编码器-解码器注意力**（Encoder-Decoder Attention）
3. **前馈神经网络**

### 位置编码
由于Transformer没有循环或卷积，需要注入位置信息：

**正弦位置编码**：
$$PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d_{model}})$$
$$PE_{(pos, 2i+1)} = \cos(pos / 10000^{2i/d_{model}})$$

其中 $pos$ 是位置，$i$ 是维度索引。

### 前馈神经网络
每个位置独立应用相同的全连接层：
$$FFN(x) = ReLU(xW_1 + b_1)W_2 + b_2$$

或使用GELU激活函数的现代变体。

## 实现方式

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

# ===== 位置编码 =====
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000, dropout=0.1):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # 计算位置编码
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                            (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)  # (max_len, 1, d_model)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)

# ===== Transformer模型 =====
class TransformerModel(nn.Module):
    def __init__(self, vocab_size, d_model=512, nhead=8, num_encoder_layers=6,
                 num_decoder_layers=6, dim_feedforward=2048, dropout=0.1):
        super(TransformerModel, self).__init__()
        
        self.d_model = d_model
        
        # 词嵌入
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout=dropout)
        
        # Transformer层
        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_encoder_layers,
            num_decoder_layers=num_decoder_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        
        # 输出层
        self.fc_out = nn.Linear(d_model, vocab_size)
        
        self._init_parameters()
    
    def _init_parameters(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, src, tgt, src_mask=None, tgt_mask=None,
                src_padding_mask=None, tgt_padding_mask=None):
        # 词嵌入并缩放
        src = self.embedding(src) * math.sqrt(self.d_model)
        tgt = self.embedding(tgt) * math.sqrt(self.d_model)
        
        # 添加位置编码
        src = self.pos_encoder(src.transpose(0, 1)).transpose(0, 1)
        tgt = self.pos_encoder(tgt.transpose(0, 1)).transpose(0, 1)
        
        # 生成掩码
        tgt_mask = self.generate_square_subsequent_mask(tgt.size(1)).to(tgt.device)
        
        # Transformer前向传播
        output = self.transformer(
            src, tgt,
            tgt_mask=tgt_mask,
            src_key_padding_mask=src_padding_mask,
            tgt_key_padding_mask=tgt_padding_mask
        )
        
        return self.fc_out(output)
    
    def generate_square_subsequent_mask(self, sz):
        """生成上三角掩码（防止看到未来信息）"""
        mask = torch.triu(torch.ones(sz, sz), diagonal=1)
        mask = mask.masked_fill(mask == 1, float('-inf'))
        return mask

# ===== BERT风格编码器（仅编码器） =====
class BertEncoder(nn.Module):
    def __init__(self, vocab_size, d_model=768, nhead=12, 
                 num_layers=12, dim_feedforward=3072, dropout=0.1):
        super(BertEncoder, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, dropout=dropout)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # 池化层
        self.pooler = nn.Linear(d_model, d_model)
        self.activation = nn.Tanh()
    
    def forward(self, x, attention_mask=None):
        x = self.embedding(x)
        x = self.pos_encoding(x.transpose(0, 1)).transpose(0, 1)
        
        # 转换mask格式
        if attention_mask is not None:
            attention_mask = (attention_mask == 0)
        
        encoded = self.encoder(x, src_key_padding_mask=attention_mask)
        
        # 取[CLS] token的表示
        pooled = self.activation(self.pooler(encoded[:, 0]))
        
        return encoded, pooled

# ===== 测试 =====
vocab_size = 10000
batch_size = 4
src_len = 32
tgt_len = 32

model = TransformerModel(vocab_size, d_model=512, nhead=8)
src = torch.randint(0, vocab_size, (batch_size, src_len))
tgt = torch.randint(0, vocab_size, (batch_size, tgt_len))

output = model(src, tgt)
print(f"源序列形状: {src.shape}")
print(f"目标序列形状: {tgt.shape}")
print(f"输出形状: {output.shape}")
print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")
```

## 应用场景
- **机器翻译**：Google翻译、DeepL等核心架构
- **预训练语言模型**：BERT（双向编码）、GPT（单向解码）
- **文本生成**：ChatGPT、Claude等对话系统
- **计算机视觉**：ViT（视觉Transformer）、DETR（目标检测）
- **语音识别**：Whisper、语音合成
- **多模态学习**：CLIP、DALL-E图文理解

## 面试要点

1. **Q: Transformer相比RNN的优势？**
   A: 1) 可完全并行计算，训练速度快；2) 长距离依赖能力强（任意两个位置直接交互）；3) 多头注意力提供多视角表示；4) 更容易扩展和优化。

2. **Q: 为什么Transformer需要位置编码？**
   A: 自注意力机制本身对序列位置不敏感（置换不变性），而序列顺序对理解语义至关重要。位置编码为每个位置提供唯一标识，使模型能区分不同位置的相同词。

3. **Q: 编码器和解码器的注意力有什么区别？**
   A: 编码器使用双向自注意力，所有位置可相互关注；解码器有两层注意力：带掩码的自注意力（只关注已生成的位置）和交叉注意力（关注编码器输出）。

4. **Q: Transformer的复杂度是多少？有什么优化方法？**
   A: 自注意力复杂度O(n²d)，n为序列长度。优化方法：稀疏注意力、线性注意力、局部窗口注意力、SwiGLU激活、RoPE相对位置编码、混合专家模型(MoE)。

## 相关概念

### AI & Data Systems
- [注意力机制](./attention.md)
- [BERT](./bert.md)
- [GPT](./gpt.md)
- [循环神经网络](./rnn.md)
- [视觉Transformer](./vision-transformer.md)
- [大语言模型](./llm.md)

### 数学基础
- [线性代数](../../mathematics/linear-algebra.md)
- [最优化方法](../../mathematics/optimization.md)
- [信息论](../../mathematics/information-theory.md)
- [概率图模型](../../mathematics/probabilistic-graphical-models.md)
