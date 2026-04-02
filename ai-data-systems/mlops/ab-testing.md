# A/B 测试 (A/B Testing)

## 简介

A/B 测试是一种统计实验方法，通过将用户随机分配到对照组 (A) 和实验组 (B)，比较不同版本的效果差异。在机器学习领域，A/B 测试用于评估模型变更、算法优化和业务策略调整的实际效果。

## 核心概念

### A/B 测试流程

```
┌─────────────────────────────────────────────────────────┐
│                   A/B Testing Flow                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Hypothesis        2. Design         3. Implement    │
│     假设              实验设计            实施部署        │
│      │                   │                  │           │
│      ▼                   ▼                  ▼           │
│  ┌─────────┐       ┌─────────┐        ┌─────────┐      │
│  │提出假设  │       │确定指标  │        │分流实现  │      │
│  │定义成功  │──────►│计算样本  │───────►│对照组A   │      │
│  │标准      │       │量        │        │实验组B   │      │
│  └─────────┘       └─────────┘        └─────────┘      │
│                                              │          │
│  6. Decision ◄──────── 5. Analyze ◄──────────┤          │
│     决策                分析                  │          │
│      │                   │            4. Run            │
│      ▼                   ▼            运行实验          │
│  ┌─────────┐       ┌─────────┐        ┌─────────┐      │
│  │显著性检验│       │统计计算  │        │数据收集  │      │
│  │业务解读  │◄──────│置信区间  │◄───────│指标监控  │      │
│  │是否发布  │       │效应大小  │        │样本检查  │      │
│  └─────────┘       └─────────┘        └─────────┘      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 核心统计概念

| 概念 | 定义 | 公式/标准 |
|------|------|-----------|
| **显著性水平 (α)** | 假阳性率，通常取 0.05 | P(拒绝H₀ \| H₀为真) |
| **统计功效 (1-β)** | 正确拒绝原假设的概率，通常取 0.8 | P(拒绝H₀ \| H₁为真) |
| **最小检测效应 (MDE)** | 希望检测到的最小差异 | 业务可接受的最小提升 |
| **P值** | 观察结果出现的概率 | p < 0.05 认为显著 |
| **置信区间** | 估计值的不确定性范围 | 95% CI: 估计值 ± 1.96×SE |

### 样本量计算

$$n = \frac{2\sigma^2(Z_{1-\alpha/2} + Z_{1-\beta})^2}{\delta^2}$$

其中：
- $\sigma^2$: 方差
- $Z_{1-\alpha/2}$: 显著性水平对应的分位数 (1.96 for α=0.05)
- $Z_{1-\beta}$: 功效对应的分位数 (0.84 for power=0.8)
- $\delta$: 最小检测效应 (MDE)

```python
# 样本量计算示例
from scipy import stats
import math

def calculate_sample_size(
    baseline_rate: float,  # 基准转化率
    mde: float,            # 最小检测效应
    alpha: float = 0.05,   # 显著性水平
    power: float = 0.8     # 统计功效
) -> int:
    """计算每组所需样本量"""
    
    # 对照组和实验组的转化率
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde)
    
    # 合并方差
    p_pooled = (p1 + p2) / 2
    var = p_pooled * (1 - p_pooled)
    
    # Z值
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    
    # 样本量公式
    n = (2 * var * (z_alpha + z_beta) ** 2) / (p2 - p1) ** 2
    
    return math.ceil(n)

# 示例：基准转化率 10%，期望检测 20% 的相对提升
calculate_sample_size(baseline_rate=0.10, mde=0.20)
# 输出: 约 1570 每组，共 3140 样本
```

## 实现方式

### 1. 随机分流实现

```python
# ab_testing.py
import hashlib
import random
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

class ExperimentStatus(Enum):
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class Experiment:
    id: str
    name: str
    control_group: str = "A"
    treatment_group: str = "B"
    traffic_split: float = 0.5  # 实验组流量比例
    status: ExperimentStatus = ExperimentStatus.RUNNING

