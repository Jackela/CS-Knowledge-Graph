# AI Agents (AI智能体)

## 简介
**AI Agents (AI智能体)** 是具备感知环境、自主决策、执行行动能力的AI系统。与单次调用的LLM不同，Agent通过多轮推理、工具调用、记忆管理等机制，能够自主完成复杂的多步骤任务。

## 核心概念

### 1. Agent架构组件
```
┌─────────────────────────────────────────────────────────────┐
│                   AI Agent架构                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   感知层     │───>│   决策层     │───>│   执行层     │     │
│  │             │    │             │    │             │     │
│  │ • 用户输入   │    │ • LLM推理   │    │ • 工具调用   │     │
│  │ • 环境观察   │    │ • 规划分解  │    │ • API调用   │     │
│  │ • 记忆检索   │    │ • 反思修正  │    │ • 代码执行   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         ↑                   │                   │          │
│         └───────────────────┴───────────────────┘          │
│                          反馈循环                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                      记忆系统                          │   │
│  │  • 短期记忆: 当前对话上下文                             │   │
│  │  • 长期记忆: 向量数据库存储的历史经验                    │   │
│  │  • 外部记忆: 知识库、文档检索                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                      工具箱                            │   │
│  │  • 搜索工具 • 计算器 • 代码解释器 • API接口            │   │
│  │  • 数据库 • 文件系统 • 浏览器自动化 • 其他Agent        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Agent设计模式
| 模式 | 描述 | 适用场景 |
|------|------|----------|
| **ReAct** | 推理(Reasoning)与行动(Acting)交替 | 需要多步推理的问题 |
| **Plan-and-Execute** | 先规划步骤，再执行 | 复杂任务分解 |
| **Reflection** | 自我反思和改进 | 质量要求高的任务 |
| **Multi-Agent** | 多个Agent协作 | 复杂系统设计 |
| **Tool Use** | 工具增强能力 | 需要外部数据/计算 |

### 3. ReAct模式详解
```
ReAct (Reasoning + Acting) 执行流程:

循环:
1. 思考 (Thought)
   "我需要查找2024年GDP数据来计算增长率"
   
2. 行动 (Action)
   调用: search_tool("2024年中国GDP")
   
3. 观察 (Observation)
   结果: "2024年中国GDP为134.9万亿元"
   
4. 思考 (Thought)
   "现在需要2023年的数据进行对比"
   
5. 行动 (Action)
   调用: search_tool("2023年中国GDP")
   
6. 观察 (Observation)
   结果: "2023年中国GDP为126.1万亿元"
   
7. 思考 (Thought)
   "可以计算了: (134.9-126.1)/126.1 = 6.98%"
   
8. 完成 (Finish)
   最终答案: 2024年GDP增长率约为7.0%
```

### 4. Agent vs LLM
```
对比维度:

              LLM                    Agent
交互方式    单次请求-响应           多轮自主执行
上下文      有限窗口                +长期记忆系统
工具使用    无                      可调用外部工具
规划能力    单次生成                多步规划与调整
持久状态    无                      有状态、可学习
适用任务    单次生成任务            复杂多步骤任务
```

## 实现方式

```python
# AI Agent完整实现
from typing import List, Dict, Callable, Any
import json
import re


class Tool:
    """工具定义"""
    
    def __init__(self, name: str, description: str, func: Callable, parameters: dict):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters
    
    def execute(self, **kwargs) -> str:
        """执行工具"""
        try:
            result = self.func(**kwargs)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"


class Memory:
    """简单记忆系统"""
    
    def __init__(self):
        self.short_term: List[Dict] = []  # 短期记忆
        self.long_term: List[Dict] = []   # 长期记忆(简化版)
    
    def add_interaction(self, role: str, content: str):
        """添加交互记录"""
        self.short_term.append({"role": role, "content": content})
        # 限制短期记忆长度
        if len(self.short_term) > 20:
            self.short_term = self.short_term[-20:]
    
    def get_context(self) -> str:
        """获取记忆上下文"""
        return "\n".join([f"{m['role']}: {m['content']}" for m in self.short_term])
    
    def clear(self):
        """清空记忆"""
        self.short_term = []


