from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="desktop-controller",
    version="1.0.0",
    author="Desktop Controller Team",
    description="功能完整的桌面自动化控制工具 - 鼠标/键盘/屏幕/窗口/进程/宏录制回放",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liwenyuang1987/desktop-controller",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
        "pyautogui>=0.9.54",
        "pillow>=9.0.0",
        "psutil>=5.9.0",
        "opencv-python>=4.5.0",
        "numpy>=1.21.0",
        "pynput>=1.7.6",
        "pyperclip>=1.8.2",
    ],
    extras_require={
        "windows": ["pywin32>=305"],
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "desktop-controller=desktop_controller.cli.commands:main",
        ],
    },
    include_package_data=True,
)