class ABTestRouter:
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {exp_id: group}
    
    def create_experiment(self, exp: Experiment):
        """创建实验"""
        self.experiments[exp.id] = exp
        print(f"Created experiment: {exp.name}")
    
    def hash_assignment(self, user_id: str, exp_id: str) -> str:
        """基于哈希的确定性分流"""
        hash_input = f"{user_id}:{exp_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        exp = self.experiments[exp_id]
        normalized = (hash_value % 10000) / 10000.0
        
        if normalized < exp.traffic_split:
            return exp.treatment_group
        return exp.control_group
    
    def assign_user(self, user_id: str, exp_id: str) -> str:
        """将用户分配到实验组"""
        if exp_id not in self.experiments:
            raise ValueError(f"Experiment {exp_id} not found")
        
        exp = self.experiments[exp_id]
        if exp.status != ExperimentStatus.RUNNING:
            return exp.control_group  # 实验未运行，全部进入对照组
        
        # 检查已有分配（保证一致性）
        if user_id in self.user_assignments and exp_id in self.user_assignments[user_id]:
            return self.user_assignments[user_id][exp_id]
        
        # 新分配
        group = self.hash_assignment(user_id, exp_id)
        
        if user_id not in self.user_assignments:
            self.user_assignments[user_id] = {}
        self.user_assignments[user_id][exp_id] = group
        
        # 记录分配日志
        self._log_assignment(user_id, exp_id, group)
        
        return group
    
    def _log_assignment(self, user_id: str, exp_id: str, group: str):
        """记录用户分配（实际应写入数据库）"""
        print(f"[ASSIGN] user={user_id}, exp={exp_id}, group={group}")

# 使用示例
router = ABTestRouter()

# 创建实验
exp = Experiment(
    id="exp_001",
    name="New Recommendation Model",
    traffic_split=0.5  # 50% 流量进入实验组
)
router.create_experiment(exp)

# 用户分流
user_id = "user_12345"
group = router.assign_user(user_id, "exp_001")

if group == "B":
    # 使用新模型
    prediction = new_model.predict(features)
else:
    # 使用旧模型
    prediction = old_model.predict(features)
```

### 2. 多变量实验 (Multi-variate Testing)

```python
# multivariate_testing.py
from itertools import product

class MultivariateTest:
    def __init__(self, factors: Dict[str, list]):
        """
        factors: {"颜色": ["红", "蓝"], "按钮": ["大", "小"]}
        """
        self.factors = factors
        self.variants = self._generate_variants()
    
    def _generate_variants(self) -> list:
        """生成所有实验组合"""
        keys = list(self.factors.keys())
        values = [self.factors[k] for k in keys]
        
        variants = []
        for combo in product(*values):
            variant = dict(zip(keys, combo))
            variants.append(variant)
        
        return variants
    
    def assign_variant(self, user_id: str) -> Dict:
        """为用户分配一个实验组合"""
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        variant_index = hash_value % len(self.variants)
        return self.variants[variant_index]

# 使用示例
mv_test = MultivariateTest({
    "model_version": ["v1", "v2"],
    "ranking_algorithm": ["cosine", "dot_product"],
    "recommendation_count": [5, 10]
})

# 共 2 × 2 × 2 = 8 种组合
variant = mv_test.assign_variant("user_123")
# 输出: {'model_version': 'v2', 'ranking_algorithm': 'cosine', 'recommendation_count': 10}
```

### 3. 统计分析实现

```python
# statistical_analysis.py
import numpy as np
from scipy import stats
from typing import Tuple, Dict

