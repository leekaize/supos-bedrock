# supOS Bedrock - Architecture

## Day 2: EMQX Integration

Master container → EMQX (port 1883) → Services network.

MQTT broker handles:
- Node-RED connections
- supOS backend pub/sub
- External device streams

Test: `mosquitto_pub -h localhost -t test/topic -m "test"`

## Pattern: Nextcloud AIO Simplified

Master container orchestrates service containers via Docker socket[^docker-socket].

[^docker-socket]: `/var/run/docker.sock` gives container access to host Docker daemon. Security trade: convenience vs. isolation. Acceptable for single-node deployments.

## Structure

```
supos-bedrock/
├── docker-compose.yml        # Master only
├── services/
│   └── docker-compose.yml    # Services
├── master/
│   ├── Dockerfile            # Python 3.12 + Docker CLI
│   ├── app.py                # Flask orchestrator (71 lines)
│   ├── requirements.txt      # Flask, docker-py, dotenv
│   └── templates/
│       └── dashboard.html    # Single-page UI
├── .env.example              # Config template
└── docs/
    ├── QUICKSTART.md         # Setup guide
    └── ARCHITECTURE.md       # This file
```

## Components

**Master Container**
- Runs: Flask web server (port 8080)
- Mounts: Docker socket (read-only)
- Purpose: Service lifecycle management
- Routes:
  - `GET /` → Dashboard
  - `GET /api/status` → Container states
  - `POST /api/services/start` → Spawn stack
  - `POST /api/services/stop` → Teardown

**Service Stack** (Day 1: Postgres only)
- Isolated network: `supos-bedrock`
- Volumes: Persistent data storage
- Health checks: Service readiness

## Data Flow

1. User opens `localhost:8080`
2. Browser fetches dashboard
3. JavaScript polls `/api/status` every 5s
4. Flask queries Docker socket
5. Status renders in UI

Button click → POST request → Flask → Docker Compose CLI → Services start

## Why This Pattern?

**Nextcloud AIO proved it works:**
- 3M+ downloads
- Handles 10+ containers
- Non-technical users succeed

**Advantages:**
- One command deployment
- Web UI simplifies Docker
- Separation: Master vs. services
- Easy debugging (logs visible)

**Tradeoffs:**
- Docker socket = elevated privilege
- Not Kubernetes-scale (acceptable for supOS)
- Single-node only (MVP scope)

## Security Notes

**Current:** Docker socket exposed to master container. Master runs as root. Acceptable for dev/internal deployments.

**Production:** Add:
- Docker socket proxy[^socket-proxy]
- Non-root user in master
- TLS between master and services
- Secret management (not .env)

[^socket-proxy]: Restricts Docker socket access to read-only operations. Example: Traefik's docker-socket-proxy.

## Testing Strategy

Day 1: Manual verification via browser.
Day 3+: Add pytest for API routes.
Day 7+: Integration tests (service startup/shutdown).

## Comparison: supOS-CE vs. Bedrock

**supOS-CE:** Bash scripts + raw docker-compose. Config scattered. Users must edit YAML. No lifecycle UI.

**Bedrock:** Web UI abstracts Docker. One-command start. Service management via buttons. Config centralized.

Goal: Nextcloud AIO simplicity for supOS platform.

---
**Validated:** Day 1 architecture proven. Postgres start/stop works. Ready for Day 2 service additions.