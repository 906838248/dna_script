import sys
import os
import time
import gc
import cv2
import numpy as np
import pyautogui
import pydirectinput
import keyboard
import random
from typing import Optional, Tuple, Dict, Any, Callable

# Windows平台DPI感知设置，防止在高DPI屏幕上出现坐标偏移
if sys.platform == 'win32':
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

from PySide6.QtCore import QThread, Signal
from src.input_recorder import InputRecorder, RecordingManager
from src.log_manager import log_manager
from src.constants import GameConstants, LogLevels, MouseModes

# 设置pyautogui全局参数
pyautogui.PAUSE = 0.1  # 每次操作后的默认暂停时间
pyautogui.FAILSAFE = True  # 启用故障安全机制，鼠标移到左上角可终止程序

class BaseAutomationThread(QThread):
    """
    自动化脚本基类
    提供通用的自动化功能，包括图像识别、鼠标移动、录制回放等
    所有具体的自动化脚本都应继承此类
    """
    # 信号定义
    log_signal = Signal(str)  # 日志信号，用于发送日志消息
    finished_signal = Signal()  # 完成信号，表示脚本执行完毕
    progress_signal = Signal(int, int)  # 进度信号，参数为(当前循环, 总循环)
    recording_state_signal = Signal(bool, int)  # 录制状态信号，参数为(是否录制中, 操作数)

    def __init__(self, loop_count: int, img_folder: str, template_resolution: Tuple[int, int] = None):
        """
        初始化自动化线程
        
        Args:
            loop_count: 循环次数
            img_folder: 图片文件夹路径，用于存储识别的图片
            template_resolution: 模板图片的分辨率，如果为None则使用基准分辨率(1920x1080)
        """
        super().__init__()
        self.loop_count = loop_count
        self.img_folder = img_folder
        self.running = True  # 运行标志，用于停止线程
        self.current_loop = 0  # 当前循环次数
        self.recorder = InputRecorder()  # 输入录制器
        # 获取项目根目录（src的父目录）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.recording_manager = RecordingManager(os.path.join(project_root, "recordings"))  # 录制管理器
        
        # 模板图片缓存，避免重复加载
        self.template_cache: Dict[str, Any] = {}
        self.template_cache_max_size = 50  # 最大缓存图片数量
        
        # 屏幕截图缓存，减少频繁截图
        self.screenshot_cache: Optional[Any] = None
        self.screenshot_cache_time: float = 0
        self.screenshot_cache_ttl = GameConstants.SCREENSHOT_CACHE_TTL  # 缓存有效期（秒）
        
        # 模板缓存访问记录，用于LRU淘汰
        self.template_cache_access: Dict[str, float] = {}
        
        # 多分辨率支持
        # 游戏分辨率（玩家设置的游戏窗口分辨率，默认1920x1080）
        self.game_resolution = template_resolution if template_resolution else GameConstants.BASE_RESOLUTION
        self.scale_factor = self._calculate_scale_factor()
        
        # ORB特征检测器（用于多分辨率匹配）
        self.orb_detector = cv2.ORB_create(nfeatures=500)
        self.bf_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # 特征点缓存
        self.feature_cache: Dict[str, Tuple[Any, Any]] = {}  # {image_name: (keypoints, descriptors)}
        
        # 设置为非守护线程，但确保能正确停止
        self.setTerminationEnabled(True)

    def stop(self):
        """停止自动化线程"""
        self.running = False
        # 清理缓存
        self.template_cache.clear()
        self.template_cache_access.clear()
        self.feature_cache.clear()
        self.screenshot_cache = None
        # 强制垃圾回收，释放内存
        gc.collect()
    
    def _get_screen_resolution(self) -> Tuple[int, int]:
        """
        获取当前屏幕分辨率
        
        Returns:
            屏幕分辨率 (width, height)
        """
        try:
            screen_width, screen_height = pyautogui.size()
            return (screen_width, screen_height)
        except Exception as e:
            self._log(f"获取屏幕分辨率失败: {e}，使用默认分辨率", "WARNING")
            return GameConstants.BASE_RESOLUTION
    
    def _calculate_scale_factor(self) -> float:
        """
        计算缩放因子
        
        缩放因子 = 游戏分辨率 / 模板分辨率
        
        Returns:
            缩放因子
        """
        game_width, game_height = self.game_resolution
        template_width, template_height = GameConstants.BASE_RESOLUTION
        
        # 计算游戏分辨率相对于模板分辨率的缩放因子
        scale_x = game_width / template_width
        scale_y = game_height / template_height
        
        # 使用平均缩放因子
        scale_factor = (scale_x + scale_y) / 2
        
        self._log(f"模板分辨率: {template_width}x{template_height}, 游戏分辨率: {game_width}x{game_height}, 缩放因子: {scale_factor:.2f}", "INFO")
        return scale_factor
    
    def _scale_template(self, template: np.ndarray) -> np.ndarray:
        """
        根据游戏分辨率缩放模板图片
        
        Args:
            template: 原始模板图片
            
        Returns:
            缩放后的模板图片
        """
        # 如果缩放因子接近1，不需要缩放
        if abs(self.scale_factor - 1.0) < 0.01:
            return template
        
        # 计算新尺寸
        h, w = template.shape[:2]
        new_w = int(w * self.scale_factor)
        new_h = int(h * self.scale_factor)
        
        # 缩放图片
        scaled = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA if self.scale_factor < 1.0 else cv2.INTER_LINEAR)
        
        return scaled
    
    def _match_by_features(self, screenshot: np.ndarray, template: np.ndarray, confidence: float) -> Optional[Tuple[int, int]]:
        """
        使用特征点匹配查找图片（分辨率无关）
        
        Args:
            screenshot: 屏幕截图
            template: 模板图片
            confidence: 置信度阈值
            
        Returns:
            找到则返回(center_x, center_y)，否则返回None
        """
        try:
            # 提取特征点和描述符
            kp1, des1 = self.orb_detector.detectAndCompute(template, None)
            kp2, des2 = self.orb_detector.detectAndCompute(screenshot, None)
            
            if des1 is None or des2 is None:
                return None
            
            if len(des1) < GameConstants.MIN_MATCH_COUNT or len(des2) < GameConstants.MIN_MATCH_COUNT:
                return None
            
            # 特征点匹配
            matches = self.bf_matcher.match(des1, des2)
            
            if len(matches) < GameConstants.MIN_MATCH_COUNT:
                return None
            
            # 按距离排序，取最佳匹配
            matches = sorted(matches, key=lambda x: x.distance)
            good_matches = matches[:min(len(matches), 20)]  # 取前20个最佳匹配
            
            if len(good_matches) < GameConstants.MIN_MATCH_COUNT:
                return None
            
            # 计算匹配质量
            avg_distance = sum(m.distance for m in good_matches) / len(good_matches)
            match_quality = 1.0 - (avg_distance / 100.0)  # 归一化距离
            
            if match_quality < GameConstants.FEATURE_MATCH_THRESHOLD:
                return None
            
            # 计算模板中心在屏幕中的位置
            template_center_x = template.shape[1] // 2
            template_center_y = template.shape[0] // 2
            
            # 使用匹配点计算中心位置
            screen_points = []
            for match in good_matches:
                # 模板中的点
                template_pt = kp1[match.queryIdx].pt
                # 屏幕中的对应点
                screen_pt = kp2[match.trainIdx].pt
                
                # 计算偏移
                offset_x = screen_pt[0] - template_pt[0] * self.scale_factor
                offset_y = screen_pt[1] - template_pt[1] * self.scale_factor
                
                screen_points.append((offset_x + template_center_x * self.scale_factor,
                                     offset_y + template_center_y * self.scale_factor))
            
            if not screen_points:
                return None
            
            # 使用中位数作为最终位置（更鲁棒）
            center_x = int(np.median([p[0] for p in screen_points]))
            center_y = int(np.median([p[1] for p in screen_points]))
            
            # 验证位置是否在屏幕范围内
            screen_h, screen_w = screenshot.shape[:2]
            if 0 <= center_x < screen_w and 0 <= center_y < screen_h:
                self._log(f"特征点匹配成功，质量: {match_quality:.2f}", "DEBUG")
                return (center_x, center_y)
            
            return None
            
        except Exception as e:
            self._log(f"特征点匹配失败: {e}", "DEBUG")
            return None

    def _log(self, message: str, level: str = "INFO"):
        """
        记录日志（同时发送信号和写入文件）
        
        Args:
            message: 日志消息
            level: 日志级别（DEBUG, INFO, WARNING, ERROR）
        """
        # 发送信号到UI
        self.log_signal.emit(message)
        
        # 写入文件日志
        if level == "DEBUG":
            log_manager.debug(message)
        elif level == "INFO":
            log_manager.info(message)
        elif level == "WARNING":
            log_manager.warning(message)
        elif level == "ERROR":
            log_manager.error(message)
        else:
            log_manager.info(message)

    def random_delay(self, min_delay: float = GameConstants.MIN_DELAY, max_delay: float = GameConstants.MAX_DELAY) -> float:
        """
        随机延迟，模拟人类操作间隔
        
        Args:
            min_delay: 最小延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            
        Returns:
            实际延迟时间
        """
        delay = random.uniform(min_delay, max_delay)
        self.interruptible_sleep(delay)
        return delay

    def interruptible_sleep(self, duration: float) -> None:
        """
        可中断的睡眠函数，在sleep期间可以响应停止信号
        
        Args:
            duration: 睡眠时长（秒）
        """
        check_interval = GameConstants.CHECK_INTERVAL  # 检查间隔
        elapsed: float = 0
        while elapsed < duration and self.running:
            sleep_time = min(check_interval, duration - elapsed)
            time.sleep(sleep_time)
            elapsed += sleep_time

    def _evict_lru_template(self) -> None:
        """
        淘汰最久未使用的模板图片（LRU策略）
        
        当缓存达到最大限制时，删除最久未使用的模板以释放内存
        """
        if not self.template_cache_access:
            return
        
        # 找到最久未使用的模板
        lru_image = min(self.template_cache_access.items(), key=lambda x: x[1])[0]
        
        # 从缓存中删除
        if lru_image in self.template_cache:
            del self.template_cache[lru_image]
            del self.template_cache_access[lru_image]
            # 同时清理特征点缓存
            if lru_image in self.feature_cache:
                del self.feature_cache[lru_image]
            self._log(f"缓存已满，淘汰最久未使用的模板: {lru_image}", "DEBUG")

    def human_like_move(self, target_x: int, target_y: int) -> None:
        """
        模拟人类鼠标移动，使用贝塞尔曲线生成平滑轨迹
        
        Args:
            target_x: 目标X坐标
            target_y: 目标Y坐标
        """
        current_x, current_y = pyautogui.position()
        
        dx = target_x - current_x
        dy = target_y - current_y
        
        # 如果移动距离很小，直接返回
        if abs(dx) < GameConstants.MIN_MOUSE_MOVE_DISTANCE and abs(dy) < GameConstants.MIN_MOUSE_MOVE_DISTANCE:
            return
        
        # 计算移动步数，根据距离动态调整
        steps = max(GameConstants.MOUSE_MOVE_STEPS_MIN, min(GameConstants.MOUSE_MOVE_STEPS_MAX, int((dx**2 + dy**2)**0.5 / GameConstants.MOUSE_MOVE_STEP_SIZE)))
        previous_accumulated_x: float = 0
        previous_accumulated_y: float = 0
        
        # 使用贝塞尔曲线生成平滑移动轨迹
        for i in range(steps):
            progress = (i + 1) / steps
            
            t = progress
            # 二次贝塞尔曲线公式，添加随机扰动
            curve_x = (1-t)**2 * 0 + 2*(1-t)*t * random.uniform(-0.1, 0.1) + t**2 * 1
            curve_y = (1-t)**2 * 0 + 2*(1-t)*t * random.uniform(-0.1, 0.1) + t**2 * 1
            
            current_accumulated_x = dx * curve_x
            current_accumulated_y = dy * curve_y
            
            step_dx = current_accumulated_x - previous_accumulated_x
            step_dy = current_accumulated_y - previous_accumulated_y
            
            pydirectinput.moveRel(int(step_dx), int(step_dy))
            
            previous_accumulated_x = current_accumulated_x
            previous_accumulated_y = current_accumulated_y

    def human_like_move_rel(self, dx: int, dy: int) -> None:
        """
        相对坐标的人类化鼠标移动
        
        Args:
            dx: X轴相对移动距离
            dy: Y轴相对移动距离
        """
        if abs(dx) < GameConstants.MIN_MOUSE_MOVE_DISTANCE and abs(dy) < GameConstants.MIN_MOUSE_MOVE_DISTANCE:
            return
        
        steps = max(GameConstants.MOUSE_MOVE_STEPS_MIN, min(GameConstants.MOUSE_MOVE_STEPS_MAX, int((dx**2 + dy**2)**0.5 / GameConstants.MOUSE_MOVE_STEP_SIZE)))
        previous_accumulated_x: float = 0
        previous_accumulated_y: float = 0
        
        for i in range(steps):
            progress = (i + 1) / steps
            
            t = progress
            curve_x = (1-t)**2 * 0 + 2*(1-t)*t * random.uniform(-0.1, 0.1) + t**2 * 1
            curve_y = (1-t)**2 * 0 + 2*(1-t)*t * random.uniform(-0.1, 0.1) + t**2 * 1
            
            current_accumulated_x = dx * curve_x
            current_accumulated_y = dy * curve_y
            
            step_dx = current_accumulated_x - previous_accumulated_x
            step_dy = current_accumulated_y - previous_accumulated_y
            
            pydirectinput.moveRel(int(step_dx), int(step_dy))
            
            previous_accumulated_x = current_accumulated_x
            previous_accumulated_y = current_accumulated_y

    def find_image(self, image_name: str, confidence: float = GameConstants.DEFAULT_CONFIDENCE, timeout: int = GameConstants.DEFAULT_TIMEOUT) -> Optional[Tuple[int, int]]:
        """
        在屏幕上查找指定图片（支持多分辨率）
        
        Args:
            image_name: 图片文件名
            confidence: 匹配置信度（0-1之间）
            timeout: 超时时间（秒）
            
        Returns:
            找到则返回(center_x, center_y)，否则返回None
        """
        # 加载模板图片
        if image_name not in self.template_cache:
            if len(self.template_cache) >= self.template_cache_max_size:
                self._evict_lru_template()
            
            image_path = os.path.join(self.img_folder, image_name)
            template = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if template is None:
                self.log_signal.emit(f"错误: 无法加载图片 {image_path}")
                return None
            
            self.template_cache[image_name] = template
            self.template_cache_access[image_name] = time.time()
        
        template = self.template_cache[image_name]
        self.template_cache_access[image_name] = time.time()
        
        # 根据游戏分辨率缩放模板图片
        scaled_template = self._scale_template(template)
        
        start_time = time.time()
        while self.running and time.time() - start_time < timeout:
            # 使用缓存的屏幕截图
            current_time = time.time()
            if self.screenshot_cache is None or current_time - self.screenshot_cache_time > self.screenshot_cache_ttl:
                if self.screenshot_cache is not None:
                    del self.screenshot_cache
                    self.screenshot_cache = None
                
                screenshot = pyautogui.screenshot()
                screenshot_np = np.array(screenshot)
                self.screenshot_cache = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                self.screenshot_cache_time = current_time
            
            screenshot_bgr = self.screenshot_cache
            
            # 方法1：模板匹配（快速）
            result = cv2.matchTemplate(screenshot_bgr, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                h, w = scaled_template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return (center_x, center_y)
            
            # 方法2：特征点匹配（如果启用且模板匹配失败）
            if GameConstants.ENABLE_FEATURE_MATCHING and max_val < confidence:
                feature_result = self._match_by_features(screenshot_bgr, template, confidence)
                if feature_result:
                    return feature_result
            
            self.interruptible_sleep(GameConstants.CHECK_INTERVAL)
        
        return None

    def click_image(self, image_name: str, confidence: float = GameConstants.DEFAULT_CONFIDENCE, timeout: int = GameConstants.DEFAULT_TIMEOUT) -> bool:
        """
        查找并点击指定图片
        
        Args:
            image_name: 图片文件名
            confidence: 匹配置信度
            timeout: 超时时间
            
        Returns:
            点击成功返回True，否则返回False
        """
        position = self.find_image(image_name, confidence, timeout)
        if position:
            self.human_like_move(position[0], position[1])
            pydirectinput.click()
            self.random_delay(GameConstants.CLICK_MIN_DELAY, GameConstants.CLICK_MAX_DELAY)
            self.log_signal.emit(f"点击 {image_name} 成功")
            return True
        else:
            self.log_signal.emit(f"未找到 {image_name}")
            return False

    def run(self) -> None:
        """
        子类必须实现的主运行方法
        """
        raise NotImplementedError("子类必须实现 run 方法")
    
    def random_space_press(self) -> None:
        """
        随机按下空格键0-6次，用于反检测
        """
        self.log_signal.emit("随机按下空格键")
        for _ in range(random.randint(GameConstants.MIN_SPACE_PRESS, GameConstants.MAX_SPACE_PRESS)):
                pydirectinput.press('space')
                self.log_signal.emit("按下空格键")
                self.random_delay(GameConstants.SPACE_PRESS_MIN_DELAY, GameConstants.SPACE_PRESS_MAX_DELAY)
    
    def game_again(self, again_timeout: int = GameConstants.AGAIN_TIMEOUT, begin_timeout: int = GameConstants.BEGIN_TIMEOUT, in_game_timeout: int = GameConstants.IN_GAME_TIMEOUT) -> bool:
        """
        游戏重开流程：点击again -> begin -> 等待进入游戏
        
        Args:
            again_timeout: 点击again的超时时间
            begin_timeout: 点击begin的超时时间
            in_game_timeout: 等待进入游戏的超时时间
            
        Returns:
            成功返回True，失败返回False
        """
        original_img_folder = self.img_folder
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.img_folder = os.path.join(script_dir, "img/common")
        
        try:
            if not self.click_image("again.png", timeout=again_timeout):
                self.log_signal.emit("点击 again 失败，停止循环")
                return False
            
            self.random_delay(1.5, 2.5)
            
            if not self.click_image("begin.png", timeout=begin_timeout):
                self.log_signal.emit("点击 begin 失败，停止循环")
                return False
            
            self.random_delay(1.5, 2.5)
            
            self.log_signal.emit("等待游戏加载...")
            if not self.find_image("in_game.png", timeout=in_game_timeout):
                self.log_signal.emit("等待 in_game 超时，停止循环")
                return False
            
            return True
        finally:
            self.img_folder = original_img_folder
    
    def game_retry(self, exit_timeout: int = GameConstants.EXIT_TIMEOUT, sure_timeout: int = GameConstants.SURE_TIMEOUT) -> bool:
        """
        游戏重试流程：按ESC -> 点击exit -> 点击sure
        
        Args:
            exit_timeout: 点击exit的超时时间
            sure_timeout: 点击sure的超时时间
            
        Returns:
            成功返回True，失败返回False
        """
        original_img_folder = self.img_folder
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.img_folder = os.path.join(script_dir, "img/common")
        
        try:
            keyboard.press_and_release('esc')
            
            self.random_delay(GameConstants.LOOP_MIN_DELAY, GameConstants.LOOP_MAX_DELAY)
            
            if not self.click_image("exit.png", timeout=exit_timeout):
                self.log_signal.emit("点击 exit 失败，停止循环")
                return False
            
            self.random_delay(GameConstants.LOOP_MIN_DELAY, GameConstants.LOOP_MAX_DELAY)
            
            if not self.click_image("sure.png", timeout=sure_timeout):
                self.log_signal.emit("点击 sure 失败，停止循环")
                return False
            
            return True
        finally:
            self.img_folder = original_img_folder
    
    def game_first(self, first_timeout: int = GameConstants.FIRST_TIMEOUT, begin_timeout: int = GameConstants.BEGIN_TIMEOUT, in_game_timeout: int = GameConstants.IN_GAME_TIMEOUT) -> bool:
        """
        游戏首次开始流程：点击first -> begin -> 等待进入游戏
        
        Args:
            first_timeout: 点击first的超时时间
            begin_timeout: 点击begin的超时时间
            in_game_timeout: 等待进入游戏的超时时间
            
        Returns:
            成功返回True，失败返回False
        """
        original_img_folder = self.img_folder
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.img_folder = os.path.join(script_dir, "img/common")
        
        try:
            
            if not self.click_image("first.png", timeout=first_timeout):
                self.log_signal.emit("点击 first 失败")
                if not self.click_image("sure_choose.png", timeout=first_timeout):
                    self.log_signal.emit("点击 sure_choose 失败，停止循环")
                    return False
            
            self.random_delay(GameConstants.LOOP_MIN_DELAY, GameConstants.LOOP_MAX_DELAY)
            
            if not self.click_image("begin.png", timeout=begin_timeout):
                self.log_signal.emit("点击 begin 失败，停止循环")
                return False
            
            self.log_signal.emit("等待游戏加载...")
            if not self.find_image("in_game.png", timeout=in_game_timeout):
                self.log_signal.emit("等待 in_game 超时，停止循环")
                return False
            
            return True
        finally:
            self.img_folder = original_img_folder
    
    def reset_position(self, set_timeout: int = GameConstants.SET_TIMEOUT, else_timeout: int = GameConstants.ELSE_TIMEOUT, reset_timeout: int = GameConstants.RESET_TIMEOUT, sure_timeout: int = GameConstants.SURE_TIMEOUT) -> bool:
        """
        游戏重置位置流程：按ESC -> 点击set -> 点击else -> 点击reset -> 点击sure
        
        Args:
            set_timeout: 点击set的超时时间
            else_timeout: 点击else的超时时间
            reset_timeout: 点击reset的超时时间
            sure_timeout: 点击sure的超时时间
            
        Returns:
            成功返回True，失败返回False
        """
        original_img_folder = self.img_folder
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.img_folder = os.path.join(script_dir, "img/common")
        try:
            pyautogui.press('esc')
            self.random_delay(GameConstants.LOOP_MIN_DELAY, GameConstants.LOOP_MAX_DELAY)
            if not self.click_image("set.png", timeout=set_timeout):
                self.log_signal.emit("点击 set 失败，停止循环")
                return False
            
            self.random_delay(GameConstants.LOOP_MIN_DELAY, GameConstants.LOOP_MAX_DELAY)
            if not self.click_image("else.png", timeout=else_timeout):
                self.log_signal.emit("点击 else 失败，停止循环")
                return False
            
            self.random_delay(GameConstants.LOOP_MIN_DELAY, GameConstants.LOOP_MAX_DELAY)
            if not self.click_image("reset.png", timeout=reset_timeout):
                self.log_signal.emit("点击 reset 失败，停止循环")
                return False
            
            self.random_delay(GameConstants.LOOP_MIN_DELAY, GameConstants.LOOP_MAX_DELAY)
            if not self.click_image("sure.png", timeout=sure_timeout):
                self.log_signal.emit("点击 sure 失败，停止循环")
                return False
            
            return True
        finally:
            self.img_folder = original_img_folder
    
    def run_game_loop(self, game_logic_callback: Callable[[], bool], first_timeout: int = GameConstants.FIRST_TIMEOUT, again_timeout: int = GameConstants.AGAIN_TIMEOUT, retry_timeout: int = GameConstants.RETRY_TIMEOUT) -> bool:
        """
        通用的游戏循环执行方法
        
        Args:
            game_logic_callback: 游戏逻辑回调函数，接收self作为参数，返回True表示成功，False表示失败
            first_timeout: 第一次进入游戏的超时时间
            again_timeout: 重新开始游戏的超时时间
            retry_timeout: 重试的超时时间
            
        Returns:
            成功完成所有循环返回True，中途失败返回False
        """
        for i in range(self.loop_count):
            if not self.running:
                break
            
            self.current_loop = i + 1
            self.progress_signal.emit(self.current_loop, self.loop_count)
            self.log_signal.emit(f"\n=== 开始第 {self.current_loop} 轮循环 ===")
            
            if self.current_loop == 1:
                self.log_signal.emit("第一次进入游戏")
                if not self.game_first(first_timeout=first_timeout):
                    self.log_signal.emit("第一次进入游戏失败，尝试重新开始")
                    if not self.game_again(again_timeout=retry_timeout):
                        self.log_signal.emit("重新开始游戏失败")
                        return False
            else:
                self.log_signal.emit("重新开始游戏")
                if not self.game_again(again_timeout=again_timeout):
                    self.log_signal.emit("重新开始游戏失败，尝试重试")
                    self.game_retry()
                    if not self.game_again(again_timeout=retry_timeout):
                        self.log_signal.emit("重试失败，停止循环")
                        return False
            
            try:
                if not game_logic_callback():
                    self.log_signal.emit("游戏逻辑执行失败，尝试重试")
                    if not self.game_retry():
                        self.log_signal.emit("重试失败，停止循环")
                        return False
                    
                    if not self.game_again(again_timeout=retry_timeout):
                        self.log_signal.emit("重新开始游戏失败，停止循环")
                        return False
                    
                    if not game_logic_callback():
                        self.log_signal.emit("游戏逻辑执行再次失败，停止循环")
                        return False
            except Exception as e:
                self.log_signal.emit(f"游戏逻辑执行异常: {str(e)}")
                if not self.game_retry():
                    self.log_signal.emit("重试失败，停止循环")
                    return False
                continue
            
            self.log_signal.emit(f"=== 第 {self.current_loop} 轮循环完成 ===")
            self.random_delay(1.5, 3.0)
        
        return True
    
    def run_game_loop_with_retry(self, game_logic_callback: Callable[[], bool], max_retries: int = GameConstants.DEFAULT_MAX_RETRIES, first_timeout: int = GameConstants.FIRST_TIMEOUT, again_timeout: int = GameConstants.AGAIN_TIMEOUT, retry_timeout: int = GameConstants.RETRY_TIMEOUT) -> bool:
        """
        通用的游戏循环执行方法（带重试机制）
        
        Args:
            game_logic_callback: 游戏逻辑回调函数，接收self作为参数，返回True表示成功，False表示失败
            max_retries: 最大重试次数
            first_timeout: 第一次进入游戏的超时时间
            again_timeout: 重新开始游戏的超时时间
            retry_timeout: 重试的超时时间
            
        Returns:
            成功完成所有循环返回True，中途失败返回False
        """
        for i in range(self.loop_count):
            if not self.running:
                break
            
            self.current_loop = i + 1
            self.progress_signal.emit(self.current_loop, self.loop_count)
            self.log_signal.emit(f"\n=== 开始第 {self.current_loop} 轮循环 ===")
            
            if self.current_loop == 1:
                self.log_signal.emit("第一次进入游戏")
                if not self.game_first(first_timeout=first_timeout):
                    self.log_signal.emit("第一次进入游戏失败，尝试重新开始")
                    if not self.game_again(again_timeout=retry_timeout):
                        self.log_signal.emit("重新开始游戏失败")
                        return False
            else:
                self.log_signal.emit("重新开始游戏")
                if not self.game_again(again_timeout=again_timeout):
                    self.log_signal.emit("重新开始游戏失败，尝试重试")
                    self.game_retry()
                    if not self.game_again(again_timeout=retry_timeout):
                        self.log_signal.emit("重试失败，停止循环")
                        return False
            
            retry_count = 0
            success = False
            
            while retry_count <= max_retries and not success:
                try:
                    if game_logic_callback():
                        success = True
                    else:
                        retry_count += 1
                        if retry_count <= max_retries:
                            self.log_signal.emit(f"游戏逻辑执行失败，第 {retry_count} 次重试")
                            if not self.game_retry():
                                self.log_signal.emit("重试失败，停止循环")
                                return False
                            
                            if not self.game_again(again_timeout=retry_timeout):
                                self.log_signal.emit("重新开始游戏失败，停止循环")
                                return False
                except Exception as e:
                    retry_count += 1
                    if retry_count <= max_retries:
                        self.log_signal.emit(f"游戏逻辑执行异常: {str(e)}，第 {retry_count} 次重试")
                        if not self.game_retry():
                            self.log_signal.emit("重试失败，停止循环")
                            return False
                        
                        if not self.game_again(again_timeout=retry_timeout):
                            self.log_signal.emit("重新开始游戏失败，停止循环")
                            return False
                    else:
                        self.log_signal.emit(f"游戏逻辑执行异常: {str(e)}，停止循环")
                        return False
            
            if not success:
                self.log_signal.emit(f"游戏逻辑执行失败，已重试 {max_retries} 次，停止循环")
                return False
            
            self.log_signal.emit(f"=== 第 {self.current_loop} 轮循环完成 ===")
            self.random_delay(1.5, 3.0)
        
        return True

        

    def start_recording(self):
        """
        开始录制键盘和鼠标操作
        
        Returns:
            开始成功返回True，否则返回False
        """
        if self.recorder.start_recording():
            self.log_signal.emit("开始录制键盘和鼠标操作 (按ESC停止)")
            self.recording_state_signal.emit(True, 0)
            return True
        return False

    def stop_recording(self):
        """
        停止录制
        
        Returns:
            停止成功返回True，否则返回False
        """
        if self.recorder.stop_recording():
            count = self.recorder.get_action_count()
            self.log_signal.emit(f"录制完成，共记录 {count} 个操作")
            self.recording_state_signal.emit(False, count)
            return True
        return False

    def save_recording(self, name: str) -> None:
        """
        保存录制到文件
        
        Args:
            name: 录制名称
        """
        filepath = self.recording_manager.get_recording_path(name)
        self.recorder.save_to_file(filepath)
        self.log_signal.emit(f"录制已保存到: {filepath}")

    def load_recording(self, name: str) -> bool:
        """
        从文件加载录制
        
        Args:
            name: 录制名称
            
        Returns:
            加载成功返回True，否则返回False
        """
        filepath = self.recording_manager.get_recording_path(name)
        if os.path.exists(filepath):
            self.recorder.load_from_file(filepath)
            count = self.recorder.get_action_count()
            self.log_signal.emit(f"已加载录制: {name} ({count} 个操作)")
            self.recording_state_signal.emit(False, count)
            return True
        else:
            self.log_signal.emit(f"录制文件不存在: {filepath}")
            return False

    def play_recording(self, speed_multiplier: float = GameConstants.DEFAULT_SPEED_MULTIPLIER) -> bool:
        """
        回放录制
        
        Args:
            speed_multiplier: 回放速度倍数
            
        Returns:
            开始回放成功返回True，否则返回False
        """
        if self.recorder.get_action_count() == 0:
            self.log_signal.emit("没有可回放的录制")
            return False
        
        stop_callback = lambda: not self.running
        
        if self.recorder.play_recording(speed_multiplier, stop_callback):
            self.log_signal.emit(f"开始回放录制 (速度: {speed_multiplier}x)")
            return True
        return False

    def stop_playback(self) -> None:
        """停止回放"""
        self.recorder.stop_playback()
        self.log_signal.emit("已停止回放")

    def list_recordings(self) -> list:
        """
        列出所有可用的录制
        
        Returns:
            录制名称列表
        """
        recordings = self.recording_manager.list_recordings()
        if recordings:
            self.log_signal.emit(f"可用录制: {', '.join(recordings)}")
        else:
            self.log_signal.emit("没有可用的录制")
        return recordings

    def delete_recording(self, name: str) -> bool:
        """
        删除指定录制
        
        Args:
            name: 录制名称
            
        Returns:
            删除成功返回True，否则返回False
        """
        if self.recording_manager.delete_recording(name):
            self.log_signal.emit(f"已删除录制: {name}")
            return True
        else:
            self.log_signal.emit(f"删除录制失败: {name}")
            return False
