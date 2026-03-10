"""
录制控制器单元测试
测试增强的错误处理功能
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import QObject, Signal, QEventLoop, QCoreApplication, QTimer
from src.controllers.recording_controller import (
    RecordingController,
    RecordingError,
    RecordingAlreadyActiveError,
    PlaybackAlreadyActiveError,
    InvalidParameterError,
    RecordingNotFoundError,
    RecordingSaveError,
    RecordingLoadError,
    RecordingPlaybackError,
    RecordingDeleteError
)


class MockInputRecorder:
    """模拟输入录制器类"""
    def __init__(self, mouse_mode='relative', min_mouse_move=3):
        self.mouse_mode = mouse_mode
        self.min_mouse_move = min_mouse_move
        self.log_signal = Mock()
        self._recording = False
        self._actions = []
    
    def start_recording(self, mouse_mode, min_mouse_move):
        """开始录制"""
        self._recording = True
        return True
    
    def stop_recording(self):
        """停止录制"""
        self._recording = False
        return True
    
    def get_action_count(self):
        """获取操作数量"""
        return len(self._actions)
    
    def save_to_file(self, filepath):
        """保存到文件"""
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            raise RecordingSaveError(f"录制目录不存在: {dirpath}")
        return True
    
    def load_from_file(self, filepath):
        """从文件加载"""
        if not os.path.exists(filepath):
            raise RecordingNotFoundError(f"录制文件不存在: {filepath}")
        self._actions = [1, 2, 3]
        return True
    
    def play_recording(self, speed_multiplier, stop_callback):
        """回放录制"""
        return True
    
    def stop_playback(self):
        """停止回放"""
        return True


class MockRecordingManager:
    """模拟录制管理器类"""
    def __init__(self, recordings_dir):
        self.recordings_dir = recordings_dir
        self._recordings = []
    
    def get_recording_path(self, name):
        """获取录制文件路径"""
        return os.path.join(self.recordings_dir, f"{name}.json")
    
    def list_recordings(self):
        """列出所有录制"""
        return list(self._recordings)
    
    def delete_recording(self, name):
        """删除录制"""
        if name in self._recordings:
            self._recordings.remove(name)
            return True
        return False


class TestRecordingController:
    """录制控制器测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def controller(self, temp_dir):
        """创建控制器实例"""
        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication([])
        
        controller = RecordingController(temp_dir)
        controller.recorder = MockInputRecorder()
        controller.recording_manager = MockRecordingManager(temp_dir)
        return controller
    
    def test_start_recording_when_already_recording(self, controller):
        """测试当录制已在进行中时开始录制"""
        controller.is_recording = True
        
        with pytest.raises(RecordingAlreadyActiveError) as exc_info:
            controller.start_recording()
        
        assert "录制已在进行中" in str(exc_info.value)
    
    def test_start_recording_with_invalid_mouse_mode(self, controller):
        """测试使用无效鼠标模式开始录制"""
        with pytest.raises(InvalidParameterError) as exc_info:
            controller.start_recording(mouse_mode='invalid')
        
        assert "无效的鼠标模式" in str(exc_info.value)
    
    def test_start_recording_with_invalid_min_mouse_move(self, controller):
        """测试使用无效最小移动距离开始录制"""
        with pytest.raises(InvalidParameterError) as exc_info:
            controller.start_recording(min_mouse_move=0)
        
        assert "无效的最小移动距离" in str(exc_info.value)
    
    def test_start_recording_with_string_min_mouse_move(self, controller):
        """测试使用字符串最小移动距离开始录制"""
        with pytest.raises(InvalidParameterError) as exc_info:
            controller.start_recording(min_mouse_move='invalid')
        
        assert "无效的最小移动距离" in str(exc_info.value)
    
    def test_start_recording_success(self, controller):
        """测试成功开始录制"""
        result = controller.start_recording(mouse_mode='relative', min_mouse_move=5)
        
        assert result is True
        assert controller.is_recording is True
    
    def test_stop_recording_when_not_recording(self, controller):
        """测试当未录制时停止录制"""
        result = controller.stop_recording()
        
        assert result is False
    
    def test_stop_recording_success(self, controller):
        """测试成功停止录制"""
        controller.start_recording()
        controller.recorder._actions = [1, 2, 3]
        
        result = controller.stop_recording()
        
        assert result is True
        assert controller.is_recording is False
    
    def test_save_recording_with_empty_name(self, controller):
        """测试使用空名称保存录制"""
        with pytest.raises(InvalidParameterError) as exc_info:
            controller.save_recording("")
        
        assert "录制名称不能为空" in str(exc_info.value)
    
    def test_save_recording_with_whitespace_name(self, controller):
        """测试使用空白字符名称保存录制"""
        with pytest.raises(InvalidParameterError) as exc_info:
            controller.save_recording("   ")
        
        assert "录制名称不能为空" in str(exc_info.value)
    
    def test_save_recording_with_no_actions(self, controller):
        """测试在没有操作时保存录制"""
        with pytest.raises(RecordingSaveError) as exc_info:
            controller.save_recording("test")
        
        assert "没有可保存的录制" in str(exc_info.value)
    
    def test_save_recording_with_nonexistent_directory(self, controller):
        """测试保存录制到不存在的目录"""
        controller.recorder._actions = [1, 2, 3]
        controller.recording_manager.recordings_dir = "/nonexistent/directory"
        
        error_received = []
        controller.error_signal.connect(lambda error_type, error_msg: error_received.append((error_type, error_msg)))
        
        controller.save_recording("test")
        
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(5000)
        
        def check_error():
            if error_received:
                loop.quit()
        
        controller.error_signal.connect(check_error)
        
        loop.exec()
        
        print(f"收到的错误: {error_received}")
        
        assert len(error_received) > 0, "应该收到错误信号"
        error_type, error_msg = error_received[0]
        assert "RecordingSaveError" in error_type or "TaskExecutorError" in error_type
    
    def test_save_recording_success(self, controller, temp_dir):
        """测试成功保存录制"""
        controller.recorder._actions = [1, 2, 3]
        
        result = controller.save_recording("test_recording")
        
        assert result is True
    
    def test_load_recording_with_empty_name(self, controller):
        """测试使用空名称加载录制"""
        with pytest.raises(InvalidParameterError) as exc_info:
            controller.load_recording("")
        
        assert "录制名称不能为空" in str(exc_info.value)
    
    def test_load_recording_with_nonexistent_file(self, controller):
        """测试加载不存在的录制"""
        error_received = []
        controller.error_signal.connect(lambda error_type, error_msg: error_received.append((error_type, error_msg)))
        
        controller.load_recording("nonexistent")
        
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(5000)
        
        def check_error():
            if error_received:
                loop.quit()
        
        controller.error_signal.connect(check_error)
        
        loop.exec()
        
        print(f"收到的错误: {error_received}")
        
        assert len(error_received) > 0, "应该收到错误信号"
        error_type, error_msg = error_received[0]
        assert "RecordingNotFoundError" in error_type or "RecordingLoadError" in error_type
    
    def test_load_recording_success(self, controller, temp_dir):
        """测试成功加载录制"""
        filepath = os.path.join(temp_dir, "test.json")
        with open(filepath, 'w') as f:
            f.write('{"actions": []}')
        
        result = controller.load_recording("test")
        
        assert result is True
    
    def test_play_recording_when_already_playing(self, controller):
        """测试当回放已在进行中时回放录制"""
        controller.is_playing = True
        controller.recorder._actions = [1, 2, 3]
        
        with pytest.raises(PlaybackAlreadyActiveError) as exc_info:
            controller.play_recording()
        
        assert "回放已在进行中" in str(exc_info.value)
    
    def test_play_recording_with_invalid_speed(self, controller):
        """测试使用无效速度回放录制"""
        controller.recorder._actions = [1, 2, 3]
        
        with pytest.raises(InvalidParameterError) as exc_info:
            controller.play_recording(speed_multiplier=0)
        
        assert "无效的回放速度" in str(exc_info.value)
    
    def test_play_recording_with_negative_speed(self, controller):
        """测试使用负速度回放录制"""
        controller.recorder._actions = [1, 2, 3]
        
        with pytest.raises(InvalidParameterError) as exc_info:
            controller.play_recording(speed_multiplier=-1)
        
        assert "无效的回放速度" in str(exc_info.value)
    
    def test_play_recording_with_no_actions(self, controller):
        """测试在没有操作时回放录制"""
        with pytest.raises(RecordingPlaybackError) as exc_info:
            controller.play_recording()
        
        assert "没有可回放的录制" in str(exc_info.value)
    
    def test_play_recording_success(self, controller):
        """测试成功回放录制"""
        controller.recorder._actions = [1, 2, 3]
        
        result = controller.play_recording(speed_multiplier=1.5)
        
        assert result is True
        assert controller.is_playing is True
    
    def test_stop_playback_when_not_playing(self, controller):
        """测试当未回放时停止回放"""
        result = controller.stop_playback()
        
        assert result is False
    
    def test_stop_playback_success(self, controller):
        """测试成功停止回放"""
        controller.recorder._actions = [1, 2, 3]
        controller.play_recording()
        
        result = controller.stop_playback()
        
        assert result is True
        assert controller.is_playing is False
    
    def test_get_action_count(self, controller):
        """测试获取操作数量"""
        controller.recorder._actions = [1, 2, 3, 4, 5]
        
        count = controller.get_action_count()
        
        assert count == 5
    
    def test_list_recordings_empty(self, controller):
        """测试列出空录制列表"""
        recordings = controller.list_recordings()
        
        assert recordings == []
    
    def test_list_recordings_with_items(self, controller):
        """测试列出有项目的录制列表"""
        controller.recording_manager._recordings = ["rec1", "rec2", "rec3"]
        
        recordings = controller.list_recordings()
        
        assert recordings == ["rec1", "rec2", "rec3"]
    
    def test_delete_recording_with_empty_name(self, controller):
        """测试使用空名称删除录制"""
        with pytest.raises(InvalidParameterError) as exc_info:
            controller.delete_recording("")
        
        assert "录制名称不能为空" in str(exc_info.value)
    
    def test_delete_recording_with_nonexistent_file(self, controller):
        """测试删除不存在的录制"""
        with pytest.raises(RecordingNotFoundError) as exc_info:
            controller.delete_recording("nonexistent")
        
        assert "录制文件不存在" in str(exc_info.value)
    
    def test_delete_recording_success(self, controller, temp_dir):
        """测试成功删除录制"""
        controller.recording_manager._recordings.append("test")
        filepath = os.path.join(temp_dir, "test.json")
        with open(filepath, 'w') as f:
            f.write('{"actions": []}')
        
        result = controller.delete_recording("test")
        
        assert result is True
    
    def test_is_recording_active(self, controller):
        """测试检查是否正在录制"""
        assert controller.is_recording_active() is False
        
        controller.is_recording = True
        
        assert controller.is_recording_active() is True
    
    def test_is_playback_active(self, controller):
        """测试检查是否正在回放"""
        assert controller.is_playback_active() is False
        
        controller.is_playing = True
        
        assert controller.is_playback_active() is True
    
    def test_get_last_error(self, controller):
        """测试获取最后一次错误"""
        assert controller.get_last_error() is None
        
        controller.last_error = "测试错误"
        
        assert controller.get_last_error() == "测试错误"
    
    def test_cleanup_when_recording(self, controller):
        """测试清理资源时正在录制"""
        controller.start_recording()
        
        controller.cleanup()
        
        assert controller.is_recording is False
    
    def test_cleanup_when_playing(self, controller):
        """测试清理资源时正在回放"""
        controller.recorder._actions = [1, 2, 3]
        controller.play_recording()
        
        controller.cleanup()
        
        assert controller.is_playing is False
    
    def test_error_signal_emission(self, controller):
        """测试错误信号发射"""
        error_received = []
        
        def on_error(error_type, error_message):
            error_received.append((error_type, error_message))
        
        controller.error_signal.connect(on_error)
        
        try:
            controller.start_recording(mouse_mode='invalid')
        except InvalidParameterError:
            pass
        
        assert len(error_received) == 1
        assert error_received[0][0] == "InvalidParameterError"
        assert "无效的鼠标模式" in error_received[0][1]
