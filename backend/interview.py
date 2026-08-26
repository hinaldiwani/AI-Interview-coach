import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .database import get_db
from .auth import get_current_user_from_token
from .question_generator import generate_questions
from .evaluator import evaluate_answer

router = APIRouter(prefix="/api/interviews", tags=["interviews"])

class CreateInterviewReq(BaseModel):
    role: str
    experience: str
    interview_type: str
    difficulty: str
    total_questions: int = 5

class SubmitAnswerReq(BaseModel):
    question_id: int
    user_answer: str

@router.post("")
def create_interview(req: CreateInterviewReq, current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO interviews 
        (user_id, role, experience, interview_type, difficulty, total_questions, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'in_progress')""",
        (user_id, req.role, req.experience, req.interview_type, req.difficulty, req.total_questions)
    )
    interview_id = cursor.lastrowid

    # Generate Questions
    questions = generate_questions(
        role=req.role,
        experience=req.experience,
        interview_type=req.interview_type,
        difficulty=req.difficulty,
        total_questions=req.total_questions
    )

    saved_questions = []
    for q in questions:
        cursor.execute(
            """INSERT INTO questions
            (interview_id, question_text, question_type, difficulty, question_order, ideal_answer, key_concepts)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                interview_id,
                q["question_text"],
                q.get("question_type", req.interview_type),
                q.get("difficulty", req.difficulty),
                q.get("question_order", 1),
                q.get("ideal_answer", ""),
                q.get("key_concepts", "")
            )
        )
        q_id = cursor.lastrowid
        saved_questions.append({
            "id": q_id,
            "question_order": q["question_order"],
            "question_text": q["question_text"],
            "question_type": q.get("question_type", req.interview_type),
            "difficulty": q.get("difficulty", req.difficulty),
            "ideal_answer": q.get("ideal_answer", ""),
            "key_concepts": q.get("key_concepts", "")
        })

    conn.close()

    return {
        "interview_id": interview_id,
        "role": req.role,
        "experience": req.experience,
        "interview_type": req.interview_type,
        "difficulty": req.difficulty,
        "total_questions": req.total_questions,
        "questions": saved_questions
    }

@router.post("/{interview_id}/answer")
def submit_answer(interview_id: int, req: SubmitAnswerReq, current_user: dict = Depends(get_current_user_from_token)):
    conn = get_db()
    cursor = conn.cursor()
    user_id = int(current_user["sub"])

    cursor.execute("SELECT id, role, difficulty FROM interviews WHERE id = %s AND user_id = %s", (interview_id, user_id))
    interview = cursor.fetchone()
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    cursor.execute("SELECT id, question_text, ideal_answer, key_concepts FROM questions WHERE id = %s AND interview_id = %s", (req.question_id, interview_id))
    question = cursor.fetchone()
    if not question:
        conn.close()
        raise HTTPException(status_code=404, detail="Question not found.")

    # Evaluate Answer
    eval_res = evaluate_answer(
        question_text=question["question_text"],
        user_answer=req.user_answer,
        ideal_answer=question["ideal_answer"] or "",
        key_concepts=question["key_concepts"] or "",
        role=interview["role"],
        difficulty=interview["difficulty"]
    )

    # Save/Update Answer
    cursor.execute("SELECT id FROM answers WHERE interview_id = %s AND question_id = %s", (interview_id, req.question_id))
    existing_ans = cursor.fetchone()

    if existing_ans:
        answer_id = existing_ans["id"]
        cursor.execute("UPDATE answers SET user_answer = %s WHERE id = %s", (req.user_answer, answer_id))
        cursor.execute(
            """UPDATE evaluations SET
            score = %s, correctness_score = %s, relevance_score = %s, technical_score = %s,
            clarity_score = %s, completeness_score = %s, feedback = %s, ideal_answer = %s,
            improvement_suggestion = %s WHERE answer_id = %s""",
            (
                eval_res["score"], eval_res["correctness_score"], eval_res["relevance_score"],
                eval_res["technical_score"], eval_res["clarity_score"], eval_res["completeness_score"],
                eval_res["feedback"], eval_res["ideal_answer"], eval_res["improvement_suggestion"], answer_id
            )
        )
    else:
        cursor.execute("INSERT INTO answers (interview_id, question_id, user_answer) VALUES (%s, %s, %s)", (interview_id, req.question_id, req.user_answer))
        answer_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO evaluations
            (answer_id, score, correctness_score, relevance_score, technical_score, clarity_score, completeness_score, feedback, ideal_answer, improvement_suggestion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                answer_id, eval_res["score"], eval_res["correctness_score"], eval_res["relevance_score"],
                eval_res["technical_score"], eval_res["clarity_score"], eval_res["completeness_score"],
                eval_res["feedback"], eval_res["ideal_answer"], eval_res["improvement_suggestion"]
            )
        )

    conn.close()
    return {"message": "Answer evaluated successfully.", "evaluation": eval_res}

