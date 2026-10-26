from pydantic import BaseModel
from typing import List


class SkillGap(BaseModel):
    skill_id: str
    skill_name: str
    predicted_mastery: float
    gap_severity: float
    observed_accuracy: float | None = None
    n_attempts: int | None = None
    hint_rate: float | None = None
    weak_difficulties: List[str]
    weak_problem_types: List[str]


class ActivityRecommendation(BaseModel):
    activity_id: str
    title: str
    type: str
    duration_min: int
    difficulty: str
    matched_skills: List[str]
    relevance_score: float
    base_skill_score: float
    difficulty_bonus: float
    problem_type_bonus: float


class PredictionResponse(BaseModel):
    skill_gaps: List[SkillGap]
    recommendations: List[ActivityRecommendation]
