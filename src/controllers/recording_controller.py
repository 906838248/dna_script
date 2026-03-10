"""
录制控制器
管理录制、保存、加载和回放功能
增强错误处理和异常管理
使用任务执行器确保耗时操作在工作线程中执行
"""

import os
import json
from PySide6.QtCore import QObject, Signal
from typing import Optional, List
from src.input_recorder import InputRecorder, RecordingManager
from src.task_executor import TaskExecutor


class RecordingError(Exception):
    """
    录制错误基类
    """
    pass


class RecordingAlreadyActiveError(RecordingError):
    """
    录制已在进行中错误
    """
    pass


class PlaybackAlreadyActiveError(RecordingError):
    """
    回放已在进行中错误
    """
    pass


class InvalidParameterError(RecordingError):
    """
    参数无效错误
    """
    pass


class RecordingNotFoundError(RecordingError):
    """
    录制未找到错误
    """
    pass


class RecordingSaveError(RecordingError):
    """
    录制保存错误
    """
    pass


class RecordingLoadError(RecordingError):
    """
    录制加载错误
    """
    pass


class RecordingPlaybackError(RecordingError):
    """
    录制回放错误
    """
    pass


class RecordingDeleteError(RecordingError):
    """
    录制删除错误
    """
    pass


class RecordingController(QObject):
    """
    录制控制器类
    负责管理录制功能的所有操作
    提供完善的错误处理和异常管理
    """
    
    log_signal = Signal(str)
    state_changed_signal = Signal(bool, int)
    error_signal = Signal(str, str)
    
    def __init__(self, recordings_dir):
        """
        初始化录制控制器
        
        Args:
            recordings_dir: 录制文件存储目录
        """
        super().__init__()
        self.recorder = InputRecorder()
        self.recording_manager = RecordingManager(recordings_dir)
        self.is_recording = False
        self.is_playing = False
        self.last_error = None
        self.task_executor = TaskExecutor()
        self.task_executor.task_finished.connect(self._on_task_finished)
        self.task_executor.task_error.connect(self._on_task_error)
    
    def start_recording(self, mouse_mode='relative', min_mouse_move=3):
        """
        开始录制
        
        Args:
            mouse_mode: 鼠标模式 ('absolute' 或 'relative')
            min_mouse_move: 最小鼠标移动距离
            
        Returns:
            bool: 是否成功开始录制
            
        Raises:
            RecordingAlreadyActiveError: 录制已在进行中
            InvalidParameterError: 参数无效
            RecordingError: 录制启动失败
        """
        if self.is_recording:
            error_msg = "录制已在进行中"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("RecordingAlreadyActiveError", error_msg)
            raise RecordingAlreadyActiveError(error_msg)
        
        if mouse_mode not in ['absolute', 'relative']:
            error_msg = f"无效的鼠标模式: {mouse_mode}，必须是 'absolute' 或 'relative'"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("InvalidParameterError", error_msg)
            raise InvalidParameterError(error_msg)
        
        if not isinstance(min_mouse_move, int) or min_mouse_move < 1 or min_mouse_move > 1000:
            error_msg = f"无效的最小移动距离: {min_mouse_move}，必须是1-1000之间的整数"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("InvalidParameterError", error_msg)
            raise InvalidParameterError(error_msg)
        
        try:
            self.recorder = InputRecorder(mouse_mode=mouse_mode, min_mouse_move=min_mouse_move)
            
            if self.recorder.start_recording(mouse_mode, min_mouse_move):
                self.is_recording = True
                self.last_error = None
                mode_text = "相对坐标" if mouse_mode == 'relative' else "绝对坐标"
                self.log_signal.emit(f"开始录制 (模式: {mode_text}, 最小移动: {min_mouse_move}px)")
                self.state_changed_signal.emit(True, 0)
                return True
            else:
                error_msg = "录制启动失败"
                self.log_signal.emit(error_msg)
                self.error_signal.emit("RecordingError", error_msg)
                raise RecordingError(error_msg)
                
        except (RecordingAlreadyActiveError, InvalidParameterError):
            raise
        except Exception as e:
            error_msg = f"启动录制时发生错误: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("UnknownError", error_msg)
            raise RecordingError(error_msg) from e
    
    def stop_recording(self):
        """
        停止录制
        
        Returns:
            bool: 是否成功停止录制
            
        Raises:
            RecordingError: 停止录制失败
        """
        if not self.is_recording:
            error_msg = "没有正在进行的录制"
            self.log_signal.emit(error_msg)
            return False
        
        try:
            if self.recorder.stop_recording():
                self.is_recording = False
                count = self.recorder.get_action_count()
                self.log_signal.emit(f"录制完成，共记录 {count} 个操作")
                self.state_changed_signal.emit(False, count)
                return True
            else:
                error_msg = "停止录制失败"
                self.log_signal.emit(error_msg)
                self.error_signal.emit("RecordingError", error_msg)
                raise RecordingError(error_msg)
                
        except Exception as e:
            error_msg = f"停止录制时发生错误: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("UnknownError", error_msg)
            self.is_recording = False
            raise RecordingError(error_msg) from e
    
    def save_recording(self, name):
        """
        保存录制
        
        Args:
            name: 录制名称
            
        Returns:
            bool: 是否成功保存
            
        Raises:
            InvalidParameterError: 录制名称无效
            RecordingSaveError: 保存失败
        """
        if not name or not isinstance(name, str) or not name.strip():
            error_msg = "录制名称不能为空"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("InvalidParameterError", error_msg)
            raise InvalidParameterError(error_msg)
        
        name = name.strip()
        
        if self.recorder.get_action_count() == 0:
            error_msg = "没有可保存的录制"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("RecordingSaveError", error_msg)
            raise RecordingSaveError(error_msg)
        
        def save_task():
            filepath = self.recording_manager.get_recording_path(name)
            
            if not os.path.exists(os.path.dirname(filepath)):
                error_msg = f"录制目录不存在: {os.path.dirname(filepath)}"
                raise RecordingSaveError(error_msg)
            
            self.recorder.save_to_file(filepath)
            return filepath
        
        if not self.task_executor.execute_task(save_task):
            error_msg = "任务执行器忙碌，无法保存录制"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("TaskExecutorError", error_msg)
            raise RecordingSaveError(error_msg)
        
        return True
    
    def load_recording(self, name):
        """
        加载录制
        
        Args:
            name: 录制名称
            
        Returns:
            bool: 是否成功加载
            
        Raises:
            InvalidParameterError: 录制名称无效
            RecordingNotFoundError: 录制未找到
            RecordingLoadError: 加载失败
        """
        if not name or not isinstance(name, str) or not name.strip():
            error_msg = "录制名称不能为空"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("InvalidParameterError", error_msg)
            raise InvalidParameterError(error_msg)
        
        name = name.strip()
        
        def load_task():
            filepath = self.recording_manager.get_recording_path(name)
            
            if not os.path.exists(filepath):
                error_msg = f"录制文件不存在: {filepath}"
                raise RecordingNotFoundError(error_msg)
            
            if not filepath.endswith('.json'):
                error_msg = f"无效的录制文件格式: {filepath}"
                raise RecordingLoadError(error_msg)
            
            if self.recorder.load_from_file(filepath):
                count = self.recorder.get_action_count()
                return count
            else:
                error_msg = f"加载录制失败: {name}"
                raise RecordingLoadError(error_msg)
        
        if not self.task_executor.execute_task(load_task):
            error_msg = "任务执行器忙碌，无法加载录制"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("TaskExecutorError", error_msg)
            raise RecordingLoadError(error_msg)
        
        return True
    
    def play_recording(self, speed_multiplier=1.0, stop_callback=None):
        """
        回放录制
        
        Args:
            speed_multiplier: 回放速度倍数
            stop_callback: 停止回调函数
            
        Returns:
            bool: 是否成功开始回放
            
        Raises:
            PlaybackAlreadyActiveError: 回放已在进行中
            InvalidParameterError: 参数无效
            RecordingPlaybackError: 回放失败
        """
        if self.is_playing:
            error_msg = "回放已在进行中"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("PlaybackAlreadyActiveError", error_msg)
            raise PlaybackAlreadyActiveError(error_msg)
        
        if not isinstance(speed_multiplier, (int, float)) or speed_multiplier <= 0:
            error_msg = f"无效的回放速度: {speed_multiplier}，必须为正数"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("InvalidParameterError", error_msg)
            raise InvalidParameterError(error_msg)
        
        if self.recorder.get_action_count() == 0:
            error_msg = "没有可回放的录制"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("RecordingPlaybackError", error_msg)
            raise RecordingPlaybackError(error_msg)
        
        try:
            if self.recorder.play_recording(speed_multiplier, stop_callback):
                self.is_playing = True
                self.last_error = None
                self.log_signal.emit(f"开始回放录制 (速度: {speed_multiplier}x)")
                return True
            else:
                error_msg = "回放录制失败"
                self.log_signal.emit(error_msg)
                self.error_signal.emit("RecordingPlaybackError", error_msg)
                raise RecordingPlaybackError(error_msg)
                
        except (PlaybackAlreadyActiveError, InvalidParameterError, RecordingPlaybackError):
            raise
        except Exception as e:
            error_msg = f"回放录制时发生未知错误: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("UnknownError", error_msg)
            self.is_playing = False
            raise RecordingPlaybackError(error_msg) from e
    
    def stop_playback(self):
        """
        停止回放
        
        Returns:
            bool: 是否成功停止
            
        Raises:
            RecordingError: 停止回放失败
        """
        if not self.is_playing:
            error_msg = "没有正在进行的回放"
            self.log_signal.emit(error_msg)
            return False
        
        try:
            self.recorder.stop_playback()
            self.is_playing = False
            self.log_signal.emit("已停止回放")
            return True
            
        except Exception as e:
            error_msg = f"停止回放时发生错误: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("UnknownError", error_msg)
            self.is_playing = False
            raise RecordingError(error_msg) from e
    
    def get_action_count(self):
        """
        获取当前录制的操作数量
        
        Returns:
            int: 操作数量
        """
        try:
            return self.recorder.get_action_count()
        except Exception as e:
            self.log_signal.emit(f"获取操作数量时发生错误: {str(e)}")
            return 0
    
    def list_recordings(self):
        """
        列出所有可用的录制
        
        Returns:
            list: 录制名称列表
        """
        try:
            recordings = self.recording_manager.list_recordings()
            if not recordings:
                self.log_signal.emit("没有可用的录制")
            else:
                self.log_signal.emit(f"找到 {len(recordings)} 个录制")
            return recordings
        except Exception as e:
            error_msg = f"列出录制时发生错误: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("UnknownError", error_msg)
            return []
    
    def delete_recording(self, name):
        """
        删除录制
        
        Args:
            name: 录制名称
            
        Returns:
            bool: 是否成功删除
            
        Raises:
            InvalidParameterError: 录制名称无效
            RecordingNotFoundError: 录制未找到
            RecordingDeleteError: 删除失败
        """
        if not name or not isinstance(name, str) or not name.strip():
            error_msg = "录制名称不能为空"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("InvalidParameterError", error_msg)
            raise InvalidParameterError(error_msg)
        
        name = name.strip()
        
        try:
            filepath = self.recording_manager.get_recording_path(name)
            
            if not os.path.exists(filepath):
                error_msg = f"录制文件不存在: {filepath}"
                self.log_signal.emit(error_msg)
                self.error_signal.emit("RecordingNotFoundError", error_msg)
                raise RecordingNotFoundError(error_msg)
            
            if self.recording_manager.delete_recording(name):
                self.log_signal.emit(f"已删除录制: {name}")
                return True
            else:
                error_msg = f"删除录制失败: {name}"
                self.log_signal.emit(error_msg)
                self.error_signal.emit("RecordingDeleteError", error_msg)
                raise RecordingDeleteError(error_msg)
                
        except (InvalidParameterError, RecordingNotFoundError, RecordingDeleteError):
            raise
        except PermissionError as e:
            error_msg = f"没有删除权限: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("PermissionError", error_msg)
            raise RecordingDeleteError(error_msg) from e
        except OSError as e:
            error_msg = f"文件系统错误: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("OSError", error_msg)
            raise RecordingDeleteError(error_msg) from e
        except Exception as e:
            error_msg = f"删除录制时发生未知错误: {str(e)}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit("UnknownError", error_msg)
            raise RecordingDeleteError(error_msg) from e
    
    def is_recording_active(self):
        """
        检查是否正在录制
        
        Returns:
            bool: 是否正在录制
        """
        return self.is_recording
    
    def is_playback_active(self):
        """
        检查是否正在回放
        
        Returns:
            bool: 是否正在回放
        """
        return self.is_playing
    
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
        try:
            if self.is_recording_active():
                try:
                    self.stop_recording()
                except Exception as e:
                    self.log_signal.emit(f"清理录制时发生错误: {str(e)}")
            
            if self.is_playback_active():
                try:
                    self.stop_playback()
                except Exception as e:
                    self.log_signal.emit(f"清理回放时发生错误: {str(e)}")
            
            self.task_executor.cleanup()
        except Exception as e:
            self.log_signal.emit(f"清理资源时发生错误: {str(e)}")
    
    def _on_task_finished(self, result):
        """
        任务完成时的回调
        
        Args:
            result: 任务结果
        """
        if isinstance(result, str) and result.endswith('.json'):
            self.log_signal.emit(f"录制已保存到: {result}")
        elif isinstance(result, int):
            self.log_signal.emit(f"已加载录制 ({result} 个操作)")
            self.state_changed_signal.emit(False, result)
        else:
            self.log_signal.emit(f"任务完成: {result}")
    
    def _on_task_error(self, error_type: str, error_msg: str):
        """
        任务出错时的回调
        
        Args:
            error_type: 错误类型
            error_msg: 错误消息
        """
        self.last_error = f"{error_type}: {error_msg}"
        self.log_signal.emit(f"任务错误 [{error_type}]: {error_msg}")
        self.error_signal.emit(error_type, error_msg)
