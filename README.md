# supOS Bedrock

Deployment orchestration for supOS platform. One command. Web UI. Update notifications. First-run setup.

**Status:** Day 3 Complete - Core orchestration

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status](https://img.shields.io/badge/status-development-yellow.svg)]()

## Overview

supOS-CE uses bash scripts + manual docker-compose. Fragile. Hard for users. No update tracking.

supOS Bedrock changes that:
- One command deploys supOS
- Web UI manages lifecycle
- Update notifications when new container images available
- First-run wizard for user creation and settings

### What It Does
Transforms supOS-CE deployment from:

Transforms supOS-CE deployment from:
```bash
# Before: Manual, fragile, 15+ steps
git clone repo
nano .env  # Edit 48 variables manually
bash install.sh  # Interactive prompts
docker-compose up  # Hope it works
```

To:
```bash
# After: One command, guided setup
docker compose up -d
# Browser: http://localhost:8080
# Click "Install supOS-CE"
# Done.
```

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

## Current Features (Day 3)

### ✅ First-Run Setup Wizard
- System requirements validation (RAM, disk, CPU, Docker)
- Admin user creation with secure password hashing
- Network configuration (domain, port, language)
- Automatic service password generation

### ✅ Configuration Management
- Template-based .env generation (48 variables)
- Single source of truth (config.json)
- Automatic regeneration on container restart
- Volume persistence across deployments

### ✅ supOS-CE Orchestration
- Git submodule integration (no manual clone)
- One-click install button
- Automated volume directory creation
- Docker Compose streaming logs
- 3-phase progress tracking

### ✅ Dashboard
- Dual-mode UI (install vs monitoring)
- Real-time container status
- Configuration state detection
- Auto-refresh service counts


## Quick Start

### Prerequisites
- Docker 24.0+
- Docker Compose 2.24+
- 4GB RAM minimum (8GB recommended)
- 20GB free disk space
- Linux/macOS/Windows with WSL2

### Installation

```bash
# 1. Clone repository
git clone --recurse-submodules https://github.com/leekaize/supos-bedrock
cd supos-bedrock

# 2. Start master container
docker compose up -d

# 3. Open browser
open http://localhost:8080

# 4. Complete setup wizard
# - System validation (automatic)
# - Create admin user
# - Configure network (127.0.0.1 works for local testing)
# - Click "Complete Setup"

# 5. Install supOS-CE
# - Click "Install supOS-CE" button
# - Wait 5-15 minutes (pulls images)
# - Services start automatically

# 6. Access supOS
# - Frontend: http://localhost:8088
# - Backend API: http://localhost:8091
# - Keycloak: http://localhost:8081
```

### Verification

```bash
# Check master status
docker logs supos-bedrock-master

# List running services
docker ps | grep -E "frontend|backend|keycloak"

# View generated config
docker exec supos-bedrock-master cat /app/config/config.json
```

See [QUICKSTART.md](docs/guides/QUICKSTART.md) for detailed setup.

## Architecture

```
User Browser
    ↓
Master Container (Flask + Docker SDK)
    ↓
Docker Socket API
    ↓
supOS-CE Stack (10 services)
    ├─ Frontend (React)
    ├─ Backend (Java)
    ├─ PostgreSQL (metadata)
    ├─ TimescaleDB (time-series)
    ├─ Keycloak (auth)
    ├─ Kong (API gateway)
    ├─ EMQX (MQTT)
    ├─ Node-RED (flows)
    ├─ Portainer (optional)
    └─ Chat2DB (optional)
```

Master container responsibilities:
- Service orchestration (start/stop/restart)
- Health monitoring (ping endpoints, check logs)
- Update detection (compare local vs registry image tags)
- First-run setup (wizard + validation)
- Notification dispatch (push to supOS UI)

**Key Decisions:**
- **Submodule approach:** supOS-CE tracked as git submodule, no runtime clone
- **Config-driven:** .env auto-generated from config.json template
- **Volume management:** Master creates all required directories
- **State detection:** Container count determines configuration status

See [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) for details.

## Roadmap

### Phase 1: Core Orchestration ✅ (Days 1-3)
- [x] Day 1: Master container + validation
- [x] Day 2: Configuration system
- [x] Day 3: First-run wizard + supOS-CE install

### Phase 2: Service Management (Days 4-7)
- [ ] Day 4: Start/stop/restart controls
- [ ] Day 4: Optional service profiles (Portainer, Grafana, etc.)
- [ ] Day 5: Update notification system
- [ ] Day 6: .env visual editor
- [ ] Day 7: Enhanced install progress + error handling

### Phase 3: Production Features (Days 8-11)
- [ ] Day 8: SSL/HTTPS setup
- [ ] Day 9: Backup/restore functionality
- [ ] Day 10: Advanced monitoring dashboard
- [ ] Day 11: Multi-environment configs

### Phase 4: Polish (Days 12-14)
- [ ] Day 12: Performance optimization
- [ ] Day 13: Final testing + documentation
- [ ] Day 14: Demo video + hackathon submission

## Project Structure

```
supos-bedrock/
├── master/                    # Orchestrator
│   ├── app.py                # Flask routes
│   ├── setup_wizard.py       # First-run logic
│   ├── templates/
│   │   ├── setup.html        # Setup wizard
│   │   └── dashboard.html    # Main UI
│   ├── Dockerfile
│   └── requirements.txt
├── services/
│   └── .env.template         # supOS-CE config template
├── supOS-ce/                 # Git submodule
│   └── docker-compose-4c8g.yml
├── tests/
│   └── test_setup_wizard.py
├── docs/
│   ├── guides/
│   │   └── QUICKSTART.md
│   └── architecture/
│       └── ARCHITECTURE.md
├── docker-compose.yml        # Master container definition
└── CHECKPOINT.md             # Daily progress log
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
- Update CHECKPOINT.md with goal + 3 tasks

**Work (4 hours):**
- Ship code incrementally
- Test after each feature
- Ask when blocked >30 min

**Evening (10 min):**
- Log completed tasks
- Note blockers
- Plan tomorrow's priority
- Commit with descriptive message

See [CHECKPOINT.md](CHECKPOINT.md) for daily logs.

## Contributing

This project is part of supOS Global Hackathon 2025.

**Contribution areas:**
- Bug reports (with reproduction steps)
- Feature requests (aligned with roadmap)
- Documentation improvements
- Test coverage expansion

**Not accepting:**
- Changes to supOS-CE submodule (upstream project)
- Breaking changes during hackathon period
- Features not in Phase 1-3 roadmap

---

## Technology Stack

**Master Container:**
- Python 3.11 (Flask web framework)
- Docker SDK for Python
- Werkzeug (password hashing)
- psutil (system monitoring)

**Frontend:**
- Tailwind CSS (styling)
- Vanilla JavaScript (no framework overhead)
- Server-Sent Events (real-time logs)

**Infrastructure:**
- Docker 24.0+
- Docker Compose 2.24+
- Git submodules

---

## Known Limitations (Day 3)

- **No service controls yet:** Start/stop/restart buttons placeholder
- **No optional services:** All services start together
- **Basic progress tracking:** Step-level only, not substep details
- **No update checker:** Image digest comparison not implemented
- **No .env editor:** Manual config.json editing required
- **No backup/restore:** Future feature

See [DAY4_PLAN.md](DAY4_PLAN.md) for upcoming features.

---

## Success Metrics

**Hackathon Goals:**
- [x] One-command deployment works
- [x] First-run wizard functional
- [ ] Service lifecycle management (Day 4)
- [ ] Update notifications (Day 5)
- [ ] Documentation complete
- [ ] Demo video (Day 13)

**Performance Targets:**
- Setup wizard: <2 minutes
- Full install: 5-15 minutes (image pull dependent)
- Service start: <60 seconds
- Dashboard load: <1 second

---

## License

Apache-2.0 - See [LICENSE](LICENSE)

## Hackathon Info

**Event:** supOS Global Hackathon 2025  
**Duration:** Oct 13 - Oct 31, 2025 (14 days)  
**Time Budget:** 4 hours/day = 56 hours total  
**Submission Deadline:** Oct 31, 2025 23:59 UTC  

**Team:** Lee Kai Ze (solo)  
**Contact:** mail@leekaize.com  
**Repository:** https://github.com/leekaize/supos-bedrock

---

## Acknowledgments

**Inspired by:**
- [Nextcloud All-in-One](https://github.com/nextcloud/all-in-one) - Master container pattern
- [supOS-CE](https://github.com/FREEZONEX/supOS-CE) - Core platform

**Built for:** Industrial IoT practitioners who need reliable, reproducible deployments without DevOps expertise.