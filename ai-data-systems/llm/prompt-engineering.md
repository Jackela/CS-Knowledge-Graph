# 提示工程 (Prompt Engineering)

## 简介
**提示工程 (Prompt Engineering)** 是通过精心设计和优化输入提示词(prompt)，引导大语言模型(LLM)生成更准确、有用、安全输出的技术与方法论。它是与大模型交互的核心技能，直接影响模型性能而无需修改模型参数。

## 核心概念

### 1. 提示的基本结构
```
┌─────────────────────────────────────────────────────────────┐
│                    提示工程基本结构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  系统提示 (System Prompt)                                    │
│  ├── 设定角色: "你是一位资深Python工程师"                    │
│  ├── 定义行为: "请提供简洁、实用的代码建议"                  │
│  └── 约束条件: "不要使用已弃用的API"                         │
│                                                             │
│  用户提示 (User Prompt)                                      │
│  ├── 上下文: 相关背景信息                                    │
│  ├── 指令: 具体任务描述                                      │
│  └── 示例: Few-shot样本                                      │
│                                                             │
│  输出格式 (Output Format)                                    │
│  ├── 结构化: JSON/XML/Markdown                               │
│  └── 风格: 正式/ casual / 技术性                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 核心提示技术
| 技术 | 描述 | 适用场景 |
|------|------|----------|
| Zero-shot | 直接描述任务，无示例 | 简单、明确的任务 |
| Few-shot | 提供2-5个输入输出示例 | 格式控制、风格迁移 |
| Chain-of-Thought | 引导模型逐步推理 | 数学、逻辑、复杂问题 |
| ReAct | 推理(Reasoning)与行动(Acting)交替 | Agent、工具调用 |
| Self-Consistency | 多次采样，投票选择最佳答案 | 提高准确性 |
| Tree of Thoughts | 多路径探索，评估后选择 | 复杂决策问题 |

### 3. 提示优化原则
- **具体性**: 明确输出格式、长度、风格要求
- **上下文**: 提供足够的背景信息
- **分步**: 复杂任务拆分为多个简单步骤
- **约束**: 明确限制条件和边界
- **迭代**: 根据输出反馈持续优化提示

## 实现方式

```python
# 基础提示工程示例
class PromptEngineering:
    """提示工程技术实现"""
    
    def __init__(self):
        self.system_prompt = """你是一位专业的代码审查助手。
请分析代码并提供以下信息：
1. 潜在bug
2. 性能优化建议
3. 代码风格问题
以JSON格式返回结果。"""
    
    def zero_shot_prompt(self, task: str, context: str) -> str:
        """零样本提示"""
        return f"""任务：{task}

上下文：
{context}

请直接给出结果。"""
    
    def few_shot_prompt(self, task: str, examples: list, input_data: str) -> str:
        """少样本提示"""
        example_text = ""
        for ex in examples:
            example_text += f"输入: {ex['input']}\n输出: {ex['output']}\n\n"
        
        return f"""任务：{task}

以下是几个示例：
{example_text}
现在请处理：
输入: {input_data}
输出:"""
    
    def chain_of_thought_prompt(self, problem: str) -> str:
        """思维链提示"""
        return f"""问题：{problem}

请一步一步思考，展示你的推理过程：
步骤1：理解问题
步骤2：分析关键信息
步骤3：制定解决方案
步骤4：验证结果

答案："""
    
    def structured_output_prompt(self, data: str, format_schema: dict) -> str:
        """结构化输出提示"""
        return f"""请分析以下数据并以指定JSON格式返回：

数据：
{data}

输出格式：
{format_schema}

要求：
- 严格遵循JSON格式
- 不要包含任何解释性文字
- 确保所有字段都有值"""


# 高级提示：ReAct模式
class ReActPrompt:
    """推理与行动交替模式"""
    
    REACT_TEMPLATE = """你正在解决一个问题。你可以使用以下工具：
{tools}

请按照以下格式回答：
思考: 分析当前情况，决定下一步行动
行动: 选择要使用的工具
观察: 工具返回的结果
... (重复思考-行动-观察直到问题解决)
思考: 我现在知道最终答案
答案: 最终答案

问题: {question}
思考:"""
    
    def __init__(self, available_tools: list):
        self.tools = "\n".join([f"- {t['name']}: {t['description']}" for t in available_tools])
    
    def generate(self, question: str) -> str:
        return self.REACT_TEMPLATE.format(
            tools=self.tools,
            question=question
        )


# 实践示例：代码审查提示优化
OPTIMIZED_CODE_REVIEW_PROMPT = """作为资深Python工程师，请审查以下代码。

审查维度：
1. 安全性: 检查SQL注入、XSS、敏感信息泄露
2. 性能: 识别O(n²)复杂度、不必要的数据库查询
3. 可读性: 命名规范、函数长度、注释质量
4. 可维护性: 耦合度、重复代码、测试覆盖

输出要求（严格JSON格式）：
{{
  "issues": [
    {{
      "severity": "high|medium|low",
      "category": "security|performance|readability|maintainability",
      "line": 行号,
      "description": "问题描述",
      "suggestion": "修复建议"
    }}
  ],
  "summary": "总体评价"
}}

代码：
```python
{code}
```"""
```

## 应用场景

- **智能客服**: 通过提示工程控制回复风格、知识边界
- **内容生成**: 引导模型生成特定风格、长度的营销文案
- **代码辅助**: 优化提示以生成更符合项目规范的代码
- **数据分析**: 结构化输出提示，自动提取数据洞察
- **Agent系统**: ReAct模式实现多步骤任务规划与执行

## 面试要点

1. **Q: Few-shot和Zero-shot提示的区别及适用场景?**  
   A: Zero-shot无示例，适合简单明确任务；Few-shot提供示例，适合格式控制、风格迁移。选择依据是任务复杂度和输出格式要求。

2. **Q: Chain-of-Thought为什么能提高推理能力?**  
   A: CoT强制模型显式展示推理步骤，将复杂问题分解为可管理的子问题，减少跳步错误，同时让中间结果可检查、可验证。

3. **Q: 如何防止提示注入攻击(Prompt Injection)?**  
   A: 1) 输入验证和过滤 2) 使用分隔符隔离用户输入 3) 系统提示优先级设置 4) 输出后处理过滤 5) 敏感操作人工审核。

4. **Q: 提示工程 vs 微调(Fine-tuning)，如何选择?**  
   A: 提示工程：快速迭代、无训练成本、适合通用任务；微调：固定行为、有训练成本、适合特定领域深度优化。通常先用提示工程探索，必要时微调固化。

5. **Q: 什么是Prompt Chaining，有什么优势?**  
   A: Prompt Chaining将复杂任务拆分为多个子任务，每个子任务的输出作为下一个的输入。优势：提高准确性、降低复杂度、便于调试、可复用组件。

## 相关概念

### AI & Data Systems
- [大语言模型](../llm.md) - 提示工程的作用对象
- [RAG](../rag.md) - 结合检索增强的提示技术
- [AI Agents](./agents.md) - 提示工程在Agent系统中的应用
- [Embedding模型](./embedding-models.md) - 语义检索支持动态提示

### 系统实现
- [RESTful API](../../computer-science/networks/http-protocol.md) - 模型API接口设计
- [缓存策略](../../computer-science/systems/cache.md) - 提示响应缓存优化
- [日志系统](../../computer-science/systems/logging.md) - 提示效果追踪与分析
