import time
import threading
from datetime import datetime, timedelta

class AutoTimeGenerator:
    """自动自增的时间生成器"""
    def __init__(self, step_seconds=1, start_time=None):
        # self.current_time = datetime.now()
        self.start_time = None
        self.step = step_seconds
        self._running = False
        self._lock = threading.Lock()
        self.set_start_time(start_time)

    def start(self):
        """启动自动时间自增线程"""
        if not self._running:
            self._running = True
            threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        """内部线程逻辑"""
        while self._running:
            time.sleep(self.step)
            with self._lock:
                self.start_time += timedelta(seconds=self.step)

    def stop(self):
        """停止自增"""
        self._running = False

    def get_time_list(self):
        """返回当前时间的 [年, 月, 日, 时, 分, 秒]"""
        with self._lock:
            t = self.start_time
        if t is None:
            return None
        else:
            return [t.year%2000, t.month, t.day, t.hour, t.minute, t.second]

    def set_start_time(self, start_time):
        if start_time is not None and len(start_time) == 6:
            self.start_time = datetime(*start_time)
        else:
            self.start_time = datetime.now()
