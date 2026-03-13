"""
任务执行器单元测试
测试任务执行器的功能，包括任务执行、取消和进度报告
"""

import pytest
import time
from PySide6.QtCore import QObject, QCoreApplication, QEventLoop
from src.task_executor import TaskWorker, TaskExecutor


@pytest.fixture(scope="session")
def qt_app():
    """创建Qt应用实例"""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    yield app


class TestTaskWorker:
    """测试TaskWorker类"""
    
    def test_task_worker_basic_execution(self, qt_app):
        """测试基本任务执行"""
        def simple_task():
            return "task completed"
        
        worker = TaskWorker(simple_task)
        worker.finished.connect(lambda result: setattr(self, 'result', result))
        worker.start()
        
        loop = QEventLoop()
        worker.finished.connect(loop.quit)
        worker.error.connect(loop.quit)
        loop.exec()
        
        assert hasattr(self, 'result')
        assert self.result == "task completed"
    
    def test_task_worker_with_args(self, qt_app):
        """测试带参数的任务执行"""
        def task_with_args(a, b):
            return a + b
        
        worker = TaskWorker(task_with_args, 5, 3)
        worker.finished.connect(lambda result: setattr(self, 'result', result))
        worker.start()
        
        loop = QEventLoop()
        worker.finished.connect(loop.quit)
        worker.error.connect(loop.quit)
        loop.exec()
        
        assert self.result == 8
    
    def test_task_worker_with_kwargs(self, qt_app):
        """测试带关键字参数的任务执行"""
        def task_with_kwargs(x, y):
            return x * y
        
        worker = TaskWorker(task_with_kwargs, x=4, y=5)
        worker.finished.connect(lambda result: setattr(self, 'result', result))
        worker.start()
        
        loop = QEventLoop()
        worker.finished.connect(loop.quit)
        worker.error.connect(loop.quit)
        loop.exec()
        
        assert self.result == 20
    
    def test_task_worker_error_handling(self, qt_app):
        """测试任务错误处理"""
        def failing_task():
            raise ValueError("test error")
        
        worker = TaskWorker(failing_task)
        worker.error.connect(lambda error_type, error_msg: setattr(self, 'error', (error_type, error_msg)))
        worker.start()
        
        loop = QEventLoop()
        worker.finished.connect(loop.quit)
        worker.error.connect(loop.quit)
        loop.exec()
        
        assert hasattr(self, 'error')
        assert self.error[0] == "ValueError"
        assert "test error" in self.error[1]
    
    def test_task_worker_cancel(self, qt_app):
        """测试任务取消"""
        def long_running_task():
            time.sleep(5)
            return "should not reach here"
        
        worker = TaskWorker(long_running_task)
        worker.start()
        time.sleep(0.1)
        worker.cancel()
        
        assert worker.is_cancelled()
    
    def test_task_worker_progress_callback(self, qt_app):
        """测试进度回调"""
        def task_with_progress(progress_callback=None):
            if progress_callback:
                progress_callback(50, 100)
                progress_callback(100, 100)
            return "done"
        
        worker = TaskWorker(task_with_progress)
        worker.set_progress_callback(lambda current, total: setattr(self, 'progress', (current, total)))
        worker.finished.connect(lambda result: setattr(self, 'result', result))
        worker.start()
        
        loop = QEventLoop()
        worker.finished.connect(loop.quit)
        worker.error.connect(loop.quit)
        loop.exec()
        
        assert hasattr(self, 'progress')
        assert self.progress[0] == 100
        assert self.progress[1] == 100
        assert self.result == "done"


class TestTaskExecutor:
    """测试TaskExecutor类"""
    
    def test_execute_task(self, qt_app):
        """测试执行任务"""
        executor = TaskExecutor()
        
        def simple_task():
            return "task result"
        
        executor.task_finished.connect(lambda result: setattr(self, 'result', result))
        success = executor.execute_task(simple_task)
        
        assert success
        
        loop = QEventLoop()
        executor.task_finished.connect(loop.quit)
        executor.task_error.connect(loop.quit)
        loop.exec()
        
        assert hasattr(self, 'result')
        assert self.result == "task result"
    
    def test_execute_task_with_args(self, qt_app):
        """测试带参数的任务执行"""
        executor = TaskExecutor()
        
        def task_with_args(a, b):
            return a - b
        
        executor.task_finished.connect(lambda result: setattr(self, 'result', result))
        executor.execute_task(task_with_args, 10, 3)
        
        loop = QEventLoop()
        executor.task_finished.connect(loop.quit)
        executor.task_error.connect(loop.quit)
        loop.exec()
        
        assert self.result == 7
    
    def test_busy_state(self, qt_app):
        """测试忙碌状态"""
        executor = TaskExecutor()
        
        def long_task():
            time.sleep(1)
            return "done"
        
        executor.execute_task(long_task)
        
        assert executor.is_busy()
        
        def another_task():
            return "should not execute"
        
        success = executor.execute_task(another_task)
        
        assert not success
        
        loop = QEventLoop()
        executor.task_finished.connect(loop.quit)
        executor.task_error.connect(loop.quit)
        loop.exec()
        
        assert not executor.is_busy()
    
    def test_cancel_task(self, qt_app):
        """测试取消任务"""
        executor = TaskExecutor()
        
        def long_task():
            time.sleep(5)
            return "should not complete"
        
        executor.execute_task(long_task)
        time.sleep(0.1)
        
        success = executor.cancel_task()
        
        assert success
        assert not executor.is_busy()
    
    def test_task_error_handling(self, qt_app):
        """测试任务错误处理"""
        executor = TaskExecutor()
        
        def failing_task():
            raise RuntimeError("task failed")
        
        executor.task_error.connect(lambda error_type, error_msg: setattr(self, 'error', (error_type, error_msg)))
        executor.execute_task(failing_task)
        
        loop = QEventLoop()
        executor.task_finished.connect(loop.quit)
        executor.task_error.connect(loop.quit)
        loop.exec()
        
        assert hasattr(self, 'error')
        assert self.error[0] == "RuntimeError"
        assert "task failed" in self.error[1]
    
    def test_progress_signal(self, qt_app):
        """测试进度信号"""
        executor = TaskExecutor()
        
        def task_with_progress(progress_callback=None):
            if progress_callback:
                for i in range(1, 6):
                    progress_callback(i, 5)
                    time.sleep(0.05)
            return "completed"
        
        executor.task_progress.connect(lambda current, total: setattr(self, 'progress', (current, total)))
        executor.task_finished.connect(lambda result: setattr(self, 'result', result))
        executor.execute_task(task_with_progress)
        
        loop = QEventLoop()
        executor.task_finished.connect(loop.quit)
        executor.task_error.connect(loop.quit)
        loop.exec()
        
        assert hasattr(self, 'progress')
        assert self.progress[0] == 5
        assert self.progress[1] == 5
        assert self.result == "completed"
    
    def test_cleanup(self, qt_app):
        """测试清理功能"""
        executor = TaskExecutor()
        
        def long_task():
            time.sleep(5)
            return "done"
        
        executor.execute_task(long_task)
        
        time.sleep(0.1)
        
        assert executor.is_busy()
        
        executor.cleanup()
        
        assert not executor.is_busy()
