"""
录制控制器
管理录制、保存、加载和回放功能
"""

from PySide6.QtCore import QObject, Signal
from src.input_recorder import InputRecorder, RecordingManager


class RecordingController(QObject):
    """
    录制控制器类
    负责管理录制功能的所有操作
    """
    
    log_signal = Signal(str)
    state_changed_signal = Signal(bool, int)
    
    def __init__(self, recordings_dir):
        super().__init__()
        self.recorder = InputRecorder()
        self.recording_manager = RecordingManager(recordings_dir)
        self.is_recording = False
        self.is_playing = False
    
    def start_recording(self, mouse_mode='relative', min_mouse_move=3):
        """
        开始录制
        
        Args:
            mouse_mode: 鼠标模式 ('absolute' 或 'relative')
            min_mouse_move: 最小鼠标移动距离
            
        Returns:
            bool: 是否成功开始录制
        """
        if self.is_recording:
            self.log_signal.emit("录制已在进行中")
            return False
        
        self.recorder = InputRecorder(mouse_mode=mouse_mode, min_mouse_move=min_mouse_move)
        
        if self.recorder.start_recording(mouse_mode, min_mouse_move):
            self.is_recording = True
            self.log_signal.emit(f"开始录制 (模式: {'相对坐标' if mouse_mode == 'relative' else '绝对坐标'}, 最小移动: {min_mouse_move}px)")
            self.state_changed_signal.emit(True, 0)
            return True
        
        return False
    
    def stop_recording(self):
        """
        停止录制
        
        Returns:
            bool: 是否成功停止录制
        """
        if not self.is_recording:
            return False
        
        if self.recorder.stop_recording():
            self.is_recording = False
            count = self.recorder.get_action_count()
            self.log_signal.emit(f"录制完成，共记录 {count} 个操作")
            self.state_changed_signal.emit(False, count)
            return True
        
        return False
    
    def save_recording(self, name):
        """
        保存录制
        
        Args:
            name: 录制名称
            
        Returns:
            bool: 是否成功保存
        """
        if self.recorder.get_action_count() == 0:
            self.log_signal.emit("没有可保存的录制")
            return False
        
        try:
            filepath = self.recording_manager.get_recording_path(name)
            self.recorder.save_to_file(filepath)
            self.log_signal.emit(f"录制已保存到: {filepath}")
            return True
        except Exception as e:
            self.log_signal.emit(f"保存录制失败: {str(e)}")
            return False
    
    def load_recording(self, name):
        """
        加载录制
        
        Args:
            name: 录制名称
            
        Returns:
            bool: 是否成功加载
        """
        try:
            filepath = self.recording_manager.get_recording_path(name)
            if self.recorder.load_from_file(filepath):
                count = self.recorder.get_action_count()
                self.log_signal.emit(f"已加载录制: {name} ({count} 个操作)")
                self.state_changed_signal.emit(False, count)
                return True
            else:
                self.log_signal.emit(f"加载录制失败: {name}")
                return False
        except Exception as e:
            self.log_signal.emit(f"加载录制失败: {str(e)}")
            return False
    
    def play_recording(self, speed_multiplier=1.0, stop_callback=None):
        """
        回放录制
        
        Args:
            speed_multiplier: 回放速度倍数
            stop_callback: 停止回调函数
            
        Returns:
            bool: 是否成功开始回放
        """
        if self.is_playing:
            self.log_signal.emit("回放已在进行中")
            return False
        
        if self.recorder.get_action_count() == 0:
            self.log_signal.emit("没有可回放的录制")
            return False
        
        try:
            if self.recorder.play_recording(speed_multiplier, stop_callback):
                self.is_playing = True
                self.log_signal.emit(f"开始回放录制 (速度: {speed_multiplier}x)")
                return True
            else:
                self.log_signal.emit("回放录制失败")
                return False
        except Exception as e:
            self.log_signal.emit(f"回放录制失败: {str(e)}")
            return False
    
    def stop_playback(self):
        """
        停止回放
        
        Returns:
            bool: 是否成功停止
        """
        if not self.is_playing:
            return False
        
        try:
            self.recorder.stop_playback()
            self.is_playing = False
            self.log_signal.emit("已停止回放")
            return True
        except Exception as e:
            self.log_signal.emit(f"停止回放失败: {str(e)}")
            return False
    
    def get_action_count(self):
        """
        获取当前录制的操作数量
        
        Returns:
            int: 操作数量
        """
        return self.recorder.get_action_count()
    
    def list_recordings(self):
        """
        列出所有可用的录制
        
        Returns:
            list: 录制名称列表
        """
        return self.recording_manager.list_recordings()
    
    def delete_recording(self, name):
        """
        删除录制
        
        Args:
            name: 录制名称
            
        Returns:
            bool: 是否成功删除
        """
        try:
            if self.recording_manager.delete_recording(name):
                self.log_signal.emit(f"已删除录制: {name}")
                return True
            else:
                self.log_signal.emit(f"删除录制失败: {name}")
                return False
        except Exception as e:
            self.log_signal.emit(f"删除录制失败: {str(e)}")
            return False
    
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
