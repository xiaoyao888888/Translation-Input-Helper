"""
Result Window Module
翻译结果悬浮窗口
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PyQt5.QtGui import QFont, QColor


class ResultWindow(QWidget):
    """翻译结果悬浮窗口"""
    
    def __init__(self, auto_hide_seconds: int = 5):
        super().__init__()
        self.auto_hide_seconds = auto_hide_seconds
        self.drag_position = None
        self._init_ui()
        self._init_animation()
        
    def _init_ui(self):
        """初始化UI"""
        # 窗口属性：无边框、置顶、透明背景
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 主容器
        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: rgba(30, 30, 30, 0.95);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        # 布局
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # 原文标签
        self.original_label = QLabel()
        self.original_label.setWordWrap(True)
        self.original_label.setFont(QFont("Microsoft YaHei", 11))
        self.original_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            background: transparent;
        """)
        layout.addWidget(self.original_label)
        
        # 分隔线
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")
        layout.addWidget(separator)
        
        # 译文标签
        self.translation_label = QLabel()
        self.translation_label.setWordWrap(True)
        self.translation_label.setFont(QFont("Segoe UI", 12))
        self.translation_label.setStyleSheet("""
            color: #4FC3F7;
            background: transparent;
        """)
        layout.addWidget(self.translation_label)
        
        # 提示标签
        hint_label = QLabel("按 Esc 关闭 | 拖拽移动")
        hint_label.setFont(QFont("Microsoft YaHei", 8))
        hint_label.setStyleSheet("color: rgba(255, 255, 255, 0.3); background: transparent;")
        hint_label.setAlignment(Qt.AlignRight)
        layout.addWidget(hint_label)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.container)
        
        # 设置最小/最大尺寸
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        
    def _init_animation(self):
        """初始化动画"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.timeout.connect(self._start_fade_out)
        
    def show_translation(self, original: str, translation: str):
        """显示翻译结果
        
        Args:
            original: 原文
            translation: 译文
        """
        self.original_label.setText(f"📝 {original}")
        self.translation_label.setText(f"🌐 {translation}")
        
        # 调整大小
        self.adjustSize()
        
        # 定位到屏幕右下角
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 30
        y = screen.height() - self.height() - 80
        self.move(x, y)
        
        # 显示窗口
        self.setWindowOpacity(0)
        self.show()
        
        # 淡入动画
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()
        
        # 启动自动隐藏计时器
        self.auto_hide_timer.start(self.auto_hide_seconds * 1000)
        
    def _start_fade_out(self):
        """开始淡出动画"""
        self.auto_hide_timer.stop()
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
    def keyPressEvent(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key_Escape:
            self.hide()
        super().keyPressEvent(event)
        
    def mousePressEvent(self, event):
        """鼠标按下事件 - 支持拖拽"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖拽窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.drag_position = None


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = ResultWindow()
    window.show_translation(
        "你好，世界！今天天气真不错。",
        "Hello, world! The weather is really nice today."
    )
    sys.exit(app.exec_())
