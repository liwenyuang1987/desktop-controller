# Desktop Controller - 桌面自动化控制工具

功能完整的桌面自动化控制套件，支持鼠标、键盘、屏幕、窗口、进程管理及宏录制回放，提供 GUI 界面和命令行接口。

## 功能特性

### 核心控制
- **鼠标控制**：移动、点击（左/右/中）、双击、拖拽、滚动、相对移动
- **键盘控制**：单键、组合键（Ctrl+C等）、文本输入、热键监听
- **屏幕操作**：全屏截图、区域截图、像素颜色获取、图像匹配定位
- **窗口管理**：列出窗口、激活/最小化/最大化/关闭、移动调整大小、窗口标题查找
- **进程管理**：列出进程、按名/PID查找、启动/终止进程、CPU/内存监控
- **文件操作**：浏览目录、复制/移动/删除、文件信息查询

### 高级功能
- **宏录制回放**：录制鼠标键盘操作序列，保存为JSON，一键回放
- **定时任务**：指定时间或间隔自动执行脚本/宏
- **图像识别**：基于模板匹配在屏幕上定位图标/按钮
- **脚本引擎**：Python脚本批量执行自动化任务

### 交互方式
- **GUI界面**：PyQt5 图形界面，可视化操作所有功能
- **CLI命令行**：命令行直接调用所有控制功能
- **Python API**：作为库导入，在自己的脚本中使用

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/liwenyuang1987/desktop-controller.git
cd desktop-controller

# 安装依赖
pip install -r requirements.txt

# 安装为包（可选）
pip install -e .
```

### 启动 GUI

```bash
python main.py
# 或
python -m desktop_controller
```

### CLI 使用

```bash
# 鼠标移动到 (500, 300) 并左键点击
python -m desktop_controller.cli mouse move 500 300
python -m desktop_controller.cli mouse click left

# 输入文本
python -m desktop_controller.cli keyboard type "Hello World"

# 截图
python -m desktop_controller.cli screen capture --output screenshot.png

# 列出窗口
python -m desktop_controller.cli window list

# 录制宏
python -m desktop_controller.cli macro record --output my_macro.json

# 回放宏
python -m desktop_controller.cli macro play my_macro.json
```

### Python API 使用

```python
from desktop_controller.core.mouse import MouseController
from desktop_controller.core.keyboard import KeyboardController
from desktop_controller.core.screen import ScreenController

mouse = MouseController()
keyboard = KeyboardController()
screen = ScreenController()

# 移动鼠标并点击
mouse.move(500, 300)
mouse.click('left')

# 输入文本
keyboard.type_text('Hello World')

# 截图并保存
screen.capture('screenshot.png')

# 查找图像位置
position = screen.find_image('button.png', confidence=0.8)
if position:
    mouse.click(position[0], position[1])
```

## 项目结构

```
desktop_controller/
├── core/                    # 核心控制模块
│   ├── mouse.py            # 鼠标控制
│   ├── keyboard.py         # 键盘控制
│   ├── screen.py           # 屏幕操作
│   ├── window.py           # 窗口管理
│   ├── process.py          # 进程管理
│   └── file_manager.py     # 文件操作
├── gui/                     # PyQt5 图形界面
│   ├── main_window.py      # 主窗口
│   ├── mouse_panel.py      # 鼠标控制面板
│   ├── keyboard_panel.py   # 键盘控制面板
│   ├── screen_panel.py     # 屏幕控制面板
│   ├── window_panel.py     # 窗口管理面板
│   ├── process_panel.py    # 进程管理面板
│   ├── macro_panel.py      # 宏录制面板
│   └── settings_dialog.py  # 设置对话框
├── macro/                   # 宏录制回放
│   ├── recorder.py         # 录制器
│   ├── player.py           # 回放器
│   └── scheduler.py        # 定时调度
├── cli/                     # 命令行接口
│   └── commands.py         # CLI命令定义
└── utils/                   # 工具类
    ├── config.py           # 配置管理
    └── logger.py           # 日志
```

## 系统要求

- Python 3.8+
- Windows 10/11（主要支持平台）
- macOS / Linux（部分功能受限）

## 依赖

- PyQt5 >= 5.15.0
- pyautogui >= 0.9.54
- pillow >= 9.0.0
- psutil >= 5.9.0
- pywin32 >= 305 (Windows)
- opencv-python >= 4.5.0
- numpy >= 1.21.0
- pynput >= 1.7.6

## 许可证

MIT License
