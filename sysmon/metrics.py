import psutil
import time
from datetime import datetime
from logger import get_logger
import json
from config import load_config
from alerts import check_thresholds
import os

def _read_proc_stat_cpu_line():
    with open("/proc/stat", "r") as f:
        stats = f.readline()

    result = stats.split()[1:]
    return result

def get_psutil_metrics():
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

def get_cpu_percent_manual(sample_interval=0.5):
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


def run_loop(config: dict, sleep_seconds: int = 2) -> None:
    logger = get_logger()
    last_alert_times = {}

    print("sysmon running - press Ctrl+C to stop.")
    try:
        while True:
            ps_metric = get_psutil_metrics()
            manual_cpu = get_cpu_percent_manual()
            nowTime = datetime.now().strftime('%H:%M:%S')

            print(f"{nowTime} | CPU psutil: {ps_metric['cpu_percent']:.2f}% | CPU manual: {manual_cpu:.2f}%"
                  f" | Memory: {ps_metric['mem_percent']:.2f}% | Disk: {ps_metric['disk_percent']:.2f}%"
                  f" | Network (Sent): {ps_metric['net_bytes_sent']}"
                  f" | Network (Received): {ps_metric['net_bytes_recv']}")

            info_dict = {
                "cpu_percent_manual": manual_cpu,
                "cpu_percent_psutil": ps_metric["cpu_percent"],
                "mem_percent": ps_metric["mem_percent"],
                "disk_percent": ps_metric["disk_percent"],
                "net_bytes_sent": ps_metric["net_bytes_sent"],
                "net_bytes_recv": ps_metric["net_bytes_recv"],
            }

            last_alert_times = check_thresholds(
                metrics=ps_metric, config=config, last_alert_times=last_alert_times
            )

            logger.info(json.dumps(info_dict))
            time.sleep(sleep_seconds)

    except KeyboardInterrupt:
        print("\nStopped by user.")


def run_check(config: dict) -> int:
    ps_metric = get_psutil_metrics()

    print(f"CPU: {ps_metric['cpu_percent']:.2f}% | "
          f"Memory: {ps_metric['mem_percent']:.2f}% | "
          f"Disk: {ps_metric['disk_percent']:.2f}%")

    thresholds = config["thresholds"]

    if ps_metric["disk_percent"] >= 95:
        print("CRITICAL: disk usage >= 95%")
        return 2 #critical exit code, written as return code for ease in unit testing

    breached = []
    if ps_metric["cpu_percent"] > thresholds["cpu_percent"]:
        breached.append("cpu_percent")
    if ps_metric["mem_percent"] > thresholds["mem_percent"]:
        breached.append("mem_percent")
    if ps_metric["disk_percent"] > thresholds["disk_percent"]:
        breached.append("disk_percent")

    if breached:
        print(f"WARNING: threshold(s) breached: {', '.join(breached)}")
        return 1 #warning exit code

    print("OK: all metrics within thresholds")
    return 0 #success/all clear exit code


def show_recent_alerts(alerts_log_path: str, num_lines: int = 20) -> None:
    if not os.path.exists(alerts_log_path):
        print("No alerts logged yet.")
        return

    with open(alerts_log_path, "r") as f:
        lines = f.readlines()

    if not lines:
        print("No alerts logged yet.")
        return

    for line in lines[-num_lines:]:
        print(line.rstrip())

