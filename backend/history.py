from fastapi import APIRouter, Depends, HTTPException
from .database import get_db
from .auth import get_current_user_from_token

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("")
def get_interview_history(current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.id, i.role, i.experience, i.interview_type, i.difficulty, i.total_questions, i.overall_score, i.status, i.started_at, i.completed_at, r.performance_category
        FROM interviews i
        LEFT JOIN interview_results r ON i.id = r.interview_id
        WHERE i.user_id = %s
        ORDER BY i.started_at DESC
    """, (user_id,))
    history = cursor.fetchall()
    conn.close()

    return {"history": history}
