# -*- coding: utf-8 -*-
"""
宏录制回放面板
提供宏录制、保存、加载、回放的可视化操作
"""

import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTextEdit, QFileDialog, QMessageBox,
    QProgressBar, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal


class PlaybackThread(QThread):
    """回放线程（避免阻塞UI）"""
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(int, int)

    def __init__(self, player, events, speed, repeat):
        super().__init__()
        self.player = player
        self.events = events
        self.speed = speed
        self.repeat = repeat

    def run(self):
        try:
            self.player.on_progress = self._on_progress
            success = self.player.play(
                self.events, speed=self.speed, repeat=self.repeat
            )
            self.finished_signal.emit(success, "回放完成" if success else "回放失败")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

    def _on_progress(self, current, total):
        self.progress_signal.emit(current, total)


class MacroPanel(QWidget):
    """宏录制回放面板"""

    def __init__(self, recorder, player, logger, parent=None):
        super().__init__(parent)
        self.recorder = recorder
        self.player = player
        self.logger = logger
        self.current_events = []
        self.playback_thread = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 录制控制
        record_group = QGroupBox("录制控制")
        record_layout = QGridLayout(record_group)

        self.record_btn = QPushButton("开始录制 (F9停止)")
        self.record_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.record_btn.clicked.connect(self._on_record)
        record_layout.addWidget(self.record_btn, 0, 0)

        self.stop_btn = QPushButton("停止录制")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_btn.clicked.connect(self._on_stop)
        record_layout.addWidget(self.stop_btn, 0, 1)

        self.record_status = QLabel("状态: 未录制")
        record_layout.addWidget(self.record_status, 0, 2)

        self.event_count_label = QLabel("事件数: 0")
        record_layout.addWidget(self.event_count_label, 0, 3)

        layout.addWidget(record_group)

        # 文件操作
        file_group = QGroupBox("宏文件")
        file_layout = QGridLayout(file_group)

        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("宏文件路径 (.json)")
        file_layout.addWidget(self.file_path, 0, 0, 1, 2)

        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(self.browse_btn, 0, 2)

        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self._on_save)
        file_layout.addWidget(self.save_btn, 1, 0)

        self.load_btn = QPushButton("加载")
        self.load_btn.clicked.connect(self._on_load)
        file_layout.addWidget(self.load_btn, 1, 1)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self._on_clear)
        file_layout.addWidget(self.clear_btn, 1, 2)

        layout.addWidget(file_group)

        # 回放控制
        play_group = QGroupBox("回放控制")
        play_layout = QGridLayout(play_group)

        play_layout.addWidget(QLabel("速度:"), 0, 0)
        self.speed = QDoubleSpinBox()
        self.speed.setRange(0.1, 10.0)
        self.speed.setSingleStep(0.1)
        self.speed.setValue(1.0)
        play_layout.addWidget(self.speed, 0, 1)

        play_layout.addWidget(QLabel("重复次数:"), 0, 2)
        self.repeat = QSpinBox()
        self.repeat.setRange(1, 999)
        self.repeat.setValue(1)
        play_layout.addWidget(self.repeat, 0, 3)

        self.play_btn = QPushButton("开始回放")
        self.play_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.play_btn.clicked.connect(self._on_play)
        play_layout.addWidget(self.play_btn, 1, 0)

        self.stop_play_btn = QPushButton("停止回放")
        self.stop_play_btn.setEnabled(False)
        self.stop_play_btn.clicked.connect(self._on_stop_play)
        play_layout.addWidget(self.stop_play_btn, 1, 1)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        play_layout.addWidget(self.progress, 1, 2, 1, 2)

        layout.addWidget(play_group)

        # 事件列表
        event_group = QGroupBox("事件列表")
        event_layout = QVBoxLayout(event_group)
        self.event_list = QListWidget()
        event_layout.addWidget(self.event_list)
        layout.addWidget(event_group)

        # 录制状态定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_record_status)
        self.timer.start(200)

    def _on_record(self):
        self.recorder.start()
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.record_status.setText("状态: 录制中...")
        self.logger.info("开始录制宏")

    def _on_stop(self):
        events = self.recorder.stop()
        self.current_events = events
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.record_status.setText("状态: 录制完成")
        self._update_event_list()
        self.logger.info(f"停止录制，共 {len(events)} 个事件")

    def _update_record_status(self):
        if self.recorder.is_recording:
            self.event_count_label.setText(f"事件数: {self.recorder.event_count}")

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择宏文件", "", "JSON (*.json)"
        )
        if path:
            self.file_path.setText(path)

    def _on_save(self):
        path = self.file_path.text().strip()
        if not path:
            path, _ = QFileDialog.getSaveFileName(
                self, "保存宏", "macro.json", "JSON (*.json)"
            )
            if path:
                self.file_path.setText(path)
        if path:
            if self.recorder.save(path):
                QMessageBox.information(self, "成功", f"宏已保存到: {path}")
            else:
                QMessageBox.warning(self, "失败", "保存失败")

    def _on_load(self):
        path = self.file_path.text().strip()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "错误", "请选择有效的宏文件")
            return
        self.current_events = self.recorder.load(path)
        self._update_event_list()
        self.record_status.setText(f"状态: 已加载 {len(self.current_events)} 个事件")

    def _on_clear(self):
        self.current_events = []
        self.recorder.events = []
        self.event_list.clear()
        self.event_count_label.setText("事件数: 0")
        self.record_status.setText("状态: 已清空")

    def _update_event_list(self):
        self.event_list.clear()
        for i, event in enumerate(self.current_events[:500]):  # 最多显示500条
            t = event.get("type", "?")
            time_val = event.get("time", 0)
            if t == "mouse_move":
                text = f"[{i}] {time:.2f}s 移动 ({event.get('x')}, {event.get('y')})"
            elif t == "mouse_click":
                text = f"[{i}] {time:.2f}s 点击 {event.get('button')} {'按下' if event.get('pressed') else '释放'}"
            elif t == "mouse_scroll":
                text = f"[{i}] {time:.2f}s 滚动 dy={event.get('dy')}"
            elif t == "key_press":
                text = f"[{i}] {time:.2f}s 按键按下 {event.get('key')}"
            elif t == "key_release":
                text = f"[{i}] {time:.2f}s 按键释放 {event.get('key')}"
            else:
                text = f"[{i}] {time:.2f}s {t}"
            self.event_list.addItem(QListWidgetItem(text))

        self.event_count_label.setText(f"事件数: {len(self.current_events)}")

    def _on_play(self):
        if not self.current_events:
            QMessageBox.information(self, "提示", "没有可回放的事件，请先录制或加载宏")
            return

        self.play_btn.setEnabled(False)
        self.stop_play_btn.setEnabled(True)
        self.progress.setValue(0)

        self.playback_thread = PlaybackThread(
            self.player, self.current_events,
            self.speed.value(), self.repeat.value()
        )
        self.playback_thread.progress_signal.connect(self._on_progress)
        self.playback_thread.finished_signal.connect(self._on_playback_finished)
        self.playback_thread.start()

    def _on_stop_play(self):
        if self.playback_thread:
            self.player.stop()

    def _on_progress(self, current, total):
        if total > 0:
            self.progress.setValue(int(current / total * 100))

    def _on_playback_finished(self, success, message):
        self.play_btn.setEnabled(True)
        self.stop_play_btn.setEnabled(False)
        self.progress.setValue(100 if success else 0)
        if success:
            QMessageBox.information(self, "完成", message)
        else:
            QMessageBox.warning(self, "错误", message)
