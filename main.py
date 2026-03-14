"""
二重螺旋 - 统一脚本管理器
主程序入口
"""

import sys
import os
import signal
import multiprocessing
import ctypes
import psutil
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.styles import apply_dark_theme
from src.shortcut_manager import shortcut_manager, ShortcutAction


def setup_dpi_awareness():
    """设置DPI感知，防止在高DPI屏幕上出现显示问题"""
    if sys.platform == 'win32':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass


def cleanup_zombie_processes():
    """
    清理僵尸进程
    查找并终止所有由当前进程创建的子进程
    """
    try:
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        
        for child in children:
            try:
                if child.is_running():
                    child.terminate()
                    child.wait(timeout=2)
                    
                    # 如果进程仍然存活，强制杀死
                    if child.is_running():
                        child.kill()
                        child.wait(timeout=1)
            except Exception as e:
                print(f"清理子进程时发生错误: {e}")
    except Exception as e:
        print(f"获取子进程列表时发生错误: {e}")


def setup_signal_handlers():
    """设置信号处理器，确保程序退出时清理资源"""
    def signal_handler(signum, frame):
        """信号处理函数"""
        print(f"接收到信号 {signum}，正在清理资源...")
        cleanup_zombie_processes()
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if sys.platform == 'win32':
        signal.signal(signal.SIGBREAK, signal_handler)


def setup_shortcuts(window):
    """设置全局快捷键"""
    shortcut_manager.register_callback(ShortcutAction.START_AUTOMATION, window.start_automation)
    shortcut_manager.register_callback(ShortcutAction.STOP_AUTOMATION, window.stop_automation)
    shortcut_manager.register_callback(ShortcutAction.CLEAR_LOG, window.clear_log)
    shortcut_manager.register_callback(ShortcutAction.TOGGLE_RECORDING, window.toggle_recording)
    shortcut_manager.register_callback(ShortcutAction.STOP_RECORDING_PLAYBACK, window.stop_playback_ui)
    shortcut_manager.setup_hotkeys()


def main():
    """主函数"""
    setup_dpi_awareness()
    setup_signal_handlers()
    
    multiprocessing.set_start_method('spawn', force=True)
    
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    
    window = MainWindow()
    window.show()
    
    setup_shortcuts(window)
    
    # 程序退出时清理僵尸进程
    def on_app_exit():
        cleanup_zombie_processes()
    
    app.aboutToQuit.connect(on_app_exit)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
