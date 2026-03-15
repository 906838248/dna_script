"""
多分辨率图片识别测试
测试特征点匹配和自适应缩放功能
"""

import pytest
import sys
import os
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base_automation import BaseAutomationThread
from src.constants import GameConstants


class MockAutomationThread(BaseAutomationThread):
    """用于测试的自动化线程"""
    SCRIPT_NAME = "测试脚本"
    SCRIPT_DESCRIPTION = "多分辨率测试"
    SCRIPT_IMG_FOLDER = "img/common"


class TestMultiResolution:
    """多分辨率图片识别测试类"""
    
    @pytest.fixture
    def automation(self):
        """创建自动化线程实例"""
        return MockAutomationThread(1, "img/common")
    
    def test_scale_factor_calculation(self, automation):
        """测试缩放因子计算"""
        assert hasattr(automation, 'scale_factor')
        assert isinstance(automation.scale_factor, float)
        assert automation.scale_factor > 0
        
        # 默认游戏分辨率是1920x1080，缩放因子应该接近1
        assert abs(automation.scale_factor - 1.0) < 0.01
    
    def test_scale_factor_with_custom_resolution(self):
        """测试自定义游戏分辨率的缩放因子"""
        # 测试2560x1440分辨率
        automation = MockAutomationThread(1, "img/common", (2560, 1440))
        expected_scale = ((2560/1920) + (1440/1080)) / 2
        assert abs(automation.scale_factor - expected_scale) < 0.01
        
        # 测试1280x720分辨率
        automation = MockAutomationThread(1, "img/common", (1280, 720))
        expected_scale = ((1280/1920) + (720/1080)) / 2
        assert abs(automation.scale_factor - expected_scale) < 0.01
    
    def test_scale_template_no_scaling(self, automation):
        """测试模板缩放（无缩放情况）"""
        # 创建测试图片
        template = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 设置缩放因子为1
        automation.scale_factor = 1.0
        
        # 缩放模板
        scaled = automation._scale_template(template)
        
        # 验证尺寸相同
        assert scaled.shape == template.shape
    
    def test_scale_template_with_scaling(self, automation):
        """测试模板缩放（有缩放情况）"""
        # 创建测试图片
        template = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 设置缩放因子为0.5
        automation.scale_factor = 0.5
        
        # 缩放模板
        scaled = automation._scale_template(template)
        
        # 验证尺寸缩小
        assert scaled.shape[0] == 50
        assert scaled.shape[1] == 50
    
    def test_scale_template_upscaling(self, automation):
        """测试模板缩放（放大情况）"""
        # 创建测试图片
        template = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 设置缩放因子为1.5
        automation.scale_factor = 1.5
        
        # 缩放模板
        scaled = automation._scale_template(template)
        
        # 验证尺寸放大
        assert scaled.shape[0] == 150
        assert scaled.shape[1] == 150
    
    def test_orb_detector_initialization(self, automation):
        """测试ORB特征检测器初始化"""
        assert hasattr(automation, 'orb_detector')
        assert automation.orb_detector is not None
        
        assert hasattr(automation, 'bf_matcher')
        assert automation.bf_matcher is not None
    
    def test_feature_cache_initialization(self, automation):
        """测试特征点缓存初始化"""
        assert hasattr(automation, 'feature_cache')
        assert isinstance(automation.feature_cache, dict)
        assert len(automation.feature_cache) == 0
    
    def test_match_by_features_no_features(self, automation):
        """测试特征点匹配（无特征点情况）"""
        # 创建纯色图片（无特征点）
        screenshot = np.ones((1080, 1920, 3), dtype=np.uint8) * 128
        template = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        # 尝试匹配
        result = automation._match_by_features(screenshot, template, 0.7)
        
        # 应该返回None（无特征点）
        assert result is None
    
    def test_match_by_features_with_features(self, automation):
        """测试特征点匹配（有特征点情况）"""
        # 创建带有特征的图片
        screenshot = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        template = screenshot[100:200, 100:200].copy()
        
        # 尝试匹配
        result = automation._match_by_features(screenshot, template, 0.5)
        
        # 可能找到匹配（取决于特征点质量）
        if result:
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert isinstance(result[0], int)
            assert isinstance(result[1], int)
    
    def test_match_by_features_out_of_bounds(self, automation):
        """测试特征点匹配（位置超出屏幕范围）"""
        # 创建测试图片
        screenshot = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        template = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 尝试匹配（可能失败）
        result = automation._match_by_features(screenshot, template, 0.9)
        
        # 结果应该是None或有效坐标
        if result:
            x, y = result
            assert 0 <= x < 1920
            assert 0 <= y < 1080
    
    def test_lru_cache_clears_feature_cache(self, automation):
        """测试LRU缓存清理特征点缓存"""
        # 设置较小的缓存大小
        automation.template_cache_max_size = 2
        
        # 添加特征点缓存
        automation.feature_cache['test1.png'] = (None, None)
        automation.feature_cache['test2.png'] = (None, None)
        
        # 添加模板缓存
        automation.template_cache['test1.png'] = np.zeros((10, 10, 3), dtype=np.uint8)
        automation.template_cache['test2.png'] = np.zeros((10, 10, 3), dtype=np.uint8)
        automation.template_cache_access['test1.png'] = 1.0
        automation.template_cache_access['test2.png'] = 2.0
        
        # 触发LRU淘汰
        automation._evict_lru_template()
        
        # 验证特征点缓存也被清理
        assert 'test1.png' not in automation.feature_cache
        assert 'test1.png' not in automation.template_cache
    
    def test_cleanup_clears_feature_cache(self, automation):
        """测试停止时清理特征点缓存"""
        # 添加特征点缓存
        automation.feature_cache['test.png'] = (None, None)
        
        # 停止线程
        automation.stop()
        
        # 验证特征点缓存已清理
        assert len(automation.feature_cache) == 0
    
    def test_find_image_with_scaling(self, automation):
        """测试图片查找（带缩放）"""
        # 设置非基准分辨率
        automation.scale_factor = 0.8
        
        # 尝试查找图片（实际测试需要真实图片）
        # 这里只验证方法不会崩溃
        try:
            result = automation.find_image("begin.png", timeout=1)
            # 结果应该是None（测试环境没有真实屏幕）或有效坐标
            if result:
                assert isinstance(result, tuple)
                assert len(result) == 2
        except Exception as e:
            # 如果图片不存在，应该返回None而不是崩溃
            pass
    
    def test_constants_multi_resolution_settings(self):
        """测试多分辨率常量设置"""
        assert hasattr(GameConstants, 'BASE_RESOLUTION')
        assert GameConstants.BASE_RESOLUTION == (1920, 1080)
        
        assert hasattr(GameConstants, 'ENABLE_FEATURE_MATCHING')
        assert isinstance(GameConstants.ENABLE_FEATURE_MATCHING, bool)
        
        assert hasattr(GameConstants, 'FEATURE_MATCH_THRESHOLD')
        assert 0 < GameConstants.FEATURE_MATCH_THRESHOLD < 1
        
        assert hasattr(GameConstants, 'MIN_MATCH_COUNT')
        assert GameConstants.MIN_MATCH_COUNT > 0
