# Skill Gap Prediction System

A complete ML-powered system for predicting skill gaps in learners and providing personalized learning recommendations. The system includes synthetic data generation, PyTorch-based model training, FastAPI backend, and React frontend.

## Prerequisites

- **Python**: 3.9 or higher
- **Node.js**: 18.0 or higher
- **MySQL**: 8.0 or higher
- **Git**: For cloning the repository

## Project Structure

```
Skill_Gap_Prediction/
├── Synthetic Data/              # Data generation scripts
├── skill_gap_model/             # PyTorch model training
├── backend/                     # FastAPI backend
├── frontend/                    # React frontend
├── artifacts/                   # Trained models and processed data
└── DataSet_Output/              # Generated datasets
```

---

## 1. Creating Synthetic Data

The data generation process has two steps:
1. **Base Data Generation**: Creates initial learner assessment data using learner.py
2. **Data Expansion**: Uses SDV (Synthetic Data Vault) to scale to 500k rows

### Step 1.1: Install Dependencies

Navigate to the `Synthetic Data` directory and install required packages:

```bash
cd "Synthetic Data"
pip install pandas numpy openpyxl sdv
```

### Step 1.2: Generate Base Data

Run the learner script to create the initial dataset:

```bash
python learner.py
```

This will:
- Generate synthetic data for 1000 students across 8 skills
- Create `DataSet_Output/synthetic_learner_assessments.xlsx`
- Print summary statistics

### Step 1.3: Expand Data with SDV

Run the SDV generator to scale the dataset:

```bash
python Synthetic_Dataset_generator_script.py
```

This will:
- Load the base data from the Excel file
- Generate 500,000 synthetic rows using Gaussian Copula Synthesizer
- Save to `DataSet_Output/Generated_Learner_Assessment.csv`
- Create metadata file `DataSet_Output/Generated_metadata.json`

**Note**: You can adjust `NUM_ROWS` in `Synthetic_Dataset_generator_script.py` to generate more or fewer rows.

---

## 2. Training the Skill Gap Model

Train the PyTorch neural network model on the generated data.

### Step 2.1: Install Model Dependencies

```bash
cd ../skill_gap_model
pip install -r requirements.txt
```

### Step 2.2: Run Feature Engineering

The training script automatically runs feature engineering if needed, but you can run it separately:

```bash
cd Torch_Model
python feature_engineering.py
```

This will:
- Load `DataSet_Output/Generated_Learner_Assessment.csv`
- Build student-skill feature vectors
- Create mastery labels
- Save to `artifacts/student_skill_features.csv`

### Step 2.3: Train the Model

```bash
python train_test.py
```

This will:
- Load or generate features
- Split data by student (80% train, 20% validation)
- Train `SkillProficiencyNet` for 100 epochs
- Evaluate on validation set (MAE, RMSE, accuracy, F1, etc.)
- Save trained model to `artifacts/skill_proficiency_model.pt`
- Save learning activities to `artifacts/activities.json`
- Display demo predictions and recommendations

**Expected Output**:
- Validation metrics (MAE, RMSE, Correlation, Accuracy, Precision, Recall, F1)
- Demo skill gap identification for sample students
- Recommended learning activities

---

## 3. Setting Up the Backend

The backend is a FastAPI application with MySQL database and JWT authentication.

### Step 3.1: Create Database and User

Log in to MySQL:

```bash
mysql -u root -p
```

Run the following SQL commands:

```sql
-- Create database
CREATE DATABASE skill_gap_db;

-- Create user (replace with your password)
CREATE USER 'skillgap_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON skill_gap_db.* TO 'skillgap_user'@'localhost';
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

### Step 3.2: Configure Backend Environment

Navigate to the backend directory:

```bash
cd ../../backend
```

Create a `.env` file in the `backend` directory:

```bash
# Database Configuration
MYSQL_HOST=your_mysql_host
MYSQL_PORT=your_mysql_port
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=skill_gap_db

