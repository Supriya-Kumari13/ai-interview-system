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
- Install dependencies from `requirements.txt`

From the project root, install the dependencies with:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
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

### 3. Configure Gemini

Copy `.env.example` to `.env` and replace `add_your_key_here` with a Gemini API key. Keep `.env` private; it is ignored by Git. Do not paste the key into chat or commit it.

Answer evaluation sends the interview question, reference answer, and candidate answer to Gemini for processing. The request opts out of Gemini server-side interaction storage.

## Run the Backend

From the project root:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Default backend URLs:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Evaluate an Answer

1. Submit an answer using `POST /answers`.
2. Use the returned answer ID with `POST /answers/{answer_id}/evaluate`.
3. The response includes five rubric scores (0-5), an overall score (0-100), feedback, strengths, and improvement suggestions. The evaluation is saved in SQLite.

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
