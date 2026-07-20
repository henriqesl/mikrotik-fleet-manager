# ARGOS

**MikroTik Fleet Manager**

ARGOS is a web application for registering and monitoring MikroTik routers through a private WireGuard management network.

The project combines a FastAPI backend, an automatic polling worker and a React dashboard.

## Features

* Router inventory
* RouterOS API-SSL connection validation
* Encrypted RouterOS credentials
* Automatic router polling
* Online, offline and error status
* CPU, memory and uptime monitoring
* Router registration and editing
* Manual polling
* Logical router deactivation
* Responsive dashboard

## Architecture

```text
React Dashboard
       |
       v
FastAPI Backend
       |
       ├── SQLite
       └── Polling Worker
                |
                | WireGuard
                v
         MikroTik CHR
                |
                └── Managed MikroTik Routers
```

Router management services are reached through private WireGuard addresses and should not be exposed directly to the public internet.

## Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* SQLite
* Pydantic
* Pytest
* RouterOS API

### Frontend

* React
* Vite
* Tailwind CSS
* Lucide React

### Network

* MikroTik RouterOS
* MikroTik CHR
* WireGuard
* RouterOS API-SSL

## Project Structure

```text
argos-network-manager/
├── backend/
├── frontend/
└── README.md
```

## Running the Project

### Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Tests

Backend:

```powershell
cd backend
python -m pytest
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

## Current Status

* Backend MVP completed
* Frontend MVP completed
* Authentication and production deployment pending

ARGOS is currently intended for development and private network environments.