@router.post("/{interview_id}/complete")
def complete_interview(interview_id: int, current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interviews WHERE id = %s AND user_id = %s", (interview_id, user_id))
    interview = cursor.fetchone()
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    cursor.execute("""
        SELECT a.*, e.score, e.correctness_score, e.relevance_score, e.technical_score,
               e.clarity_score, e.completeness_score, e.improvement_suggestion, e.feedback
        FROM answers a
        JOIN evaluations e ON a.id = e.answer_id
        WHERE a.interview_id = %s
    """, (interview_id,))
    evals = cursor.fetchall()

    if not evals:
        overall_score = tech_score = correctness_score = comm_score = comp_score = 0.0
    else:
        avg_score_10 = sum(e["score"] for e in evals) / len(evals)
        overall_score = round(avg_score_10 * 10, 1)
        tech_score = round(sum(e["technical_score"] for e in evals) / len(evals) * 10, 1)
        correctness_score = round(sum(e["correctness_score"] for e in evals) / len(evals) * 10, 1)
        comm_score = round(sum(e["clarity_score"] for e in evals) / len(evals) * 10, 1)
        comp_score = round(sum(e["completeness_score"] for e in evals) / len(evals) * 10, 1)

    if overall_score >= 85:
        category = "EXCELLENT"
    elif overall_score >= 70:
        category = "GOOD"
    elif overall_score >= 50:
        category = "AVERAGE"
    else:
        category = "NEEDS IMPROVEMENT"

    cursor.execute("UPDATE interviews SET overall_score = %s, status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = %s", (overall_score, interview_id))

    strengths_text = "Good core comprehension; clean answers; clear communication."
    weak_text = "Detailed code syntax; advanced edge case optimization."
    recs_text = f"Practice 10 {interview['role']} questions on Medium difficulty. Focus on technical definitions."

    # Save to interview_results
    cursor.execute("""
        INSERT INTO interview_results
        (interview_id, technical_score, correctness_score, communication_score, completeness_score, overall_score, performance_category, strengths, weak_areas, recommendations)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        interview_id, tech_score, correctness_score, comm_score, comp_score,
        overall_score, category, strengths_text, weak_text, recs_text
    ))

    conn.close()

    return {
        "interview_id": interview_id,
        "overall_score": overall_score,
        "performance_category": category,
        "technical_score": tech_score,
        "correctness_score": correctness_score,
        "communication_score": comm_score,
        "completeness_score": comp_score,
        "strengths": strengths_text,
        "weak_areas": weak_text,
        "recommendations": recs_text
    }

@router.get("/{interview_id}/results")
def get_interview_results(interview_id: int, current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interviews WHERE id = %s AND user_id = %s", (interview_id, user_id))
    interview = cursor.fetchone()
    if not interview:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    cursor.execute("SELECT * FROM interview_results WHERE interview_id = %s ORDER BY id DESC LIMIT 1", (interview_id,))
    result = cursor.fetchone()

    cursor.execute("""
        SELECT q.question_order, q.question_text, a.user_answer, e.score, e.feedback, e.ideal_answer, e.improvement_suggestion
        FROM questions q
        LEFT JOIN answers a ON q.id = a.question_id
        LEFT JOIN evaluations e ON a.id = e.answer_id
        WHERE q.interview_id = %s
        ORDER BY q.question_order ASC
    """, (interview_id,))
    reviews = cursor.fetchall()

    conn.close()
    return {"interview": interview, "result": result, "reviews": reviews}
