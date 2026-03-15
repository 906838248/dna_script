"""
自动化控制器单元测试
测试增强的错误处理功能
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import QObject, Signal
from src.controllers.automation_controller import (
    AutomationController,
    AutomationError,
    AutomationRunningError,
    ScriptNotFoundError,
    ScriptInitializationError,
    AutomationExecutionError
)


class MockScriptInfo:
    """模拟脚本信息类"""
    def __init__(self, name, script_class, img_folder):
        self.name = name
        self.script_class = script_class
        self.img_folder = img_folder


class MockAutomationThread:
    """模拟自动化线程类"""
    def __init__(self, loop_count, img_folder, game_resolution=None):
        self.loop_count = loop_count
        self.img_folder = img_folder
        self.game_resolution = game_resolution
        self.log_signal = Mock()
        self.finished_signal = Mock()
        self.progress_signal = Mock()
        self._running = False
    
    def start(self):
        """启动线程"""
        self._running = True
    
    def stop(self):
        """停止线程"""
        self._running = False
    
    def isRunning(self):
        """检查是否正在运行"""
        return self._running
    
    def wait(self, timeout):
        """等待线程结束"""
        return True


class TestAutomationController:
    """自动化控制器测试类"""
    
    @pytest.fixture
    def controller(self):
        """创建控制器实例"""
        return AutomationController()
    
    @pytest.fixture
    def mock_script_info(self):
        """创建模拟脚本信息"""
        return MockScriptInfo(
            name="测试脚本",
            script_class=MockAutomationThread,
            img_folder="test_images"
        )
    
    def test_start_automation_when_already_running(self, controller, mock_script_info):
        """测试当自动化正在运行时启动自动化"""
        controller.is_running = True
        
        with pytest.raises(AutomationRunningError) as exc_info:
            controller.start_automation(mock_script_info, 1)
        
        assert "自动化正在运行中" in str(exc_info.value)
    
    def test_start_automation_with_none_script_info(self, controller):
        """测试使用None脚本信息启动自动化"""
        with pytest.raises(ScriptNotFoundError) as exc_info:
            controller.start_automation(None, 1)
        
        assert "请先选择一个脚本" in str(exc_info.value)
    
    def test_start_automation_with_invalid_script_info(self, controller):
        """测试使用无效脚本信息启动自动化"""
        invalid_script = Mock()
        del invalid_script.name
        
        with pytest.raises(ScriptNotFoundError) as exc_info:
            controller.start_automation(invalid_script, 1)
        
        assert "脚本信息无效" in str(exc_info.value)
    
    def test_start_automation_with_invalid_loop_count(self, controller, mock_script_info):
        """测试使用无效循环次数启动自动化"""
        with pytest.raises(ValueError) as exc_info:
            controller.start_automation(mock_script_info, 0)
        
        assert "循环次数无效" in str(exc_info.value)
    
    def test_start_automation_with_string_loop_count(self, controller, mock_script_info):
        """测试使用字符串循环次数启动自动化"""
        with pytest.raises(ValueError) as exc_info:
            controller.start_automation(mock_script_info, "invalid")
        
        assert "循环次数无效" in str(exc_info.value)
    
    def test_start_automation_success(self, controller, mock_script_info):
        """测试成功启动自动化"""
        result = controller.start_automation(mock_script_info, 5)
        
        assert result is True
        assert controller.is_running is True
        assert controller.current_script == mock_script_info
        assert controller.automation_thread is not None
    
    def test_start_automation_script_initialization_error(self, controller):
        """测试脚本初始化失败"""
        class FailingScript:
            def __init__(self, loop_count, img_folder):
                raise RuntimeError("初始化失败")
        
        mock_script = MockScriptInfo(
            name="失败脚本",
            script_class=FailingScript,
            img_folder="test_images"
        )
        
        with pytest.raises(ScriptInitializationError) as exc_info:
            controller.start_automation(mock_script, 1)
        
        assert "脚本初始化失败" in str(exc_info.value)
        assert controller.is_running is False
    
    def test_stop_automation_when_not_running(self, controller):
        """测试当自动化未运行时停止自动化"""
        result = controller.stop_automation()
        
        assert result is False
    
    def test_stop_automation_success(self, controller, mock_script_info):
        """测试成功停止自动化"""
        controller.start_automation(mock_script_info, 1)
        
        result = controller.stop_automation()
        
        assert result is True
        assert controller.is_running is False
        assert controller.current_script is None
        assert controller.automation_thread is None
    
    def test_stop_automation_timeout(self, controller, mock_script_info):
        """测试停止自动化超时"""
        class SlowThread:
            def __init__(self, loop_count, img_folder, game_resolution=None):
                self.log_signal = Mock()
                self.finished_signal = Mock()
                self.progress_signal = Mock()
            
            def start(self):
                pass
            
            def stop(self):
                pass
            
            def wait(self, timeout):
                return False
            
            def isRunning(self):
                return True
            
            def terminate(self):
                pass
        
        mock_script = MockScriptInfo(
            name="慢脚本",
            script_class=SlowThread,
            img_folder="test_images"
        )
        
        controller.start_automation(mock_script, 1)
        
        with pytest.raises(TimeoutError) as exc_info:
            controller.stop_automation(timeout=1)
        
        assert "停止自动化超时" in str(exc_info.value)
        assert controller.is_running is False
    
    def test_get_current_script(self, controller, mock_script_info):
        """测试获取当前脚本"""
        controller.start_automation(mock_script_info, 1)
        
        current_script = controller.get_current_script()
        
        assert current_script == mock_script_info
    
    def test_get_current_script_when_not_running(self, controller):
        """测试当自动化未运行时获取当前脚本"""
        current_script = controller.get_current_script()
        
        assert current_script is None
    
    def test_is_automation_running(self, controller, mock_script_info):
        """测试检查自动化是否正在运行"""
        assert controller.is_automation_running() is False
        
        controller.start_automation(mock_script_info, 1)
        
        assert controller.is_automation_running() is True
        
        controller.stop_automation()
        
        assert controller.is_automation_running() is False
    
    def test_get_last_error(self, controller):
        """测试获取最后一次错误"""
        assert controller.get_last_error() is None
        
        controller.last_error = "测试错误"
        
        assert controller.get_last_error() == "测试错误"
    
    def test_cleanup_when_running(self, controller, mock_script_info):
        """测试清理资源时自动化正在运行"""
        controller.start_automation(mock_script_info, 1)
        
        controller.cleanup()
        
        assert controller.is_running is False
        assert controller.current_script is None
        assert controller.automation_thread is None
    
    def test_cleanup_when_not_running(self, controller):
        """测试清理资源时自动化未运行"""
        controller.cleanup()
        
        assert controller.is_running is False
        assert controller.current_script is None
        assert controller.automation_thread is None
    
    def test_error_signal_emission(self, controller, mock_script_info):
        """测试错误信号发射"""
        error_received = []
        
        def on_error(error_type, error_message):
            error_received.append((error_type, error_message))
        
        controller.error_signal.connect(on_error)
        
        try:
            controller.start_automation(None, 1)
        except ScriptNotFoundError:
            pass
        
        assert len(error_received) == 1
        assert error_received[0][0] == "ScriptNotFoundError"
        assert "请先选择一个脚本" in error_received[0][1]
