# Technical Specification - supOS Bedrock

**Version:** 0.1.0 | **Updated:** 2025-10-12

---

## System Overview

Industry-grade deployment orchestration for supOS platform. One-command installation. Web-based management. Nextcloud AIO pattern.

**Mission:** Make supOS deployment as reliable as enterprise infrastructure.

---

## Current State (Baseline)

**Existing supOS deployment:**
- Bash scripts for installation
- Manual docker-compose management
- No unified interface
- No backup/restore automation
- Fragile (order-dependent, not idempotent)

**Problems solved by Bedrock:**
- Single container orchestrates everything
- Web UI abstracts complexity
- Automatic health checks
- Built-in backup/restore
- Version management

---

## Architecture

### Master Container Pattern

**Inspired by:** Nextcloud AIO (https://github.com/nextcloud/all-in-one)

**Core concept:**
1. Master container has Docker socket access
2. Spawns/manages all supOS service containers
3. Web UI for lifecycle operations
4. Health monitoring + auto-restart
5. Backup/restore via interface

### Components

**Master Container:**
- Python orchestrator (Docker SDK)
- Flask/FastAPI web UI
- SQLite state database
- Health check engine
- Backup manager

**Managed Services:**
- PostgreSQL (supOS database)
- Redis (caching)
- supOS backend
- supOS frontend
- [Others from compose file]

---

## Design Decisions

### D001: Python Orchestrator

**Why Python:**
- Docker SDK well-maintained
- Async support (health checks)
- Web framework integration
- Rapid prototyping (70-hour constraint)

**Alternatives rejected:**
- Go: Steeper learning curve
- Bash: Not maintainable
- Node.js: Less Docker SDK maturity

### D002: Flask for UI

**Why Flask:**
- Lightweight
- Template engine built-in
- Sufficient for management interface

**Alternatives:**
- FastAPI: Overkill for simple UI
- Django: Too heavy
- Pure JS: Adds complexity

### D003: SQLite for State

**Why SQLite:**
- No separate database needed
- Persists in master volume
- Sufficient for orchestration state

**State tracked:**
- Container versions
- Configuration
- Backup history
- User settings

---

## Deployment Flow

### Installation

```bash
docker run -d \
  --name supos-bedrock \
  -p 8080:8080 \
  -v supos_bedrock_data:/data \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  ghcr.io/leekaize/supos-bedrock:latest
```

**User accesses:** `https://server-ip:8080`

### First Run Wizard

1. Generate admin password
2. Configure data directory
3. Select services to enable
4. Review settings
5. Click "Deploy supOS"
6. Wait for containers to start
7. Access supOS via provided URL

---

## Service Management

### Lifecycle Operations

**Start:** Pull images, create containers, health check loop  
**Stop:** Graceful shutdown, preserve data  
**Update:** Pull new images, recreate containers  
**Restart:** Stop + Start with zero downtime target  
**Backup:** Export volumes + database dumps  
**Restore:** Import volumes, recreate from backup  

### Health Checks

**Per-service checks:**
- HTTP endpoint (if applicable)
- TCP port availability
- Container status
- Log error detection

**Frequency:** 30s for critical, 2min for non-critical

**Actions on failure:**
- Log event
- Attempt restart (max 3 times)
- Alert via UI
- Disable auto-restart if persistent

---

## Web Interface

### Pages

1. **Dashboard:** Service status, resource usage, recent events
2. **Services:** Enable/disable, logs, restart controls
3. **Configuration:** Environment variables, ports, volumes
4. **Backup:** Create backup, restore from backup, schedule
5. **Updates:** Check versions, apply updates, rollback
6. **Logs:** Aggregated logs from all services

### Technology

- Flask backend
- Jinja2 templates
- Tailwind CSS (via CDN)
- HTMX for dynamic updates (optional)
- WebSockets for live logs

---

## Security

### Access Control

- Admin password generated on first run
- Stored hashed (bcrypt)
- HTTPS via self-signed cert (user can replace)
- Session timeout after 30 min

### Docker Socket

- Mounted read-only where possible
- Operations validated before execution
- No arbitrary command execution
- Whitelisted image sources

---

## CoreOS Integration (Phase 2)

**If time permits:**

### Custom Image

**Butane config generates:**
- Ignition file for first boot
- Pulls Bedrock container automatically
- Sets up Cockpit management
- Configures WireGuard

**Target platforms:**
- Raspberry Pi 5 (ARM64)
- x86_64 VMs
- Bare metal servers

### User Experience

1. Download CoreOS ISO with Bedrock pre-configured
2. Flash to device
3. Boot
4. Access Cockpit at `https://device-ip:9090`
5. Bedrock auto-starts, deploys supOS
6. Manage via Bedrock UI or Cockpit

---

## Performance Requirements

### Resource Usage

**Master container:**
- CPU: <5% idle, <20% during operations
- RAM: <200MB
- Disk: <100MB

**Target system:**
- Minimum: 4GB RAM, 2 cores, 20GB disk
- Recommended: 8GB RAM, 4 cores, 50GB disk

### Deployment Time

**Fresh install:** <10 minutes (network dependent)  
**Update:** <5 minutes  
**Backup:** <2 minutes (dependent on data size)  
**Restore:** <5 minutes  

---

## Testing Strategy

### Unit Tests

- Orchestrator functions
- Health check logic
- Backup/restore operations

### Integration Tests

- Full deployment flow
- Service lifecycle
- Update mechanism

### Acceptance Criteria

- [ ] One-command deployment works
- [ ] All supOS services start successfully
- [ ] Web UI accessible and functional
- [ ] Health checks detect failures
- [ ] Backup/restore completes without data loss
- [ ] Update process doesn't break installation

---

## Documentation Requirements

### User Documentation

- QUICKSTART.md (installation)
- ARCHITECTURE.md (how it works)
- TROUBLESHOOTING.md (common issues)

### Developer Documentation

- CONTRIBUTING.md (development setup)
- API.md (orchestrator Python API)
- DESIGN.md (architecture decisions)

---

## Open Questions

1. **supOS service dependencies:** What's the startup order? (Research Day 1)
2. **Backup strategy:** Which volumes critical? (Research Day 2)
3. **Update conflicts:** How to handle schema migrations? (Design Day 3)
4. **Resource limits:** Should we enforce container limits? (Decide Day 4)

---

## Success Metrics

**Deployment simplicity:**
- Current: 10+ manual steps
- Target: 1 command

**Reliability:**
- Current: Manual monitoring required
- Target: Auto-restart, health checks

**Update process:**
- Current: Stop everything, manual update, hope it works
- Target: Click button, automated with rollback

---

## References

- [Nextcloud AIO](https://github.com/nextcloud/all-in-one)
- [Docker SDK for Python](https://docker-py.readthedocs.io/)
- [supOS Hackathon](https://github.com/FREEZONEX/2025_supOS_Global_Hackathon)