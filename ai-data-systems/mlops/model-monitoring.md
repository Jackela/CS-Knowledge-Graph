# 模型监控 (Model Monitoring)

## 简介

模型监控是 MLOps 的核心环节，用于持续跟踪生产环境中机器学习模型的性能、数据质量和系统健康状况。与软件监控不同，模型监控需要关注数据漂移、概念漂移等 ML 特有的问题。

## 核心概念

### 监控维度

```
┌─────────────────────────────────────────────────────────┐
│                    Model Monitoring                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Data Drift │  │ Concept Drift│  │   Performance│  │
│  │  (数据漂移)   │  │  (概念漂移)   │  │  (性能监控)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Data Quality │  │   Latency    │  │   System     │  │
│  │  (数据质量)   │  │  (延迟监控)   │  │  (系统健康)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 数据漂移 (Data Drift)

| 类型 | 定义 | 检测方法 |
|------|------|----------|
| **特征漂移** | 输入特征分布变化 | KS检验、PSI、Wasserstein距离 |
| **标签漂移** | 目标变量分布变化 | 标签分布对比 |
| **协变量漂移** | $P(X)$ 变化但 $P(Y\|X)$ 不变 | 特征分布监控 |

**PSI (Population Stability Index)**:
$$PSI = \sum_{i}(Actual_i - Expected_i) \times \ln\left(\frac{Actual_i}{Expected_i}\right)$$

- PSI < 0.1: 无显著变化
- 0.1 ≤ PSI < 0.25: 轻微变化，需关注
- PSI ≥ 0.25: 显著变化，需采取行动

### 概念漂移 (Concept Drift)

```
时间线 ─────────────────────────────────────────►

真实分布 P(Y|X):
    │    ╭─╮
    │   ╱   ╲        ╭──╮
    │  ╱     ╲      ╱    ╲     ╭────╮
    │ ╱       ╲____╱      ╲___╱      ╲___
    └─────────────────────────────────────
      训练期    概念漂移点    新分布

类型:
- 突然漂移 (Sudden): 瞬时变化
- 渐进漂移 (Gradual): 缓慢变化
- 周期性漂移 (Periodic): 季节性变化
- 重复漂移 (Recurring): 循环出现
```

### 性能监控指标

| 指标 | 分类问题 | 回归问题 |
|------|----------|----------|
| **Accuracy** | 准确率 | - |
| **Precision/Recall** | 精确率/召回率 | - |
| **F1 Score** | F1分数 | - |
| **AUC-ROC** | ROC曲线下面积 | - |
| **Log Loss** | 对数损失 | - |
| **MAE** | - | 平均绝对误差 |
| **RMSE** | - | 均方根误差 |
| **R²** | - | 决定系数 |

## 实现方式

### 1. Evidently AI 监控

```python
# 数据漂移检测
import evidently
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
from evidently.metrics import DatasetDriftMetric

# 创建漂移报告
report = Report(metrics=[
    DataDriftPreset(),
    DatasetDriftMetric()
])

report.run(
    reference_data=train_df,  # 训练数据
    current_data=prod_df      # 生产数据
)

report.save_html("drift_report.html")

# 获取漂移指标
drift_score = report.as_dict()['metrics'][0]['result']['dataset_drift']
print(f"Data drift detected: {drift_score}")
```

### 2. 自定义漂移检测

```python
import numpy as np
from scipy import stats
from sklearn.preprocessing import KBinsDiscretizer

class DriftDetector:
    def __init__(self, n_bins=10, psi_threshold=0.2):
        self.n_bins = n_bins
        self.psi_threshold = psi_threshold
        self.reference_dist = {}
    
    def fit(self, X: np.ndarray):
        """拟合参考数据分布"""
        for i in range(X.shape[1]):
            hist, bins = np.histogram(X[:, i], bins=self.n_bins)
            self.reference_dist[i] = {
                'hist': hist / len(X),
                'bins': bins
            }
    
    def calculate_psi(self, expected, actual, epsilon=1e-10):
        """计算 PSI 指标"""
        expected = np.array(expected) + epsilon
        actual = np.array(actual) + epsilon
        return np.sum((actual - expected) * np.log(actual / expected))
    
    def detect_drift(self, X: np.ndarray) -> dict:
        """检测数据漂移"""
        drift_report = {'features': {}, 'drifted_features': []}
        
        for i in range(X.shape[1]):
            ref = self.reference_dist[i]
            current_hist, _ = np.histogram(
                X[:, i], bins=ref['bins']
            )
            current_dist = current_hist / len(X)
            
            psi = self.calculate_psi(ref['hist'], current_dist)
            drift_report['features'][f'feature_{i}'] = {
                'psi': psi,
                'drifted': psi > self.psi_threshold
            }
            
            if psi > self.psi_threshold:
                drift_report['drifted_features'].append(f'feature_{i}')
        
        drift_report['dataset_drift'] = len(drift_report['drifted_features']) > 0
        return drift_report
    
    def ks_test(self, X_ref: np.ndarray, X_current: np.ndarray) -> dict:
        """KS 检验"""
        results = {}
        for i in range(X_ref.shape[1]):
            statistic, pvalue = stats.ks_2samp(X_ref[:, i], X_current[:, i])
            results[f'feature_{i}'] = {
                'statistic': statistic,
                'pvalue': pvalue,
                'drifted': pvalue < 0.05
            }
        return results

