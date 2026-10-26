from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.prediction import PredictionResponse
from app.services.auth import get_current_user
from app.services.model_service import predict_and_recommend

router = APIRouter(prefix="/api/prediction", tags=["Prediction"])


@router.get("/recommendations", response_model=PredictionResponse)
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get skill gap analysis and learning activity recommendations for the current user.
    """
    try:
        # Check if user has any test attempts
        from app.models.test_attempt import TestAttempt
        latest_attempt = db.query(TestAttempt).filter(
            TestAttempt.user_id == current_user.id
        ).order_by(TestAttempt.test_date.desc()).first()

        if not latest_attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No test attempts found. Please complete a test first."
            )

        # Generate predictions and recommendations
        result = predict_and_recommend(
            student_id=current_user.id,
            db=db
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )
