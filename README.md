# supOS Bedrock

Deployment orchestration for supOS platform. One command. Web UI. Inspired by Nextcloud AIO simplicity.

**Phase:** Active Development (Day 1 in progress)

## Overview

supOS-CE uses bash scripts + manual docker-compose. Fragile. Hard for users.

supOS Bedrock changes that. One command deploys supOS. Web UI manages lifecycle.

**Core Pattern:** Master container orchestrates services via Docker socket[^docker-socket].

[^docker-socket]: `/var/run/docker.sock` gives container access to host Docker daemon. Read-only mount limits risk.

## Quick Start

```bash
# 1. Clone
git clone https://github.com/leekaize/supos-bedrock
cd supos-bedrock

# 2. Configure
cp .env.example .env
nano .env  # Change POSTGRES_PASSWORD

# 3. Start
docker compose up -d --build

# 4. Verify
curl http://localhost:8080  # Should return HTML
open http://localhost:8080
```

See [QUICKSTART.md](docs/guides/QUICKSTART.md) for detailed setup.

## Architecture

```
Master Container (Flask + Docker SDK)
    ↓
Docker Socket
    ↓
Service Stack (Postgres, EMQX, Node-RED...)
```

See [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) for pattern details.

## Roadmap

### Phase 1: Core Orchestration (Days 1-7)
- [x] Day 1: Master container + Postgres
- [ ] Day 2: Add EMQX (MQTT broker)
- [ ] Day 3: Add Node-RED (flow integration)
- [ ] Day 4: Add Kong/Konga (API gateway)
- [ ] Day 5: Add Keycloak (authentication)
- [ ] Day 6: Service health checks
- [ ] Day 7: Integration testing

### Phase 2: Production Features (Days 8-14)
- [ ] Day 8: HTTPS/SSL certificates
- [ ] Day 9: Backup/restore UI
- [ ] Day 10: Configuration validation
- [ ] Day 11: Service logs in UI
- [ ] Day 12: Documentation polish
- [ ] Day 13: Demo video
- [ ] Day 14: Hackathon submission

### Phase 3: Future (Post-Hackathon)
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
│   └── templates/
├── docs/
│   ├── guides/               # User documentation
│   │   └── QUICKSTART.md
│   └── architecture/         # Technical specs
│       └── ARCHITECTURE.md
└── .env.example
```

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

## Success Metrics

- [ ] One-command deployment works
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