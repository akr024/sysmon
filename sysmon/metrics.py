import psutil
import time
from datetime import datetime

def _read_proc_stat_cpu_line():
    with open("/proc/stat", "r") as f:
        stats = f.readline()

    result = stats.split()[1:]
    return result

def get_cpu_percent_manual(sample_interval=0.5):
    """
    Takes two samples of /proc/stat 'sample_interval' seconds apart,
    computes and returns CPU usage as a float percentage (0-100).
    """
    sample1 = _read_proc_stat_cpu_line()
    time.sleep(sample_interval)
    sample2 = _read_proc_stat_cpu_line()
    deltas = [0]*len(sample1)
    
    for i in range(len(sample1)):
        deltas[i] = int(sample2[i]) - int(sample1[i])

    total_delta = 0
    idle_delta = deltas[3]

    for delta in deltas:
        total_delta += delta
    
    usage_percent = (total_delta-idle_delta)/total_delta * 100
    return usage_percent

def get_psutil_metrics():
    """
    'cpu_percent' (float)
    'mem_percent' (float)
    'disk_percent' (float)
    'net_bytes_sent' (int)
    'net_bytes_recv' (int)
    """

    metrics = {}
    
    metrics["cpu_percent"] = psutil.cpu_percent(interval=0.5)
    
    memObj = psutil.virtual_memory()
    metrics["mem_percent"] = memObj.percent
    
    diskObj = psutil.disk_usage('/')
    metrics["disk_percent"] = diskObj.percent
    
    netObj = psutil.net_io_counters()
    metrics["net_bytes_sent"] = netObj.bytes_sent
    metrics["net_bytes_recv"] = netObj.bytes_recv

    return metrics

def main():
    try:
        while True:
            ps_metric = get_psutil_metrics()
            ps_metric_cpu = ps_metric["cpu_percent"]
            manual_cpu = get_cpu_percent_manual()
            print(f"{datetime.now().strftime('%H:%M:%S')} | CPU psutil: {ps_metric_cpu:.2f}% | CPU manual: {manual_cpu:.2f}%")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()
