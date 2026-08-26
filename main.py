import os
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Header, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from database import init_db, get_db
from auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    get_current_user_from_token
)
from ai_engine import (
    generate_interview_questions, 
    evaluate_user_answer, 
    generate_personalized_recommendations
)

app = FastAPI(
    title="AI Interview Coach API",
    description="AI-Powered Interview Preparation & Evaluation System API",
    version="1.0.0"
)

# CORS middleware for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Event to initialize database schema
@app.on_event("startup")
def startup_event():
    init_db()

# --- Pydantic Request Models ---
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class CreateInterviewRequest(BaseModel):
    role: str
    experience_level: str
    interview_type: str
    difficulty: str
    num_questions: int = 5

class SubmitAnswerRequest(BaseModel):
    question_id: int
    user_answer: str
    time_taken_seconds: int = 0


# --- Authentication Routes ---
@app.post("/api/auth/register")
def register_user(req: RegisterRequest):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if email exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (req.email,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Email is already registered. Please login.")
    
    pw_hash = hash_password(req.password)
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (req.name, req.email, pw_hash)
    )
    user_id = cursor.lastrowid
    conn.close()
    
    token = create_access_token({"sub": str(user_id), "name": req.name, "email": req.email})
    return {
        "message": "Registration successful",
        "token": token,
        "user": {"id": user_id, "name": req.name, "email": req.email}
    }


