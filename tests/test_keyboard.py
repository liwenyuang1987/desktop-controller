# -*- coding: utf-8 -*-
"""
键盘控制器单元测试
"""

import pytest
from desktop_controller.core.keyboard import KeyboardController


@pytest.fixture
def keyboard():
    return KeyboardController()


class TestKeyboardController:
    """键盘控制器测试"""

    def test_normalize_key(self, keyboard):
        """测试按键名称标准化"""
        assert keyboard._normalize_key("ENTER") == "enter"
        assert keyboard._normalize_key("Ctrl") == "ctrl"
        assert keyboard._normalize_key("ESC") == "esc"
        assert keyboard._normalize_key("a") == "a"
        assert keyboard._normalize_key("F5") == "f5"

    def test_special_keys_mapping(self, keyboard):
        """测试特殊键映射"""
        assert "enter" in keyboard.SPECIAL_KEYS
        assert "ctrl" in keyboard.SPECIAL_KEYS
        assert "alt" in keyboard.SPECIAL_KEYS
        assert "shift" in keyboard.SPECIAL_KEYS
        assert "win" in keyboard.SPECIAL_KEYS
        assert "f1" in keyboard.SPECIAL_KEYS
        assert "f12" in keyboard.SPECIAL_KEYS

    def test_contains_non_ascii(self):
        """测试非ASCII检测"""
        assert KeyboardController._contains_non_ascii("你好")
        assert KeyboardController._contains_non_ascii("Hello") is False
        assert KeyboardController._contains_non_ascii("Hello你好")
        assert KeyboardController._contains_non_ascii("123!@#") is False

    def test_hotkey_no_exception(self, keyboard):
        """测试组合键不抛异常"""
        # 注意：实际组合键可能影响当前操作
        # keyboard.hotkey("ctrl", "a")  # 取消注释以测试
        pass

    def test_press_no_exception(self, keyboard):
        """测试按键不抛异常"""
        # keyboard.press("enter")  # 取消注释以测试
        pass

    def test_type_text_no_exception(self, keyboard):
        """测试文本输入不抛异常"""
        # keyboard.type_text("test")  # 取消注释以测试
        pass
