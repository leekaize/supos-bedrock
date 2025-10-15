# supOS Bedrock

Deployment orchestration for supOS platform. One command. Web UI. Update notifications. First-run setup.

**Phase:** Active Development (Day 2 complete)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status](https://img.shields.io/badge/status-development-yellow.svg)]()

## Overview

supOS-CE uses bash scripts + manual docker-compose. Fragile. Hard for users. No update tracking.

supOS Bedrock changes that:
- One command deploys supOS
- Web UI manages lifecycle
- Update notifications when new container images available
- First-run wizard for user creation and settings

**Core Pattern:** Master container orchestrates services via Docker socket[^docker-socket].

[^docker-socket]: `/var/run/docker.sock` gives container access to host Docker daemon. Read-only mount limits risk.

## Key Features

### Production-Ready Orchestration
- Single master container manages entire supOS stack
- Docker socket API for service lifecycle control
- Service health monitoring with real-time status

### Update Intelligence
- **Container update detection:** Master checks Docker registry for new images
- **Notification system:** Dashboard shows which services have updates available
- **supOS front-end integration:** Push notifications to supOS UI when updates detected
- One-click update application (future)

### First-Run Experience
- **Setup wizard on first launch:** Create admin user, set domain, configure passwords
- **Validation checks:** Verify system requirements before deployment
- **Configuration persistence:** Settings saved to volume, survives container restarts

## Quick Start

```bash
# 1. Clone
git clone https://github.com/leekaize/supos-bedrock
cd supos-bedrock

# 2. Start (first-run wizard will appear)
docker compose up -d --build

# 3. Complete setup wizard
open http://localhost:8080/setup
# Follow prompts: Create admin, set domain, configure services

# 4. Access dashboard
open http://localhost:8080
```

See [QUICKSTART.md](docs/guides/QUICKSTART.md) for detailed setup.

## Architecture

```
Master Container (Flask + Docker SDK)
    ↓
Docker Socket (service control)
    ↓
Docker Registry API (update checks)
    ↓
Service Stack (Postgres, EMQX, Node-RED...)
    ↓
supOS Front-End (update notifications)
```

Master container responsibilities:
- Service orchestration (start/stop/restart)
- Health monitoring (ping endpoints, check logs)
- Update detection (compare local vs registry image tags)
- First-run setup (wizard + validation)
- Notification dispatch (push to supOS UI)

See [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) for pattern details.

## Roadmap

### Phase 1: Core Orchestration (Days 1-7)
- [x] Day 1: Master container + Postgres
- [x] Day 2: Add EMQX (MQTT broker)
- [ ] Day 3: Update notifications + first-run wizard
- [ ] Day 4: Add Node-RED (flow integration)
- [ ] Day 5: Add Kong/Konga (API gateway)
- [ ] Day 6: Service health checks
- [ ] Day 7: Integration testing

### Phase 2: Production Features (Days 8-14)
- [ ] Day 8: HTTPS/SSL certificates
- [ ] Day 9: Backup/restore UI
- [ ] Day 10: supOS front-end notification integration
- [ ] Day 11: Service logs in UI
- [ ] Day 12: Documentation polish
- [ ] Day 13: Demo video
- [ ] Day 14: Hackathon submission

### Phase 3: Future (Post-Hackathon)
- One-click updates
- Custom CoreOS images
- Advanced backup systems
- Multi-node orchestration

## Project Structure

```
supos-bedrock/
├── CHECKPOINT.md              # Daily progress tracking
├── docker-compose.yml         # Master container
├── services/
│   └── docker-compose.yml    # Service stack
├── master/
│   ├── Dockerfile
│   ├── app.py                # Flask orchestrator
│   ├── update_checker.py     # Image version comparator
│   ├── setup_wizard.py       # First-run configuration
│   └── templates/
│       ├── dashboard.html
│       └── setup.html
├── docs/
│   ├── guides/               # User documentation
│   │   └── QUICKSTART.md
│   └── architecture/         # Technical specs
│       ├── ARCHITECTURE.md
│       └── UPDATE_SYSTEM.md
└── .env.example
```

## Update Notification System

Master container checks Docker Hub every 6 hours:

1. **Fetch current tags:** Query registry API for latest image digests
2. **Compare versions:** Local image SHA vs registry SHA
3. **Flag outdated:** Mark services with updates in dashboard
4. **Notify supOS:** POST to supOS notification endpoint with update details
5. **User action:** Dashboard shows "Update Available" badge

User sees notification in both:
- Master UI (localhost:8080)
- supOS front-end (main application)

See [UPDATE_SYSTEM.md](docs/architecture/UPDATE_SYSTEM.md) for implementation.

## First-Run Setup

On first launch (no config file detected):

1. **Redirect to wizard:** All routes redirect to `/setup`
2. **System checks:** Verify Docker socket, network connectivity, disk space
3. **User creation:** Set admin username, email, password
4. **Domain config:** Set FQDN or use localhost
5. **Service passwords:** Generate or set Postgres, Redis, etc.
6. **Write config:** Save to `master/config.json` (persisted volume)
7. **Deploy services:** Trigger `docker compose up` for service stack

After setup complete, wizard disappears. Config can be changed via settings UI.

## Daily Workflow

**Morning (5 min):**
- Update CHECKPOINT.md: Goal + 3 tasks

**Work (4 hours):**
- Ship code
- Ask when blocked >30 min

**Evening (10 min):**
- Log: Completed + blockers + tomorrow's priority
- Commit with hash

See [CHECKPOINT.md](CHECKPOINT.md) for daily logs.

## Target

**supOS Global Hackathon 2025**
- 14-day sprint (4 hours/day)
- 56 hours total
- Submission deadline: 2025-10-31

## Target

**supOS Global Hackathon 2025**
- 14-day sprint (4 hours/day)
- 56 hours total
- Submission deadline: 2025-10-31

## Success Metrics

- [ ] One-command deployment works
- [ ] First-run wizard functional
- [ ] Update notifications appear in dashboard
- [ ] Update notifications push to supOS front-end
- [ ] Web UI shows service status
- [ ] Basic lifecycle controls (start/stop/restart)
- [ ] Documentation complete
- [ ] Demo video recorded
- [ ] Hackathon submission ready

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

Apache-2.0 - See [LICENSE](LICENSE)

## Citation

```bibtex
@misc{supos-bedrock,
  author = {Lee Kai Ze},
  title = {supOS Bedrock: Deployment Orchestration for supOS Platform},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/leekaize/supos-bedrock}
}
```

## Contact

- Issues: Bug reports and feature requests
- Discussions: Architecture questions
- Email: mail@leekaize.com

Built for: supOS Global Hackathon 2025