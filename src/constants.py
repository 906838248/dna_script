"""
常量定义模块
定义项目中使用的常量，避免魔法数字
"""

from typing import Tuple, Optional


class GameConstants:
    """游戏相关常量"""
    
    # 默认配置
    DEFAULT_CONFIDENCE = 0.8
    DEFAULT_TIMEOUT = 30
    MIN_DELAY = 0.5
    MAX_DELAY = 2.0
    
    # 图像识别
    MIN_MOUSE_MOVE_DISTANCE = 5
    MOUSE_MOVE_STEPS_MIN = 3
    MOUSE_MOVE_STEPS_MAX = 5
    MOUSE_MOVE_STEP_SIZE = 100
    
    # 多分辨率支持
    BASE_RESOLUTION = (1920, 1080)  # 基准分辨率
    ENABLE_FEATURE_MATCHING = True  # 启用特征点匹配
    FEATURE_MATCH_THRESHOLD = 0.7  # 特征点匹配阈值
    MIN_MATCH_COUNT = 4  # 最小匹配点数量
    
    # 延迟时间
    CHECK_INTERVAL = 0.1
    SCREENSHOT_CACHE_TTL = 0.5  # 增加缓存有效期，减少频繁内存分配
    
    # 游戏流程超时
    AGAIN_TIMEOUT = 240
    BEGIN_TIMEOUT = 5
    IN_GAME_TIMEOUT = 30
    EXIT_TIMEOUT = 5
    SURE_TIMEOUT = 5
    FIRST_TIMEOUT = 5
    SET_TIMEOUT = 5
    ELSE_TIMEOUT = 5
    RESET_TIMEOUT = 5
    RETRY_TIMEOUT = 5
    
    # 回放
    DEFAULT_SPEED_MULTIPLIER = 1.0
    PLAYBACK_WAIT_TIMEOUT = 300.0
    
    # 空格键
    MIN_SPACE_PRESS = 0
    MAX_SPACE_PRESS = 6
    SPACE_PRESS_MIN_DELAY = 0.5
    SPACE_PRESS_MAX_DELAY = 1.2
    
    # 点击延迟
    CLICK_MIN_DELAY = 0.3
    CLICK_MAX_DELAY = 0.8
    
    # 游戏循环延迟
    LOOP_MIN_DELAY = 1.5
    LOOP_MAX_DELAY = 3.0
    
    # 默认重试次数
    DEFAULT_MAX_RETRIES = 2


class LogLevels:
    """日志级别常量"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MouseModes:
    """鼠标录制模式常量"""
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
