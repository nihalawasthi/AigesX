# AigesX

This repository is consolidated into two top-level parts:

- Backend: Django API + integrated scan engine modules
- Frontend: React web app

## Project Structure

```text
AigesX/
	Backend/
		backend/         # Django API + apps (web entry point)
		  scan_engine/   # Integrated scan engine package (analysis/core/models/cve data)
		  scripts/       # Utility scripts (including API smoke test)
	Frontend/
		app/       # React + Vite frontend
```

## Runtime Flow

The application now runs as a web app:

- Frontend calls backend APIs.
- Backend triggers scans through internal `scan_engine` integration.
- No external report upload flow is used.

## Quick Start

### Backend API (Django)

```bash
cd Backend
python manage.py runserver
```

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

## Main Report APIs

- POST /api/scan/
- GET /api/latest-report/

## API Smoke Test

```bash
cd Backend/backend
python scripts/smoke_test_api.py --username <your_username> --password <your_password>
```

Optional flags:

- --base-url http://127.0.0.1:8000
- --timeout 300
