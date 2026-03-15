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
        self.current_version = "v1.2.0"
        self.release_date = "2026-03-15"
        
        # 版本更新日志
        self.update_logs = [
            UpdateLog(
                version="v1.2.0",
                date="2026-03-15",
                changes=[
                    "【新增功能】多分辨率支持 - 自动检测当前屏幕分辨率并计算缩放因子，根据分辨率自动缩放模板图片，使用ORB特征点匹配实现分辨率无关的图片识别，无需为不同分辨率准备多套图片",
                    "【性能优化】优化多进程资源清理，防止进程泄漏，添加僵尸进程自动清理机制，改进信号处理确保程序退出时正确释放资源，增强内存管理添加强制垃圾回收",
                    "【Bug修复】修复OpenCV内存不足错误，修复录制回放进程未正确关闭的问题，修复窗口关闭时资源未完全清理的问题，修复程序退出后不停止的问题",
                    "【测试改进】新增多分辨率功能测试（14个测试用例），总测试用例数量达到160个"
                ]
            ),
            UpdateLog(
                version="v1.1.0",
                date="2026-03-07",
                changes=[
                    "【新增功能】添加60级皎皎币脚本，添加深红凝珠脚本",
                    "【性能优化】实现模板图片缓存机制避免重复加载同一模板图片，实现屏幕截图缓存减少频繁截图操作，停止时自动清理缓存释放内存资源",
                    "【代码重构】在base_automation.py中实现通用游戏循环方法，重构所有脚本使用通用游戏循环方法减少代码量，优化脚本导入自动加载scripts文件夹中的脚本",
                    "【其他改进】改回放多线程为多进程，完善错误处理机制添加自定义异常类，添加完整的单元测试覆盖（83个测试用例），优化代码结构和可维护性"
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
            "80级深红凝珠",
            "65级扼守",
            "60级皎皎币（待完善）"
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
            "请在16:9的1920x1080分辨率下使用",
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
