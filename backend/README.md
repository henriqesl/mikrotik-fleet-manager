# ARGOS Backend

FastAPI backend responsible for router registration, monitoring and persistence.

## Main Features

* Router CRUD
* RouterOS API-SSL validation
* Encrypted credentials
* Management network restrictions
* Automatic and manual polling
* CPU, memory and uptime collection
* SQLite database
* Alembic migrations
* Unit tests

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Generate the credential encryption key:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add it to `.env`:

```env
CREDENTIAL_ENCRYPTION_KEY=your-generated-key
```

Apply migrations:

```powershell
python -m alembic upgrade head
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

## Main Environment Variables

```env
DATABASE_URL=sqlite+aiosqlite:///./argos.db

CREDENTIAL_ENCRYPTION_KEY=your-generated-key

MANAGEMENT_NETWORKS=10.200.0.0/24
ALLOWED_ROUTER_API_PORTS=8729

ROUTEROS_CA_FILE=certs/routeros-ca.pem

POLLING_ENABLED=true
POLL_INTERVAL_SECONDS=60
MAX_CONCURRENT_ROUTER_CHECKS=10
```

Adjust the network values according to the WireGuard deployment.

## RouterOS Certificate

Place the trusted public CA certificate at:

```text
certs/routeros-ca.pem
```

Do not commit private keys, passwords or `.env` files.

When connecting through an IP address, the router certificate should include that management IP in its Subject Alternative Name.

## Tests

```powershell
python -m pytest
```

## Development Notes

The FastAPI API and polling worker currently run in the same process.

Use only one Uvicorn worker during the MVP to avoid running duplicate polling workers.

Authentication, RBAC, audit logs and production hardening are not included yet.
