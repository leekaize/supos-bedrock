# Contributing to supOS Bedrock

**Status:** Active development. Day 1-14 sprint for supOS Global Hackathon 2025.

## Development Setup

### Prerequisites
```bash
docker --version        # 24.0+
docker compose version  # v2+
python --version        # 3.12+ (optional, for local Flask dev)
```

### Local Development

**Master container (Flask):**
```bash
cd master
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Access: `http://localhost:8080`

**Live reload:** Restart Flask after code changes.

### Testing Changes

**Build master:**
```bash
docker compose build master
docker compose up -d
```

**Check logs:**
```bash
docker logs -f supos-bedrock-master
```

**Test services stack:**
```bash
cd services
docker compose up -d
docker ps  # Verify all running
cd ..
```

## Daily Workflow (Aligned with tinyol-hitl)

**Morning (5 min):**
```bash
nano CHECKPOINT.md
# Update: Day X morning checkpoint
# Goal + 3 tasks
```

**Work (4 hours):**
- Ship code
- Ask when blocked >30 min
- Test locally before commit

**Evening (10 min):**
```bash
nano CHECKPOINT.md
# Log: Completed + blockers + tomorrow's priority

git add -A
git commit -m "Day X: [feature description]"
git push origin main

# Paste commit hash into CHECKPOINT.md
```

## Repository Structure

```
supos-bedrock/
├── CHECKPOINT.md              # Daily logs (update daily)
├── docker-compose.yml         # Master (rarely change)
├── services/
│   └── docker-compose.yml    # Add services here
├── master/
│   ├── app.py                # Flask routes
│   ├── templates/
│   │   └── dashboard.html    # UI updates
│   └── requirements.txt      # Python deps
├── docs/
│   ├── guides/               # User-facing docs
│   │   └── QUICKSTART.md
│   └── architecture/         # Technical specs
│       └── ARCHITECTURE.md
└── .env.example              # Config template
```

## Commit Standards

**Format:**
```
Day X: [Component] Brief description

- Bullet point detail 1
- Bullet point detail 2
```

**Examples:**
```
Day 1: Master container orchestration baseline

- Master container with Flask UI
- Postgres proof of concept
- Docker socket orchestration working
```

```
Day 2: EMQX integration

- Added EMQX to services stack
- MQTT connectivity verified
- Dashboard shows EMQX status
```

## Adding New Services

**Pattern:** All services go in `services/docker-compose.yml`

**Steps:**
1. Add service definition
2. Update `master/app.py` status route
3. Update `master/templates/dashboard.html` UI
4. Test start/stop via UI
5. Document in `docs/guides/QUICKSTART.md`

**Example (EMQX):**

```yaml
# services/docker-compose.yml
emqx:
  image: emqx/emqx:5.4.0
  container_name: supos-emqx
  environment:
    - EMQX_NAME=supos
  ports:
    - "1883:1883"
    - "18083:18083"
  networks:
    - supos-bedrock
```

## Testing Checklist

Before commit:
- [ ] Master container builds without errors
- [ ] Web UI loads at localhost:8080
- [ ] All services start via UI button
- [ ] All services stop via UI button
- [ ] Status refresh shows correct states
- [ ] No Docker errors in logs

## Getting Help

**Blocked >30 min?** Open issue with:
- What you tried
- Error output (full)
- Expected vs actual behavior

**Discussion needed?** Use GitHub Discussions.

## Sprint Timeline

**Days 1-7:** Core orchestration (services + lifecycle)
**Days 8-14:** Production features (backup, SSL, docs)

See [CHECKPOINT.md](CHECKPOINT.md) for daily progress.

## License

Apache-2.0. All contributions licensed under same terms.