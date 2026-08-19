# -*- coding: utf-8 -*-
"""
屏幕操作模块
提供截图、像素颜色、图像匹配等功能
"""

import os
import time
import pyautogui
from PIL import Image
from typing import Tuple, Optional, List
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


class ScreenController:
    """屏幕控制器"""

    def __init__(self):
        self._screen_width, self._screen_height = pyautogui.size()

    @property
    def size(self) -> Tuple[int, int]:
        """屏幕分辨率"""
        return (self._screen_width, self._screen_height)

    @property
    def width(self) -> int:
        return self._screen_width

    @property
    def height(self) -> int:
        return self._screen_height

    def capture(
        self,
        filepath: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Image.Image:
        """
        截屏

        Args:
            filepath: 保存路径（None则不保存）
            region: 截图区域 (left, top, width, height)，None为全屏

        Returns:
            PIL Image 对象
        """
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()

        if filepath:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
            screenshot.save(filepath)

        return screenshot

    def capture_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        filepath: Optional[str] = None,
    ) -> Image.Image:
        """
        截取指定区域

        Args:
            x: 区域左上角X
            y: 区域左上角Y
            width: 区域宽度
            height: 区域高度
            filepath: 保存路径
        """
        return self.capture(filepath, region=(x, y, width, height))

    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """
        获取指定坐标的像素颜色

        Args:
            x: X坐标
            y: Y坐标

        Returns:
            (R, G, B) 颜色元组
        """
        pixel = pyautogui.pixel(x, y)
        return (pixel[0], pixel[1], pixel[2])

    def pixel_matches(
        self,
        x: int,
        y: int,
        expected_color: Tuple[int, int, int],
        tolerance: int = 0,
    ) -> bool:
        """
        检查指定坐标像素是否匹配预期颜色

        Args:
            x: X坐标
            y: Y坐标
            expected_color: 预期 (R,G,B)
            tolerance: 颜色容差
        """
        return pyautogui.pixelMatchesColor(x, y, expected_color, tolerance=tolerance)

    def find_image(
        self,
        template_path: str,
        confidence: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = False,
    ) -> Optional[Tuple[int, int]]:
        """
        在屏幕上查找模板图像，返回中心坐标

        Args:
            template_path: 模板图像路径
            confidence: 匹配置信度 0-1
            region: 搜索区域
            grayscale: 是否灰度匹配（更快）

        Returns:
            匹配位置中心坐标 (x, y)，未找到返回None
        """
        try:
            if region:
                location = pyautogui.locateCenterOnScreen(
                    template_path,
                    confidence=confidence,
                    region=region,
                    grayscale=grayscale,
                )
            else:
                location = pyautogui.locateCenterOnScreen(
                    template_path,
                    confidence=confidence,
                    grayscale=grayscale,
                )

            if location:
                return (location.x, location.y)
            return None
        except Exception:
            return None

    def find_image_all(
        self,
        template_path: str,
        confidence: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> List[Tuple[int, int]]:
        """
        查找屏幕上所有匹配的图像

        Returns:
            所有匹配位置中心坐标列表
        """
        results = []
        try:
            if region:
                locations = pyautogui.locateAllOnScreen(
                    template_path, confidence=confidence, region=region
                )
            else:
                locations = pyautogui.locateAllOnScreen(
                    template_path, confidence=confidence
                )

            for loc in locations:
                center = pyautogui.center(loc)
                results.append((center.x, center.y))
        except Exception:
            pass
        return results

    def wait_for_image(
        self,
        template_path: str,
        timeout: float = 10.0,
        interval: float = 0.5,
        confidence: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Optional[Tuple[int, int]]:
        """
        等待图像出现

        Args:
            template_path: 模板图像
            timeout: 超时时间（秒）
            interval: 检查间隔
            confidence: 置信度
            region: 搜索区域

        Returns:
            匹配位置，超时返回None
        """
        start = time.time()
        while time.time() - start < timeout:
            pos = self.find_image(template_path, confidence, region)
            if pos:
                return pos
            time.sleep(interval)
        return None

    def wait_for_color(
        self,
        x: int,
        y: int,
        target_color: Tuple[int, int, int],
        timeout: float = 10.0,
        interval: float = 0.1,
        tolerance: int = 0,
    ) -> bool:
        """
        等待指定位置变为目标颜色

        Returns:
            是否在超时前匹配成功
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.pixel_matches(x, y, target_color, tolerance):
                return True
            time.sleep(interval)
        return False

    def click_image(
        self,
        template_path: str,
        confidence: float = 0.8,
        button: str = "left",
        region: Optional[Tuple[int, int, int, int]] = None,
        timeout: float = 5.0,
    ) -> bool:
        """
        找到图像并点击

        Returns:
            是否找到并点击成功
        """
        pos = self.wait_for_image(template_path, timeout, confidence=confidence, region=region)
        if pos:
            pyautogui.click(pos[0], pos[1], button=button)
            return True
        return False

    def get_active_window_region(self) -> Optional[Tuple[int, int, int, int]]:
        """获取活动窗口区域（需要pywin32，Windows）"""
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            rect = win32gui.GetWindowRect(hwnd)
            return (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
        except Exception:
            return None

    def compare_images(
        self, img1_path: str, img2_path: str, threshold: float = 0.95
    ) -> float:
        """
        比较两张图片的相似度

        Returns:
            相似度 0-1
        """
        if not HAS_CV2:
            # 降级方案：用PIL比较
            img1 = Image.open(img1_path).convert("RGB")
            img2 = Image.open(img2_path).convert("RGB")
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            mse = np.mean((arr1 - arr2) ** 2)
            similarity = 1.0 - (mse / (255 ** 2))
            return max(0.0, min(1.0, similarity))

        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        if img1 is None or img2 is None:
            return 0.0

        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        result = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
        return float(result[0][0])

    def record_screen(
        self, output_path: str, duration: float = 5.0, fps: int = 10
    ) -> None:
        """
        录制屏幕为视频（需要opencv）

        Args:
            output_path: 输出视频路径 (.avi)
            duration: 录制时长（秒）
            fps: 帧率
        """
        if not HAS_CV2:
            raise ImportError("录制功能需要 opencv-python")

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(output_path, fourcc, fps, (self._screen_width, self._screen_height))

        frames = int(duration * fps)
        for _ in range(frames):
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
            time.sleep(1.0 / fps)

        out.release()