@app.post("/api/auth/login")
def login_user(req: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (req.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    token = create_access_token({"sub": str(user["id"]), "name": user["name"], "email": user["email"]})
    return {
        "message": "Login successful",
        "token": token,
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
    }


@app.get("/api/auth/me")
def get_current_user(current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"user": user}


# --- Interview Flow Routes ---
@app.post("/api/interviews/create")
def create_interview(req: CreateInterviewRequest, current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    
    # 1. Create interview entry in DB
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO interviews 
        (user_id, role, experience_level, interview_type, difficulty, num_questions, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'in_progress')""",
        (user_id, req.role, req.experience_level, req.interview_type, req.difficulty, req.num_questions)
    )
    interview_id = cursor.lastrowid

    # 2. Generate questions using AI engine
    questions = generate_interview_questions(
        role=req.role,
        experience=req.experience_level,
        interview_type=req.interview_type,
        difficulty=req.difficulty,
        num_questions=req.num_questions
    )

    # 3. Store generated questions in DB
    saved_questions = []
    for q in questions:
        cursor.execute(
            """INSERT INTO questions
            (interview_id, question_number, question_text, topic, difficulty, ideal_answer, key_concepts)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                interview_id,
                q["question_number"],
                q["question"],
                q.get("topic", "General"),
                q.get("difficulty", req.difficulty),
                q.get("ideal_answer", ""),
                q.get("key_concepts", "")
            )
        )
        q_id = cursor.lastrowid
        saved_questions.append({
            "id": q_id,
            "question_number": q["question_number"],
            "question_text": q["question"],
            "topic": q.get("topic", "General"),
            "difficulty": q.get("difficulty", req.difficulty),
            "ideal_answer": q.get("ideal_answer", ""),
            "key_concepts": q.get("key_concepts", "")
        })

    conn.close()

    return {
        "interview_id": interview_id,
        "role": req.role,
        "experience_level": req.experience_level,
        "interview_type": req.interview_type,
        "difficulty": req.difficulty,
        "num_questions": req.num_questions,
        "questions": saved_questions
    }


@app.post("/api/interviews/{interview_id}/submit_answer")
def submit_answer(
    interview_id: int, 
    req: SubmitAnswerRequest, 
    current_user: dict = Depends(get_current_user_from_token)
):
    conn = get_db()
    cursor = conn.cursor()

    # Verify interview ownership
    user_id = int(current_user["sub"])
    cursor.execute("SELECT id, role, difficulty FROM interviews WHERE id = %s AND user_id = %s", (interview_id, user_id))
    interview = cursor.fetchone()
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview session not found.")

    # Get question details
    cursor.execute("SELECT id, question_text, ideal_answer, key_concepts FROM questions WHERE id = %s AND interview_id = %s", (req.question_id, interview_id))
    question = cursor.fetchone()
    if not question:
        conn.close()
        raise HTTPException(status_code=404, detail="Question not found for this interview.")

    # Run AI evaluation
    eval_res = evaluate_user_answer(
        question_text=question["question_text"],
        user_answer=req.user_answer,
        ideal_answer=question["ideal_answer"] or "",
        key_concepts=question["key_concepts"] or "",
        role=interview["role"],
        difficulty=interview["difficulty"]
    )

    # Check if answer already exists (update if so, else insert)
    cursor.execute("SELECT id FROM answers WHERE interview_id = %s AND question_id = %s", (interview_id, req.question_id))
    existing_answer = cursor.fetchone()

    if existing_answer:
        answer_id = existing_answer["id"]
        cursor.execute(
            """UPDATE answers SET
            user_answer = %s, time_taken_seconds = %s, score = %s, status = %s,
            what_went_well = %s, areas_for_improvement = %s, ideal_answer = %s,
            key_concepts = %s, feedback_json = %s
            WHERE id = %s""",
            (
                req.user_answer, req.time_taken_seconds, eval_res["score"], eval_res["status"],
                eval_res["what_went_well"], eval_res["areas_for_improvement"], eval_res["ideal_answer"],
                eval_res["key_concepts"], json.dumps(eval_res), answer_id
            )
        )
        cursor.execute(
            """UPDATE evaluations SET
            correctness_score = %s, relevance_score = %s, technical_score = %s,
            completeness_score = %s, clarity_score = %s, confidence_score = %s,
            detailed_feedback = %s WHERE answer_id = %s""",
            (
                eval_res["correctness_score"], eval_res["relevance_score"], eval_res["technical_score"],
                eval_res["completeness_score"], eval_res["clarity_score"], eval_res["confidence_score"],
                eval_res["detailed_feedback"], answer_id
            )
        )
    else:
        cursor.execute(
            """INSERT INTO answers
            (interview_id, question_id, user_answer, time_taken_seconds, score, status,
             what_went_well, areas_for_improvement, ideal_answer, key_concepts, feedback_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                interview_id, req.question_id, req.user_answer, req.time_taken_seconds,
                eval_res["score"], eval_res["status"], eval_res["what_went_well"],
                eval_res["areas_for_improvement"], eval_res["ideal_answer"],
                eval_res["key_concepts"], json.dumps(eval_res)
            )
        )
        answer_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO evaluations
            (answer_id, correctness_score, relevance_score, technical_score,
             completeness_score, clarity_score, confidence_score, detailed_feedback)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                answer_id, eval_res["correctness_score"], eval_res["relevance_score"],
                eval_res["technical_score"], eval_res["completeness_score"],
                eval_res["clarity_score"], eval_res["confidence_score"], eval_res["detailed_feedback"]
            )
        )

    conn.close()
    return {"message": "Answer submitted and evaluated successfully.", "evaluation": eval_res}


@app.post("/api/interviews/{interview_id}/complete")
def complete_interview(
    interview_id: int, 
    current_user: dict = Depends(get_current_user_from_token)
):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interviews WHERE id = %s AND user_id = %s", (interview_id, user_id))
    interview = cursor.fetchone()
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    # Fetch all answers & evaluations for this interview
    cursor.execute("""
        SELECT a.*, e.correctness_score, e.relevance_score, e.technical_score,
               e.completeness_score, e.clarity_score, e.confidence_score, q.topic
        FROM answers a
        JOIN evaluations e ON a.id = e.answer_id
        JOIN questions q ON a.question_id = q.id
        WHERE a.interview_id = %s
    """, (interview_id,))
    answers_evals = cursor.fetchall()

    if not answers_evals:
        overall_score = 0.0
        tech_score = correctness_score = relevance_score = comm_score = comp_score = 0.0
    else:
        avg_10 = sum(item["score"] for item in answers_evals) / len(answers_evals)
        overall_score = round(avg_10 * 10, 1) # Convert score out of 10 to 100
        
        tech_score = round(sum(item["technical_score"] for item in answers_evals) / len(answers_evals) * 10, 1)
        correctness_score = round(sum(item["correctness_score"] for item in answers_evals) / len(answers_evals) * 10, 1)
        relevance_score = round(sum(item["relevance_score"] for item in answers_evals) / len(answers_evals) * 10, 1)
        comm_score = round(sum(item["clarity_score"] for item in answers_evals) / len(answers_evals) * 10, 1)
        comp_score = round(sum(item["completeness_score"] for item in answers_evals) / len(answers_evals) * 10, 1)

    # Determine Performance Category
    if overall_score >= 85:
        category = "Excellent"
    elif overall_score >= 70:
        category = "Good"
    elif overall_score >= 50:
        category = "Average"
    else:
        category = "Needs Improvement"

    # Update Interview Summary in DB
    cursor.execute("""
        UPDATE interviews SET
        overall_score = %s, performance_category = %s, technical_score = %s,
        correctness_score = %s, relevance_score = %s, communication_score = %s,
        completeness_score = %s, status = 'completed'
        WHERE id = %s
    """, (
        overall_score, category, tech_score, correctness_score,
        relevance_score, comm_score, comp_score, interview_id
    ))

    # Generate Personalized Recommendations
    recs = generate_personalized_recommendations(interview, answers_evals)
    
    # Store Recommendations in DB
    cursor.execute("""
        INSERT INTO recommendations
        (interview_id, weak_topics_json, strong_topics_json, practice_suggestions_json, recommended_difficulty)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        interview_id,
        json.dumps(recs["weak_topics"]),
        json.dumps(recs["strong_topics"]),
        json.dumps(recs["practice_suggestions"]),
        recs["recommended_difficulty"]
    ))

    conn.close()

    return {
        "message": "Interview completed successfully.",
        "interview_id": interview_id,
        "overall_score": overall_score,
        "performance_category": category,
        "breakdown": {
            "technical_knowledge": tech_score,
            "correctness": correctness_score,
            "relevance": relevance_score,
            "communication": comm_score,
            "completeness": comp_score
        },
        "recommendations": recs
    }


