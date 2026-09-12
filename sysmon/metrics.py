import psutil
import time
from datetime import datetime
from logger import get_logger
import json
from config import load_config
from alerts import check_thresholds

def _read_proc_stat_cpu_line():
    with open("/proc/stat", "r") as f:
        stats = f.readline()

    result = stats.split()[1:]
    return result

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

def main():
    try:
        logger = get_logger()
        config = load_config()
        last_alert_times = {}

        while True:
            ps_metric = get_psutil_metrics()
            ps_metric_cpu = ps_metric["cpu_percent"]
            manual_cpu = get_cpu_percent_manual()

            metric_mem = ps_metric["mem_percent"]
            metric_disk = ps_metric["disk_percent"]
            metric_net_sent = ps_metric["net_bytes_sent"]
            metric_net_recv = ps_metric["net_bytes_recv"]

            nowTime = datetime.now().strftime('%H:%M:%S')

            print(f"{nowTime} | CPU psutil: {ps_metric_cpu:.2f}% | CPU manual: {manual_cpu:.2f}%" 
                  f" | Memory: {metric_mem:.2f}% | Disk: {metric_disk:.2f}% | Network (Sent): {metric_net_sent}" 
                  f" | Network (Received): {metric_net_recv}")

            info_dict = {
                "cpu_percent_manual": manual_cpu,
                "cpu_percent_psutil": ps_metric_cpu,
                "mem_percent": metric_mem,
                "disk_percent": metric_disk,
                "net_bytes_sent": metric_net_sent,
                "net_bytes_recv": metric_net_recv
            }

            last_alert_times = check_thresholds(metrics=ps_metric, config=config,last_alert_times=last_alert_times)

            json_info = json.dumps(info_dict)
            logger.info(json_info)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()
