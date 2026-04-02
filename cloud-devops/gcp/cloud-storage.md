# 云存储 (Cloud Storage)

## 简介

Google Cloud Storage 是 GCP 提供的完全托管的对象存储服务，提供全球统一、高可用、高持久性的数据存储。支持从几字节到数 TB 的对象存储，适用于数据湖、备份、内容分发和大数据分析等场景。

## 核心概念

### 存储桶 (Buckets)
- **全局唯一命名空间**: 所有存储桶名称全球唯一
- **地理位置**: 多区域 (Multi-Region)、双区域 (Dual-Region)、区域 (Region)
- **存储类别**: 标准、近线、冷线、归档
- **标签和元数据**: 组织和管理存储资源

### 存储类别
| 类别 | 适用场景 | 最小存储时间 | 检索费用 |
|------|----------|--------------|----------|
| **Standard** | 频繁访问数据 | 无 | 无 |
| **Nearline** | 月访问少于1次 | 30天 | 较低 |
| **Coldline** | 季度访问少于1次 | 90天 | 中等 |
| **Archive** | 年度访问少于1次 | 365天 | 较高 |

### 对象管理
- **对象版本控制**: 保留对象的多个版本
- **对象生命周期管理**: 自动删除或转换存储类别
- **对象组合**: 将多个对象组合成一个大对象
- **分块上传**: 支持大文件并行上传

### 访问控制
- **IAM**: 细粒度的身份和访问管理
- **ACL**: 访问控制列表（已逐渐弃用）
- **签名 URL**: 临时授权访问（V2/V4 签名）
- **统一桶级访问**: 简化访问控制管理

### 数据保护
- **加密**: 服务端加密（Google 管理或 CMEK）
- **保留策略**: 合规性要求的对象锁定
- **对象持有**: 法律诉讼保留

## 实现方式

### 存储桶创建和配置
```bash
# 创建多区域存储桶
gsutil mb -p my-project -c Standard -l US gs://my-unique-bucket-name

# 创建带标签和版本的存储桶
gsutil mb -l us-central1 gs://versioned-bucket
gsutil versioning set on gs://versioned-bucket

# 使用 Terraform
resource "google_storage_bucket" "data_bucket" {
  name          = "my-data-bucket"
  location      = "US"
  storage_class = "STANDARD"
  
  versioning {
    enabled = true
  }
  
  labels = {
    environment = "production"
    team        = "data-engineering"
  }
  
  lifecycle_rule {
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 30
    }
  }
  
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }
}
```

### 对象操作
```bash
# 上传文件
gsutil cp local-file.txt gs://my-bucket/
gsutil cp -r local-directory/ gs://my-bucket/remote-directory/

# 下载文件
gsutil cp gs://my-bucket/remote-file.txt ./local-file.txt
gsutil cp -r gs://my-bucket/remote-directory/ ./local-directory/

# 列出对象
gsutil ls gs://my-bucket/
gsutil ls -l gs://my-bucket/prefix/

# 删除对象
gsutil rm gs://my-bucket/file.txt
gsutil rm -r gs://my-bucket/directory/
```

### Python SDK 示例
```python
from google.cloud import storage
from google.cloud.storage import Blob

# 初始化客户端
storage_client = storage.Client()

# 创建存储桶
def create_bucket(bucket_name, location='US'):
    bucket = storage_client.bucket(bucket_name)
    bucket.location = location
    bucket.storage_class = 'STANDARD'
    return storage_client.create_bucket(bucket)

# 上传对象
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # 分块上传大文件
    blob.chunk_size = 5 * 1024 * 1024  # 5MB chunks
    blob.upload_from_filename(source_file_name)
    
    print(f"File {source_file_name} uploaded to {destination_blob_name}")

# 生成签名 URL（临时访问）
def generate_signed_url(bucket_name, blob_name, expiration=3600):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    url = blob.generate_signed_url(
        version='v4',
        expiration=expiration,
        method='GET'
    )
    return url

# 流式上传（适合大文件）
def stream_upload(bucket_name, blob_name, file_obj):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # 使用可恢复上传
    blob.upload_from_file(file_obj, content_type='application/octet-stream')
    return blob.public_url

# 对象元数据管理
def set_metadata(bucket_name, blob_name, metadata):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    
    blob.metadata = metadata
    blob.patch()
    
    return blob.metadata
```

### 生命周期管理配置
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {
          "type": "SetStorageClass",
          "storageClass": "NEARLINE"
        },
        "condition": {
          "age": 30,
          "matchesPrefix": ["logs/"]
        }
      },
      {
        "action": {
          "type": "SetStorageClass",
          "storageClass": "COLDLINE"
        },
        "condition": {
          "age": 90,
          "matchesPrefix": ["logs/"]
        }
      },
      {
        "action": {
          "type": "Delete"
        },
        "condition": {
          "age": 365,
          "numNewerVersions": 3
        }
      },
      {
        "action": {
          "type": "AbortIncompleteMultipartUpload"
        },
        "condition": {
          "age": 7
        }
      }
    ]
  }
}
```

### 签名 URL 生成（V4）
```python
import datetime
from google.cloud import storage

