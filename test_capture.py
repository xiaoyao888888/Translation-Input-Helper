"""
测试脚本 - 测试全局热键和剪贴板捕获
运行方法：以管理员权限运行 python test_capture.py
"""

import time
import pyperclip
import keyboard
import pyautogui

print("=" * 50)
print("全局热键测试")
print("=" * 50)

def test_hotkey():
    """测试热键触发"""
    print("\n[测试1] 测试热键注册...")
    
    def on_hotkey():
        print(f"[OK] 热键触发成功! 时间: {time.strftime('%H:%M:%S')}")
        
        # 保存原剪贴板
        try:
            original = pyperclip.paste()
            print(f"[信息] 原剪贴板内容: {original[:50] if original else '(空)'}...")
        except Exception as e:
            print(f"[错误] 读取剪贴板失败: {e}")
            original = ""
        
        # 先释放修饰键
        print("[信息] 释放修饰键...")
        try:
            keyboard.release('ctrl')
            keyboard.release('alt')
        except Exception as e:
            print(f"[警告] 释放修饰键失败: {e}")
        
        time.sleep(0.1)
        
        # 发送 Ctrl+C
        print("[信息] 发送 Ctrl+C...")
        try:
            pyautogui.hotkey('ctrl', 'c')
            print("[OK] Ctrl+C 发送成功")
        except Exception as e:
            print(f"[错误] 发送 Ctrl+C 失败: {e}")
        
        time.sleep(0.2)
        
        # 读取新剪贴板
        try:
            new_content = pyperclip.paste()
            print(f"[信息] 新剪贴板内容: {new_content}")
            
            if new_content and new_content != original:
                print(f"\n{'='*30}")
                print(f"✅ 成功捕获文本: {new_content}")
                print(f"{'='*30}\n")
            elif new_content:
                print(f"\n[信息] 剪贴板内容未变化，但有内容: {new_content}")
            else:
                print("\n[警告] 没有捕获到任何文本")
        except Exception as e:
            print(f"[错误] 读取剪贴板失败: {e}")
    
    try:
        keyboard.add_hotkey('ctrl+alt+t', on_hotkey, suppress=True)
        print("[OK] 热键 Ctrl+Alt+T 注册成功")
    except Exception as e:
        print(f"[错误] 热键注册失败: {e}")
        print("[提示] 请尝试以管理员权限运行")
        return False
    
    return True

def main():
    print("\n开始测试...")
    print("请确保以管理员权限运行此脚本！\n")
    
    if not test_hotkey():
        return
    
    print("\n" + "=" * 50)
    print("测试说明：")
    print("1. 在任意窗口中选中一些文本")
    print("2. 按 Ctrl+Alt+T")
    print("3. 观察上面的日志输出")
    print("按 Esc 退出测试")
    print("=" * 50 + "\n")
    
    keyboard.wait('esc')
    print("\n测试结束")

if __name__ == "__main__":
    main()