class ABTestAnalyzer:
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    def analyze_conversion(self, 
                          control_conversions: int, control_visitors: int,
                          treatment_conversions: int, treatment_visitors: int) -> Dict:
        """转化率差异分析"""
        
        # 转化率
        p_control = control_conversions / control_visitors
        p_treatment = treatment_conversions / treatment_visitors
        
        # 合并方差（原假设：两组无差异）
        p_pooled = (control_conversions + treatment_conversions) / \
                   (control_visitors + treatment_visitors)
        
        # 标准误
        se = np.sqrt(p_pooled * (1 - p_pooled) * 
                     (1/control_visitors + 1/treatment_visitors))
        
        # Z统计量
        z_score = (p_treatment - p_control) / se
        
        # P值（双侧检验）
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        # 置信区间
        diff = p_treatment - p_control
        margin = stats.norm.ppf(1 - self.alpha/2) * se
        ci_lower = diff - margin
        ci_upper = diff + margin
        
        # 相对提升
        relative_lift = (p_treatment - p_control) / p_control if p_control > 0 else 0
        
        return {
            "control_rate": p_control,
            "treatment_rate": p_treatment,
            "absolute_diff": diff,
            "relative_lift": relative_lift,
            "z_score": z_score,
            "p_value": p_value,
            "significant": p_value < self.alpha,
            "confidence_interval": (ci_lower, ci_upper),
            "recommendation": "Deploy" if (p_value < self.alpha and diff > 0) else "Keep Control"
        }
    
    def analyze_continuous(self,
                          control_values: np.ndarray,
                          treatment_values: np.ndarray) -> Dict:
        """连续指标分析（如平均订单金额）"""
        
        # 描述统计
        mean_control = np.mean(control_values)
        mean_treatment = np.mean(treatment_values)
        std_control = np.std(control_values, ddof=1)
        std_treatment = np.std(treatment_values, ddof=1)
        n_control = len(control_values)
        n_treatment = len(treatment_values)
        
        # Welch's t-test（不假设方差齐性）
        se = np.sqrt(std_control**2/n_control + std_treatment**2/n_treatment)
        t_stat = (mean_treatment - mean_control) / se
        
        # 自由度 (Welch-Satterthwaite equation)
        df = (std_control**2/n_control + std_treatment**2/n_treatment)**2 / \
             ((std_control**2/n_control)**2/(n_control-1) + 
              (std_treatment**2/n_treatment)**2/(n_treatment-1))
        
        # P值
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
        
        # 置信区间
        diff = mean_treatment - mean_control
        margin = stats.t.ppf(1 - self.alpha/2, df) * se
        
        return {
            "control_mean": mean_control,
            "treatment_mean": mean_treatment,
            "absolute_diff": diff,
            "relative_lift": diff / mean_control if mean_control != 0 else 0,
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < self.alpha,
            "confidence_interval": (diff - margin, diff + margin),
            "degrees_of_freedom": df
        }
    
    def sequential_testing(self, 
                          control_data: list, 
                          treatment_data: list,
                          checkpoints: list = None) -> list:
        """序贯检验（早期停止）"""
        if checkpoints is None:
            checkpoints = [0.25, 0.5, 0.75, 1.0]
        
        n = min(len(control_data), len(treatment_data))
        results = []
        
        # Alpha spending function (O'Brien-Fleming)
        def obf_boundary(t, alpha=0.05):
            return 2 * (1 - stats.norm.cdf(
                stats.norm.ppf(1 - alpha/2) / np.sqrt(t)
            ))
        
        for checkpoint in checkpoints:
            idx = int(n * checkpoint)
            result = self.analyze_continuous(
                np.array(control_data[:idx]),
                np.array(treatment_data[:idx])
            )
            
            # 调整后的显著性水平
            adjusted_alpha = obf_boundary(checkpoint, self.alpha)
            result["checkpoint"] = checkpoint
            result["adjusted_alpha"] = adjusted_alpha
            result["early_stop"] = result["p_value"] < adjusted_alpha
            
            results.append(result)
        
        return results

# 使用示例
analyzer = ABTestAnalyzer(confidence_level=0.95)

# 转化率分析
result = analyzer.analyze_conversion(
    control_conversions=100, control_visitors=1000,
    treatment_conversions=120, treatment_visitors=1000
)
print(f"Relative lift: {result['relative_lift']:.2%}")
print(f"P-value: {result['p_value']:.4f}")
print(f"Significant: {result['significant']}")
```

### 4. 完整的 A/B 测试平台

```python
# ab_test_platform.py
import sqlite3
from datetime import datetime
import json

