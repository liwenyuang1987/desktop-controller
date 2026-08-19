# -*- coding: utf-8 -*-
"""
自动化脚本示例
演示如何组合使用各模块完成复杂自动化任务
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop_controller.core.mouse import MouseController
from desktop_controller.core.keyboard import KeyboardController
from desktop_controller.core.screen import ScreenController
from desktop_controller.core.window import WindowController
from desktop_controller.core.process import ProcessController


class AutoWorkflow:
    """自动化工作流基类"""

    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.screen = ScreenController()
        self.window = WindowController()
        self.process = ProcessController()

    def wait(self, seconds):
        """等待"""
        time.sleep(seconds)

    def run(self):
        """执行工作流（子类重写）"""
        raise NotImplementedError


class OpenNotepadAndType(AutoWorkflow):
    """打开记事本并输入文本"""

    def __init__(self, text="Hello from Desktop Controller!"):
        super().__init__()
        self.text = text

    def run(self):
        print("启动记事本...")
        self.process.start_process("notepad.exe")
        self.wait(1.5)

        # 激活记事本窗口
        notepad = self.window.find_window("记事本")
        if notepad:
            self.window.activate(notepad)
            self.wait(0.5)

        print(f"输入文本: {self.text}")
        self.keyboard.type_text(self.text, use_clipboard=True)
        self.wait(0.3)
        self.keyboard.press("enter")

        print("保存文件...")
        self.keyboard.save()
        self.wait(0.5)

        # 输入文件名
        self.keyboard.type_text("auto_test.txt", use_clipboard=True)
        self.wait(0.3)
        self.keyboard.press("enter")
        print("完成！")


class ScreenshotWorkflow(AutoWorkflow):
    """批量截图工作流"""

    def __init__(self, output_dir="screenshots", count=5, interval=2):
        super().__init__()
        self.output_dir = output_dir
        self.count = count
        self.interval = interval

    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"开始批量截图，共{self.count}张，间隔{self.interval}秒")

        for i in range(self.count):
            filename = os.path.join(self.output_dir, f"shot_{i+1:03d}.png")
            self.screen.capture(filename)
            print(f"  [{i+1}/{self.count}] {filename}")
            if i < self.count - 1:
                self.wait(self.interval)

        print("批量截图完成！")


class WindowArrangement(AutoWorkflow):
    """窗口排列工作流 - 将指定窗口平铺排列"""

    def __init__(self, window_titles=None):
        super().__init__()
        self.window_titles = window_titles or []

    def run(self):
        screen_w, screen_h = self.screen.size
        windows = []

        for title in self.window_titles:
            w = self.window.find_window(title)
            if w:
                windows.append(w)
                print(f"找到窗口: {w.title}")

        if not windows:
            print("未找到指定窗口")
            return

        # 左右分屏
        if len(windows) >= 2:
            half_w = screen_w // 2
            self.window.move_and_resize(windows[0].hwnd, 0, 0, half_w, screen_h)
            self.window.move_and_resize(windows[1].hwnd, half_w, 0, half_w, screen_h)
            print("已左右分屏排列")

        # 激活第一个窗口
        if windows:
            self.window.activate(windows[0])


class FindAndClickWorkflow(AutoWorkflow):
    """图像识别点击工作流"""

    def __init__(self, template_path, confidence=0.8, timeout=10):
        super().__init__()
        self.template_path = template_path
        self.confidence = confidence
        self.timeout = timeout

    def run(self):
        print(f"等待图像出现: {self.template_path}")
        pos = self.screen.wait_for_image(
            self.template_path,
            timeout=self.timeout,
            confidence=self.confidence
        )

        if pos:
            print(f"找到图像位置: {pos}")
            self.mouse.move(pos[0], pos[1], duration=0.3)
            self.wait(0.2)
            self.mouse.click()
            print("已点击")
        else:
            print("超时未找到图像")


if __name__ == "__main__":
    print("自动化脚本示例")
    print("选择要运行的工作流:")
    print("  1. 打开记事本并输入文本")
    print("  2. 批量截图")
    print("  3. 窗口左右分屏")
    print("  4. 图像识别点击")

    # 示例：运行记事本工作流
    # workflow = OpenNotepadAndType("你好，这是自动化测试！")
    # workflow.run()

    print("\n取消对应代码注释即可运行。")
