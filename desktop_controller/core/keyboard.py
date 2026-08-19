# -*- coding: utf-8 -*-
"""
键盘控制模块
提供按键、组合键、文本输入、热键等功能
"""

import time
import pyautogui
import pyperclip
from typing import List, Optional, Union


class KeyboardController:
    """键盘控制器"""

    # 常用特殊键映射
    SPECIAL_KEYS = {
        "enter": "enter",
        "return": "enter",
        "esc": "esc",
        "escape": "esc",
        "tab": "tab",
        "space": "space",
        "backspace": "backspace",
        "delete": "delete",
        "del": "delete",
        "insert": "insert",
        "home": "home",
        "end": "end",
        "pageup": "pageup",
        "pagedown": "pagedown",
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "capslock": "capslock",
        "numlock": "numlock",
        "scrolllock": "scrolllock",
        "printscreen": "printscreen",
        "pause": "pause",
        "win": "win",
        "windows": "win",
        "cmd": "win",
        "command": "win",
        "alt": "alt",
        "ctrl": "ctrl",
        "control": "ctrl",
        "shift": "shift",
        "fn": "fn",
        "menu": "menu",
    }

    # F1-F24
    for i in range(1, 25):
        SPECIAL_KEYS[f"f{i}"] = f"f{i}"

    def __init__(self, interval: float = 0.0):
        """
        初始化键盘控制器

        Args:
            interval: 默认按键间隔（秒）
        """
        self.default_interval = interval

    def press(self, key: str, presses: int = 1, interval: Optional[float] = None) -> None:
        """
        按下并释放单个键

        Args:
            key: 按键名称（如 'a', 'enter', 'ctrl'）
            presses: 按几次
            interval: 每次间隔
        """
        key = self._normalize_key(key)
        dur = interval if interval is not None else self.default_interval
        pyautogui.press(key, presses=presses, interval=dur)

    def key_down(self, key: str) -> None:
        """按下键不释放"""
        key = self._normalize_key(key)
        pyautogui.keyDown(key)

    def key_up(self, key: str) -> None:
        """释放键"""
        key = self._normalize_key(key)
        pyautogui.keyUp(key)

    def hotkey(self, *keys: str, interval: float = 0.05) -> None:
        """
        按下组合键（如 ctrl+c, alt+tab）

        Args:
            *keys: 组合键序列，如 'ctrl', 'c'
            interval: 按键间隔

        示例:
            keyboard.hotkey('ctrl', 'c')
            keyboard.hotkey('ctrl', 'shift', 'esc')
        """
        normalized = [self._normalize_key(k) for k in keys]
        pyautogui.hotkey(*normalized, interval=interval)

    def type_text(
        self,
        text: str,
        interval: Optional[float] = None,
        use_clipboard: bool = False,
    ) -> None:
        """
        输入文本

        Args:
            text: 要输入的文本
            interval: 字符间隔（秒）
            use_clipboard: 是否使用剪贴板粘贴（适合中文等非ASCII文本）
        """
        if use_clipboard or self._contains_non_ascii(text):
            # 使用剪贴板方式，支持中文
            pyperclip.copy(text)
            time.sleep(0.05)
            self.hotkey("ctrl", "v")
        else:
            dur = interval if interval is not None else self.default_interval
            pyautogui.typewrite(text, interval=dur)

    def type_line(self, text: str, interval: Optional[float] = None) -> None:
        """输入一行文本并按回车"""
        self.type_text(text, interval)
        self.press("enter")

    def select_all(self) -> None:
        """全选 Ctrl+A"""
        self.hotkey("ctrl", "a")

    def copy(self) -> None:
        """复制 Ctrl+C"""
        self.hotkey("ctrl", "c")

    def cut(self) -> None:
        """剪切 Ctrl+X"""
        self.hotkey("ctrl", "x")

    def paste(self) -> None:
        """粘贴 Ctrl+V"""
        self.hotkey("ctrl", "v")

    def undo(self) -> None:
        """撤销 Ctrl+Z"""
        self.hotkey("ctrl", "z")

    def redo(self) -> None:
        """重做 Ctrl+Y"""
        self.hotkey("ctrl", "y")

    def save(self) -> None:
        """保存 Ctrl+S"""
        self.hotkey("ctrl", "s")

    def open_find(self) -> None:
        """查找 Ctrl+F"""
        self.hotkey("ctrl", "f")

    def switch_window(self) -> None:
        """切换窗口 Alt+Tab"""
        self.hotkey("alt", "tab")

    def close_window(self) -> None:
        """关闭窗口 Alt+F4"""
        self.hotkey("alt", "f4")

    def open_task_manager(self) -> None:
        """打开任务管理器 Ctrl+Shift+Esc"""
        self.hotkey("ctrl", "shift", "esc")

    def lock_screen(self) -> None:
        """锁定屏幕 Win+L"""
        self.hotkey("win", "l")

    def open_run_dialog(self) -> None:
        """打开运行对话框 Win+R"""
        self.hotkey("win", "r")

    def open_explorer(self) -> None:
        """打开文件资源管理器 Win+E"""
        self.hotkey("win", "e")

    def show_desktop(self) -> None:
        """显示桌面 Win+D"""
        self.hotkey("win", "d")

    def screenshot_shortcut(self) -> None:
        """截图 Win+Shift+S (Windows)"""
        self.hotkey("win", "shift", "s")

    def press_sequence(self, keys: List[str], interval: float = 0.1) -> None:
        """
        依次按下一系列按键

        Args:
            keys: 按键列表
            interval: 间隔
        """
        for key in keys:
            self.press(key)
            time.sleep(interval)

    def hold_keys(self, *keys: str) -> "_KeyHolder":
        """
        上下文管理器：按住多个键

        示例:
            with keyboard.hold_keys('ctrl', 'shift'):
                keyboard.press('esc')
        """
        return _KeyHolder(self, keys)

    def _normalize_key(self, key: str) -> str:
        """标准化按键名称"""
        key_lower = key.lower().strip()
        return self.SPECIAL_KEYS.get(key_lower, key_lower)

    @staticmethod
    def _contains_non_ascii(text: str) -> bool:
        """检查文本是否包含非ASCII字符"""
        try:
            text.encode("ascii")
            return False
        except UnicodeEncodeError:
            return True


class _KeyHolder:
    """按键保持上下文管理器"""

    def __init__(self, controller: KeyboardController, keys):
        self.controller = controller
        self.keys = keys

    def __enter__(self):
        for key in self.keys:
            self.controller.key_down(key)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in reversed(self.keys):
            self.controller.key_up(key)
        return False
