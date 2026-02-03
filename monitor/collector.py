import psutil
import time


def sample_metrics():
    """Return a snapshot dict with cpu%, mem%, total bytes sent/recv and process count."""
    ts = time.time()
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    net = psutil.net_io_counters()
    # process count
    try:
        procs = len(psutil.pids())
    except Exception:
        # fallback: iterate
        procs = sum(1 for _ in psutil.process_iter())

    return {
        'timestamp': ts,
        'cpu': cpu,
        'mem': mem,
        'net_sent': net.bytes_sent,
        'net_recv': net.bytes_recv,
        'processes': procs
    }