# 使用示例
detector = DriftDetector(psi_threshold=0.2)
detector.fit(X_train)
drift_result = detector.detect_drift(X_production)
```

### 3. MLflow 模型监控

```python
import mlflow
from mlflow.tracking import MlflowClient

# 记录模型指标
with mlflow.start_run():
    # 训练指标
    mlflow.log_metric("train_accuracy", 0.95)
    mlflow.log_metric("train_f1", 0.93)
    
    # 验证指标
    mlflow.log_metric("val_accuracy", 0.92)
    mlflow.log_metric("val_f1", 0.90)
    
    # 模型签名
    signature = infer_signature(X_train, y_pred)
    mlflow.sklearn.log_model(model, "model", signature=signature)

# 生产监控
class ProductionMonitor:
    def __init__(self, model_name):
        self.client = MlflowClient()
        self.model_name = model_name
        self.predictions = []
        self.latencies = []
    
    def log_prediction(self, features, prediction, latency_ms, actual=None):
        """记录预测日志"""
        self.predictions.append({
            'timestamp': datetime.now(),
            'features': features,
            'prediction': prediction,
            'actual': actual,
            'latency_ms': latency_ms
        })
    
    def calculate_metrics(self, window_size=1000):
        """计算滑动窗口指标"""
        recent = self.predictions[-window_size:]
        
        metrics = {
            'avg_latency': np.mean([p['latency_ms'] for p in recent]),
            'p99_latency': np.percentile([p['latency_ms'] for p in recent], 99),
            'prediction_distribution': Counter([p['prediction'] for p in recent])
        }
        
        # 如果有真实标签，计算准确率
        labeled = [p for p in recent if p['actual'] is not None]
        if labeled:
            y_true = [p['actual'] for p in labeled]
            y_pred = [p['prediction'] for p in labeled]
            metrics['accuracy'] = accuracy_score(y_true, y_pred)
        
        return metrics
```

### 4. Prometheus + Grafana 监控

```python
# model_metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# 定义指标
PREDICTION_COUNTER = Counter(
    'model_predictions_total',
    'Total predictions',
    ['model_version', 'prediction_class']
)

