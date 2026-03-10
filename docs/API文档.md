# 自动化脚本开发接口文档

## 概述

本文档为开发者提供自动化脚本开发的详细接口说明。所有自动化脚本都需要继承 `BaseAutomationThread` 基类，该类提供了图像识别、鼠标操作、录制回放等核心功能。

## 基类说明

### BaseAutomationThread

**位置**: `src/base_automation.py`

**描述**: 自动化脚本基类，提供通用的自动化功能，包括图像识别、鼠标移动、录制回放等。所有具体的自动化脚本都应继承此类。

**继承关系**: `BaseAutomationThread` -> `QThread` (PySide6)

## 信号定义

基类定义了以下信号，用于与UI层通信：

| 信号名称 | 参数类型 | 说明 |
|---------|---------|------|
| `log_signal` | `str` | 日志信号，用于发送日志消息到UI |
| `finished_signal` | 无 | 完成信号，表示脚本执行完毕 |
| `progress_signal` | `int, int` | 进度信号，参数为(当前循环, 总循环) |
| `recording_state_signal` | `bool, int` | 录制状态信号，参数为(是否录制中, 操作数) |

## 初始化方法

### `__init__(self, loop_count, img_folder)`

**描述**: 初始化自动化线程

**参数**:
- `loop_count` (int): 循环次数
- `img_folder` (str): 图片文件夹路径，用于存储识别的图片

**示例**:
```python
class MyScript(BaseAutomationThread):
    def __init__(self, loop_count):
        super().__init__(loop_count, "img/my_script")
```

## 脚本元数据

每个脚本类应定义以下类属性，用于在UI中显示脚本信息：

| 属性名称 | 类型 | 必需 | 说明 |
|---------|------|------|------|
| `SCRIPT_NAME` | `str` | 是 | 脚本名称，显示在脚本选择列表中 |
| `SCRIPT_DESCRIPTION` | `str` | 是 | 脚本描述，说明脚本功能和使用要求 |
| `SCRIPT_IMG_FOLDER` | `str` | 是 | 图片文件夹路径，相对于项目根目录 |

**示例**:
```python
class Script40LevelExpel(BaseAutomationThread):
    """40级魔之楔驱离脚本"""
    
    SCRIPT_NAME = "40级魔之楔驱离"
    SCRIPT_DESCRIPTION = "刚需黎瑟"
    SCRIPT_IMG_FOLDER = "img/common"
    
    def __init__(self, loop_count):
        super().__init__(loop_count, self.SCRIPT_IMG_FOLDER)
    
    def run(self):
        # 脚本逻辑
        pass
```

**说明**:
- `SCRIPT_NAME`: 应简洁明了，便于用户识别
- `SCRIPT_DESCRIPTION`: 可包含脚本的使用前提、注意事项等
- `SCRIPT_IMG_FOLDER`: 如果多个脚本共用图片，可使用 `img/common`；否则建议每个脚本使用独立文件夹

## 核心方法

### 1. 控制方法

#### `stop(self)`

**描述**: 停止自动化线程

**参数**: 无

**返回值**: 无

**说明**: 设置运行标志为False，清理缓存，线程会在下一个检查点停止

---

### 2. 日志方法

#### `_log(self, message, level="INFO")`

**描述**: 记录日志（同时发送信号到UI和写入文件）

**参数**:
- `message` (str): 日志消息
- `level` (str): 日志级别，可选值：`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`

**返回值**: 无

**示例**:
```python
self._log("开始执行脚本", "INFO")
self._log("找不到目标图片", "WARNING")
self._log("发生错误", "ERROR")
```

---

### 3. 延迟方法

#### `random_delay(self, min_delay=0.5, max_delay=2.0)`

**描述**: 随机延迟，模拟人类操作间隔

**参数**:
- `min_delay` (float): 最小延迟时间（秒），默认0.5
- `max_delay` (float): 最大延迟时间（秒），默认2.0

**返回值**: `float` - 实际延迟时间

**示例**:
```python
delay = self.random_delay(1.0, 3.0)  # 延迟1-3秒
```

---

#### `interruptible_sleep(self, duration)`

**描述**: 可中断的睡眠函数，在sleep期间可以响应停止信号

**参数**:
- `duration` (float): 睡眠时长（秒）

**返回值**: 无

**说明**: 每0.1秒检查一次运行状态，如果线程被停止则立即返回