class ReActAgent:
    """ReAct模式Agent实现"""
    
    def __init__(self, llm_client, tools: List[Tool], max_iterations: int = 10):
        self.llm = llm_client
        self.tools = {t.name: t for t in tools}
        self.max_iterations = max_iterations
        self.memory = Memory()
        
    def _create_system_prompt(self) -> str:
        """创建系统提示"""
        tools_desc = "\n".join([
            f"- {name}: {tool.description}\n  参数: {json.dumps(tool.parameters)}"
            for name, tool in self.tools.items()
        ])
        
        return f"""你是一个智能助手，可以使用以下工具完成任务：

可用工具：
{tools_desc}

请按照以下格式思考和行动：

思考: 分析当前情况，决定下一步行动
行动: 工具名称，参数为JSON格式
观察: 工具返回的结果
... (重复思考-行动-观察直到完成任务)

当你完成任务时，输出：
完成: 最终答案

重要：
- 每次只能执行一个行动
- 行动参数必须是有效的JSON
- 如果工具返回错误，请尝试其他方法"""
    
    def _parse_action(self, text: str) -> tuple:
        """解析行动指令"""
        # 匹配: 行动: tool_name, {"param": "value"}
        pattern = r'行动:\s*(\w+)\s*,\s*(\{.*?\})'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            tool_name = match.group(1)
            params_str = match.group(2)
            try:
                params = json.loads(params_str)
                return tool_name, params
            except json.JSONDecodeError:
                return None, None
        return None, None
    
    def run(self, task: str) -> str:
        """执行Agent任务"""
        self.memory.clear()
        self.memory.add_interaction("用户", task)
        
        system_prompt = self._create_system_prompt()
        
        for i in range(self.max_iterations):
            # 构建当前上下文
            context = self.memory.get_context()
            
            # 调用LLM
            response = self.llm.generate(
                system=system_prompt,
                user=f"历史:\n{context}\n\n请继续完成任务。"
            )
            
            self.memory.add_interaction("助手", response)
            
            # 检查是否完成
            if "完成:" in response:
                return response.split("完成:")[1].strip()
            
            # 解析行动
            tool_name, params = self._parse_action(response)
            
            if tool_name and tool_name in self.tools:
                # 执行工具
                tool = self.tools[tool_name]
                observation = tool.execute(**params)
                
                self.memory.add_interaction("系统", f"观察: {observation}")
            else:
                # 没有可执行的行动，可能已完成
                if "思考:" in response and "行动:" not in response:
                    return response.split("思考:")[-1].strip()
        
        return f"达到最大迭代次数({self.max_iterations})，任务未完成。"


# 工具实现示例
def create_tools() -> List[Tool]:
    """创建常用工具"""
    
    # 搜索工具
    def search(query: str) -> str:
        """模拟搜索"""
        return f"搜索结果: {query}的相关信息..."
    
    # 计算器
    def calculate(expression: str) -> str:
        """安全计算"""
        try:
            # 只允许数字和运算符
            allowed = set('0123456789+-*/.() ')
            if all(c in allowed for c in expression):
                result = eval(expression)
                return str(result)
            return "Error: Invalid characters"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # 天气查询
    def get_weather(city: str) -> str:
        """模拟天气查询"""
        weather_data = {
            "北京": "晴天，25°C",
            "上海": "多云，28°C",
            "深圳": "小雨，30°C"
        }
        return weather_data.get(city, f"未找到{city}的天气信息")
    
    # 当前时间
    def get_current_time() -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return [
        Tool("search", "搜索互联网获取信息", search, {"query": "string"}),
        Tool("calculate", "执行数学计算", calculate, {"expression": "string"}),
        Tool("get_weather", "获取城市天气", get_weather, {"city": "string"}),
        Tool("get_current_time", "获取当前时间", get_current_time, {})
    ]


# 多Agent协作系统
class MultiAgentSystem:
    """多Agent协作系统"""
    
    def __init__(self):
        self.agents: Dict[str, ReActAgent] = {}
        
    def register_agent(self, name: str, agent: ReActAgent):
        """注册Agent"""
        self.agents[name] = agent
    
    def coordinate(self, task: str, coordinator_llm) -> str:
        """协调多个Agent完成任务"""
        
        # 分析任务并分配
        decomposition_prompt = f"""将以下任务分解为子任务，并指定最适合的Agent：

可用Agent：
{list(self.agents.keys())}

任务：{task}

请按以下格式输出：
1. [Agent名称] - [子任务描述]
2. ..."""
        
        plan = coordinator_llm.generate(user=decomposition_prompt)
        
        # 执行子任务
        results = []
        for line in plan.split('\n'):
            if '-' in line:
                agent_name = line.split(']')[0].split('[')[1]
                subtask = line.split('-')[1].strip()
                
                if agent_name in self.agents:
                    result = self.agents[agent_name].run(subtask)
                    results.append(f"{agent_name}: {result}")
        
        # 整合结果
        synthesis_prompt = f"""整合以下子任务结果，给出完整答案：

原始任务：{task}

子任务结果：
{chr(10).join(results)}

请给出最终答案。"""
        
        return coordinator_llm.generate(user=synthesis_prompt)


