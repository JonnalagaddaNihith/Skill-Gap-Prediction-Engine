from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class QuestionResponse(BaseModel):
    id: int
    skill_id: str
    skill_name: str
    difficulty: str
    problem_type: str
    question_text: str
    options: Optional[str] = None
    explanation: Optional[str] = None
    hints: Optional[str] = None

    class Config:
        from_attributes = True


class TestAnswerSubmit(BaseModel):
    question_id: int
    user_answer: str
    time_taken_seconds: Optional[int] = None
    hint_used: int = 0  # Changed from hints_used to hint_used for model compatibility
    attempt_number: int = 1


class TestSubmit(BaseModel):
    time_taken_seconds: Optional[int] = None
    answers: list[TestAnswerSubmit]


class TestAttemptResponse(BaseModel):
    id: int
    test_date: datetime
    total_score: float
    total_questions: int
    correct_answers: int
    time_taken_seconds: Optional[int] = None

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    skill_id: str
    skill_name: str
    predicted_mastery: float
    gap_severity: float
    weak_difficulties: list[str]
    weak_problem_types: list[str]


class ActivityRecommendation(BaseModel):
    activity_id: str
    title: str
    type: str
    duration_min: int
    difficulty: str
    matched_skills: list[str]
    relevance_score: float


class QuestionDetail(BaseModel):
    id: int
    question_text: str
    options: Optional[str] = None
    correct_answer: str
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class AnswerDetail(BaseModel):
    question_id: int
    user_answer: str
    is_correct: int
    hint_used: int
    question: QuestionDetail

    class Config:
        from_attributes = True


class TestAttemptDetailResponse(BaseModel):
    id: int
    test_date: datetime
    total_score: float
    total_questions: int
    correct_answers: int
    time_taken_seconds: Optional[int] = None
    answers: list[AnswerDetail]

    class Config:
        from_attributes = True
