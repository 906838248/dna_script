"""
自动化控制器
管理自动化脚本的启动、停止和状态
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox
from src.base_automation import BaseAutomationThread


class AutomationController(QObject):
    """
    自动化控制器类
    负责管理自动化脚本的生命周期
    """
    
    log_signal = Signal(str)
    finished_signal = Signal()
    progress_signal = Signal(int, int)
    
    def __init__(self):
        super().__init__()
        self.automation_thread: BaseAutomationThread = None
        self.current_script = None
        self.is_running = False
    
    def start_automation(self, script_info, loop_count):
        """
        启动自动化脚本
        
        Args:
            script_info: 脚本信息对象
            loop_count: 循环次数
            
        Returns:
            bool: 是否成功启动
        """
        if self.is_running:
            self.log_signal.emit("自动化正在运行中！")
            return False
        
        if not script_info:
            self.log_signal.emit("请先选择一个脚本！")
            return False
        
        self.log_signal.emit(f"\n开始执行脚本: {script_info.name}")
        self.log_signal.emit(f"循环次数: {loop_count}")
        
        try:
            self.current_script = script_info
            self.automation_thread = script_info.script_class(loop_count, script_info.img_folder)
            
            self.automation_thread.log_signal.connect(self.log_signal)
            self.automation_thread.finished_signal.connect(self._on_automation_finished)
            self.automation_thread.progress_signal.connect(self.progress_signal)
            
            self.automation_thread.start()
            self.is_running = True
            
            return True
        except Exception as e:
            self.log_signal.emit(f"启动自动化失败: {str(e)}")
            return False
    
    def stop_automation(self):
        """
        停止自动化脚本
        
        Returns:
            bool: 是否成功停止
        """
        if not self.is_running or not self.automation_thread:
            return False
        
        self.log_signal.emit("正在停止自动化...")
        self.automation_thread.stop()
        self.automation_thread.wait()
        self.log_signal.emit("自动化已停止")
        
        return True
    
    def _on_automation_finished(self):
        """自动化完成时的回调函数"""
        self.is_running = False
        self.finished_signal.emit()
    
    def get_current_script(self):
        """
        获取当前运行的脚本
        
        Returns:
            当前脚本信息对象
        """
        return self.current_script
    
    def is_automation_running(self):
        """
        检查自动化是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self.is_running
