"""
版本信息管理模块
用于管理软件版本信息、更新日志和帮助文档
"""

from typing import List, Dict
from datetime import datetime


class VersionInfo:
    """版本信息类"""
    def __init__(self, version: str, date: str, description: str):
        self.version = version
        self.date = date
        self.description = description


class UpdateLog:
    """更新日志类"""
    def __init__(self, version: str, date: str, changes: List[str]):
        self.version = version
        self.date = date
        self.changes = changes


class VersionManager:
    """版本管理器类"""
    
    def __init__(self):
        self.app_name = "二重螺旋 - 统一脚本管理器"
        self.current_version = "v1.0.7"
        self.release_date = "2026-03-02"
        
        # 版本更新日志
        self.update_logs = [
            UpdateLog(
                version="v1.0.7",
                date="2026-03-02",
                changes=[
                    "将快捷键设置单独提取为独立标签页",
                    "优化界面布局，提升用户体验"
                ]
            ),
            UpdateLog(
                version="v1.0.6",
                date="2026-03-02",
                changes=[
                    "优化界面布局，调整窗口宽度和按钮尺寸",
                    "修复录制结束时把停止按键录制进去的问题",
                    "新增自动跳转日志页面选项，勾选后开始脚本自动跳转到日志页面"
                ]
            ),
            UpdateLog(
                version="v1.0.5",
                date="2026-03-02",
                changes=[
                    "优化界面布局",
                ]
            ),
            UpdateLog(
                version="v1.0.4",
                date="2026-03-02",
                changes=[
                    "修复快捷键无法使用的问题",
                    "修复程序图片读取错误的问题"
                ]
            ),
            UpdateLog(
                version="v1.0.3",
                date="2026-03-02",
                changes=[
                    "新增快捷键管理模块 shortcut_manager.py",
                    "实现快捷键自定义功能，用户可在版本说明页面修改快捷键",
                    "移除底部快捷键说明，统一在版本说明页面显示和设置",
                    "支持保存和重置快捷键配置",
                    "快捷键配置自动保存到配置文件",
                    "程序启动时自动加载上次保存的快捷键配置",
                    "优化快捷键管理，使用枚举类型统一管理快捷键操作",
                    "提升用户界面整洁度，避免快捷键说明重复显示"
                ]
            ),
            UpdateLog(
                version="v1.0.2",
                date="2026-03-02",
                changes=[
                    "新增配置管理模块 config_manager.py",
                    "实现用户配置自动保存和加载功能",
                    "自动记录上次选择的脚本，启动时自动恢复",
                    "自动记录上次设置的循环次数，启动时自动恢复",
                    "自动记录上次使用的录制名称，启动时自动恢复",
                    "配置文件使用 JSON 格式存储在 config 文件夹",
                    "程序启动时自动加载上次保存的配置",
                    "用户操作时自动保存配置（脚本选择、循环次数、录制名称）",
                    "提升用户体验，无需重复设置常用参数"
                ]
            ),
            UpdateLog(
                version="v1.0.1",
                date="2026-03-02",
                changes=[
                    "优化项目结构，创建 src 文件夹存放核心模块",
                    "将 base_automation.py、input_recorder.py、styles.py、version_info.py 移至 src 文件夹",
                    "更新所有模块的导入语句，统一使用 src. 前缀",
                    "解决 Qt DPI 感知错误（SetProcessDpiAwarenessContext 失败）",
                    "创建 qt.conf 配置文件，禁用 Qt DPI 感知设置",
                    "移除 main.py 中的 ctypes DPI 设置代码，避免冲突",
                    "创建 src/__init__.py 包初始化文件",
                    "保持 main.py 在根目录作为程序入口",
                    "提升代码组织性和可维护性"
                ]
            ),
            UpdateLog(
                version="v1.0.0",
                date="2026-03-02",
                changes=[
                    "初始版本发布",
                    "支持60级魔之楔驱离脚本",
                    "支持40级魔之楔驱离脚本",
                    "支持机傀大乱斗脚本",
                    "支持护送副本脚本",
                    "实现图像识别功能",
                    "实现录制回放功能",
                    "实现反作弊机制（随机延迟、贝塞尔曲线）",
                    "实现进度追踪功能",
                    "实现详细日志记录",
                    "优化UI布局，使用标签页分组"
                ]
            )
        ]
        
        # 功能特性
        self.features = [
            "多脚本支持：支持多个游戏副本的自动化脚本",
            "图像识别：基于OpenCV的图像识别技术",
            "录制回放：支持键盘鼠标操作的录制与回放",
            "反作弊机制：随机延迟和贝塞尔曲线鼠标移动",
            "进度追踪：实时显示脚本执行进度",
            "日志记录：详细的运行日志便于调试"
        ]
        
        # 支持的脚本
        self.supported_scripts = [
            "60级魔之楔驱离",
            "40级魔之楔驱离",
            "机傀大乱斗",
            "80级护送副本",
            "65级扼守"
        ]
        
        # 使用说明
        self.usage_guide = [
            "在「自动化脚本」标签页选择要执行的脚本",
            "设置循环次数，点击「开始」按钮或按F5启动",
            "在「录制功能」标签页可以录制和回放操作",
            "在「日志」标签页查看详细的运行日志",
            "在「快捷键设置」标签页设置和查看快捷键",
            "请在开始挑战界面开启脚本，否则脚本无法正常运行"
        ]
        
        # 注意事项
        self.notices = [
            "请在16:10的1920x1080分辨率下使用",
            "如遇问题请查看日志标签页的详细错误信息",
            "使用过程中请保持网络连接稳定"
        ]
    
    def get_current_version(self) -> VersionInfo:
        """
        获取当前版本信息
        
        Returns:
            VersionInfo: 当前版本信息对象
        """
        return VersionInfo(
            version=self.current_version,
            date=self.release_date,
            description=f"{self.app_name} {self.current_version}"
        )
    
    def get_update_logs(self) -> List[UpdateLog]:
        """
        获取所有更新日志
        
        Returns:
            List[UpdateLog]: 更新日志列表
        """
        return self.update_logs
    
    def get_features(self) -> List[str]:
        """
        获取功能特性列表
        
        Returns:
            List[str]: 功能特性列表
        """
        return self.features
    
    def get_supported_scripts(self) -> List[str]:
        """
        获取支持的脚本列表
        
        Returns:
            List[str]: 支持的脚本列表
        """
        return self.supported_scripts
    
    def get_tech_stack(self) -> List[str]:
        """
        获取技术栈列表
        
        Returns:
            List[str]: 技术栈列表
        """
        return self.tech_stack
    
    def get_usage_guide(self) -> List[str]:
        """
        获取使用说明列表
        
        Returns:
            List[str]: 使用说明列表
        """
        return self.usage_guide
    
    def get_notices(self) -> List[str]:
        """
        获取注意事项列表
        
        Returns:
            List[str]: 注意事项列表
        """
        return self.notices
    
    def add_update_log(self, version: str, date: str, changes: List[str]):
        """
        添加新的更新日志
        
        Args:
            version: 版本号
            date: 发布日期
            changes: 更新内容列表
        """
        self.update_logs.insert(0, UpdateLog(version, date, changes))
    
    def update_current_version(self, version: str, date: str = None):
        """
        更新当前版本号
        
        Args:
            version: 新版本号
            date: 发布日期（可选，默认为当前日期）
        """
        self.current_version = version
        if date:
            self.release_date = date
        else:
            self.release_date = datetime.now().strftime("%Y-%m-%d")
    
    def format_update_logs(self) -> str:
        """
        格式化更新日志为字符串
        
        Returns:
            str: 格式化后的更新日志字符串
        """
        result = []
        for log in self.update_logs:
            result.append(f"【{log.version}】 - {log.date}")
            for i, change in enumerate(log.changes, 1):
                result.append(f"  {i}. {change}")
            result.append("")
        return "\n".join(result)
    
    def format_latest_update_log(self) -> str:
        """
        格式化最新的更新日志为字符串
        
        Returns:
            str: 格式化后的最新更新日志字符串
        """
        if not self.update_logs:
            return "暂无更新日志"
        
        log = self.update_logs[0]
        result = [f"【{log.version}】 - {log.date}"]
        for i, change in enumerate(log.changes, 1):
            result.append(f"  {i}. {change}")
        return "\n".join(result)
    
    def format_historical_update_logs(self) -> str:
        """
        格式化历史更新日志为字符串（排除最新版本）
        
        Returns:
            str: 格式化后的历史更新日志字符串
        """
        if len(self.update_logs) <= 1:
            return "暂无历史更新日志"
        
        result = []
        for log in self.update_logs[1:]:
            result.append(f"【{log.version}】 - {log.date}")
            for i, change in enumerate(log.changes, 1):
                result.append(f"  {i}. {change}")
            result.append("")
        return "\n".join(result)


# 全局版本管理器实例
version_manager = VersionManager()
