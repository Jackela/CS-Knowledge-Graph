# 模型部署 (Model Deployment)

## 简介

模型部署是将训练好的机器学习模型从开发环境迁移到生产环境，使其能够为实际业务提供预测服务的过程。成功的模型部署需要考虑性能、可扩展性、可靠性和运维成本等多个维度。

## 核心概念

### 部署模式

| 模式 | 描述 | 适用场景 |
|------|------|----------|
| **在线服务 (Online)** | 实时响应请求，低延迟 | 推荐系统、欺诈检测 |
| **批量处理 (Batch)** | 定期处理大量数据 | 日报生成、用户分群 |
| **流式处理 (Streaming)** | 持续处理数据流 | 实时监控、IoT 数据处理 |
| **边缘部署 (Edge)** | 部署到边缘设备 | 移动端、嵌入式设备 |

### 模型服务架构

```
┌─────────────────────────────────────────────────────────┐
│                      Load Balancer                       │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ Model   │   │ Model   │   │ Model   │
   │ Server  │   │ Server  │   │ Server  │
   │  (v1)   │   │  (v2)   │   │  (v1)   │
   └─────────┘   └─────────┘   └─────────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              ┌───────────────┐
              │  Model Store  │
              │  (S3/MinIO)   │
              └───────────────┘
```

### 推理优化技术

- **模型量化 (Quantization)**: FP32 → INT8/FP16
- **模型剪枝 (Pruning)**: 移除不重要的权重
- **知识蒸馏 (Knowledge Distillation)**: 小模型学习大模型
- **批处理推理 (Batch Inference)**: 合并请求提高效率
- **模型编译 (Compilation)**: TVM, TensorRT 优化

## 实现方式

### 1. REST API 部署 (Flask/FastAPI)

```python
# FastAPI 模型服务示例
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="ML Model Service")

# 加载模型
model = joblib.load("models/rf_classifier.pkl")

class PredictionRequest(BaseModel):
    features: list[float]

class PredictionResponse(BaseModel):
    prediction: int
    probability: list[float]
    model_version: str

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        features = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0].tolist()
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=probability,
            model_version="v1.0.0"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查
@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}
```

### 2. 使用 MLflow 部署

```python
# MLflow 模型部署
import mlflow
from mlflow.models.signature import infer_signature

# 记录模型
with mlflow.start_run():
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name="rf_classifier"
    )

# 部署为 REST 服务
# mlflow models serve -m models:/{model_name}/{version} -p 5001

# 或使用 MLflow 部署到 SageMaker/ Azure ML
import mlflow.deployments as deployments

client = deployments.get_deploy_client("sagemaker")
client.create_deployment(
    name="my-deployment",
    model_uri="models:/{model_name}/Production",
    config={"instance_type": "ml.m5.xlarge"}
)
```

### 3. 使用 TorchServe 部署 PyTorch 模型

```python
# model_handler.py
from ts.torch_handler.base_handler import BaseHandler
import torch
import json

class ModelHandler(BaseHandler):
    def initialize(self, context):
        self.manifest = context.manifest
        properties = context.system_properties
        model_dir = properties.get("model_dir")
        
        # 加载模型
        self.model = torch.jit.load(f"{model_dir}/model.pt")
        self.model.eval()
        
        # 加载预处理配置
        with open(f"{model_dir}/preprocess.json") as f:
            self.preprocess = json.load(f)
    
    def preprocess(self, data):
        """预处理输入数据"""
        return torch.tensor(data)
    
    def inference(self, data):
        """模型推理"""
        with torch.no_grad():
            return self.model(data)
    
    def postprocess(self, inference_output):
        """后处理输出"""
        return inference_output.tolist()
```

```bash
# 打包模型
torch-model-archiver \
    --model-name resnet18 \
    --version 1.0 \
    --model-file model.py \
    --serialized-file resnet18.pth \
    --handler model_handler.py \
    --export-path model_store

# 启动服务
torchserve --start \
    --model-store model_store \
    --models resnet18=resnet18.mar
```

### 4. 使用 Triton Inference Server

```python
# Triton 客户端示例
import tritonclient.http as httpclient
import numpy as np

client = httpclient.InferenceServerClient(url="localhost:8000")

# 准备输入
input_data = np.random.rand(1, 3, 224, 224).astype(np.float32)
inputs = [httpclient.InferInput("input", input_data.shape, "FP32")]
inputs[0].set_data_from_numpy(input_data)

# 设置输出
outputs = [httpclient.InferRequestedOutput("output")]

# 推理
results = client.infer("resnet50", inputs, outputs=outputs)
output_data = results.as_numpy("output")
```

