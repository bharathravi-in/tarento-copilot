# Getting PostgreSQL Running - Quick Setup Guide

## Problem
The backend returns 500 errors on auth endpoints because PostgreSQL is not running. The code is correct, but it needs a database connection.

## Solution: Start PostgreSQL

### Option 1: Using Docker (Recommended - Easiest)

```bash
# Pull and run PostgreSQL container
docker run -d \
  --name tarento-postgres \
  -e POSTGRES_USER=tarento \
  -e POSTGRES_PASSWORD=tarento_dev \
  -e POSTGRES_DB=tarento_db \
  -p 5432:5432 \
  postgres:16-alpine

# Verify it's running
docker ps | grep postgres
```

**Expected output:**
```
tarento-postgres   postgres:16-alpine   ...   Up 2 seconds   0.0.0.0:5432->5432/tcp
```

### Option 2: Using Local PostgreSQL Installation

```bash
# Create database and user
sudo -u postgres createdb tarento_db
sudo -u postgres psql -c "CREATE USER tarento WITH PASSWORD 'tarento_dev';"
sudo -u postgres psql -c "ALTER DATABASE tarento_db OWNER TO tarento;"

# Verify connection
psql -U tarento -d tarento_db -c "SELECT 1;"
```

## Verify Database is Running

```bash
# Test connection
psql -U tarento -d tarento_db -c "SELECT now();"

# Or in Python
python3 << 'EOF'
import psycopg2
try:
    conn = psycopg2.connect("dbname=tarento_db user=tarento password=tarento_dev host=localhost")
    print("✓ PostgreSQL is running and accessible")
    conn.close()
except Exception as e:
    print(f"✗ Cannot connect: {e}")
EOF
```

## Run Database Migrations

Once PostgreSQL is running:

```bash
cd backend

# Apply all migrations to create tables
alembic upgrade head

# Verify tables were created
psql -U tarento -d tarento_db -c "\dt"
```

## Populate Test Data

```bash
python3 seed_db.py
```

**Expected output:**
```
✓ Created 2 organizations
✓ Created 13 permissions
✓ Created roles
✓ Created 3 users
✓ Created 2 projects
✓ Created 2 agent configurations

✅ Database seeding completed successfully!

Test Credentials:
  Organization 1: acme.com
    - Email: admin@acme.com, Password: SecurePassword123!
    - Email: member@acme.com, Password: SecurePassword123!
  Organization 2: startup.io
    - Email: admin@startup.io, Password: SecurePassword123!
```

## Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

## Test the API

### 1. Check Health
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "app": "Tarento Enterprise AI Co-Pilot"}
```

### 2. Access Swagger UI
```
Open browser: http://localhost:8000/docs
```

### 3. Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "NewPassword123!",
    "organization_id": "PASTE_ORG_ID_HERE"
  }'
```

### 4. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@acme.com",
    "password": "SecurePassword123!"
  }'
```

**Response will include:**
```json
{
  "user": {
    "id": "...",
    "email": "admin@acme.com",
    "username": "admin_acme",
    "full_name": "Alice Administrator",
    ...
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 5. Use the Token
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer PASTE_ACCESS_TOKEN_HERE"
```

## Troubleshooting

### Docker Permission Denied
```
Error: permission denied while trying to connect to the Docker daemon
```
**Solution:** Add your user to docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Port 5432 Already in Use
```
Error: Address already in use
```
**Solution:** 
```bash
# Check what's using port 5432
lsof -i :5432

# Kill it
sudo kill -9 PID

# Or use different port
docker run -p 5433:5432 ...
```

### PostgreSQL Container Won't Start
```bash
# Check logs
docker logs tarento-postgres

# Remove and retry
docker rm tarento-postgres
docker run -d --name tarento-postgres ...
```

### Cannot Connect to Database
```
FATAL: password authentication failed for user "tarento"
```
**Solution:** Verify credentials in .env file:
```bash
# .env should have:
DATABASE_URL="postgresql://tarento:tarento_dev@localhost:5432/tarento_db"
```

## Complete Quick Start Sequence

```bash
# 1. Start PostgreSQL
docker run -d \
  --name tarento-postgres \
  -e POSTGRES_USER=tarento \
  -e POSTGRES_PASSWORD=tarento_dev \
  -e POSTGRES_DB=tarento_db \
  -p 5432:5432 \
  postgres:16-alpine

# 2. Wait for PostgreSQL to be ready (10-15 seconds)
sleep 15

# 3. Run migrations
cd backend
alembic upgrade head

# 4. Seed test data
python3 seed_db.py

# 5. Start backend
uvicorn app.main:app --reload

# 6. In another terminal, test the API
curl http://localhost:8000/health
```

## Success Indicators

✅ **You'll know it's working when:**
- PostgreSQL container is running: `docker ps | grep postgres`
- Migration completes without errors
- Seed script shows test credentials
- API responds at http://localhost:8000/health
- Swagger UI loads at http://localhost:8000/docs
- Auth endpoints return 200 (not 500)

## Next Steps

Once everything is running:
1. Test endpoints in Swagger UI
2. Login with test credentials
3. Call other endpoints with access token
4. Review QUICKSTART.md for more details
5. Check NEXT_STEPS.md for Week 2 priorities

---

**Status:** System is code-complete and ready to run once PostgreSQL is available
**PostgreSQL Required:** Yes
**Database Migrations:** Required
**Test Data:** Optional but recommended
