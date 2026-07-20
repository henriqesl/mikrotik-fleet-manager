# ARGOS

**MikroTik Fleet Manager**

ARGOS is a centralized platform for registering, monitoring and managing MikroTik router fleets through a private WireGuard management network.

The project combines a FastAPI backend, a React dashboard and secure RouterOS API-SSL communication.

## Overview

ARGOS was designed to monitor MikroTik devices that may be distributed across different customer networks without exposing their management interfaces directly to the public internet.

The application server reaches the routers through WireGuard tunnels, using a central MikroTik CHR as the VPN hub.

```text
ARGOS
├── React Dashboard
├── FastAPI API
└── Background Polling Worker
          |
          | WireGuard
          v
     Central MikroTik CHR
          |
          ├── Customer MikroTik 1
          ├── Customer MikroTik 2
          └── Customer MikroTik N
```

## Current Features

### Backend

* Router inventory and registration
* Secure RouterOS API-SSL validation
* Encrypted RouterOS credentials
* Private management network restrictions
* Configurable RouterOS API port allowlist
* Background router polling
* Concurrent RouterOS checks
* Configurable polling interval and concurrency
* CPU, memory, uptime and RouterOS information collection
* Online, offline and error status tracking
* Manual polling trigger
* Polling worker runtime status
* Logical router deactivation
* SQLite database
* Alembic database migrations
* Unit tests for critical components
* Interactive OpenAPI documentation

### Frontend

* React application created with Vite
* Tailwind CSS interface
* Dark operations dashboard
* Sidebar and application header
* Fleet statistics cards
* Router table foundation
* Responsive initial layout

The frontend is currently being connected to the live ARGOS API.

## Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic
* SQLite
* Cryptography/Fernet
* RouterOS API
* Pytest

### Frontend

* React
* Vite
* Tailwind CSS
* Lucide React

### Network Infrastructure

* MikroTik RouterOS
* MikroTik CHR
* WireGuard
* RouterOS API-SSL

## Repository Structure

```text
argos-network-manager/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── workers/
│   ├── certs/
│   ├── tests/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
└── README.md
```

## Backend Development

See the backend documentation for environment configuration, database migrations, tests and API execution:

```text
backend/README.md
```

Basic startup:

```powershell
cd backend

py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Frontend Development

```powershell
cd frontend
npm install
npm run dev
```

The development interface will normally be available at:

```text
http://localhost:5173
```

## Security Model

ARGOS follows these initial security principles:

* Router management addresses must belong to configured private networks.
* RouterOS communication uses API-SSL.
* Router certificates must be validated through a trusted certificate authority.
* Router passwords are encrypted before being stored.
* Credentials are never returned to the frontend.
* Router management services should not be exposed directly to the public internet.
* RouterOS users should be unique and restricted to the permissions required by ARGOS.
* Certificate private keys must never be committed to the repository.

Authentication, multi-factor authentication, role-based access control and audit logs are planned before public production exposure.

## API Overview

```text
GET    /
GET    /health

GET    /api/routers
POST   /api/routers
GET    /api/routers/{router_id}
PATCH  /api/routers/{router_id}
DELETE /api/routers/{router_id}

GET    /api/monitoring/status
POST   /api/monitoring/poll
```

## Project Status

### Completed

* Backend MVP
* Router CRUD
* Encrypted credential storage
* RouterOS API-SSL integration
* Background polling worker
* Monitoring endpoints
* Backend test suite
* Initial frontend foundation

### In Progress

* Frontend API integration
* Live router table
* Router registration interface
* Router detail view
* Router management actions

### Planned

* Authentication
* Multi-factor authentication
* Role-based access control
* Audit logs
* Historical metrics
* Alerts and notifications
* PostgreSQL migration
* Production deployment
* Production security hardening

## Disclaimer

ARGOS is currently under active development. The current version should be used only in controlled development or private network environments.
