"""
翻译输入助手 - 悬浮输入窗口
Translation Input Helper - Floating Input Window

功能：
- Ctrl+Space 全局热键唤起
- 用户输入中文 → 实时翻译
- Enter 粘贴翻译结果到目标窗口
- Esc 取消关闭
"""

import sys
import ctypes
import threading
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QApplication,
    QGraphicsDropShadowEffect, QShortcut
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import QFont, QColor, QKeySequence

# Windows API
user32 = ctypes.windll.user32


class FloatingInputWindow(QWidget):
    """悬浮输入窗口"""
    
    # 信号
    translate_requested = pyqtSignal(str)  # 请求翻译
    paste_requested = pyqtSignal(str)       # 请求粘贴结果
    closed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._target_hwnd = None  # 记录目标窗口
        self._current_translation = ""
        self._translating = False
        self._init_ui()
        self._setup_shortcuts()
        
    def _init_ui(self):
        """初始化UI"""
        # 窗口属性
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(500)
        
        # 主容器
        container = QWidget(self)
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background-color: #1e1e2e;
                border-radius: 12px;
                border: 1px solid #45475a;
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        container.setGraphicsEffect(shadow)
        
        # 布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        title = QLabel("⌨️ 翻译输入助手")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #89b4fa;
            font-family: "Microsoft YaHei", "Segoe UI";
        """)
        title_layout.addWidget(title)
        
        hint = QLabel("Enter=粘贴 | Esc=取消")
        hint.setStyleSheet("""
            font-size: 11px;
            color: #6c7086;
            font-family: "Microsoft YaHei", "Segoe UI";
        """)
        title_layout.addWidget(hint, 0, Qt.AlignRight)
        
        layout.addLayout(title_layout)
        
        # 输入框
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("输入中文...")
        self.input_edit.setStyleSheet("""
            QLineEdit {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                color: #f5e0dc;
                font-family: "Microsoft YaHei", "Segoe UI";
            }
            QLineEdit:focus {
                border: 2px solid #89b4fa;
            }
        """)
        self.input_edit.textChanged.connect(self._on_text_changed)
        self.input_edit.returnPressed.connect(self._on_enter_pressed)
        layout.addWidget(self.input_edit)
        
        # 翻译结果
        self.result_label = QLabel("翻译结果将显示在这里...")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #313244;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #94e2d5;
                font-family: "Microsoft YaHei", "Segoe UI";
                min-height: 40px;
            }
        """)
        layout.addWidget(self.result_label)
        
        # 状态栏
        self.status_label = QLabel("💡 按 Ctrl+Space 随时唤起")
        self.status_label.setStyleSheet("""
            font-size: 11px;
            color: #6c7086;
            font-family: "Microsoft YaHei", "Segoe UI";
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 翻译延迟计时器
        self._translate_timer = QTimer()
        self._translate_timer.setSingleShot(True)
        self._translate_timer.timeout.connect(self._do_translate)
        
    def _setup_shortcuts(self):
        """设置快捷键"""
        # Esc 关闭
        esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc.activated.connect(self._on_escape)
        
    def _on_text_changed(self, text):
        """文本变化 - 延迟翻译"""
        self._translate_timer.stop()
        if text.strip():
            self.result_label.setText("⏳ 翻译中...")
            self.result_label.setStyleSheet("""
                QLabel {
                    background-color: #313244;
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-size: 14px;
                    color: #6c7086;
                    font-family: "Microsoft YaHei", "Segoe UI";
                    min-height: 40px;
                }
            """)
            # 延迟 500ms 翻译（避免频繁请求）
            self._translate_timer.start(500)
        else:
            self.result_label.setText("翻译结果将显示在这里...")
            self._current_translation = ""
            
    def _do_translate(self):
        """执行翻译"""
        text = self.input_edit.text().strip()
        if text:
            self.translate_requested.emit(text)
            
    def show_translation(self, translation: str):
        """显示翻译结果"""
        self._current_translation = translation
        self.result_label.setText(translation)
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #313244;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #94e2d5;
                font-family: "Microsoft YaHei", "Segoe UI";
                min-height: 40px;
            }
        """)
        self.status_label.setText("✅ 按 Enter 粘贴到目标窗口")
        
    def show_error(self, error: str):
        """显示错误"""
        self.result_label.setText(f"❌ {error}")
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: #313244;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #f38ba8;
                font-family: "Microsoft YaHei", "Segoe UI";
                min-height: 40px;
            }
        """)
        
    def _on_enter_pressed(self):
        """按下 Enter - 粘贴结果"""
        if self._current_translation:
            self.paste_requested.emit(self._current_translation)
            self._close_and_paste()
            
    def _on_escape(self):
        """按下 Esc - 取消"""
        self.hide()
        self.closed.emit()
        
    def _close_and_paste(self):
        """关闭窗口并粘贴"""
        self.hide()
        self.closed.emit()
        
    def activate(self):
        """激活窗口"""
        # 记录当前前台窗口
        self._target_hwnd = user32.GetForegroundWindow()
        
        # 清空并显示
        self.input_edit.clear()
        self.result_label.setText("翻译结果将显示在这里...")
        self._current_translation = ""
        self.status_label.setText("💡 输入中文后自动翻译")
        
        # 定位到屏幕中央偏上
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() // 3
        self.move(x, y)
        
        # 显示并聚焦
        self.show()
        self.activateWindow()
        self.input_edit.setFocus()
        
    def get_target_hwnd(self):
        """获取目标窗口句柄"""
        return self._target_hwnd


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = FloatingInputWindow()
    window.translate_requested.connect(lambda t: print(f"翻译: {t}"))
    window.paste_requested.connect(lambda t: print(f"粘贴: {t}"))
    window.activate()
    
    sys.exit(app.exec_())
