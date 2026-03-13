"""
异步日志处理器模块
提供高性能的异步日志写入功能，减少I/O阻塞
"""

import logging
import queue
import threading
import time
import os
from typing import List, Tuple, Optional
from logging.handlers import RotatingFileHandler
from pathlib import Path


class AsyncLogHandler(logging.Handler):
    """
    异步日志处理器
    
    使用队列和工作线程实现异步日志写入，减少I/O阻塞对主线程的影响
    支持批量写入以进一步减少I/O操作次数
    """
    
    def __init__(self, base_handler: logging.Handler, batch_size: int = 10, flush_interval: float = 1.0):
        """
        初始化异步日志处理器
        
        Args:
            base_handler: 底层日志处理器（如RotatingFileHandler）
            batch_size: 批量写入的日志条数，默认10条
            flush_interval: 强制刷新间隔（秒），默认1秒
        """
        super().__init__()
        self.base_handler = base_handler
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        self.log_queue = queue.Queue(maxsize=10000)
        self.worker_thread = None
        self._stop_event = threading.Event()
        self._last_flush_time = time.time()
        
        # 确保日志目录存在
        if hasattr(base_handler, 'baseFilename'):
            log_file = Path(base_handler.baseFilename)
            log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._start_worker()
    
    def _start_worker(self):
        """启动工作线程"""
        self.worker_thread = threading.Thread(
            target=self._process_logs,
            name="AsyncLogWorker",
            daemon=False  # 改为非守护线程，确保日志写入完成
        )
        self.worker_thread.start()
    
    def _process_logs(self):
        """
        工作线程处理日志队列
        
        从队列中取出日志记录，批量写入底层处理器
        """
        batch: List[logging.LogRecord] = []
        
        while not self._stop_event.is_set():
            try:
                record = self.log_queue.get(timeout=0.1)
                batch.append(record)
                
                current_time = time.time()
                should_flush = (
                    len(batch) >= self.batch_size or
                    (current_time - self._last_flush_time) >= self.flush_interval
                )
                
                if should_flush and batch:
                    self._flush_batch(batch)
                    batch = []
                    self._last_flush_time = current_time
                    
            except queue.Empty:
                if batch and (time.time() - self._last_flush_time) >= self.flush_interval:
                    self._flush_batch(batch)
                    batch = []
                    self._last_flush_time = time.time()
                continue
            except Exception as e:
                print(f"异步日志处理器错误: {e}")
                if batch:
                    self._flush_batch(batch)
                    batch = []
        
        if batch:
            self._flush_batch(batch)
    
    def _flush_batch(self, batch: List[logging.LogRecord]):
        """
        批量写入日志记录
        
        Args:
            batch: 日志记录列表
        """
        for record in batch:
            try:
                self.base_handler.emit(record)
            except Exception as e:
                print(f"写入日志失败: {e}")
    
    def emit(self, record: logging.LogRecord):
        """
        发送日志记录到队列
        
        Args:
            record: 日志记录对象
        """
        try:
            self.log_queue.put_nowait(record)
        except queue.Full:
            print("警告: 日志队列已满，丢弃日志")
    
    def close(self):
        """
        关闭异步日志处理器
        
        停止工作线程，刷新剩余日志，关闭底层处理器
        """
        self._stop_event.set()
        
        if self.worker_thread and self.worker_thread.is_alive():
            # 等待工作线程完成
            self.worker_thread.join(timeout=5.0)
        
        self.base_handler.close()
        super().close()
    
    def flush(self):
        """强制刷新所有待处理的日志"""
        while not self.log_queue.empty():
            try:
                record = self.log_queue.get_nowait()
                self.base_handler.emit(record)
            except queue.Empty:
                break
        self.base_handler.flush()
    
    def limit_log_files(self, max_files: int = 10):
        """
        限制日志文件数量
        
        Args:
            max_files: 保留的最大日志文件数量，默认10
        """
        if not hasattr(self.base_handler, 'baseFilename'):
            return
        
        log_file = Path(self.base_handler.baseFilename)
        log_dir = log_file.parent
        log_prefix = log_file.stem
        
        # 获取所有匹配的日志文件
        log_files = []
        for file in log_dir.glob(f"{log_prefix}*"):
            if file.is_file():
                log_files.append(file)
        
        # 按修改时间排序，删除最旧的文件
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if len(log_files) > max_files:
            for old_file in log_files[max_files:]:
                try:
                    old_file.unlink()
                except Exception as e:
                    print(f"删除旧日志文件失败: {old_file}, 错误: {e}")


class AsyncLogManager:
    """
    异步日志管理器
    
    管理异步日志处理器的创建和生命周期
    """
    
    def __init__(self, log_dir: Path, batch_size: int = 10, flush_interval: float = 1.0, max_log_files: int = 10):
        """
        初始化异步日志管理器
        
        Args:
            log_dir: 日志文件目录
            batch_size: 批量写入的日志条数
            flush_interval: 强制刷新间隔（秒）
            max_log_files: 保留的最大日志文件数量，默认10
        """
        self.log_dir = log_dir
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_log_files = max_log_files
        self.async_handlers: List[AsyncLogHandler] = []
    
    def create_async_file_handler(
        self,
        filename: str,
        level: int = logging.DEBUG,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5
    ) -> AsyncLogHandler:
        """
        创建异步文件日志处理器
        
        Args:
            filename: 日志文件名
            level: 日志级别
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的备份文件数量
            
        Returns:
            AsyncLogHandler: 异步日志处理器实例
        """
        base_handler = RotatingFileHandler(
            self.log_dir / filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        base_handler.setLevel(level)
        
        async_handler = AsyncLogHandler(
            base_handler,
            batch_size=self.batch_size,
            flush_interval=self.flush_interval
        )
        async_handler.setLevel(level)
        
        self.async_handlers.append(async_handler)
        return async_handler
    
    def cleanup(self):
        """清理所有异步日志处理器"""
        for handler in self.async_handlers:
            handler.close()
        self.async_handlers.clear()