### 5. 使用 Kubeflow Serving

```yaml
# kfservice.yaml
apiVersion: serving.kubeflow.org/v1beta1
kind: InferenceService
metadata:
  name: sklearn-iris
spec:
  predictor:
    sklearn:
      storageUri: "gs://your-bucket/models/iris"
      resources:
        limits:
          cpu: "1"
          memory: 2Gi
        requests:
          cpu: "100m"
          memory: 256Mi
  transformer:
    containers:
      - image: gcr.io/your-project/transformer:latest
        name: transformer
```

### 6. 边缘部署 (TensorFlow Lite)

```python
# 转换为 TFLite 模型
import tensorflow as tf

converter = tf.lite.TFLiteConverter.from_saved_model('saved_model_dir')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# 保存模型
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)

# 量化配置
converter.target_spec.supported_types = [tf.float16]  # FP16 量化
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8  # INT8 量化
]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8
```

## 示例

### 完整的 Docker 部署流程

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY model/ ./model/
COPY app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```python
# app.py - 生产级服务
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram
import asyncio
import redis.asyncio as redis

app = FastAPI()

# 指标监控
PREDICTION_COUNTER = Counter('predictions_total', 'Total predictions')
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency')

# 缓存连接
cache = redis.Redis(host='redis', port=6379)

@app.post("/predict")
@PREDICTION_LATENCY.time()
async def predict(request: PredictionRequest):
    # 缓存检查
    cache_key = f"pred:{hash(tuple(request.features))}"
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 推理
    result = await run_inference(request.features)
    
    # 缓存结果
    await cache.setex(cache_key, 300, json.dumps(result))
    
    PREDICTION_COUNTER.inc()
    return result
```

## 应用场景

| 场景 | 部署方式 | 技术栈 |
|------|----------|--------|
| **电商推荐** | 在线服务 | TensorFlow Serving, Redis |
| **风控系统** | 流式处理 | Flink, Kafka, 在线模型 |
| **图像识别** | 边缘部署 | TensorFlow Lite, Core ML |
| **广告投放** | 批量+在线 | Spark ML, REST API |
| **智能客服** | 在线服务 | Kubernetes, GPU 推理 |

## 面试要点

Q: 模型部署有哪些主要挑战？
A: 主要挑战包括：
   - **性能**: 低延迟、高吞吐的推理需求
   - **可扩展性**: 应对流量峰值的能力
   - **版本管理**: 模型版本控制和回滚机制
   - **监控**: 模型性能和健康状态的实时监控
   - **资源优化**: GPU/CPU 资源的有效利用

Q: 在线服务 vs 批量处理如何选择？
A: 选择依据：
   - 在线服务：需要实时响应，延迟敏感（<100ms）
   - 批量处理：可接受延迟，数据量大，计算密集
   - 混合模式：实时特征 + 批量模型更新

Q: 如何实现模型 A/B 测试？
A: 实现方式：
   - 流量分割：按用户 ID 哈希或随机分配
   - 影子流量：新模型处理但不影响线上结果
   - 金丝雀发布：逐步增加新模型流量比例
   - 多臂老虎机：动态调整流量分配

Q: 模型量化有什么优缺点？
A: 优点：
   - 减少模型大小（4x）
   - 降低内存占用
   - 加速推理（特别是 INT8）
   缺点：
   - 可能损失精度
   - 需要校准数据
   - 某些层不支持量化

Q: 如何保证模型服务的高可用？
A: 策略包括：
   - 多副本部署 + 负载均衡
   - 健康检查和自动重启
   - 模型预热避免冷启动
   - 降级策略（使用简单模型或规则系统）
   - 多可用区部署

## 相关概念

### 数据结构
- [缓存策略](../ml-fundamentals/data-processing.md) - Redis 缓存设计
- [版本控制](../ml-fundamentals/ml-pipeline.md) - 模型版本管理

### 算法
- [模型优化](../deep-learning/model-optimization.md) - 量化、剪枝、蒸馏
- [神经网络](../deep-learning/neural-networks.md) - 模型结构基础

### 复杂度分析
- **推理时间复杂度**: $O(n \cdot d)$，$n$ 为样本数，$d$ 为特征维度
- **空间复杂度**: 模型大小 + 运行时内存
- **并发模型**: 吞吐量 = $\frac{\text{并发数}}{\text{平均延迟}}$

### 系统实现
- [Docker](../../cloud-devops/docker.md) - 容器化部署
- [Kubernetes](../../cloud-devops/kubernetes/README.md) - 容器编排
- [特征存储](./feature-store.md) - 特征在线获取
- [模型监控](./model-monitoring.md) - 生产环境监控
