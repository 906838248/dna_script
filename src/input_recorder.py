import json
import time
import threading
import multiprocessing
import keyboard
import pynput
from pynput import mouse
from typing import List, Dict, Callable, Optional
import os


def _playback_worker(actions: List[Dict], speed_multiplier: float, 
                     stop_event: multiprocessing.Event, 
                     status_queue: multiprocessing.Queue):
    """
    回放工作进程函数
    
    Args:
        actions: 要回放的操作列表
        speed_multiplier: 回放速度倍数
        stop_event: 停止事件
        status_queue: 状态队列，用于通信
    """
    import pydirectinput
    
    start_time = time.perf_counter()
    playback_pressed_keys = set()
    
    try:
        for action in actions:
            # 检查停止信号
            if stop_event.is_set():
                status_queue.put(('finished', None))
                break
            
            # 计算目标时间并等待
            target_time = start_time + (action['time'] / speed_multiplier)
            current_time = time.perf_counter()
            
            if target_time > current_time:
                sleep_time = target_time - current_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            # 执行操作
            if action['type'] == 'keyboard':
                key = action['key']
                if action['action'] == 'press':
                    pydirectinput.keyDown(key)
                    playback_pressed_keys.add(key)
                elif action['action'] == 'release':
                    pydirectinput.keyUp(key)
                    if key in playback_pressed_keys:
                        playback_pressed_keys.remove(key)
            
            elif action['type'] == 'mouse':
                if action['action'] == 'move':
                    # 鼠标移动
                    if 'dx' in action and 'dy' in action:
                        pydirectinput.moveRel(int(action['dx']), int(action['dy']))
                    else:
                        pydirectinput.moveTo(action['x'], action['y'])
                elif action['action'] == 'click':
                    # 鼠标点击
                    if 'dx' in action and 'dy' in action:
                        pydirectinput.moveRel(int(action['dx']), int(action['dy']))
                    else:
                        x, y = action['x'], action['y']
                        pydirectinput.moveTo(x, y)
                    
                    if action['pressed']:
                        if action['button'] == 'Button.left':
                            pydirectinput.mouseDown()
                        elif action['button'] == 'Button.right':
                            pydirectinput.mouseDown(button='right')
                    else:
                        if action['button'] == 'Button.left':
                            pydirectinput.mouseUp()
                        elif action['button'] == 'Button.right':
                            pydirectinput.mouseUp(button='right')
                elif action['action'] == 'scroll':
                    # 鼠标滚轮
                    pydirectinput.scroll(action['dy'], action['x'], action['y'])
            
            # 再次检查停止信号
            if stop_event.is_set():
                status_queue.put(('finished', None))
                break
        
        # 释放所有按键
        for key in playback_pressed_keys:
            try:
                pydirectinput.keyUp(key)
            except:
                pass
        
        # 释放鼠标按键
        try:
            pydirectinput.mouseUp()
        except:
            pass
        
        try:
            pydirectinput.mouseUp(button='right')
        except:
            pass
        
        # 释放修饰键
        try:
            pydirectinput.keyUp('shift')
        except:
            pass
        
        try:
            pydirectinput.keyUp('ctrl')
        except:
            pass
        
        try:
            pydirectinput.keyUp('alt')
        except:
            pass
        
        status_queue.put(('finished', None))
        
    except Exception as e:
        status_queue.put(('error', str(e)))


