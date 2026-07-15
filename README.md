# ARGOS

**MikroTik Fleet Manager**

A scalable platform for monitoring and managing MikroTik router fleets.

## Project Structure

```text
mikrotik-fleet-manager/
├── backend/
├── frontend/
├── .gitignore
└── README.md
```

## Planned Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* RouterOS API

### Frontend

* React
* Vite
* Tailwind CSS
* Lucide React

## Architecture

The frontend communicates only with the FastAPI backend.

The backend is responsible for periodically connecting to MikroTik routers, collecting monitoring data and storing the latest state in the database.

```text
React Frontend
      |
      | HTTP
      v
FastAPI Backend
      |
      +---- Database
      |
      +---- MikroTik RouterOS API
```

## Planned Features

* Fleet overview dashboard
* Online and offline router monitoring
* CPU and memory usage indicators
* Router registration and management
* Router detail view
* Search and filtering
* Automatic background data collection
* Support for multiple MikroTik routers

## Project Status

Project under initial development.
