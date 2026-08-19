# -*- coding: utf-8 -*-
"""
鼠标控制面板
提供鼠标移动、点击、拖拽、滚动的可视化操作
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class MousePanel(QWidget):
    """鼠标控制面板"""

    def __init__(self, mouse_controller, logger, parent=None):
        super().__init__(parent)
        self.mouse = mouse_controller
        self.logger = logger
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 当前位置显示
        pos_group = QGroupBox("当前状态")
        pos_layout = QHBoxLayout(pos_group)
        self.pos_label = QLabel("X: 0, Y: 0")
        self.pos_label.setFont(QFont("Consolas", 14))
        self.pos_label.setAlignment(Qt.AlignCenter)
        pos_layout.addWidget(self.pos_label)

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._refresh_position)
        pos_layout.addWidget(self.refresh_btn)
        layout.addWidget(pos_group)

        # 移动控制
        move_group = QGroupBox("鼠标移动")
        move_layout = QGridLayout(move_group)

        move_layout.addWidget(QLabel("目标 X:"), 0, 0)
        self.move_x = QSpinBox()
        self.move_x.setRange(0, 99999)
        self.move_x.setValue(500)
        move_layout.addWidget(self.move_x, 0, 1)

        move_layout.addWidget(QLabel("目标 Y:"), 0, 2)
        self.move_y = QSpinBox()
        self.move_y.setRange(0, 99999)
        self.move_y.setValue(300)
        move_layout.addWidget(self.move_y, 0, 3)

        move_layout.addWidget(QLabel("持续时间(s):"), 1, 0)
        self.move_duration = QDoubleSpinBox()
        self.move_duration.setRange(0, 10)
        self.move_duration.setSingleStep(0.1)
        self.move_duration.setValue(0.0)
        move_layout.addWidget(self.move_duration, 1, 1)

        self.move_btn = QPushButton("移动到")
        self.move_btn.clicked.connect(self._on_move)
        move_layout.addWidget(self.move_btn, 1, 2, 1, 2)

        # 相对移动
        rel_layout = QHBoxLayout()
        self.rel_dx = QSpinBox()
        self.rel_dx.setRange(-9999, 9999)
        self.rel_dx.setValue(100)
        rel_layout.addWidget(QLabel("DX:"))
        rel_layout.addWidget(self.rel_dx)

        self.rel_dy = QSpinBox()
        self.rel_dy.setRange(-9999, 9999)
        self.rel_dy.setValue(0)
        rel_layout.addWidget(QLabel("DY:"))
        rel_layout.addWidget(self.rel_dy)

        self.rel_btn = QPushButton("相对移动")
        self.rel_btn.clicked.connect(self._on_move_relative)
        rel_layout.addWidget(self.rel_btn)
        move_layout.addLayout(rel_layout, 2, 0, 1, 4)

        layout.addWidget(move_group)

        # 点击控制
        click_group = QGroupBox("鼠标点击")
        click_layout = QGridLayout(click_group)

        click_layout.addWidget(QLabel("按键:"), 0, 0)
        self.click_button = QComboBox()
        self.click_button.addItems(["left", "right", "middle"])
        click_layout.addWidget(self.click_button, 0, 1)

        click_layout.addWidget(QLabel("次数:"), 0, 2)
        self.click_count = QSpinBox()
        self.click_count.setRange(1, 100)
        self.click_count.setValue(1)
        click_layout.addWidget(self.click_count, 0, 3)

        self.click_btn = QPushButton("在当前位置点击")
        self.click_btn.clicked.connect(self._on_click)
        click_layout.addWidget(self.click_btn, 1, 0, 1, 2)

        self.double_btn = QPushButton("双击")
        self.double_btn.clicked.connect(self._on_double_click)
        click_layout.addWidget(self.double_btn, 1, 2)

        self.right_btn = QPushButton("右键")
        self.right_btn.clicked.connect(self._on_right_click)
        click_layout.addWidget(self.right_btn, 1, 3)

        layout.addWidget(click_group)

        # 拖拽控制
        drag_group = QGroupBox("鼠标拖拽")
        drag_layout = QGridLayout(drag_group)

        drag_layout.addWidget(QLabel("起点 X:"), 0, 0)
        self.drag_sx = QSpinBox()
        self.drag_sx.setRange(0, 99999)
        self.drag_sx.setValue(100)
        drag_layout.addWidget(self.drag_sx, 0, 1)

        drag_layout.addWidget(QLabel("起点 Y:"), 0, 2)
        self.drag_sy = QSpinBox()
        self.drag_sy.setRange(0, 99999)
        self.drag_sy.setValue(100)
        drag_layout.addWidget(self.drag_sy, 0, 3)

        drag_layout.addWidget(QLabel("终点 X:"), 1, 0)
        self.drag_ex = QSpinBox()
        self.drag_ex.setRange(0, 99999)
        self.drag_ex.setValue(500)
        drag_layout.addWidget(self.drag_ex, 1, 1)

        drag_layout.addWidget(QLabel("终点 Y:"), 1, 2)
        self.drag_ey = QSpinBox()
        self.drag_ey.setRange(0, 99999)
        self.drag_ey.setValue(300)
        drag_layout.addWidget(self.drag_ey, 1, 3)

        self.drag_btn = QPushButton("执行拖拽")
        self.drag_btn.clicked.connect(self._on_drag)
        drag_layout.addWidget(self.drag_btn, 2, 0, 1, 4)

        layout.addWidget(drag_group)

        # 滚动控制
        scroll_group = QGroupBox("滚轮滚动")
        scroll_layout = QHBoxLayout(scroll_group)

        self.scroll_amount = QSpinBox()
        self.scroll_amount.setRange(-100, 100)
        self.scroll_amount.setValue(3)
        scroll_layout.addWidget(QLabel("滚动量:"))
        scroll_layout.addWidget(self.scroll_amount)

        self.scroll_up_btn = QPushButton("向上")
        self.scroll_up_btn.clicked.connect(lambda: self.mouse.scroll_up(3))
        scroll_layout.addWidget(self.scroll_up_btn)

        self.scroll_down_btn = QPushButton("向下")
        self.scroll_down_btn.clicked.connect(lambda: self.mouse.scroll_down(3))
        scroll_layout.addWidget(self.scroll_down_btn)

        self.scroll_btn = QPushButton("执行")
        self.scroll_btn.clicked.connect(self._on_scroll)
        scroll_layout.addWidget(self.scroll_btn)

        layout.addWidget(scroll_group)

        layout.addStretch()

        # 定时刷新位置
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_position)
        self.timer.start(200)

    def _refresh_position(self):
        try:
            x, y = self.mouse.position
            self.pos_label.setText(f"X: {x}, Y: {y}")
        except Exception:
            pass

    def _on_move(self):
        self.mouse.move(self.move_x.value(), self.move_y.value(), self.move_duration.value())
        self.logger.info(f"鼠标移动到 ({self.move_x.value()}, {self.move_y.value()})")

    def _on_move_relative(self):
        self.mouse.move_relative(self.rel_dx.value(), self.rel_dy.value())

    def _on_click(self):
        self.mouse.click(button=self.click_button.currentText(), clicks=self.click_count.value())

    def _on_double_click(self):
        self.mouse.double_click()

    def _on_right_click(self):
        self.mouse.right_click()

    def _on_drag(self):
        self.mouse.drag(
            self.drag_sx.value(), self.drag_sy.value(),
            self.drag_ex.value(), self.drag_ey.value(),
        )

    def _on_scroll(self):
        self.mouse.scroll(self.scroll_amount.value())
