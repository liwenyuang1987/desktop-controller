# -*- coding: utf-8 -*-
"""
屏幕操作面板
提供截图、像素颜色、图像匹配的可视化操作
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
import io


class ScreenPanel(QWidget):
    """屏幕操作面板"""

    def __init__(self, screen_controller, logger, parent=None):
        super().__init__(parent)
        self.screen = screen_controller
        self.logger = logger
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 屏幕信息
        info_group = QGroupBox("屏幕信息")
        info_layout = QHBoxLayout(info_group)
        w, h = self.screen.size
        self.info_label = QLabel(f"分辨率: {w} x {h}")
        info_layout.addWidget(self.info_label)
        layout.addWidget(info_group)

        # 截图控制
        capture_group = QGroupBox("截图")
        capture_layout = QGridLayout(capture_group)

        self.fullscreen_btn = QPushButton("全屏截图")
        self.fullscreen_btn.clicked.connect(self._on_fullscreen_capture)
        capture_layout.addWidget(self.fullscreen_btn, 0, 0)

        self.region_btn = QPushButton("区域截图")
        self.region_btn.clicked.connect(self._on_region_capture)
        capture_layout.addWidget(self.region_btn, 0, 1)

        capture_layout.addWidget(QLabel("X:"), 1, 0)
        self.cap_x = QSpinBox()
        self.cap_x.setRange(0, 99999)
        capture_layout.addWidget(self.cap_x, 1, 1)

        capture_layout.addWidget(QLabel("Y:"), 1, 2)
        self.cap_y = QSpinBox()
        self.cap_y.setRange(0, 99999)
        capture_layout.addWidget(self.cap_y, 1, 3)

        capture_layout.addWidget(QLabel("宽:"), 2, 0)
        self.cap_w = QSpinBox()
        self.cap_w.setRange(1, 99999)
        self.cap_w.setValue(800)
        capture_layout.addWidget(self.cap_w, 2, 1)

        capture_layout.addWidget(QLabel("高:"), 2, 2)
        self.cap_h = QSpinBox()
        self.cap_h.setRange(1, 99999)
        self.cap_h.setValue(600)
        capture_layout.addWidget(self.cap_h, 2, 3)

        self.save_path = QLineEdit()
        self.save_path.setPlaceholderText("保存路径（留空则不保存）")
        capture_layout.addWidget(self.save_path, 3, 0, 1, 3)

        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._browse_save_path)
        capture_layout.addWidget(self.browse_btn, 3, 3)

        layout.addWidget(capture_group)

        # 截图预览
        preview_group = QGroupBox("截图预览")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel("暂无截图")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)

        # 像素颜色
        pixel_group = QGroupBox("像素颜色")
        pixel_layout = QGridLayout(pixel_group)

        pixel_layout.addWidget(QLabel("X:"), 0, 0)
        self.pixel_x = QSpinBox()
        self.pixel_x.setRange(0, 99999)
        pixel_layout.addWidget(self.pixel_x, 0, 1)

        pixel_layout.addWidget(QLabel("Y:"), 0, 2)
        self.pixel_y = QSpinBox()
        self.pixel_y.setRange(0, 99999)
        pixel_layout.addWidget(self.pixel_y, 0, 3)

        self.get_color_btn = QPushButton("获取颜色")
        self.get_color_btn.clicked.connect(self._on_get_color)
        pixel_layout.addWidget(self.get_color_btn, 1, 0, 1, 2)

        self.color_display = QLabel("RGB: (0, 0, 0)")
        self.color_display.setMinimumHeight(30)
        self.color_display.setAlignment(Qt.AlignCenter)
        pixel_layout.addWidget(self.color_display, 1, 2, 1, 2)

        layout.addWidget(pixel_group)

        # 图像匹配
        match_group = QGroupBox("图像匹配定位")
        match_layout = QGridLayout(match_group)

        self.template_path = QLineEdit()
        self.template_path.setPlaceholderText("模板图像路径")
        match_layout.addWidget(self.template_path, 0, 0, 1, 3)

        self.template_browse = QPushButton("浏览...")
        self.template_browse.clicked.connect(self._browse_template)
        match_layout.addWidget(self.template_browse, 0, 3)

        match_layout.addWidget(QLabel("置信度:"), 1, 0)
        self.confidence = QDoubleSpinBox()
        self.confidence.setRange(0.1, 1.0)
        self.confidence.setSingleStep(0.05)
        self.confidence.setValue(0.8)
        match_layout.addWidget(self.confidence, 1, 1)

        self.find_btn = QPushButton("查找图像")
        self.find_btn.clicked.connect(self._on_find_image)
        match_layout.addWidget(self.find_btn, 1, 2, 1, 2)

        self.match_result = QLabel("结果: 未查找")
        match_layout.addWidget(self.match_result, 2, 0, 1, 4)

        layout.addWidget(match_group)

        layout.addStretch()

    def _on_fullscreen_capture(self):
        path = self.save_path.text().strip() or None
        if not path:
            path = os.path.join(
                os.path.expanduser("~"), "Desktop",
                f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
        img = self.screen.capture(path)
        self._show_preview(img)
        self.logger.info(f"全屏截图: {path}")

    def _on_region_capture(self):
        path = self.save_path.text().strip() or None
        if not path:
            path = os.path.join(
                os.path.expanduser("~"), "Desktop",
                f"region_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
        img = self.screen.capture_region(
            self.cap_x.value(), self.cap_y.value(),
            self.cap_w.value(), self.cap_h.value(), path
        )
        self._show_preview(img)

    def _show_preview(self, pil_image):
        """在预览区显示PIL图像"""
        try:
            buf = io.BytesIO()
            pil_image.save(buf, format='PNG')
            qimg = QImage.fromData(buf.getvalue())
            pixmap = QPixmap.fromImage(qimg)
            scaled = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
        except Exception as e:
            self.preview_label.setText(f"预览失败: {e}")

    def _browse_save_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存截图", "", "PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        if path:
            self.save_path.setText(path)

    def _browse_template(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择模板图像", "", "图像 (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.template_path.setText(path)

    def _on_get_color(self):
        r, g, b = self.screen.get_pixel_color(self.pixel_x.value(), self.pixel_y.value())
        self.color_display.setText(f"RGB: ({r}, {g}, {b})")
        self.color_display.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); color: {'white' if (r+g+b) < 384 else 'black'};"
        )

    def _on_find_image(self):
        path = self.template_path.text().strip()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "错误", "请选择有效的模板图像")
            return
        pos = self.screen.find_image(path, confidence=self.confidence.value())
        if pos:
            self.match_result.setText(f"结果: 找到位置 ({pos[0]}, {pos[1]})")
        else:
            self.match_result.setText("结果: 未找到匹配")
