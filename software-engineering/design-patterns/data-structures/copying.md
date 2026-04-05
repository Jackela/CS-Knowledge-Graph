# 深拷贝与浅拷贝 (Deep Copy vs Shallow Copy)

在编程中，复制对象时需要理解深拷贝和浅拷贝的区别，这关系到对象的独立性和内存管理。

## 基本概念

### 引用赋值
```
┌───────────────────────────────────────────────┐
│                   引用赋值                     │
├───────────────────────────────────────────────┤
│                                               │
│  a ──▶ [Object: {x: 1, y: 2}] ◀── b          │
│                                               │
│  a 和 b 指向同一个对象，修改会影响双方           │
│                                               │
└───────────────────────────────────────────────┘
```

### 浅拷贝
```
┌───────────────────────────────────────────────┐
│                   浅拷贝                       │
├───────────────────────────────────────────────┤
│                                               │
│  a ──▶ [Object] ◀── b                         │
│          │                                    │
│          ▼                                    │
│        [nested] ◀── 共享引用                    │
│                                               │
│  顶层对象复制，嵌套对象共享引用                   │
│                                               │
└───────────────────────────────────────────────┘
```

### 深拷贝
```
┌───────────────────────────────────────────────┐
│                   深拷贝                       │
├───────────────────────────────────────────────┤
│                                               │
│  a ──▶ [Object A]                             │
│          │                                    │
│          ▼                                    │
│        [nested A]                             │
│                                               │
│  b ──▶ [Object B]                             │
│          │                                    │
│          ▼                                    │
│        [nested B]                             │
│                                               │
│  所有层级完全独立复制                           │
│                                               │
└───────────────────────────────────────────────┘
```

## 实现方式

### JavaScript
```javascript
// 浅拷贝
const shallow1 = { ...obj };           // 展开运算符
const shallow2 = Object.assign({}, obj);

// 深拷贝
const deep1 = JSON.parse(JSON.stringify(obj));  // 简单但有限制
const deep2 = structuredClone(obj);             // 现代浏览器
const deep3 = _.cloneDeep(obj);                 // Lodash

// 自定义深拷贝
function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj);
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    if (obj instanceof Object) {
        const cloned = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                cloned[key] = deepClone(obj[key]);
            }
        }
        return cloned;
    }
}
```

### Python
```python
import copy

# 浅拷贝
shallow = copy.copy(obj)
list_shallow = original_list[:]

# 深拷贝
deep = copy.deepcopy(obj)

# 浅拷贝 vs 深拷贝示例
original = [[1, 2], [3, 4]]

shallow = copy.copy(original)
shallow[0][0] = 999
print(original)  # [[999, 2], [3, 4]] - 被修改！

deep = copy.deepcopy(original)
deep[0][0] = 888
print(original)  # [[999, 2], [3, 4]] - 不受影响
```

### Java
```java
// 浅拷贝：实现 Cloneable 接口
public class Person implements Cloneable {
    private String name;
    private Address address;  // 引用类型
    
    @Override
    public Person clone() throws CloneNotSupportedException {
        return (Person) super.clone();  // 浅拷贝
    }
    
    // 深拷贝
    public Person deepClone() throws CloneNotSupportedException {
        Person cloned = (Person) super.clone();
        cloned.address = new Address(this.address.getCity());
        return cloned;
    }
}

// 序列化深拷贝
public Person deepCloneBySerialization() {
    try {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(baos);
        oos.writeObject(this);
        
        ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
        ObjectInputStream ois = new ObjectInputStream(bais);
        return (Person) ois.readObject();
    } catch (Exception e) {
        throw new RuntimeException(e);
    }
}
```

## 对比总结

| 特性 | 浅拷贝 | 深拷贝 |
|------|--------|--------|
| 复制层级 | 仅顶层 | 所有层级 |
| 嵌套对象 | 共享引用 | 独立复制 |
| 内存占用 | 少 | 多 |
| 性能 | 快 | 慢 |
| 循环引用 | 无影响 | 需处理 |
| 函数/特殊对象 | 保留 | 可能丢失 |

## 应用场景

### 使用浅拷贝
- 对象只有基本类型属性
- 需要节省内存
- 嵌套对象不需要修改

### 使用深拷贝
- 需要完全独立的副本
- 嵌套对象需要修改
- 状态管理（Redux, Vuex）

## 相关概念

### 数据结构与算法
- [对象拷贝](../creational/prototype.md) - 原型模式中的拷贝
- [内存管理](../../../computer-science/systems/memory-management.md) - 内存分配与回收

### 设计模式
- [原型模式](../creational/prototype.md) - 通过复制创建对象
