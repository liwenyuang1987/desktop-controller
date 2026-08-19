#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Desktop Controller - 桌面自动化控制工具
主入口文件
"""

import sys
import os

# 将项目根目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_gui():
    """启动 GUI 界面"""
    try:
        from PyQt5.QtWidgets import QApplication
        from desktop_controller.gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("Desktop Controller")
        app.setApplicationVersion("1.0.0")

        window = MainWindow()
        window.show()

        sys.exit(app.exec_())
    except ImportError as e:
        print(f"错误: 无法导入GUI依赖 - {e}")
        print("请运行: pip install PyQt5")
        sys.exit(1)


def run_cli():
    """启动 CLI 命令行"""
    from desktop_controller.cli.commands import main
    main()


def main():
    """主入口"""
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # CLI 模式: python main.py --cli <command>
        sys.argv.pop(1)
        run_cli()
    else:
        # 默认启动 GUI
        run_gui()


if __name__ == "__main__":
    main()
