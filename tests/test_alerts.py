import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sysmon"))

import time
from alerts import check_thresholds

FAKE_CONFIG = {
    "thresholds": {"cpu_percent": 85, "mem_percent": 90, "disk_percent": 90},
    "alert_cooldown_seconds": 300,
    "paths": {"alerts_log": "/tmp/test_alerts.log"},
}


def test_alert_fires_on_breach():
    metrics = {"cpu_percent": 95.0, "mem_percent": 50.0, "disk_percent": 50.0}
    result = check_thresholds(metrics, FAKE_CONFIG, {})
    assert "cpu_percent" in result


def test_alert_suppressed_within_cooldown():
    metrics = {"cpu_percent": 95.0, "mem_percent": 50.0, "disk_percent": 50.0}
    first_result = check_thresholds(metrics, FAKE_CONFIG, {})
    first_time = first_result["cpu_percent"]

    second_result = check_thresholds(metrics, FAKE_CONFIG, first_result)
    assert second_result["cpu_percent"] == first_time  # unchanged = suppressed


def test_alert_fires_again_after_cooldown_expires():
    metrics = {"cpu_percent": 95.0, "mem_percent": 50.0, "disk_percent": 50.0}
    old_time = time.time() - 1000
    last_alert_times = {"cpu_percent": old_time}

    result = check_thresholds(metrics, FAKE_CONFIG, last_alert_times)
    assert result["cpu_percent"] > old_time


def test_multiple_metrics_tracked_independently():
    metrics = {"cpu_percent": 95.0, "mem_percent": 95.0, "disk_percent": 50.0}
    result = check_thresholds(metrics, FAKE_CONFIG, {})
    assert "cpu_percent" in result
    assert "mem_percent" in result
    assert "disk_percent" not in result
