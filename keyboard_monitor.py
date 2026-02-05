"""
Windows UI Automation Text Capture
使用 UI Automation 读取当前焦点控件的文本内容

原理：
- 使用 pywinauto/uiautomation 获取当前焦点控件
- 定期读取控件的文本内容
- 检测中文字符变化
"""

import re
import time
import threading
import ctypes
import ctypes.wintypes as wintypes
from typing import Callable, Optional

# 尝试导入 uiautomation
try:
    import uiautomation as auto
    HAS_UIAUTOMATION = True
except ImportError:
    HAS_UIAUTOMATION = False
    print("[警告] 未安装 uiautomation，将使用备用方案")

# Windows API
user32 = ctypes.windll.user32

# 中文字符 Unicode 范围
CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff，。！？、；：""''【】《》（）—…·]+')


class ChineseInputCapture:
    """中文输入实时捕获器 - 使用 UI Automation"""
    
    def __init__(self, on_chinese_input: Callable[[str], None]):
        """初始化
        
        Args:
            on_chinese_input: 捕获到中文时的回调函数
        """
        self.on_chinese_input = on_chinese_input
        self._buffer = ""
        self._last_text = ""
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._check_interval = 0.2  # 检查间隔（秒）
        
        print("[文本捕获] 初始化完成")
        
    def _extract_chinese(self, text: str) -> str:
        """提取文本中的中文字符"""
        if not text:
            return ""
        matches = CHINESE_PATTERN.findall(text)
        return ''.join(matches)
    
    def _get_focused_element_text(self) -> str:
        """获取当前焦点元素的文本"""
        if not HAS_UIAUTOMATION:
            return ""
            
        try:
            # 获取焦点元素
            focused = auto.GetFocusedControl()
            if focused:
                # 尝试获取文本
                try:
                    # 首先尝试 ValuePattern
                    pattern = focused.GetValuePattern()
                    if pattern:
                        return pattern.Value or ""
                except:
                    pass
                
                try:
                    # 然后尝试 TextPattern
                    pattern = focused.GetTextPattern()
                    if pattern:
                        return pattern.DocumentRange.GetText(-1) or ""
                except:
                    pass
                
                try:
                    # 最后尝试 Name 属性
                    return focused.Name or ""
                except:
                    pass
                    
        except Exception as e:
            pass
            
        return ""
    
    def _get_edit_text_via_win32(self) -> str:
        """使用 Win32 API 获取编辑控件文本"""
        try:
            # 获取前台窗口
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return ""
            
            # 获取焦点控件
            thread_id = user32.GetWindowThreadProcessId(hwnd, None)
            user32.AttachThreadInput(ctypes.windll.kernel32.GetCurrentThreadId(), thread_id, True)
            
            focus_hwnd = user32.GetFocus()
            
            user32.AttachThreadInput(ctypes.windll.kernel32.GetCurrentThreadId(), thread_id, False)
            
            if not focus_hwnd:
                return ""
            
            # 获取控件文本
            length = user32.SendMessageW(focus_hwnd, 0x000E, 0, 0)  # WM_GETTEXTLENGTH
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.SendMessageW(focus_hwnd, 0x000D, length + 1, buffer)  # WM_GETTEXT
                return buffer.value
                
        except Exception as e:
            pass
            
        return ""
    
    def _monitor_loop(self):
        """监控循环"""
        print("[文本捕获] 监控循环启动")
        
        while self._running:
            try:
                # 首先尝试 Win32 API（更可靠）
                current_text = self._get_edit_text_via_win32()
                
                # 如果失败，尝试 UI Automation
                if not current_text and HAS_UIAUTOMATION:
                    current_text = self._get_focused_element_text()
                
                # 提取中文
                chinese = self._extract_chinese(current_text)
                
                # 检测变化
                if chinese and chinese != self._buffer:
                    self._buffer = chinese
                    print(f"[文本捕获] 检测到中文: {chinese}")
                    self.on_chinese_input(chinese)
                    
            except Exception as e:
                pass
            
            time.sleep(self._check_interval)
        
        print("[文本捕获] 监控循环结束")
        
    def start(self):
        """启动捕获"""
        print("[文本捕获] 正在启动...")
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print("[文本捕获] ✅ 已启动 - 监控当前焦点控件的中文内容")
        
    def stop(self):
        """停止捕获"""
        print("[文本捕获] 正在停止...")
        self._running = False
        
    def get_buffer(self) -> str:
        """获取当前缓冲区内容"""
        return self._buffer
    
    def clear_buffer(self):
        """清空缓冲区"""
        self._buffer = ""
        self.on_chinese_input("")


if __name__ == "__main__":
    print("=" * 50)
    print("中文输入实时捕获测试 (UI Automation)")
    print("=" * 50)
    
    if not HAS_UIAUTOMATION:
        print("\n[提示] 安装 uiautomation 以获得更好的兼容性:")
        print("pip install uiautomation\n")
    
    def on_chinese(text):
        if text:
            print(f"\n[回调] 捕获到中文: {text}\n")
    
    capture = ChineseInputCapture(on_chinese)
    capture.start()
    
    print("\n在任意窗口（如记事本）中输入中文，观察这里的输出...")
    print("按 Ctrl+C 退出\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        capture.stop()
        print("\n已退出")