def generate_upload_signed_url_v4(bucket_name, blob_name, content_type='application/octet-stream'):
    """生成用于上传的签名 URL（PUT 请求）"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version='v4',
        expiration=datetime.timedelta(minutes=15),
        method='PUT',
        content_type=content_type,
    )

    return url

# 客户端使用签名 URL 上传
def upload_with_signed_url(signed_url, file_path, content_type='application/octet-stream'):
    import requests
    
    with open(file_path, 'rb') as f:
        response = requests.put(
            signed_url,
            data=f,
            headers={'Content-Type': content_type}
        )
    
    return response.status_code == 200
```

## 示例

### 数据湖架构
```
┌───────────────┐     ┌───────────────┐     ┌─────────────────────┐
│  Data Sources │────▶│  Cloud Pub/Sub│────▶│  Cloud Dataflow     │
│  (IoT/Apps)   │     │  (Streaming)  │     │  (ETL Processing)   │
└───────────────┘     └───────────────┘     └──────────┬──────────┘
                                                       │
                              ┌────────────────────────┼────────────────────────┐
                              │                        │                        │
                     ┌────────▼────────┐      ┌───────▼────────┐      ┌──────▼───────┐
                     │  Raw Zone       │      │  Processed     │      │  Curated     │
                     │  (Standard)     │      │  (Standard)    │      │  (Standard)  │
                     │  Parquet/ORC    │      │  Cleaned Data  │      │  Analytics   │
                     └────────┬────────┘      └───────┬────────┘      └──────┬───────┘
                              │                        │                      │
                     ┌────────▼────────┐      ┌───────▼────────┐      ┌──────▼───────┐
                     │  Archive Zone   │      │  BigQuery      │      │  ML/AI       │
                     │  (Coldline)     │      │  External Tables│     │  Training    │
                     └─────────────────┘      └────────────────┘      └──────────────┘
```

### 静态网站托管
```bash
# 创建用于托管网站的存储桶
gsutil mb -b on gs://www.example.com

# 配置存储桶为网站
gsutil web set -m index.html -e 404.html gs://www.example.com

# 设置公共访问权限（谨慎使用）
gsutil iam ch allUsers:objectViewer gs://www.example.com

# 上传网站内容
gsutil cp -r ./dist/* gs://www.example.com/

# 配置 CORS
cat > cors.json <<EOF
[{
  "origin": ["https://example.com"],
  "method": ["GET", "HEAD"],
  "responseHeader": ["Content-Type"],
  "maxAgeSeconds": 3600
}]
EOF
gsutil cors set cors.json gs://www.example.com
```

## 应用场景

| 场景 | 解决方案 | 最佳实践 |
|------|----------|----------|
| **内容分发** | Cloud CDN + Cloud Storage | 使用多区域桶，配置缓存策略 |
| **备份与归档** | 生命周期规则 + Archive | 自动降级存储类别，降低长期成本 |
| **大数据分析** | BigQuery + Cloud Storage | 使用外部表查询，Parquet/ORC 格式 |
| **ML 数据集** | 多区域桶 + 签名 URL | 训练数据版本控制，安全访问 |
| **日志归档** | 标准→近线→冷线生命周期 | 30天→90天→删除的自动转换 |
| **灾难恢复** | 双区域桶 + 对象版本 | 跨区域冗余，防止数据丢失 |

## 面试要点

Q: Cloud Storage 与 AWS S3 的主要区别？
A: Cloud Storage 提供统一的全局命名空间（无需选择特定终端节点）、自动多区域冗余（US/EU/Asia）、按分钟计费（而非小时）、与 GCP 服务更紧密集成（BigQuery、Dataflow）。

Q: 如何选择存储类别？
A: 根据访问频率：Standard（频繁访问，延迟敏感）、Nearline（月访问<1次）、Coldline（季度访问<1次）、Archive（年访问<1次）。注意检索费用和最小存储时间。

Q: 签名 URL V2 和 V4 的区别？
A: V4 使用更安全的签名算法（RSA-SHA256 vs HMAC-SHA1），支持更精细的权限控制，URL 有效期最长 7 天（V2 最长 1 周），是 Google 推荐的新标准。

Q: 如何实现对象版本控制？
A: 启用版本控制后，每次覆盖或删除都会创建非当前版本，保留原始数据。可配置生命周期规则自动删除旧版本（保留最近 N 个或超过 N 天的版本）。

Q: 生命周期规则的执行顺序？
A: 生命周期规则按定义顺序执行，但 Cloud Storage 可能合并操作。常见模式：30天→Nearline，90天→Coldline，365天→删除。AbortIncompleteMultipartUpload 应优先配置。

## 相关概念

### 数据结构
- **一致性哈希**: 对象在存储节点间的分布
- **B树索引**: 对象元数据索引结构
- **Merkle树**: 数据完整性验证

### 算法
- **纠删码**: 数据冗余和容错（Reed-Solomon）
- **分块算法**: 大文件分片上传和并行传输
- **去重算法**: 重复数据删除优化

### 复杂度分析
- **读写延迟**: 强一致性读取 O(1)，列表操作 O(n)
- **存储成本**: 标准存储 O(n)，归档存储 O(n) 但检索成本 O(1) 较高

### 系统实现
- **Colossus**: Google 分布式文件系统后端
- **Bigtable**: 元数据存储索引
- **GFS/Spanner**: 底层存储一致性保证

### 对比参考
- [AWS S3](../aws/s3.md) - AWS 对象存储对比
- [Kubernetes Persistent Volumes](../kubernetes/persistent-volumes.md) - 持久化存储
- [分布式文件系统](../../distributed-systems/distributed-file-system.md) - 文件系统原理
- [一致性模型](../../distributed-systems/consistency-models.md) - 存储一致性