@app.get("/api/interviews/{interview_id}/results")
def get_interview_results(
    interview_id: int, 
    current_user: dict = Depends(get_current_user_from_token)
):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()

    # Get Interview metadata
    cursor.execute("SELECT * FROM interviews WHERE id = %s AND user_id = %s", (interview_id, user_id))
    interview = cursor.fetchone()
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview results not found.")

    # Get Questions, Answers & Evaluations
    cursor.execute("""
        SELECT q.id as question_id, q.question_number, q.question_text, q.topic, q.difficulty,
               q.ideal_answer as ref_ideal_answer, q.key_concepts as ref_key_concepts,
               a.user_answer, a.score, a.status as answer_status, a.what_went_well,
               a.areas_for_improvement, a.ideal_answer as eval_ideal_answer, a.key_concepts as eval_key_concepts,
               e.correctness_score, e.relevance_score, e.technical_score,
               e.completeness_score, e.clarity_score, e.confidence_score, e.detailed_feedback
        FROM questions q
        LEFT JOIN answers a ON q.id = a.question_id AND a.interview_id = q.interview_id
        LEFT JOIN evaluations e ON a.id = e.answer_id
        WHERE q.interview_id = %s
        ORDER BY q.question_number ASC
    """, (interview_id,))
    reviews = cursor.fetchall()

    # Get Recommendations
    cursor.execute("SELECT * FROM recommendations WHERE interview_id = %s ORDER BY id DESC LIMIT 1", (interview_id,))
    rec_row = cursor.fetchone()

    conn.close()

    recommendations = {
        "weak_topics": json.loads(rec_row["weak_topics_json"]) if rec_row and rec_row["weak_topics_json"] else [],
        "strong_topics": json.loads(rec_row["strong_topics_json"]) if rec_row and rec_row["strong_topics_json"] else [],
        "practice_suggestions": json.loads(rec_row["practice_suggestions_json"]) if rec_row and rec_row["practice_suggestions_json"] else [],
        "recommended_difficulty": rec_row["recommended_difficulty"] if rec_row else "Medium"
    }

    return {
        "interview": interview,
        "reviews": reviews,
        "recommendations": recommendations
    }


# --- User Dashboard & History Routes ---
@app.get("/api/dashboard/stats")
def get_dashboard_stats(current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()

    # Total completed interviews
    cursor.execute("SELECT COUNT(*) as count FROM interviews WHERE user_id = %s AND status = 'completed'", (user_id,))
    total_completed = cursor.fetchone()["count"]

    # Avg and Best Score
    cursor.execute("SELECT AVG(overall_score) as avg_score, MAX(overall_score) as max_score FROM interviews WHERE user_id = %s AND status = 'completed'", (user_id,))
    scores = cursor.fetchone()
    avg_score = round(scores["avg_score"], 1) if scores["avg_score"] is not None else 0.0
    best_score = round(scores["max_score"], 1) if scores["max_score"] is not None else 0.0

    # Recent Interviews
    cursor.execute("""
        SELECT id, role, experience_level, interview_type, difficulty, num_questions, overall_score, performance_category, created_at
        FROM interviews WHERE user_id = %s AND status = 'completed'
        ORDER BY created_at DESC LIMIT 5
    """, (user_id,))
    recent_interviews = cursor.fetchall()

    # Topic Mastery Breakdown (weak vs strong topics across all past recommendations)
    cursor.execute("""
        SELECT r.weak_topics_json, r.strong_topics_json
        FROM recommendations r
        JOIN interviews i ON r.interview_id = i.id
        WHERE i.user_id = %s
    """, (user_id,))
    rec_rows = cursor.fetchall()

    conn.close()

    weak_map = {}
    strong_map = {}
    for r in rec_rows:
        w_list = json.loads(r["weak_topics_json"]) if r["weak_topics_json"] else []
        s_list = json.loads(r["strong_topics_json"]) if r["strong_topics_json"] else []
        for item in w_list:
            weak_map[item] = weak_map.get(item, 0) + 1
        for item in s_list:
            strong_map[item] = strong_map.get(item, 0) + 1

    sorted_weak = sorted(weak_map.keys(), key=lambda x: weak_map[x], reverse=True)[:5]
    sorted_strong = sorted(strong_map.keys(), key=lambda x: strong_map[x], reverse=True)[:5]

    return {
        "total_interviews": total_completed,
        "average_score": avg_score,
        "best_score": best_score,
        "recent_interviews": recent_interviews,
        "weak_topics": sorted_weak if sorted_weak else ["Python Exception Handling", "OOP Inheritance"],
        "strong_topics": sorted_strong if sorted_strong else ["Basic Syntax", "Data Structures"]
    }


@app.get("/api/interviews/history")
def get_interview_history(current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, role, experience_level, interview_type, difficulty, num_questions, overall_score, performance_category, status, created_at
        FROM interviews WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    history = cursor.fetchall()
    conn.close()
    return {"history": history}


# --- Static Files & SPA Route ---
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    # Serve static file if exists, otherwise serve index.html
    file_path = os.path.join(static_dir, full_path)
    if full_path and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(status_code=404, content={"message": "Frontend not found."})
