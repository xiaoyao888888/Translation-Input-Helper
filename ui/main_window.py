"""
Main Control Window Module
主控制窗口 - 支持直接输入和剪贴板监听
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QFrame, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter


class MainWindow(QWidget):
    """主控制窗口"""
    
    # 信号
    translate_clicked = pyqtSignal(str)  # 传递要翻译的文本
    clear_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._last_clipboard = ""
        self._init_ui()
        self._init_clipboard_monitor()
        
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("中文输入翻译器")
        self.setWindowIcon(self._create_icon())
        self.setMinimumSize(450, 420)
        self.resize(500, 480)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: "Microsoft YaHei", "Segoe UI";
            }
            QTextEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #cdd6f4;
            }
            QTextEdit:focus {
                border: 1px solid #89b4fa;
            }
            QTextEdit#inputBox {
                color: #f5e0dc;
            }
            QTextEdit#resultBox {
                color: #94e2d5;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
            QPushButton#clearBtn {
                background-color: #45475a;
                color: #cdd6f4;
            }
            QPushButton#clearBtn:hover {
                background-color: #585b70;
            }
            QPushButton#clipboardBtn {
                background-color: #a6e3a1;
                color: #1e1e2e;
            }
            QPushButton#clipboardBtn:hover {
                background-color: #94e2d5;
            }
            QLabel#title {
                font-size: 18px;
                font-weight: bold;
                color: #89b4fa;
            }
            QLabel#hint {
                font-size: 11px;
                color: #6c7086;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # 标题
        title_label = QLabel("🌐 中文输入翻译器")
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # 提示信息
        hint_label = QLabel("💡 在任意窗口输入中文，下方会自动显示捕获的内容")
        hint_label.setObjectName("hint")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)
        
        # 输入区域
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(5)
        
        input_header = QLabel("📝 捕获的中文（实时显示）：")
        input_header.setStyleSheet("color: #a6adc8; font-size: 12px;")
        input_layout.addWidget(input_header)
        
        self.input_box = QTextEdit()
        self.input_box.setObjectName("inputBox")
        self.input_box.setPlaceholderText("等待捕获中文输入...")
        self.input_box.setMaximumHeight(120)
        input_layout.addWidget(self.input_box)
        
        layout.addWidget(input_frame)
        
        # 按钮区域1
        btn_layout1 = QHBoxLayout()
        btn_layout1.setSpacing(10)
        
        self.paste_btn = QPushButton("📋 粘贴翻译")
        self.paste_btn.setObjectName("clipboardBtn")
        self.paste_btn.setCursor(Qt.PointingHandCursor)
        self.paste_btn.clicked.connect(self._on_paste_translate)
        btn_layout1.addWidget(self.paste_btn)
        
        self.translate_btn = QPushButton("🌐 翻译")
        self.translate_btn.setCursor(Qt.PointingHandCursor)
        self.translate_btn.clicked.connect(self._on_translate_clicked)
        btn_layout1.addWidget(self.translate_btn, 1)
        
        layout.addLayout(btn_layout1)
        
        # 翻译结果区域
        result_frame = QFrame()
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(5)
        
        result_header = QLabel("🔄 翻译结果：")
        result_header.setStyleSheet("color: #a6adc8; font-size: 12px;")
        result_layout.addWidget(result_header)
        
        self.result_box = QTextEdit()
        self.result_box.setObjectName("resultBox")
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("翻译结果将显示在这里...")
        result_layout.addWidget(self.result_box)
        
        layout.addWidget(result_frame, 1)
        
        # 按钮区域2
        btn_layout2 = QHBoxLayout()
        btn_layout2.setSpacing(10)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        btn_layout2.addWidget(self.clear_btn)
        
        self.copy_btn = QPushButton("📄 复制结果")
        self.copy_btn.setObjectName("clearBtn")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self._on_copy_result)
        btn_layout2.addWidget(self.copy_btn, 1)
        
        layout.addLayout(btn_layout2)
        
        # 底部状态提示
        status_label = QLabel("💡 关闭窗口最小化到托盘 | 双击托盘图标恢复窗口")
        status_label.setObjectName("hint")
        status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)
        
    def _init_clipboard_monitor(self):
        """初始化剪贴板监控"""
        self.clipboard = QApplication.clipboard()
        # 保存初始剪贴板内容，避免启动时触发
        self._last_clipboard = self.clipboard.text()
        
    def _create_icon(self) -> QIcon:
        """创建窗口图标"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(137, 180, 250))
        painter.setPen(QColor(137, 180, 250))
        painter.drawEllipse(4, 4, 56, 56)
        
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Microsoft YaHei", 28, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "译")
        painter.end()
        
        return QIcon(pixmap)
        
    def _on_translate_clicked(self):
        """翻译按钮点击"""
        text = self.input_box.toPlainText().strip()
        if text:
            self.translate_clicked.emit(text)
        
    def _on_paste_translate(self):
        """粘贴并翻译"""
        clipboard_text = self.clipboard.text().strip()
        if clipboard_text:
            self.input_box.setPlainText(clipboard_text)
            self.translate_clicked.emit(clipboard_text)
        
    def _on_clear_clicked(self):
        """清空按钮点击"""
        self.input_box.clear()
        self.result_box.clear()
        self.clear_clicked.emit()
        
    def _on_copy_result(self):
        """复制翻译结果"""
        result = self.result_box.toPlainText()
        if result:
            self.clipboard.setText(result)
        
    def get_input_text(self) -> str:
        """获取输入框文本"""
        return self.input_box.toPlainText().strip()
        
    def show_translation(self, original: str, translation: str):
        """显示翻译结果
        
        Args:
            original: 原文
            translation: 译文
        """
        self.input_box.setPlainText(original)
        self.result_box.setPlainText(translation)
        
    def set_translating(self, is_translating: bool):
        """设置翻译中状态
        
        Args:
            is_translating: 是否正在翻译
        """
        if is_translating:
            self.translate_btn.setText("⏳ 翻译中...")
            self.translate_btn.setEnabled(False)
            self.paste_btn.setEnabled(False)
        else:
            self.translate_btn.setText("🌐 翻译")
            self.translate_btn.setEnabled(True)
            self.paste_btn.setEnabled(True)
            
    def closeEvent(self, event):
        """窗口关闭事件 - 最小化到托盘"""
        event.ignore()
        self.hide()


if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.translate_clicked.connect(lambda t: print(f"Translate: {t}"))
    window.show()
    sys.exit(app.exec_())
