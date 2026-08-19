# -*- coding: utf-8 -*-
"""
Desktop Controller - 桌面自动化控制工具

功能完整的桌面自动化控制套件，支持鼠标、键盘、屏幕、窗口、进程管理及宏录制回放。
"""

__version__ = "1.0.0"
__author__ = "Desktop Controller Team"

from .core.mouse import MouseController
from .core.keyboard import KeyboardController
from .core.screen import ScreenController
from .core.window import WindowController
from .core.process import ProcessController
from .core.file_manager import FileManager

__all__ = [
    "MouseController",
    "KeyboardController",
    "ScreenController",
    "WindowController",
    "ProcessController",
    "FileManager",
]
