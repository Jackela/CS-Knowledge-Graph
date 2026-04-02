# 备忘录模式 (Memento Pattern)

备忘录模式（Memento Pattern）是一种**行为型设计模式**，允许在不破坏封装性的情况下捕获和恢复对象的内部状态。

## 核心概念

### 模式结构

```
备忘录模式角色：

┌─────────────────────────────────────────────────────────────┐
│                  备忘录模式结构                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────┐         ┌─────────────────┐          │
│   │   Originator    │────────▶│     Memento     │          │
│   │   (原发器)       │  创建/恢复 │    (备忘录)      │          │
│   │                 │         │                 │          │
│   │ - state         │         │ - state         │          │
│   │ + save()        │         │ + getState()    │          │
│   │ + restore()     │◀────────│ (仅原发器访问)   │          │
│   └────────┬────────┘  恢复状态 └─────────────────┘          │
│            │                                                │
│            │ 请求管理                                        │
│            ▼                                                │
│   ┌─────────────────┐                                       │
│   │    Caretaker    │                                       │
│   │    (负责人)      │                                       │
│   │                 │                                       │
│   │ - mementos[]    │  负责保存备忘录历史                     │
│   │ + add()         │  不访问备忘录内容                       │
│   │ + get()         │                                       │
│   └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 为什么需要备忘录模式

```
场景：文本编辑器的撤销功能

❌ 不使用备忘录模式：
- 编辑器需要暴露内部状态给外部管理
- 破坏封装性，违反了面向对象原则
- 外部管理器需要了解编辑器内部结构

✅ 使用备忘录模式：
- 编辑器自己创建状态快照
- 封装性得到保护，内部细节不暴露
- 管理器只负责存储，不解析内容
```

## 实现示例

### Python 实现

```python
from dataclasses import dataclass
from typing import List
from datetime import datetime

# 备忘录 - 存储状态
class EditorMemento:
    def __init__(self, content: str, cursor_position: int):
        self._content = content
        self._cursor_position = cursor_position
        self._date = datetime.now()
    
    @property
    def content(self) -> str:
        return self._content
    
    @property
    def cursor_position(self) -> int:
        return self._cursor_position
    
    @property
    def date(self) -> datetime:
        return self._date
    
    def __str__(self):
        return f"Memento [{self._date}]: '{self._content[:20]}...'"


# 原发器 - 创建和恢复状态
class TextEditor:
    def __init__(self):
        self._content = ""
        self._cursor_position = 0
    
    def type(self, text: str):
        """输入文本"""
        self._content = self._content[:self._cursor_position] + text
        self._cursor_position += len(text)
    
    def delete(self, count: int = 1):
        """删除字符"""
        self._content = (self._content[:self._cursor_position] + 
                        self._content[self._cursor_position + count:])
    
    def move_cursor(self, position: int):
        """移动光标"""
        self._cursor_position = max(0, min(position, len(self._content)))
    
    # 创建备忘录
    def save(self) -> EditorMemento:
        return EditorMemento(self._content, self._cursor_position)
    
    # 从备忘录恢复
    def restore(self, memento: EditorMemento):
        self._content = memento.content
        self._cursor_position = memento.cursor_position
    
    def __str__(self):
        return f"Content: '{self._content}', Cursor: {self._cursor_position}"


# 负责人 - 管理备忘录历史
class History:
    def __init__(self):
        self._mementos: List[EditorMemento] = []
        self._current = -1
    
    def backup(self, memento: EditorMemento):
        """备份状态"""
        # 删除当前位置之后的所有历史
        self._mementos = self._mementos[:self._current + 1]
        self._mementos.append(memento)
        self._current += 1
    
    def undo(self) -> EditorMemento:
        """撤销"""
        if self._current > 0:
            self._current -= 1
            return self._mementos[self._current]
        return None
    
    def redo(self) -> EditorMemento:
        """重做"""
        if self._current < len(self._mementos) - 1:
            self._current += 1
            return self._mementos[self._current]
        return None
    
    def show_history(self):
        """显示历史"""
        for i, memento in enumerate(self._mementos):
            marker = " <-- current" if i == self._current else ""
            print(f"  {i}: {memento}{marker}")


# 使用示例
editor = TextEditor()
history = History()

# 编辑并保存
editor.type("Hello, World!")
print(f"1. {editor}")
history.backup(editor.save())

