# Implementation Reference (Hinglish)

This document records the backend features implemented so far and the steps to try them. It is a reference for the current prototype, not a description of unfinished features.

## Current user flow

The backend supports this sequence:

1. Add an interview question to the question bank.
2. Start an interview session by role and skill.
3. Fetch a question matching that role and skill.
4. Save the candidate's answer.
5. Ask Gemini to evaluate the saved answer and store the evaluation.

## Files and responsibilities

- [`backend/main.py`](../backend/main.py) — FastAPI request schemas and API endpoints.
- [`backend/models/questions.py`](../backend/models/questions.py) — shared SQLAlchemy `Base` and `Question` model.
- [`backend/models/interview.py`](../backend/models/interview.py) — interview sessions, answers, and saved assessments.
- [`backend/services/answer_evaluator.py`](../backend/services/answer_evaluator.py) — Gemini request, rubric, and structured evaluation validation.
- [`database/database.py`](../database/database.py) — SQLite engine and database-session dependency.
- [`requirements.txt`](../requirements.txt) — Python dependencies, including the Gemini SDK.
- [`.env.example`](../.env.example) — template for local Gemini configuration. Copy this to `.env` and add a real key locally.
- [`tests/test_answer_evaluator.py`](../tests/test_answer_evaluator.py) — tests for score validation, score calculation, missing key handling, and mocked Gemini output.

## Database tables

### `questions`

Stores:

- `question`
- `skill`
- `difficulty` (`Easy`, `Medium`, or `Hard`)
- `competency`
- `role`
- `reference_answer`

Older question rows can have `NULL` for `competency`, `role`, and `reference_answer`; API responses allow this for compatibility.

### `interview_sessions`

Stores an automatically generated interview ID, selected `role`, and `skill`.

### `answers`

Stores the answer text and links it to an interview session and question.

### `answer_assessments`

Stores one Gemini evaluation per answer as JSON. Re-evaluating an answer updates its saved assessment.

## API reference and Swagger test flow

Open `http://127.0.0.1:8000/docs`. Use the IDs returned by the API; IDs may differ between databases.

### 1. Add a question — `POST /questions`

Example request:

```json
{
  "question": "What is polymorphism in Java?",
  "skill": "Java",
  "difficulty": "Easy",
  "competency": "Polymorphism",
  "role": "Java Interview",
  "reference_answer": "Polymorphism allows an object to take different forms, such as method overloading and overriding."
}
```

Expected status: `201 Created`.

`GET /questions` lists the saved questions. Swagger's `"string"` values in the schema are placeholders, not actual database values.

### 2. Start an interview — `POST /interviews`

```json
{
  "role": "Java Interview",
  "skill": "Java"
}
```

Expected status: `201 Created`. Save the returned `id`; the frontend should keep and reuse this ID automatically.

### 3. Fetch a matching question — `GET /interviews/{interview_id}/question`

Example: `GET /interviews/1/question`.

The endpoint finds the interview and returns the first question matching both its `role` and `skill`. The role and skill must match the question record. If the interview or matching question does not exist, the API returns `404`.

### 4. Save the candidate answer — `POST /answers`

Use the actual interview and question IDs from earlier responses:

```json
{
  "interview_id": 1,
  "question_id": 4,
  "answer_text": "One interface can have many implementations."
}
```

Expected status: `201 Created`. The response contains the new answer `id`. At this stage the answer is stored, but not evaluated.

### 5. Evaluate the saved answer — `POST /answers/{answer_id}/evaluate`

Example: `POST /answers/1/evaluate`.

No request body is needed. The endpoint loads the saved answer and its question, sends the question, competency, reference answer, and candidate answer to Gemini, then stores and returns the evaluation.

The response contains:

- Five rubric scores, each from `0` to `5`: correctness, completeness, relevance, clarity, and technical terminology.
- `overall_score` from `0` to `100`, calculated as the sum of the five scores multiplied by four.
- Written feedback, strengths, and suggested improvements.

## Gemini setup and privacy

1. From the project root, copy `.env.example` to `.env`:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Put the Gemini API key in `.env` as the value of `GEMINI_API_KEY`. Keep the key private. `.env` is ignored by Git; never commit it or paste the key into chat.
3. The default model is `gemini-4-hydrogen`. `GEMINI_MODEL` in `.env` can be changed to another model available to your Gemini API key.
4. Restart the backend after editing `.env`.

The evaluation request uses `store=False` to opt out of Gemini server-side interaction storage. The question, reference answer, and candidate answer are still sent to Google for model processing.

If `GEMINI_API_KEY` is missing, evaluation returns `503`. If Gemini cannot complete the request or returns invalid data, evaluation returns `502`. The already-saved answer remains in the database so evaluation can be retried.

## Install, run, and test

From the project root:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Run the local evaluator tests in another terminal:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

The automated tests use a mocked Gemini response; they do not require or verify a live API key.

## Current limitations / not implemented yet

- No frontend: Swagger is currently used to test the flow.
- Question fetching is a first matching question by ID order; it does not yet track questions already asked or adapt difficulty.
- Gemini scores and feedback are a prototype rubric, not a calibrated hiring decision. Review evaluation quality with human-labelled examples.
- No resume/job-description analysis, voice input, authentication, user dashboard, or participant study yet.
- This prototype has no production database migration framework. Adding columns to an existing SQLite table requires a migration; `create_all()` creates missing tables but does not add columns to an existing table.
