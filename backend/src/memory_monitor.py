import psutil
import time
import threading
import sys

def monitor_memory(threshold_gb: float = 50.0, check_interval: float = 5.0):
    """
    Periodically checks the process's memory usage.
    If used memory exceeds threshold_gb, the process is terminated.
    """
    while True:
        process = psutil.Process()
        mem_used_gb = process.memory_info().rss / (1024 ** 3)
        if mem_used_gb > threshold_gb:
            print(f"Memory usage exceeded {threshold_gb}GB: {mem_used_gb:.2f}GB. Terminating process.")
            sys.exit(1)
        time.sleep(check_interval)

def start_memory_monitor(threshold_gb: float = 50.0, check_interval: float = 5.0):
    monitor_thread = threading.Thread(target=monitor_memory, args=(threshold_gb, check_interval), daemon=True)
    monitor_thread.start()