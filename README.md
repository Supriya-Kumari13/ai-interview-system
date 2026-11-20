# AI Interview System

AI Interview System is an AI-based application being developed to automate and improve interview preparation and practice.

## Project Structure

```text
ai-interview-system/
├── backend/       # FastAPI backend
├── frontend/      # Frontend application
├── database/      # Database files and migrations
├── venv/          # Local Python virtual environment
└── README.md
```

## Backend

The backend is built with FastAPI and Uvicorn. The current API root endpoint is available:

- `GET /` - Returns the API status message
- API documentation: `http://127.0.0.1:8000/docs`

## Requirements

- Python 3.10 or later
- FastAPI
- Uvicorn

The dependencies may already be installed in the project. For a new environment, install them with:

```powershell
pip install fastapi uvicorn
```

## Setup and Installation

### 1. Navigate to the project folder

```powershell
cd "C:\Users\Hp pc\Documents\ai-interview-system"
```

### 2. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

If you encounter a PowerShell execution policy issue, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install the backend dependencies

```powershell
pip install fastapi uvicorn
```

## Run the Backend

From the project root:

```powershell
uvicorn backend.main:app --reload
```

Default backend URLs:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Development Status

The basic FastAPI backend setup is complete. Frontend development, database integration, and AI interview features are currently in progress.

## Planned Features

- AI-generated interview questions
- Interviews based on resumes and job descriptions
- Text or voice-based answers
- Candidate performance feedback
- Interview scoring and analytics
- User authentication
- Interview history and reporting
