from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(String(50), index=True, nullable=False)
    skill_name = Column(String(100), nullable=False)
    difficulty = Column(String(20), nullable=False)  # Easy, Medium, Hard
    problem_type = Column(String(50), nullable=False)  # Coding, Debugging, Conceptual, Multiple Choice
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=True)  # JSON string for multiple choice options
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    hints = Column(Text, nullable=True)  # Hint text to help students
    course_id = Column(String(50), default="CS101")  # Course ID for model compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
