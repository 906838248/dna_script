"""
日志管理模块
提供专业的日志记录功能，包括文件持久化、日志轮转和UI集成
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, Signal


class SignalLogHandler(logging.Handler, QObject):
    """
    自定义日志处理器，将日志消息发送到Qt信号
    """
    
    log_signal = Signal(str)
    
    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)
    
    def emit(self, record):
        """
        发送日志记录到信号
        
        Args:
            record: 日志记录对象
        """
        try:
            msg = self.format(record)
            self.log_signal.emit(msg)
        except Exception:
            self.handleError(record)


class LogManager:
    """日志管理器类"""
    
    _instance: Optional['LogManager'] = None
    _initialized: bool = False
    
    def __new__(cls, *args, **kwargs):
        """
        单例模式，确保全局只有一个日志管理器实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir: str = None, log_level: int = logging.DEBUG):
        """
        初始化日志管理器
        
        Args:
            log_dir: 日志文件目录，默认为项目根目录下的 logs 文件夹
            log_level: 日志级别，默认为 DEBUG
        """
        if self._initialized:
            return
        
        if log_dir is None:
            self.log_dir = Path(__file__).parent.parent / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        self.log_level = log_level
        self.logger = logging.getLogger('dna_script')
        self.logger.setLevel(log_level)
        
        # 初始化信号处理器属性
        self.signal_handler = None
        
        # 防止重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()
        
        self._initialized = True
    
    def _setup_handlers(self):
        """
        设置日志处理器
        """
        # 确保日志目录存在
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件处理器（带轮转）
        file_handler = RotatingFileHandler(
            self.log_dir / 'dna_script.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.name = 'file_handler'
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.name = 'console_handler'
        
        # UI信号处理器
        self.signal_handler = SignalLogHandler()
        self.signal_handler.setLevel(logging.INFO)
        self.signal_handler.name = 'signal_handler'
        
        # 格式化器
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        signal_formatter = logging.Formatter(
            '%(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        self.signal_handler.setFormatter(signal_formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(self.signal_handler)
    
    def get_logger(self) -> logging.Logger:
        """
        获取日志记录器
        
        Returns:
            logging.Logger: 日志记录器实例
        """
        return self.logger
    
    def get_signal_handler(self) -> SignalLogHandler:
        """
        获取信号处理器，用于连接UI
        
        Returns:
            SignalLogHandler: 信号处理器实例
        """
        return self.signal_handler
    
    def set_level(self, level: int):
        """
        设置日志级别
        
        Args:
            level: 日志级别（logging.DEBUG, INFO, WARNING, ERROR, CRITICAL）
        """
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            if handler.name == 'console_handler':
                handler.setLevel(level)
            elif handler.name == 'signal_handler':
                handler.setLevel(level)
    
    def add_log_file(self, filename: str, level: int = logging.DEBUG, max_bytes: int = 10*1024*1024, backup_count: int = 5):
        """
        添加额外的日志文件处理器
        
        Args:
            filename: 日志文件名
            level: 日志级别
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的备份文件数量
        """
        file_handler = RotatingFileHandler(
            self.log_dir / filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.name = f'file_handler_{filename}'
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def remove_handler(self, handler_name: str):
        """
        移除指定的日志处理器
        
        Args:
            handler_name: 处理器名称
        """
        for handler in self.logger.handlers[:]:
            if handler.name == handler_name:
                self.logger.removeHandler(handler)
                handler.close()
    
    def clear_handlers(self):
        """
        清除所有日志处理器
        """
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            handler.close()
    
    def log(self, level: int, message: str):
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        self.logger.log(level, message)
    
    def debug(self, message: str):
        """
        记录DEBUG级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.debug(message)
    
    def info(self, message: str):
        """
        记录INFO级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.info(message)
    
    def warning(self, message: str):
        """
        记录WARNING级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.warning(message)
    
    def error(self, message: str):
        """
        记录ERROR级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.error(message)
    
    def critical(self, message: str):
        """
        记录CRITICAL级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.critical(message)
    
    def exception(self, message: str):
        """
        记录异常日志（包含堆栈跟踪）
        
        Args:
            message: 日志消息
        """
        self.logger.exception(message)


# 全局日志管理器实例
log_manager = LogManager()
