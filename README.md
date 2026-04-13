# Cinema Ticket Service

RESTful API for cinema ticket management — built with FastAPI + PostgreSQL + Docker.

## Instruction to start
### Step 1 — create .env from .env.example:
Open .env and set variables:

### **Environment variables**

| Variable | Default                                                                | Description                        |
|----------|------------------------------------------------------------------------|------------------------------------|
| `POSTGRES_DB` | `cinema`                                                               | Database name                      |
| `POSTGRES_USER` | `cinema`                                                               | DB username                        |
| `POSTGRES_PASSWORD` | —                                                                      | DB password                        |
| `SECRET_KEY` | —                                                                      | App secret (change in prod)        |
| `SESSION_TTL_HOURS` | `24`                                                                   | Session lifetime                   |
| `APP_BASE_URL` | `http://localhost:8000`                                                | Used in verification links         |
|`DATABASE_URL`| postgresql+asyncpg://cinema:password@127.0.0.1:5433/cinema?ssl=disable | For running the app outside Docker |

### Step 2 — start:
```bash
    docker compose up --build -d
```
### Step 3 — chek:
```bash
    docker compose ps
```
>db and app must be healthy/running

```bash
    curl http://localhost:8000/health
```
>{"status":"ok"}

### Step 4 — open Swagger:
http://localhost:8000/docs
Stop:
```bash
    docker compose down
```

## Make an admin user

The admin role is assigned manually in the database or prepared before start docker in `002_schema.sql` :
```bash
    docker compose exec db psql -U cinema -d cinema -c \
    "UPDATE users SET role = 'admin' WHERE email = 'your@email.com';"
    
    # Update password hash (if necessary)
    docker compose exec app python -c "from auth.security import hash_password; print(hash_password('YourPassword1'))"
```

## API overview

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/auth/register` | — | Register a viewer account |
| POST | `/auth/login` | — | Login, receive Bearer token |
| POST | `/auth/logout` | Bearer | Invalidate session |
| GET | `/auth/me` | Bearer | Current user profile |
| GET | `/tickets/sessions` | — | List all screenings |
| GET | `/tickets/sessions/{id}/seats` | — | Available seats |
| POST | `/tickets/buy` | viewer | Buy/reserve a ticket |
| GET | `/tickets/my` | viewer | My tickets |
| GET | `/reports/sales?date_from=&date_to=` | admin | Download sales CSV |

## Room types

| Type | Booking | seat_id |
|------|---------|---------|
| `fixed` | Specific numbered seat | Required |
| `open` | Any spot up to capacity | Must be omitted |

## Project structure

```
.
├── auth/                    # Authentication module
│   ├── config.py
│   ├── dependencies.py
│   ├── models.py
│   ├── router.py
│   ├── schemas.py
│   ├── security.py
│   └── service.py
│
├── migrations/              # SQL migrations
│   ├── 001_create_users.sql
│   ├── 002_create_movies.sql
│   ├── 003_create_rooms.sql
│   ├── 004_create_sessions.sql
│   ├── 005_create_tickets.sql
│   ├── 006_create_sales_view.sql
│   └── 007_seed_data.sql
│   
├── reports/                 # Sales reports module
│   ├── router.py
│   └── service.py
│
├── tickets/                 # Ticket purchase module
│   ├── models.py
│   ├── router.py
│   ├── schemas.py
│   └── service.py
│
├── .env
├── docker-compose.yml
├── Dockerfile
├── main.py                  # FastAPI app
├── Makefile
├── README.md               
└── requirements.txt
 
```

# Tech Stack

## Language

| Link | Description |
|------|-------------|
| ![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python) | **Python 3.12** — language of choice |
| ![asyncio](https://img.shields.io/badge/asyncio-built--in-lightgrey) | **asyncio** — asynchronous execution model (non-blocking I/O) |

## Web Framework and Services

| Link | Description |
|------|-------------|
| ![FastAPI](https://img.shields.io/badge/FastAPI-%3E%3D0.111-009688?logo=fastapi) | **[FastAPI](https://fastapi.tiangolo.com/)** — REST API implementation, automatic OpenAPI/Swagger generation |
| ![Uvicorn](https://img.shields.io/badge/Uvicorn-%3E%3D0.29-222222) | **[Uvicorn](https://www.uvicorn.org/)** — ASGI server for running the application |
| ![Pydantic](https://img.shields.io/badge/Pydantic-%3E%3D2.7-E92063) | **[Pydantic v2](https://docs.pydantic.dev/)** — data validation and schema description |

## Database

| Link | Description |
|------|-------------|
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql) | **[PostgreSQL 16](https://www.postgresql.org/)** — the main DBMS (ENUM, UUID, integrity constraints) |
| ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-%3E%3D2.0-red) | **[SQLAlchemy 2.0](https://www.sqlalchemy.org/)** — async ORM (models, sessions, queries) |
| ![asyncpg](https://img.shields.io/badge/asyncpg-%3E%3D0.29-green) | **[asyncpg](https://magicstack.github.io/asyncpg/)** — PostgreSQL asynchronous driver |

## Security and Authentication

| Link | Description |
|------|-------------|
| ![passlib](https://img.shields.io/badge/passlib-%3E%3D1.7-blue) ![bcrypt](https://img.shields.io/badge/bcrypt-secure-green) | **passlib + bcrypt** — password hashing |
| ![secrets](https://img.shields.io/badge/secrets-built--in-lightgrey) | **secrets** — generating cryptographically strong tokens |
| ![Session](https://img.shields.io/badge/Session-custom-orange) | **Session tokens (custom)** — storing tokens in the database (JWT alternative, simplified invalidation) |

## DevOps

| Link | Description |
|------|-------------|
| ![Docker](https://img.shields.io/badge/Docker-containerized-2496ED?logo=docker) | **[Docker](https://www.docker.com/)** — application containerization (multi-stage build) |
| ![Docker Compose](https://img.shields.io/badge/Docker--Compose-orchestration-1488C6?logo=docker) | **[Docker Compose](https://docs.docker.com/compose/)** — service orchestration (application, database, mail) |


