# -*- coding: utf-8 -*-
"""
定时任务调度器
支持指定时间执行、间隔执行、定时执行宏或脚本
"""

import time
import threading
import json
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, Any, List
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduledTask:
    """定时任务"""

    def __init__(
        self,
        task_id: str,
        name: str,
        action: Callable,
        schedule_type: str = "once",
        run_at: Optional[datetime] = None,
        interval_seconds: float = 60.0,
        cron_expr: str = "",
        args: tuple = (),
        kwargs: dict = None,
    ):
        self.task_id = task_id
        self.name = name
        self.action = action
        self.schedule_type = schedule_type  # once, interval, daily, cron
        self.run_at = run_at
        self.interval_seconds = interval_seconds
        self.cron_expr = cron_expr
        self.args = args
        self.kwargs = kwargs or {}
        self.status = TaskStatus.PENDING
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = run_at
        self.run_count = 0
        self.error: Optional[str] = None

    def should_run(self, now: datetime) -> bool:
        """判断是否应该执行"""
        if self.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            return False

        if self.schedule_type == "once":
            return self.run_at and now >= self.run_at

        elif self.schedule_type == "interval":
            if self.last_run is None:
                return self.run_at is None or now >= self.run_at
            return (now - self.last_run).total_seconds() >= self.interval_seconds

        elif self.schedule_type == "daily":
            if self.run_at and now >= self.run_at:
                if self.last_run is None or self.last_run.date() < now.date():
                    return True
            return False

        return False

    def execute(self) -> bool:
        """执行任务"""
        self.status = TaskStatus.RUNNING
        self.last_run = datetime.now()
        self.run_count += 1
        try:
            self.action(*self.args, **self.kwargs)
            self.status = TaskStatus.COMPLETED if self.schedule_type == "once" else TaskStatus.PENDING
            if self.schedule_type == "interval":
                self.next_run = datetime.now() + timedelta(seconds=self.interval_seconds)
            return True
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "schedule_type": self.schedule_type,
            "run_at": self.run_at.isoformat() if self.run_at else None,
            "interval_seconds": self.interval_seconds,
            "status": self.status.value,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "error": self.error,
        }


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._task_counter = 0

    @property
    def is_running(self) -> bool:
        return self._running

    def add_task(
        self,
        name: str,
        action: Callable,
        schedule_type: str = "once",
        run_at: Optional[datetime] = None,
        interval_seconds: float = 60.0,
        delay_seconds: float = 0,
        args: tuple = (),
        kwargs: dict = None,
    ) -> str:
        """
        添加定时任务

        Args:
            name: 任务名称
            action: 要执行的函数
            schedule_type: 调度类型 once/interval/daily
            run_at: 首次执行时间
            interval_seconds: 间隔执行的秒数
            delay_seconds: 延迟多少秒后执行（替代run_at）
            args: 位置参数
            kwargs: 关键字参数

        Returns:
            任务ID
        """
        self._task_counter += 1
        task_id = f"task_{self._task_counter}_{int(time.time())}"

        if delay_seconds > 0 and run_at is None:
            run_at = datetime.now() + timedelta(seconds=delay_seconds)

        task = ScheduledTask(
            task_id=task_id,
            name=name,
            action=action,
            schedule_type=schedule_type,
            run_at=run_at,
            interval_seconds=interval_seconds,
            args=args,
            kwargs=kwargs,
        )

        with self._lock:
            self.tasks[task_id] = task

        return task_id

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.CANCELLED
                return True
        return False

    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        with self._lock:
            return self.tasks.pop(task_id, None) is not None

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """获取任务信息"""
        return self.tasks.get(task_id)

    def list_tasks(self) -> List[ScheduledTask]:
        """列出所有任务"""
        return list(self.tasks.values())

    def start(self) -> None:
        """启动调度器（后台线程）"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def _run_loop(self) -> None:
        """调度循环"""
        while self._running:
            now = datetime.now()
            with self._lock:
                for task in list(self.tasks.values()):
                    if task.should_run(now):
                        # 在新线程中执行，避免阻塞调度
                        t = threading.Thread(target=task.execute, daemon=True)
                        t.start()
            time.sleep(0.5)

    def run_pending(self) -> int:
        """
        手动执行所有到期任务（非线程模式）

        Returns:
            执行的任务数量
        """
        now = datetime.now()
        count = 0
        with self._lock:
            for task in list(self.tasks.values()):
                if task.should_run(now):
                    if task.execute():
                        count += 1
        return count

    def clear_completed(self) -> int:
        """清理已完成/失败/取消的任务"""
        to_remove = []
        with self._lock:
            for tid, task in self.tasks.items():
                if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                    to_remove.append(tid)
            for tid in to_remove:
                del self.tasks[tid]
        return len(to_remove)

    def save_schedule(self, filepath: str) -> bool:
        """保存任务计划到文件"""
        try:
            data = {
                "tasks": [t.to_dict() for t in self.tasks.values()],
                "saved_at": datetime.now().isoformat(),
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
