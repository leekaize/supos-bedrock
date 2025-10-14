# supOS Bedrock - Quickstart

## Prerequisites
- Docker installed
- Docker Compose v2+
- 4GB RAM minimum
- Port 8080 available

## Day 1 Proof of Concept

### 1. Clone
```bash
git clone https://github.com/leekaize/supos-bedrock
cd supos-bedrock
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env - change POSTGRES_PASSWORD
```

### 3. Start Master
```bash
docker compose up -d
```

Wait 30 seconds for build completion.

### 4. Verify
Open `http://localhost:8080`

Expected: "supOS Bedrock" dashboard loads.

### 5. Start Services
Click "Start Services" button in web UI.

Wait 10 seconds. Click "Refresh".

Expected: postgres shows "running" status.

### 6. Test Postgres
```bash
docker exec -it supos-postgres psql -U supos -d supos -c "SELECT version();"
```

Expected: PostgreSQL version prints.

## Success Criteria
- [x] Master container running
- [x] Web UI accessible
- [x] Postgres starts via UI
- [x] Postgres responds to queries

## Next Steps (Day 2)
Add EMQX container to services stack.

## Troubleshooting

**Port 8080 in use:**
```bash
lsof -i :8080
# Kill process or change port in docker-compose.yml
```

**Docker socket permission denied:**
```bash
sudo usermod -aG docker $USER
# Logout and login
```

**Master build fails:**
Check Docker has internet access for pulling Python image.

---
**Status:** Day 1 complete. Baseline established.