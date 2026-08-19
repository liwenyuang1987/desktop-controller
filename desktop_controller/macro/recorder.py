# -*- coding: utf-8 -*-
"""
宏录制器
录制鼠标和键盘操作，保存为JSON格式
"""

import json
import time
import threading
from typing import List, Dict, Any, Optional
from pynput import mouse, keyboard


class MacroRecorder:
    """宏录制器"""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self._start_time: float = 0
        self._is_recording: bool = False
        self._mouse_listener = None
        self._keyboard_listener = None
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    @property
    def event_count(self) -> int:
        return len(self.events)

    def start(self) -> None:
        """开始录制"""
        if self._is_recording:
            return

        self.events = []
        self._start_time = time.time()
        self._is_recording = True

        # 鼠标监听
        self._mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll,
        )
        self._mouse_listener.start()

        # 键盘监听
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._keyboard_listener.start()

    def stop(self) -> List[Dict[str, Any]]:
        """停止录制，返回事件列表"""
        if not self._is_recording:
            return self.events

        self._is_recording = False

        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

        return self.events

    def save(self, filepath: str) -> bool:
        """
        保存录制的宏到JSON文件

        Args:
            filepath: 保存路径
        """
        try:
            data = {
                "version": "1.0",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": round(time.time() - self._start_time, 2) if self._start_time else 0,
                "event_count": len(self.events),
                "events": self.events,
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存宏失败: {e}")
            return False

    def load(self, filepath: str) -> List[Dict[str, Any]]:
        """从JSON文件加载宏"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.events = data.get("events", [])
            return self.events
        except Exception as e:
            print(f"加载宏失败: {e}")
            return []

    def _timestamp(self) -> float:
        """获取相对时间戳"""
        return round(time.time() - self._start_time, 4)

    def _add_event(self, event_type: str, **kwargs) -> None:
        """添加事件"""
        with self._lock:
            event = {"type": event_type, "time": self._timestamp()}
            event.update(kwargs)
            self.events.append(event)

    def _on_mouse_move(self, x, y):
        # 鼠标移动事件较多，做节流（每50ms记录一次）
        if self.events:
            last = self.events[-1]
            if last["type"] == "mouse_move" and self._timestamp() - last["time"] < 0.05:
                return
        self._add_event("mouse_move", x=int(x), y=int(y))

    def _on_mouse_click(self, x, y, button, pressed):
        btn = "left" if button == mouse.Button.left else \
              "right" if button == mouse.Button.right else "middle"
        self._add_event(
            "mouse_click",
            x=int(x), y=int(y),
            button=btn,
            pressed=pressed,
        )

    def _on_mouse_scroll(self, x, y, dx, dy):
        self._add_event("mouse_scroll", x=int(x), y=int(y), dx=int(dx), dy=int(dy))

    def _on_key_press(self, key):
        key_str = self._key_to_string(key)
        # F9 作为停止录制的热键
        if key_str == "f9":
            self.stop()
            return False
        self._add_event("key_press", key=key_str)

    def _on_key_release(self, key):
        key_str = self._key_to_string(key)
        self._add_event("key_release", key=key_str)

    @staticmethod
    def _key_to_string(key) -> str:
        """将pynput按键转为字符串"""
        try:
            # 普通字符键
            return key.char.lower() if key.char else str(key)
        except AttributeError:
            # 特殊键
            key_name = str(key).replace("Key.", "").lower()
            return key_name

    def get_summary(self) -> Dict[str, Any]:
        """获取录制摘要"""
        summary = {
            "total_events": len(self.events),
            "mouse_moves": 0,
            "mouse_clicks": 0,
            "mouse_scrolls": 0,
            "key_presses": 0,
            "key_releases": 0,
        }
        for event in self.events:
            t = event["type"]
            if t == "mouse_move":
                summary["mouse_moves"] += 1
            elif t == "mouse_click":
                summary["mouse_clicks"] += 1
            elif t == "mouse_scroll":
                summary["mouse_scrolls"] += 1
            elif t == "key_press":
                summary["key_presses"] += 1
            elif t == "key_release":
                summary["key_releases"] += 1

        if self.events:
            summary["duration"] = self.events[-1]["time"]
        else:
            summary["duration"] = 0

        return summary
