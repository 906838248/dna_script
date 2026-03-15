"""
配置管理模块
用于管理用户配置，包括脚本选择、循环次数等设置
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器类"""
    
    # 默认配置作为类属性，便于访问和验证
    DEFAULT_CONFIG = {
        "script": {
            "last_selected": None,
            "last_loop_count": 1,
            "auto_switch_to_log": False,
            "game_resolution": {
                "width": 1920,
                "height": 1080
            }
        },
        "recording": {
            "last_name": ""
        },
        "window": {
            "width": 900,
            "height": 700
        },
        "shortcuts": {
            "start_automation": "F5",
            "stop_automation": "F6",
            "clear_log": "F7",
            "toggle_recording": "F8",
            "stop_recording_playback": "esc"
        }
    }
    
    # 配置验证规则
    VALIDATION_RULES = {
        "script.last_loop_count": {
            "type": int,
            "min": 1,
            "max": 9999
        },
        "script.template_resolution.width": {
            "type": int,
            "min": 800,
            "max": 7680
        },
        "script.template_resolution.height": {
            "type": int,
            "min": 600,
            "max": 4320
        },
        "window.width": {
            "type": int,
            "min": 800,
            "max": 3840
        },
        "window.height": {
            "type": int,
            "min": 600,
            "max": 2160
        }
    }
    
    def __init__(self, config_dir: str = None, config_filename: str = "user_config.json"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，默认为项目根目录下的 config 文件夹
            config_filename: 配置文件名
        """
        if config_dir is None:
            self.config_dir = Path(__file__).parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)
        
        self.config_file = self.config_dir / config_filename
        
        self.config_data = {}
        
        self._ensure_config_dir()
        self.load_config()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> bool:
        """
        从文件加载配置
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                
                # 验证并修复配置
                if not self.validate_config():
                    print("配置验证失败，正在修复...")
                    self.validate_and_fix_config()
                
                return True
            else:
                self.config_data = self._get_default_config()
                return False
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.config_data = self._get_default_config()
            return False
    
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置字典
        """
        return self.DEFAULT_CONFIG.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键（如 "script.last_selected"）
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键（如 "script.last_selected"）
            value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        keys = key.split('.')
        data = self.config_data
        
        # 保存旧值以便回滚
        old_value = None
        key_exists = False
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        # 检查键是否存在并保存旧值
        if keys[-1] in data:
            old_value = data[keys[-1]]
            key_exists = True
        
        # 设置新值
        data[keys[-1]] = value
        
        # 验证配置是否有效
        if not self.validate_config():
            print(f"配置验证失败: {key}={value}")
            # 回滚更改
            if key_exists:
                data[keys[-1]] = old_value
            else:
                del data[keys[-1]]
            return False
        
        return self.save_config()
    
    def get_last_selected_script(self) -> Optional[str]:
        """
        获取上次选择的脚本
        
        Returns:
            Optional[str]: 脚本名称，如果没有则返回 None
        """
        return self.get("script.last_selected")
    
    def set_last_selected_script(self, script_name: str) -> bool:
        """
        设置上次选择的脚本
        
        Args:
            script_name: 脚本名称
            
        Returns:
            bool: 设置是否成功
        """
        return self.set("script.last_selected", script_name)
    
    def get_last_loop_count(self) -> int:
        """
        获取上次设置的循环次数
        
        Returns:
            int: 循环次数，默认为 1
        """
        return self.get("script.last_loop_count", 1)
    
    def set_last_loop_count(self, count: int) -> bool:
        """
        设置循环次数
        
        Args:
            count: 循环次数
            
        Returns:
            bool: 设置是否成功
        """
        return self.set("script.last_loop_count", count)
    
    def get_auto_switch_to_log(self) -> bool:
        """
        获取是否自动跳转到日志页面
        
        Returns:
            bool: 是否自动跳转，默认为 False
        """
        return self.get("script.auto_switch_to_log", False)
    
    def set_auto_switch_to_log(self, auto_switch: bool) -> bool:
        """
        设置是否自动跳转到日志页面
        
        Args:
            auto_switch: 是否自动跳转
            
        Returns:
            bool: 设置是否成功
        """
        return self.set("script.auto_switch_to_log", auto_switch)
    
    def get_last_resolution_width(self) -> int:
        """
        获取上次设置的游戏分辨率宽度
        
        Returns:
            int: 游戏分辨率宽度，默认为 1920
        """
        return self.get("script.game_resolution.width", 1920)
    
    def get_last_resolution_height(self) -> int:
        """
        获取上次设置的游戏分辨率高度
        
        Returns:
            int: 游戏分辨率高度，默认为 1080
        """
        return self.get("script.game_resolution.height", 1080)
    
    def set_template_resolution(self, width: int, height: int) -> bool:
        """
        设置游戏分辨率
        
        Args:
            width: 游戏分辨率宽度
            height: 游戏分辨率高度
            
        Returns:
            bool: 设置是否成功
        """
        self.set("script.game_resolution.width", width)
        return self.set("script.game_resolution.height", height)
    
    def get_last_recording_name(self) -> str:
        """
        获取上次使用的录制名称
        
        Returns:
            str: 录制名称，默认为空字符串
        """
        return self.get("recording.last_name", "")
    
    def set_last_recording_name(self, name: str) -> bool:
        """
        设置录制名称
        
        Args:
            name: 录制名称
            
        Returns:
            bool: 设置是否成功
        """
        return self.set("recording.last_name", name)
    
    def get_window_size(self) -> tuple:
        """
        获取窗口大小
        
        Returns:
            tuple: (width, height)
        """
        width = self.get("window.width", 900)
        height = self.get("window.height", 700)
        return (width, height)
    
    def set_window_size(self, width: int, height: int) -> bool:
        """
        设置窗口大小
        
        Args:
            width: 窗口宽度
            height: 窗口高度
            
        Returns:
            bool: 设置是否成功
        """
        self.set("window.width", width)
        return self.set("window.height", height)
    
    def get_shortcuts(self) -> Dict[str, str]:
        """
        获取快捷键配置
        
        Returns:
            Dict[str, str]: 快捷键配置字典
        """
        return self.get("shortcuts", {})
    
    def set_shortcuts(self, shortcuts: Dict[str, str]) -> bool:
        """
        设置快捷键配置
        
        Args:
            shortcuts: 快捷键配置字典
            
        Returns:
            bool: 设置是否成功
        """
        return self.set("shortcuts", shortcuts)
    
    def reset_config(self) -> bool:
        """
        重置配置为默认值
        
        Returns:
            bool: 重置是否成功
        """
        self.config_data = self._get_default_config()
        return self.save_config()
    
    def validate_config(self, config_data: Dict[str, Any] = None) -> bool:
        """
        验证配置数据的有效性
        
        Args:
            config_data: 要验证的配置数据，如果为None则验证当前配置
            
        Returns:
            bool: 配置是否有效
        """
        if config_data is None:
            config_data = self.config_data
        
        try:
            # 验证循环次数（如果存在）
            loop_count = self._get_nested_value(config_data, "script.last_loop_count")
            if loop_count is not None:
                if not isinstance(loop_count, int) or loop_count < 1 or loop_count > 9999:
                    return False
            
            # 验证窗口大小（如果存在）
            width = self._get_nested_value(config_data, "window.width")
            if width is not None:
                if not isinstance(width, int) or width < 800 or width > 3840:
                    return False
            
            height = self._get_nested_value(config_data, "window.height")
            if height is not None:
                if not isinstance(height, int) or height < 600 or height > 2160:
                    return False
            
            # 验证快捷键（如果存在）
            shortcuts = self._get_nested_value(config_data, "shortcuts")
            if shortcuts is not None:
                if not isinstance(shortcuts, dict):
                    return False
                for action, shortcut in shortcuts.items():
                    if not self._validate_shortcut(shortcut):
                        return False
            
            return True
        except Exception as e:
            print(f"配置验证异常: {e}")
            return False
    
    def _validate_shortcut(self, shortcut: Any) -> bool:
        """
        验证快捷键的有效性
        
        Args:
            shortcut: 快捷键字符串
            
        Returns:
            bool: 快捷键是否有效
        """
        if not isinstance(shortcut, str):
            return False
        
        # 快捷键不能为空或只包含空格
        if not shortcut.strip():
            return False
        
        # 快捷键长度限制（防止过长）
        if len(shortcut) > 50:
            return False
        
        # 允许的快捷键格式：字母、数字、功能键、特殊键
        valid_keys = [
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            'esc', 'enter', 'space', 'tab', 'backspace', 'delete', 'insert',
            'home', 'end', 'pageup', 'pagedown',
            'up', 'down', 'left', 'right',
            'ctrl', 'alt', 'shift'
        ]
        
        # 检查是否是有效的单键
        if shortcut.lower() in valid_keys:
            return True
        
        # 检查是否是单个字母或数字
        if len(shortcut) == 1 and (shortcut.isalpha() or shortcut.isdigit()):
            return True
        
        # 检查组合键（如 ctrl+a, alt+f4 等）
        if '+' in shortcut:
            parts = [part.strip().lower() for part in shortcut.split('+')]
            if len(parts) >= 2:
                # 每个部分都应该是有效的键
                for part in parts:
                    if part not in valid_keys and not (len(part) == 1 and (part.isalpha() or part.isdigit())):
                        return False
                return True
        
        return False
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """
        获取嵌套字典中的值
        
        Args:
            data: 字典数据
            key: 点号分隔的键（如 "script.last_loop_count"）
            
        Returns:
            Any: 找到的值，如果不存在则返回 None
        """
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def validate_and_fix_config(self) -> bool:
        """
        验证并修复配置，将无效值替换为默认值
        
        Returns:
            bool: 是否修复了配置
        """
        fixed = False
        
        # 确保配置结构存在
        if "script" not in self.config_data:
            self.config_data["script"] = {}
            fixed = True
        if "window" not in self.config_data:
            self.config_data["window"] = {}
            fixed = True
        if "shortcuts" not in self.config_data:
            self.config_data["shortcuts"] = {}
            fixed = True
        
        # 验证并修复循环次数
        loop_count = self.get("script.last_loop_count")
        if not isinstance(loop_count, int) or loop_count < 1 or loop_count > 9999:
            self.config_data["script"]["last_loop_count"] = 1
            fixed = True
        
        # 验证并修复窗口大小
        width = self.get("window.width")
        if not isinstance(width, int) or width < 800 or width > 3840:
            self.config_data["window"]["width"] = 900
            fixed = True
        
        height = self.get("window.height")
        if not isinstance(height, int) or height < 600 or height > 2160:
            self.config_data["window"]["height"] = 700
            fixed = True
        
        # 验证并修复快捷键
        shortcuts = self.get("shortcuts", {})
        if not isinstance(shortcuts, dict):
            self.config_data["shortcuts"] = self.DEFAULT_CONFIG["shortcuts"].copy()
            fixed = True
        else:
            for action, default_shortcut in self.DEFAULT_CONFIG["shortcuts"].items():
                if action not in shortcuts or not self._validate_shortcut(shortcuts.get(action)):
                    self.config_data["shortcuts"][action] = default_shortcut
                    fixed = True
        
        if fixed:
            self.save_config()
        
        return fixed
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 所有配置数据
        """
        return self.config_data.copy()


# 全局配置管理器实例
config_manager = ConfigManager()