**示例**:
```python
self.interruptible_sleep(5)  # 睡眠5秒，可被中断
```

---

### 4. 鼠标移动方法

#### `human_like_move(self, target_x, target_y)`

**描述**: 模拟人类鼠标移动，使用贝塞尔曲线生成平滑轨迹

**参数**:
- `target_x` (int): 目标X坐标
- `target_y` (int): 目标Y坐标

**返回值**: 无

**说明**: 移动轨迹带有随机扰动，更加拟人化

**示例**:
```python
self.human_like_move(500, 300)  # 移动到坐标(500, 300)
```

---

#### `human_like_move_rel(self, dx, dy)`

**描述**: 相对坐标的人类化鼠标移动

**参数**:
- `dx` (int): X轴相对移动距离
- `dy` (int): Y轴相对移动距离

**返回值**: 无

**示例**:
```python
self.human_like_move_rel(100, -50)  # 相对当前位置移动
```

---

### 5. 图像识别方法

#### `find_image(self, image_name, confidence=0.8, timeout=30)`

**描述**: 在屏幕上查找指定图片

**参数**:
- `image_name` (str): 图片文件名（相对于img_folder）
- `confidence` (float): 匹配置信度（0-1之间），默认0.8
- `timeout` (int): 超时时间（秒），默认30

**返回值**: `tuple` 或 `None`
- 成功: `(center_x, center_y)` - 图片中心坐标
- 失败: `None`

**说明**: 
- 使用模板匹配算法查找图片
- 支持模板图片缓存，避免重复加载
- 支持屏幕截图缓存，减少频繁截图操作

**示例**:
```python
# 查找图片，置信度0.9，超时10秒
position = self.find_image("button.png", confidence=0.9, timeout=10)
if position:
    print(f"找到图片，位置: {position}")
else:
    print("未找到图片")
```

---

#### `click_image(self, image_name, confidence=0.8, timeout=30)`

**描述**: 查找并点击指定图片

**参数**:
- `image_name` (str): 图片文件名
- `confidence` (float): 匹配置信度，默认0.8
- `timeout` (int): 超时时间（秒），默认30

**返回值**: `bool`
- `True`: 点击成功
- `False`: 未找到图片

**说明**: 自动执行人类化移动和点击操作

**示例**:
```python
if self.click_image("start_button.png", confidence=0.85, timeout=5):
    print("点击成功")
else:
    print("未找到按钮")
```

---

### 6. 游戏流程方法

#### `game_again(self, again_timeout=240, begin_timeout=5, in_game_timeout=30)`

**描述**: 游戏重开流程：点击again -> begin -> 等待进入游戏

**参数**:
- `again_timeout` (int): 点击again的超时时间（秒），默认240
- `begin_timeout` (int): 点击begin的超时时间（秒），默认5
- `in_game_timeout` (int): 等待进入游戏的超时时间（秒），默认30

**返回值**: `bool`
- `True`: 成功
- `False`: 失败

**所需图片**: `again.png`, `begin.png`, `in_game.png` (位于 `img/common/` 目录)

**示例**:
```python
if self.game_again():
    print("成功重新开始游戏")
```

---

#### `game_retry(self, exit_timeout=5, sure_timeout=5)`

**描述**: 游戏重试流程：按ESC -> 点击exit -> 点击sure

**参数**:
- `exit_timeout` (int): 点击exit的超时时间（秒），默认5
- `sure_timeout` (int): 点击sure的超时时间（秒），默认5

**返回值**: `bool`
- `True`: 成功
- `False`: 失败

**所需图片**: `exit.png`, `sure.png` (位于 `img/common/` 目录)

**示例**:
```python
if self.game_retry():
    print("成功退出当前游戏")
```

---

#### `game_first(self, first_timeout=5, begin_timeout=5, in_game_timeout=30)`

**描述**: 游戏首次开始流程：点击first -> begin -> 等待进入游戏

**参数**:
- `first_timeout` (int): 点击first的超时时间（秒），默认5
- `begin_timeout` (int): 点击begin的超时时间（秒），默认5
- `in_game_timeout` (int): 等待进入游戏的超时时间（秒），默认30

**返回值**: `bool`
- `True`: 成功
- `False`: 失败

**所需图片**: `first.png`, `sure_choose.png`, `begin.png`, `in_game.png` (位于 `img/common/` 目录)

