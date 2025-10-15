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

## Day 2: EMQX + MQTT

### Start Services

Click "Start Services" in UI.

Expected: postgres + emqx both "running".

### Test MQTT

Terminal:
\`\`\`bash
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test
\`\`\`

### EMQX Dashboard

URL: http://localhost:18083  
Login: admin / public

Expected: Shows 0 clients. Publish/subscribe works.

## Day 3 Onwards: Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-mock

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_setup_wizard.py -v

# With coverage
pytest tests/ --cov=master --cov-report=html
```

### Development Workflow

```bash
# 1. Make changes to master/*
nano master/app.py

# 2. Rebuild master container
docker compose build master

# 3. Restart
docker compose restart master

# 4. View logs
docker logs -f supos-bedrock-master

# 5. Test in browser
open http://localhost:8080
```

### Troubleshooting

**Setup wizard loops:**
```bash
# Check config flag
docker exec supos-bedrock-master python -c "
import setup_wizard
print(setup_wizard.is_first_run())
"
# Should be False after setup complete
```

**Install button doesn't show:**
```bash
# Check API status
curl http://localhost:8080/api/supos/status | jq

# Expected: {"installed": true, "configured": false}
```

**Volume errors during install:**
```bash
# Volumes created automatically, but verify path
docker exec supos-bedrock-master ls /volumes/supos/data
```