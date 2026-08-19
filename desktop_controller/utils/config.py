# -*- coding: utf-8 -*-
"""
配置管理模块
支持JSON配置文件的读写、默认值、热更新
"""

import json
import os
import threading
from typing import Any, Dict, Optional


class ConfigManager:
    """配置管理器"""

    DEFAULT_CONFIG = {
        "mouse": {
            "default_duration": 0.0,
            "click_interval": 0.0,
        },
        "keyboard": {
            "default_interval": 0.0,
            "use_clipboard_for_non_ascii": True,
        },
        "screen": {
            "default_confidence": 0.8,
            "screenshot_format": "png",
        },
        "macro": {
            "default_speed": 1.0,
            "default_repeat": 1,
            "stop_hotkey": "f9",
        },
        "scheduler": {
            "check_interval": 0.5,
        },
        "ui": {
            "theme": "default",
            "window_width": 900,
            "window_height": 650,
            "always_on_top": False,
        },
        "logging": {
            "level": "INFO",
            "file": "desktop_controller.log",
            "max_size_mb": 10,
            "backup_count": 3,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，None则使用默认路径
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.expanduser("~"), ".desktop_controller", "config.json"
            )
        self.config_path = config_path
        self._lock = threading.Lock()
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        with self._lock:
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        self._config = json.load(f)
                except Exception:
                    self._config = {}
            else:
                self._config = {}
            # 合并默认值
            self._config = self._deep_merge(self.DEFAULT_CONFIG, self._config)
        return self._config

    def save(self) -> bool:
        """保存配置到文件"""
        with self._lock:
            try:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(self._config, f, ensure_ascii=False, indent=2)
                return True
            except Exception:
                return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点分隔路径

        示例:
            config.get("mouse.default_duration")
            config.get("ui.theme", "dark")
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值，支持点分隔路径
        """
        with self._lock:
            keys = key.split(".")
            config = self._config
            for k in keys[:-1]:
                if k not in config or not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """获取全部配置"""
        return self._config.copy()

    def reset(self) -> None:
        """重置为默认配置"""
        with self._lock:
            self._config = json.loads(json.dumps(self.DEFAULT_CONFIG))

    def reset_key(self, key: str) -> None:
        """重置单个配置项为默认值"""
        default_val = self.get_from_default(key)
        if default_val is not None:
            self.set(key, default_val)

    def get_from_default(self, key: str) -> Any:
        """从默认配置中获取值"""
        keys = key.split(".")
        value = self.DEFAULT_CONFIG
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value

    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
