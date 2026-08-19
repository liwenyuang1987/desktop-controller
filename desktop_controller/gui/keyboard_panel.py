# -*- coding: utf-8 -*-
"""
键盘控制面板
提供按键、组合键、文本输入的可视化操作
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox,
    QCheckBox, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt


class KeyboardPanel(QWidget):
    """键盘控制面板"""

    def __init__(self, keyboard_controller, logger, parent=None):
        super().__init__(parent)
        self.keyboard = keyboard_controller
        self.logger = logger
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 文本输入
        text_group = QGroupBox("文本输入")
        text_layout = QVBoxLayout(text_group)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("输入要键入的文本（支持中文）")
        text_layout.addWidget(self.text_input)

        btn_row = QHBoxLayout()
        self.type_btn = QPushButton("输入文本")
        self.type_btn.clicked.connect(self._on_type)
        btn_row.addWidget(self.type_btn)

        self.type_line_btn = QPushButton("输入并回车")
        self.type_line_btn.clicked.connect(self._on_type_line)
        btn_row.addWidget(self.type_line_btn)

        self.use_clipboard = QCheckBox("使用剪贴板（中文推荐）")
        self.use_clipboard.setChecked(True)
        btn_row.addWidget(self.use_clipboard)
        text_layout.addLayout(btn_row)

        layout.addWidget(text_group)

        # 单键控制
        key_group = QGroupBox("单键操作")
        key_layout = QGridLayout(key_group)

        key_layout.addWidget(QLabel("按键:"), 0, 0)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("如: enter, a, f5, ctrl")
        key_layout.addWidget(self.key_input, 0, 1)

        key_layout.addWidget(QLabel("次数:"), 0, 2)
        self.key_count = QSpinBox()
        self.key_count.setRange(1, 100)
        self.key_count.setValue(1)
        key_layout.addWidget(self.key_count, 0, 3)

        self.press_btn = QPushButton("按键")
        self.press_btn.clicked.connect(self._on_press)
        key_layout.addWidget(self.press_btn, 1, 0, 1, 2)

        self.key_down_btn = QPushButton("按下不释放")
        self.key_down_btn.clicked.connect(self._on_key_down)
        key_layout.addWidget(self.key_down_btn, 1, 2)

        self.key_up_btn = QPushButton("释放")
        self.key_up_btn.clicked.connect(self._on_key_up)
        key_layout.addWidget(self.key_up_btn, 1, 3)

        layout.addWidget(key_group)

        # 组合键
        combo_group = QGroupBox("组合键")
        combo_layout = QGridLayout(combo_group)

        self.combo_keys = QLineEdit()
        self.combo_keys.setPlaceholderText("用空格分隔，如: ctrl c, alt tab, ctrl shift esc")
        combo_layout.addWidget(self.combo_keys, 0, 0, 1, 4)

        self.combo_btn = QPushButton("执行组合键")
        self.combo_btn.clicked.connect(self._on_hotkey)
        combo_layout.addWidget(self.combo_btn, 1, 0, 1, 4)

        layout.addWidget(combo_group)

        # 常用快捷键
        shortcut_group = QGroupBox("常用快捷键")
        shortcut_layout = QGridLayout(shortcut_group)

        shortcuts = [
            ("全选", "ctrl a"),
            ("复制", "ctrl c"),
            ("剪切", "ctrl x"),
            ("粘贴", "ctrl v"),
            ("撤销", "ctrl z"),
            ("重做", "ctrl y"),
            ("保存", "ctrl s"),
            ("查找", "ctrl f"),
            ("切换窗口", "alt tab"),
            ("关闭窗口", "alt f4"),
            ("任务管理器", "ctrl shift esc"),
            ("显示桌面", "win d"),
            ("运行", "win r"),
            ("资源管理器", "win e"),
            ("锁屏", "win l"),
            ("截图", "win shift s"),
        ]

        for i, (name, keys) in enumerate(shortcuts):
            row = i // 4
            col = i % 4
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, k=keys: self._execute_shortcut(k))
            shortcut_layout.addWidget(btn, row, col)

        layout.addWidget(shortcut_group)

        layout.addStretch()

    def _on_type(self):
        text = self.text_input.text()
        if text:
            self.keyboard.type_text(text, use_clipboard=self.use_clipboard.isChecked())
            self.logger.info(f"输入文本: {text[:30]}")

    def _on_type_line(self):
        text = self.text_input.text()
        if text:
            self.keyboard.type_line(text, use_clipboard=self.use_clipboard.isChecked())

    def _on_press(self):
        key = self.key_input.text().strip()
        if key:
            self.keyboard.press(key, presses=self.key_count.value())

    def _on_key_down(self):
        key = self.key_input.text().strip()
        if key:
            self.keyboard.key_down(key)

    def _on_key_up(self):
        key = self.key_input.text().strip()
        if key:
            self.keyboard.key_up(key)

    def _on_hotkey(self):
        keys = self.combo_keys.text().strip().split()
        if keys:
            self.keyboard.hotkey(*keys)
            self.logger.info(f"组合键: {'+'.join(keys)}")

    def _execute_shortcut(self, keys_str):
        keys = keys_str.split()
        self.keyboard.hotkey(*keys)
