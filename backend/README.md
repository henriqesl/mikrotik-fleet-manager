# ARGOS Backend

FastAPI backend responsible for managing, monitoring and communicating with MikroTik routers.

## Responsibilities

* Manage registered MikroTik routers
* Communicate with devices through the RouterOS API
* Collect router information and monitoring metrics
* Store router data in a local database
* Provide REST API endpoints to the frontend
* Run periodic background monitoring tasks
* Handle connection failures and offline devices

## Planned Technologies

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* RouterOS API
* AsyncIO

## Planned Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes/
│   ├── services/
│   └── workers/
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## Environment Variables

The real environment variables will be stored in:

```text
backend/.env
```

This file must not be committed to Git.

An example configuration will be available in:

```text
backend/.env.example
```

## Project Status

The backend implementation will be added in the next development steps.
