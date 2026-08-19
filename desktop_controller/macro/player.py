# -*- coding: utf-8 -*-
"""
宏回放器
读取录制的宏事件并执行
"""

import json
import time
import pyautogui
from typing import List, Dict, Any, Optional, Callable


class MacroPlayer:
    """宏回放器"""

    def __init__(self, speed: float = 1.0, repeat: int = 1):
        """
        初始化回放器

        Args:
            speed: 回放速度倍率（1.0=原速，2.0=两倍速，0.5=半速）
            repeat: 重复次数
        """
        self.speed = speed
        self.repeat = repeat
        self._is_playing = False
        self._stop_requested = False
        self.on_progress: Optional[Callable[[int, int], None]] = None

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    def load(self, filepath: str) -> List[Dict[str, Any]]:
        """从JSON文件加载宏"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("events", [])

    def play(
        self,
        events: List[Dict[str, Any]],
        speed: Optional[float] = None,
        repeat: Optional[int] = None,
    ) -> bool:
        """
        回放宏事件

        Args:
            events: 事件列表
            speed: 速度倍率（覆盖默认）
            repeat: 重复次数（覆盖默认）

        Returns:
            是否成功完成
        """
        if not events:
            return False

        spd = speed if speed is not None else self.speed
        reps = repeat if repeat is not None else self.repeat

        self._is_playing = True
        self._stop_requested = False

        try:
            for r in range(reps):
                if self._stop_requested:
                    break
                self._play_once(events, spd, r, reps)
            return True
        except Exception as e:
            print(f"回放出错: {e}")
            return False
        finally:
            self._is_playing = False

    def play_file(
        self,
        filepath: str,
        speed: Optional[float] = None,
        repeat: Optional[int] = None,
    ) -> bool:
        """从文件加载并回放"""
        events = self.load(filepath)
        return self.play(events, speed, repeat)

    def stop(self) -> None:
        """请求停止回放"""
        self._stop_requested = True

    def _play_once(
        self, events: List[Dict[str, Any]], speed: float,
        current_rep: int, total_reps: int,
    ) -> None:
        """回放一次"""
        last_time = 0.0
        total = len(events)

        for i, event in enumerate(events):
            if self._stop_requested:
                break

            # 进度回调
            if self.on_progress:
                overall = current_rep * total + i
                self.on_progress(overall, total_reps * total)

            # 等待时间间隔
            event_time = event.get("time", 0)
            delay = (event_time - last_time) / speed
            if delay > 0:
                time.sleep(min(delay, 5.0))  # 最大等待5秒
            last_time = event_time

            # 执行事件
            self._execute_event(event)

    def _execute_event(self, event: Dict[str, Any]) -> None:
        """执行单个事件"""
        event_type = event.get("type")

        if event_type == "mouse_move":
            pyautogui.moveTo(event["x"], event["y"], duration=0)

        elif event_type == "mouse_click":
            x, y = event["x"], event["y"]
            button = event.get("button", "left")
            pressed = event.get("pressed", True)
            if pressed:
                pyautogui.mouseDown(x=x, y=y, button=button)
            else:
                pyautogui.mouseUp(x=x, y=y, button=button)

        elif event_type == "mouse_scroll":
            dy = event.get("dy", 0)
            pyautogui.scroll(dy)

        elif event_type == "key_press":
            key = self._normalize_key(event.get("key", ""))
            pyautogui.keyDown(key)

        elif event_type == "key_release":
            key = self._normalize_key(event.get("key", ""))
            pyautogui.keyUp(key)

    @staticmethod
    def _normalize_key(key: str) -> str:
        """标准化按键名称以匹配pyautogui"""
        key_map = {
            "ctrl_l": "ctrl",
            "ctrl_r": "ctrl",
            "alt_l": "alt",
            "alt_r": "alt",
            "shift_l": "shift",
            "shift_r": "shift",
            "cmd": "win",
            "cmd_l": "win",
            "cmd_r": "win",
            "enter": "enter",
            "return": "enter",
            "esc": "esc",
            "space": "space",
            "tab": "tab",
            "backspace": "backspace",
            "delete": "delete",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right",
            "home": "home",
            "end": "end",
            "pageup": "pageup",
            "pagedown": "pagedown",
            "caps_lock": "capslock",
            "num_lock": "numlock",
        }
        return key_map.get(key.lower(), key.lower())

    def validate_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证宏事件列表

        Returns:
            验证结果字典
        """
        result = {
            "valid": True,
            "total": len(events),
            "errors": [],
            "warnings": [],
            "event_types": {},
        }

        for i, event in enumerate(events):
            event_type = event.get("type")
            result["event_types"][event_type] = result["event_types"].get(event_type, 0) + 1

            if event_type not in ("mouse_move", "mouse_click", "mouse_scroll",
                                   "key_press", "key_release"):
                result["warnings"].append(f"事件{i}: 未知类型 '{event_type}'")

            if "time" not in event:
                result["warnings"].append(f"事件{i}: 缺少时间戳")

        return result
