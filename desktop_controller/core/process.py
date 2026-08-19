# -*- coding: utf-8 -*-
"""
进程管理模块
提供进程列举、查找、启动、终止、资源监控等功能
"""

import os
import time
import subprocess
import psutil
from typing import List, Optional, Dict, Any


class ProcessInfo:
    """进程信息封装"""

    def __init__(self, pid: int, name: str = "", status: str = "",
                 cpu_percent: float = 0.0, memory_mb: float = 0.0,
                 create_time: float = 0.0, num_threads: int = 0,
                 exe_path: str = "", cmdline: List[str] = None):
        self.pid = pid
        self.name = name
        self.status = status
        self.cpu_percent = cpu_percent
        self.memory_mb = memory_mb
        self.create_time = create_time
        self.num_threads = num_threads
        self.exe_path = exe_path
        self.cmdline = cmdline or []

    def __repr__(self):
        return (f"ProcessInfo(pid={self.pid}, name='{self.name}', "
                f"cpu={self.cpu_percent:.1f}%, mem={self.memory_mb:.1f}MB)")


class ProcessController:
    """进程控制器"""

    def list_processes(self, refresh_cpu: bool = False) -> List[ProcessInfo]:
        """
        列出所有进程

        Args:
            refresh_cpu: 是否刷新CPU使用率（需要等待0.1秒）
        """
        processes = []
        for proc in psutil.process_iter(["pid", "name", "status", "cpu_percent",
                                          "memory_info", "create_time", "num_threads",
                                          "exe", "cmdline"]):
            try:
                info = proc.info
                mem = info.get("memory_info")
                mem_mb = mem.rss / (1024 * 1024) if mem else 0.0
                processes.append(ProcessInfo(
                    pid=info["pid"],
                    name=info.get("name", ""),
                    status=info.get("status", ""),
                    cpu_percent=info.get("cpu_percent", 0.0) or 0.0,
                    memory_mb=mem_mb,
                    create_time=info.get("create_time", 0.0),
                    num_threads=info.get("num_threads", 0),
                    exe_path=info.get("exe", "") or "",
                    cmdline=info.get("cmdline", []) or [],
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if refresh_cpu:
            time.sleep(0.1)
            for p in processes:
                try:
                    proc = psutil.Process(p.pid)
                    p.cpu_percent = proc.cpu_percent()
                except Exception:
                    pass

        return processes

    def find_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """按PID查找进程"""
        try:
            proc = psutil.Process(pid)
            mem = proc.memory_info()
            return ProcessInfo(
                pid=proc.pid,
                name=proc.name(),
                status=proc.status(),
                cpu_percent=proc.cpu_percent(),
                memory_mb=mem.rss / (1024 * 1024),
                create_time=proc.create_time(),
                num_threads=proc.num_threads(),
                exe_path=proc.exe() or "",
                cmdline=proc.cmdline() or [],
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def find_by_name(self, name: str, exact: bool = False) -> List[ProcessInfo]:
        """
        按名称查找进程

        Args:
            name: 进程名（不区分大小写）
            exact: 是否精确匹配
        """
        all_procs = self.list_processes()
        name_lower = name.lower()
        if exact:
            return [p for p in all_procs if p.name.lower() == name_lower]
        return [p for p in all_procs if name_lower in p.name.lower()]

    def start_process(
        self,
        command: str,
        arguments: List[str] = None,
        working_dir: Optional[str] = None,
        shell: bool = False,
        hidden: bool = False,
    ) -> Optional[subprocess.Popen]:
        """
        启动新进程

        Args:
            command: 可执行文件路径或命令
            arguments: 参数列表
            working_dir: 工作目录
            shell: 是否通过shell执行
            hidden: 是否隐藏窗口（Windows）

        Returns:
            Popen对象，失败返回None
        """
        try:
            cmd = [command] + (arguments or [])
            creationflags = 0
            if hidden and os.name == "nt":
                creationflags = subprocess.CREATE_NO_WINDOW

            return subprocess.Popen(
                cmd,
                cwd=working_dir,
                shell=shell,
                creationflags=creationflags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print(f"启动进程失败: {e}")
            return None

    def terminate(self, pid: int, force: bool = False, timeout: float = 3.0) -> bool:
        """
        终止进程

        Args:
            pid: 进程ID
            force: 是否强制终止（kill）
            timeout: 优雅终止等待超时

        Returns:
            是否成功终止
        """
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
                return True
            else:
                proc.terminate()
                proc.wait(timeout=timeout)
                return True
        except psutil.NoSuchProcess:
            return True  # 已经不存在
        except psutil.TimeoutExpired:
            # 超时则强制终止
            try:
                proc.kill()
                return True
            except Exception:
                return False
        except Exception:
            return False

    def terminate_by_name(self, name: str, force: bool = False) -> int:
        """
        按名称终止所有匹配的进程

        Returns:
            终止的进程数量
        """
        procs = self.find_by_name(name)
        count = 0
        for p in procs:
            if self.terminate(p.pid, force=force):
                count += 1
        return count

    def kill(self, pid: int) -> bool:
        """强制终止进程（SIGKILL）"""
        return self.terminate(pid, force=True)

    def kill_by_name(self, name: str) -> int:
        """按名称强制终止所有匹配进程"""
        return self.terminate_by_name(name, force=True)

    def get_cpu_percent(self, interval: float = 0.1) -> float:
        """获取系统整体CPU使用率"""
        return psutil.cpu_percent(interval=interval)

    def get_memory_info(self) -> Dict[str, Any]:
        """
        获取系统内存信息

        Returns:
            包含 total/available/used/percent 的字典
        """
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "used_gb": round(mem.used / (1024 ** 3), 2),
            "percent": mem.percent,
        }

    def get_disk_info(self, path: str = "/") -> Dict[str, Any]:
        """获取磁盘使用信息"""
        disk = psutil.disk_usage(path)
        return {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "percent": disk.percent,
        }

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统综合信息"""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": self.get_memory_info(),
            "boot_time": psutil.boot_time(),
            "platform": os.name,
        }

    def get_process_tree(self, pid: int, max_depth: int = 3) -> Dict[str, Any]:
        """
        获取进程树（子进程结构）
        """
        try:
            proc = psutil.Process(pid)
            return self._build_tree(proc, max_depth, 0)
        except Exception as e:
            return {"error": str(e)}

    def _build_tree(self, proc: psutil.Process, max_depth: int, depth: int) -> Dict[str, Any]:
        """递归构建进程树"""
        if depth > max_depth:
            return {}
        try:
            children = []
            for child in proc.children():
                children.append(self._build_tree(child, max_depth, depth + 1))
            return {
                "pid": proc.pid,
                "name": proc.name(),
                "children": children,
            }
        except Exception:
            return {}

    def wait_for_process(
        self, name: str, timeout: float = 10.0, interval: float = 0.5
    ) -> Optional[ProcessInfo]:
        """
        等待指定名称的进程出现

        Returns:
            找到的进程信息，超时返回None
        """
        start = time.time()
        while time.time() - start < timeout:
            procs = self.find_by_name(name)
            if procs:
                return procs[0]
            time.sleep(interval)
        return None

    def print_top_processes(self, n: int = 10, by: str = "cpu") -> None:
        """
        打印占用资源最多的前N个进程

        Args:
            n: 显示数量
            by: 排序依据 'cpu' 或 'memory'
        """
        procs = self.list_processes(refresh_cpu=True)
        if by == "cpu":
            procs.sort(key=lambda p: p.cpu_percent, reverse=True)
        else:
            procs.sort(key=lambda p: p.memory_mb, reverse=True)

        print(f"\nTop {n} 进程（按{'CPU' if by == 'cpu' else '内存'}排序）:")
        print(f"{'PID':>8} {'CPU%':>7} {'MEM(MB)':>9} {'名称'}")
        print("-" * 50)
        for p in procs[:n]:
            print(f"{p.pid:>8} {p.cpu_percent:>7.1f} {p.memory_mb:>9.1f} {p.name}")
