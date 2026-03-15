"""
自动化控制器
管理自动化脚本的启动、停止和状态
增强错误处理和异常管理
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QThread
from typing import Optional
from src.base_automation import BaseAutomationThread


class AutomationError(Exception):
    """
    自动化错误基类
    """
    pass


class AutomationRunningError(AutomationError):
    """
    自动化正在运行错误
    """
    pass


class ScriptNotFoundError(AutomationError):
    """
    脚本未找到错误
    """
    pass


class ScriptInitializationError(AutomationError):
    """
    脚本初始化错误
    """
    pass


class AutomationExecutionError(AutomationError):
    """
    自动化执行错误
    """
    pass


class AutomationController(QObject):
    """
    自动化控制器类
    负责管理自动化脚本的生命周期
    提供完善的错误处理和异常管理
    """
    
    log_signal = Signal(str)
    finished_signal = Signal()
    progress_signal = Signal(int, int)
    error_signal = Signal(str, str)
    
    def __init__(self):
        """
        初始化自动化控制器
        """
        super().__init__()
        self.automation_thread: Optional[BaseAutomationThread] = None
        self.current_script = None
        self.is_running = False
        self.last_error = None
    
    def start_automation(self, script_info, loop_count, game_resolution=None):
        """
        启动自动化脚本
        
        Args:
            script_info: 脚本信息对象
            loop_count: 循环次数
            game_resolution: 游戏窗口分辨率，如果为None则使用默认分辨率(1920x1080)
            
        Returns:
            bool: 是否成功启动
            
        Raises:
            AutomationRunningError: 自动化正在运行中
            ScriptNotFoundError: 脚本信息无效
            ScriptInitializationError: 脚本初始化失败
            AutomationExecutionError: 自动化执行失败
        """
        if self.is_running:
            error_msg = "自动化正在运行中！"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("AutomationRunningError", error_msg)
            raise AutomationRunningError(error_msg)
        
        if not script_info:
            error_msg = "请先选择一个脚本！"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("ScriptNotFoundError", error_msg)
            raise ScriptNotFoundError(error_msg)
        
        if not hasattr(script_info, 'name') or not hasattr(script_info, 'script_class'):
            error_msg = "脚本信息无效，缺少必要属性！"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("ScriptNotFoundError", error_msg)
            raise ScriptNotFoundError(error_msg)
        
        if not isinstance(loop_count, int) or loop_count < 1:
            error_msg = f"循环次数无效: {loop_count}，必须为正整数"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("ValueError", error_msg)
            raise ValueError(error_msg)
        
        self.log_signal.emit(f"\n开始执行脚本: {script_info.name}")
        self.log_signal.emit(f"循环次数: {loop_count}")
        
        try:
            self.current_script = script_info
            
            try:
                self.automation_thread = script_info.script_class(loop_count, script_info.img_folder, game_resolution)
            except Exception as e:
                error_msg = f"脚本初始化失败: {str(e)}"
                self.log_signal.emit(error_msg)
                self.error_signal.emit("ScriptInitializationError", error_msg)
                raise ScriptInitializationError(error_msg) from e
            
            try:
                self.automation_thread.log_signal.connect(self.log_signal)
                self.automation_thread.finished_signal.connect(self._on_automation_finished)
                self.automation_thread.progress_signal.connect(self.progress_signal)
            except Exception as e:
                error_msg = f"信号连接失败: {str(e)}"
                self.log_signal.emit(error_msg)
                self.error_signal.emit("ConnectionError", error_msg)
                raise AutomationExecutionError(error_msg) from e
            
            try:
                self.automation_thread.start()
                self.is_running = True
                self.last_error = None
                self.log_signal.emit("自动化已成功启动")
                return True
            except Exception as e:
                error_msg = f"线程启动失败: {str(e)}"
                self.log_signal.emit(error_msg)
                self.error_signal.emit("ThreadError", error_msg)
                self.is_running = False
                raise AutomationExecutionError(error_msg) from e
                
        except (AutomationRunningError, ScriptNotFoundError, ScriptInitializationError):
            raise
        except Exception as e:
            error_msg = f"启动自动化时发生未知错误: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("UnknownError", error_msg)
            self.is_running = False
            self.current_script = None
            self.automation_thread = None
            raise AutomationExecutionError(error_msg) from e
    
    def stop_automation(self, timeout: int = 10):
        """
        停止自动化脚本
        
        Args:
            timeout: 停止超时时间（秒），默认10秒
            
        Returns:
            bool: 是否成功停止
            
        Raises:
            TimeoutError: 停止超时
            RuntimeError: 停止失败
        """
        if not self.is_running or not self.automation_thread:
            error_msg = "自动化未运行，无需停止"
            self.log_signal.emit(error_msg)
            return False
        
        self.log_signal.emit("正在停止自动化...")
        
        try:
            self.automation_thread.stop()
            
            if not self.automation_thread.wait(timeout * 1000):
                error_msg = f"停止自动化超时（{timeout}秒），强制终止线程"
                self.log_signal.emit(error_msg)
                self.error_signal.emit("TimeoutError", error_msg)
                
                try:
                    self.automation_thread.terminate()
                    self.automation_thread.wait(2000)
                except Exception as e:
                    self.log_signal.emit(f"强制终止线程失败: {str(e)}")
                
                self.is_running = False
                self.current_script = None
                self.automation_thread = None
                raise TimeoutError(error_msg)
            
            self.is_running = False
            self.current_script = None
            self.automation_thread = None
            self.log_signal.emit("自动化已成功停止")
            return True
            
        except TimeoutError:
            raise
        except Exception as e:
            error_msg = f"停止自动化时发生错误: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("RuntimeError", error_msg)
            raise RuntimeError(error_msg) from e
    
    def _on_automation_finished(self):
        """
        自动化完成时的回调函数
        处理正常完成和异常完成的情况
        """
        self.is_running = False
        self.current_script = None
        self.automation_thread = None
        self.finished_signal.emit()
        self.log_signal.emit("自动化执行完成")
    
    def get_current_script(self):
        """
        获取当前运行的脚本
        
        Returns:
            当前脚本信息对象，如果没有则返回None
        """
        return self.current_script
    
    def is_automation_running(self):
        """
        检查自动化是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        if self.is_running and self.automation_thread:
            return self.automation_thread.isRunning()
        return False
    
    def get_last_error(self):
        """
        获取最后一次错误信息
        
        Returns:
            最后一次错误信息，如果没有则返回None
        """
        return self.last_error
    
    def cleanup(self):
        """
        清理资源
        在控制器销毁时调用
        """
        if self.is_automation_running():
            try:
                self.stop_automation(timeout=5)
            except Exception as e:
                self.log_signal.emit(f"清理资源时发生错误: {str(e)}")
                # 强制终止线程
                if self.automation_thread:
                    try:
                        self.automation_thread.terminate()
                        self.automation_thread.wait(2000)
                    except:
                        pass
        
        # 断开所有信号连接
        if self.automation_thread:
            try:
                self.automation_thread.log_signal.disconnect()
                self.automation_thread.finished_signal.disconnect()
                self.automation_thread.progress_signal.disconnect()
            except:
                pass
        
        self.automation_thread = None
        self.current_script = None
        self.is_running = False
