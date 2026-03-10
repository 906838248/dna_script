"""
配置管理器测试
测试配置验证和修复功能
"""

import pytest
import os
import json
import tempfile
import shutil

from src.config_manager import ConfigManager


class TestConfigManager:
    """配置管理器测试类"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """创建临时配置目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """创建配置管理器实例"""
        return ConfigManager(config_dir=temp_config_dir)
    
    def test_default_config_exists(self, config_manager):
        """测试默认配置存在"""
        assert hasattr(ConfigManager, 'DEFAULT_CONFIG')
        assert isinstance(ConfigManager.DEFAULT_CONFIG, dict)
        assert 'script' in ConfigManager.DEFAULT_CONFIG
        assert 'recording' in ConfigManager.DEFAULT_CONFIG
        assert 'window' in ConfigManager.DEFAULT_CONFIG
        assert 'shortcuts' in ConfigManager.DEFAULT_CONFIG
    
    def test_validation_rules_exist(self, config_manager):
        """测试验证规则存在"""
        assert hasattr(ConfigManager, 'VALIDATION_RULES')
        assert isinstance(ConfigManager.VALIDATION_RULES, dict)
        assert 'script.last_loop_count' in ConfigManager.VALIDATION_RULES
        assert 'window.width' in ConfigManager.VALIDATION_RULES
        assert 'window.height' in ConfigManager.VALIDATION_RULES
    
    def test_validate_config_with_valid_data(self, config_manager):
        """测试验证有效配置"""
        valid_config = {
            "script": {
                "last_selected": "test_script",
                "last_loop_count": 10,
                "auto_switch_to_log": False
            },
            "recording": {
                "last_name": "test_recording"
            },
            "window": {
                "width": 1024,
                "height": 768
            },
            "shortcuts": {
                "start_automation": "F5",
                "stop_automation": "F6",
                "clear_log": "F7",
                "toggle_recording": "F8",
                "stop_recording_playback": "esc"
            }
        }
        
        assert config_manager.validate_config(valid_config) is True
    
    def test_validate_config_with_invalid_loop_count(self, config_manager):
        """测试验证无效循环次数"""
        invalid_config = {
            "script": {
                "last_loop_count": -1
            }
        }
        
        assert config_manager.validate_config(invalid_config) is False
    
    def test_validate_config_with_invalid_loop_count_type(self, config_manager):
        """测试验证循环次数类型错误"""
        invalid_config = {
            "script": {
                "last_loop_count": "not_a_number"
            }
        }
        
        assert config_manager.validate_config(invalid_config) is False
    
    def test_validate_config_with_invalid_window_width(self, config_manager):
        """测试验证无效窗口宽度"""
        invalid_config = {
            "window": {
                "width": 100
            }
        }
        
        assert config_manager.validate_config(invalid_config) is False
    
    def test_validate_config_with_invalid_window_height(self, config_manager):
        """测试验证无效窗口高度"""
        invalid_config = {
            "window": {
                "height": 5000
            }
        }
        
        assert config_manager.validate_config(invalid_config) is False
    
    def test_validate_shortcut_with_valid_single_key(self, config_manager):
        """测试验证有效单键快捷键"""
        assert config_manager._validate_shortcut("F5") is True
        assert config_manager._validate_shortcut("esc") is True
        assert config_manager._validate_shortcut("a") is True
        assert config_manager._validate_shortcut("1") is True
    
    def test_validate_shortcut_with_valid_combo_key(self, config_manager):
        """测试验证有效组合键快捷键"""
        assert config_manager._validate_shortcut("ctrl+a") is True
        assert config_manager._validate_shortcut("alt+F4") is True
        assert config_manager._validate_shortcut("shift+ctrl+a") is True
    
    def test_validate_shortcut_with_invalid_key(self, config_manager):
        """测试验证无效快捷键"""
        assert config_manager._validate_shortcut("") is False
        assert config_manager._validate_shortcut("   ") is False
        assert config_manager._validate_shortcut(123) is False
        assert config_manager._validate_shortcut("invalid_key_name") is False
    
    def test_validate_shortcut_with_too_long_key(self, config_manager):
        """测试验证过长的快捷键"""
        long_key = "a" * 51
        assert config_manager._validate_shortcut(long_key) is False
    
    def test_validate_and_fix_config(self, config_manager):
        """测试验证并修复配置"""
        # 设置无效配置
        config_manager.config_data = {
            "script": {
                "last_loop_count": -1
            },
            "window": {
                "width": 100,
                "height": 5000
            },
            "shortcuts": {
                "start_automation": ""
            }
        }
        
        # 验证并修复
        fixed = config_manager.validate_and_fix_config()
        
        assert fixed is True
        assert config_manager.get("script.last_loop_count") == 1
        assert config_manager.get("window.width") == 900
        assert config_manager.get("window.height") == 700
        assert config_manager.get("shortcuts.start_automation") == "F5"
    
    def test_set_with_valid_value(self, config_manager):
        """测试设置有效配置值"""
        result = config_manager.set("script.last_loop_count", 100)
        assert result is True
        assert config_manager.get("script.last_loop_count") == 100
    
    def test_set_with_invalid_value(self, config_manager):
        """测试设置无效配置值"""
        original_value = config_manager.get("script.last_loop_count")
        result = config_manager.set("script.last_loop_count", -1)
        assert result is False
        assert config_manager.get("script.last_loop_count") == original_value
    
    def test_load_config_with_invalid_file(self, temp_config_dir):
        """测试加载无效配置文件"""
        # 创建无效的配置文件
        config_file = os.path.join(temp_config_dir, "user_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        config_manager = ConfigManager(config_dir=temp_config_dir)
        
        # 应该使用默认配置
        assert config_manager.config_data == ConfigManager.DEFAULT_CONFIG.copy()
    
    def test_load_config_with_invalid_values(self, temp_config_dir):
        """测试加载包含无效值的配置文件"""
        # 创建包含无效值的配置文件
        config_file = os.path.join(temp_config_dir, "user_config.json")
        invalid_config = {
            "script": {
                "last_loop_count": -1
            },
            "window": {
                "width": 100
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f)
        
        config_manager = ConfigManager(config_dir=temp_config_dir)
        
        # 应该修复无效值
        assert config_manager.get("script.last_loop_count") == 1
        assert config_manager.get("window.width") == 900
    
    def test_get_nested_value(self, config_manager):
        """测试获取嵌套值"""
        config_manager.config_data = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        
        assert config_manager._get_nested_value(config_manager.config_data, "level1.level2.level3") == "value"
        assert config_manager._get_nested_value(config_manager.config_data, "level1.level2.nonexistent") is None
        assert config_manager._get_nested_value(config_manager.config_data, "nonexistent.key") is None
    
    def test_config_persistence(self, config_manager):
        """测试配置持久化"""
        # 设置配置
        config_manager.set("script.last_loop_count", 50)
        config_manager.set("script.last_selected", "test_script")
        
        # 重新加载
        config_manager.load_config()
        
        # 验证配置已保存
        assert config_manager.get("script.last_loop_count") == 50
        assert config_manager.get("script.last_selected") == "test_script"
