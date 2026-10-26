from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import random

from app.db.database import get_db
from app.models.user import User
from app.models.question import Question
from app.models.test_attempt import TestAttempt, TestAnswer
from app.schemas.question import QuestionResponse, TestSubmit, TestAttemptResponse, TestAttemptDetailResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/test", tags=["Test"])


@router.get("/questions", response_model=List[QuestionResponse])
def get_test_questions(
    skill_id: str = None,
    difficulty: str = None,
    num_questions: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get questions for a test.
    Can filter by skill_id and/or difficulty.
    """
    query = db.query(Question)

    if skill_id:
        query = query.filter(Question.skill_id == skill_id)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)

    questions = query.all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions found matching the criteria"
        )

    # Randomly select questions if more than requested
    if len(questions) > num_questions:
        questions = random.sample(questions, num_questions)

    return questions


@router.post("/submit", response_model=TestAttemptResponse)
def submit_test(
    test_data: TestSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a test attempt with answers.
    Returns the test results and triggers prediction/recommendation.
    """
    # Validate that we have answers
    if not test_data.answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No answers provided"
        )

    # Calculate score
    correct_count = 0
    total_questions = len(test_data.answers)

    # Create test attempt
    test_attempt = TestAttempt(
        user_id=current_user.id,
        total_score=0.0,  # Will update after processing
        total_questions=total_questions,
        correct_answers=0,  # Will update after processing
        time_taken_seconds=test_data.time_taken_seconds
    )
    db.add(test_attempt)
    db.flush()  # Get the ID without committing

    # Process each answer
    for answer in test_data.answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        if not question:
            continue

        is_correct = 1 if answer.user_answer.strip() == question.correct_answer.strip() else 0
        if is_correct:
            correct_count += 1

        test_answer = TestAnswer(
            test_attempt_id=test_attempt.id,
            question_id=answer.question_id,
            user_answer=answer.user_answer,
            is_correct=is_correct,
            time_taken_seconds=answer.time_taken_seconds,
            hint_used=answer.hint_used,  # Changed from hints_used to hint_used
            attempt_number=answer.attempt_number
        )
        db.add(test_answer)

    # Update test attempt with final score
    test_attempt.total_score = (correct_count / total_questions) * 100
    test_attempt.correct_answers = correct_count

    db.commit()
    db.refresh(test_attempt)

    # Note: Predictions are generated on-demand via the /api/prediction/recommendations endpoint
    # This allows the user to view recommendations after completing the test

    return test_attempt


@router.get("/history", response_model=List[TestAttemptResponse])
def get_test_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all test attempts for the current user."""
    attempts = db.query(TestAttempt).filter(
        TestAttempt.user_id == current_user.id
    ).order_by(TestAttempt.test_date.desc()).all()

    return attempts


@router.get("/history/{attempt_id}", response_model=TestAttemptDetailResponse)
def get_test_attempt_details(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific test attempt with question details."""
    attempt = db.query(TestAttempt).options(
        joinedload(TestAttempt.answers).joinedload(TestAnswer.question)
    ).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test attempt not found"
        )

    return attempt