PREDICTION_LATENCY = Histogram(
    'model_prediction_latency_seconds',
    'Prediction latency',
    ['model_version'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

MODEL_ACCURACY = Gauge(
    'model_accuracy',
    'Model accuracy on labeled data',
    ['model_version']
)

FEATURE_DRIFT = Gauge(
    'feature_psi_score',
    'PSI score for feature drift',
    ['feature_name']
)

class MonitoredModel:
    def __init__(self, model, version="1.0"):
        self.model = model
        self.version = version
        start_http_server(8000)  # 暴露 /metrics 端点
    
    def predict(self, X):
        start = time.time()
        predictions = self.model.predict(X)
        latency = time.time() - start
        
        # 记录指标
        PREDICTION_LATENCY.labels(model_version=self.version).observe(latency)
        
        for pred in predictions:
            PREDICTION_COUNTER.labels(
                model_version=self.version,
                prediction_class=str(pred)
            ).inc()
        
        return predictions
```

```yaml
# docker-compose.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 5. 实时概念漂移检测

```python
from skmultiflow.drift_detection import ADWIN, PageHinkley

class ConceptDriftMonitor:
    def __init__(self):
        # ADWIN: 自适应窗口算法
        self.adwin = ADWIN(delta=0.002)
        # Page-Hinkley 检验
        self.ph = PageHinkley(min_instances=30, delta=0.005)
        self.errors = []
    
    def update(self, y_true, y_pred):
        """更新漂移检测器"""
        error = int(y_true != y_pred)
        self.errors.append(error)
        
        # 添加到 ADWIN
        self.adwin.add_element(error)
        
        # 添加到 Page-Hinkley
        self.ph.add_element(error)
        
        # 检查漂移
        drift_detected = self.adwin.detected_change() or self.ph.detected_change()
        
        return {
            'adwin_detected': self.adwin.detected_change(),
            'ph_detected': self.ph.detected_change(),
            'any_drift': drift_detected,
            'current_error_rate': np.mean(self.errors[-100:])
        }
    
    def reset(self):
        """重置检测器"""
        self.adwin.reset()
        self.ph.reset()
        self.errors = []

# 使用示例
monitor = ConceptDriftMonitor()
for y_true, y_pred in zip(y_true_stream, y_pred_stream):
    result = monitor.update(y_true, y_pred)
    if result['any_drift']:
        print(f"概念漂移检测到！当前错误率: {result['current_error_rate']}")
        # 触发模型重训练
```

## 示例

### 完整的监控仪表盘

```python
# monitoring_dashboard.py
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

class MonitoringDashboard:
    def __init__(self):
        st.set_page_config(page_title="ML Model Monitoring", layout="wide")
    
    def render(self):
        st.title("🤖 Model Monitoring Dashboard")
        
        # 侧边栏
        st.sidebar.header("配置")
        model_version = st.sidebar.selectbox(
            "模型版本", ["v1.0", "v1.1", "v2.0"]
        )
        time_range = st.sidebar.selectbox(
            "时间范围", ["1小时", "24小时", "7天", "30天"]
        )
        
        # 关键指标
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("预测总数", "1.2M", "+5%")
        with col2:
            st.metric("平均延迟", "45ms", "-2ms")
        with col3:
            st.metric("准确率", "94.2%", "-0.3%")
        with col4:
            st.metric("数据漂移", "⚠️ 警告", "2个特征")
        
        # 性能趋势图
        st.subheader("性能趋势")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=accuracy_history,
            mode='lines', name='准确率'
        ))
        fig.add_hline(y=0.90, line_dash="dash", line_color="red",
                     annotation_text="阈值")
        st.plotly_chart(fig, use_container_width=True)
        
        # 特征漂移热力图
        st.subheader("特征漂移检测")
        drift_data = self.get_drift_data()
        st.dataframe(drift_data.style.background_gradient(cmap='YlOrRd'))
        
        # 预测分布
        st.subheader("预测分布")
        fig2 = go.Figure(data=[go.Pie(
            labels=['Class 0', 'Class 1', 'Class 2'],
            values=[45, 35, 20]
        )])
        st.plotly_chart(fig2)

if __name__ == "__main__":
    dashboard = MonitoringDashboard()
    dashboard.render()
```

## 应用场景

| 场景 | 监控重点 | 告警策略 |
|------|----------|----------|
| **信贷风控** | 特征漂移、KS值下降 | PSI > 0.25 立即告警 |
| **推荐系统** | 点击率变化、冷启动性能 | CTR 下降 10% 告警 |
| **医疗诊断** | 准确率、召回率 | 任何指标下降都需人工介入 |
| **广告投放** | 转化率、延迟 | 转化率异常波动告警 |
| **反欺诈** | 误杀率、漏报率 | 误杀率 > 1% 告警 |

## 面试要点

Q: 数据漂移和概念漂移有什么区别？
A: 
- **数据漂移**: $P(X)$ 变化，即输入特征的分布发生变化，但 $P(Y\|X)$ 关系不变
- **概念漂移**: $P(Y\|X)$ 变化，即特征与目标的关系发生变化，即使特征分布不变
- 实际中两者常同时发生，需用 PSI、KS 检验等方法检测数据漂移，用误差监控检测概念漂移

Q: PSI 指标如何计算和解读？
A: PSI 计算公式：$PSI = \sum (Actual - Expected) \times \ln(Actual/Expected)$
- PSI < 0.1: 无显著变化，绿色
- 0.1 ≤ PSI < 0.25: 轻微变化，黄色，需关注
- PSI ≥ 0.25: 显著变化，红色，必须处理

Q: 如何处理检测到的模型漂移？
A: 处理流程：
   1. **告警通知**: 立即通知相关团队
   2. **根因分析**: 确定是数据问题还是真实漂移
   3. **临时措施**: 切换备用模型或规则系统
   4. **数据收集**: 收集新数据标注
   5. **模型重训练**: 使用新数据重新训练
   6. **A/B 测试**: 验证新模型效果后上线

Q: 没有标签时如何监控模型性能？
A: 无标签监控方法：
   - **数据漂移检测**: PSI、KS 检验监控特征分布
   - **预测分布监控**: 观察输出概率分布变化
   - **上游数据验证**: 检查数据源质量
   - **业务指标监控**: 通过间接业务指标推断
   - **主动学习**: 定期采样请求人工标注

Q: 实时漂移检测有哪些算法？
A: 常用算法：
   - **ADWIN**: 自适应窗口，动态调整检测窗口
   - **Page-Hinkley**: 累积和检验
   - **DDM (Drift Detection Method)**: 基于错误率监控
   - **EDDM**: 早期漂移检测
   - **HDDM**: Hoeffding 漂移检测

## 相关概念

### 数据结构
- [数据流处理](../ml-fundamentals/data-processing.md) - 实时数据管道
- [特征工程](../ml-fundamentals/feature-engineering.md) - 特征监控

### 算法
- [统计检验](../mathematics/statistics/hypothesis-testing.md) - KS 检验、卡方检验
- [在线学习](../ml-fundamentals/online-learning.md) - 增量更新

### 复杂度分析
- **漂移检测复杂度**: $O(n)$ 每次更新
- **PSI 计算**: $O(k)$，$k$ 为分箱数
- **ADWIN 空间**: $O(\log n)$，$n$ 为窗口大小

### 系统实现
- [Docker](../../cloud-devops/docker.md) - 监控服务容器化
- [Kubernetes](../../cloud-devops/kubernetes/README.md) - 监控部署
- [模型部署](./model-deployment.md) - 监控集成
- [A/B 测试](./ab-testing.md) - 实验监控
