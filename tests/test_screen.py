# -*- coding: utf-8 -*-
"""
屏幕控制器单元测试
"""

import pytest
import os
import tempfile
from desktop_controller.core.screen import ScreenController


@pytest.fixture
def screen():
    return ScreenController()


class TestScreenController:
    """屏幕控制器测试"""

    def test_screen_size(self, screen):
        """测试屏幕尺寸"""
        w, h = screen.size
        assert w > 0
        assert h > 0
        assert screen.width == w
        assert screen.height == h

    def test_capture_fullscreen(self, screen):
        """测试全屏截图"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            filepath = f.name

        try:
            img = screen.capture(filepath)
            assert img is not None
            assert img.size[0] == screen.width
            assert img.size[1] == screen.height
            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_capture_region(self, screen):
        """测试区域截图"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            filepath = f.name

        try:
            img = screen.capture_region(0, 0, 200, 200, filepath)
            assert img is not None
            assert img.size[0] == 200
            assert img.size[1] == 200
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_get_pixel_color(self, screen):
        """测试像素颜色获取"""
        r, g, b = screen.get_pixel_color(0, 0)
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255

    def test_pixel_matches(self, screen):
        """测试像素匹配"""
        r, g, b = screen.get_pixel_color(10, 10)
        # 相同颜色应该匹配
        assert screen.pixel_matches(10, 10, (r, g, b), tolerance=0)
        # 大容差应该匹配
        assert screen.pixel_matches(10, 10, (r, g, b), tolerance=50)

    def test_find_image_not_found(self, screen):
        """测试找不到图像时返回None"""
        # 使用一个不存在的图像路径
        result = screen.find_image("nonexistent_image_12345.png")
        assert result is None

    def test_capture_no_save(self, screen):
        """测试不保存文件的截图"""
        img = screen.capture()
        assert img is not None
        assert img.size[0] > 0
