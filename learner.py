import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)

# Synthetic population and technical skills
N_STUDENTS = 300
N_SKILLS = 8
MIN_ATTEMPTS = 8
MAX_ATTEMPTS = 20

skills = {
    "SK001": ("Python Basics", "COURSE_PY", 0.16, 0.20, 0.10, 0.25),
    "SK002": ("Python Loops", "COURSE_PY", 0.12, 0.20, 0.10, 0.25),
    "SK003": ("Functions", "COURSE_PY", 0.10, 0.18, 0.12, 0.30),
    "SK004": ("Data Structures", "COURSE_DS", 0.10, 0.22, 0.12, 0.30),
    "SK005": ("SQL Queries", "COURSE_SQL", 0.14, 0.20, 0.10, 0.25),
    "SK006": ("SQL Joins", "COURSE_SQL", 0.08, 0.22, 0.12, 0.30),
    "SK007": ("Debugging", "COURSE_CS", 0.08, 0.18, 0.15, 0.35),
    "SK008": ("Algorithms", "COURSE_ALGO", 0.06, 0.25, 0.15, 0.35),
}
difficulty_levels = ["Easy", "Medium", "Hard"]
difficulty_weights = [0.45, 0.40, 0.15]
problem_types = ["Multiple Choice", "Conceptual", "Coding", "Debugging"]
problem_weights = [0.25, 0.20, 0.35, 0.20]

rows = []
question_counter = 1

for student_idx in range(1, N_STUDENTS + 1):
    student_id = f"STU{student_idx:04d}"
    # Individual learner differences
    learner_ability = rng.beta(2.2, 2.2)
    
    for skill_id, (skill_name, course_id, p_learn, p_guess, p_slip, base_difficulty) in skills.items():
        n_attempts = int(rng.integers(MIN_ATTEMPTS, MAX_ATTEMPTS + 1))
        # Some students begin with more prior knowledge than others
        mastered = bool(rng.random() < (0.10 + 0.65 * learner_ability))
        
        for attempt in range(1, n_attempts + 1):
            difficulty = rng.choice(difficulty_levels, p=difficulty_weights)
            difficulty_factor = {"Easy": 0.0, "Medium": 0.10, "Hard": 0.22}[difficulty]
            
            # Hint use is more likely when skill is not mastered
            hint_probability = 0.12 + (0.42 if not mastered else 0.0)
            hint_used = int(rng.random() < min(hint_probability, 0.85))
            
            # Response probability includes latent mastery, guessing, slipping,
            # learner ability, difficulty, and a modest hint benefit.
            if mastered:
                p_correct = 1 - p_slip
            else:
                p_correct = p_guess + 0.18 * learner_ability
            
            p_correct += (0.08 if hint_used else 0.0)
            p_correct -= difficulty_factor
            p_correct = float(np.clip(p_correct, 0.03, 0.98))
            correct = int(rng.random() < p_correct)
            
            # Simulated response time in seconds; lower on mastered/easier tasks
            base_time = {"Easy": 35, "Medium": 60, "Hard": 95}[difficulty]
            response_time = rng.lognormal(
                mean=np.log(base_time * (1.35 if not mastered else 0.80)),
                sigma=0.35
            )
            response_time = round(float(np.clip(response_time, 5, 600)), 2)
            
            answer_attempt = int(rng.choice([1, 2, 3], p=[0.78, 0.17, 0.05]))
            problem_type = str(rng.choice(problem_types, p=problem_weights))
            
            rows.append({
                "student_id": student_id,
                "question_id": f"Q{question_counter:07d}",
                "skill_id": skill_id,
                "correct": correct,
                "attempt_number": attempt,
                "response_time": response_time,
                "hint_used": hint_used,
                "difficulty": difficulty,
                "course_id": course_id,
                "answer_attempt": answer_attempt,
                "problem_type": problem_type,
            })
            question_counter += 1
            
            # Learning transition: probability depends on skill and learner ability
            effective_learning = min(0.75, p_learn * (0.65 + 0.70 * learner_ability))
            if not mastered and rng.random() < effective_learning:
                mastered = True

df = pd.DataFrame(rows)
out_path = Path("synthetic_learner_assessments.csv")
df.to_csv(out_path, index=False)

summary = {
    "rows": len(df),
    "students": df["student_id"].nunique(),
    "skills": df["skill_id"].nunique(),
    "questions": df["question_id"].nunique(),
    "overall_correct_rate": round(float(df["correct"].mean()), 3),
    "file": str(out_path),
}
print(summary)
print(df.head(10).to_string(index=False))
