# 模型微调 (Fine-tuning)

## 简介
**模型微调 (Fine-tuning)** 是在预训练大语言模型的基础上，使用特定领域或任务的数据进行进一步训练，使模型适应特定应用场景的技术。相比提示工程，微调能深度改变模型行为，实现更稳定的领域专业化。

## 核心概念

### 1. 微调范式对比
```
┌─────────────────────────────────────────────────────────────┐
│                   微调方法对比                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  全量微调 (Full Fine-tuning)                                 │
│  ├── 更新所有参数                                            │
│  ├── 效果最好但计算成本高                                      │
│  ├── 需要大量显存和训练数据                                    │
│  └── 适用：充足资源、核心模型                                 │
│                                                             │
│  参数高效微调 (PEFT)                                         │
│  ├── LoRA: 低秩适配，冻结原参数，训练低秩矩阵                  │
│  ├── Prefix Tuning: 训练前缀嵌入                             │
│  ├── Prompt Tuning: 训练软提示                                │
│  └── 适用：资源受限、快速迭代                                 │
│                                                             │
│  指令微调 (Instruction Tuning)                               │
│  ├── 使用(指令, 输出)对训练                                  │
│  ├── 提升指令遵循能力                                        │
│  └── 适用：构建Chat模型                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. LoRA (Low-Rank Adaptation) 原理
```
原始权重: W ∈ R^(d×k)
微调更新: W' = W + ΔW

LoRA核心思想:
ΔW = BA, 其中 B ∈ R^(d×r), A ∈ R^(r×k), r << min(d,k)

训练时: 冻结W，只训练A和B
推理时: W' = W + BA (可合并，无额外推理成本)

参数节省: (d×k) vs (d×r + r×k)
例: d=4096, k=4096, r=16
全量: 16,777,216 参数
LoRA: 131,072 参数 (节省99.2%)
```

### 3. 数据准备要点
| 维度 | 要求 | 示例 |
|------|------|------|
| 质量 | 准确、无噪声、一致性 | 人工审核或高质量来源 |
| 多样性 | 覆盖各种场景和边界情况 | 正例、反例、边界例 |
| 格式 | 统一结构化格式 | JSON、JSONL |
| 规模 | 通常1000-10000条 | 质量>数量 |
| 分布 | 与推理场景一致 | 避免训练-推理分布偏移 |

## 实现方式

```python
# LoRA微调实现示例
import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset


