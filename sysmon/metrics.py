import psutil

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
