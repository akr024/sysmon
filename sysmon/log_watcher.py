import subprocess
import re
from logger import get_logger

_PATTERN = re.compile(r"error|fail|oom-killer|segfault", re.IGNORECASE)


def watch_journal(alerts_log_path: str) -> None:
    alert_logger = get_logger(name="alert", log_file=alerts_log_path)

    process = subprocess.Popen(
        ["journalctl", "-f", "--no-pager"],
        stdout=subprocess.PIPE,
        text=True,
    )

    print("Watching journal for error patterns — press Ctrl+C to stop.")
    try:
        for line in process.stdout:
            line = line.strip()
            if _PATTERN.search(line):
                message = f"Log pattern match: {line}"
                print(message)
                alert_logger.warning(message)
    except KeyboardInterrupt:
        print("\nStopping log watcher...")
        process.terminate()
