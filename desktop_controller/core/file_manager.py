# -*- coding: utf-8 -*-
"""
文件管理模块
提供文件浏览、复制、移动、删除、信息查询等功能
"""

import os
import shutil
import time
import hashlib
from typing import List, Optional, Dict, Any
from pathlib import Path


class FileInfo:
    """文件/目录信息封装"""

    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.name = os.path.basename(path)
        self.is_dir = os.path.isdir(path)
        self.is_file = os.path.isfile(path)
        self.exists = os.path.exists(path)

        if self.exists:
            stat = os.stat(path)
            self.size = stat.st_size
            self.create_time = stat.st_ctime
            self.modify_time = stat.st_mtime
            self.access_time = stat.st_atime
        else:
            self.size = 0
            self.create_time = 0
            self.modify_time = 0
            self.access_time = 0

    @property
    def size_human(self) -> str:
        """人类可读的文件大小"""
        return self._format_size(self.size)

    @property
    def extension(self) -> str:
        """文件扩展名（含点）"""
        return os.path.splitext(self.path)[1]

    @property
    def parent(self) -> str:
        """父目录路径"""
        return os.path.dirname(self.path)

    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    def __repr__(self):
        type_str = "DIR" if self.is_dir else "FILE"
        return f"FileInfo({type_str}, '{self.name}', {self.size_human})"


class FileManager:
    """文件管理器"""

    def list_directory(self, path: str = ".", show_hidden: bool = False) -> List[FileInfo]:
        """
        列出目录内容

        Args:
            path: 目录路径
            show_hidden: 是否显示隐藏文件
        """
        results = []
        try:
            for name in os.listdir(path):
                if not show_hidden and name.startswith("."):
                    continue
                full_path = os.path.join(path, name)
                results.append(FileInfo(full_path))
        except PermissionError:
            print(f"权限不足: {path}")
        except FileNotFoundError:
            print(f"目录不存在: {path}")
        return results

    def list_files(self, path: str = ".", extension: Optional[str] = None) -> List[FileInfo]:
        """只列出文件（可选按扩展名过滤）"""
        items = self.list_directory(path)
        files = [f for f in items if f.is_file]
        if extension:
            ext = extension.lower()
            if not ext.startswith("."):
                ext = "." + ext
            files = [f for f in files if f.extension.lower() == ext]
        return files

    def list_dirs(self, path: str = ".") -> List[FileInfo]:
        """只列出子目录"""
        items = self.list_directory(path)
        return [f for f in items if f.is_dir]

    def exists(self, path: str) -> bool:
        """检查路径是否存在"""
        return os.path.exists(path)

    def is_file(self, path: str) -> bool:
        return os.path.isfile(path)

    def is_dir(self, path: str) -> bool:
        return os.path.isdir(path)

    def get_info(self, path: str) -> FileInfo:
        """获取文件/目录信息"""
        return FileInfo(path)

    def create_directory(self, path: str, recursive: bool = True) -> bool:
        """
        创建目录

        Args:
            path: 目录路径
            recursive: 是否递归创建父目录
        """
        try:
            if recursive:
                os.makedirs(path, exist_ok=True)
            else:
                os.mkdir(path)
            return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False

    def copy(self, src: str, dst: str, overwrite: bool = True) -> bool:
        """
        复制文件或目录

        Args:
            src: 源路径
            dst: 目标路径
            overwrite: 是否覆盖已存在的目标
        """
        try:
            if os.path.isdir(src):
                if os.path.exists(dst) and overwrite:
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                if os.path.exists(dst) and not overwrite:
                    return False
                os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
                shutil.copy2(src, dst)
            return True
        except Exception as e:
            print(f"复制失败: {e}")
            return False

    def move(self, src: str, dst: str, overwrite: bool = True) -> bool:
        """移动文件或目录"""
        try:
            if os.path.exists(dst) and overwrite:
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
            shutil.move(src, dst)
            return True
        except Exception as e:
            print(f"移动失败: {e}")
            return False

    def rename(self, src: str, new_name: str) -> bool:
        """重命名文件或目录"""
        try:
            parent = os.path.dirname(src)
            dst = os.path.join(parent, new_name)
            os.rename(src, dst)
            return True
        except Exception as e:
            print(f"重命名失败: {e}")
            return False

    def delete(self, path: str, recursive: bool = True) -> bool:
        """
        删除文件或目录

        Args:
            path: 要删除的路径
            recursive: 目录是否递归删除
        """
        try:
            if os.path.isdir(path):
                if recursive:
                    shutil.rmtree(path)
                else:
                    os.rmdir(path)
            else:
                os.remove(path)
            return True
        except Exception as e:
            print(f"删除失败: {e}")
            return False

    def read_text(self, path: str, encoding: str = "utf-8") -> Optional[str]:
        """读取文本文件内容"""
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败: {e}")
            return None

    def write_text(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """写入文本文件"""
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件失败: {e}")
            return False

    def append_text(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """追加文本到文件"""
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "a", encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"追加文件失败: {e}")
            return False

    def get_file_hash(self, path: str, algorithm: str = "md5") -> Optional[str]:
        """
        计算文件哈希值

        Args:
            path: 文件路径
            algorithm: 哈希算法 md5/sha1/sha256
        """
        try:
            h = hashlib.new(algorithm)
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception as e:
            print(f"计算哈希失败: {e}")
            return None

    def find_files(
        self,
        root: str,
        pattern: str = "*",
        recursive: bool = True,
    ) -> List[FileInfo]:
        """
        按通配符查找文件

        Args:
            root: 搜索根目录
            pattern: 通配符模式（如 *.txt, *.py）
            recursive: 是否递归子目录
        """
        import fnmatch
        results = []

        if recursive:
            for dirpath, _, filenames in os.walk(root):
                for name in filenames:
                    if fnmatch.fnmatch(name, pattern):
                        results.append(FileInfo(os.path.join(dirpath, name)))
        else:
            for name in os.listdir(root):
                full = os.path.join(root, name)
                if os.path.isfile(full) and fnmatch.fnmatch(name, pattern):
                    results.append(FileInfo(full))
        return results

    def find_by_content(
        self,
        root: str,
        keyword: str,
        extensions: Optional[List[str]] = None,
        recursive: bool = True,
    ) -> List[str]:
        """
        按内容关键字查找文件

        Returns:
            包含关键字的文件路径列表
        """
        results = []
        for dirpath, _, filenames in os.walk(root) if recursive else [(root, [], os.listdir(root))]:
            for name in filenames:
                if extensions:
                    if not any(name.lower().endswith(ext.lower()) for ext in extensions):
                        continue
                full = os.path.join(dirpath, name)
                try:
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        if keyword in f.read():
                            results.append(full)
                except Exception:
                    continue
        return results

    def get_directory_size(self, path: str) -> int:
        """获取目录总大小（字节）"""
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for name in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, name))
                except Exception:
                    pass
        return total

    def open_in_explorer(self, path: str) -> bool:
        """在文件资源管理器中打开路径"""
        try:
            if os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", path])
            return True
        except Exception as e:
            print(f"打开失败: {e}")
            return False

    def get_disk_usage(self, path: str = "/") -> Dict[str, Any]:
        """获取磁盘使用情况"""
        total, used, free = shutil.disk_usage(path)
        return {
            "total_gb": round(total / (1024 ** 3), 2),
            "used_gb": round(used / (1024 ** 3), 2),
            "free_gb": round(free / (1024 ** 3), 2),
            "percent": round(used / total * 100, 1),
        }
