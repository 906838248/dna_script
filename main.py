"""
二重螺旋 - 统一脚本管理器
主程序入口
"""

import sys
import multiprocessing
import ctypes
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
    
    multiprocessing.set_start_method('spawn', force=True)
    
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    
    window = MainWindow()
    window.show()
    
    setup_shortcuts(window)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
