import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
import torch

# Add the skill_gap_model to path
backend_dir = Path(__file__).parent.parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from skill_gap_model.Torch_Model.load_model import load_checkpoint, load_activities
from skill_gap_model.Torch_Model.predict import identify_gaps
from skill_gap_model.Torch_Model.recommend import recommend_activities
from skill_gap_model.Torch_Model.feature_engineering import build_student_skill_features, create_mastery_labels
from app.config import get_settings

settings = get_settings()
_model = None
_meta = None
_activities = None


def load_model():
    """Load the trained model and metadata."""
    global _model, _meta, _activities

    if _model is None:
        artifact_dir = settings.ARTIFACTS_DIR_ABSOLUTE
        _model, _meta = load_checkpoint(artifact_dir=artifact_dir)
        _activities = load_activities(artifact_dir=artifact_dir)

    return _model, _meta, _activities


def get_model():
    """Get the loaded model (lazy loading)."""
    if _model is None:
        load_model()
    return _model, _meta, _activities


def predict_and_recommend(student_id: int, db):
    model, meta, activities = get_model()

    # Extract test data from database
    from app.models.test_attempt import TestAttempt, TestAnswer
    from app.models.question import Question

    attempts = db.query(TestAttempt).filter(TestAttempt.user_id == student_id).all()

    if not attempts:
        # If no attempts, return empty results
        return {
            "skill_gaps": [],
            "recommendations": []
        }

    # Build raw data dataframe
    raw_data = []
    for attempt in attempts:
        for answer in attempt.answers:
            question = db.query(Question).filter(Question.id == answer.question_id).first()
            if question:
                raw_data.append({
                    "student_id": student_id,
                    "question_id": answer.question_id,
                    "skill_id": question.skill_id,
                    "difficulty": question.difficulty,
                    "problem_type": question.problem_type,
                    "course_id": question.course_id,
                    "correct": answer.is_correct,
                    "attempt_number": answer.attempt_number if answer.attempt_number else 1,
                    "response_time": answer.time_taken_seconds if answer.time_taken_seconds else 0,
                    "hint_used": answer.hint_used if answer.hint_used else 0,
                    "timestamp": attempt.test_date
                })

    if not raw_data:
        return {
            "skill_gaps": [],
            "recommendations": []
        }

    raw_df = pd.DataFrame(raw_data)

    # Add difficulty numeric mapping
    diff_map = {"Easy": 0, "Medium": 1, "Hard": 2}
    raw_df["diff_num"] = raw_df["difficulty"].map(diff_map)

    # Create features
    feat_df = build_student_skill_features(raw_df)
    feat_df = create_mastery_labels(feat_df)

    if feat_df.empty:
        return {
            "skill_gaps": [],
            "recommendations": []
        }

    # Identify skill gaps
    gaps = identify_gaps(
        student_id=student_id,
        feat_df=feat_df,
        model=model,
        means=meta['means'],
        stds=meta['stds'],
        raw_df=raw_df,
        threshold=0.6,
        feature_cols=meta['feature_cols'],
        skill_names=meta['skill_names'],
        device=meta['device']
    )

    # Get recommendations
    recommendations = recommend_activities(
        gaps=gaps,
        activities=activities,
        skill_names=meta['skill_names'],
        top_k=5
    )

    return {
        "skill_gaps": gaps,
        "recommendations": recommendations
    }
