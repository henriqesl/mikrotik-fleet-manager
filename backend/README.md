# ARGOS Backend

**MikroTik Fleet Manager API**

Backend responsible for registering, monitoring and managing MikroTik routers through secure RouterOS API connections.

## Main Features

* Router registration and inventory
* RouterOS API-SSL connection validation
* Encrypted RouterOS credentials
* WireGuard management network restrictions
* Router status, CPU, memory and uptime collection
* Concurrent background polling
* Configurable polling interval and concurrency
* Router activation and deactivation
* Manual polling trigger
* SQLite database with Alembic migrations
* Interactive OpenAPI documentation

## Requirements

* Python 3.10 or newer
* Access to the WireGuard management network
* RouterOS API-SSL enabled on managed routers
* Trusted RouterOS certificate authority

## Development Setup

Create and activate the virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the application dependencies:

```powershell
pip install -r requirements.txt
```

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

Generate a credential encryption key:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the generated value to `.env`:

```env
CREDENTIAL_ENCRYPTION_KEY=generated-key
```

Apply the database migrations:

```powershell
python -m alembic upgrade head
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Tests

Install development dependencies:

```powershell
pip install -r requirements-dev.txt
```

Run the test suite:

```powershell
pytest
```

## RouterOS Connectivity

ARGOS is designed to reach customer routers through a private WireGuard management network.

```text
ARGOS Server
      |
      | WireGuard
      v
Central CHR
      |
      +---- Customer MikroTik 1
      +---- Customer MikroTik 2
      +---- Customer MikroTik N
```

RouterOS API services should not be exposed directly to the public internet.

## Current Status

Backend MVP completed.

Authentication, role-based access control, historical metrics, alerts and production deployment hardening will be implemented in later stages.