class LLMFineTuner:
    """LLM微调器 - 支持LoRA和全量微调"""
    
    def __init__(self, model_name: str, use_lora: bool = True):
        self.model_name = model_name
        self.use_lora = use_lora
        self.model = None
        self.tokenizer = None
        
    def load_base_model(self, load_in_8bit: bool = False):
        """加载基础模型"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            load_in_8bit=load_in_8bit
        )
        
    def setup_lora(self, r: int = 16, lora_alpha: int = 32, lora_dropout: float = 0.05):
        """配置LoRA"""
        if not self.use_lora:
            return
            
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        )
        
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
    def prepare_data(self, data: list) -> Dataset:
        """准备训练数据
        
        Args:
            data: [{"instruction": "...", "input": "...", "output": "..."}]
        """
        def format_prompt(example):
            if example["input"]:
                prompt = f"### 指令:\n{example['instruction']}\n\n### 输入:\n{example['input']}\n\n### 回答:\n{example['output']}"
            else:
                prompt = f"### 指令:\n{example['instruction']}\n\n### 回答:\n{example['output']}"
            return {"text": prompt}
        
        dataset = Dataset.from_list(data)
        dataset = dataset.map(format_prompt)
        
        def tokenize(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=512,
                padding="max_length"
            )
        
        return dataset.map(tokenize, batched=True)
    
    def train(
        self,
        train_dataset: Dataset,
        output_dir: str,
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4
    ):
        """执行训练"""
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            learning_rate=learning_rate,
            fp16=True,
            logging_steps=10,
            save_strategy="epoch",
            warmup_ratio=0.1,
            lr_scheduler_type="cosine",
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=lambda x: {"input_ids": torch.stack([torch.tensor(d["input_ids"]) for d in x]),
                                    "attention_mask": torch.stack([torch.tensor(d["attention_mask"]) for d in x]),
                                    "labels": torch.stack([torch.tensor(d["input_ids"]) for d in x])}
        )
        
        trainer.train()
        
        # 保存模型
        if self.use_lora:
            self.model.save_pretrained(output_dir)
        else:
            self.model.save_pretrained(output_dir)
            self.tokenizer.save_pretrained(output_dir)


# 使用示例
training_data = [
    {
        "instruction": "将以下中文翻译成英文",
        "input": "人工智能正在改变世界",
        "output": "Artificial intelligence is changing the world."
    },
    {
        "instruction": "总结以下内容",
        "input": "微服务架构是一种将应用程序构建为一组小型服务的方法...",
        "output": "微服务架构将应用拆分为独立部署的小型服务。"
    },
]

# 初始化并训练
# tuner = LLMFineTuner("meta-llama/Llama-2-7b-hf", use_lora=True)
# tuner.load_base_model(load_in_8bit=True)
# tuner.setup_lora(r=16)
# dataset = tuner.prepare_data(training_data)
# tuner.train(dataset, "./output", num_epochs=3)


# 推理示例
class FineTunedInference:
    """微调后模型推理"""
    
    def __init__(self, model_path: str, base_model: str = None):
        from peft import PeftModel
        
        self.tokenizer = AutoTokenizer.from_pretrained(base_model or model_path)
        base = AutoModelForCausalLM.from_pretrained(
            base_model or model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        if base_model:
            self.model = PeftModel.from_pretrained(base, model_path)
            self.model = self.model.merge_and_unload()  # 合并权重
        else:
            self.model = base
    
    def generate(self, prompt: str, max_length: int = 200) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## 应用场景

- **领域专业化**: 医疗、法律、金融等专业领域问答模型
- **代码生成**: 针对特定编程语言或框架的代码助手
- **风格迁移**: 调整模型输出风格（正式、幽默、简洁）
- **功能增强**: 增加特定能力如结构化输出、工具调用
- **多语言优化**: 提升对特定语言的理解和生成能力

## 面试要点

1. **Q: LoRA为什么能减少可训练参数?**  
   A: LoRA假设权重更新的低秩结构，用两个小矩阵BA近似大矩阵ΔW。参数量从d×k降为(d×r + r×k)，r通常16-64，远小于d和k。

2. **Q: 全量微调和LoRA的适用场景差异?**  
   A: 全量微调适合资源丰富、追求最佳效果的核心模型；LoRA适合快速迭代、多任务适配、资源受限场景。LoRA可训练多个适配器灵活切换。

3. **Q: 微调时如何选择学习率?**  
   A: LoRA通常2e-4到1e-3，全量微调通常1e-5到5e-5。使用warmup逐步增大，cosine衰减。太大导致灾难性遗忘，太小收敛慢。

4. **Q: 什么是灾难性遗忘，如何缓解?**  
   A: 灾难性遗忘指微调后模型丢失通用能力。缓解：1) 使用LoRA冻结原参数 2) 保留通用能力的混合数据 3) 控制学习率和epoch 4) 正则化约束。

5. **Q: 如何评估微调效果?**  
   A: 1) 目标任务指标（准确率、BLEU等）2) 通用能力保持测试 3) 人工评估输出质量 4) 对比基线模型 5) A/B测试真实业务指标。

## 相关概念

### AI & Data Systems
- [大语言模型](../llm.md) - 微调的基础模型
- [RLHF](./rlhf.md) - 强化学习微调方法
- [提示工程](./prompt-engineering.md) - 与微调的协同策略
- [模型部署](../mlops/model-deployment.md) - 微调模型的部署上线

### 系统实现
- [GPU架构](../../computer-science/architecture/cpu-architecture.md) - 训练硬件基础
- [分布式训练](../../computer-science/systems/process.md) - 大规模训练并行化
- [Docker](../../cloud-devops/docker.md) - 训练环境容器化
