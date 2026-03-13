"""
异步日志处理器单元测试
测试异步日志写入、批量处理和资源清理功能
"""

import logging
import os
import time
import queue
import tempfile
import shutil
from pathlib import Path
import pytest

from src.async_log_handler import AsyncLogHandler, AsyncLogManager
from src.log_manager import LogManager


class TestAsyncLogHandler:
    """异步日志处理器测试类"""
    
    @pytest.fixture
    def temp_log_dir(self):
        """临时日志目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def base_handler(self, temp_log_dir):
        """基础日志处理器"""
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(
            temp_log_dir / 'test.log',
            maxBytes=1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        handler.setLevel(logging.DEBUG)
        return handler
    
    def test_async_handler_initialization(self, base_handler):
        """测试异步日志处理器初始化"""
        async_handler = AsyncLogHandler(base_handler)
        
        assert async_handler.base_handler == base_handler
        assert async_handler.batch_size == 10
        assert async_handler.flush_interval == 1.0
        assert async_handler.worker_thread is not None
        assert async_handler.worker_thread.is_alive()
    
    def test_async_handler_emit(self, base_handler, temp_log_dir):
        """测试异步日志发送"""
        async_handler = AsyncLogHandler(base_handler, batch_size=5, flush_interval=0.1)
        
        logger = logging.getLogger('test_async')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(async_handler)
        
        test_messages = [
            "Test message 1",
            "Test message 2",
            "Test message 3"
        ]
        
        for msg in test_messages:
            logger.info(msg)
        
        time.sleep(0.3)
        async_handler.flush()
        
        log_file = temp_log_dir / 'test.log'
        assert log_file.exists()
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for msg in test_messages:
                assert msg in content
        
        async_handler.close()
        logger.removeHandler(async_handler)
    
    def test_async_handler_batch_writing(self, base_handler, temp_log_dir):
        """测试批量写入功能"""
        async_handler = AsyncLogHandler(base_handler, batch_size=3, flush_interval=10.0)
        
        logger = logging.getLogger('test_batch')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(async_handler)
        
        for i in range(5):
            logger.info(f"Batch test message {i}")
        
        time.sleep(0.5)
        
        log_file = temp_log_dir / 'test.log'
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Batch test message 0" in content
            assert "Batch test message 1" in content
            assert "Batch test message 2" in content
        
        async_handler.close()
        logger.removeHandler(async_handler)
    
    def test_async_handler_flush_interval(self, base_handler, temp_log_dir):
        """测试刷新间隔功能"""
        async_handler = AsyncLogHandler(base_handler, batch_size=100, flush_interval=0.2)
        
        logger = logging.getLogger('test_flush')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(async_handler)
        
        logger.info("Flush interval test")
        
        time.sleep(0.5)
        
        log_file = temp_log_dir / 'test.log'
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Flush interval test" in content
        
        async_handler.close()
        logger.removeHandler(async_handler)
    
    def test_async_handler_close(self, base_handler, temp_log_dir):
        """测试关闭功能"""
        async_handler = AsyncLogHandler(base_handler)
        
        logger = logging.getLogger('test_close')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(async_handler)
        
        logger.info("Before close")
        
        async_handler.close()
        
        assert not async_handler.worker_thread.is_alive()
        
        log_file = temp_log_dir / 'test.log'
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Before close" in content
        
        logger.removeHandler(async_handler)
    
    def test_async_handler_queue_full(self, base_handler, temp_log_dir):
        """测试队列满的情况"""
        async_handler = AsyncLogHandler(base_handler, batch_size=100, flush_interval=10.0)
        async_handler.log_queue = queue.Queue(maxsize=2)
        
        logger = logging.getLogger('test_queue')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(async_handler)
        
        for i in range(10):
            logger.info(f"Message {i}")
        
        async_handler.close()
        logger.removeHandler(async_handler)
    
    def test_async_handler_performance(self, base_handler, temp_log_dir):
        """测试异步日志性能"""
        async_handler = AsyncLogHandler(base_handler, batch_size=50, flush_interval=0.5)
        
        logger = logging.getLogger('test_perf')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(async_handler)
        
        start_time = time.time()
        
        for i in range(100):
            logger.info(f"Performance test message {i}")
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 1.0, f"异步日志写入耗时: {elapsed_time:.2f}秒"
        
        time.sleep(1.0)
        async_handler.flush()
        
        log_file = temp_log_dir / 'test.log'
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Performance test message 0" in content
            assert "Performance test message 99" in content
        
        async_handler.close()
        logger.removeHandler(async_handler)


class TestAsyncLogManager:
    """异步日志管理器测试类"""
    
    @pytest.fixture
    def temp_log_dir(self):
        """临时日志目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_async_log_manager_initialization(self, temp_log_dir):
        """测试异步日志管理器初始化"""
        manager = AsyncLogManager(temp_log_dir)
        
        assert manager.log_dir == temp_log_dir
        assert manager.batch_size == 10
        assert manager.flush_interval == 1.0
        assert len(manager.async_handlers) == 0
    
    def test_create_async_file_handler(self, temp_log_dir):
        """测试创建异步文件处理器"""
        manager = AsyncLogManager(temp_log_dir)
        
        handler = manager.create_async_file_handler(
            'test_async.log',
            level=logging.DEBUG,
            max_bytes=1024*1024,
            backup_count=3
        )
        
        assert isinstance(handler, AsyncLogHandler)
        assert len(manager.async_handlers) == 1
        assert handler.worker_thread.is_alive()
        
        logger = logging.getLogger('test_manager')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        logger.info("Test message")
        
        time.sleep(1.0)
        handler.flush()
        time.sleep(0.5)
        
        log_file = temp_log_dir / 'test_async.log'
        assert log_file.exists()
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test message" in content
        
        logger.removeHandler(handler)
        manager.cleanup()
    
    def test_async_log_manager_cleanup(self, temp_log_dir):
        """测试清理功能"""
        manager = AsyncLogManager(temp_log_dir)
        
        handler1 = manager.create_async_file_handler('test1.log')
        handler2 = manager.create_async_file_handler('test2.log')
        
        assert len(manager.async_handlers) == 2
        
        manager.cleanup()
        
        assert len(manager.async_handlers) == 0
        assert not handler1.worker_thread.is_alive()
        assert not handler2.worker_thread.is_alive()