# 高级: Plan-and-Solve Agent
class PlanAndSolveAgent:
    """先规划后执行的Agent"""
    
    def __init__(self, llm_client, tools: List[Tool]):
        self.llm = llm_client
        self.tools = {t.name: t for t in tools}
    
    def run(self, task: str) -> str:
        """执行规划-解决流程"""
        
        # 步骤1: 制定计划
        plan_prompt = f"""请为以下任务制定详细执行计划：

任务：{task}

可用工具：{list(self.tools.keys())}

请输出具体步骤列表，每步包含：
1. 步骤编号
2. 步骤描述
3. 需要使用的工具（如果有）
4. 预期输出"""
        
        plan = self.llm.generate(user=plan_prompt)
        
        # 步骤2: 执行计划
        execution_results = []
        context = f"任务：{task}\n计划：{plan}\n"
        
        for step in self._parse_plan(plan):
            execute_prompt = f"""{context}

当前步骤：{step}
请执行此步骤。如果需要使用工具，请说明工具名称和参数。
执行结果："""
            
            result = self.llm.generate(user=execute_prompt)
            execution_results.append(f"步骤: {step}\n结果: {result}")
            context += f"\n已完成：{result}"
        
        # 步骤3: 综合答案
        final_prompt = f"""基于以下执行结果，给出最终答案：

{chr(10).join(execution_results)}

最终答案："""
        
        return self.llm.generate(user=final_prompt)
    
    def _parse_plan(self, plan: str) -> List[str]:
        """解析计划为步骤列表"""
        steps = []
        for line in plan.split('\n'):
            # 匹配数字开头的行
            if re.match(r'^\d+[.\)]', line.strip()):
                steps.append(line.strip())
        return steps


# 使用示例
class MockLLM:
    """模拟LLM用于演示"""
    
    def generate(self, system: str = "", user: str = "") -> str:
        """模拟生成"""
        # 这里应该调用真实的LLM API
        if "计算" in user or "calculate" in user:
            return "思考: 需要使用计算器\n行动: calculate, {\"expression\": \"2+2\"}\n观察: 4\n完成: 计算结果是4"
        return "思考: 正在处理\n行动: search, {\"query\": \"相关信息\"}"


# 演示
# agent = ReActAgent(MockLLM(), create_tools())
# result = agent.run("北京今天天气如何？")
```

## 应用场景

- **个人助手**: 日程管理、信息查询、任务执行
- **代码助手**: 理解需求、编写代码、调试测试
- **研究助理**: 文献检索、数据分析、报告撰写
- **客服系统**: 多轮对话、问题诊断、工单处理
- **数据分析**: 自动获取数据、清洗、分析、可视化
- **自动化运维**: 监控告警、故障诊断、自动修复

## 面试要点

1. **Q: Agent和普通LLM调用有什么区别?**  
   A: Agent是多轮自主执行，有状态、能调用工具、能规划分解任务。LLM是单次请求-响应，无状态，仅基于参数生成文本。

2. **Q: ReAct模式为什么有效?**  
   A: ReAct将推理和行动交织，让LLM在每一步都显式展示思考过程。这种"慢思考"模式减少错误，同时观察反馈形成闭环，适合多步任务。

3. **Q: Agent的记忆系统如何设计?**  
   A: 通常分三层：1) 短期记忆(对话上下文) 2) 长期记忆(向量数据库存储) 3) 外部记忆(知识库)。短期用滑动窗口，长期用RAG检索。

4. **Q: 如何防止Agent无限循环或偏离任务?**  
   A: 1) 设置最大迭代次数 2) 任务完成检测 3) 相关性检查(行动是否与目标相关) 4) 人类监督介入点 5) 工具执行超时控制。

5. **Q: Multi-Agent系统的设计挑战?**  
   A: 1) 任务分解与分配 2) Agent间通信协议 3) 冲突解决机制 4) 结果一致性 5) 容错和重试 6) 性能优化(并行vs串行)。

## 相关概念

### AI & Data Systems
- [大语言模型](../llm.md) - Agent的核心推理引擎
- [RAG架构](./rag-architecture.md) - Agent的长期记忆系统
- [提示工程](./prompt-engineering.md) - Agent的Prompt设计
- [RLHF](./rlhf.md) - Agent行为对齐方法

### 系统实现
- [API设计](../../computer-science/networks/http-protocol.md) - Agent工具接口设计
- [消息队列](../../computer-science/systems/ipc.md) - Multi-Agent通信
- [状态管理](../../computer-science/systems/process.md) - Agent状态持久化
