# -*- coding: utf-8 -*-
"""
进程管理面板
提供进程列举、查找、启动、终止、资源监控的可视化操作
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer


class ProcessPanel(QWidget):
    """进程管理面板"""

    def __init__(self, process_controller, logger, parent=None):
        super().__init__(parent)
        self.process_ctrl = process_controller
        self.logger = logger
        self._init_ui()
        self._refresh_processes()
        self._refresh_system_info()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 系统资源监控
        sys_group = QGroupBox("系统资源")
        sys_layout = QGridLayout(sys_group)

        sys_layout.addWidget(QLabel("CPU:"), 0, 0)
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        sys_layout.addWidget(self.cpu_bar, 0, 1)

        self.cpu_label = QLabel("0%")
        sys_layout.addWidget(self.cpu_label, 0, 2)

        sys_layout.addWidget(QLabel("内存:"), 1, 0)
        self.mem_bar = QProgressBar()
        self.mem_bar.setRange(0, 100)
        sys_layout.addWidget(self.mem_bar, 1, 1)

        self.mem_label = QLabel("0% (0/0 GB)")
        sys_layout.addWidget(self.mem_label, 1, 2)

        layout.addWidget(sys_group)

        # 工具栏
        toolbar = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._refresh_processes)
        toolbar.addWidget(self.refresh_btn)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按进程名搜索...")
        self.search_input.returnPressed.connect(self._search_process)
        toolbar.addWidget(self.search_input)

        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self._search_process)
        toolbar.addWidget(self.search_btn)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["按CPU排序", "按内存排序", "按PID排序", "按名称排序"])
        self.sort_combo.currentIndexChanged.connect(self._refresh_processes)
        toolbar.addWidget(self.sort_combo)

        layout.addLayout(toolbar)

        # 进程列表
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["PID", "名称", "CPU%", "内存(MB)", "线程数", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        # 进程操作
        action_group = QGroupBox("进程操作")
        action_layout = QGridLayout(action_group)

        action_layout.addWidget(QLabel("启动程序:"), 0, 0)
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("可执行文件路径或命令")
        action_layout.addWidget(self.start_input, 0, 1, 1, 2)

        self.start_btn = QPushButton("启动")
        self.start_btn.clicked.connect(self._on_start)
        action_layout.addWidget(self.start_btn, 0, 3)

        self.terminate_btn = QPushButton("终止进程")
        self.terminate_btn.clicked.connect(self._on_terminate)
        action_layout.addWidget(self.terminate_btn, 1, 0)

        self.kill_btn = QPushButton("强制终止")
        self.kill_btn.clicked.connect(self._on_kill)
        action_layout.addWidget(self.kill_btn, 1, 1)

        self.terminate_name_btn = QPushButton("按名称终止")
        self.terminate_name_btn.clicked.connect(self._on_terminate_by_name)
        action_layout.addWidget(self.terminate_name_btn, 1, 2)

        self.top_btn = QPushButton("Top 10 CPU")
        self.top_btn.clicked.connect(self._show_top_cpu)
        action_layout.addWidget(self.top_btn, 1, 3)

        layout.addWidget(action_group)

        # 自动刷新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_processes)
        self.timer.timeout.connect(self._refresh_system_info)
        self.timer.start(3000)

    def _refresh_system_info(self):
        try:
            cpu = self.process_ctrl.get_cpu_percent(interval=0)
            self.cpu_bar.setValue(int(cpu))
            self.cpu_label.setText(f"{cpu:.1f}%")

            mem = self.process_ctrl.get_memory_info()
            self.mem_bar.setValue(int(mem["percent"]))
            self.mem_label.setText(
                f"{mem['percent']:.1f}% ({mem['used_gb']}/{mem['total_gb']} GB)"
            )
        except Exception:
            pass

    def _refresh_processes(self):
        processes = self.process_ctrl.list_processes(refresh_cpu=False)

        sort_idx = self.sort_combo.currentIndex()
        if sort_idx == 0:
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        elif sort_idx == 1:
            processes.sort(key=lambda p: p.memory_mb, reverse=True)
        elif sort_idx == 2:
            processes.sort(key=lambda p: p.pid)
        else:
            processes.sort(key=lambda p: p.name.lower())

        # 限制显示数量
        processes = processes[:200]

        self.table.setRowCount(len(processes))
        for row, p in enumerate(processes):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.pid)))
            self.table.setItem(row, 1, QTableWidgetItem(p.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{p.cpu_percent:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{p.memory_mb:.1f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.num_threads)))
            self.table.setItem(row, 5, QTableWidgetItem(p.status))

    def _search_process(self):
        name = self.search_input.text().strip()
        if not name:
            self._refresh_processes()
            return
        processes = self.process_ctrl.find_by_name(name)
        self.table.setRowCount(len(processes))
        for row, p in enumerate(processes):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.pid)))
            self.table.setItem(row, 1, QTableWidgetItem(p.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{p.cpu_percent:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{p.memory_mb:.1f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.num_threads)))
            self.table.setItem(row, 5, QTableWidgetItem(p.status))

    def _get_selected_pid(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择一个进程")
            return None
        return int(self.table.item(row, 0).text())

    def _on_start(self):
        cmd = self.start_input.text().strip()
        if cmd:
            self.process_ctrl.start_process(cmd)
            self.logger.info(f"启动进程: {cmd}")

    def _on_terminate(self):
        pid = self._get_selected_pid()
        if pid:
            reply = QMessageBox.question(
                self, "确认", f"确定终止进程 PID {pid}？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.process_ctrl.terminate(pid)
                self._refresh_processes()

    def _on_kill(self):
        pid = self._get_selected_pid()
        if pid:
            reply = QMessageBox.question(
                self, "确认", f"确定强制终止进程 PID {pid}？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.process_ctrl.kill(pid)
                self._refresh_processes()

    def _on_terminate_by_name(self):
        name = self.search_input.text().strip()
        if name:
            count = self.process_ctrl.terminate_by_name(name)
            QMessageBox.information(self, "结果", f"已终止 {count} 个进程")
            self._refresh_processes()

    def _show_top_cpu(self):
        self.process_ctrl.print_top_processes(10, by="cpu")
        self.sort_combo.setCurrentIndex(0)
        self._refresh_processes()
