from sqlalchemy import Column, Integer, Float, DateTime, Text, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_date = Column(DateTime(timezone=True), server_default=func.now())
    total_score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    time_taken_seconds = Column(Integer, nullable=True)

    # Relationship with answers
    answers = relationship("TestAnswer", back_populates="test_attempt", cascade="all, delete-orphan")


class TestAnswer(Base):
    __tablename__ = "test_answers"

    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Integer, nullable=False)  # 0 or 1
    time_taken_seconds = Column(Integer, nullable=True)
    hint_used = Column(Integer, default=0)  
    attempt_number = Column(Integer, default=1)

    # Relationships
    test_attempt = relationship("TestAttempt", back_populates="answers")
    question = relationship("Question", backref="test_answers")