editor.type(" How are you?")
print(f"2. {editor}")
history.backup(editor.save())

editor.delete(5)
print(f"3. {editor}")
history.backup(editor.save())

print("\n历史记录:")
history.show_history()

# 撤销
print("\n撤销...")
memento = history.undo()
if memento:
    editor.restore(memento)
    print(f"4. {editor}")

# 重做
print("\n重做...")
memento = history.redo()
if memento:
    editor.restore(memento)
    print(f"5. {editor}")
```

### Java 实现

```java
// 备忘录接口（窄接口）
public interface Memento {
    String getName();
    String getDate();
}

// 具体备忘录
public class EditorMemento implements Memento {
    private final String content;
    private final int cursorPosition;
    private final String date;
    
    public EditorMemento(String content, int cursorPosition) {
        this.content = content;
        this.cursorPosition = cursorPosition;
        this.date = new Date().toString();
    }
    
    // 仅包可见，原发器可以访问
    String getContent() { return content; }
    int getCursorPosition() { return cursorPosition; }
    
    @Override
    public String getName() { return date + " / " + content.substring(0, Math.min(10, content.length())) + "..."; }
    
    @Override
    public String getDate() { return date; }
}

// 原发器
public class TextEditor {
    private String content = "";
    private int cursorPosition = 0;
    
    public void type(String text) {
        content = content.substring(0, cursorPosition) + text;
        cursorPosition += text.length();
    }
    
    public EditorMemento save() {
        return new EditorMemento(content, cursorPosition);
    }
    
    public void restore(EditorMemento memento) {
        this.content = memento.getContent();
        this.cursorPosition = memento.getCursorPosition();
    }
}

// 负责人
public class History {
    private List<EditorMemento> mementos = new ArrayList<>();
    private int current = -1;
    
    public void backup(EditorMemento memento) {
        mementos = mementos.subList(0, current + 1);
        mementos.add(memento);
        current++;
    }
    
    public EditorMemento undo() {
        if (current > 0) {
            current--;
            return mementos.get(current);
        }
        return null;
    }
}
```

## 应用场景

### 1. 撤销/重做功能

```
应用场景：
- 文本编辑器
- 图形编辑器（Photoshop）
- IDE 代码编辑
- 数据库事务回滚
```

### 2. 游戏存档

```python
# 游戏状态存档示例
class GameMemento:
    def __init__(self, level: int, health: int, position: tuple, inventory: list):
        self._level = level
        self._health = health
        self._position = position
        self._inventory = inventory.copy()
    
    # 属性访问...

class GameCharacter:
    def save_game(self) -> GameMemento:
        return GameMemento(
            self.level, 
            self.health, 
            self.position, 
            self.inventory
        )
    
    def load_game(self, memento: GameMemento):
        self.level = memento.level
        self.health = memento.health
        self.position = memento.position
        self.inventory = memento.inventory.copy()
```

### 3. 浏览器历史

```
浏览器前进/后退：
- 每个页面状态作为备忘录
- 浏览器维护历史栈
- 前进/后退时恢复对应状态
```

## 优缺点

| 优点 | 缺点 |
|------|------|
| 不破坏封装性 | 消耗内存（每个备忘录都存储数据） |
| 简化原发器代码 | 可能影响性能（频繁创建备忘录） |
| 支持撤销/重做 | 负责人需要管理备忘录生命周期 |
| 容易实现 | 某些语言中实现访问控制较复杂 |

## 相关概念 (Related Concepts)

### 设计模式
- [命令模式](./command.md) - 常与备忘录结合实现撤销
- [迭代器模式](./iterator.md) - 遍历备忘录历史
- [原型模式](../creational/prototype.md) - 另一种对象复制方式

### 数据结构
- [栈](../../../computer-science/data-structures/stack.md) - 存储撤销历史
- [链表](../../../computer-science/data-structures/linked-list.md) - 实现无限撤销

### 应用场景
- [数组](../../../computer-science/data-structures/array.md) - 数据存储示例
- [事务管理](../../../computer-science/databases/transaction-acid.md) - 数据库事务回滚
- [版本控制](./version-control.md) - 代码版本管理

## 参考资料

1. "Design Patterns: Elements of Reusable Object-Oriented Software" - GoF
2. Refactoring Guru - Memento Pattern
3. Game Programming Patterns - State Management
