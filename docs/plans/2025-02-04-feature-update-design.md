# Preview-PC 功能更新设计文档

## 1. 批次轮询模式

### 新增两种模式
**固定模式**：用户通过下拉框选择1-6张每批（保持现有UI）
**轮询模式**：按预设序列自动循环批次数量

### 配置存储
轮询序列保存到 `config.json`：
```json
{
  "batch_cycling_enabled": true,
  "batch_cycling_sequence": "1,2,3,4,5,6"
}
```

### 逻辑修改
- `BatchManager` 增加 `_batch_count_sequence` 属性
- `start_batch()` 时根据模式计算当前批次数量
- 固定模式：`batch_count = 用户选择值`
- 轮询模式：`batch_count = sequence[(batch_num-1) % len(sequence)]`

---

## 2. 超时处理优化

### 核心逻辑
- 超时触发后：显示timeout图片，不自动切换下一张
- 继续等待N/M按键：用户按N/M后才推进到下一张
- 最后一张超时时：显示超时图，等待按键，批次完成后弹确认框

### 状态管理
```python
# MainWindow 新增状态
self._waiting_for_key_after_timeout = False  # 超时后等待按键
```

---

## 3. 大图同步模式

### 行为定义
- 大图打开后，始终跟随主界面当前图片
- 主界面按N/M切换时，大图自动更新
- 大图打开/关闭不影响超时计时
- 大图按Esc关闭

### 实现方式
- 主界面 `_update_display()` 时同步更新大图（已有）
- 大图 `set_image()` 时检查当前是否为超时/等待状态
- 大图使用信号机制与主界面解耦（已有）

---

## 4. Wait按钮移除

### 删除内容
- `main_window.py` 中的 `_wait_btn` 按钮及相关布局
- `_set_image_mode(show_wait)` 方法
- `_showing_wait` 状态变量

### 保留内容
- `wait.png` 图片文件（用于预加载显示）
- `ImageLoader.get_wait_image()` 方法
- GridWidget 中未来图片显示wait.png的逻辑

---

## 5. UI改动

### 控制面板新增
- **模式切换**：固定模式 / 轮询模式（QComboBox或QButtonGroup）
- **轮询序列输入**：QLineEdit，格式 "1,2,3,4,5,6"

### 删除内容
- "Wait" 按钮

---

## 6. 测试用例

### 批次轮询测试
1. 启用轮询模式，设置序列 "1,2,3"
2. 开始 → 批次1（1张）→ 确认 → 批次2（2张）→ 确认 → 批次3（3张）
3. 批次4（1张）... 验证循环

### 超时处理测试
1. 设置超时5秒
2. 开始后等待超时 → 验证显示timeout图片
3. 等待超时后按N → 验证推进到下一张
4. 最后一张超时 → 按M → 验证批次完成弹窗

### 大图同步测试
1. 打开大图
2. 按N/M切换 → 验证大图同步更新
3. 超时发生时 → 验证大图显示timeout图片
4. 关闭大图 → 验证主界面不受影响
