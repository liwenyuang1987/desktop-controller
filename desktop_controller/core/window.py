# -*- coding: utf-8 -*-
"""
窗口管理模块
提供窗口列举、激活、移动、调整大小等功能
主要支持 Windows（pywin32），其他平台降级处理
"""

import time
import subprocess
from typing import List, Optional, Tuple, Dict


try:
    import win32gui
    import win32con
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


class WindowInfo:
    """窗口信息封装"""

    def __init__(self, hwnd=None, title: str = "", rect: Tuple = (0, 0, 0, 0),
                 process_id: int = 0, visible: bool = True):
        self.hwnd = hwnd
        self.title = title
        self.rect = rect  # (left, top, right, bottom)
        self.process_id = process_id
        self.visible = visible

    @property
    def x(self) -> int:
        return self.rect[0]

    @property
    def y(self) -> int:
        return self.rect[1]

    @property
    def width(self) -> int:
        return self.rect[2] - self.rect[0]

    @property
    def height(self) -> int:
        return self.rect[3] - self.rect[1]

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def __repr__(self):
        return f"WindowInfo(hwnd={self.hwnd}, title='{self.title[:30]}', rect={self.rect})"


class WindowController:
    """窗口控制器"""

    def __init__(self):
        if not HAS_WIN32:
            print("警告: 未安装pywin32，窗口管理功能受限。运行: pip install pywin32")

    def list_windows(self, only_visible: bool = True) -> List[WindowInfo]:
        """
        列出所有窗口

        Args:
            only_visible: 只列出可见窗口

        Returns:
            窗口信息列表
        """
        if not HAS_WIN32:
            return []

        windows = []

        def callback(hwnd, _):
            if only_visible and not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if not title and only_visible:
                return
            rect = win32gui.GetWindowRect(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            windows.append(WindowInfo(
                hwnd=hwnd,
                title=title,
                rect=rect,
                process_id=pid,
                visible=win32gui.IsWindowVisible(hwnd),
            ))

        win32gui.EnumWindows(callback, None)
        return windows

    def find_window(self, title_keyword: str, exact: bool = False) -> Optional[WindowInfo]:
        """
        按标题关键词查找窗口

        Args:
            title_keyword: 标题关键词
            exact: 是否精确匹配

        Returns:
            第一个匹配的窗口，未找到返回None
        """
        windows = self.list_windows()
        keyword = title_keyword.lower()

        for win in windows:
            if exact:
                if win.title.lower() == keyword:
                    return win
            else:
                if keyword in win.title.lower():
                    return win
        return None

    def find_windows(self, title_keyword: str) -> List[WindowInfo]:
        """查找所有匹配标题关键词的窗口"""
        windows = self.list_windows()
        keyword = title_keyword.lower()
        return [w for w in windows if keyword in w.title.lower()]

    def get_active_window(self) -> Optional[WindowInfo]:
        """获取当前活动窗口"""
        if not HAS_WIN32:
            return None
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return WindowInfo(hwnd=hwnd, title=title, rect=rect, process_id=pid)

    def activate(self, hwnd_or_window) -> bool:
        """
        激活（前置）窗口

        Args:
            hwnd_or_window: 窗口句柄或WindowInfo对象
        """
        if not HAS_WIN32:
            return False

        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window

        try:
            # 如果窗口最小化，先恢复
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            return True
        except Exception:
            return False

    def activate_by_title(self, title_keyword: str) -> bool:
        """按标题激活窗口"""
        win = self.find_window(title_keyword)
        if win:
            return self.activate(win)
        return False

    def close(self, hwnd_or_window) -> bool:
        """关闭窗口"""
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception:
            return False

    def minimize(self, hwnd_or_window) -> bool:
        """最小化窗口"""
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception:
            return False

    def maximize(self, hwnd_or_window) -> bool:
        """最大化窗口"""
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception:
            return False

    def restore(self, hwnd_or_window) -> bool:
        """还原窗口"""
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return True
        except Exception:
            return False

    def move(self, hwnd_or_window, x: int, y: int) -> bool:
        """
        移动窗口到指定位置（保持大小）
        """
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            win32gui.MoveWindow(hwnd, x, y, width, height, True)
            return True
        except Exception:
            return False

    def resize(self, hwnd_or_window, width: int, height: int) -> bool:
        """
        调整窗口大小（保持位置）
        """
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            rect = win32gui.GetWindowRect(hwnd)
            win32gui.MoveWindow(hwnd, rect[0], rect[1], width, height, True)
            return True
        except Exception:
            return False

    def move_and_resize(
        self, hwnd_or_window, x: int, y: int, width: int, height: int
    ) -> bool:
        """移动并调整窗口大小"""
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            win32gui.MoveWindow(hwnd, x, y, width, height, True)
            return True
        except Exception:
            return False

    def get_window_rect(self, hwnd_or_window) -> Optional[Tuple[int, int, int, int]]:
        """获取窗口矩形 (left, top, right, bottom)"""
        if not HAS_WIN32:
            return None
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            return win32gui.GetWindowRect(hwnd)
        except Exception:
            return None

    def is_maximized(self, hwnd_or_window) -> bool:
        """窗口是否最大化"""
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            return win32gui.IsZoomed(hwnd)
        except Exception:
            return False

    def is_minimized(self, hwnd_or_window) -> bool:
        """窗口是否最小化"""
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            return win32gui.IsIconic(hwnd)
        except Exception:
            return False

    def send_to_back(self, hwnd_or_window) -> bool:
        """窗口置后"""
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            return True
        except Exception:
            return False

    def always_on_top(self, hwnd_or_window, enable: bool = True) -> bool:
        """设置窗口置顶"""
        if not HAS_WIN32:
            return False
        hwnd = hwnd_or_window.hwnd if isinstance(hwnd_or_window, WindowInfo) else hwnd_or_window
        try:
            flag = win32con.HWND_TOPMOST if enable else win32con.HWND_NOTOPMOST
            win32gui.SetWindowPos(hwnd, flag, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            return True
        except Exception:
            return False

    def print_all_windows(self) -> None:
        """打印所有窗口信息（调试用）"""
        windows = self.list_windows()
        print(f"共找到 {len(windows)} 个窗口:")
        for i, win in enumerate(windows):
            print(f"  [{i}] hwnd={win.hwnd} pid={win.process_id} "
                  f"pos=({win.x},{win.y}) size={win.width}x{win.height} "
                  f"title='{win.title[:50]}'")
