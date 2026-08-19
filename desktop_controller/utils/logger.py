# -*- coding: utf-8 -*-
"""
日志模块
提供统一的日志记录功能，支持控制台和文件输出
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


# 全局日志实例缓存
_loggers = {}


class Logger:
    """日志封装类"""

    def __init__(self, name: str = "desktop_controller", log_file: Optional[str] = None,
                 level: str = "INFO", max_size_mb: int = 10, backup_count: int = 3):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.logger.handlers.clear()

        # 控制台输出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_fmt = logging.Formatter(
            "[%(asctime)s] %(levelname)-7s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler.setFormatter(console_fmt)
        self.logger.addHandler(console_handler)

        # 文件输出
        if log_file:
            try:
                os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=max_size_mb * 1024 * 1024,
                    backupCount=backup_count,
                    encoding="utf-8",
                )
                file_handler.setLevel(logging.DEBUG)
                file_fmt = logging.Formatter(
                    "[%(asctime)s] %(levelname)-7s %(name)s (%(filename)s:%(lineno)d): %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                file_handler.setFormatter(file_fmt)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"无法创建日志文件: {e}")

        self.logger.propagate = False

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)


def get_logger(name: str = "desktop_controller", log_file: Optional[str] = None,
               level: str = "INFO") -> Logger:
    """
    获取日志实例（单例模式）

    Args:
        name: 日志名称
        log_file: 日志文件路径
        level: 日志级别

    Returns:
        Logger实例
    """
    if name not in _loggers:
        _loggers[name] = Logger(name, log_file, level)
    return _loggers[name]
