# sysmon

A lightweight Linux system health monitor and alerting daemon, written in Python. It watches CPU, memory, disk, and network usage, logs everything in a structured format, raises alerts when thresholds are breached, and runs as a proper systemd service under its own unprivileged user.

I built this to get genuinely comfortable with core Linux internals - process introspection, systemd, logging, permissions, SELinux - rather than just knowing the commands from certification study. My background going in was RHCSA, CCNA, and CCNA Automation, which is solid on networking and basic admin work but doesn't force you to actually understand what's happening underneath a tool like `top` or a `systemctl start`. This project is scoped specifically around that gap.

## What it does

- Collects CPU, memory, disk, and network metrics every few seconds
- Calculates CPU usage two ways: once via `psutil`, and once by reading `/proc/stat` directly and doing the delta calculation by hand, mostly so I'd actually understand what `psutil` is doing under the hood instead of trusting a library blindly
- Logs metrics as structured JSON, with automatic log rotation so the log file can't grow unbounded
- Compares metrics against configurable thresholds and fires alerts, with cooldown logic so a sustained breach doesn't spam identical alerts every polling cycle
- Watches the systemd journal for error patterns (`oom-killer`, `segfault`, etc.) system-wide, not just its own output
- Exposes a small CLI (`run`, `check`, `alerts`, `watch-logs`), with `check` returning Unix-style exit codes (0/1/2) so it can be wired into cron or an external monitoring system without anyone having to parse text output
- Runs as a dedicated, non-root systemd service, with proper SIGTERM handling so a `systemctl stop` doesn't just yank the process mid-write

## Architecture

The project is split into small, single-purpose modules rather than one script, mostly so I could reason about and test each piece independently:

```
cli.py          -> entry point, parses args, loads config, dispatches
metrics.py      -> collects metrics (psutil + manual /proc/stat), run_loop/run_check
logger.py       -> configures rotating file loggers (reused for both metrics and alerts)
alerts.py       -> threshold comparison + cooldown logic, writes to alerts.log
config.py       -> loads and validates config.yaml, fails loudly on bad input
log_watcher.py  -> tails journalctl, regex-matches error patterns, writes to alerts.log
```

`cli.py` is the only place that ties these together. None of the other modules import from each other except where they genuinely need to (`alerts.py` and `log_watcher.py` both use `logger.py`, for instance) - the idea being that `logger.py` doesn't know or care what "bad" means, `alerts.py` decides what's bad, and `cli.py` just wires the pieces together based on what the user asked for.

Metrics logging and alert logging are two separate files on disk (`sysmon.log` and `alerts.log`) for the same reason you'd keep a firehose of routine data separate from the small number of things that actually need a human's attention - you don't want to grep through thousands of routine snapshots to find the three lines that mattered.

## Installation

```bash
git clone <this repo>
cd sysmon
./install.sh
```

`install.sh` sets up the virtual environment, installs dependencies, creates the `sysmon` system user, sets up log directories with correct ownership, adds the service account to the `systemd-journal` group (needed for `watch-logs`), applies the SELinux context rules the service needs (see `TROUBLESHOOTING.md` for why these are necessary), installs the systemd unit, and starts the service.

It's idempotent - safe to re-run if something changes, it won't fail just because the user or SELinux rule already exists.

## Configuration

`config.yaml`:

```yaml
thresholds:
  cpu_percent: 85
  mem_percent: 90
  disk_percent: 90

alert_cooldown_seconds: 300

paths:
  metrics_log: /var/log/sysmon/sysmon.log
  alerts_log: /var/log/sysmon/alerts.log
```

`load_config()` validates all of this at startup - every threshold has to be a number between 0 and 100, the cooldown has to be non-negative, and both log paths have to be present. If any of that's wrong, the program refuses to start and tells you exactly which field is the problem, rather than limping along with bad data and failing somewhere confusing three function calls later.

## Usage

```bash
sysmon run                  # continuous monitoring loop, logs + alerts, Ctrl+C to stop
sysmon check                # one-shot health check
sysmon alerts --lines 20    # show recent alerts
sysmon watch-logs           # tail the journal for system-wide error patterns
```

`check` is the one worth calling out - it doesn't just print something and exit 0 every time. It returns:

- `0` - everything's within threshold
- `1` - at least one metric breached its threshold
- `2` - disk usage is at or above 95%, regardless of the configured threshold, since a near-full disk is a categorically more urgent problem than a routine CPU spike

That means something like this actually works, and isn't just for show:

```bash
sysmon check
if [ $? -eq 2 ]; then
    echo "paging on-call"
fi
```

## Design decisions

**Why a dedicated non-root user instead of running as root.** The service runs as `sysmon`, a system account with no home directory and `nologin` as its shell. If there's ever a bug in this code, or a dependency gets compromised, the blast radius is whatever that one low-privilege account can touch - nowhere near what root could do. The `nologin` shell specifically means the account can own a running process but nobody can actually log into it interactively, even with the right password.

**Why JSON for metrics but plain text for alerts.** Metrics are logged one JSON object per line, which makes them trivially machine-parseable if I ever wanted to feed them into something else later, with zero regex needed. Alerts are plain readable text instead, because they're meant to be scanned quickly by a human during an actual incident, not parsed downstream - different logs, different audiences, different formats.

**Why cooldown logic exists on alerting.** Without it, a CPU spike that lasts ten minutes with a two-second polling interval would generate 300 nearly-identical alerts. This is a real, named problem in operations - alert fatigue - where too many alerts means the important one gets lost in the noise. Each metric tracks its own cooldown independently, so a noisy CPU alert doesn't suppress or interfere with a separate disk alert.

**Why `check` uses actual Unix exit codes instead of just printing status.** This is exactly how tools like Nagios plugins work - the entire point is letting other software (cron, a monitoring system, a shell script) branch on the result without parsing text. Building `check` this way was a deliberate choice to make the tool actually composable with other Linux tooling, not just runnable in isolation.

**Why the log watcher runs as a separate mode instead of a background thread inside the main loop.** I considered threading it into `run_loop()` directly, but given the time I had, running it as its own independent CLI subcommand was simpler to get right and gives cleaner failure isolation - if the log watcher has a problem, it can't take metrics collection down with it. The tradeoff is you need two things running instead of one unified daemon, which I'd revisit if I had more time.

**Why testing focuses on pure logic and skips the main loop.** `check_thresholds()`, `load_config()`, and `run_check()`'s exit-code logic are all pure functions - same input, same output, no dependency on live system state - so they're cheap to test exhaustively with made-up data. `run_loop()` and the actual `psutil` calls depend on real, unpredictable hardware state and run forever, which would need heavier integration-testing machinery to test meaningfully. I tested the parts where tests add real value instead of chasing full coverage for its own sake.

## Known limitations

This is a single-host tool by design - no dashboard, no remote/multi-host monitoring, no distributed anything. The log watcher's pattern matching includes broad terms like `error` and `fail`, which will produce real false positives on lines that happen to contain those words innocuously; a more robust version would need an allowlist or more specific patterns. Config validation checks types and ranges but doesn't yet handle every malformed-YAML shape gracefully - a `thresholds:` value that's a string instead of a nested mapping will currently raise an `AttributeError` instead of the cleaner `ConfigError` everything else uses.
