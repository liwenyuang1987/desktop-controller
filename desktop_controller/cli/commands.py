#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行接口
支持鼠标、键盘、屏幕、窗口、进程、宏等所有功能的命令行调用
"""

import sys
import os
import json
import argparse

# 将项目根目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.mouse import MouseController
from ..core.keyboard import KeyboardController
from ..core.screen import ScreenController
from ..core.window import WindowController
from ..core.process import ProcessController
from ..core.file_manager import FileManager
from ..macro.recorder import MacroRecorder
from ..macro.player import MacroPlayer
from ..macro.scheduler import TaskScheduler


def cmd_mouse(args):
    """鼠标控制命令"""
    mouse = MouseController()

    if args.action == "move":
        mouse.move(args.x, args.y, getattr(args, 'duration', 0.0))
        print(f"鼠标移动到 ({args.x}, {args.y})")

    elif args.action == "move_rel":
        mouse.move_relative(args.dx, args.dy)
        print(f"鼠标相对移动 ({args.dx}, {args.dy})")

    elif args.action == "click":
        button = getattr(args, 'button', 'left')
        clicks = getattr(args, 'clicks', 1)
        x = getattr(args, 'x', None)
        y = getattr(args, 'y', None)
        mouse.click(x, y, button=button, clicks=clicks)
        print(f"鼠标{button}键点击 {clicks}次")

    elif args.action == "double":
        mouse.double_click()
        print("鼠标双击")

    elif args.action == "right":
        mouse.right_click()
        print("鼠标右键点击")

    elif args.action == "drag":
        mouse.drag(args.sx, args.sy, args.ex, args.ey)
        print(f"拖拽从 ({args.sx},{args.sy}) 到 ({args.ex},{args.ey})")

    elif args.action == "scroll":
        mouse.scroll(args.amount)
        print(f"滚轮滚动 {args.amount}")

    elif args.action == "position":
        x, y = mouse.position
        print(f"当前鼠标位置: ({x}, {y})")

    elif args.action == "size":
        w, h = mouse.screen_size
        print(f"屏幕分辨率: {w} x {h}")


def cmd_keyboard(args):
    """键盘控制命令"""
    keyboard = KeyboardController()

    if args.action == "type":
        use_clipboard = getattr(args, 'clipboard', False)
        keyboard.type_text(args.text, use_clipboard=use_clipboard)
        print(f"输入文本: {args.text[:50]}")

    elif args.action == "press":
        keyboard.press(args.key, presses=getattr(args, 'count', 1))
        print(f"按键: {args.key}")

    elif args.action == "hotkey":
        keys = args.keys.split()
        keyboard.hotkey(*keys)
        print(f"组合键: {'+'.join(keys)}")

    elif args.action == "copy":
        keyboard.copy()
        print("复制 Ctrl+C")

    elif args.action == "paste":
        keyboard.paste()
        print("粘贴 Ctrl+V")

    elif args.action == "select_all":
        keyboard.select_all()
        print("全选 Ctrl+A")

    elif args.action == "undo":
        keyboard.undo()
        print("撤销 Ctrl+Z")

    elif args.action == "save":
        keyboard.save()
        print("保存 Ctrl+S")


def cmd_screen(args):
    """屏幕操作命令"""
    screen = ScreenController()

    if args.action == "capture":
        output = getattr(args, 'output', 'screenshot.png')
        region = None
        if hasattr(args, 'region') and args.region:
            region = tuple(args.region)
        screen.capture(output, region=region)
        print(f"截图已保存: {output}")

    elif args.action == "color":
        r, g, b = screen.get_pixel_color(args.x, args.y)
        print(f"像素颜色 ({args.x},{args.y}): RGB({r},{g},{b})")

    elif args.action == "find":
        pos = screen.find_image(
            args.template,
            confidence=getattr(args, 'confidence', 0.8)
        )
        if pos:
            print(f"找到图像位置: ({pos[0]}, {pos[1]})")
        else:
            print("未找到匹配图像")

    elif args.action == "click_image":
        success = screen.click_image(
            args.template,
            confidence=getattr(args, 'confidence', 0.8),
            timeout=getattr(args, 'timeout', 5.0)
        )
        print("点击图像成功" if success else "未找到图像")

    elif args.action == "size":
        w, h = screen.size
        print(f"屏幕分辨率: {w} x {h}")


def cmd_window(args):
    """窗口管理命令"""
    win = WindowController()

    if args.action == "list":
        windows = win.list_windows()
        print(f"共 {len(windows)} 个窗口:")
        for i, w in enumerate(windows[:30]):
            print(f"  [{i}] hwnd={w.hwnd} title='{w.title[:40]}' pos=({w.x},{w.y}) size={w.width}x{w.height}")
        if len(windows) > 30:
            print(f"  ... 还有 {len(windows)-30} 个窗口")

    elif args.action == "find":
        w = win.find_window(args.title)
        if w:
            print(f"找到窗口: hwnd={w.hwnd} title='{w.title}' pos=({w.x},{w.y}) size={w.width}x{w.height}")
        else:
            print("未找到匹配窗口")

    elif args.action == "activate":
        if args.hwnd:
            win.activate(args.hwnd)
        elif args.title:
            win.activate_by_title(args.title)
        print("窗口已激活")

    elif args.action == "close":
        win.close(args.hwnd)
        print("窗口已关闭")

    elif args.action == "minimize":
        win.minimize(args.hwnd)
        print("窗口已最小化")

    elif args.action == "maximize":
        win.maximize(args.hwnd)
        print("窗口已最大化")

    elif args.action == "move":
        win.move(args.hwnd, args.x, args.y)
        print(f"窗口移动到 ({args.x},{args.y})")

    elif args.action == "resize":
        win.resize(args.hwnd, args.width, args.height)
        print(f"窗口调整为 {args.width}x{args.height}")

    elif args.action == "active":
        w = win.get_active_window()
        if w:
            print(f"当前活动窗口: hwnd={w.hwnd} title='{w.title}'")


def cmd_process(args):
    """进程管理命令"""
    proc = ProcessController()

    if args.action == "list":
        processes = proc.list_processes()
        sort_by = getattr(args, 'sort', 'cpu')
        if sort_by == "cpu":
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda p: p.memory_mb, reverse=True)

        print(f"{'PID':>8} {'CPU%':>7} {'MEM(MB)':>9} {'名称'}")
        print("-" * 50)
        for p in processes[:getattr(args, 'limit', 20)]:
            print(f"{p.pid:>8} {p.cpu_percent:>7.1f} {p.memory_mb:>9.1f} {p.name}")

    elif args.action == "find":
        procs = proc.find_by_name(args.name)
        print(f"找到 {len(procs)} 个匹配进程:")
        for p in procs:
            print(f"  PID={p.pid} CPU={p.cpu_percent:.1f}% MEM={p.memory_mb:.1f}MB")

    elif args.action == "start":
        proc.start_process(args.command)
        print(f"启动进程: {args.command}")

    elif args.action == "kill":
        if args.pid:
            proc.kill(args.pid)
            print(f"终止进程 PID={args.pid}")
        elif args.name:
            count = proc.kill_by_name(args.name)
            print(f"终止 {count} 个进程")

    elif args.action == "terminate":
        proc.terminate(args.pid)
        print(f"终止进程 PID={args.pid}")

    elif args.action == "info":
        info = proc.get_system_info()
        print(json.dumps(info, indent=2, ensure_ascii=False))

    elif args.action == "top":
        n = getattr(args, 'number', 10)
        proc.print_top_processes(n, by=getattr(args, 'by', 'cpu'))


def cmd_macro(args):
    """宏录制回放命令"""
    if args.action == "record":
        recorder = MacroRecorder()
        output = getattr(args, 'output', 'macro.json')
        print("开始录制... 按 F9 停止")
        recorder.start()
        try:
            while recorder.is_recording:
                import time
                time.sleep(0.1)
        except KeyboardInterrupt:
            recorder.stop()
        recorder.save(output)
        print(f"宏已保存: {output} ({recorder.event_count} 个事件)")

    elif args.action == "play":
        player = MacroPlayer(
            speed=getattr(args, 'speed', 1.0),
            repeat=getattr(args, 'repeat', 1)
        )
        success = player.play_file(args.file)
        print("回放完成" if success else "回放失败")

    elif args.action == "info":
        recorder = MacroRecorder()
        events = recorder.load(args.file)
        summary = recorder.get_summary()
        print(f"宏文件: {args.file}")
        print(f"事件总数: {summary['total_events']}")
        print(f"鼠标移动: {summary['mouse_moves']}")
        print(f"鼠标点击: {summary['mouse_clicks']}")
        print(f"滚轮滚动: {summary['mouse_scrolls']}")
        print(f"按键按下: {summary['key_presses']}")
        print(f"按键释放: {summary['key_releases']}")
        print(f"时长: {summary['duration']:.2f}s")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        prog="desktop-controller",
        description="桌面自动化控制工具 - 鼠标/键盘/屏幕/窗口/进程/宏录制回放"
    )
    subparsers = parser.add_subparsers(dest="module", help="功能模块")

    # 鼠标命令
    mouse_parser = subparsers.add_parser("mouse", help="鼠标控制")
    mouse_sub = mouse_parser.add_subparsers(dest="action", required=True)

    p = mouse_sub.add_parser("move", help="移动鼠标")
    p.add_argument("x", type=int)
    p.add_argument("y", type=int)
    p.add_argument("--duration", type=float, default=0.0)

    p = mouse_sub.add_parser("move_rel", help="相对移动")
    p.add_argument("dx", type=int)
    p.add_argument("dy", type=int)

    p = mouse_sub.add_parser("click", help="点击")
    p.add_argument("--button", choices=["left", "right", "middle"], default="left")
    p.add_argument("--clicks", type=int, default=1)
    p.add_argument("--x", type=int, default=None)
    p.add_argument("--y", type=int, default=None)

    mouse_sub.add_parser("double", help="双击")
    mouse_sub.add_parser("right", help="右键")

    p = mouse_sub.add_parser("drag", help="拖拽")
    p.add_argument("sx", type=int, help="起点X")
    p.add_argument("sy", type=int, help="起点Y")
    p.add_argument("ex", type=int, help="终点X")
    p.add_argument("ey", type=int, help="终点Y")

    p = mouse_sub.add_parser("scroll", help="滚动")
    p.add_argument("amount", type=int, help="滚动量(正上负下)")

    mouse_sub.add_parser("position", help="当前位置")
    mouse_sub.add_parser("size", help="屏幕分辨率")

    # 键盘命令
    kb_parser = subparsers.add_parser("keyboard", help="键盘控制")
    kb_sub = kb_parser.add_subparsers(dest="action", required=True)

    p = kb_sub.add_parser("type", help="输入文本")
    p.add_argument("text", help="要输入的文本")
    p.add_argument("--clipboard", action="store_true", help="使用剪贴板(中文推荐)")

    p = kb_sub.add_parser("press", help="按键")
    p.add_argument("key", help="按键名称")
    p.add_argument("--count", type=int, default=1)

    p = kb_sub.add_parser("hotkey", help="组合键")
    p.add_argument("keys", help="空格分隔的按键，如 'ctrl c'")

    kb_sub.add_parser("copy", help="复制")
    kb_sub.add_parser("paste", help="粘贴")
    kb_sub.add_parser("select_all", help="全选")
    kb_sub.add_parser("undo", help="撤销")
    kb_sub.add_parser("save", help="保存")

    # 屏幕命令
    scr_parser = subparsers.add_parser("screen", help="屏幕操作")
    scr_sub = scr_parser.add_subparsers(dest="action", required=True)

    p = scr_sub.add_parser("capture", help="截图")
    p.add_argument("--output", default="screenshot.png")
    p.add_argument("--region", nargs=4, type=int, metavar=("X", "Y", "W", "H"))

    p = scr_sub.add_parser("color", help="像素颜色")
    p.add_argument("x", type=int)
    p.add_argument("y", type=int)

    p = scr_sub.add_parser("find", help="查找图像")
    p.add_argument("template", help="模板图像路径")
    p.add_argument("--confidence", type=float, default=0.8)

    p = scr_sub.add_parser("click_image", help="找到图像并点击")
    p.add_argument("template")
    p.add_argument("--confidence", type=float, default=0.8)
    p.add_argument("--timeout", type=float, default=5.0)

    scr_sub.add_parser("size", help="屏幕分辨率")

    # 窗口命令
    win_parser = subparsers.add_parser("window", help="窗口管理")
    win_sub = win_parser.add_subparsers(dest="action", required=True)

    win_sub.add_parser("list", help="列出窗口")

    p = win_sub.add_parser("find", help="查找窗口")
    p.add_argument("title", help="标题关键词")

    p = win_sub.add_parser("activate", help="激活窗口")
    p.add_argument("--hwnd", type=int)
    p.add_argument("--title")

    p = win_sub.add_parser("close", help="关闭窗口")
    p.add_argument("hwnd", type=int)

    p = win_sub.add_parser("minimize", help="最小化")
    p.add_argument("hwnd", type=int)

    p = win_sub.add_parser("maximize", help="最大化")
    p.add_argument("hwnd", type=int)

    p = win_sub.add_parser("move", help="移动窗口")
    p.add_argument("hwnd", type=int)
    p.add_argument("x", type=int)
    p.add_argument("y", type=int)

    p = win_sub.add_parser("resize", help="调整大小")
    p.add_argument("hwnd", type=int)
    p.add_argument("width", type=int)
    p.add_argument("height", type=int)

    win_sub.add_parser("active", help="当前活动窗口")

    # 进程命令
    proc_parser = subparsers.add_parser("process", help="进程管理")
    proc_sub = proc_parser.add_subparsers(dest="action", required=True)

    p = proc_sub.add_parser("list", help="列出进程")
    p.add_argument("--sort", choices=["cpu", "memory", "pid", "name"], default="cpu")
    p.add_argument("--limit", type=int, default=20)

    p = proc_sub.add_parser("find", help="查找进程")
    p.add_argument("name")

    p = proc_sub.add_parser("start", help="启动进程")
    p.add_argument("command")

    p = proc_sub.add_parser("kill", help="强制终止")
    p.add_argument("--pid", type=int)
    p.add_argument("--name")

    p = proc_sub.add_parser("terminate", help="终止进程")
    p.add_argument("pid", type=int)

    proc_sub.add_parser("info", help="系统信息")

    p = proc_sub.add_parser("top", help="Top进程")
    p.add_argument("--number", type=int, default=10)
    p.add_argument("--by", choices=["cpu", "memory"], default="cpu")

    # 宏命令
    macro_parser = subparsers.add_parser("macro", help="宏录制回放")
    macro_sub = macro_parser.add_subparsers(dest="action", required=True)

    p = macro_sub.add_parser("record", help="录制宏")
    p.add_argument("--output", default="macro.json")

    p = macro_sub.add_parser("play", help="回放宏")
    p.add_argument("file")
    p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--repeat", type=int, default=1)

    p = macro_sub.add_parser("info", help="宏信息")
    p.add_argument("file")

    args = parser.parse_args()

    if not args.module:
        parser.print_help()
        return

    # 分发命令
    handlers = {
        "mouse": cmd_mouse,
        "keyboard": cmd_keyboard,
        "screen": cmd_screen,
        "window": cmd_window,
        "process": cmd_process,
        "macro": cmd_macro,
    }

    handler = handlers.get(args.module)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