**示例**:
```python
if self.game_first():
    print("成功首次进入游戏")
```

---

#### `reset_position(self, set_timeout=5, else_timeout=5, reset_timeout=5, sure_timeout=5)`

**描述**: 游戏重置位置流程：按ESC -> 点击set -> 点击else -> 点击reset -> 点击sure

**参数**:
- `set_timeout` (int): 点击set的超时时间（秒），默认5
- `else_timeout` (int): 点击else的超时时间（秒），默认5
- `reset_timeout` (int): 点击reset的超时时间（秒），默认5
- `sure_timeout` (int): 点击sure的超时时间（秒），默认5

**返回值**: `bool`
- `True`: 成功
- `False`: 失败

**所需图片**: `set.png`, `else.png`, `reset.png`, `sure.png` (位于 `img/common/` 目录)

**示例**:
```python
if self.reset_position():
    print("成功重置位置")
```

---

### 7. 通用游戏循环方法

#### `run_game_loop(self, game_logic_callback, first_timeout=5, again_timeout=600, retry_timeout=5)`

**描述**: 通用的游戏循环执行方法

**参数**:
- `game_logic_callback` (callable): 游戏逻辑回调函数，接收self作为参数，返回True表示成功，False表示失败
- `first_timeout` (int): 第一次进入游戏的超时时间（秒），默认5
- `again_timeout` (int): 重新开始游戏的超时时间（秒），默认600
- `retry_timeout` (int): 重试的超时时间（秒），默认5

**返回值**: `bool`
- `True`: 成功完成所有循环
- `False`: 中途失败

**说明**: 
- 自动处理第一次进入和后续重开的逻辑
- 自动处理失败重试
- 自动发送进度信号

**示例**:
```python
def my_game_logic(self):
    """游戏逻辑回调函数"""
    # 执行游戏操作
    if not self.click_image("target.png"):
        return False
    self.random_delay(1, 2)
    return True

def run(self):
    """主运行方法"""
    self.run_game_loop(my_game_logic)
```

---

#### `run_game_loop_with_retry(self, game_logic_callback, max_retries=2, first_timeout=5, again_timeout=600, retry_timeout=5)`

**描述**: 通用的游戏循环执行方法（带重试机制）

**参数**:
- `game_logic_callback` (callable): 游戏逻辑回调函数
- `max_retries` (int): 最大重试次数，默认2
- `first_timeout` (int): 第一次进入游戏的超时时间（秒），默认5
- `again_timeout` (int): 重新开始游戏的超时时间（秒），默认600
- `retry_timeout` (int): 重试的超时时间（秒），默认5

**返回值**: `bool`
- `True`: 成功完成所有循环
- `False`: 中途失败

**说明**: 每次游戏逻辑失败后，会尝试最多 `max_retries` 次重试

---

### 8. 录制回放方法

#### `start_recording(self)`

**描述**: 开始录制键盘和鼠标操作

**参数**: 无

**返回值**: `bool`
- `True`: 开始成功
- `False`: 开始失败（可能已在录制中）

**说明**: 录制期间按ESC键可停止录制

**示例**:
```python
if self.start_recording():
    print("开始录制操作")
```

---

#### `stop_recording(self)`

**描述**: 停止录制

**参数**: 无

**返回值**: `bool`
- `True`: 停止成功
- `False`: 停止失败（可能未在录制中）

**示例**:
```python
if self.stop_recording():
    count = self.recorder.get_action_count()
    print(f"录制完成，共 {count} 个操作")
```

---

#### `save_recording(self, name)`

**描述**: 保存录制到文件

**参数**:
- `name` (str): 录制名称

**返回值**: 无

**说明**: 录制文件保存在 `recordings/` 目录下

**示例**:
```python
self.save_recording("my_recording")  # 保存为 my_recording.json
```

---

#### `load_recording(self, name)`

**描述**: 从文件加载录制

**参数**:
- `name` (str): 录制名称

**返回值**: `bool`
- `True`: 加载成功
- `False`: 加载失败（文件不存在）

**示例**:
```python
if self.load_recording("my_recording"):
    print("录制加载成功")
else:
    print("录制文件不存在")
```

---

#### `play_recording(self, speed_multiplier=1.0)`

**描述**: 回放录制的操作

