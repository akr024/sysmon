import yaml

class ConfigError(Exception):
    pass

def load_config(path: str = "/home/akr/projects/sysmon/config.yaml") -> dict:
    with open(path, "r") as config:
        raw_yaml = config.read()

    yaml_string = yaml.safe_load(raw_yaml)

    if(not yaml_string):
          raise ConfigError("Config.yaml is empty")

    #top-level exist checks
    if(yaml_string.get("thresholds") == None):
        raise ConfigError("Missing required field: thresholds")


    #threshold-checks: cpu percent
    if(yaml_string.get("thresholds").get("cpu_percent") == None):
          raise ConfigError("Missing required field: thresholds.cpu_percent")
    if(type(yaml_string.get("thresholds").get("cpu_percent")) != int and type(yaml_string.get("thresholds").get("cpu_percent")) != float):
          raise ConfigError("Type error: thresholds.cpu_percent must be int or float")
    if(yaml_string.get("thresholds").get("cpu_percent") < 0 or yaml_string.get("thresholds").get("cpu_percent") > 100):
          raise ConfigError("Value range error: thresholds.cpu_percent must be between 0 and 100")

    #threshold-checks: mem percent
    if(yaml_string.get("thresholds").get("mem_percent") == None):
          raise ConfigError("Missing required field: thresholds.mem_percent")
    if(type(yaml_string.get("thresholds").get("mem_percent")) != int and type(yaml_string.get("thresholds").get("mem_percent")) != float):
          raise ConfigError("Type error: thresholds.mem_percent must be int or float")
    if(yaml_string.get("thresholds").get("mem_percent") < 0 or yaml_string.get("thresholds").get("mem_percent") > 100):
          raise ConfigError("Value range error: thresholds.mem_percent must be between 0 and 100")

    
    #threshold-checks: mem percent
    if(yaml_string.get("thresholds").get("disk_percent") == None):
          raise ConfigError("Missing required field: thresholds.disk_percent")
    if(type(yaml_string.get("thresholds").get("disk_percent")) != int and type(yaml_string.get("thresholds").get("disk_percent")) != float):
          raise ConfigError("Type error: thresholds.disk_percent must be int or float")
    if(yaml_string.get("thresholds").get("disk_percent") < 0 or yaml_string.get("thresholds").get("disk_percent") > 100):
          raise ConfigError("Value range error: thresholds.disk_percent must be between 0 and 100")

    if(yaml_string.get("alert_cooldown_seconds") == None):
          raise ConfigError("Missing required field: alert_cooldown_seconds")
    if(type(yaml_string.get("alert_cooldown_seconds")) != int and type(yaml_string.get("alert_cooldown_seconds")) != float):
          raise ConfigError("Type error: alert_cooldown_seconds must be int or float")
    if(yaml_string.get("alert_cooldown_seconds") < 0):
          raise ConfigError("Value range error: alert_cooldown_seconds must be >= 0")

    if(yaml_string.get("paths") == None):
          raise ConfigError("Missing required field: paths")
    if(yaml_string.get("paths").get("metrics_log") == None):
          raise ConfigError("Missing required field: paths.metrics_log")
    if(yaml_string.get("paths").get("alerts_log") == None):
          raise ConfigError("Missing required field: paths.alerts_log")

    return yaml_string