class InputRecorder:
    """
    输入录制器类
    用于录制和回放键盘、鼠标操作
    支持绝对坐标和相对坐标两种录制模式
    使用多进程进行回放，确保时间精确性
    """
    def __init__(self, mouse_mode='absolute', min_mouse_move=20):
        """
        初始化输入录制器
        
        Args:
            mouse_mode: 鼠标录制模式，'absolute'为绝对坐标，'relative'为相对坐标
            min_mouse_move: 最小鼠标移动距离（像素），小于此值的移动将被忽略
        """
        self.is_recording = False  # 是否正在录制
        self.is_playing = False  # 是否正在回放
        self.recorded_actions: List[Dict] = []  # 记录的操作列表
        self.start_time: float = 0  # 录制开始时间
        self.play_process: Optional[multiprocessing.Process] = None  # 回放进程
        self.stop_event: Optional[multiprocessing.Event] = None  # 停止事件
        self.status_queue: Optional[multiprocessing.Queue] = None  # 状态队列
        self.mouse_mode = mouse_mode  # 鼠标录制模式
        self.min_mouse_move = min_mouse_move  # 最小鼠标移动距离
        
        self.mouse_listener: Optional[mouse.Listener] = None  # 鼠标监听器
        self.keyboard_hook = None  # 键盘钩子
        self.last_mouse_pos = None  # 上一次鼠标位置
        self.pressed_keys = set()  # 当前按下的键集合
        self.recording_lock = threading.Lock()  # 录制锁，保证线程安全
    
    def __enter__(self):
        """
        上下文管理器入口
        
        Returns:
            InputRecorder实例
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口，确保资源正确释放
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
            
        Returns:
            False表示不抑制异常
        """
        # 停止录制
        if self.is_recording:
            self.stop_recording()
        
        # 停止回放
        if self.is_playing:
            self.stop_playback()
        
        return False
        
    def start_recording(self, mouse_mode: str = 'relative', min_mouse_move: int = 3):
        """
        开始录制键盘和鼠标操作
        
        Args:
            mouse_mode: 鼠标录制模式
            min_mouse_move: 最小鼠标移动距离
            
        Returns:
            开始成功返回True，否则返回False
        """
        if self.is_recording:
            return False
        
        self.is_recording = True
        self.recorded_actions = []
        self.pressed_keys.clear()
        self.mouse_mode = mouse_mode
        self.min_mouse_move = min_mouse_move
        self.start_time = time.perf_counter()
        self.last_mouse_pos = None
        
        self._setup_keyboard_recording()
        self._setup_mouse_recording()
        
        return True
    
    def _setup_keyboard_recording(self):
        """设置键盘录制监听"""
        def on_keyboard_event(event):
            if not self.is_recording:
                return
            
            # ESC键停止录制
            if event.name == 'esc':
                self.stop_recording()
                return
            
            key = event.name.lower()
            is_press = event.event_type == 'down'
            
            with self.recording_lock:
                if is_press:
                    # 记录按键按下事件
                    if key not in self.pressed_keys:
                        self.pressed_keys.add(key)
                        action = {
                            'type': 'keyboard',
                            'action': 'press',
                            'key': key,
                            'time': time.perf_counter() - self.start_time
                        }
                        self.recorded_actions.append(action)
                else:
                    # 记录按键释放事件
                    if key in self.pressed_keys:
                        self.pressed_keys.remove(key)
                        action = {
                            'type': 'keyboard',
                            'action': 'release',
                            'key': key,
                            'time': time.perf_counter() - self.start_time
                        }
                        self.recorded_actions.append(action)
        
        self.keyboard_hook = keyboard.hook(on_keyboard_event)
    
    def _setup_mouse_recording(self):
        """设置鼠标录制监听"""
        def on_move(x, y):
            if not self.is_recording:
                return
            
            with self.recording_lock:
                if self.mouse_mode == 'relative':
                    # 相对坐标模式：记录移动增量
                    if self.last_mouse_pos is not None:
                        dx = x - self.last_mouse_pos[0]
                        dy = y - self.last_mouse_pos[1]
                        
                        # 只记录超过最小距离的移动
                        if abs(dx) >= self.min_mouse_move or abs(dy) >= self.min_mouse_move:
                            action = {
                                'type': 'mouse',
                                'action': 'move',
                                'dx': dx,
                                'dy': dy,
                                'time': time.perf_counter() - self.start_time
                            }
                            self.recorded_actions.append(action)
                            self.last_mouse_pos = (x, y)
                    else:
                        self.last_mouse_pos = (x, y)
                else:
                    # 绝对坐标模式：记录绝对位置
                    if self.last_mouse_pos is not None:
                        dx = abs(x - self.last_mouse_pos[0])
                        dy = abs(y - self.last_mouse_pos[1])
                        
                        if dx >= self.min_mouse_move or dy >= self.min_mouse_move:
                            action = {
                                'type': 'mouse',
                                'action': 'move',
                                'x': x,
                                'y': y,
                                'time': time.perf_counter() - self.start_time
                            }
                            self.recorded_actions.append(action)
                            self.last_mouse_pos = (x, y)
                    else:
                        self.last_mouse_pos = (x, y)
                        # 记录初始位置
                        action = {
                            'type': 'mouse',
                            'action': 'move',
                            'x': x,
                            'y': y,
                            'time': time.perf_counter() - self.start_time
                        }
                        self.recorded_actions.append(action)
        
        def on_click(x, y, button, pressed):
            if not self.is_recording:
                return
            
            with self.recording_lock:
                if self.mouse_mode == 'relative':
                    # 相对坐标模式：记录点击时的相对位置
                    if self.last_mouse_pos is None:
                        self.last_mouse_pos = (x, y)
                    
                    dx = x - self.last_mouse_pos[0]
                    dy = y - self.last_mouse_pos[1]
                    
                    action = {
                        'type': 'mouse',
                        'action': 'click',
                        'dx': dx,
                        'dy': dy,
                        'button': str(button),
                        'pressed': pressed,
                        'time': time.perf_counter() - self.start_time
                    }
                    self.recorded_actions.append(action)
                else:
                    # 绝对坐标模式：记录点击时的绝对位置
                    action = {
                        'type': 'mouse',
                        'action': 'click',
                        'x': x,
                        'y': y,
                        'button': str(button),
                        'pressed': pressed,
                        'time': time.perf_counter() - self.start_time
                    }
                    self.recorded_actions.append(action)
        
        def on_scroll(x, y, dx, dy):
            if not self.is_recording:
                return
            
            with self.recording_lock:
                # 记录滚轮滚动事件
                action = {
                    'type': 'mouse',
                    'action': 'scroll',
                    'x': x,
                    'y': y,
                    'dx': dx,
                    'dy': dy,
                    'time': time.perf_counter() - self.start_time
                }
                self.recorded_actions.append(action)
        
        # 创建鼠标监听器
        self.mouse_listener = mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll
        )
        self.mouse_listener.start()
    
    def stop_recording(self):
        """
        停止录制
        
        Returns:
            停止成功返回True，否则返回False
        """
        if not self.is_recording:
            return False
        
        self.is_recording = False
        
        # 停止鼠标监听器
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        # 停止键盘钩子
        if self.keyboard_hook:
            keyboard.unhook(self.keyboard_hook)
            self.keyboard_hook = None
        
        # 释放所有按下的键
        import pydirectinput
        for key in self.pressed_keys:
            try:
                pydirectinput.keyUp(key)
            except:
                pass
        self.pressed_keys.clear()
        
        return True
    
    def save_to_file(self, filepath: str):
        """
        保存录制到文件
        
        Args:
            filepath: 文件保存路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.recorded_actions, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: str) -> List[Dict]:
        """
        从文件加载录制
        
        Args:
            filepath: 文件路径
            
        Returns:
            加载的操作列表
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            self.recorded_actions = json.load(f)
        return self.recorded_actions
    
    def play_recording(self, speed_multiplier: float = 1.0, 
                       stop_callback: Optional[Callable[[], bool]] = None):
        """
        回放录制（使用多进程）
        
        Args:
            speed_multiplier: 回放速度倍数，1.0为正常速度
            stop_callback: 停止回调函数，返回True时停止回放
            
        Returns:
            开始回放成功返回True，否则返回False
        """
        if self.is_playing:
            return False
        
        if not self.recorded_actions:
            return False
        
        self.is_playing = True
        
        # 创建多进程通信对象
        self.stop_event = multiprocessing.Event()
        self.status_queue = multiprocessing.Queue()
        
        # 创建回放进程
        self.play_process = multiprocessing.Process(
            target=_playback_worker,
            args=(self.recorded_actions, speed_multiplier, self.stop_event, self.status_queue)
        )
        self.play_process.start()
        
        # 启动监控线程检查停止回调
        if stop_callback:
            self._start_stop_monitor(stop_callback)
        
        return True
    
    def _start_stop_monitor(self, stop_callback: Callable[[], bool]):
        """
        启动停止监控线程
        
        Args:
            stop_callback: 停止回调函数
        """
        def monitor():
            while self.is_playing and self.play_process and self.play_process.is_alive():
                if stop_callback():
                    self.stop_event.set()
                    break
                time.sleep(0.1)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def wait_for_playback(self, timeout: float = 300.0):
        """
        等待回放完成
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            回放完成返回True，超时返回False
        """
        if not self.is_playing or not self.play_process:
            return True
        
        start_time = time.time()
        while self.is_playing and self.play_process and self.play_process.is_alive():
            # 检查状态队列
            try:
                status, _ = self.status_queue.get_nowait()
                if status == 'finished':
                    self.is_playing = False
                    return True
                elif status == 'error':
                    self.is_playing = False
                    return False
            except:
                pass
            
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.1)
        
        # 进程结束后，再次检查状态队列
        while self.is_playing:
            try:
                status, _ = self.status_queue.get(timeout=0.5)
                if status == 'finished':
                    self.is_playing = False
                    return True
                elif status == 'error':
                    self.is_playing = False
                    return False
            except:
                break
        
        return True
    
    def stop_playback(self):
        """停止回放"""
        if self.stop_event:
            self.stop_event.set()
        
        self.is_playing = False
        
        # 终止回放进程
        if self.play_process and self.play_process.is_alive():
            self.play_process.terminate()
            self.play_process.join(timeout=2)
        
        # 清理资源
        self.play_process = None
        self.stop_event = None
        self.status_queue = None
    
    def get_action_count(self) -> int:
        """
        获取录制的操作数量
        
        Returns:
            操作数量
        """
        return len(self.recorded_actions)
    
    def clear_recording(self):
        """清空录制"""
        self.recorded_actions = []
        self.start_time = 0


