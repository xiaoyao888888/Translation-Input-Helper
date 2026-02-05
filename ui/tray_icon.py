"""
System Tray Icon Module
系统托盘图标
"""

import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import pyqtSignal, QObject


class TrayIcon(QObject):
    """系统托盘图标"""
    
    # 信号
    translate_triggered = pyqtSignal()
    clear_buffer_triggered = pyqtSignal()
    show_window_triggered = pyqtSignal()
    quit_triggered = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(parent)
        self._init_icon()
        self._init_menu()
        
    def _init_icon(self):
        """初始化图标"""
        # 创建一个简洁的图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆形背景
        painter.setBrush(QColor(79, 195, 247))
        painter.setPen(QColor(79, 195, 247))
        painter.drawEllipse(4, 4, 56, 56)
        
        # 绘制文字 "译"
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Microsoft YaHei", 28, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), 0x0084, "译")  # AlignCenter
        
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("中文输入翻译器\n按 Ctrl+Alt+T 翻译")
        
    def _init_menu(self):
        """初始化右键菜单"""
        menu = QMenu()
        
        # 显示主窗口
        show_action = QAction("📺 显示主窗口", menu)
        show_action.triggered.connect(self.show_window_triggered.emit)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        # 翻译当前缓冲
        translate_action = QAction("🌐 立即翻译 (Ctrl+Alt+T)", menu)
        translate_action.triggered.connect(self.translate_triggered.emit)
        menu.addAction(translate_action)
        
        menu.addSeparator()
        
        # 清空缓冲区
        clear_action = QAction("🗑️ 清空输入缓冲", menu)
        clear_action.triggered.connect(self.clear_buffer_triggered.emit)
        menu.addAction(clear_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction("❌ 退出", menu)
        quit_action.triggered.connect(self.quit_triggered.emit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        
        # 双击显示主窗口
        self.tray_icon.activated.connect(self._on_activated)
        
    def _on_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window_triggered.emit()
            
    def show(self):
        """显示托盘图标"""
        self.tray_icon.show()
        
    def hide(self):
        """隐藏托盘图标"""
        self.tray_icon.hide()
        
    def show_message(self, title: str, message: str, duration: int = 3000):
        """显示托盘消息
        
        Args:
            title: 标题
            message: 消息内容
            duration: 显示时长（毫秒）
        """
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, duration)


if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    tray = TrayIcon()
    tray.quit_triggered.connect(app.quit)
    tray.show()
    tray.show_message("测试", "托盘图标已启动")
    
    sys.exit(app.exec_())