# JWT Secret (generate a secure random string)
SECRET_KEY=your_very_secure_random_secret_key_here_change_this_in_production

# Model Paths (relative to backend)
MODEL_PATH=../artifacts/skill_proficiency_model.pt
FEATURES_PATH=../artifacts/student_skill_features.csv
ACTIVITIES_PATH=../artifacts/activities.json
```

**Important**: Generate a secure `SECRET_KEY` using:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3.3: Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### Step 3.4: Initialize Database

The database tables will be automatically created when you start the backend (via `Base.metadata.create_all` in `main.py`).

---

## 4. Setting Up the Frontend

The frontend is a React application built with Vite and Material-UI.

### Step 4.1: Install Frontend Dependencies

Navigate to the frontend directory:

```bash
cd ../frontend
```

Install dependencies using npm:

```bash
npm install
```

Or using yarn:

```bash
yarn install
```

This will install:
- React 19.3.1
- Material-UI (MUI) 6.4.8
- React Router DOM 7.3.0
- Axios 1.7.9
- Vite 5.4.11

### Step 4.2: Configure API Endpoint

The frontend should be configured to connect to the backend API. Check the API configuration in your React components and ensure it points to `http://localhost:8000`.

---

## 5. Running Backend and Frontend

### Step 5.1: Start the Backend

From the `backend` directory:

```bash
uvicorn app.main:app
```

The backend will start at `http://localhost:8000`

**Available endpoints**:
- `http://localhost:8000` - API root
- `http://localhost:8000/docs` - Interactive API documentation (Swagger UI)
- `http://localhost:8000/health` - Health check endpoint
- `http://localhost:8000/auth/*` - Authentication endpoints
- `http://localhost:8000/prediction/*` - Prediction endpoints
- `http://localhost:8000/test/*` - Test management endpoints

### Step 5.2: Start the Frontend

From the `frontend` directory (in a new terminal):

```bash
npm run dev
```

Or using yarn:

```bash
yarn dev
```

The frontend will start at `http://localhost:5173` (or another port if 5173 is in use)

### Step 5.3: Access the Application

1. Open your browser and navigate to `http://localhost:5173`
2. Register a new user account
3. Log in with your credentials
4. Take tests or view skill gap predictions
5. Receive personalized learning recommendations

---

## Verification Checklist

- [ ] Synthetic data generated in `DataSet_Output/Generated_Learner_Assessment.csv`
- [ ] Model trained and saved to `artifacts/skill_proficiency_model.pt`
- [ ] MySQL database `skill_gap_db` created
- [ ] Backend `.env` file configured with correct database credentials
- [ ] Backend starts successfully at `http://localhost:8000`
- [ ] API documentation accessible at `http://localhost:8000/docs`
- [ ] Frontend starts successfully at `http://localhost:5173`
- [ ] Frontend can communicate with backend API

---

## Troubleshooting

### Backend Issues

**Database connection error**:
- Verify MySQL is running: `mysql -u root -p`
- Check credentials in `.env` file
- Ensure database `skill_gap_db` exists

**Model loading error**:
- Ensure `artifacts/skill_proficiency_model.pt` exists
- Check that paths in `.env` are correct relative to backend directory

### Frontend Issues

**Port already in use**:
- Kill process on port 5173: `npx kill-port 5173` (Windows) or `lsof -ti:5173 | xargs kill` (Mac/Linux)
- Or configure Vite to use a different port in `vite.config.js`

**API connection error**:
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Verify no firewall blocking localhost connections

---

## Development Notes

- The model uses PyTorch with GPU support if available (CUDA)
- Backend includes automatic model retraining every 24 hours (configurable via `RETRAIN_INTERVAL_HOURS`)
- Frontend uses Material-UI components for consistent styling
- All API routes are documented in Swagger UI at `/docs`

---
