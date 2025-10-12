# supOS Bedrock

**Industry-grade deployment orchestration for supOS platform.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status](https://img.shields.io/badge/status-development-yellow.svg)]()

## Overview

supOS Bedrock makes deploying supOS as easy as running a single container. Web-based management. Automatic health checks. Built-in backup/restore.

**Current deployment:** Bash scripts + manual docker-compose  
**Bedrock:** One command. Web UI. Enterprise reliability.

**Inspired by:** Nextcloud All-in-One

---

## Features

✅ **One-Command Deployment**
```bash
docker run -d --name supos-bedrock \
  -p 8080:8080 \
  -v supos_bedrock_data:/data \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  ghcr.io/leekaize/supos-bedrock:latest
```

✅ **Web-Based Management**
- Service status dashboard
- Start/stop/restart controls
- Real-time logs
- Health monitoring

✅ **Lifecycle Automation**
- Automatic health checks
- Auto-restart on failure
- Version management
- Backup/restore via UI

✅ **Enterprise Reliability**
- Container orchestration
- Dependency management
- Graceful shutdowns
- Update rollback

---

## Quick Start

**Prerequisites:**
- Docker installed
- 4GB RAM minimum (8GB recommended)
- 20GB disk space

**Deploy:**
```bash
docker run -d \
  --name supos-bedrock \
  -p 8080:8080 \
  -v supos_bedrock_data:/data \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  ghcr.io/leekaize/supos-bedrock:latest
```

**Access:** https://localhost:8080

**First run:**
1. Copy generated admin password from logs
2. Complete setup wizard
3. Click "Deploy supOS"
4. Wait 5-10 minutes
5. Access supOS at provided URL

Full instructions: [QUICKSTART.md](docs/guides/QUICKSTART.md)

---

## Architecture

```
┌─────────────────────────────────────┐
│   supOS Bedrock Master Container    │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  Web UI      │  │ Orchestrator│ │
│  │  (Flask)     │  │  (Python)   │ │
│  └──────────────┘  └─────────────┘ │
│           │              │          │
│           └──────┬───────┘          │
│                  │                  │
│         Docker Socket Access        │
└──────────────────┼──────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐    ┌────▼────┐    ┌───▼────┐
│ supOS │    │Database │    │ Redis  │
│Backend│    │(Postgres│    │ Cache  │
└───────┘    └─────────┘    └────────┘
```

**Master orchestrates all services via Docker API.**

---

## Components

### Master Container
- **Orchestrator:** Python service managing container lifecycle
- **Web UI:** Management interface (Flask)
- **Health Monitor:** Automatic failure detection
- **Backup Manager:** Volume export/import

### Managed Services
- supOS Backend
- supOS Frontend
- PostgreSQL database
- Redis cache
- [Additional services from compose]

---

## Project Status

**Phase:** Development (Day 1)

**Roadmap:**
- [x] Project structure
- [ ] Master container framework
- [ ] Service orchestration
- [ ] Web UI implementation
- [ ] Health check system
- [ ] Backup/restore functionality
- [ ] Documentation

**Target:** supOS Global Hackathon 2025 submission

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions.

**Structure:**
```
supos-bedrock/
├── master-container/    # Orchestration container
├── coreos-image/        # (Phase 2) Fedora CoreOS
├── docs/                # Documentation
└── tests/               # Test suites
```

---

## Comparison

| Feature | Current Scripts | Bedrock |
|---------|----------------|---------|
| Installation | System-level | Containerised |
| Management | CLI only | Web UI |
| Health checks | None | Automatic |
| Backup | Manual | Built-in |
| Updates | Risky | Automated |
| Monitoring | External tools | Integrated |

---

## Contributing

**We welcome:**
- Orchestration improvements
- UI enhancements
- Documentation
- Testing

**Development setup:**
```bash
git clone https://github.com/leekaize/supos-bedrock.git
cd supos-bedrock
# See CONTRIBUTING.md for details
```

---

## License

Apache-2.0 - See [LICENSE](LICENSE)

---

## Citation

```bibtex
@misc{supos-bedrock,
  author = {Lee Kai Ze},
  title = {supOS Bedrock: Industry-Grade Deployment Orchestration},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/leekaize/supos-bedrock}
}
```

---

## References

**Baseline:** Nextcloud All-in-One - https://github.com/nextcloud/all-in-one  
**Target:** supOS Platform - https://github.com/FREEZONEX/2025_supOS_Global_Hackathon

---

## Contact

- **Issues:** Bug reports and features
- **Discussions:** Architecture and deployment questions
- **Email:** mail@leekaize.com

**Built for:** Industrial IoT deployments, edge computing, production supOS installations