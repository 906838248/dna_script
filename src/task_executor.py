"""
任务执行器
用于在工作线程中执行耗时操作，避免阻塞UI线程
支持进度报告和任务取消
"""

from PySide6.QtCore import QObject, Signal, QThread
from typing import Callable, Optional, Any


class TaskWorker(QThread):
    """
    任务工作线程
    在后台线程中执行耗时操作
    """
    
    finished = Signal(object)  # 任务完成信号，参数为结果
    error = Signal(str, str)  # 错误信号，参数为(错误类型, 错误消息)
    progress = Signal(int, int)  # 进度信号，参数为(当前值, 总值)
    
    def __init__(self, task_func: Callable, *args, **kwargs):
        """
        初始化任务工作线程
        
        Args:
            task_func: 要执行的任务函数
            *args: 任务函数的位置参数
            **kwargs: 任务函数的关键字参数
        """
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False
        self._progress_callback = None
    
    def run(self):
        """
        执行任务
        """
        try:
            if self._progress_callback:
                self.kwargs['progress_callback'] = self._progress_callback
            
            result = self.task_func(*self.args, **self.kwargs)
            
            if not self._is_cancelled:
                self.finished.emit(result)
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            self.error.emit(error_type, error_msg)
    
    def cancel(self):
        """
        取消任务
        """
        self._is_cancelled = True
        self.quit()
        self.wait()
    
    def set_progress_callback(self, callback: Callable[[int, int], None]):
        """
        设置进度回调函数
        
        Args:
            callback: 进度回调函数，参数为(当前值, 总值)
        """
        self._progress_callback = callback
    
    def is_cancelled(self) -> bool:
        """
        检查任务是否被取消
        
        Returns:
            bool: 是否被取消
        """
        return self._is_cancelled


class TaskExecutor(QObject):
    """
    任务执行器
    管理任务工作线程的生命周期
    提供任务取消和进度报告功能
    """
    
    task_finished = Signal(object)  # 任务完成信号
    task_error = Signal(str, str)  # 任务错误信号
    task_progress = Signal(int, int)  # 任务进度信号
    
    def __init__(self):
        """
        初始化任务执行器
        """
        super().__init__()
        self._current_worker: Optional[TaskWorker] = None
        self._is_busy = False
    
    def execute_task(self, task_func: Callable, *args, **kwargs) -> bool:
        """
        执行任务
        
        Args:
            task_func: 要执行的任务函数
            *args: 任务函数的位置参数
            **kwargs: 任务函数的关键字参数
            
        Returns:
            bool: 是否成功启动任务
        """
        if self._is_busy:
            return False
        
        self._current_worker = TaskWorker(task_func, *args, **kwargs)
        self._current_worker.finished.connect(self._on_task_finished)
        self._current_worker.error.connect(self._on_task_error)
        self._current_worker.progress.connect(self.task_progress)
        
        self._current_worker.start()
        self._is_busy = True
        
        return True
    
    def cancel_task(self) -> bool:
        """
        取消当前任务
        
        Returns:
            bool: 是否成功取消
        """
        if not self._is_busy or not self._current_worker:
            return False
        
        self._current_worker.cancel()
        self._is_busy = False
        self._current_worker = None
        
        return True
    
    def is_busy(self) -> bool:
        """
        检查是否有任务正在执行
        
        Returns:
            bool: 是否忙碌
        """
        return self._is_busy
    
    def _on_task_finished(self, result: Any):
        """
        任务完成时的回调
        
        Args:
            result: 任务结果
        """
        self._is_busy = False
        self._current_worker = None
        self.task_finished.emit(result)
    
    def _on_task_error(self, error_type: str, error_msg: str):
        """
        任务出错时的回调
        
        Args:
            error_type: 错误类型
            error_msg: 错误消息
        """
        self._is_busy = False
        self._current_worker = None
        self.task_error.emit(error_type, error_msg)
    
    def cleanup(self):
        """
        清理资源
        """
        if self._is_busy and self._current_worker:
            self.cancel_task()
