import sys
import os
import time
import keyboard
import threading
import importlib.util
import inspect
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QSpinBox, 
                               QTextEdit, QMessageBox, QGroupBox, QComboBox, 
                               QTabWidget, QLineEdit, QFileDialog, QRadioButton, 
                               QButtonGroup, QCheckBox)
from PySide6.QtCore import Qt, QMetaObject, Slot
from PySide6.QtGui import QFont

from src.styles import apply_dark_theme
from src.input_recorder import InputRecorder, RecordingManager
from src.version_info import version_manager
from src.config_manager import config_manager
from src.shortcut_manager import shortcut_manager, ShortcutAction
from src.base_automation import BaseAutomationThread



class ScriptInfo:
    """
    脚本信息类
    用于存储脚本的元数据信息
    """
    def __init__(self, name, description, script_class, img_folder):
        """
        初始化脚本信息
        
        Args:
            name: 脚本名称
            description: 脚本描述
            script_class: 脚本类
            img_folder: 图片文件夹路径
        """
        self.name = name
        self.description = description
        self.script_class = script_class
        self.img_folder = img_folder

class MainWindow(QMainWindow):
    """
    主窗口类
    游戏自动化脚本管理器的主界面
    提供脚本选择、控制、录制和日志显示等功能
    """
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.setWindowTitle("二重螺旋 - 统一脚本管理器")
        self.setGeometry(100, 100, 410, 550) # 窗口大小
        self.setMinimumWidth(350) # 最小宽度，防止窗口过于窄
        self.automation_thread = None  # 自动化线程
        # 获取项目根目录（main.py所在目录）
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 自动加载scripts文件夹中的脚本
        self.scripts = self.auto_load_scripts()
        
        self.current_script = None  # 当前选中的脚本
        self.is_recording = False  # 是否正在录制
        self.recorder = InputRecorder()  # 录制器
        self.recording_manager = RecordingManager()  # 录制管理器
        self.init_ui()
        self.load_saved_config()

    def auto_load_scripts(self):
        """
        自动加载scripts文件夹中的所有脚本
        
        Returns:
            list: ScriptInfo对象列表
        """
        scripts = []
        scripts_dir = os.path.join(self.script_dir, "scripts")
        
        if not os.path.exists(scripts_dir):
            print(f"警告: scripts文件夹不存在: {scripts_dir}")
            return scripts
        
        for file_path in Path(scripts_dir).glob("script_*.py"):
            if file_path.name == "__init__.py":
                continue
            
            try:
                spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseAutomationThread) and 
                            obj != BaseAutomationThread and
                            hasattr(obj, 'SCRIPT_NAME')):
                            
                            script_name = getattr(obj, 'SCRIPT_NAME')
                            script_description = getattr(obj, 'SCRIPT_DESCRIPTION', '')
                            script_img_folder = getattr(obj, 'SCRIPT_IMG_FOLDER', '')
                            
                            scripts.append(ScriptInfo(
                                script_name,
                                script_description,
                                obj,
                                os.path.join(self.script_dir, script_img_folder)
                            ))
                            
                            print(f"已加载脚本: {script_name}")
            except Exception as e:
                print(f"加载脚本失败 {file_path.name}: {str(e)}")
        
        return scripts

    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        
        # 创建各个标签页
        self.create_automation_tab()
        self.create_recording_tab()
        self.create_log_tab()
        self.create_shortcut_tab()
        self.create_version_tab()
        
        # 底部信息区域
        bottom_layout = self.create_bottom_section()
        
        # 添加到主布局
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(bottom_layout)
        
        central_widget.setLayout(main_layout)
        
        self.log("游戏自动化脚本管理器已启动")
        self.log("选择脚本后点击开始按钮或按F5键启动")

    def create_automation_tab(self):
        """创建自动化脚本标签页"""
        automation_widget = QWidget()
        automation_layout = QVBoxLayout()
        
        # 脚本选择区域
        script_group = QGroupBox("脚本选择")
        script_layout = QVBoxLayout()
        
        script_select_layout = QHBoxLayout()
        script_label = QLabel("选择脚本:")
        self.script_combo = QComboBox()
        for script in self.scripts:
            self.script_combo.addItem(script.name, script)
        self.script_combo.currentIndexChanged.connect(self.on_script_changed)
        
        script_select_layout.addWidget(script_label)
        script_select_layout.addWidget(self.script_combo)
        
        self.script_description = QLabel()
        self.script_description.setObjectName("descriptionLabel")
        self.update_script_description()
        
        script_layout.addLayout(script_select_layout)
        script_layout.addWidget(self.script_description)
        script_group.setLayout(script_layout)
        
        # 控制面板区域
        control_group = QGroupBox("控制面板")
        control_layout = QHBoxLayout()
        control_layout.setSpacing(5)
        
        loop_label = QLabel("循环次数:")
        self.loop_spinbox = QSpinBox()
        self.loop_spinbox.setMinimum(1)
        self.loop_spinbox.setMaximum(9999)
        self.loop_spinbox.setValue(config_manager.get_last_loop_count())
        self.loop_spinbox.valueChanged.connect(self.on_loop_count_changed)
        
        self.start_button = QPushButton("开始")
        self.start_button.setObjectName("startButton")
        self.start_button.setFixedSize(60, 28)
        self.start_button.clicked.connect(self.start_automation)
        
        self.stop_button = QPushButton("停止")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setFixedSize(60, 28)
        self.stop_button.clicked.connect(self.stop_automation)
        self.stop_button.setEnabled(False)
        
        control_layout.addWidget(loop_label)
        control_layout.addWidget(self.loop_spinbox)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_group.setLayout(control_layout)
        
        # 自动跳转日志选项
        auto_switch_layout = QHBoxLayout()
        self.auto_switch_checkbox = QCheckBox("自动跳转到日志")
        self.auto_switch_checkbox.setChecked(False)
        self.auto_switch_checkbox.stateChanged.connect(self.on_auto_switch_changed)
        auto_switch_layout.addWidget(self.auto_switch_checkbox)
        
        # 进度显示
        progress_group = QGroupBox("进度")
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel("进度: 0 / 0")
        self.progress_label.setObjectName("progressLabel")
        progress_layout.addWidget(self.progress_label)
        progress_group.setLayout(progress_layout)
        
        # 添加到自动化标签页布局
        automation_layout.addWidget(script_group)
        automation_layout.addWidget(control_group)
        automation_layout.addLayout(auto_switch_layout)
        automation_layout.addWidget(progress_group)
        automation_layout.addStretch()
        
        automation_widget.setLayout(automation_layout)
        self.tab_widget.addTab(automation_widget, "自动化脚本")

    def create_recording_tab(self):
        """创建录制功能标签页"""
        recording_widget = QWidget()
        recording_layout = QVBoxLayout()
        
        # 录制名称输入
        recording_name_group = QGroupBox("录制名称")
        recording_name_layout = QHBoxLayout()
        self.recording_name_input = QLineEdit()
        self.recording_name_input.setPlaceholderText("输入录制名称")
        recording_name_layout.addWidget(self.recording_name_input)
        recording_name_group.setLayout(recording_name_layout)
        
        # 鼠标模式选择
        recording_mode_group = QGroupBox("鼠标模式")
        recording_mode_layout = QHBoxLayout()
        recording_mode_label = QLabel("模式:")
        self.mouse_mode_group = QButtonGroup()
        self.mouse_mode_absolute = QRadioButton("绝对坐标")
        self.mouse_mode_relative = QRadioButton("相对坐标")
        self.mouse_mode_absolute.setChecked(True)
        self.mouse_mode_group.addButton(self.mouse_mode_absolute, 0)
        self.mouse_mode_group.addButton(self.mouse_mode_relative, 1)
        recording_mode_layout.addWidget(recording_mode_label)
        recording_mode_layout.addWidget(self.mouse_mode_absolute)
        recording_mode_layout.addWidget(self.mouse_mode_relative)
        recording_mode_group.setLayout(recording_mode_layout)
        
        # 最小移动距离设置
        recording_threshold_group = QGroupBox("最小移动距离")
        recording_threshold_layout = QHBoxLayout()
        self.mouse_threshold_spinbox = QSpinBox()
        self.mouse_threshold_spinbox.setMinimum(1)
        self.mouse_threshold_spinbox.setMaximum(1000)
        self.mouse_threshold_spinbox.setValue(3)
        recording_threshold_layout.addWidget(self.mouse_threshold_spinbox)
        recording_threshold_group.setLayout(recording_threshold_layout)
        
        # 录制操作按钮
        recording_buttons_group = QGroupBox("操作")
        recording_buttons_layout = QVBoxLayout()
        recording_buttons_layout.setSpacing(5)
        
        # 第一行按钮
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(5)
        self.record_button = QPushButton("录制")
        self.record_button.setObjectName("recordButton")
        self.record_button.setFixedSize(60, 28)
        self.record_button.clicked.connect(self.toggle_recording)
        
        self.save_recording_button = QPushButton("保存")
        self.save_recording_button.setFixedSize(60, 28)
        self.save_recording_button.clicked.connect(self.save_recording)
        
        self.load_recording_button = QPushButton("加载")
        self.load_recording_button.setFixedSize(60, 28)
        self.load_recording_button.clicked.connect(self.load_recording)
        
        first_row_layout.addWidget(self.record_button)
        first_row_layout.addWidget(self.save_recording_button)
        first_row_layout.addWidget(self.load_recording_button)
        first_row_layout.addStretch()
        
        # 第二行按钮
        second_row_layout = QHBoxLayout()
        second_row_layout.setSpacing(5)
        self.play_recording_button = QPushButton("回放")
        self.play_recording_button.setFixedSize(60, 28)
        self.play_recording_button.clicked.connect(self.play_recording)
        
        self.stop_playback_button = QPushButton("停止")
        self.stop_playback_button.setFixedSize(60, 28)
        self.stop_playback_button.clicked.connect(self.stop_playback_ui)
        self.stop_playback_button.setEnabled(False)
        
        second_row_layout.addWidget(self.play_recording_button)
        second_row_layout.addWidget(self.stop_playback_button)
        second_row_layout.addStretch()
        
        recording_buttons_layout.addLayout(first_row_layout)
        recording_buttons_layout.addLayout(second_row_layout)
        recording_buttons_group.setLayout(recording_buttons_layout)
        
        # 录制状态显示
        recording_status_group = QGroupBox("状态")
        recording_status_layout = QHBoxLayout()
        self.recording_status_label = QLabel("状态: 未录制")
        self.recording_count_label = QLabel("操作数: 0")
        recording_status_layout.addWidget(self.recording_status_label)
        recording_status_layout.addWidget(self.recording_count_label)
        recording_status_group.setLayout(recording_status_layout)
        
        # 添加到录制标签页布局
        recording_layout.addWidget(recording_name_group)
        recording_layout.addWidget(recording_mode_group)
        recording_layout.addWidget(recording_threshold_group)
        recording_layout.addWidget(recording_buttons_group)
        recording_layout.addWidget(recording_status_group)
        recording_layout.addStretch()
        
        recording_widget.setLayout(recording_layout)
        self.tab_widget.addTab(recording_widget, "录制功能")

    def create_log_tab(self):
        """创建日志标签页"""
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        
        # 运行日志
        log_group = QGroupBox("运行日志")
        log_inner_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_inner_layout.addWidget(self.log_text)
        log_group.setLayout(log_inner_layout)
        
        # 清空日志按钮
        clear_button_layout = QHBoxLayout()
        clear_button_layout.addStretch()
        self.clear_log_button = QPushButton("清空")
        self.clear_log_button.setFixedSize(60, 28)
        self.clear_log_button.clicked.connect(self.clear_log)
        clear_button_layout.addWidget(self.clear_log_button)
        
        log_layout.addWidget(log_group)
        log_layout.addLayout(clear_button_layout)
        
        log_widget.setLayout(log_layout)
        self.tab_widget.addTab(log_widget, "日志")

    def create_shortcut_tab(self):
        """创建快捷键设置标签页"""
        shortcut_widget = QWidget()
        shortcut_layout = QVBoxLayout()
        
        # 快捷键设置
        shortcut_group = QGroupBox("快捷键设置")
        shortcut_inner_layout = QVBoxLayout()
        
        self.shortcut_inputs = {}
        
        for action in [
            ShortcutAction.START_AUTOMATION,
            ShortcutAction.STOP_AUTOMATION,
            ShortcutAction.CLEAR_LOG,
            ShortcutAction.TOGGLE_RECORDING,
            ShortcutAction.STOP_RECORDING_PLAYBACK
        ]:
            action_layout = QHBoxLayout()
            action_label = QLabel(shortcut_manager.get_shortcut_description(action))
            action_label.setMinimumWidth(100)
            
            shortcut_input = QLineEdit()
            shortcut_input.setText(shortcut_manager.get_shortcut(action))
            shortcut_input.setMaximumWidth(80)
            self.shortcut_inputs[action] = shortcut_input
            
            action_layout.addWidget(action_label)
            action_layout.addWidget(shortcut_input)
            shortcut_inner_layout.addLayout(action_layout)
        
        shortcut_buttons_layout = QHBoxLayout()
        shortcut_buttons_layout.setSpacing(5)
        
        save_shortcut_button = QPushButton("保存")
        save_shortcut_button.setFixedSize(60, 28)
        save_shortcut_button.clicked.connect(self.save_shortcuts)
        shortcut_buttons_layout.addWidget(save_shortcut_button)
        
        reset_shortcut_button = QPushButton("重置")
        reset_shortcut_button.setFixedSize(60, 28)
        reset_shortcut_button.clicked.connect(self.reset_shortcuts)
        shortcut_buttons_layout.addWidget(reset_shortcut_button)
        
        shortcut_inner_layout.addLayout(shortcut_buttons_layout)
        shortcut_group.setLayout(shortcut_inner_layout)
        
        # 添加到快捷键标签页布局
        shortcut_layout.addWidget(shortcut_group)
        shortcut_layout.addStretch()
        
        shortcut_widget.setLayout(shortcut_layout)
        self.tab_widget.addTab(shortcut_widget, "快捷键设置")

    def create_version_tab(self):
        """创建版本说明标签页"""
        from PySide6.QtWidgets import QScrollArea
        
        version_widget = QWidget()
        version_layout = QVBoxLayout()
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 滚动区域的内容容器
        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout()
        
        # 版本信息
        version_info_group = QGroupBox("版本信息")
        version_info_layout = QVBoxLayout()
        
        version_info = version_manager.get_current_version()
        
        version_label = QLabel(version_info.description)
        version_label.setFont(QFont("Arial", 14, QFont.Bold))
        version_label.setAlignment(Qt.AlignCenter)
        
        version_number_label = QLabel(f"版本: {version_info.version}")
        version_number_label.setFont(QFont("Arial", 10))
        version_number_label.setAlignment(Qt.AlignCenter)
        
        version_date_label = QLabel(f"发布日期: {version_info.date}")
        version_date_label.setFont(QFont("Arial", 9))
        version_date_label.setAlignment(Qt.AlignCenter)
        
        version_info_layout.addWidget(version_label)
        version_info_layout.addWidget(version_number_label)
        version_info_layout.addWidget(version_date_label)
        version_info_group.setLayout(version_info_layout)
        
        # 最新更新日志
        latest_update_log_group = QGroupBox("最新更新")
        latest_update_log_layout = QVBoxLayout()
        
        latest_update_log_text = QLabel()
        latest_update_log_text.setWordWrap(True)
        latest_update_log_text.setText(version_manager.format_latest_update_log())
        latest_update_log_layout.addWidget(latest_update_log_text)
        latest_update_log_group.setLayout(latest_update_log_layout)
        
        # 历史更新日志（默认隐藏）
        self.historical_update_log_group = QGroupBox("历史更新")
        historical_update_log_layout = QVBoxLayout()
        
        self.historical_update_log_text = QLabel()
        self.historical_update_log_text.setWordWrap(True)
        self.historical_update_log_text.setText(version_manager.format_historical_update_logs())
        historical_update_log_layout.addWidget(self.historical_update_log_text)
        self.historical_update_log_group.setLayout(historical_update_log_layout)
        self.historical_update_log_group.setVisible(False)
        
        # 展开/折叠按钮
        self.toggle_history_button = QPushButton("查看历史更新")
        self.toggle_history_button.setFixedSize(90, 28)
        self.toggle_history_button.clicked.connect(self.toggle_history_updates)
        
        # 支持的脚本
        scripts_group = QGroupBox("支持的脚本")
        scripts_layout = QVBoxLayout()
        
        scripts_text = QLabel("\n".join(f"• {script}" for script in version_manager.get_supported_scripts()))
        scripts_layout.addWidget(scripts_text)
        scripts_group.setLayout(scripts_layout)
        
        # 使用说明
        usage_group = QGroupBox("使用说明")
        usage_layout = QVBoxLayout()
        
        usage_text = QLabel("\n".join(f"{i}. {guide}" for i, guide in enumerate(version_manager.get_usage_guide(), 1)))
        usage_text.setWordWrap(True)
        usage_layout.addWidget(usage_text)
        usage_group.setLayout(usage_layout)
        
        # 注意事项
        notice_group = QGroupBox("注意事项")
        notice_layout = QVBoxLayout()
        
        notice_text = QLabel("\n".join(f"• {notice}" for notice in version_manager.get_notices()))
        notice_text.setWordWrap(True)
        notice_layout.addWidget(notice_text)
        notice_group.setLayout(notice_layout)
        
        # 添加到滚动内容布局        
        scroll_content_layout.addWidget(version_info_group)
        scroll_content_layout.addWidget(latest_update_log_group)
        scroll_content_layout.addWidget(self.toggle_history_button)
        scroll_content_layout.addWidget(self.historical_update_log_group)
        scroll_content_layout.addWidget(scripts_group)
        scroll_content_layout.addWidget(usage_group)
        scroll_content_layout.addWidget(notice_group)
        scroll_content_layout.addStretch()
        
        scroll_content.setLayout(scroll_content_layout)
        scroll_area.setWidget(scroll_content)
        
        # 添加到版本标签页布局
        version_layout.addWidget(scroll_area)
        
        version_widget.setLayout(version_layout)
        self.tab_widget.addTab(version_widget, "版本说明")

    def toggle_history_updates(self):
        """切换历史更新的显示/隐藏状态"""
        if self.historical_update_log_group.isVisible():
            self.historical_update_log_group.setVisible(False)
            self.toggle_history_button.setText("查看历史更新")
        else:
            self.historical_update_log_group.setVisible(True)
            self.toggle_history_button.setText("收起历史更新")
    
    def create_bottom_section(self):
        """创建底部信息区域"""
        bottom_layout = QHBoxLayout()
        
        return bottom_layout

    def load_saved_config(self):
        """加载保存的配置"""
        last_script = config_manager.get_last_selected_script()
        if last_script:
            for i in range(self.script_combo.count()):
                script = self.script_combo.itemData(i)
                if script and script.name == last_script:
                    self.script_combo.setCurrentIndex(i)
                    break
        
        last_recording_name = config_manager.get_last_recording_name()
        if last_recording_name:
            self.recording_name_input.setText(last_recording_name)
        
        auto_switch_to_log = config_manager.get_auto_switch_to_log()
        self.auto_switch_checkbox.setChecked(auto_switch_to_log)
        
        self.log("已加载上次保存的配置")
        
        # 先注册快捷键回调函数
        self.setup_shortcuts()
        
        # 加载保存的快捷键配置
        saved_shortcuts = config_manager.get_shortcuts()
        if saved_shortcuts:
            shortcut_manager.set_all_shortcuts(saved_shortcuts)
            shortcut_manager.setup_hotkeys()
            self.log("已加载快捷键配置")
            
            # 更新快捷键输入框的显示
            if hasattr(self, 'shortcut_inputs'):
                for action, input_field in self.shortcut_inputs.items():
                    input_field.setText(shortcut_manager.get_shortcut(action))
        else:
            # 如果没有保存的快捷键配置，使用默认值
            shortcut_manager.setup_hotkeys()

    def save_shortcuts(self):
        """保存快捷键设置"""
        shortcuts = {}
        for action, input_field in self.shortcut_inputs.items():
            shortcut = input_field.text().strip()
            if shortcut_manager._validate_shortcut(shortcut):
                shortcuts[action.value] = shortcut
            else:
                QMessageBox.warning(self, "警告", f"快捷键 '{shortcut}' 无效！")
                return
        
        if shortcut_manager.set_all_shortcuts(shortcuts):
            config_manager.set_shortcuts(shortcuts)
            shortcut_manager.setup_hotkeys()
            QMessageBox.information(self, "成功", "快捷键设置已保存！")
            self.log("快捷键设置已保存")
        else:
            QMessageBox.warning(self, "警告", "快捷键设置保存失败！")
    
    def reset_shortcuts(self):
        """重置快捷键为默认值"""
        reply = QMessageBox.question(self, "确认", "确定要重置所有快捷键为默认值吗？",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            shortcut_manager.reset_to_default()
            config_manager.set_shortcuts(shortcut_manager.get_all_shortcuts())
            shortcut_manager.setup_hotkeys()
            
            for action, input_field in self.shortcut_inputs.items():
                input_field.setText(shortcut_manager.get_shortcut(action))
            
            QMessageBox.information(self, "成功", "快捷键已重置为默认值！")
            self.log("快捷键已重置为默认值")

    def setup_shortcuts(self):
        """设置全局快捷键"""
        # 注册快捷键回调函数
        shortcut_manager.register_callback(
            ShortcutAction.START_AUTOMATION,
            lambda: QMetaObject.invokeMethod(self, "start_automation", Qt.QueuedConnection)
        )
        shortcut_manager.register_callback(
            ShortcutAction.STOP_AUTOMATION,
            lambda: QMetaObject.invokeMethod(self, "stop_automation", Qt.QueuedConnection)
        )
        shortcut_manager.register_callback(
            ShortcutAction.CLEAR_LOG,
            lambda: QMetaObject.invokeMethod(self, "clear_log", Qt.QueuedConnection)
        )
        shortcut_manager.register_callback(
            ShortcutAction.TOGGLE_RECORDING,
            lambda: QMetaObject.invokeMethod(self, "toggle_recording", Qt.QueuedConnection)
        )
        
        # ESC键根据当前状态执行不同操作
        def on_esc():
            if self.is_recording:
                QMetaObject.invokeMethod(self, "stop_recording_ui", Qt.QueuedConnection)
            elif self.recorder.is_playing:
                QMetaObject.invokeMethod(self, "stop_playback_ui", Qt.QueuedConnection)
        
        shortcut_manager.register_callback(ShortcutAction.STOP_RECORDING_PLAYBACK, on_esc)
        
        # 设置所有快捷键
        shortcut_manager.setup_hotkeys()

    def on_script_changed(self, index):
        """脚本选择改变时的回调函数"""
        self.update_script_description()
        script = self.script_combo.currentData()
        if script:
            config_manager.set_last_selected_script(script.name)
    
    def on_loop_count_changed(self, value):
        """循环次数改变时的回调函数"""
        config_manager.set_last_loop_count(value)
    
    def on_auto_switch_changed(self, state):
        """自动跳转选项改变时的回调函数"""
        is_checked = state == 2
        config_manager.set_auto_switch_to_log(is_checked)

    def update_script_description(self):
        """更新脚本描述显示"""
        script = self.script_combo.currentData()
        if script:
            self.script_description.setText(f"描述: {script.description}")

    def log(self, message):
        """
        添加日志消息
        
        Args:
            message: 日志消息内容
        """
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # 只在日志标签页可见时自动滚动
        if self.tab_widget.currentIndex() == 2:
            self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    @Slot()
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()

    @Slot()
    def start_automation(self):
        """开始自动化脚本"""
        if self.automation_thread and self.automation_thread.isRunning():
            QMessageBox.warning(self, "警告", "自动化正在运行中！")
            return
        
        script = self.script_combo.currentData()
        if not script:
            QMessageBox.warning(self, "警告", "请先选择一个脚本！")
            return
        
        loop_count = self.loop_spinbox.value()
        self.log(f"\n开始执行脚本: {script.name}")
        self.log(f"循环次数: {loop_count}")
        
        # 更新UI状态
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.loop_spinbox.setEnabled(False)
        self.script_combo.setEnabled(False)
        
        # 创建并启动自动化线程
        self.current_script = script
        self.automation_thread = script.script_class(loop_count, script.img_folder)
        self.automation_thread.log_signal.connect(self.log)
        self.automation_thread.finished_signal.connect(self.on_automation_finished)
        self.automation_thread.progress_signal.connect(self.update_progress)
        self.automation_thread.start()
        
        # 如果勾选了自动跳转，则跳转到日志页面
        if self.auto_switch_checkbox.isChecked():
            self.tab_widget.setCurrentIndex(2)

    @Slot()
    def stop_automation(self):
        """停止自动化脚本"""
        if self.automation_thread and self.automation_thread.isRunning():
            self.log("正在停止自动化...")
            self.automation_thread.stop()
            self.automation_thread.wait()
            self.log("自动化已停止")

    @Slot()
    def on_automation_finished(self):
        """自动化完成时的回调函数"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.loop_spinbox.setEnabled(True)
        self.script_combo.setEnabled(True)

    @Slot()
    def update_progress(self, current, total):
        """
        更新进度显示
        
        Args:
            current: 当前进度
            total: 总进度
        """
        self.progress_label.setText(f"进度: {current} / {total}")

    @Slot()
    def toggle_recording(self):
        """切换录制状态"""
        if self.is_recording:
            self.stop_recording_ui()
        else:
            self.start_recording_ui()

    @Slot()
    def start_recording_ui(self):
        """开始录制"""
        if self.is_recording:
            return
        
        # 获取录制参数
        mouse_mode = 'relative' if self.mouse_mode_relative.isChecked() else 'absolute'
        min_mouse_move = self.mouse_threshold_spinbox.value()
        self.recorder = InputRecorder(mouse_mode=mouse_mode, min_mouse_move=min_mouse_move)
        
        # 更新UI状态
        self.is_recording = True
        self.record_button.setText("停止")
        self.recording_status_label.setText("状态: 录制中...")
        self.log(f"开始录制键盘和鼠标操作 (模式: {'相对坐标' if mouse_mode == 'relative' else '绝对坐标'}, 最小移动: {min_mouse_move}px)")
        
        # 开始录制
        self.recorder.start_recording()

    @Slot()
    def stop_recording_ui(self):
        """停止录制"""
        if not self.is_recording:
            return
        
        # 先停止录制，避免录制到停止按钮的点击事件
        self.recorder.stop_recording()
        
        # 更新UI状态
        self.is_recording = False
        self.record_button.setText("录制")
        self.recording_status_label.setText("状态: 已停止")
        self.log("停止录制")
        self.recording_count_label.setText(f"操作数: {self.recorder.get_action_count()}")

    @Slot()
    def save_recording(self):
        """保存录制到文件"""
        name = self.recording_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入录制名称！")
            return
        
        if self.recorder.get_action_count() == 0:
            QMessageBox.warning(self, "警告", "没有可保存的录制！")
            return
        
        self.recorder.save_to_file(self.recording_manager.get_recording_path(name))
        self.log(f"录制已保存: {name}")
        self.recording_status_label.setText(f"状态: 已保存 ({name})")
        config_manager.set_last_recording_name(name)

    @Slot()
    def load_recording(self):
        """从文件加载录制"""
        name = self.recording_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入录制名称！")
            return
        
        filepath = self.recording_manager.get_recording_path(name)
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "警告", f"录制文件不存在: {name}")
            return
        
        self.recorder.load_from_file(filepath)
        self.log(f"已加载录制: {name} ({self.recorder.get_action_count()} 个操作)")
        self.recording_status_label.setText(f"状态: 已加载 ({name})")
        self.recording_count_label.setText(f"操作数: {self.recorder.get_action_count()}")

    @Slot()
    def play_recording(self):
        """回放录制"""
        if self.recorder.get_action_count() == 0:
            QMessageBox.warning(self, "警告", "请先加载录制！")
            return
        
        if self.recorder.is_playing:
            QMessageBox.warning(self, "警告", "回放正在进行中！")
            return
        
        self.log("开始回放录制")
        self.recording_status_label.setText("状态: 回放中...")
        self.play_recording_button.setEnabled(False)
        self.stop_playback_button.setEnabled(True)
        
        # 在新线程中回放
        def playback_worker():
            self.recorder.play_recording(speed_multiplier=1.0)
            time.sleep(0.1)
            QMetaObject.invokeMethod(self, "on_playback_finished", Qt.QueuedConnection)
        
        playback_thread = threading.Thread(target=playback_worker)
        playback_thread.daemon = True
        playback_thread.start()
    
    @Slot()
    def on_playback_finished(self):
        """回放完成时的回调函数"""
        if self.recorder.is_playing:
            return
        self.recording_status_label.setText("状态: 回放完成")
        self.play_recording_button.setEnabled(True)
        self.stop_playback_button.setEnabled(False)
        self.log("回放录制完成")

    @Slot()
    def stop_playback_ui(self):
        """停止回放"""
        if not self.recorder.is_playing:
            return
        
        self.log("停止回放")
        self.recorder.stop_playback()
        self.recording_status_label.setText("状态: 回放已停止")
        self.play_recording_button.setEnabled(True)
        self.stop_playback_button.setEnabled(False)

    def closeEvent(self, event):
        """
        窗口关闭事件处理
        清理所有资源
        """
        keyboard.unhook_all()
        
        # 停止录制
        if self.is_recording:
            self.recorder.stop_recording()
        
        # 停止回放
        if self.recorder.is_playing:
            self.recorder.stop_playback()
        
        # 停止自动化线程
        if self.automation_thread and self.automation_thread.isRunning():
            self.automation_thread.stop()
            self.automation_thread.wait()
        event.accept()

if __name__ == "__main__":
    import multiprocessing
    
    # 设置多进程启动方式为spawn，避免Windows平台的问题
    multiprocessing.set_start_method('spawn', force=True)
    
    import ctypes
    
    # Windows平台DPI感知设置
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass
    
    # 创建并显示主窗口
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
