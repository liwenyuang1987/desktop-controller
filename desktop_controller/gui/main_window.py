# -*- coding: utf-8 -*-
"""
主窗口
桌面控制器的GUI主界面，包含标签页切换各功能模块
"""

import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QStatusBar, QAction, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from ..core.mouse import MouseController
from ..core.keyboard import KeyboardController
from ..core.screen import ScreenController
from ..core.window import WindowController
from ..core.process import ProcessController
from ..core.file_manager import FileManager
from ..macro.recorder import MacroRecorder
from ..macro.player import MacroPlayer
from ..macro.scheduler import TaskScheduler
from ..utils.config import ConfigManager
from ..utils.logger import get_logger

from .mouse_panel import MousePanel
from .keyboard_panel import KeyboardPanel
from .screen_panel import ScreenPanel
from .window_panel import WindowPanel
from .process_panel import ProcessPanel
from .macro_panel import MacroPanel


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.logger = get_logger("gui")
        self.config = ConfigManager()

        # 初始化控制器
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.screen = ScreenController()
        self.window_ctrl = WindowController()
        self.process_ctrl = ProcessController()
        self.file_mgr = FileManager()
        self.macro_recorder = MacroRecorder()
        self.macro_player = MacroPlayer()
        self.scheduler = TaskScheduler()
        self.scheduler.start()

        self._init_ui()
        self._init_menu()
        self._init_statusbar()
        self._start_position_timer()

        self.logger.info("主窗口初始化完成")

    def _init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Desktop Controller - 桌面自动化控制工具")
        width = self.config.get("ui.window_width", 900)
        height = self.config.get("ui.window_height", 650)
        self.resize(width, height)

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)

        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)

        # 添加各功能面板
        self.mouse_panel = MousePanel(self.mouse, self.logger)
        self.keyboard_panel = KeyboardPanel(self.keyboard, self.logger)
        self.screen_panel = ScreenPanel(self.screen, self.logger)
        self.window_panel = WindowPanel(self.window_ctrl, self.logger)
        self.process_panel = ProcessPanel(self.process_ctrl, self.logger)
        self.macro_panel = MacroPanel(
            self.macro_recorder, self.macro_player, self.logger
        )

        self.tabs.addTab(self.mouse_panel, "鼠标控制")
        self.tabs.addTab(self.keyboard_panel, "键盘控制")
        self.tabs.addTab(self.screen_panel, "屏幕操作")
        self.tabs.addTab(self.window_panel, "窗口管理")
        self.tabs.addTab(self.process_panel, "进程管理")
        self.tabs.addTab(self.macro_panel, "宏录制回放")

        layout.addWidget(self.tabs)

    def _init_menu(self):
        """初始化菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        exit_action = QAction("退出(&Q)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        screenshot_action = QAction("快速截图", self)
        screenshot_action.setShortcut("F2")
        screenshot_action.triggered.connect(self._quick_screenshot)
        tools_menu.addAction(screenshot_action)

        tools_menu.addSeparator()

        always_top_action = QAction("窗口置顶", self, checkable=True)
        always_top_action.setChecked(self.config.get("ui.always_on_top", False))
        always_top_action.triggered.connect(self._toggle_always_on_top)
        tools_menu.addAction(always_top_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _init_statusbar(self):
        """初始化状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.position_label = QLabel("鼠标位置: (0, 0)")
        self.statusbar.addWidget(self.position_label)

        self.status_label = QLabel("就绪")
        self.statusbar.addPermanentWidget(self.status_label)

    def _start_position_timer(self):
        """启动鼠标位置更新定时器"""
        self.pos_timer = QTimer(self)
        self.pos_timer.timeout.connect(self._update_mouse_position)
        self.pos_timer.start(100)

    def _update_mouse_position(self):
        """更新鼠标位置显示"""
        try:
            x, y = self.mouse.position
            self.position_label.setText(f"鼠标位置: ({x}, {y})")
        except Exception:
            pass

    def _quick_screenshot(self):
        """快速截图"""
        try:
            from datetime import datetime
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)
            self.screen.capture(filepath)
            self.status_label.setText(f"截图已保存: {filepath}")
            self.logger.info(f"快速截图: {filepath}")
        except Exception as e:
            QMessageBox.warning(self, "截图失败", str(e))

    def _toggle_always_on_top(self, checked):
        """切换窗口置顶"""
        self.setWindowFlag(Qt.WindowStaysOnTopHint, checked)
        self.show()
        self.config.set("ui.always_on_top", checked)
        self.config.save()

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 Desktop Controller",
            """<h3>Desktop Controller v1.0.0</h3>
            <p>功能完整的桌面自动化控制工具</p>
            <p>功能：鼠标控制 / 键盘控制 / 屏幕操作 / 窗口管理 / 进程管理 / 宏录制回放</p>
            <p>基于 Python + PyQt5 + pyautogui 开发</p>
            <p><a href='https://github.com/liwenyuang1987/desktop-controller'>GitHub 仓库</a></p>""",
        )

    def closeEvent(self, event):
        """关闭事件"""
        # 保存窗口大小
        self.config.set("ui.window_width", self.width())
        self.config.set("ui.window_height", self.height())
        self.config.save()

        # 停止调度器
        self.scheduler.stop()

        # 停止宏录制（如果正在录制）
        if self.macro_recorder.is_recording:
            self.macro_recorder.stop()

        self.logger.info("程序退出")
        event.accept()
