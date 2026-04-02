# 计算几何 (Computational Geometry)

## 简介

**计算几何**（Computational Geometry）研究解决几何问题的算法，广泛应用于计算机图形学、机器人学、GIS、CAD 等领域。核心问题包括凸包、最近点对、线段交、多边形处理等，需要处理浮点精度、退化情况等工程细节。

## 核心概念

### 基础几何运算

**向量运算：**
```python
# 点积: a·b = |a||b|cosθ
dot(a, b) = a.x * b.x + a.y * b.y

# 叉积: |a×b| = |a||b|sinθ
cross(a, b) = a.x * b.y - a.y * b.x

# 叉积符号含义:
# cross > 0: b 在 a 的逆时针方向
# cross < 0: b 在 a 的顺时针方向
# cross = 0: 共线
```

**方向判断：**
- `cross(b-a, c-a)` 判断点 c 相对于线段 ab 的位置

### 凸包算法

**凸包**：包含所有点的最小凸多边形

**Graham Scan - O(n log n)：**
1. 找最左下角的点作为极点
2. 按极角排序其他点
3. 使用栈维护凸包，叉积判断转向

**Andrew 单调链 - O(n log n)：**
1. 按 x 坐标排序
2. 分别构建下凸包和上凸包
3. 合并结果

### 线段交

**判断两线段相交：**
1. 快速排斥实验：包围盒是否相交
2. 跨立实验：`cross` 判断点是否在两侧

### 最近点对

**分治算法 - O(n log n)：**
1. 按 x 坐标排序，中线分割
2. 递归求解左右子集的最近点对
3. 检查跨中线的点对（只需检查最多6个点）

## 实现方式

```python
import math
from typing import List, Tuple
from functools import cmp_to_key

class Point:
    """二维点类"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9

def cross(o: Point, a: Point, b: Point) -> float:
    """叉积: (a-o) × (b-o)"""
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)

def dot(a: Point, b: Point) -> float:
    """点积"""
    return a.x * b.x + a.y * b.y

def dist_sq(a: Point, b: Point) -> float:
    """距离平方"""
    return (a.x - b.x)**2 + (a.y - b.y)**2

def dist(a: Point, b: Point) -> float:
    """欧几里得距离"""
    return math.sqrt(dist_sq(a, b))


class ConvexHull:
    """凸包算法"""
    
    @staticmethod
    def graham_scan(points: List[Point]) -> List[Point]:
        """
        Graham Scan 凸包算法
        时间: O(n log n)
        """
        if len(points) <= 1:
            return points
        
        # 找最左下角的点
        start = min(points, key=lambda p: (p.y, p.x))
        
        # 按极角排序
        def polar_angle(p: Point) -> float:
            return math.atan2(p.y - start.y, p.x - start.x)
        
        sorted_points = sorted(points, key=lambda p: (polar_angle(p), 
                                                      dist_sq(start, p)))
        
        # 构建凸包
        hull = []
        for p in sorted_points:
            while len(hull) >= 2 and cross(hull[-2], hull[-1], p) <= 0:
                hull.pop()
            hull.append(p)
        
        return hull
    
    @staticmethod
    def monotone_chain(points: List[Point]) -> List[Point]:
        """
        Andrew 单调链算法
        时间: O(n log n)
        """
        if len(points) <= 1:
            return points
        
        # 按 x 排序
        points = sorted(points, key=lambda p: (p.x, p.y))
        
        # 构建下凸包
        lower = []
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        
        # 构建上凸包
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        
        # 合并（去掉重复端点）
        return lower[:-1] + upper[:-1]


class SegmentIntersection:
    """线段交判断"""
    
    @staticmethod
    def on_segment(p: Point, q: Point, r: Point) -> bool:
        """判断 q 是否在线段 pr 上"""
        if min(p.x, r.x) <= q.x <= max(p.x, r.x) and \
           min(p.y, r.y) <= q.y <= max(p.y, r.y):
            return abs(cross(p, q, r)) < 1e-9
        return False
    
    @staticmethod
    def intersect(p1: Point, q1: Point, p2: Point, q2: Point) -> bool:
        """
        判断线段 p1q1 和 p2q2 是否相交
        """
        d1 = cross(p2, q2, p1)
        d2 = cross(p2, q2, q1)
        d3 = cross(p1, q1, p2)
        d4 = cross(p1, q1, q2)
        
        # 一般情况
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        
        # 共线情况
        if d1 == 0 and SegmentIntersection.on_segment(p2, p1, q2):
            return True
        if d2 == 0 and SegmentIntersection.on_segment(p2, q1, q2):
            return True
        if d3 == 0 and SegmentIntersection.on_segment(p1, p2, q1):
            return True
        if d4 == 0 and SegmentIntersection.on_segment(p1, q2, q1):
            return True
        
        return False


class ClosestPair:
    """最近点对"""
    
    @staticmethod
    def closest_pair(points: List[Point]) -> Tuple[float, Tuple[Point, Point]]:
        """
        分治法找最近点对
        时间: O(n log n)
        """
        if len(points) <= 3:
            return ClosestPair._brute_force(points)
        
        px = sorted(points, key=lambda p: p.x)
        py = sorted(points, key=lambda p: p.y)
        
        return ClosestPair._closest_recursive(px, py)
    
    @staticmethod
    def _brute_force(points: List[Point]) -> Tuple[float, Tuple[Point, Point]]:
        min_dist = float('inf')
        closest = None
        n = len(points)
        for i in range(n):
            for j in range(i + 1, n):
                d = dist(points[i], points[j])
                if d < min_dist:
                    min_dist = d
                    closest = (points[i], points[j])
        return min_dist, closest
    
    @staticmethod
    def _closest_recursive(px: List[Point], py: List[Point]) -> Tuple[float, Tuple[Point, Point]]:
        n = len(px)
        if n <= 3:
            return ClosestPair._brute_force(px)
        
        mid = n // 2
        mid_point = px[mid]
        
        # 分割
        pyl = [p for p in py if p.x <= mid_point.x]
        pyr = [p for p in py if p.x > mid_point.x]
        
        # 递归
        dl, pair_l = ClosestPair._closest_recursive(px[:mid], pyl)
        dr, pair_r = ClosestPair._closest_recursive(px[mid:], pyr)
        
        d = min(dl, dr)
        best_pair = pair_l if dl <= dr else pair_r
        
        # 检查跨中线区域
        strip = [p for p in py if abs(p.x - mid_point.x) < d]
        
        for i in range(len(strip)):
            for j in range(i + 1, min(i + 7, len(strip))):
                if strip[j].y - strip[i].y >= d:
                    break
                dst = dist(strip[i], strip[j])
                if dst < d:
                    d = dst
                    best_pair = (strip[i], strip[j])
        
        return d, best_pair


# 使用示例
if __name__ == "__main__":
    # 凸包测试
    points = [
        Point(0, 0), Point(1, 1), Point(2, 2),
        Point(0, 2), Point(2, 0), Point(1, 0.5)
    ]
    hull = ConvexHull.monotone_chain(points)
    print(f"凸包顶点: {hull}")
    
    # 线段交测试
    p1, q1 = Point(0, 0), Point(2, 2)
    p2, q2 = Point(0, 2), Point(2, 0)
    result = SegmentIntersection.intersect(p1, q1, p2, q2)
    print(f"线段相交: {result}")
    
    # 最近点对测试
    points = [Point(2, 3), Point(12, 30), Point(40, 50), 
              Point(5, 1), Point(12, 10), Point(3, 4)]
    min_dist, pair = ClosestPair.closest_pair(points)
    print(f"最近点对距离: {min_dist:.4f}, 点对: {pair}")
```

