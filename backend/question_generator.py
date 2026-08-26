import json
import random
import re
from typing import List, Dict, Any
from .config import AI_API_KEY
from .database import get_db

FALLBACK_QUESTIONS = [
    {
        "question_text": "What are the main features of Python as a programming language?",
        "topic": "Python Fundamentals",
        "ideal_answer": "Python is an interpreted, high-level, dynamically typed language supporting OOP, procedural, and functional paradigms. Key features include clean syntax, automatic garbage collection, and extensive standard libraries.",
        "key_concepts": "Interpreted, High-level, Dynamic Typing, Standard Library"
    },
    {
        "question_text": "What is the difference between a list and a tuple in Python?",
        "topic": "Data Structures",
        "ideal_answer": "Lists are mutable sequences defined using square brackets [], while tuples are immutable sequences defined using parentheses (). Tuples consume less memory and execute faster.",
        "key_concepts": "Mutability, Immutability, Memory Efficiency"
    },
    {
        "question_text": "What is the difference between `==` and `is` operators in Python?",
        "topic": "Operators & Memory",
        "ideal_answer": "The == operator compares value equality, checking if two objects hold identical content. The `is` operator compares identity equality, checking if two variables reference the exact same memory address.",
        "key_concepts": "Value Equality, Identity Equality, Memory Address"
    },
    {
        "question_text": "Explain Python decorators and provide a practical use case.",
        "topic": "Advanced Python",
        "ideal_answer": "A decorator is a higher-order function that takes another function as an argument, extends its functionality without modifying it, and returns the modified function. Practical uses include logging, auth, and caching.",
        "key_concepts": "First-class functions, Higher-order functions, Wrappers"
    },
    {
        "question_text": "How does exception handling work in Python using try, except, else, and finally?",
        "topic": "Error Handling",
        "ideal_answer": "Exceptions are handled in try-except blocks. `try` executes candidate code; `except` catches specific errors; `else` runs if no exception occurred; `finally` runs unconditionally for resource cleanup.",
        "key_concepts": "Try-Except, Exception Hierarchy, Cleanup"
    }
]

def generate_questions(
    role: str,
    experience: str,
    interview_type: str,
    difficulty: str,
    total_questions: int = 5
) -> List[Dict[str, Any]]:
    """Generates interview questions using Gemini API or MySQL database seed bank."""

    # 1. Try Gemini API if API key configured
    if AI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=AI_API_KEY)
            prompt = f"""
            Generate exactly {total_questions} interview questions for:
            - Role: {role}
            - Experience: {experience}
            - Type: {interview_type}
            - Difficulty: {difficulty}

            Return strict JSON list of objects with keys:
            "question_text", "topic", "ideal_answer", "key_concepts".
            Do NOT return markdown formatting.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
                raw_text = re.sub(r"\n?```$", "", raw_text)
            parsed = json.loads(raw_text)
            if isinstance(parsed, list) and len(parsed) > 0:
                for idx, q in enumerate(parsed):
                    q["question_order"] = idx + 1
                    q["difficulty"] = difficulty
                    q["question_type"] = interview_type
                return parsed[:total_questions]
        except Exception as e:
            print(f"[AI Generator Warning] API call skipped ({e}). Using Database Seed Bank.")

    # 2. Database Seed Bank Fallback
    db_questions = []
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT question_text, topic, ideal_answer, key_concepts 
               FROM question_bank 
               WHERE (role = %s OR role = 'Software Developer') 
                 AND (difficulty = %s OR difficulty = 'Medium')""",
            (role, difficulty)
        )
        rows = cursor.fetchall()
        conn.close()
        if rows:
            db_questions = list(rows)
    except Exception as db_err:
        print(f"[Database Seed Bank Warning] {db_err}")

    # Fallback to local array if db seed query empty
    if not db_questions:
        db_questions = FALLBACK_QUESTIONS

    # Shuffle for randomness
    pool = list(db_questions)
    random.shuffle(pool)
    while len(pool) < total_questions:
        pool.extend(db_questions)

    selected = []
    for idx in range(total_questions):
        item = pool[idx].copy()
        item["question_order"] = idx + 1
        item["difficulty"] = difficulty
        item["question_type"] = interview_type
        selected.append(item)

    return selected