class RecordingManager:
    """
    录制管理器类
    用于管理录制的存储、加载、列表和删除
    """
    def __init__(self, recordings_dir: str = "recordings"):
        """
        初始化录制管理器
        
        Args:
            recordings_dir: 录制文件存储目录
        """
        self.recordings_dir = recordings_dir
        self.ensure_recordings_dir()
    
    def __enter__(self):
        """
        上下文管理器入口
        
        Returns:
            RecordingManager实例
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
            
        Returns:
            False表示不抑制异常
        """
        return False
    
    def ensure_recordings_dir(self):
        """确保录制目录存在"""
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
    
    def get_recording_path(self, name: str) -> str:
        """
        获取录制文件的完整路径
        
        Args:
            name: 录制名称
            
        Returns:
            录制文件的完整路径
        """
        return os.path.join(self.recordings_dir, f"{name}.json")
    
    def list_recordings(self) -> List[str]:
        """
        列出所有可用的录制
        
        Returns:
            录制名称列表
        """
        if not os.path.exists(self.recordings_dir):
            return []
        
        recordings = []
        for file in os.listdir(self.recordings_dir):
            if file.endswith('.json'):
                recordings.append(file[:-5])
        return recordings
    
    def delete_recording(self, name: str) -> bool:
        """
        删除指定录制
        
        Args:
            name: 录制名称
            
        Returns:
            删除成功返回True，否则返回False
        """
        filepath = self.get_recording_path(name)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
