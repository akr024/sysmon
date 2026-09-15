import argparse
import sys
from config import load_config, ConfigError
from metrics import run_loop, run_check, show_recent_alerts

DEFAULT_CONFIG_PATH = "/home/akr/projects/sysmon/config.yaml"


def main():
    parser = argparse.ArgumentParser(prog="sysmon", description="Linux system health monitor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run continuous monitoring loop")
    run_parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to config.yaml")
    run_parser.add_argument("--interval", type=int, default=2, help="Seconds between checks")

    check_parser = subparsers.add_parser("check", help="Run a single health check and exit")
    check_parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to config.yaml")

    alerts_parser = subparsers.add_parser("alerts", help="Show recent alerts")
    alerts_parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to config.yaml")
    alerts_parser.add_argument("--lines", type=int, default=20, help="Number of recent alert lines to show")

    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except ConfigError as e:
        print(f"Config error: {e}")
        sys.exit(3)

    if args.command == "run":
        try:
            run_loop(config, sleep_seconds=args.interval)
        except PermissionError as e:
            print(f"Permission error: {e}")
            sys.exit(3)

    elif args.command == "check":
        try:
            exit_code = run_check(config)
        except PermissionError as e:
            print(f"Permission error: {e}")
            sys.exit(3)
        sys.exit(exit_code)

    elif args.command == "alerts":
        show_recent_alerts(config["paths"]["alerts_log"], args.lines)


if __name__ == "__main__":
    main()