**参数**:
- `speed_multiplier` (float): 回放速度倍数，默认1.0

**返回值**: `bool`
- `True`: 开始回放成功
- `False`: 开始回放失败（没有可回放的录制）

**说明**: 
- 速度倍数大于1.0会加快回放，小于1.0会减慢回放
- 回放期间可通过 `stop_playback()` 或停止线程来中断

**示例**:
```python
# 正常速度回放
self.play_recording()

# 2倍速回放
self.play_recording(speed_multiplier=2.0)

# 0.5倍速回放（慢放）
self.play_recording(speed_multiplier=0.5)
```

---

#### `stop_playback(self)`

**描述**: 停止回放

**参数**: 无

**返回值**: 无

**示例**:
```python
self.stop_playback()
```

---

#### `list_recordings(self)`

**描述**: 列出所有可用的录制

**参数**: 无

**返回值**: `list` - 录制名称列表

**示例**:
```python
recordings = self.list_recordings()
for name in recordings:
    print(f"可用录制: {name}")
```

---

#### `delete_recording(self, name)`

**描述**: 删除指定录制

**参数**:
- `name` (str): 录制名称

**返回值**: `bool`
- `True`: 删除成功
- `False`: 删除失败

**示例**:
```python
if self.delete_recording("old_recording"):
    print("录制已删除")
```

---

### 9. 其他方法

#### `random_space_press(self)`

**描述**: 随机按下空格键0-6次，用于反检测

**参数**: 无

**返回值**: 无

**示例**:
```python
self.random_space_press()  # 随机按空格键
```

---

#### `run(self)`

**描述**: 子类必须实现的主运行方法

**参数**: 无

**返回值**: 无

**说明**: 这是一个抽象方法，子类必须实现

**示例**:
```python
class MyScript(BaseAutomationThread):
    def run(self):
        """主运行方法"""
        self._log("脚本开始执行")
        
        for i in range(self.loop_count):
            if not self.running:
                break
            
            self.current_loop = i + 1
            self.progress_signal.emit(self.current_loop, self.loop_count)
            
            # 执行游戏逻辑
            if self.click_image("start.png"):
                self.random_delay(1, 2)
        
        self.finished_signal.emit()
```

## 完整开发示例

### 示例1：简单的点击脚本

```python
import os
from PySide6.QtCore import Signal
from src.base_automation import BaseAutomationThread

class SimpleClickScript(BaseAutomationThread):
    """简单点击脚本示例"""
    
    # 脚本元数据
    SCRIPT_NAME = "简单点击脚本"
    SCRIPT_DESCRIPTION = "演示基本的图片点击功能"
    SCRIPT_IMG_FOLDER = "img/simple_click"
    
    def __init__(self, loop_count):
        # 设置图片文件夹路径
        super().__init__(loop_count, self.SCRIPT_IMG_FOLDER)
    
    def run(self):
        """主运行方法"""
        self._log("开始执行简单点击脚本")
        
        for i in range(self.loop_count):
            if not self.running:
                break
            
            self.current_loop = i + 1
            self.progress_signal.emit(self.current_loop, self.loop_count)
            self._log(f"第 {self.current_loop} 轮循环")
            
            # 点击目标图片
            if self.click_image("target.png", confidence=0.85, timeout=10):
                self._log("点击成功")
                self.random_delay(1, 2)
            else:
                self._log("点击失败", "WARNING")
        
        self._log("脚本执行完成")
        self.finished_signal.emit()
```

### 示例2：使用通用游戏循环

```python
import os
from src.base_automation import BaseAutomationThread

class GameScript(BaseAutomationThread):
    """游戏脚本示例"""
    
    # 脚本元数据
    SCRIPT_NAME = "游戏循环脚本"
    SCRIPT_DESCRIPTION = "演示通用游戏循环的使用"
    SCRIPT_IMG_FOLDER = "img/game_script"
    
    def __init__(self, loop_count):
        super().__init__(loop_count, self.SCRIPT_IMG_FOLDER)
    
    def game_logic(self):
        """游戏逻辑回调函数"""
        self._log("执行游戏逻辑")
        
        # 点击目标
        if not self.click_image("target.png", timeout=10):
            return False
        
        self.random_delay(1, 2)
        
        # 等待结果
        if self.find_image("success.png", timeout=30):
            self._log("游戏成功")
            return True
        else:
            self._log("游戏失败", "WARNING")
            return False
    
    def run(self):
        """主运行方法"""
        self._log("开始执行游戏脚本")
        
        # 使用通用游戏循环
        success = self.run_game_loop(
            game_logic_callback=self.game_logic,
            first_timeout=10,
            again_timeout=300
        )
        
        if success:
            self._log("所有循环完成")
        else:
            self._log("脚本执行失败", "ERROR")
        
        self.finished_signal.emit()
```

