"""
全局热键管理器
Global Hotkey Manager

使用 pynput 监听全局热键 Ctrl+Space 唤起翻译输入窗口
"""

import threading
from pynput import keyboard
from typing import Callable, Set
import time


class HotkeyManager:
    """全局热键管理器"""
    
    def __init__(self, on_activate: Callable[[], None]):
        """初始化
        
        Args:
            on_activate: 热键触发时的回调函数
        """
        self.on_activate = on_activate
        self._pressed_keys: Set = set()
        self._listener = None
        self._last_trigger_time = 0
        
    def _on_press(self, key):
        """按键按下"""
        # 记录按下的键
        self._pressed_keys.add(key)
        
        # 检测 Ctrl + Space
        has_ctrl = (
            keyboard.Key.ctrl_l in self._pressed_keys or
            keyboard.Key.ctrl_r in self._pressed_keys
        )
        has_space = keyboard.Key.space in self._pressed_keys
        
        if has_ctrl and has_space:
            # 防抖动
            current_time = time.time()
            if current_time - self._last_trigger_time < 0.5:
                return
            self._last_trigger_time = current_time
            
            print("[热键] Ctrl+Space 触发")
            self.on_activate()
            
    def _on_release(self, key):
        """按键释放"""
        self._pressed_keys.discard(key)
        
    def start(self):
        """启动热键监听"""
        print("[热键] 启动监听 (Ctrl+Space)")
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()
        
    def stop(self):
        """停止热键监听"""
        if self._listener:
            self._listener.stop()
            self._listener = None


if __name__ == "__main__":
    print("测试热键管理器")
    print("按 Ctrl+Space 触发")
    print("按 Ctrl+C 退出")
    
    def on_activate():
        print("🔥 热键触发！")
    
    manager = HotkeyManager(on_activate)
    manager.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
        print("\n已退出")
