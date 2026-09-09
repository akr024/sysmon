import logging
from logging.handlers import RotatingFileHandler

def get_logger(
    name: str = "sysmon",
    log_file: str = "/var/log/sysmon/sysmon.log",
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
    level=logging.INFO,
) -> logging.Logger:

    sysmon_logger = logging.getLogger(name)
    sysmon_logger.setLevel(level)
    
    if not sysmon_logger.handlers:
    
        rotatingHandler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        rotatingHandler.setFormatter(formatter)
        sysmon_logger.addHandler(rotatingHandler)

    return sysmon_logger
