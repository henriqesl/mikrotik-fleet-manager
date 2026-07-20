# ARGOS Backend

**MikroTik Fleet Manager API**

The ARGOS backend provides the API, persistence, security controls and background worker responsible for monitoring MikroTik router fleets.

## Responsibilities

The backend currently handles:

* Router registration
* Router inventory
* RouterOS API-SSL connection validation
* Credential encryption
* Management network validation
* Router status collection
* CPU and memory monitoring
* RouterOS version and device information collection
* Automatic background polling
* Manual polling execution
* Polling worker runtime status
* Router activation and deactivation
* Database migrations
* API documentation
* Unit tests

## Architecture

```text
React Frontend
      |
      | HTTP
      v
FastAPI Backend
      |
      ├── REST API
      ├── SQLAlchemy
      ├── SQLite
      └── Polling Worker
              |
              | RouterOS API-SSL
              | over WireGuard
              v
         MikroTik CHR
              |
              ├── Router 1
              ├── Router 2
              └── Router N
```

The FastAPI API and polling worker currently run inside the same application process.

For the MVP, the application should run with a single Uvicorn worker to prevent multiple background polling workers from running simultaneously.

## Requirements

* Python
* Access to the configured WireGuard management network
* RouterOS API-SSL enabled on managed routers
* Trusted RouterOS certificate authority
* MikroTik credentials with restricted permissions

## Development Setup

Enter the backend directory:

```powershell
cd backend
```

Create the virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install application and development dependencies:

```powershell
pip install -r requirements-dev.txt
```

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

## Credential Encryption Key

Generate a Fernet encryption key:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the generated value to `.env`:

```env
CREDENTIAL_ENCRYPTION_KEY=your-generated-key
```

Do not change this key after routers have already been registered. Changing it would prevent ARGOS from decrypting previously stored credentials.

Never commit the encryption key.

## RouterOS Certificate Authority

ARGOS validates the certificates presented by MikroTik routers.

The public certificate authority file can be placed at:

```text
backend/certs/routeros-ca.pem
```

Environment configuration:

```env
ROUTEROS_CA_FILE=certs/routeros-ca.pem
```

Only the public CA certificate should be placed there.

Never commit:

* Private keys
* Router certificates containing private keys
* Environment files
* Credentials

When ARGOS connects to a router by its WireGuard IP address, the router certificate should contain that IP address in its Subject Alternative Name.

## Important Environment Variables

Example configuration:

```env
ENVIRONMENT=development
DEBUG=true

DATABASE_URL=sqlite+aiosqlite:///./argos.db

CREDENTIAL_ENCRYPTION_KEY=your-generated-key

MANAGEMENT_NETWORKS=10.200.0.0/24
ALLOWED_ROUTER_API_PORTS=8729

ROUTEROS_CA_FILE=certs/routeros-ca.pem
ROUTEROS_SOCKET_TIMEOUT_SECONDS=10

POLLING_ENABLED=true
POLL_INTERVAL_SECONDS=60
MAX_CONCURRENT_ROUTER_CHECKS=10

LOG_LEVEL=INFO
```

Adjust the management network according to the WireGuard addressing used in the deployment.

## Database Migrations

Apply all migrations:

```powershell
python -m alembic upgrade head
```

View the current migration:

```powershell
python -m alembic current
```

View migration history:

```powershell
python -m alembic history
```

## Running the API

Start the development server:

```powershell
python -m uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Available Endpoints

### General

```http
GET /
```

Returns the application name and version.

```http
GET /health
```

Checks the API and database status.

### Routers

```http
GET /api/routers
```

Returns a paginated router list.

```http
POST /api/routers
```

Validates the RouterOS API-SSL connection and registers a router.

```http
GET /api/routers/{router_id}
```

Returns one router.

```http
PATCH /api/routers/{router_id}
```

Updates safe router properties.

```http
DELETE /api/routers/{router_id}
```

Performs logical deactivation.

### Monitoring

```http
GET /api/monitoring/status
```

Returns:

* Whether the worker is running
* Whether a polling cycle is in progress
* Configured polling interval
* Last cycle timestamps
* Last polling summary
* Last worker error

```http
POST /api/monitoring/poll
```

Starts a manual polling cycle.

The endpoint returns HTTP `409 Conflict` when another cycle is already in progress.

## Background Polling

When polling is enabled, the worker:

1. Loads all active routers.
2. Closes the initial database session.
3. Decrypts credentials only when required.
4. Checks routers concurrently.
5. Limits simultaneous RouterOS connections.
6. Stores the results sequentially.
7. Updates status and metrics in a single database transaction.
8. Waits for the configured interval.
9. Starts the next cycle.

The worker does not intentionally overlap polling cycles.

Possible router states:

```text
online
offline
error
unknown
```

Examples:

* `online`: RouterOS responded and metrics were collected.
* `offline`: Network connection to the router failed.
* `error`: Configuration, certificate, credential or RouterOS data error.
* `unknown`: No successful polling state is currently available.

## Collected Information

Depending on RouterOS availability, ARGOS collects:

* Router identity
* Hardware model
* RouterOS version
* CPU usage
* Memory usage
* Uptime
* Last checked timestamp
* Last successful contact
* Last polling error

## Tests

Run the test suite:

```powershell
python -m pytest
```

The current tests cover:

* Credential encryption and decryption
* Invalid encrypted values
* Management network restrictions
* RouterOS API port restrictions
* RouterOS uptime parsing
* Memory usage calculation
* Polling summaries
* Router schema validation
* Password protection in object representations

## Development Notes

### SQLite

SQLite is sufficient for the current MVP.

Because SQLite has limited concurrent write support, router network checks run concurrently, but polling results are persisted sequentially.

A future production version may migrate to PostgreSQL.

### Uvicorn Workers

The background polling worker currently starts through the FastAPI lifespan.

Do not start the application with multiple Uvicorn workers during the MVP, because each process could start its own polling worker.

### Polling Without Certificates

When the RouterOS certificate authority is not configured, the application should continue running, but router checks will be recorded as errors.

For frontend-only development, polling may be disabled:

```env
POLLING_ENABLED=false
```

## Security Considerations

* Do not expose RouterOS API ports publicly.
* Restrict router access to the WireGuard management network.
* Use RouterOS API-SSL.
* Validate router certificates.
* Use a private certificate authority controlled by the organization.
* Create a dedicated RouterOS user for ARGOS.
* Give that user only the permissions required by the application.
* Never return router passwords through API responses.
* Never commit `.env`, credentials, private keys or production certificates.

Authentication, MFA, RBAC and audit logging are not part of the current backend MVP and must be implemented before public production use.

## Current Status

Backend MVP completed.

The next development stages include:

* Frontend integration
* Authentication
* Role-based access control
* Historical metrics
* Alerts
* PostgreSQL support
* Deployment automation
* Production hardening
