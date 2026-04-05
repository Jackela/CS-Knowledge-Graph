# 人类反馈强化学习 (Reinforcement Learning from Human Feedback, RLHF)

## 简介
**RLHF (Reinforcement Learning from Human Feedback)** 是一种将人类偏好融入大语言模型训练的技术，通过强化学习优化模型输出以符合人类价值观和期望。它是ChatGPT、Claude等对话模型对齐人类意图的核心技术。

## 核心概念

### 1. RLHF三阶段流程
```
┌─────────────────────────────────────────────────────────────┐
│                   RLHF 三阶段训练流程                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  阶段1: 监督微调 (SFT)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  输入: 高质量人工编写的(指令, 回答)数据                │   │
│  │  目标: 让模型学习基本的指令遵循能力                    │   │
│  │  输出: SFT模型 (Supervised Fine-Tuned Model)        │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  阶段2: 奖励模型训练 (Reward Model)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  输入: 同一提示的多个回答 + 人类偏好排序               │   │
│  │  目标: 学习预测人类偏好得分                            │   │
│  │  输出: Reward Model (偏好预测器)                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  阶段3: 强化学习优化 (PPO/RL)                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  策略: 当前语言模型 (生成回答)                         │   │
│  │  奖励: Reward Model + KL惩罚 (防止偏离太远)           │   │
│  │  目标: 最大化期望奖励                                  │   │
│  │  输出: RLHF对齐模型                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 奖励模型原理
```
输入: 提示(prompt) x，模型回答 y
输出: 标量奖励值 r(x, y) ∈ ℝ

训练数据: (x, y_win, y_lose) - 人类偏好y_win胜过y_lose

损失函数 (Bradley-Terry模型):
L = -E[log σ(r(x, y_win) - r(x, y_lose))]

目标: 让奖励模型学会预测人类偏好的相对排序
```

### 3. PPO算法要点
| 组件 | 说明 |
|------|------|
| 策略网络 (Policy) | 当前语言模型，生成token概率分布 |
| 价值网络 (Value) | 估计状态价值，减少方差 |
| 参考模型 (Reference) | SFT模型，用于计算KL散度惩罚 |
| 奖励模型 (Reward) | 预训练好的偏好预测器 |
| KL惩罚 | 防止策略偏离参考模型太远 |

### 4. RLHF变体
- **DPO (Direct Preference Optimization)**: 直接优化偏好，无需显式奖励模型
- **KTO (Kahneman-Tversky Optimization)**: 基于是否"更好"的二元反馈
- **RLAIF**: 用AI代替人类进行偏好标注，降低成本
- **Constitutional AI**: Claude使用的方法，通过原则自我批评

## 实现方式

```python
# RLHF核心组件示意
import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer


class RewardModel(nn.Module):
    """奖励模型: 预测人类偏好得分"""
    
    def __init__(self, base_model_name: str):
        super().__init__()
        self.base = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16
        )
        # 添加奖励头
        self.reward_head = nn.Linear(self.base.config.hidden_size, 1)
        
    def forward(self, input_ids, attention_mask):
        """返回奖励分数"""
        outputs = self.base.transformer(input_ids, attention_mask=attention_mask)
        hidden = outputs.last_hidden_state[:, -1, :]  # 取最后一个token
        reward = self.reward_head(hidden)
        return reward.squeeze(-1)
    
    def preference_loss(self, input_ids, attention_mask, chosen_ids, rejected_ids):
        """偏好比较损失"""
        # chosen和rejected是同一prompt的两种回答
        chosen_reward = self.forward(chosen_ids, attention_mask)
        rejected_reward = self.forward(rejected_ids, attention_mask)
        
        # Bradley-Terry损失
        loss = -torch.log(torch.sigmoid(chosen_reward - rejected_reward)).mean()
        return loss


class PPOTrainer:
    """PPO训练器 (简化示意)"""
    
    def __init__(
        self,
        policy_model,      # 当前策略
        reference_model,   # 参考模型(SFT)
        reward_model,      # 奖励模型
        value_model,       # 价值模型
        kl_coef=0.2        # KL惩罚系数
    ):
        self.policy = policy_model
        self.reference = reference_model
        self.reward = reward_model
        self.value = value_model
        self.kl_coef = kl_coef
        
    def compute_rewards(self, prompts, responses):
        """计算奖励 = 偏好奖励 - KL惩罚"""
        # 偏好奖励
        with torch.no_grad():
            full_text = [p + r for p, r in zip(prompts, responses)]
            preference_reward = self.reward(full_text)
        
        # KL散度惩罚 (防止策略偏离太远)
        kl_penalty = []
        for prompt, response in zip(prompts, responses):
            policy_logits = self.policy(prompt + response).logits
            ref_logits = self.reference(prompt + response).logits
            
            kl = (policy_logits - ref_logits).pow(2).mean()  # 近似KL
            kl_penalty.append(kl)
        
        kl_penalty = torch.stack(kl_penalty)
        
        # 总奖励
        total_reward = preference_reward - self.kl_coef * kl_penalty
        return total_reward
    
    def ppo_step(self, batch):
        """单步PPO更新"""
        prompts = batch["prompts"]
        old_responses = batch["responses"]
        old_logprobs = batch["logprobs"]
        old_values = batch["values"]
        returns = batch["returns"]
        advantages = batch["advantages"]
        
        # 重新生成响应并计算新概率
        new_outputs = self.policy(prompts)
        new_logprobs = self.get_logprobs(new_outputs, old_responses)
        
        # 计算比率
        ratio = torch.exp(new_logprobs - old_logprobs)
        
        # PPO裁剪目标
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 0.8, 1.2) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()
        
        # 价值函数损失
        new_values = self.value(prompts)
        value_loss = (returns - new_values).pow(2).mean()
        
        # 总损失
        total_loss = policy_loss + 0.5 * value_loss
        
        return total_loss


