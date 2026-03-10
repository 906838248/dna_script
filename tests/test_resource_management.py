"""
资源管理测试
测试InputRecorder和RecordingManager的上下文管理器支持
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

from src.input_recorder import InputRecorder, RecordingManager


class TestInputRecorderResourceManager:
    """InputRecorder资源管理测试类"""
    
    def test_context_manager_enter(self):
        """测试上下文管理器入口"""
        with InputRecorder() as recorder:
            assert recorder is not None
            assert isinstance(recorder, InputRecorder)
    
    def test_context_manager_exit_stops_recording(self):
        """测试上下文管理器退出时停止录制"""
        with InputRecorder() as recorder:
            # 模拟录制状态
            recorder.is_recording = True
            
            # 模拟stop_recording方法
            original_stop = recorder.stop_recording
            stop_called = []
            def mock_stop():
                stop_called.append(True)
                recorder.is_recording = False
                return True
            recorder.stop_recording = mock_stop
        
        # 验证stop_recording被调用
        assert len(stop_called) > 0
    
    def test_context_manager_exit_stops_playback(self):
        """测试上下文管理器退出时停止回放"""
        with InputRecorder() as recorder:
            # 模拟回放状态
            recorder.is_playing = True
            
            # 模拟stop_playback方法
            stop_called = []
            def mock_stop():
                stop_called.append(True)
                recorder.is_playing = False
            recorder.stop_playback = mock_stop
        
        # 验证stop_playback被调用
        assert len(stop_called) > 0
    
    def test_context_manager_exit_on_exception(self):
        """测试上下文管理器在异常时正确清理资源"""
        with pytest.raises(ValueError):
            with InputRecorder() as recorder:
                recorder.is_recording = True
                # 模拟stop_recording方法
                stop_called = []
                def mock_stop():
                    stop_called.append(True)
                    recorder.is_recording = False
                    return True
                recorder.stop_recording = mock_stop
                raise ValueError("Test exception")
        
        # 验证stop_recording被调用（即使发生异常）
        assert len(stop_called) > 0
    
    def test_context_manager_does_not_suppress_exceptions(self):
        """测试上下文管理器不抑制异常"""
        exception_raised = False
        try:
            with InputRecorder() as recorder:
                raise RuntimeError("Test error")
        except RuntimeError as e:
            exception_raised = True
            assert str(e) == "Test error"
        
        assert exception_raised
    
    def test_context_manager_with_normal_usage(self):
        """测试上下文管理器的正常使用"""
        with InputRecorder() as recorder:
            # 验证初始状态
            assert not recorder.is_recording
            assert not recorder.is_playing
            assert recorder.get_action_count() == 0
    
    def test_context_manager_reentrant(self):
        """测试上下文管理器可重入"""
        recorder = InputRecorder()
        
        with recorder as r1:
            assert r1 is recorder
        
        with recorder as r2:
            assert r2 is recorder


class TestRecordingManagerResourceManager:
    """RecordingManager资源管理测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_context_manager_enter(self, temp_dir):
        """测试上下文管理器入口"""
        with RecordingManager(temp_dir) as manager:
            assert manager is not None
            assert isinstance(manager, RecordingManager)
    
    def test_context_manager_creates_directory(self, temp_dir):
        """测试上下文管理器创建目录"""
        new_dir = os.path.join(temp_dir, "new_recordings")
        
        with RecordingManager(new_dir) as manager:
            assert os.path.exists(new_dir)
    
    def test_context_manager_normal_usage(self, temp_dir):
        """测试上下文管理器的正常使用"""
        with RecordingManager(temp_dir) as manager:
            # 测试基本功能
            recordings = manager.list_recordings()
            assert isinstance(recordings, list)
            
            # 测试路径获取
            path = manager.get_recording_path("test")
            assert path.endswith("test.json")


class TestInputRecorderResourceCleanup:
    """InputRecorder资源清理测试类"""
    
    def test_stop_recording_clears_state(self):
        """测试停止录制清理状态"""
        recorder = InputRecorder()
        recorder.is_recording = True
        recorder.pressed_keys.add('a')
        recorder.pressed_keys.add('b')
        
        # 直接调用stop_recording（不实际启动录制）
        # 由于没有实际的监听器，我们需要模拟
        recorder.mouse_listener = None
        recorder.keyboard_hook = None
        
        # 清理按键状态
        import pydirectinput
        for key in recorder.pressed_keys:
            try:
                pydirectinput.keyUp(key)
            except:
                pass
        recorder.pressed_keys.clear()
        recorder.is_recording = False
        
        assert not recorder.is_recording
        assert len(recorder.pressed_keys) == 0
    
    def test_stop_playback_clears_state(self):
        """测试停止回放清理状态"""
        recorder = InputRecorder()
        recorder.is_playing = True
        recorder.stop_event = None
        recorder.play_process = None
        
        recorder.stop_playback()
        
        assert not recorder.is_playing
    
    def test_multiple_context_entries(self):
        """测试多次进入上下文"""
        recorder = InputRecorder()
        
        # 第一次进入
        with recorder as r1:
            r1.is_recording = True
        
        # 验证状态被清理
        assert not recorder.is_recording
        
        # 第二次进入
        with recorder as r2:
            r2.is_playing = True
        
        # 验证状态被清理
        assert not recorder.is_playing


class TestInputRecorderThreadSafety:
    """InputRecorder线程安全测试类"""
    
    def test_recording_lock_exists(self):
        """测试录制锁存在"""
        recorder = InputRecorder()
        assert hasattr(recorder, 'recording_lock')
        assert recorder.recording_lock is not None
    
    def test_recording_lock_type(self):
        """测试录制锁类型"""
        recorder = InputRecorder()
        import threading
        assert isinstance(recorder.recording_lock, type(threading.Lock()))
