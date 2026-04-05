# 线性变换 (Linear Transformations)

## 简介

**线性变换**（Linear Transformations）是线性代数中的核心概念，描述了向量空间之间的映射关系。一个变换 T 是线性的，当且仅当它满足加性和齐次性。线性变换在计算机图形学、机器学习、信号处理等领域有广泛应用。

## 核心概念

### 定义与性质

**线性变换的定义：**
变换 T: V → W 是线性的，如果满足：
1. **加性**：T(u + v) = T(u) + T(v)
2. **齐次性**：T(c·v) = c·T(v)

**常见线性变换：**
- **缩放**（Scaling）：各坐标按比例缩放
- **旋转**（Rotation）：绕原点旋转
- **投影**（Projection）：投影到子空间
- **反射**（Reflection）：关于直线或平面的镜像
- **剪切**（Shear）：沿某一方向的倾斜变换

### 变换矩阵

**矩阵表示：**
```
T(v) = A·v
其中 A 是 m×n 矩阵，v 是 n 维向量
```

**二维变换矩阵：**
| 变换类型 | 矩阵 |
|---------|------|
| 缩放 (sx, sy) | [sx 0; 0 sy] |
| 旋转 θ | [cosθ -sinθ; sinθ cosθ] |
| 投影到x轴 | [1 0; 0 0] |
| 关于x轴反射 | [1 0; 0 -1] |

### 核与像

**核（Kernel/Null Space）：**
```
Ker(T) = {v ∈ V | T(v) = 0}
```
- 所有被映射到零向量的输入向量集合
- 维度称为**零度**（nullity）

**像（Image/Range）：**
```
Im(T) = {T(v) | v ∈ V}
```
- 所有可能的输出向量集合
- 维度称为**秩**（rank）

**秩-零度定理：**
```
dim(V) = rank(T) + nullity(T)
```

### 可逆性

**可逆变换：**
变换 T 可逆 ⟺ 存在逆变换 T⁻¹ 使得 T⁻¹(T(v)) = v

**条件：**
- T 是双射（一一对应且满射）
- det(A) ≠ 0（变换矩阵行列式非零）
- Ker(T) = {0}（零空间只有零向量）

## 实现方式

```python
import numpy as np
from typing import Tuple

class LinearTransformation:
    """线性变换类"""
    
    def __init__(self, matrix: np.ndarray):
        self.A = matrix
        self.m, self.n = matrix.shape
    
    def transform(self, v: np.ndarray) -> np.ndarray:
        """应用变换 T(v) = A·v"""
        return self.A @ v
    
    def is_invertible(self) -> bool:
        """判断变换是否可逆"""
        if self.m != self.n:
            return False
        return np.linalg.det(self.A) != 0
    
    def inverse(self) -> 'LinearTransformation':
        """求逆变换"""
        if not self.is_invertible():
            raise ValueError("变换不可逆")
        return LinearTransformation(np.linalg.inv(self.A))
    
    def kernel(self) -> np.ndarray:
        """计算核空间（零空间）"""
        # 使用SVD求解零空间
        u, s, vh = np.linalg.svd(self.A)
        tolerance = np.finfo(s.dtype).eps * max(self.A.shape) * s[0]
        rank = np.sum(s > tolerance)
        null_space = vh[rank:].T
        return null_space
    
    def image(self) -> np.ndarray:
        """计算像空间（列空间）"""
        u, s, vh = np.linalg.svd(self.A)
        tolerance = np.finfo(s.dtype).eps * max(self.A.shape) * s[0]
        rank = np.sum(s > tolerance)
        return u[:, :rank]
    
    def rank(self) -> int:
        """计算秩"""
        return np.linalg.matrix_rank(self.A)
    
    def nullity(self) -> int:
        """计算零度"""
        return self.n - self.rank()


# 常见二维变换工厂函数
def rotation_matrix(theta: float) -> np.ndarray:
    """创建旋转矩阵"""
    return np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

def scaling_matrix(sx: float, sy: float) -> np.ndarray:
    """创建缩放矩阵"""
    return np.array([
        [sx, 0],
        [0, sy]
    ])

def projection_matrix(axis: str = 'x') -> np.ndarray:
    """创建投影矩阵"""
    if axis == 'x':
        return np.array([[1, 0], [0, 0]])
    else:
        return np.array([[0, 0], [0, 1]])

def reflection_matrix(axis: str = 'x') -> np.ndarray:
    """创建反射矩阵"""
    if axis == 'x':
        return np.array([[1, 0], [0, -1]])
    elif axis == 'y':
        return np.array([[-1, 0], [0, 1]])
    else:  # y=x
        return np.array([[0, 1], [1, 0]])


# 使用示例
if __name__ == "__main__":
    # 创建一个旋转45度的变换
    theta = np.pi / 4
    A = rotation_matrix(theta)
    T = LinearTransformation(A)
    
    # 变换向量 (1, 0)
    v = np.array([1, 0])
    v_transformed = T.transform(v)
    print(f"旋转变换: {v} -> {v_transformed}")
    
    # 计算秩和零度
    print(f"Rank: {T.rank()}, Nullity: {T.nullity()}")
    
    # 投影变换（不可逆）
    P = LinearTransformation(projection_matrix('x'))
    print(f"投影变换可逆? {P.is_invertible()}")
    print(f"投影变换的核空间:\n{P.kernel()}")
```