## 应用场景

### 1. 计算机图形学
- **碰撞检测**：包围盒、凸包相交测试
- **裁剪算法**：线段裁剪、多边形裁剪
- **网格生成**：Delaunay 三角剖分

### 2. GIS 地理信息
- **最短路径**：路网几何计算
- **空间索引**：R-tree、四叉树
- **区域分析**：多边形交集、并集

### 3. 机器人学
- **运动规划**：避障路径规划
- **抓取规划**：凸包分析稳定抓取
- **定位**：三角测量、多边定位

### 4. CAD/CAM
- **几何建模**：曲面求交
- **数控加工**：刀具路径规划
- **公差分析**：几何约束求解

## 面试要点

**Q1: 叉积的几何意义？**
A: 二维叉积 |a×b| = |a||b|sinθ，表示平行四边形面积。符号表示方向：正为逆时针，负为顺时针，0 为共线。

**Q2: Graham Scan 和 Andrew 算法的区别？**
A: Graham 按极角排序需要三角函数；Andrew 按 x 坐标排序，构建上下两个单调链，常数更小且更稳定。

**Q3: 最近点对分治算法为什么只需检查6个点？**
A: 鸽巢原理。将 d×2d 区域分成6个 d×(2d/3) 小格，每格最多1个点（否则子问题有更短距离），所以只需检查排序后相邻的最多6个点。

**Q4: 如何处理浮点精度问题？**
A: 使用 epsilon（如 1e-9）比较，避免直接 ==。叉积结果接近0时视为共线。距离比较用平方避免开方。

**Q5: 判断点是否在多边形内？**
A: 射线法：从点向右发射射线，统计与多边形边的交点数，奇数在内部。注意处理点在边上的特殊情况。

## 相关概念

### 数据结构
- [点/向量](../data-structures/point.md) - 基本几何对象
- [树](../data-structures/tree.md) - 空间索引结构
- [图](../data-structures/graph.md) - 网格表示

### 算法
- [分治法](./divide-conquer.md) - 最近点对核心
- [排序](./sorting.md) - 凸包预处理
- [扫描线算法](./sweep-line.md) - 线段交优化

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 通常为 O(n log n)
- [空间复杂度](../../references/space-complexity.md) - O(n)

### 系统实现
- [图形引擎](../../references/graphics-engines.md) - 实时渲染
- [GIS系统](../../references/gis.md) - 地理信息处理
