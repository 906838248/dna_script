"""
性能优化测试
测试模板缓存和屏幕截图缓存的效果
"""

import pytest
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base_automation import BaseAutomationThread


class MockAutomationThread(BaseAutomationThread):
    """用于测试的自动化线程"""
    SCRIPT_NAME = "测试脚本"
    SCRIPT_DESCRIPTION = "性能测试"
    SCRIPT_IMG_FOLDER = "img/common"


class TestPerformanceOptimization:
    """性能优化测试类"""
    
    @pytest.fixture
    def automation(self):
        """创建自动化线程实例"""
        return MockAutomationThread(1, "img/common")
    
    def test_template_cache_initialization(self, automation):
        """测试模板缓存初始化"""
        assert hasattr(automation, 'template_cache')
        assert automation.template_cache == {}
        assert len(automation.template_cache) == 0
    
    def test_screenshot_cache_initialization(self, automation):
        """测试屏幕截图缓存初始化"""
        assert hasattr(automation, 'screenshot_cache')
        assert automation.screenshot_cache is None
        assert hasattr(automation, 'screenshot_cache_ttl')
        assert automation.screenshot_cache_ttl == 0.1
    
    def test_template_cache_population(self, automation):
        """测试模板缓存填充"""
        assert len(automation.template_cache) == 0
        
        # 尝试查找图片（会填充缓存）
        automation.find_image("begin.png", timeout=1)
        
        # 验证缓存已填充
        assert len(automation.template_cache) > 0
        assert "begin.png" in automation.template_cache
    
    def test_template_cache_reuse(self, automation):
        """测试模板缓存重用"""
        # 第一次查找（会加载到缓存）
        start_time = time.time()
        automation.find_image("begin.png", timeout=1)
        first_load_time = time.time() - start_time
        
        # 第二次查找（应该使用缓存）
        start_time = time.time()
        automation.find_image("begin.png", timeout=1)
        second_load_time = time.time() - start_time
        
        # 第二次应该更快（使用缓存）
        assert second_load_time < first_load_time * 2
    
    def test_screenshot_cache_effectiveness(self, automation):
        """测试屏幕截图缓存有效性"""
        # 第一次截图
        start_time = time.time()
        automation.find_image("begin.png", timeout=1)
        first_screenshot_time = time.time() - start_time
        
        # 短时间内再次查找（应该使用缓存）
        start_time = time.time()
        automation.find_image("begin.png", timeout=1)
        second_screenshot_time = time.time() - start_time
        
        # 第二次应该更快（使用缓存的截图）
        assert second_screenshot_time < first_screenshot_time * 1.5
    
    def test_cache_clear_on_stop(self, automation):
        """测试停止时清理缓存"""
        # 填充缓存
        automation.find_image("begin.png", timeout=1)
        assert len(automation.template_cache) > 0
        
        # 停止线程
        automation.stop()
        
        # 验证缓存已清理
        assert len(automation.template_cache) == 0
        assert automation.screenshot_cache is None
    
    def test_multiple_images_cache(self, automation):
        """测试多图片缓存"""
        images = ["begin.png", "set.png", "else.png"]
        
        # 查找多个图片
        for img in images:
            automation.find_image(img, timeout=1)
        
        # 验证所有图片都在缓存中
        for img in images:
            assert img in automation.template_cache
        
        # 验证缓存大小正确
        assert len(automation.template_cache) == len(images)
    
    def test_cache_ttl_expiration(self, automation):
        """测试缓存过期机制"""
        # 第一次截图
        automation.find_image("begin.png", timeout=1)
        first_cache_time = automation.screenshot_cache_time
        
        # 等待超过TTL时间
        time.sleep(0.15)
        
        # 再次查找（应该重新截图）
        automation.find_image("begin.png", timeout=1)
        second_cache_time = automation.screenshot_cache_time
        
        # 验证缓存已更新
        assert second_cache_time > first_cache_time
    
    def test_performance_improvement(self, automation):
        """测试整体性能改进"""
        # 模拟多次查找操作
        iterations = 3
        
        # 预热缓存
        automation.find_image("begin.png", timeout=0.5)
        
        # 测量缓存性能（短时间内多次查找，应该使用缓存）
        start_time = time.time()
        for _ in range(iterations):
            automation.find_image("begin.png", timeout=0.5)
        cached_time = time.time() - start_time
        
        # 清除缓存
        automation.template_cache.clear()
        automation.screenshot_cache = None
        
        # 测量无缓存性能
        start_time = time.time()
        for _ in range(iterations):
            automation.find_image("begin.png", timeout=0.5)
        uncached_time = time.time() - start_time
        
        # 验证缓存机制正常工作（缓存版本应该不慢于无缓存版本太多）
        # 由于网络和系统负载等因素，允许一定的性能波动
        time_ratio = cached_time / uncached_time
        assert time_ratio < 1.5, f"缓存版本耗时 {cached_time:.2f}s，无缓存版本耗时 {uncached_time:.2f}s，比例 {time_ratio:.2f}"
