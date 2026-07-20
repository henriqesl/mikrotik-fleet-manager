# ARGOS Frontend

React dashboard for the ARGOS MikroTik Fleet Manager.

## Features

* Fleet statistics
* Router table and search
* Router registration
* Router detail panel
* Router editing
* Manual polling
* Router deactivation
* Responsive navigation
* Loading and error states

## Setup

Install dependencies:

```powershell
npm install
```

Create the local environment:

```powershell
Copy-Item .env.example .env.local
```

Configure the backend:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

Start the development server:

```powershell
npm run dev
```

## Build

```powershell
npm run lint
npm run build
```

The production files will be generated inside:

```text
dist/
```

Never place credentials or private keys in frontend environment variables.
