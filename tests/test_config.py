import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sysmon"))

import pytest
from config import load_config, ConfigError

VALID_YAML = """
thresholds:
  cpu_percent: 85
  mem_percent: 90
  disk_percent: 90
alert_cooldown_seconds: 300
paths:
  metrics_log: /tmp/metrics.log
  alerts_log: /tmp/alerts.log
"""


def test_valid_config_loads(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(VALID_YAML)
    result = load_config(str(config_file))
    assert result["thresholds"]["cpu_percent"] == 85


def test_missing_thresholds_raises(tmp_path):
    bad_yaml = """
alert_cooldown_seconds: 300
paths:
  metrics_log: /tmp/metrics.log
  alerts_log: /tmp/alerts.log
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(bad_yaml)
    with pytest.raises(ConfigError):
        load_config(str(config_file))


def test_cpu_percent_out_of_range_raises(tmp_path):
    bad_yaml = VALID_YAML.replace("cpu_percent: 85", "cpu_percent: 150")
    config_file = tmp_path / "config.yaml"
    config_file.write_text(bad_yaml)
    with pytest.raises(ConfigError):
        load_config(str(config_file))


def test_cpu_percent_wrong_type_raises(tmp_path):
    bad_yaml = VALID_YAML.replace("cpu_percent: 85", 'cpu_percent: "85"')
    config_file = tmp_path / "config.yaml"
    config_file.write_text(bad_yaml)
    with pytest.raises(ConfigError):
        load_config(str(config_file))
