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
        self.current_version = "v1.1.0"
        self.release_date = "2026-03-07"
        
        # 版本更新日志
        self.update_logs = [
            UpdateLog(
                version="v1.1.0",
                date="2026-03-07",
                changes=[
                    "改回放多线程为多进程",
                    "优化脚本导入,现在可以自动加载scripts文件夹中的脚本",
                    "优化脚本逻辑和命名",
                    "优化了代码结构",
                    "完善了错误处理机制",
                    "在 base_automation.py 中实现通用游戏循环方法",
                    "模板图片缓存 - 避免重复加载同一模板图片，减少文件I/O和图像解码开销",
                    "屏幕截图缓存 - 短时间内多次查找使用同一张截图，减少频繁截图操作",
                    "内存管理 - 停止时自动清理缓存，释放内存资源",
                    "优化配置相关代码",
                    "优化了日志记录机制",
                    "资源管理优化 - InputRecorder和RecordingManager支持上下文管理器",
                    "添加类型注解 - 提高代码可读性和维护性",
                    "UI响应性优化"

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
