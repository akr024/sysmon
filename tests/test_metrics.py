import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sysmon"))

from unittest.mock import patch
from metrics import run_check

FAKE_CONFIG = {
    "thresholds": {"cpu_percent": 85, "mem_percent": 90, "disk_percent": 90},
    "alert_cooldown_seconds": 300,
    "paths": {"metrics_log": "/tmp/test_metrics.log", "alerts_log": "/tmp/test_alerts.log"},
}


def test_run_check_returns_0_when_healthy():
    fake_metrics = {"cpu_percent": 10.0, "mem_percent": 20.0, "disk_percent": 30.0,
                     "net_bytes_sent": 0, "net_bytes_recv": 0}
    with patch("metrics.get_psutil_metrics", return_value=fake_metrics):
        assert run_check(FAKE_CONFIG) == 0


def test_run_check_returns_1_on_warning():
    fake_metrics = {"cpu_percent": 95.0, "mem_percent": 20.0, "disk_percent": 30.0,
                     "net_bytes_sent": 0, "net_bytes_recv": 0}
    with patch("metrics.get_psutil_metrics", return_value=fake_metrics):
        assert run_check(FAKE_CONFIG) == 1


def test_run_check_returns_2_on_critical_disk():
    fake_metrics = {"cpu_percent": 10.0, "mem_percent": 20.0, "disk_percent": 97.0,
                     "net_bytes_sent": 0, "net_bytes_recv": 0}
    with patch("metrics.get_psutil_metrics", return_value=fake_metrics):
        assert run_check(FAKE_CONFIG) == 2


def test_critical_takes_precedence_over_warning():
    fake_metrics = {"cpu_percent": 95.0, "mem_percent": 20.0, "disk_percent": 97.0,
                     "net_bytes_sent": 0, "net_bytes_recv": 0}
    with patch("metrics.get_psutil_metrics", return_value=fake_metrics):
        assert run_check(FAKE_CONFIG) == 2
