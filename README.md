# sysmon — Linux System Health Monitor & Alerting Daemon

## Core Features (v1 scope)
- [DONE] Collect CPU / memory / disk / network metrics
- [DONE] Log metrics with rotation
- [ ] Threshold-based alerting with cooldown
- [ ] CLI: run / check / alerts
- [ ] Runs as a systemd service (non-root)
- [ ] journalctl log watching for error patterns
- [ ] Unit tests for core logic
- [ ] install.sh for one-shot setup

## Explicitly out of scope for v1
- No web dashboard
- No multi-host/remote monitoring
- No Slack/webhook alerting (possible stretch goal only)
- No networking-specific features (this project's focus is Linux fundamentals)

## Status
Day 1 of 9 — environment and scaffold complete.
