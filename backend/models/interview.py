from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Text
from backend.models.questions import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)
    skill = Column(String, nullable=False)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    interview_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)


class AnswerAssessment(Base):
    __tablename__ = "answer_assessments"

    id = Column(Integer, primary_key=True)
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=False, unique=True)
    evaluation = Column(JSON, nullable=False)