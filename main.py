"""
翻译输入助手 - 简洁长条设计
- 只有输入框
- 翻译后直接粘贴
"""

import sys
import json
import threading
import ctypes
import time
import pyperclip
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QShortcut, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import QFont, QColor, QCursor, QIcon, QPixmap, QPainter, QLinearGradient

from translator import Translator
from pynput.keyboard import Key, Controller as KeyboardController

user32 = ctypes.windll.user32


class FloatingTranslator(QWidget):
    """简洁长条翻译窗口"""
    
    translation_done = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self._pinned = True
        self._dragging = False
        self._drag_position = QPoint()
        
        self.translator = Translator('config.json')
        self.keyboard = KeyboardController()
        
        self._init_ui()
        self._setup_shortcuts()
        self.translation_done.connect(self._show_result)
        
    def _init_ui(self):
        """初始化简洁 UI"""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Size will be set dynamically in main()
        
        # 主容器
        self.container = QWidget(self)
        self.container.setObjectName("container")
        
        # 阴影 - 清透水滴阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(100, 200, 255, 50))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        # 清透水滴样式 - 高透明度
        self.setStyleSheet("""
            #container {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.75),
                    stop:0.1 rgba(230, 245, 255, 0.65),
                    stop:0.9 rgba(200, 235, 255, 0.6),
                    stop:1 rgba(180, 225, 255, 0.7)
                );
                border-radius: 30px;
                border: 1.5px solid rgba(255, 255, 255, 0.9);
            }
            QLabel {
                color: #2c5282;
                font-family: "Microsoft YaHei", "Segoe UI";
            }
            QLabel#titleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2b6cb0;
            }
            QLabel#statusLabel {
                font-size: 15px;
                color: rgba(44, 82, 130, 0.8);
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.5);
                border: 2px solid rgba(100, 180, 220, 0.4);
                border-radius: 18px;
                padding: 14px 20px;
                color: #1a365d;
                font-family: "Microsoft YaHei", "Segoe UI";
                font-size: 22px;
                selection-background-color: rgba(100, 180, 220, 0.4);
            }
            QLineEdit:focus {
                border: 2px solid rgba(66, 153, 225, 0.7);
                background-color: rgba(255, 255, 255, 0.7);
            }
            QLineEdit::placeholder {
                color: rgba(44, 82, 130, 0.5);
            }
            QPushButton {
                border: none;
                border-radius: 16px;
                padding: 14px 28px;
                font-family: "Microsoft YaHei", "Segoe UI";
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton#actionBtn {
                background-color: rgba(66, 153, 225, 0.9);
                color: #ffffff;
            }
            QPushButton#actionBtn:hover {
                background-color: rgba(49, 130, 206, 1);
            }
            QPushButton#actionBtn:disabled {
                background-color: rgba(66, 153, 225, 0.4);
            }
            QPushButton#pinBtn {
                background-color: rgba(66, 153, 225, 0.3);
                color: #2b6cb0;
                padding: 10px 14px;
                font-size: 13px;
            }
            QPushButton#pinBtn:hover {
                background-color: rgba(66, 153, 225, 0.5);
            }
            QPushButton#closeBtn {
                background-color: transparent;
                color: rgba(44, 82, 130, 0.6);
                padding: 6px 12px;
                font-size: 22px;
            }
            QPushButton#closeBtn:hover {
                color: #e53e3e;
                background-color: rgba(254, 178, 178, 0.5);
                border-radius: 14px;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.addWidget(self.container)
        
        # 容器布局 - 水平一行
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(16)
        
        # 标题
        title = QLabel("🌈")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # 输入框
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入中文，按 Enter 翻译并粘贴...")
        self.input_box.textChanged.connect(self._on_text_changed)
        self.input_box.returnPressed.connect(self._on_translate_and_paste)
        layout.addWidget(self.input_box, 1)
        
        # 状态
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setFixedWidth(80)
        layout.addWidget(self.status_label)
        
        # 操作按钮
        self.action_btn = QPushButton("翻译 ↵")
        self.action_btn.setObjectName("actionBtn")
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self._on_translate_and_paste)
        layout.addWidget(self.action_btn)
        
        # 置顶按钮
        self.pin_btn = QPushButton("📌")
        self.pin_btn.setObjectName("pinBtn")
        self.pin_btn.setCursor(Qt.PointingHandCursor)
        self.pin_btn.clicked.connect(self._toggle_pin)
        self.pin_btn.setToolTip("切换置顶")
        layout.addWidget(self.pin_btn)
        
        # 关闭
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeBtn")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
    def _setup_shortcuts(self):
        paste = QShortcut(Qt.CTRL + Qt.Key_Return, self)
        paste.activated.connect(self._on_translate_and_paste)
        
        esc = QShortcut(Qt.Key_Escape, self)
        esc.activated.connect(self.close)
        
    def _toggle_pin(self):
        self._pinned = not self._pinned
        if self._pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📌")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📍")
        self.show()
        
    def _on_text_changed(self):
        pass
        
    def _on_translate_and_paste(self):
        text = self.input_box.text().strip()
        if not text:
            self.status_label.setText("请输入")
            return
        
        self.status_label.setText("翻译中...")
        self.action_btn.setEnabled(False)
        threading.Thread(target=self._do_translate, args=(text,), daemon=True).start()
        
    def _do_translate(self, text):
        try:
            result = self.translator.translate(text)
            self.translation_done.emit(result)
        except Exception as e:
            self.translation_done.emit(f"错误: {e}")
            
    def _show_result(self, result):
        self.action_btn.setEnabled(True)
        self.status_label.setText("粘贴中...")
        pyperclip.copy(result)
        self.hide()
        QApplication.processEvents()
        QTimer.singleShot(200, self._do_paste)
        
    def _do_paste(self):
        time.sleep(0.1)
        self.keyboard.press(Key.ctrl)
        time.sleep(0.05)
        self.keyboard.press('v')
        time.sleep(0.05)
        self.keyboard.release('v')
        self.keyboard.release(Key.ctrl)
        print("[粘贴] 完成")
        QTimer.singleShot(300, self._reshow)
        
    def _reshow(self):
        self.show()
        self.input_box.clear()
        self.status_label.setText("")
        self.input_box.setFocus()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if self._dragging:
            self.move(event.globalPos() - self._drag_position)
            
    def mouseReleaseEvent(self, event):
        self._dragging = False
        
    def closeEvent(self, event):
        event.ignore()
        self.hide()


class SystemTray:
    def __init__(self, window):
        self.window = window
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, 64, 64)
        gradient.setColorAt(0, QColor(102, 126, 234))
        gradient.setColorAt(1, QColor(240, 147, 251))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 14, 14)
        
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "译")
        painter.end()
        
        self.tray = QSystemTrayIcon(QIcon(pixmap))
        
        menu = QMenu()
        show_action = QAction("显示", menu)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)
        
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)
        
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_activated)
        
    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_window()
            
    def _show_window(self):
        self.window.show()
        self.window.activateWindow()
        self.window.input_box.setFocus()
        
    def _quit(self):
        self.tray.hide()
        QApplication.quit()
        
    def show(self):
        self.tray.show()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = FloatingTranslator()
    tray = SystemTray(window)
    
    # 动态计算窗口大小 - 屏幕宽度的 1/3
    screen = app.primaryScreen().geometry()
    window_width = int(screen.width() / 3)
    window_height = 120
    window.setFixedSize(window_width, window_height)
    
    # 屏幕顶部居中
    x = (screen.width() - window_width) // 2
    y = 60
    window.move(x, y)
    
    window.show()
    tray.show()
    window.input_box.setFocus()
    
    print("✅ 翻译助手 - 输入中文，按 Enter 翻译并粘贴")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
