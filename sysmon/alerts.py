import time
from logger import get_logger
import logging

def check_thresholds(metrics: dict, config: dict, last_alert_times: dict) -> dict:

    alert_logger = get_logger(name="alert", log_file=config["paths"]["alerts_log"], level=logging.WARNING)

    cpu_threshold = config["thresholds"]["cpu_percent"]
    cpu_val = metrics["cpu_percent"]

    currTime = time.time()

    cpu_time = last_alert_times.get("cpu_percent",0)

    if(cpu_val > cpu_threshold and currTime - cpu_time > config["alert_cooldown_seconds"]):
            alert_logger.warning(f"CPU Usage {cpu_val}% Exceeds Threshold {cpu_threshold}%")
            last_alert_times["cpu_percent"] = currTime

    mem_threshold = config["thresholds"]["mem_percent"]
    mem_val = metrics["mem_percent"]
    
    mem_time = last_alert_times.get("mem_percent",0)

    if(mem_val > mem_threshold and currTime - mem_time > config["alert_cooldown_seconds"]):
            alert_logger.warning(f"Memory Usage {mem_val}% Exceeds Threshold {mem_threshold}%")
            last_alert_times["mem_percent"] = currTime

    disk_threshold = config["thresholds"]["disk_percent"]
    disk_val = metrics["disk_percent"]

    disk_time = last_alert_times.get("disk_percent",0)

    if(disk_val > disk_threshold and currTime - disk_time > config["alert_cooldown_seconds"]):
            alert_logger.warning(f"Disk Usage {disk_val}% Exceeds Threshold {disk_threshold}%")
            last_alert_times["disk_percent"] = currTime

    return last_alert_times
