# -*- coding: utf-8 -*-
"""
基础使用示例
演示Desktop Controller各模块的基本用法
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_controller.core.mouse import MouseController
from desktop_controller.core.keyboard import KeyboardController
from desktop_controller.core.screen import ScreenController
from desktop_controller.core.window import WindowController
from desktop_controller.core.process import ProcessController


def example_mouse():
    """鼠标控制示例"""
    print("=== 鼠标控制示例 ===")
    mouse = MouseController()

    # 获取屏幕大小
    w, h = mouse.screen_size
    print(f"屏幕分辨率: {w} x {h}")

    # 获取当前位置
    x, y = mouse.position
    print(f"当前鼠标位置: ({x}, {y})")

    # 移动到屏幕中心
    mouse.move(w // 2, h // 2, duration=0.5)
    print("移动到屏幕中心")

    # 相对移动
    mouse.move_relative(100, 50, duration=0.3)
    print("相对移动 (100, 50)")

    # 左键点击
    mouse.click(button="left")
    print("左键点击")

    # 双击
    mouse.double_click()
    print("双击")

    # 右键
    mouse.right_click()
    print("右键点击")

    # 拖拽
    mouse.drag(100, 100, 300, 300, duration=0.5)
    print("拖拽从 (100,100) 到 (300,300)")

    # 滚动
    mouse.scroll_down(3)
    print("向下滚动3格")


def example_keyboard():
    """键盘控制示例"""
    print("\n=== 键盘控制示例 ===")
    keyboard = KeyboardController()

    # 输入文本（支持中文）
    keyboard.type_text("Hello World! 你好世界！", use_clipboard=True)
    print("输入文本")

    # 按回车
    keyboard.press("enter")
    print("按回车")

    # 组合键
    keyboard.hotkey("ctrl", "a")  # 全选
    print("全选 Ctrl+A")

    keyboard.hotkey("ctrl", "c")  # 复制
    print("复制 Ctrl+C")

    keyboard.hotkey("ctrl", "v")  # 粘贴
    print("粘贴 Ctrl+V")

    # 常用快捷键
    keyboard.save()       # Ctrl+S
    keyboard.undo()       # Ctrl+Z
    keyboard.open_find()  # Ctrl+F

    # 按键序列
    keyboard.press_sequence(["up", "up", "down", "down", "left", "right"])
    print("按键序列")

    # 上下文管理器按住键
    with keyboard.hold_keys("ctrl", "shift"):
        keyboard.press("esc")  # Ctrl+Shift+Esc 任务管理器
    print("打开任务管理器")


def example_screen():
    """屏幕操作示例"""
    print("\n=== 屏幕操作示例 ===")
    screen = ScreenController()

    # 全屏截图
    screen.capture("screenshot_full.png")
    print("全屏截图保存为 screenshot_full.png")

    # 区域截图
    screen.capture_region(100, 100, 800, 600, "screenshot_region.png")
    print("区域截图 (100,100,800,600) 保存为 screenshot_region.png")

    # 获取像素颜色
    r, g, b = screen.get_pixel_color(500, 300)
    print(f"像素 (500,300) 颜色: RGB({r},{g},{b})")

    # 查找图像
    # pos = screen.find_image("button.png", confidence=0.8)
    # if pos:
    #     print(f"找到按钮位置: {pos}")
    #     screen.click_image("button.png")  # 找到并点击

    # 等待图像出现
    # pos = screen.wait_for_image("dialog.png", timeout=10)


def example_window():
    """窗口管理示例"""
    print("\n=== 窗口管理示例 ===")
    win = WindowController()

    # 列出所有窗口
    windows = win.list_windows()
    print(f"当前共 {len(windows)} 个窗口")
    for w in windows[:5]:
        print(f"  - {w.title[:40]} (hwnd={w.hwnd})")

    # 获取活动窗口
    active = win.get_active_window()
    if active:
        print(f"当前活动窗口: {active.title}")

    # 查找窗口
    # notepad = win.find_window("记事本")
    # if notepad:
    #     win.activate(notepad)       # 激活
    #     win.move(notepad, 100, 100) # 移动
    #     win.resize(notepad, 800, 600)  # 调整大小
    #     win.maximize(notepad)      # 最大化
    #     win.minimize(notepad)      # 最小化
    #     win.restore(notepad)       # 还原
    #     win.always_on_top(notepad, True)  # 置顶


def example_process():
    """进程管理示例"""
    print("\n=== 进程管理示例 ===")
    proc = ProcessController()

    # 系统信息
    info = proc.get_system_info()
    print(f"CPU核心数: {info['cpu_count']}")
    print(f"CPU使用率: {info['cpu_percent']:.1f}%")
    print(f"内存: {info['memory']['used_gb']}/{info['memory']['total_gb']} GB")

    # 列出进程（按CPU排序）
    proc.print_top_processes(5, by="cpu")

    # 查找进程
    # chrome_procs = proc.find_by_name("chrome")
    # print(f"找到 {len(chrome_procs)} 个Chrome进程")

    # 启动进程
    # proc.start_process("notepad.exe")

    # 终止进程
    # proc.terminate_by_name("notepad.exe")


if __name__ == "__main__":
    print("Desktop Controller 基础使用示例")
    print("注意：运行这些示例会实际操作你的鼠标键盘，请保存好工作！")
    print()

    # 取消注释运行对应示例
    # example_mouse()
    # example_keyboard()
    # example_screen()
    # example_window()
    # example_process()

    print("\n示例代码已加载，取消对应函数注释即可运行。")
