import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the skill_gap_model to path
backend_dir = Path(__file__).parent.parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from skill_gap_model.Torch_Model.feature_engineering import build_student_skill_features, create_mastery_labels
from skill_gap_model.Torch_Model.train_test import train_model
from app.db.database import SessionLocal
from app.models.test_attempt import TestAttempt, TestAnswer
from app.models.question import Question
from app.config import get_settings

settings = get_settings()


def extract_data_from_db(db: Session, min_samples: int = 100) -> pd.DataFrame | None:
    # Get all test attempts with answers
    attempts = db.query(TestAttempt).all()

    if len(attempts) < min_samples:
        print(f"Insufficient data for retraining: {len(attempts)} attempts (need at least {min_samples})")
        return None

    # Build raw data dataframe
    raw_data = []

    for attempt in attempts:
        for answer in attempt.answers:
            question = db.query(Question).filter(Question.id == answer.question_id).first()
            if question:
                raw_data.append({
                    "student_id": attempt.user_id,
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
        print("No raw data extracted from database")
        return None

    df = pd.DataFrame(raw_data)
    print(f"Extracted {len(df)} raw data points from database")
    return df


def retrain_model():
    print(f"Starting model retraining at {datetime.now()}")

    db = SessionLocal()
    try:
        # Extract data from database
        raw_df = extract_data_from_db(db)

        if raw_df is None:
            print("Skipping retraining due to insufficient data")
            return False

        # Create features
        print("Creating features from raw data...")
        # Add difficulty numeric mapping
        diff_map = {"Easy": 0, "Medium": 1, "Hard": 2}
        raw_df["diff_num"] = raw_df["difficulty"].map(diff_map)

        feat_df = build_student_skill_features(raw_df)
        feat_df = create_mastery_labels(feat_df)

        if feat_df.empty:
            print("Feature creation failed or returned empty dataframe")
            return False

        # Save features to artifacts
        artifact_dir = settings.ARTIFACTS_DIR_ABSOLUTE
        artifact_dir.mkdir(exist_ok=True)

        features_path = artifact_dir / "student_skill_features.csv"
        feat_df.to_csv(features_path, index=False)
        print(f"Saved features to {features_path}")

        # Train model
        print("Training model...")
        model_path, metrics = train_model(
            feat_df=feat_df,
            artifact_dir=artifact_dir,
            epochs=50,
            batch_size=32,
            learning_rate=0.001
        )

        print(f"Model retrained successfully!")
        print(f"New model saved to: {model_path}")
        print(f"Training metrics: {metrics}")

        # Update model service to reload the model
        # In production, you might want to use a signal or restart the service
        print("Note: Restart the API server to load the new model")

        return True

    except Exception as e:
        print(f"Error during model retraining: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def should_retrain(last_retrain_time: datetime | None = None) -> bool:
    if last_retrain_time is None:
        return True

    interval = timedelta(hours=settings.RETRAIN_INTERVAL_HOURS)
    return datetime.now() - last_retrain_time >= interval


if __name__ == "__main__":
    # Manual trigger for retraining
    success = retrain_model()
    if success:
        print("Retraining completed successfully")
    else:
        print("Retraining failed or was skipped")
