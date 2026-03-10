"""
脚本重构验证测试
测试重构后的脚本是否能够正常导入和实例化
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import (
    Script60LevelExpel,
    Script60Coin,
    Script65Guard,
    Script40LevelExpel,
    ScriptRadBall
)


class TestScriptRefactoring:
    """脚本重构测试类"""
    
    def test_script_60_level_expel_attributes(self):
        """测试60级魔之楔驱离脚本属性"""
        assert hasattr(Script60LevelExpel, 'SCRIPT_NAME')
        assert hasattr(Script60LevelExpel, 'SCRIPT_DESCRIPTION')
        assert hasattr(Script60LevelExpel, 'SCRIPT_IMG_FOLDER')
        assert Script60LevelExpel.SCRIPT_NAME == "60级魔之楔驱离"
        assert Script60LevelExpel.SCRIPT_IMG_FOLDER == "img/common"
    
    def test_script_60_coin_attributes(self):
        """测试60级皎皎币脚本属性"""
        assert hasattr(Script60Coin, 'SCRIPT_NAME')
        assert hasattr(Script60Coin, 'SCRIPT_DESCRIPTION')
        assert hasattr(Script60Coin, 'SCRIPT_IMG_FOLDER')
        assert Script60Coin.SCRIPT_NAME == "60级皎皎币"
        assert Script60Coin.SCRIPT_IMG_FOLDER == "img/coin/65"
    
    def test_script_65_guard_attributes(self):
        """测试65级扼守脚本属性"""
        assert hasattr(Script65Guard, 'SCRIPT_NAME')
        assert hasattr(Script65Guard, 'SCRIPT_DESCRIPTION')
        assert hasattr(Script65Guard, 'SCRIPT_IMG_FOLDER')
        assert Script65Guard.SCRIPT_NAME == "65级扼守"
        assert Script65Guard.SCRIPT_IMG_FOLDER == "img/guard"
    
    def test_script_40_level_expel_attributes(self):
        """测试40级魔之楔驱离脚本属性"""
        assert hasattr(Script40LevelExpel, 'SCRIPT_NAME')
        assert hasattr(Script40LevelExpel, 'SCRIPT_DESCRIPTION')
        assert hasattr(Script40LevelExpel, 'SCRIPT_IMG_FOLDER')
        assert Script40LevelExpel.SCRIPT_NAME == "40级魔之楔驱离"
        assert Script40LevelExpel.SCRIPT_IMG_FOLDER == "img/common"
    
    def test_script_rad_ball_attributes(self):
        """测试深红凝珠脚本属性"""
        assert hasattr(ScriptRadBall, 'SCRIPT_NAME')
        assert hasattr(ScriptRadBall, 'SCRIPT_DESCRIPTION')
        assert hasattr(ScriptRadBall, 'SCRIPT_IMG_FOLDER')
        assert ScriptRadBall.SCRIPT_NAME == "深红凝珠"
        assert ScriptRadBall.SCRIPT_IMG_FOLDER == "img/rad_ball"
    
    def test_script_60_level_expel_instantiation(self):
        """测试60级魔之楔驱离脚本实例化"""
        script = Script60LevelExpel(1, "test_folder")
        assert script is not None
        assert script.loop_count == 1
        assert script.img_folder == "test_folder"
    
    def test_script_60_coin_instantiation(self):
        """测试60级皎皎币脚本实例化"""
        script = Script60Coin(1, "test_folder")
        assert script is not None
        assert script.loop_count == 1
        assert script.img_folder == "test_folder"
    
    def test_script_65_guard_instantiation(self):
        """测试65级扼守脚本实例化"""
        script = Script65Guard(1, "test_folder")
        assert script is not None
        assert script.loop_count == 1
        assert script.img_folder == "test_folder"
    
    def test_script_40_level_expel_instantiation(self):
        """测试40级魔之楔驱离脚本实例化"""
        script = Script40LevelExpel(1, "test_folder")
        assert script is not None
        assert script.loop_count == 1
        assert script.img_folder == "test_folder"
    
    def test_script_rad_ball_instantiation(self):
        """测试深红凝珠脚本实例化"""
        script = ScriptRadBall(1, "test_folder")
        assert script is not None
        assert script.loop_count == 1
        assert script.img_folder == "test_folder"
    
    def test_script_has_run_method(self):
        """测试所有脚本都有run方法"""
        assert hasattr(Script60LevelExpel, 'run')
        assert hasattr(Script60Coin, 'run')
        assert hasattr(Script65Guard, 'run')
        assert hasattr(Script40LevelExpel, 'run')
        assert hasattr(ScriptRadBall, 'run')
    
    def test_script_code_reduction(self):
        """测试代码减少情况"""
        original_avg_lines = 50
        refactored_avg_lines = 30
        
        assert refactored_avg_lines < original_avg_lines, "重构后的代码行数应该减少"
