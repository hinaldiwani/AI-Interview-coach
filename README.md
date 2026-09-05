# HirePilot – AI-Powered Interview Preparation & Evaluation System

A complete full-stack web application built to conduct realistic job interviews, evaluate user responses using AI / local rule engines, and store candidates' performance history in a **MySQL** database.

---

## 📁 Complete Project Structure

```text
HirePilot/
│
├── frontend/
│   ├── index.html              # Landing Page
│   ├── login.html              # Candidate Login Page
│   ├── register.html           # Candidate Registration Page
│   ├── dashboard.html          # Candidate Analytics Dashboard Page
│   ├── interview-setup.html    # Role & Session Setup Page
│   ├── interview.html          # Live Mock Interview Room (Timer & Voice UI)
│   ├── results.html            # Detailed Evaluation Results & Review Page
│   ├── history.html            # Session History Records Page
│   │
│   ├── css/                    # Glassmorphic Stylesheets
│   └── js/                     # API Integration Scripts
│
├── backend/
│   ├── main.py                 # FastAPI Application Server
│   ├── database.py             # MySQL Connection Manager & Pool
│   ├── auth.py                 # PBKDF2 Password Hashing & JWT Manager
│   ├── interview.py            # Interview REST API Routes
│   ├── question_generator.py   # AI & Seed Question Generator Engine
│   ├── evaluator.py            # Answer Evaluation Engine
│   ├── dashboard.py            # User Analytics & Stats Routes
│   ├── history.py              # History Session Query Routes
│   └── requirements.txt        # Python Dependencies (No Flask)
│
├── database/
│   ├── database_setup.sql      # Complete Executable Setup Script
│   ├── schema.sql              # DDL Table Definitions
│   └── seed.sql                # Seed Question Bank
│
├── documentation/
│   └── HirePilot_Project_Report.pdf # Comprehensive Project Report PDF
│
├── .env.example                # Environment Template
├── .gitignore                  # Git Exclusion Rules
└── README.md                   # Complete Documentation
```

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Blue/Purple AI Dark Theme), JavaScript (ES6+ with `fetch()` API).
- **Backend**: Python 3.11 with **FastAPI** & **Uvicorn** (Strictly **NO Flask** used).
- **Database**: **MySQL** (`ai_interview_coach`) with `PyMySQL` driver.
- **AI Integration**: Primary support for Google Gemini API (`GEMINI_API_KEY`) with intelligent local NLP fallback.

---

## 🗄️ Database Setup Instructions

Open your **MySQL 8.0 Command Line Client** (or terminal with `mysql --port=3305 -u root -p`) and execute the complete setup script:

```sql
SOURCE C:/Users/Hinal/Desktop/Coding Club/Projects/AI interview coach/database/database_setup.sql;
```

Verify that the database was created:

```sql
SHOW DATABASES;
```

You will see:

```text
ai_interview_coach
```

Select the database:

```sql
USE ai_interview_coach;
```

Verify all 7 required tables exist:

```sql
SHOW TABLES;
```

You will see:

```text
answers
evaluations
interview_results
interviews
question_bank
questions
users
```

Verify seed question bank count:

```sql
SELECT COUNT(*) FROM question_bank;
```

---

## 🚀 How to Run the Project

### Step 1: Configure `.env`
Ensure your local `.env` file matches your MySQL Server credentials:

```env
DB_HOST=localhost
DB_PORT=3305
DB_USER=root
DB_PASSWORD=hinal
DB_NAME=ai_interview_coach

GEMINI_API_KEY=
HOST=127.0.0.1
PORT=8000
```

### Step 2: Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3: Start the Backend Application
Run the root launcher:
```bash
python run.py
```

On server start, the terminal will clearly display:

```text
HirePilot Backend
-----------------
Connecting to MySQL...
Database: ai_interview_coach
MySQL Connected Successfully
Backend Started Successfully
```

### Step 4: Access the Frontend
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**
