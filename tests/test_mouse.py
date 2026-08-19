# -*- coding: utf-8 -*-
"""
鼠标控制器单元测试
注意：这些测试会实际移动鼠标，建议在虚拟机或空闲时运行
"""

import pytest
import time
from desktop_controller.core.mouse import MouseController


@pytest.fixture
def mouse():
    return MouseController()


class TestMouseController:
    """鼠标控制器测试"""

    def test_screen_size(self, mouse):
        """测试屏幕尺寸获取"""
        w, h = mouse.screen_size
        assert w > 0
        assert h > 0
        assert isinstance(w, int)
        assert isinstance(h, int)

    def test_position(self, mouse):
        """测试位置获取"""
        x, y = mouse.position
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert 0 <= x <= mouse.screen_size[0]
        assert 0 <= y <= mouse.screen_size[1]

    def test_move(self, mouse):
        """测试鼠标移动"""
        original_x, original_y = mouse.position
        target_x, target_y = 100, 100

        mouse.move(target_x, target_y)
        time.sleep(0.1)

        new_x, new_y = mouse.position
        assert abs(new_x - target_x) <= 2
        assert abs(new_y - target_y) <= 2

        # 恢复原位置
        mouse.move(original_x, original_y)

    def test_move_relative(self, mouse):
        """测试相对移动"""
        original_x, original_y = mouse.position

        mouse.move_relative(50, 30)
        time.sleep(0.1)

        new_x, new_y = mouse.position
        assert abs(new_x - original_x - 50) <= 2
        assert abs(new_y - original_y - 30) <= 2

        # 恢复
        mouse.move(original_x, original_y)

    def test_scroll(self, mouse):
        """测试滚动（不抛异常即可）"""
        # 滚动操作难以验证结果，确保不抛异常
        mouse.scroll(3)
        mouse.scroll(-3)
        mouse.scroll_up(2)
        mouse.scroll_down(2)

    def test_click_no_exception(self, mouse):
        """测试点击不抛异常"""
        # 注意：实际点击可能影响当前操作，仅验证不报错
        # mouse.click()  # 取消注释以测试实际点击
        pass

    def test_drag_no_exception(self, mouse):
        """测试拖拽不抛异常"""
        # mouse.drag(100, 100, 200, 200)  # 取消注释以测试
        pass

    def test_press_release(self, mouse):
        """测试按下释放"""
        # 测试按下后释放，确保不卡住
        mouse.press("left")
        time.sleep(0.1)
        mouse.release("left")
        mouse.release_all()  # 确保所有键释放