class ABTestPlatform:
    def __init__(self, db_path="ab_tests.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                name TEXT,
                status TEXT,
                created_at TIMESTAMP,
                config TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT,
                user_id TEXT,
                variant TEXT,
                event_type TEXT,  -- 'impression', 'conversion', etc.
                value REAL,
                timestamp TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def track_event(self, experiment_id: str, user_id: str, 
                   variant: str, event_type: str, value: float = 1.0):
        """记录实验事件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (experiment_id, user_id, variant, event_type, value, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (experiment_id, user_id, variant, event_type, value, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_experiment_results(self, experiment_id: str) -> Dict:
        """获取实验结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询各组数据
        cursor.execute('''
            SELECT variant, 
                   COUNT(DISTINCT user_id) as users,
                   SUM(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) as conversions,
                   SUM(CASE WHEN event_type = 'revenue' THEN value ELSE 0 END) as revenue
            FROM events
            WHERE experiment_id = ?
            GROUP BY variant
        ''', (experiment_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return self._analyze_results(results)
    
    def _analyze_results(self, data: list) -> Dict:
        """分析实验结果"""
        analyzer = ABTestAnalyzer()
        
        # 解析数据
        control = next((r for r in data if r[0] == 'A'), None)
        treatment = next((r for r in data if r[0] == 'B'), None)
        
        if not control or not treatment:
            return {"error": "Missing control or treatment data"}
        
        # 转化率分析
        conversion_result = analyzer.analyze_conversion(
            control_conversions=control[2],
            control_visitors=control[1],
            treatment_conversions=treatment[2],
            treatment_visitors=treatment[1]
        )
        
        return {
            "control": {"users": control[1], "conversions": control[2]},
            "treatment": {"users": treatment[1], "conversions": treatment[2]},
            "conversion_analysis": conversion_result,
            "timestamp": datetime.now().isoformat()
        }

# Flask API 示例
from flask import Flask, request, jsonify

app = Flask(__name__)
platform = ABTestPlatform()
router = ABTestRouter()

@app.route('/api/experiment/<exp_id>/assign', methods=['POST'])
def assign_user(exp_id):
    user_id = request.json.get('user_id')
    variant = router.assign_user(user_id, exp_id)
    return jsonify({"user_id": user_id, "variant": variant})

@app.route('/api/experiment/<exp_id>/track', methods=['POST'])
def track_event(exp_id):
    data = request.json
    platform.track_event(
        experiment_id=exp_id,
        user_id=data['user_id'],
        variant=data['variant'],
        event_type=data['event_type'],
        value=data.get('value', 1.0)
    )
    return jsonify({"status": "success"})

@app.route('/api/experiment/<exp_id>/results', methods=['GET'])
def get_results(exp_id):
    results = platform.get_experiment_results(exp_id)
    return jsonify(results)
```

## 示例

### 机器学习模型 A/B 测试完整流程

```python
# ml_ab_test_example.py
class ModelABTest:
    """机器学习模型的 A/B 测试示例"""
    
    def __init__(self):
        self.router = ABTestRouter()
        self.analyzer = ABTestAnalyzer()
    
    def setup_experiment(self, exp_name: str, model_a, model_b):
        """设置模型 A/B 测试"""
        exp = Experiment(
            id=exp_name,
            name=f"Model Comparison: {exp_name}",
            traffic_split=0.5
        )
        self.router.create_experiment(exp)
        
        self.models = {
            "A": model_a,  # 基线模型
            "B": model_b   # 新模型
        }
    
    def serve_recommendation(self, user_id: str, context: dict):
        """提供推荐服务"""
        # 分流
        group = self.router.assign_user(user_id, "rec_model_test")
        
        # 使用对应模型
        model = self.models[group]
        recommendations = model.predict(context)
        
        # 记录曝光
        self._log_event(user_id, group, "impression", len(recommendations))
        
        return {
            "user_id": user_id,
            "group": group,
            "recommendations": recommendations
        }
    
    def track_click(self, user_id: str, item_id: str):
        """记录点击"""
        group = self.router.user_assignments.get(user_id, {}).get("rec_model_test", "A")
        self._log_event(user_id, group, "click", 1)
    
    def track_conversion(self, user_id: str, revenue: float):
        """记录转化"""
        group = self.router.user_assignments.get(user_id, {}).get("rec_model_test", "A")
        self._log_event(user_id, group, "conversion", revenue)
    
    def analyze(self, metric: str = "ctr") -> dict:
        """分析实验结果"""
        # 获取指标数据（实际应从数据库查询）
        # 这里展示分析逻辑
        
        if metric == "ctr":
            # 点击率分析
            return self.analyzer.analyze_conversion(
                control_conversions=self._get_clicks("A"),
                control_visitors=self._get_impressions("A"),
                treatment_conversions=self._get_clicks("B"),
                treatment_visitors=self._get_impressions("B")
            )
        elif metric == "revenue":
            # 收入分析
            return self.analyzer.analyze_continuous(
                np.array(self._get_revenues("A")),
                np.array(self._get_revenues("B"))
            )

# 使用示例
ml_test = ModelABTest()

# 假设有两个推荐模型
baseline_model = BaselineRecommender()
new_model = NeuralRecommender()

ml_test.setup_experiment("neural_rec_v2", baseline_model, new_model)

# 服务请求
result = ml_test.serve_recommendation("user_123", {"context": "evening"})
print(f"User assigned to group: {result['group']}")

# 用户交互追踪
ml_test.track_click("user_123", "item_456")
ml_test.track_conversion("user_123", 99.99)

# 分析结果
analysis = ml_test.analyze(metric="ctr")
if analysis["significant"] and analysis["relative_lift"] > 0.05:
    print("新模型显著优于基线，建议全量发布")
```

## 应用场景

| 场景 | 测试目标 | 关键指标 | 样本量建议 |
|------|----------|----------|------------|
| **推荐算法** | 新模型 vs 旧模型 | CTR、转化率、停留时长 | 10000+ |
| **UI 优化** | 界面改版 | 点击率、任务完成率 | 5000+ |
| **定价策略** | 不同价格点 | 收入、转化率 | 需要更大样本 |
| **推送策略** | 发送频率/内容 | 打开率、卸载率 | 10000+ |
| **搜索排序** | 新排序算法 | 点击率、相关性评分 | 50000+ |

## 面试要点

Q: A/B 测试与模型离线评估的区别？
A: 
- **离线评估**: 使用历史数据，无法反映真实用户行为
- **A/B 测试**: 真实环境验证，考虑业务指标、用户满意度
- **相互补充**: 离线筛选候选模型，A/B 测试最终决策

Q: 如何确定 A/B 测试的样本量？
A: 样本量取决于：
   - **基线指标**: 当前转化率/均值
   - **MDE**: 业务可接受的最小提升
   - **显著性水平**: 通常 α=0.05
   - **统计功效**: 通常 1-β=0.8
   公式: $n = \frac{2\sigma^2(Z_{1-\alpha/2} + Z_{1-\beta})^2}{\delta^2}$

Q: A/B 测试有哪些常见陷阱？
A: 常见陷阱：
   - **样本污染**: 同一用户看到不同版本
   - **网络效应**: 用户间相互影响（如社交功能）
   - **新奇效应**: 用户对新版本的好奇偏差
   - **多重检验问题**: 多个指标/多次查看增加假阳性
   - **辛普森悖论**: 整体显著但各子群不显著

Q: 如何处理多个实验同时进行？
A: 策略：
   - **正交分层**: 不同实验使用不同的哈希桶
   - **互斥实验**: 同一层实验互斥
   - **实验优先级**: 高优先级实验优先分流
   - **流量分层**: 每层使用独立流量桶

Q: P 值和置信区间如何解读？
A: 
   - **P 值**: 在原假设为真时，观察到当前或更极端结果的概率
     - p < 0.05: 拒绝原假设，认为有显著差异
   - **置信区间**: 真实差异的可能范围
     - 不包含 0: 统计显著
     - 区间宽窄反映估计精度

## 相关概念

### 数据结构
- [哈希表](../ml-fundamentals/data-processing.md) - 用户分流
- [时序数据库](../ml-fundamentals/data-processing.md) - 实验数据存储

### 算法
- [假设检验](../mathematics/statistics/hypothesis-testing.md) - 统计检验基础
- [置信区间](../mathematics/statistics/estimation.md) - 效应估计
- [随机化](../mathematics/statistics/sampling.md) - 随机抽样

### 复杂度分析
- **分流计算**: $O(1)$ - Hash 计算
- **样本量计算**: $O(1)$ - 公式计算
- **统计检验**: $O(n)$ - n 为样本量
- **多重比较校正**: $O(m)$ - m 为比较次数

### 系统实现
- [模型部署](./model-deployment.md) - 实验模型部署
- [模型监控](./model-monitoring.md) - 实验监控
- [特征存储](./feature-store.md) - 实验特征管理
