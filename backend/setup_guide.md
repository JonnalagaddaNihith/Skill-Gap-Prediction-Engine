# Skill Gap Prediction Backend

FastAPI backend for the Skill Gap Prediction system with MySQL database and ML model integration.

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Database

Ensure MySQL is installed and running. Create a database:

```sql
CREATE DATABASE skill_gap_db;
```

Update the database configuration in `app/config.py` or create a `.env` file:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=skill_gap_db
SECRET_KEY=your-super-secret-key
```

### 3. Migrate Database (if needed)

If you have an existing database from a previous version, run the migration script to add new columns:

```bash
python migrate_db.py
```

This will add:
- `course_id` column to `questions` table
- `hint_used` column to `test_answers` table  
- `attempt_number` column to `test_answers` table

### 4. Seed the Database

Run the seed script to populate initial questions and create a test user:

```bash
python seed_questions.py
```

This will:
- Create all database tables
- Add sample questions for all skills
- Create a test user: `username=testuser`, `password=test123`

### 5. Run the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive JWT token
- `GET /api/auth/me` - Get current user info (requires auth)

### Test

- `GET /api/test/questions` - Get test questions (optional filters: skill_id, difficulty, num_questions)
- `POST /api/test/submit` - Submit a test attempt with answers
- `GET /api/test/history` - Get all test attempts for current user
- `GET /api/test/history/{attempt_id}` - Get specific test attempt details

### Prediction

- `GET /api/prediction/recommendations` - Get skill gaps and learning recommendations

## Model Integration

The backend integrates with the trained PyTorch model from `skill_gap_model/Torch_Model/`. 

### Required Model Parameters

The model expects the following parameters for each test answer:
- `student_id` - User ID
- `question_id` - Question ID
- `skill_id` - Skill identifier (e.g., SK001)
- `correct` - Whether the answer was correct (0 or 1)
- `attempt_number` - Attempt number for this question
- `response_time` - Time taken to answer (in seconds)
- `hint_used` - Number of hints used (0 or 1)
- `difficulty` - Question difficulty (Easy, Medium, Hard)
- `course_id` - Course identifier
- `problem_type` - Type of problem (Coding, Debugging, Conceptual, Multiple Choice)

These parameters are stored in the database and used to:
1. Extract features for the ML model
2. Generate skill gap predictions
3. Provide personalized learning recommendations

## Model Retraining

The system supports periodic model retraining with new data from the database.

### Manual Retraining

```bash
python app/services/retrain_service.py
```

### Automatic Retraining

The retraining interval is configured in `app/config.py` (default: 24 hours).

To set up automatic retraining, you can:
1. Use a cron job (Linux/Mac) or Task Scheduler (Windows)
2. Use a background task scheduler like Celery
3. Add a startup event in FastAPI that checks periodically

Example cron job (runs daily at 2 AM):
```
0 2 * * * cd /path/to/Skill_Gap_Prediction/backend && python app/services/retrain_service.py
```

## Project Structure

```
backend/
├── app/
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py          # Database connection and session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── question.py          # Question model (includes course_id)
│   │   └── test_attempt.py      # TestAttempt and TestAnswer models (includes hint_used, attempt_number)
│   ├── schemas/
│   │   ├── user.py              # User Pydantic schemas
│   │   ├── question.py          # Question and test schemas (includes hint_used, attempt_number)
│   │   └── prediction.py        # Prediction response schemas
│   ├── services/
│   │   ├── auth.py              # Authentication logic (JWT, password hashing)
│   │   ├── model_service.py     # ML model integration with proper feature extraction
│   │   └── retrain_service.py   # Model retraining logic with all required parameters
│   ├── routers/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── test.py              # Test-related endpoints
│   │   └── prediction.py        # Prediction endpoints
│   ├── config.py                # Application configuration
│   └── main.py                  # FastAPI application entry point
├── requirements.txt
├── seed_questions.py           # Database seeding script (includes course_id)
├── migrate_db.py               # Migration script for existing databases
└── setup_guide.md              # This file
```

## Testing the API

### 1. Register a user

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "mypassword123"}'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "mypassword123"}'
```

Save the `access_token` from the response.

### 3. Get questions

```bash
curl -X GET "http://localhost:8000/api/test/questions?num_questions=5" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Submit test

```bash
curl -X POST "http://localhost:8000/api/test/submit" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "time_taken_seconds": 300,
    "answers": [
      {"question_id": 1, "user_answer": "x = 5", "time_taken_seconds": 30, "hint_used": 0, "attempt_number": 1},
      {"question_id": 2, "user_answer": "print('Hello')", "time_taken_seconds": 45, "hint_used": 0, "attempt_number": 1}
    ]
  }'
```

### 5. Get recommendations

```bash
curl -X GET "http://localhost:8000/api/prediction/recommendations" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Notes

- The ML model expects features in a specific format. The current implementation extracts all required parameters from the database (student_id, question_id, skill_id, correct, attempt_number, response_time, hint_used, difficulty, course_id, problem_type).
- For production use, you should:
  - Implement proper error handling and logging
  - Set up monitoring and alerting
  - Use environment variables for sensitive configuration
  - Implement rate limiting
  - Add proper input validation
  - Set up HTTPS
