# -*- coding: utf-8 -*-
"""
窗口管理面板
提供窗口列举、查找、激活、移动、调整大小的可视化操作
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, QTimer


class WindowPanel(QWidget):
    """窗口管理面板"""

    def __init__(self, window_controller, logger, parent=None):
        super().__init__(parent)
        self.window_ctrl = window_controller
        self.logger = logger
        self._init_ui()
        self._refresh_windows()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 工具栏
        toolbar = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新窗口列表")
        self.refresh_btn.clicked.connect(self._refresh_windows)
        toolbar.addWidget(self.refresh_btn)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按标题搜索窗口...")
        self.search_input.returnPressed.connect(self._search_window)
        toolbar.addWidget(self.search_input)

        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self._search_window)
        toolbar.addWidget(self.search_btn)

        self.only_visible = QComboBox()
        self.only_visible.addItems(["仅可见窗口", "全部窗口"])
        toolbar.addWidget(self.only_visible)

        layout.addLayout(toolbar)

        # 窗口列表
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["句柄", "标题", "PID", "位置", "大小", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)

        # 窗口操作
        action_group = QGroupBox("窗口操作")
        action_layout = QGridLayout(action_group)

        self.activate_btn = QPushButton("激活窗口")
        self.activate_btn.clicked.connect(self._on_activate)
        action_layout.addWidget(self.activate_btn, 0, 0)

        self.minimize_btn = QPushButton("最小化")
        self.minimize_btn.clicked.connect(self._on_minimize)
        action_layout.addWidget(self.minimize_btn, 0, 1)

        self.maximize_btn = QPushButton("最大化")
        self.maximize_btn.clicked.connect(self._on_maximize)
        action_layout.addWidget(self.maximize_btn, 0, 2)

        self.restore_btn = QPushButton("还原")
        self.restore_btn.clicked.connect(self._on_restore)
        action_layout.addWidget(self.restore_btn, 0, 3)

        self.close_btn = QPushButton("关闭窗口")
        self.close_btn.clicked.connect(self._on_close)
        action_layout.addWidget(self.close_btn, 0, 4)

        # 移动调整
        action_layout.addWidget(QLabel("X:"), 1, 0)
        self.move_x = QSpinBox()
        self.move_x.setRange(-10000, 10000)
        action_layout.addWidget(self.move_x, 1, 1)

        action_layout.addWidget(QLabel("Y:"), 1, 2)
        self.move_y = QSpinBox()
        self.move_y.setRange(-10000, 10000)
        action_layout.addWidget(self.move_y, 1, 3)

        self.move_btn = QPushButton("移动窗口")
        self.move_btn.clicked.connect(self._on_move)
        action_layout.addWidget(self.move_btn, 1, 4)

        action_layout.addWidget(QLabel("宽:"), 2, 0)
        self.resize_w = QSpinBox()
        self.resize_w.setRange(1, 10000)
        self.resize_w.setValue(800)
        action_layout.addWidget(self.resize_w, 2, 1)

        action_layout.addWidget(QLabel("高:"), 2, 2)
        self.resize_h = QSpinBox()
        self.resize_h.setRange(1, 10000)
        self.resize_h.setValue(600)
        action_layout.addWidget(self.resize_h, 2, 3)

        self.resize_btn = QPushButton("调整大小")
        self.resize_btn.clicked.connect(self._on_resize)
        action_layout.addWidget(self.resize_btn, 2, 4)

        self.topmost_btn = QPushButton("切换置顶")
        self.topmost_btn.clicked.connect(self._on_topmost)
        action_layout.addWidget(self.topmost_btn, 3, 0, 1, 5)

        layout.addWidget(action_group)

        # 自动刷新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_windows)
        self.timer.start(5000)

    def _refresh_windows(self):
        only_visible = self.only_visible.currentIndex() == 0
        windows = self.window_ctrl.list_windows(only_visible=only_visible)
        self.table.setRowCount(len(windows))
        for row, win in enumerate(windows):
            self.table.setItem(row, 0, QTableWidgetItem(str(win.hwnd)))
            self.table.setItem(row, 1, QTableWidgetItem(win.title))
            self.table.setItem(row, 2, QTableWidgetItem(str(win.process_id)))
            self.table.setItem(row, 3, QTableWidgetItem(f"({win.x}, {win.y})"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{win.width}x{win.height}"))
            status = "可见" if win.visible else "隐藏"
            if self.window_ctrl.is_minimized(win.hwnd):
                status = "最小化"
            elif self.window_ctrl.is_maximized(win.hwnd):
                status = "最大化"
            self.table.setItem(row, 5, QTableWidgetItem(status))

    def _get_selected_hwnd(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择一个窗口")
            return None
        return int(self.table.item(row, 0).text())

    def _on_double_click(self, row, col):
        hwnd = int(self.table.item(row, 0).text())
        self.window_ctrl.activate(hwnd)

    def _search_window(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            self._refresh_windows()
            return
        windows = self.window_ctrl.find_windows(keyword)
        self.table.setRowCount(len(windows))
        for row, win in enumerate(windows):
            self.table.setItem(row, 0, QTableWidgetItem(str(win.hwnd)))
            self.table.setItem(row, 1, QTableWidgetItem(win.title))
            self.table.setItem(row, 2, QTableWidgetItem(str(win.process_id)))
            self.table.setItem(row, 3, QTableWidgetItem(f"({win.x}, {win.y})"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{win.width}x{win.height}"))
            self.table.setItem(row, 5, QTableWidgetItem("匹配"))

    def _on_activate(self):
        hwnd = self._get_selected_hwnd()
        if hwnd:
            self.window_ctrl.activate(hwnd)

    def _on_minimize(self):
        hwnd = self._get_selected_hwnd()
        if hwnd:
            self.window_ctrl.minimize(hwnd)

    def _on_maximize(self):
        hwnd = self._get_selected_hwnd()
        if hwnd:
            self.window_ctrl.maximize(hwnd)

    def _on_restore(self):
        hwnd = self._get_selected_hwnd()
        if hwnd:
            self.window_ctrl.restore(hwnd)

    def _on_close(self):
        hwnd = self._get_selected_hwnd()
        if hwnd:
            reply = QMessageBox.question(
                self, "确认", "确定要关闭此窗口吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.window_ctrl.close(hwnd)

    def _on_move(self):
        hwnd = self._get_selected_hwnd()
        if hwnd:
            self.window_ctrl.move(hwnd, self.move_x.value(), self.move_y.value())

    def _on_resize(self):
        hwnd = self._get_selected_hwnd()
        if hwnd:
            self.window_ctrl.resize(hwnd, self.resize_w.value(), self.resize_h.value())

    def _on_topmost(self):
        hwnd = self._get_selected_hwnd()
        if hwnd:
            self.window_ctrl.always_on_top(hwnd, enable=True)
