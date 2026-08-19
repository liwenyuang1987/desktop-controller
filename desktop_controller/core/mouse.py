# -*- coding: utf-8 -*-
"""
鼠标控制模块
提供鼠标移动、点击、拖拽、滚动等功能
"""

import time
import pyautogui
from typing import Tuple, Optional

# 禁用 pyautogui 的安全失败保护（移动到角落不会抛异常）
pyautogui.FAILSAFE = False


class MouseController:
    """鼠标控制器"""

    def __init__(self, duration: float = 0.0):
        """
        初始化鼠标控制器

        Args:
            duration: 默认移动持续时间（秒），0=瞬间移动
        """
        self.default_duration = duration
        self._pressed_buttons = set()

    @property
    def position(self) -> Tuple[int, int]:
        """获取当前鼠标坐标"""
        x, y = pyautogui.position()
        return (x, y)

    @property
    def screen_size(self) -> Tuple[int, int]:
        """获取屏幕分辨率"""
        return pyautogui.size()

    def move(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """
        绝对移动鼠标到指定坐标

        Args:
            x: 目标X坐标
            y: 目标Y坐标
            duration: 移动持续时间（秒）
        """
        dur = duration if duration is not None else self.default_duration
        pyautogui.moveTo(x, y, duration=dur)

    def move_relative(self, dx: int, dy: int, duration: Optional[float] = None) -> None:
        """
        相对当前位置移动鼠标

        Args:
            dx: X方向偏移量
            dy: Y方向偏移量
            duration: 移动持续时间（秒）
        """
        dur = duration if duration is not None else self.default_duration
        pyautogui.moveRel(dx, dy, duration=dur)

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        clicks: int = 1,
        interval: float = 0.0,
    ) -> None:
        """
        鼠标点击

        Args:
            x: 点击X坐标（None则当前位置）
            y: 点击Y坐标（None则当前位置）
            button: 按键 'left'/'right'/'middle'
            clicks: 点击次数
            interval: 多次点击间隔（秒）
        """
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
        else:
            pyautogui.click(clicks=clicks, interval=interval, button=button)

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """双击左键"""
        self.click(x, y, button="left", clicks=2, interval=0.1)

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """右键单击"""
        self.click(x, y, button="right")

    def middle_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """中键单击"""
        self.click(x, y, button="middle")

    def press(self, button: str = "left") -> None:
        """按下鼠标按键（不释放）"""
        pyautogui.mouseDown(button=button)
        self._pressed_buttons.add(button)

    def release(self, button: str = "left") -> None:
        """释放鼠标按键"""
        pyautogui.mouseUp(button=button)
        self._pressed_buttons.discard(button)

    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5,
        button: str = "left",
    ) -> None:
        """
        拖拽操作：从起点按下拖到终点释放

        Args:
            start_x: 起点X
            start_y: 起点Y
            end_x: 终点X
            end_y: 终点Y
            duration: 拖拽持续时间
            button: 拖拽按键
        """
        self.move(start_x, start_y)
        time.sleep(0.1)
        pyautogui.dragTo(end_x, end_y, duration=duration, button=button)

    def drag_relative(
        self,
        dx: int,
        dy: int,
        duration: float = 0.5,
        button: str = "left",
    ) -> None:
        """相对当前位置拖拽"""
        pyautogui.dragRel(dx, dy, duration=duration, button=button)

    def scroll(self, amount: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """
        鼠标滚轮滚动

        Args:
            amount: 滚动量（正数向上，负数向下）
            x: 滚动位置X
            y: 滚动位置Y
        """
        if x is not None and y is not None:
            pyautogui.scroll(amount, x=x, y=y)
        else:
            pyautogui.scroll(amount)

    def scroll_up(self, amount: int = 3) -> None:
        """向上滚动"""
        self.scroll(amount)

    def scroll_down(self, amount: int = 3) -> None:
        """向下滚动"""
        self.scroll(-amount)

    def scroll_left(self, amount: int = 3) -> None:
        """横向向左滚动（部分平台支持）"""
        pyautogui.hscroll(-amount)

    def scroll_right(self, amount: int = 3) -> None:
        """横向向右滚动"""
        pyautogui.hscroll(amount)

    def hold_and_move(
        self,
        x: int,
        y: int,
        button: str = "left",
        duration: float = 0.0,
    ) -> None:
        """按住按键移动到指定位置（不释放）"""
        self.press(button)
        self.move(x, y, duration=duration)

    def release_all(self) -> None:
        """释放所有按下的鼠标按键"""
        for btn in list(self._pressed_buttons):
            self.release(btn)

    def wait(self, seconds: float) -> None:
        """等待指定秒数"""
        time.sleep(seconds)
