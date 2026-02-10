# Preview-PC 功能更新实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现5个功能更新：批次轮询模式、超时处理优化、大图同步模式、Wait按钮移除、UI优化

**Architecture:** 修改MainWindow协调逻辑，BatchManager增加轮询支持，简化_wait状态管理，大图通过信号机制同步

**Tech Stack:** PyQt6, Python 3.10+

---

## 准备工作

### Step 0: 创建worktree隔离工作区（可选）

如果需要隔离开发环境：
```bash
git worktree add ../worktrees/2025-02-04-feature-update main
cd ../worktrees/2025-02-04-feature-update
```

---

## 任务1：配置管理扩展

**Files:**
- Modify: `src/config/config_manager.py`
- Test: `tests/test_config.py` (如存在)

### Step 1: 添加轮询配置项

**Step 1: 写失败的测试**

```python
def test_batch_cycling_config():
    config = ConfigManager()
    # 模拟测试配置读写
    assert config.get('batch_cycling_enabled') == False  # 默认值
    assert config.get('batch_cycling_sequence') == "1,2,3"  # 默认值
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_config.py::test_batch_cycling_config -v`
Expected: FAIL (配置项不存在)

**Step 3: 实现配置项**

修改 `src/config/config_manager.py`：
```python
# 在 ConfigManager.__init__ 或加载逻辑中添加
def _apply_defaults(self) -> None:
    # ... 现有代码 ...
    self._defaults['batch_cycling_enabled'] = False
    self._defaults['batch_cycling_sequence'] = "1,2,3"
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_config.py::test_batch_cycling_config -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/config/config_manager.py
git commit -m "feat: add batch cycling config options"
```

---

## 任务2：BatchManager轮询支持

**Files:**
- Modify: `src/core/batch_manager.py`
- Test: `tests/test_batch_manager.py`

### Step 1: 添加轮询序列解析

**Step 1: 写失败的测试**

```python
def test_batch_sequence_parsing():
    manager = BatchManager()
    manager.set_batch_sequence([1, 2, 3])
    manager.start_batch()  # batch_num=1
    assert manager.batch_count == 1  # 第1批应该是1张
    manager.confirm_batch()
    manager.start_batch()  # batch_num=2
    assert manager.batch_count == 2  # 第2批应该是2张
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_batch_manager.py::test_batch_sequence_parsing -v`
Expected: FAIL (方法不存在)

**Step 3: 实现轮询逻辑**

修改 `src/core/batch_manager.py`：
```python
class BatchManager(QObject):
    def __init__(self, parent=None):
        # ... 现有代码 ...
        self._use_cycling_sequence = False
        self._batch_sequence = [1, 2, 3]  # 默认序列

    def set_cycling_mode(self, enabled: bool, sequence: str = None) -> None:
        """设置轮询模式"""
        self._use_cycling_sequence = enabled
        if sequence:
            self._batch_sequence = self._parse_sequence(sequence)

    def _parse_sequence(self, sequence_str: str) -> list:
        """解析序列字符串 '1,2,3' -> [1, 2, 3]"""
        return [int(x.strip()) for x in sequence_str.split(',')]

    def _calculate_batch_count(self) -> int:
        """计算当前批次数量"""
        if not self._use_cycling_sequence:
            return self._batch_count
        index = (self._batch_num - 1) % len(self._batch_sequence)
        return self._batch_sequence[index]

    def start_batch(self) -> None:
        """开始新批次"""
        self._batch_num += 1
        self._current_image = 0
        self._batch_count = self._calculate_batch_count()
        self._set_state(BatchState.RUNNING)
        self.image_changed.emit(1, self._batch_count)
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_batch_manager.py::test_batch_sequence_parsing -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/core/batch_manager.py
git commit -m "feat: add batch cycling sequence support"
```

---

## 任务3：超时处理优化

**Files:**
- Modify: `src/ui/main_window.py`
- Modify: `src/core/timeout_manager.py`
- Test: `tests/test_timeout_flow.py`

### Step 1: 超时后等待按键

**Step 1: 写失败的测试**

```python
def test_timeout_waits_for_key():
    """超时后应该显示超时图，等待按键才推进"""
    # 需要模拟MainWindow环境
    pass  # UI测试较复杂，手动测试为主
```

**Step 2: 实现超时后等待逻辑**

修改 `src/ui/main_window.py`：

```python
class MainWindow(QMainWindow):
    def __init__(self):
        # ... 现有代码 ...
        self._waiting_for_key_after_timeout = False  # 新增状态

    def _on_timeout(self) -> None:
        """处理超时"""
        current = self._batch.current_image
        self._logger.log_timeout(current, self._timeout._current_duration, "timeout image")
        self._show_timeout_image()
        self._waiting_for_key_after_timeout = True
        # 不调用 process_timeout()，等待按键

    def _on_key_processed(self, detail: str) -> None:
        """处理按键后"""
        if self._waiting_for_key_after_timeout:
            self._waiting_for_key_after_timeout = False
            # 超时后第一次按键，推进到下一张
            self._batch.process_timeout()  # 计数为NG并推进
        self._timeout.stop()
        self._logger.log_key("", detail)
```

**Step 3: 验证现有测试通过**

