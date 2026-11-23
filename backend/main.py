from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.models.questions import Base, Question
from database.database import engine, get_db
from backend.models.interview import Answer, AnswerAssessment, InterviewSession
from backend.services.answer_evaluator import (
    EvaluationConfigurationError,
    EvaluationProviderError,
    evaluate_answer,
)

app = FastAPI(title="AI Interview System API")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionCreate(BaseModel):
    question: str = Field(min_length=1)
    skill: str = Field(min_length=1)
    difficulty: str = Field(pattern="^(Easy|Medium|Hard)$")
    competency: str = Field(min_length=1)
    role: str = Field(min_length=1)
    reference_answer: str = Field(min_length=1)


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    skill: str
    difficulty: str
    competency: str | None
    role: str | None
    reference_answer: str | None

class InterviewCreate(BaseModel):
    role: str = Field(min_length=1)
    skill: str = Field(min_length=1)


class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    skill: str

class AnswerCreate(BaseModel):
    interview_id: int = Field(gt=0)
    question_id: int = Field(gt=0)
    answer_text: str = Field(min_length=1)


class AnswerEvaluationResponse(BaseModel):
    answer_id: int
    overall_score: int = Field(ge=0, le=100)
    correctness_score: int = Field(ge=0, le=5)
    completeness_score: int = Field(ge=0, le=5)
    relevance_score: int = Field(ge=0, le=5)
    clarity_score: int = Field(ge=0, le=5)
    technical_terminology_score: int = Field(ge=0, le=5)
    feedback: str
    strengths: list[str]
    improvements: list[str]


@app.get("/")
def root():
    return {"message": "AI Interview System API is running"}


@app.get("/questions", response_model=list[QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    return db.query(Question).all()


@app.post(
    "/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    question = Question(
        question=payload.question.strip(),
        skill=payload.skill.strip(),
        difficulty=payload.difficulty,
        competency=payload.competency.strip(),
        role=payload.role.strip(),
        reference_answer=payload.reference_answer.strip()
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@app.post(
    "/interviews",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview(payload: InterviewCreate, db: Session = Depends(get_db)):
    interview = InterviewSession(
        role=payload.role.strip(),
        skill=payload.skill.strip(),
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@app.get(
    "/interviews/{interview_id}/question",
    response_model=QuestionResponse,
)
def get_interview_question(
    interview_id: int,
    db: Session = Depends(get_db),
):
    interview = db.query(InterviewSession).filter(
        InterviewSession.id == interview_id
    ).first()

    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")

    question = db.query(Question).filter(
        Question.role == interview.role,
        Question.skill == interview.skill,
    ).order_by(Question.id).first()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="No questions found for this interview",
        )

    return question

@app.post("/answers", status_code=status.HTTP_201_CREATED)
def submit_answer(payload: AnswerCreate, db: Session = Depends(get_db)):
    interview = db.query(InterviewSession).filter(
        InterviewSession.id == payload.interview_id
    ).first()

    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")

    question = db.query(Question).filter(
        Question.id == payload.question_id,
        Question.role == interview.role,
        Question.skill == interview.skill,
    ).first()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found for this interview",
        )

    answer_text = payload.answer_text.strip()
    if not answer_text:
        raise HTTPException(status_code=422, detail="Answer cannot be blank")

    answer = Answer(
        interview_id=payload.interview_id,
        question_id=payload.question_id,
        answer_text=answer_text,
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    return {
        "id": answer.id,
        "interview_id": answer.interview_id,
        "question_id": answer.question_id,
        "answer_text": answer.answer_text,
    }


@app.post(
    "/answers/{answer_id}/evaluate",
    response_model=AnswerEvaluationResponse,
)
def evaluate_saved_answer(answer_id: int, db: Session = Depends(get_db)):
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")

    question = db.query(Question).filter(Question.id == answer.question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    try:
        result = evaluate_answer(
            question=question.question,
            competency=question.competency,
            reference_answer=question.reference_answer,
            candidate_answer=answer.answer_text,
        )
    except EvaluationConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EvaluationProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    evaluation = result.as_result()
    assessment = (
        db.query(AnswerAssessment)
        .filter(AnswerAssessment.answer_id == answer.id)
        .first()
    )
    if assessment is None:
        assessment = AnswerAssessment(
            answer_id=answer.id,
            evaluation=evaluation,
        )
        db.add(assessment)
    else:
        assessment.evaluation = evaluation

    db.commit()
    return {"answer_id": answer.id, **evaluation}