class TestLogManagerAsyncIntegration:
    """LogManager异步日志集成测试"""
    
    @pytest.fixture
    def temp_log_dir(self):
        """临时日志目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_log_manager_with_async_enabled(self, temp_log_dir):
        """测试启用异步日志的LogManager"""
        LogManager._instance = None
        LogManager._initialized = False
        
        log_manager = LogManager(
            log_dir=str(temp_log_dir),
            enable_async=True
        )
        
        assert log_manager.enable_async is True
        assert log_manager.async_log_manager is not None
        
        logger = log_manager.get_logger()
        
        test_messages = [
            "Async test message 1",
            "Async test message 2",
            "Async test message 3"
        ]
        
        for msg in test_messages:
            logger.info(msg)
        
        time.sleep(2.0)
        
        log_manager.cleanup()
    
    def test_log_manager_with_async_disabled(self, temp_log_dir):
        """测试禁用异步日志的LogManager"""
        LogManager._instance = None
        LogManager._initialized = False
        
        log_manager = LogManager(
            log_dir=str(temp_log_dir),
            enable_async=False
        )
        
        assert log_manager.enable_async is False
        assert log_manager.async_log_manager is None
        
        logger = log_manager.get_logger()
        logger.info("Sync test message")
        
        time.sleep(0.5)
        
        log_manager.cleanup()
    
    def test_log_manager_async_performance(self, temp_log_dir):
        """测试异步日志性能提升"""
        LogManager._instance = None
        LogManager._initialized = False
        
        log_manager = LogManager(
            log_dir=str(temp_log_dir),
            enable_async=True
        )
        
        logger = log_manager.get_logger()
        
        start_time = time.time()
        
        for i in range(200):
            logger.info(f"Performance test {i}")
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 2.0, f"异步日志写入耗时: {elapsed_time:.2f}秒"
        
        time.sleep(1.0)
        log_manager.cleanup()
    
    def test_log_manager_cleanup(self, temp_log_dir):
        """测试LogManager清理功能"""
        LogManager._instance = None
        LogManager._initialized = False
        
        log_manager = LogManager(
            log_dir=str(temp_log_dir),
            enable_async=True
        )
        
        logger = log_manager.get_logger()
        logger.info("Before cleanup")
        
        log_manager.cleanup()
        
        assert len(log_manager.async_log_manager.async_handlers) == 0
        assert len(logger.handlers) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