Run: `pytest tests/ -v`
Expected: PASS (无回归)

**Step 4: 提交**

```bash
git add src/ui/main_window.py
git commit -m "feat: timeout waits for key press before advancing"
```

---

## 任务4：大图同步模式

**Files:**
- Modify: `src/ui/main_window.py`
- Modify: `src/ui/big_image_dialog.py`
- Test: 手动测试

### Step 1: 大图始终跟随当前图片

修改 `src/ui/main_window.py` 的 `_update_big_dialog`：

```python
def _update_big_dialog(self) -> None:
    """更新大图显示（始终跟随当前图片）"""
    if self._big_dialog and self._big_dialog.isVisible():
        current = self._batch.current_image - 1
        if self._showing_timeout and self._current_timeout_image:
            pixmap = self._current_timeout_image
        elif self._showing_wait:
            pixmap = self._image_loader.get_wait_image()
        else:
            pixmap = self._image_loader.get_normal_image(current)
        self._big_dialog.set_image(pixmap)
```

**修改点**：大图始终跟随，不需要额外逻辑（当前已实现）

### Step 2: 提交

```bash
git add src/ui/main_window.py src/ui/big_image_dialog.py
git commit -m "refactor: big image sync mode (already implemented)"
```

---

## 任务5：移除Wait按钮

**Files:**
- Modify: `src/ui/main_window.py`

### Step 1: 删除Wait按钮及逻辑

**Step 1: 写失败的测试**

```python
def test_wait_button_removed():
    """验证界面没有Wait按钮"""
    main = MainWindow()
    # 应该没有_wait_btn属性
    assert not hasattr(main, '_wait_btn')
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_ui.py::test_wait_button_removed -v`
Expected: FAIL (_wait_btn存在)

**Step 3: 删除Wait按钮**

修改 `src/ui/main_window.py`：

1. 删除 `_wait_btn` 创建代码（约第158-160行）
2. 删除 `_set_image_mode` 方法中的 wait 相关逻辑
3. 简化 `_update_display`：
```python
def _update_display(self) -> None:
    """更新图片显示"""
    current = self._batch.current_image - 1
    pixmaps = []

    for i in range(self._batch.batch_count):
        if i < current:
            # 已处理 - 显示正常图片
            pixmaps.append(self._image_loader.get_normal_image(i))
        elif i == current:
            # 当前图片
            if self._showing_timeout and self._current_timeout_image:
                pixmaps.append(self._current_timeout_image)
            else:
                pixmaps.append(self._image_loader.get_normal_image(i))
        else:
            # 未来图片 - 显示wait.png占位
            pixmaps.append(self._image_loader.get_wait_image())

    self._grid.update_images(pixmaps, current)
    self._update_big_dialog()
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_ui.py::test_wait_button_removed -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/ui/main_window.py
git commit -m "feat: remove Wait button and related logic"
```

---

## 任务6：UI轮询模式控件

**Files:**
- Modify: `src/ui/main_window.py`

### Step 1: 添加模式切换UI

在控制面板添加：
- 模式切换：固定模式 / 轮询模式（QComboBox）
- 序列输入：QLineEdit（轮询模式时启用）

```python
# 在 _create_control_panel 中添加
# Flow control row 修改
flow_row = QHBoxLayout()
self._mode_combo = QComboBox()
self._mode_combo.addItems(["固定模式", "轮询模式"])
self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
flow_row.addWidget(self._mode_combo)
# ... 现有start/pause/stop按钮 ...

# 新增轮询序列输入行
sequence_row = QHBoxLayout()
sequence_row.addWidget(QLabel("轮询序列:"))
self._sequence_edit = QLineEdit("1,2,3,4,5,6")
self._sequence_edit.setEnabled(False)
sequence_row.addWidget(self._sequence_edit)
layout.addLayout(sequence_row)

def _on_mode_changed(self, index) -> None:
    """模式切换"""
    if index == 1:  # 轮询模式
        self._sequence_edit.setEnabled(True)
    else:
        self._sequence_edit.setEnabled(False)
```

### Step 2: 提交

```bash
git add src/ui/main_window.py
git commit -m "feat: add cycling mode UI controls"
```

---

## 任务7：集成测试

### Step 1: 完整流程测试

```bash
# 启动应用
D:/miniforge3/envs/yolo/python.exe main.py

# 测试项：
# 1. 固定模式：选择4张批次，验证每批4张
# 2. 轮询模式：启用，设置序列 "1,2,3"，验证1→2→3循环
# 3. 超时：等待超时，验证显示timeout图片，按N/M推进
# 4. 大图：打开大图，按N/M验证同步更新
# 5. 批次完成：验证确认框和自动开始下一批
```

### Step 2: 提交最终状态

```bash
git add .
git commit -m "feat: complete feature update - cycling mode, timeout optimization, big image sync"
```

---

## 执行选项

**计划已完成并保存到 `docs/plans/2025-02-04-feature-update-implementation.md`**

**两种执行方式：**

**1. Subagent-Driven（本会话）** - 我每个任务创建子agent，任务间代码审查，快速迭代

**2. Parallel Session（新会话）** - 在worktree中批量执行，设置检查点

选择哪种方式？
