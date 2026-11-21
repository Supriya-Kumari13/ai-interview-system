from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine
from backend.models.questions import Base

app = FastAPI(title="AI Interview System API")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "AI Interview System API is running"}


@app.get("/questions")
def get_questions():
    # Placeholder for fetching questions from a database or other source
    questions = [
        {"id": 1, "question": "What is oops?"},
        {"id": 2, "question": "What is your greatest weakness?"},
        {"id": 3, "question": "Why do you want to work here?"},
    ]
    return {"questions": questions}