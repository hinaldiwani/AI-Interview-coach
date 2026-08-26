from fastapi import APIRouter, Depends, HTTPException
from .database import get_db
from .auth import get_current_user_from_token

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("")
def get_dashboard_stats(current_user: dict = Depends(get_current_user_from_token)):
    user_id = int(current_user["sub"])
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM interviews WHERE user_id = %s AND status = 'completed'", (user_id,))
    total_interviews = cursor.fetchone()["count"]

    cursor.execute("SELECT AVG(overall_score) as avg_s, MAX(overall_score) as max_s FROM interviews WHERE user_id = %s AND status = 'completed'", (user_id,))
    stats = cursor.fetchone()
    avg_score = round(stats["avg_s"], 1) if stats["avg_s"] is not None else 0.0
    best_score = round(stats["max_s"], 1) if stats["max_s"] is not None else 0.0

    cursor.execute("SELECT overall_score FROM interviews WHERE user_id = %s AND status = 'completed' ORDER BY completed_at DESC LIMIT 1", (user_id,))
    latest_row = cursor.fetchone()
    latest_score = round(latest_row["overall_score"], 1) if latest_row else 0.0

    cursor.execute("""
        SELECT i.id, i.role, i.interview_type, i.difficulty, i.overall_score, i.started_at, r.performance_category
        FROM interviews i
        LEFT JOIN interview_results r ON i.id = r.interview_id
        WHERE i.user_id = %s AND i.status = 'completed'
        ORDER BY i.completed_at DESC LIMIT 5
    """, (user_id,))
    recent_interviews = cursor.fetchall()

    conn.close()

    return {
        "user_name": current_user.get("name", "User"),
        "total_interviews": total_interviews,
        "average_score": avg_score,
        "best_score": best_score,
        "latest_score": latest_score,
        "recent_interviews": recent_interviews,
        "strong_topics": ["Python Basics", "Problem Solving", "HTTP Protocols"],
        "weak_topics": ["Exception Handling", "Decorators", "Memory Management"]
    }