### 示例3：带异常处理的脚本

```python
import os
from src.base_automation import BaseAutomationThread
from src.controllers.exceptions import AutomationError

class RobustScript(BaseAutomationThread):
    """健壮的脚本示例"""
    
    # 脚本元数据
    SCRIPT_NAME = "健壮脚本"
    SCRIPT_DESCRIPTION = "演示异常处理和错误恢复"
    SCRIPT_IMG_FOLDER = "img/robust_script"
    
    def __init__(self, loop_count):
        super().__init__(loop_count, self.SCRIPT_IMG_FOLDER)
    
    def run(self):
        """主运行方法"""
        self._log("开始执行健壮脚本")
        
        try:
            for i in range(self.loop_count):
                if not self.running:
                    break
                
                self.current_loop = i + 1
                self.progress_signal.emit(self.current_loop, self.loop_count)
                
                try:
                    self._execute_round()
                except AutomationError as e:
                    self._log(f"第 {self.current_loop} 轮执行失败: {e}", "ERROR")
                    # 尝试重置游戏状态
                    if not self.game_retry():
                        self._log("重置失败，停止脚本", "ERROR")
                        break
                except Exception as e:
                    self._log(f"未知错误: {e}", "ERROR")
                    break
        
        except Exception as e:
            self._log(f"脚本异常终止: {e}", "ERROR")
        finally:
            self._log("脚本执行结束")
            self.finished_signal.emit()
    
    def _execute_round(self):
        """执行单轮游戏逻辑"""
        self._log(f"执行第 {self.current_loop} 轮")
        
        # 查找并点击目标
        position = self.find_image("target.png", timeout=10)
        if not position:
            raise AutomationError("找不到目标图片")
        
        self.human_like_move(position[0], position[1])
        self.random_delay(0.5, 1.0)
        
        # 执行点击
        from pydirectinput import click
        click()
        
        self.random_delay(1, 2)
```

## 图片资源管理

### 图片文件夹结构

```
项目根目录/
├── img/
│   ├── common/           # 公共图片（游戏流程相关）
│   │   ├── again.png
│   │   ├── begin.png
│   │   ├── in_game.png
│   │   ├── exit.png
│   │   ├── sure.png
│   │   ├── first.png
│   │   ├── sure_choose.png
│   │   ├── set.png
│   │   ├── else.png
│   │   └── reset.png
│   └── my_script/        # 自定义脚本的图片
│       ├── target.png
│       └── button.png
└── scripts/
    └── my_script.py
```

### 图片制作建议

1. **分辨率**: 使用与游戏相同的分辨率截图
2. **格式**: PNG格式，支持透明度
3. **大小**: 尽量小而精确，避免包含过多背景
4. **命名**: 使用有意义的英文名称，如 `start_button.png`

## 性能优化建议

1. **使用缓存**: 基类已实现模板图片缓存和屏幕截图缓存
2. **合理设置超时**: 根据实际情况设置合理的超时时间
3. **避免频繁截图**: 使用 `find_image` 的默认缓存机制
4. **使用通用循环**: 使用 `run_game_loop` 方法减少代码重复

## 注意事项

1. **必须实现 `run` 方法**: 所有子类都必须实现 `run` 方法
2. **检查运行状态**: 在长时间操作中定期检查 `self.running` 状态
3. **发送进度信号**: 在循环中发送 `progress_signal` 以更新UI
4. **发送完成信号**: 脚本结束时发送 `finished_signal`
5. **异常处理**: 合理使用 try-except 处理异常情况
6. **日志记录**: 使用 `_log` 方法记录关键操作和错误信息

## 相关文件

- 基类实现: `src/base_automation.py`
- 异常定义: `src/controllers/exceptions.py`
- 日志管理: `src/log_manager.py`
- 录制功能: `src/input_recorder.py`

## 版本信息

- 文档版本: 1.0.0
- 最后更新: 2026-03-10
