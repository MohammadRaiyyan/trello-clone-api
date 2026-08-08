# Trello API

Backend API for the Trello-style application built with FastAPI, PostgreSQL, SQLModel/SQLAlchemy, Alembic and Docker.

## Prerequisites

Make sure you have:

- Python 3.13+
- Docker
- Docker Compose
- Git

---

## 1. Clone the repository

```bash
git clone <repository-url>
cd trello-api
```

---

## 2. Create and activate virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If the project uses `pyproject.toml`, install the project dependencies using the package manager configured for the project.

---

## 4. Environment variables

Create a `.env` file in the project root.

Example:

```env
APP_NAME=Trello API
APP_VERSION=1.0.0

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/trello

JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

RESEND_API_KEY=your-resend-api-key
EMAIL_FROM=your-verified-email@example.com
```

Do not commit `.env` to Git.

---

# Docker

## 5. Start PostgreSQL with Docker

If the project contains a `docker-compose.yml` / `compose.yml`:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

View PostgreSQL logs only:

```bash
docker compose logs -f postgres
```

Stop containers:

```bash
docker compose down
```

Stop containers and remove volumes:

```bash
docker compose down -v
```

> `docker compose down -v` deletes the PostgreSQL volume and therefore deletes local database data.

---

## 6. Useful Docker commands

List running containers:

```bash
docker ps
```

List all containers:

```bash
docker ps -a
```

Start a stopped container:

```bash
docker start <container-name>
```

Stop a container:

```bash
docker stop <container-name>
```

Open a shell inside a container:

```bash
docker exec -it <container-name> sh
```

For PostgreSQL, open `psql` directly:

```bash
docker exec -it <postgres-container> psql -U postgres -d trello
```

---

# Database Migrations

This project uses Alembic for database migrations.

## 7. Create a migration

After changing a SQLModel/database model:

```bash
alembic revision --autogenerate -m "describe your change"
```

Example:

```bash
alembic revision --autogenerate -m "add organization members"
```

Always review the generated migration before applying it.

---

## 8. Apply migrations

Apply all pending migrations:

```bash
alembic upgrade head
```

---

## 9. Check current migration

```bash
alembic current
```

Show migration history:

```bash
alembic history
```

Show migrations that would be applied:

```bash
alembic heads
```

---

## 10. Roll back the latest migration

```bash
alembic downgrade -1
```

Roll back to a specific revision:

```bash
alembic downgrade <revision>
```

---

## 11. Create an empty migration manually

When autogenerate is not appropriate:

```bash
alembic revision -m "describe your change"
```

---

# Development

## 12. Start FastAPI

Run the development server:

```bash
fastapi dev
```

If the entry point is not detected automatically:

```bash
fastapi dev main.py
```

The API will normally be available at:

```text
http://localhost:8000
```

---

## 13. API documentation

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

If the API is configured with an `/api/v1` prefix, API endpoints will look like:

```text
http://localhost:8000/api/v1/auth/login
http://localhost:8000/api/v1/auth/register
http://localhost:8000/api/v1/manifest
```

---

# Typical Development Workflow

After changing a database model:

```bash
# 1. Make sure PostgreSQL is running
docker compose up -d

# 2. Create migration
alembic revision --autogenerate -m "describe change"

# 3. Review migration

# 4. Apply migration
alembic upgrade head

# 5. Start API
fastapi dev
```

---

# Fresh Database Setup

For a completely fresh local database:

```bash
docker compose down -v
docker compose up -d
alembic upgrade head
fastapi dev
```

> Warning: `docker compose down -v` removes the database volume and all local database data.

---

# Git

Check status:

```bash
git status
```

Stage changes:

```bash
git add .
```

Commit:

```bash
git commit -m "your commit message"
```

Push:

```bash
git push
```

Make sure generated Python cache files and environment files are ignored:

```gitignore
.venv/
__pycache__/
*.py[cod]
.env
```

---

# Authentication Flow

The current authentication flow is:

```text
Register
   ↓
Verification Email
   ↓
Verify Email
   ↓
Access + Refresh Tokens
   ↓
GET /manifest
   ↓
Check onboarding state
   ↓
Pending invitation?
   ├── Yes → Accept invitation
   └── No  → Create organization if required
   ↓
Dashboard
```

Refresh tokens are currently returned in the API response. Moving refresh tokens to an `HttpOnly`, `Secure` cookie can be added later as a browser-security hardening step.

---

# Organization Flow

When an organization is created:

```text
Create Organization
       ↓
Create OrganizationMember
       ↓
Creator = OWNER
       ↓
Commit transaction
```

Invitations:

```text
OWNER / ADMIN
      ↓
Create Invitation
      ↓
OrganizationInvite
      ↓
Invitation Email
      ↓
User Accepts
      ↓
OrganizationMember
```

The invited role is stored in the invitation and becomes the member's organization role after acceptance.

---

# Troubleshooting

## PostgreSQL connection error

Check that PostgreSQL is running:

```bash
docker compose ps
```

Check logs:

```bash
docker compose logs -f postgres
```

Verify `DATABASE_URL` in `.env`.

---

## Migration errors

Check the current revision:

```bash
alembic current
```

Check available migrations:

```bash
alembic history
```

If a migration was generated incorrectly, review or remove the migration file before applying it.

---

## Port already in use

Check which process is using port 8000:

```bash
lsof -i :8000
```

For PostgreSQL port 5432:

```bash
lsof -i :5432
```

---

## bcrypt / Passlib compatibility

If using Passlib 1.7.4, pin bcrypt to a compatible version:

```bash
pip install "bcrypt==4.0.1"
```

Verify:

```bash
pip show passlib bcrypt
```

Expected:

```text
passlib 1.7.4
bcrypt 4.0.1
```

---

# Quick Start

For an existing checkout where dependencies and `.env` are already configured:

```bash
# Start database
docker compose up -d

# Apply migrations
alembic upgrade head

# Start API
fastapi dev
```

Then open:

```text
http://localhost:8000/docs
```
