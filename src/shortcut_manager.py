"""
快捷键管理模块
用于管理程序的全局快捷键配置
"""

import keyboard
from typing import Dict, Callable, Optional
from enum import Enum


class ShortcutAction(Enum):
    """快捷键操作枚举"""
    START_AUTOMATION = "start_automation"
    STOP_AUTOMATION = "stop_automation"
    CLEAR_LOG = "clear_log"
    TOGGLE_RECORDING = "toggle_recording"
    STOP_RECORDING_PLAYBACK = "stop_recording_playback"


class ShortcutManager:
    """快捷键管理器类"""
    
    def __init__(self):
        """初始化快捷键管理器"""
        self.shortcuts = {
            ShortcutAction.START_AUTOMATION: "F5",
            ShortcutAction.STOP_AUTOMATION: "F6",
            ShortcutAction.CLEAR_LOG: "F7",
            ShortcutAction.TOGGLE_RECORDING: "F8",
            ShortcutAction.STOP_RECORDING_PLAYBACK: "esc"
        }
        
        self.action_callbacks = {}
        self.registered_hotkeys = {}
    
    def get_shortcut(self, action: ShortcutAction) -> str:
        """
        获取指定操作的快捷键
        
        Args:
            action: 快捷键操作枚举
            
        Returns:
            str: 快捷键字符串
        """
        return self.shortcuts.get(action, "")
    
    def set_shortcut(self, action: ShortcutAction, shortcut: str) -> bool:
        """
        设置指定操作的快捷键
        
        Args:
            action: 快捷键操作枚举
            shortcut: 快捷键字符串
            
        Returns:
            bool: 设置是否成功
        """
        if self._validate_shortcut(shortcut):
            self.shortcuts[action] = shortcut
            return True
        return False
    
    def register_callback(self, action: ShortcutAction, callback: Callable):
        """
        注册快捷键回调函数
        
        Args:
            action: 快捷键操作枚举
            callback: 回调函数
        """
        self.action_callbacks[action] = callback
    
    def setup_hotkeys(self):
        """设置所有快捷键"""
        self._remove_all_hotkeys()
        
        for action, shortcut in self.shortcuts.items():
            if action in self.action_callbacks:
                try:
                    hotkey_id = keyboard.add_hotkey(shortcut, self.action_callbacks[action])
                    self.registered_hotkeys[action] = hotkey_id
                except Exception as e:
                    print(f"注册快捷键失败: {action} -> {shortcut}, 错误: {e}")
    
    def _remove_all_hotkeys(self):
        """移除所有已注册的快捷键"""
        for action in list(self.registered_hotkeys.keys()):
            try:
                keyboard.remove_hotkey(self.shortcuts[action])
            except:
                pass
        self.registered_hotkeys.clear()
    
    def _validate_shortcut(self, shortcut: str) -> bool:
        """
        验证快捷键是否有效
        
        Args:
            shortcut: 快捷键字符串
            
        Returns:
            bool: 是否有效
        """
        if not shortcut:
            return False
        
        try:
            keyboard.parse_hotkey(shortcut)
            return True
        except:
            return False
    
    def get_shortcut_description(self, action: ShortcutAction) -> str:
        """
        获取快捷键的描述文本
        
        Args:
            action: 快捷键操作枚举
            
        Returns:
            str: 描述文本
        """
        descriptions = {
            ShortcutAction.START_AUTOMATION: "开始自动化",
            ShortcutAction.STOP_AUTOMATION: "停止自动化",
            ShortcutAction.CLEAR_LOG: "清空日志",
            ShortcutAction.TOGGLE_RECORDING: "开始/停止录制",
            ShortcutAction.STOP_RECORDING_PLAYBACK: "停止录制/回放"
        }
        return descriptions.get(action, "")
    
    def get_all_shortcuts(self) -> Dict[str, str]:
        """
        获取所有快捷键配置
        
        Returns:
            Dict[str, str]: 快捷键配置字典 {action_name: shortcut}
        """
        return {action.value: shortcut for action, shortcut in self.shortcuts.items()}
    
    def set_all_shortcuts(self, shortcuts: Dict[str, str]) -> bool:
        """
        设置所有快捷键
        
        Args:
            shortcuts: 快捷键配置字典 {action_name: shortcut}
            
        Returns:
            bool: 设置是否成功
        """
        try:
            for action_name, shortcut in shortcuts.items():
                action = ShortcutAction(action_name)
                if not self._validate_shortcut(shortcut):
                    return False
                self.shortcuts[action] = shortcut
            return True
        except:
            return False
    
    def reset_to_default(self):
        """重置所有快捷键为默认值"""
        self.shortcuts = {
            ShortcutAction.START_AUTOMATION: "F5",
            ShortcutAction.STOP_AUTOMATION: "F6",
            ShortcutAction.CLEAR_LOG: "F7",
            ShortcutAction.TOGGLE_RECORDING: "F8",
            ShortcutAction.STOP_RECORDING_PLAYBACK: "esc"
        }
    
    def cleanup(self):
        """清理资源，移除所有快捷键"""
        self._remove_all_hotkeys()
        self.action_callbacks.clear()


# 全局快捷键管理器实例
shortcut_manager = ShortcutManager()