## 应用场景

### 1. 计算机图形学
- **3D渲染**：模型-视图-投影变换链
- **动画**：骨骼动画中的坐标变换
- **图像处理**：旋转、缩放、裁剪

### 2. 机器学习
- **PCA降维**：正交投影到低维子空间
- **特征变换**：将数据映射到新特征空间
- **神经网络**：层与层之间的线性映射

### 3. 数据压缩
- **JPEG压缩**：离散余弦变换（DCT）
- **小波变换**：多分辨率分析

### 4. 机器人学
- **坐标系转换**：世界坐标系到机器人坐标系
- **运动学**：关节角度到末端位姿的映射

## 面试要点

**Q1: 什么是线性变换？必须满足哪两个条件？**
A: 线性变换是保持向量加法和标量乘法的映射 T: V → W。必须满足：
- 加性：T(u+v) = T(u) + T(v)
- 齐次性：T(cv) = cT(v)

**Q2: 秩-零度定理是什么？**
A: 对于线性变换 T: V → W，有 dim(V) = rank(T) + nullity(T)。即原空间维数等于像空间维数加上核空间维数。

**Q3: 如何判断一个线性变换是否可逆？**
A: 以下条件等价：
- T 是双射
- 变换矩阵 A 的行列式 det(A) ≠ 0
- rank(A) = n（满秩）
- Ker(T) = {0}（零空间只有零向量）

**Q4: 旋转、缩放、投影的变换矩阵分别是什么？**
A:
- 旋转θ：[cosθ -sinθ; sinθ cosθ]
- 缩放(sx, sy)：[sx 0; 0 sy]
- 投影到x轴：[1 0; 0 0]

**Q5: 线性变换在机器学习中的应用？**
A: PCA降维使用正交投影；神经网络中的全连接层是线性变换+激活函数；特征工程中常用线性变换标准化或归一化数据。

## 相关概念

### 数据结构
- [矩阵](../data-structures/matrix.md) - 线性变换的数值表示
- [数组](../data-structures/array.md) - 向量存储

### 算法
- [矩阵乘法](../algorithms/matrix-multiplication.md) - 变换的应用
- [高斯消元](../algorithms/gaussian-elimination.md) - 求解线性系统
- [SVD分解](../algorithms/svd-algorithm.md) - 分解变换矩阵

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 矩阵乘法复杂度为 O(n³) 或更优
- [空间复杂度](../../references/space-complexity.md) - 存储变换矩阵需要 O(n²)

### 系统实现
- [计算机图形学](../../references/computer-graphics.md) - 变换的应用领域
- [图像处理](../../references/image-processing.md) - 仿射变换应用
- [CUDA](../../references/cuda.md) - GPU加速矩阵运算