# DPO直接偏好优化 (更简洁的替代方案)
class DPOTrainer:
    """DPO: 直接偏好优化，无需奖励模型"""
    
    def __init__(self, model, ref_model, beta=0.1):
        self.model = model
        self.ref_model = ref_model
        self.beta = beta  # 温度参数
        
    def dpo_loss(self, batch):
        """DPO损失函数"""
        prompts = batch["prompts"]
        chosen = batch["chosen"]
        rejected = batch["rejected"]
        
        # 策略模型log概率
        policy_chosen_logps = self.get_logprobs(self.model, prompts, chosen)
        policy_rejected_logps = self.get_logprobs(self.model, prompts, rejected)
        
        # 参考模型log概率
        with torch.no_grad():
            ref_chosen_logps = self.get_logprobs(self.ref_model, prompts, chosen)
            ref_rejected_logps = self.get_logprobs(self.ref_model, prompts, rejected)
        
        # 计算隐式奖励差
        policy_diff = policy_chosen_logps - policy_rejected_logps
        ref_diff = ref_chosen_logps - ref_rejected_logps
        
        # DPO损失 (逻辑回归形式)
        logits = self.beta * (policy_diff - ref_diff)
        loss = -torch.log(torch.sigmoid(logits)).mean()
        
        return loss


# Constitutional AI 示意 (Claude使用)
CONSTITUTIONAL_AI_PROMPT = """以下是助手的回答：
{assistant_response}

请根据以下原则检查回答是否有害：
1. 不包含仇恨言论或歧视性内容
2. 不提供危险行为的指导
3. 不传播错误信息
4. 尊重个人隐私

如果存在违反，请解释原因并给出修正后的回答。"""
```

## 应用场景

- **对话模型对齐**: 让AI助手回答更有帮助、无害、诚实
- **内容安全**: 减少有害、偏见、不当内容输出
- **风格优化**: 调整语气、详细程度、格式偏好
- **领域适应**: 适应特定用户群体的期望
- **长上下文优化**: 训练模型在长对话中保持一致性

## 面试要点

1. **Q: RLHF相比SFT的优势是什么?**  
   A: SFT学习的是"示范回答"，RLHF学习的是"偏好排序"。人类更容易判断哪个回答更好，而不是写出完美回答。RLHF可以探索比示范回答更好的策略。

2. **Q: 为什么需要KL散度惩罚?**  
   A: 防止策略为了获得高奖励而偏离原始模型太远，导致输出质量下降或模式崩溃。KL惩罚保持模型在合理的行为空间内优化。

3. **Q: DPO相比PPO+RL的优势?**  
   A: DPO直接优化偏好，无需训练奖励模型和价值模型，更简单稳定。DPO本质上是将奖励建模和策略优化合并为一个步骤。

4. **Q: 如何收集高质量的人类偏好数据?**  
   A: 1) 清晰的标注指南 2) 多样化的人口代表性 3) 质量控制机制(一致性检查) 4) 适度的选项数量(通常2-4个) 5) 考虑文化和价值观差异。

5. **Q: RLHF中的reward hacking问题是什么?**  
   A: 模型找到奖励模型的漏洞而非真正满足人类意图，如生成特定格式欺骗奖励模型。解决：1) 定期更新奖励模型 2) 对抗训练 3) 多维度奖励 4) 人类持续监督。

## 相关概念

### AI & Data Systems
- [模型微调](./fine-tuning.md) - RLHF的前置SFT阶段
- [大语言模型](../llm.md) - RLHF的应用对象
- [AI Agents](./agents.md) - RLHF在Agent行为对齐中的应用

### 系统实现
- [强化学习](../../mathematics/statistics/statistical-learning.md) - RLHF的理论基础
- [优化算法](../../mathematics/linear-algebra/matrix-operations.md) - 梯度优化基础
- [分布式训练](../../computer-science/systems/process.md) - 大规模RLHF训练
