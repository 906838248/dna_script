from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

DARK_THEME = """
/* 全局样式 */
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
}

/* 主窗口 */
QMainWindow {
    background-color: #1e1e2e;
}

/* GroupBox样式 */
QGroupBox {
    background-color: #262638;
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
    color: #cba6f7;
    font-size: 16px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px 0 8px;
}

/* 按钮样式 */
QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
    min-width: 60px;
    font-size: 11px;
}

QPushButton:hover {
    background-color: #585b70;
}

QPushButton:pressed {
    background-color: #313244;
}

QPushButton:disabled {
    background-color: #313244;
    color: #6c7086;
}

/* 开始按钮 */
QPushButton#startButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #a6e3a1, stop:1 #94e2d5);
    color: #1e1e2e;
    font-weight: bold;
}

QPushButton#startButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #b6f3b1, stop:1 #a4f2e5);
}

QPushButton#startButton:disabled {
    background: #313244;
    color: #6c7086;
}

/* 停止按钮 */
QPushButton#stopButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f38ba8, stop:1 #eba0ac);
    color: #1e1e2e;
    font-weight: bold;
}

QPushButton#stopButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ff9bb8, stop:1 #fbb0bc);
}

QPushButton#stopButton:disabled {
    background: #313244;
    color: #6c7086;
}

/* 录制按钮 */
QPushButton#recordButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f9e2af, stop:1 #fab387);
    color: #1e1e2e;
    font-weight: bold;
}

QPushButton#recordButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #fff2bf, stop:1 #fec397);
}

QPushButton#recordButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #e9d29f, stop:1 #eaa377);
}

/* 标签样式 */
QLabel {
    color: #cdd6f4;
    padding: 4px;
    font-size: 16px;
}

QLabel#descriptionLabel {
    color: #a6adc8;
    font-style: italic;
    padding: 8px;
    font-size: 15px;
}

QLabel#progressLabel {
    color: #89b4fa;
    font-weight: bold;
    font-size: 16px;
}

/* 下拉框样式 */
QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 24px;
    font-size: 10pt;
}

QComboBox:hover {
    border: 1px solid #585b70;
}

QComboBox:focus {
    border: 1px solid #cba6f7;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 24px;
    border-left: 1px solid #45475a;
    border-radius: 0 6px 6px 0;
    background-color: #313244;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #cdd6f4;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    selection-background-color: #45475a;
    selection-color: #cdd6f4;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    min-height: 24px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #45475a;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #585b70;
}

/* LineEdit样式 */
QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 24px;
    font-size: 14px;
}

QLineEdit:hover {
    border: 1px solid #585b70;
}

QLineEdit:focus {
    border: 1px solid #cba6f7;
}

QLineEdit:disabled {
    background-color: #1e1e2e;
    color: #6c7086;
}

/* RadioButton样式 */
QRadioButton {
    background-color: transparent;
    color: #cdd6f4;
    spacing: 8px;
    font-size: 14px;
}

QRadioButton:hover {
    color: #cdd6f4;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #45475a;
    border-radius: 9px;
    background-color: #1e1e2e;
}

QRadioButton::indicator:hover {
    border: 2px solid #585b70;
}

QRadioButton::indicator:checked {
    background-color: #cba6f7;
    border: 2px solid #cba6f7;
}

QRadioButton::indicator:checked:hover {
    background-color: #d7b6f7;
    border: 2px solid #d7b6f7;
}

/* SpinBox样式 */
QSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px;
    min-height: 24px;
    font-size: 14px;
}

QSpinBox:hover {
    border: 1px solid #585b70;
}

QSpinBox:focus {
    border: 1px solid #cba6f7;
}

QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border: none;
    border-left: 1px solid #45475a;
    border-radius: 0 6px 0 0;
    background-color: #313244;
    padding: 2px;
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border: none;
    border-left: 1px solid #45475a;
    border-top: 1px solid #45475a;
    border-radius: 0 0 6px 0;
    background-color: #313244;
    padding: 2px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #45475a;
}

QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
    background-color: #585b70;
}

QSpinBox::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #cdd6f4;
    width: 0;
    height: 0;
}

QSpinBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #cdd6f4;
    width: 0;
    height: 0;
}

/* 文本编辑框样式 */
QTextEdit {
    background-color: #181825;
    color: #a6adc8;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}

QTextEdit:focus {
    border: 1px solid #cba6f7;
}

/* 滚动条样式 */
QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1e1e2e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #585b70;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* 消息框样式 */
QMessageBox {
    background-color: #1e1e2e;
}

QMessageBox QLabel {
    color: #cdd6f4;
    min-width: 300px;
    font-size: 14px;
}

QMessageBox QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border-radius: 6px;
    padding: 8px 24px;
    font-weight: 600;
    font-size: 14px;
}

QMessageBox QPushButton:hover {
    background-color: #585b70;
}
"""

def apply_dark_theme(app):
    app.setStyleSheet(DARK_THEME)
    font = app.font()
    font.setFamily('Microsoft YaHei UI')
    font.setPointSize(12)
    app.setFont(font)
