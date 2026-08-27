import json
import random
import re
from typing import List, Dict, Any
from .config import AI_API_KEY
from .database import get_db

# Specialized Fallback Pools for offline / seed backup
FALLBACK_TECHNICAL_QUESTIONS = [
    {
        "question_text": "What are the main features of Python as a programming language?",
        "topic": "Python Fundamentals",
        "question_type": "Technical",
        "ideal_answer": "Python is an interpreted, high-level, dynamically typed language supporting OOP, procedural, and functional paradigms. Key features include clean syntax, automatic garbage collection, and extensive standard libraries.",
        "key_concepts": "Interpreted, High-level, Dynamic Typing, Standard Library"
    },
    {
        "question_text": "What is the difference between a list and a tuple in Python?",
        "topic": "Data Structures",
        "question_type": "Technical",
        "ideal_answer": "Lists are mutable sequences defined using square brackets [], while tuples are immutable sequences defined using parentheses (). Tuples consume less memory and execute faster.",
        "key_concepts": "Mutability, Immutability, Memory Efficiency"
    },
    {
        "question_text": "What is the difference between `==` and `is` operators in Python?",
        "topic": "Operators & Memory",
        "question_type": "Technical",
        "ideal_answer": "The == operator compares value equality, checking if two objects hold identical content. The `is` operator compares identity equality, checking if two variables reference the exact same memory address.",
        "key_concepts": "Value Equality, Identity Equality, Memory Address"
    },
    {
        "question_text": "Explain Python decorators and provide a practical use case.",
        "topic": "Advanced Python",
        "question_type": "Technical",
        "ideal_answer": "A decorator is a higher-order function that takes another function as an argument, extends its functionality without modifying it, and returns the modified function. Practical uses include logging, auth, and caching.",
        "key_concepts": "First-class functions, Higher-order functions, Wrappers"
    },
    {
        "question_text": "How does exception handling work in Python using try, except, else, and finally?",
        "topic": "Error Handling",
        "question_type": "Technical",
        "ideal_answer": "Exceptions are handled in try-except blocks. `try` executes candidate code; `except` catches specific errors; `else` runs if no exception occurred; `finally` runs unconditionally for resource cleanup.",
        "key_concepts": "Try-Except, Exception Hierarchy, Cleanup"
    }
]

FALLBACK_HR_QUESTIONS = [
    {
        "question_text": "Tell me about yourself and why you chose a career in software engineering.",
        "topic": "Introduction",
        "question_type": "HR",
        "ideal_answer": "Candidate should summarize educational background, core technical skills, passion for technology, and long-term career ambition in a clear, concise manner.",
        "key_concepts": "Communication, Self-Introduction, Passion, Career Goals"
    },
    {
        "question_text": "Why are you interested in joining our company specifically?",
        "topic": "Company Fit",
        "question_type": "HR",
        "ideal_answer": "Candidate should demonstrate research into company products, engineering culture, and align personal professional goals with company mission.",
        "key_concepts": "Motivation, Alignment, Company Research, Product Understanding"
    },
    {
        "question_text": "What are your greatest professional strengths, and what is one area you are working to improve?",
        "topic": "Self Awareness",
        "question_type": "HR",
        "ideal_answer": "Candidate should highlight genuine technical strengths backed by project examples, and share an honest growth area alongside concrete steps taken to improve.",
        "key_concepts": "Strengths, Self Reflection, Continuous Learning, Adaptability"
    },
    {
        "question_text": "Where do you see yourself professionally in the next 3 to 5 years?",
        "topic": "Career Vision",
        "question_type": "HR",
        "ideal_answer": "Candidate should describe a realistic trajectory toward technical mastery, taking on architecture responsibilities, or leading project teams.",
        "key_concepts": "Vision, Growth Mindset, Long-term Commitment, Professional Development"
    },
    {
        "question_text": "How do you handle constructive criticism and feedback on your work?",
        "topic": "Workplace Culture",
        "question_type": "HR",
        "ideal_answer": "Candidate should show humility, active listening skills, and explain how feedback is evaluated to improve code quality and team performance.",
        "key_concepts": "Feedback, Professionalism, Team Collaboration, Receptiveness"
    }
]

FALLBACK_BEHAVIORAL_QUESTIONS = [
    {
        "question_text": "Tell me about a time when you had to work under a tight project deadline. How did you prioritize tasks?",
        "topic": "Time Management",
        "question_type": "Behavioral",
        "ideal_answer": "Candidate should structure response using STAR method: situation overview, task requirements, action taken to refactor scope/prioritize critical paths, and positive outcome.",
        "key_concepts": "STAR Method, Prioritization, Deadline Pressure, Problem Solving"
    },
    {
        "question_text": "Describe a situation where you had a technical disagreement with a teammate. How did you resolve it?",
        "topic": "Conflict Resolution",
        "question_type": "Behavioral",
        "ideal_answer": "Candidate should highlight respectful communication, evaluating technical benchmarks or metrics objectively, finding common ground, and committing to the final team decision.",
        "key_concepts": "Respectful Dialogue, Technical Trade-offs, Compromise, Team Consensus"
    },
    {
        "question_text": "Tell me about a project that did not go as planned or a mistake you made. What did you learn from it?",
        "topic": "Accountability & Growth",
        "question_type": "Behavioral",
        "ideal_answer": "Candidate should take ownership without blaming others, analyze root causes (estimation error, scope creep), and detail how they updated their engineering workflow.",
        "key_concepts": "Ownership, Root Cause Analysis, Post-Mortem, Accountability"
    },
    {
        "question_text": "Describe a time when you had to learn a completely new technology or framework quickly for a task.",
        "topic": "Adaptability",
        "question_type": "Behavioral",
        "ideal_answer": "Candidate should describe learning strategy (docs, tutorials, prototyping), rapid execution, and delivering a functional solution under time constraints.",
        "key_concepts": "Agile Learning, Prototyping, Resourcefulness, Execution"
    },
    {
        "question_text": "Give an example of a situation where you demonstrated leadership or initiative in a project.",
        "topic": "Leadership",
        "question_type": "Behavioral",
        "ideal_answer": "Candidate should describe identifying a gap or technical debt, proposing a solution, guiding peers, and delivering measurable value.",
        "key_concepts": "Initiative, Technical Leadership, Problem Identification, Impact"
    }
]


def normalize_text(text: str) -> str:
    """Normalizes string for deduplication comparison."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return " ".join(text.split())


def deduplicate_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Removes duplicate or near-duplicate questions based on normalized text."""
    unique = []
    seen_texts = set()

    for q in questions:
        norm = normalize_text(q.get("question_text", ""))
        if not norm:
            continue
        # Extract core words
        words = set(norm.split())
        is_duplicate = False

        for existing_words in seen_texts:
            intersection = words.intersection(existing_words)
            union = words.union(existing_words)
            jaccard_sim = len(intersection) / max(len(union), 1)
            if jaccard_sim > 0.65:
                is_duplicate = True
                break

        if not is_duplicate:
            seen_texts.add(frozenset(words))
            unique.append(q)

    return unique


def get_type_prompt_instructions(type_name: str, role: str, experience: str, difficulty: str) -> str:
    """Generates strict guidelines per interview type."""
    t = type_name.strip().lower()
    if t == "technical":
        return f"""
        Generate STRICTLY TECHNICAL questions specifically relevant to the role '{role}'.
        - Target Experience: {experience}
        - Difficulty Level: {difficulty}
        - Focus ONLY on: programming concepts, language syntax, algorithms, frameworks, database queries, API design, architecture, debugging, and practical engineering scenarios for a {role}.
        - ABSOLUTELY DO NOT include any HR, behavioral, personal background, or general recruitment questions (e.g., DO NOT ask 'Tell me about yourself', 'Why work here', 'Strengths and weaknesses').
        """
    elif t == "hr":
        return f"""
        Generate STRICTLY HR and recruitment-focused interview questions.
        - Target Role: {role} (context only)
        - Target Experience: {experience}
        - Focus ONLY on: career motivation, professional goals, teamwork preferences, communication skills, handling feedback, strengths/weaknesses, compensation expectations, and company culture fit.
        - ABSOLUTELY DO NOT ask any programming, coding, technical syntax, or direct technology definition questions (e.g., DO NOT ask 'What is a decorator', 'What is a list vs tuple', 'What is an API').
        """
    elif t == "behavioral":
        return f"""
        Generate STRICTLY BEHAVIORAL and situational interview questions evaluating past experiences.
        - Target Role: {role} (context only)
        - Target Experience: {experience}
        - Questions MUST use situational formats like: 'Tell me about a time when...', 'Describe a situation where...', 'Give an example of...', 'How did you handle...'.
        - Focus ONLY on evaluating: problem-solving under pressure, conflict resolution, teamwork, accountability, leadership, handling tight deadlines, and learning from mistakes.
        - ABSOLUTELY DO NOT ask direct technical definitions or coding syntax questions (e.g., DO NOT ask 'What is inheritance', 'What is an index').
        """
    else:
        return f"Generate questions suitable for role {role}, experience {experience}, difficulty {difficulty}."


def generate_questions(
    role: str,
    experience: str,
    interview_type: str,
    difficulty: str,
    total_questions: int = 5
) -> List[Dict[str, Any]]:
    """Generates interview questions using Gemini API or MySQL database seed bank."""

    target_type = (interview_type or "Technical").strip()
    result_questions: List[Dict[str, Any]] = []

    # Calculate category distribution if Mixed
    if target_type.lower() == "mixed":
        # Controlled mix: ~40% Technical, ~30% Behavioral, ~30% HR
        tech_count = max(1, int(round(total_questions * 0.4)))
        beh_count = max(1, int(round(total_questions * 0.3)))
        hr_count = max(1, total_questions - tech_count - beh_count)
        
        type_batches = [
            ("Technical", tech_count),
            ("Behavioral", beh_count),
            ("HR", hr_count)
        ]
    else:
        type_batches = [(target_type, total_questions)]

    for batch_type, batch_count in type_batches:
        batch_questions = []

        # 1. Try Gemini API
        if AI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=AI_API_KEY)
                
                type_instructions = get_type_prompt_instructions(batch_type, role, experience, difficulty)
                
                prompt = f"""
                Generate exactly {batch_count} interview questions.

                {type_instructions}

                Return a strict JSON array of objects with keys:
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
                    for q in parsed:
                        q["question_type"] = batch_type
                        q["difficulty"] = difficulty
                    batch_questions.extend(parsed[:batch_count])
            except Exception as e:
                print(f"[AI Generator Warning] Gemini call for {batch_type} skipped ({e}). Using Database Seed Bank.")

        # 2. Database Seed Bank Fallback if batch incomplete
        if len(batch_questions) < batch_count:
            needed = batch_count - len(batch_questions)
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT question_text, topic, ideal_answer, key_concepts, interview_type 
                       FROM question_bank 
                       WHERE (role = %s OR role = 'Software Developer') 
                         AND (interview_type = %s OR %s = 'Mixed')
                         AND (difficulty = %s OR difficulty = 'Medium')""",
                    (role, batch_type, batch_type, difficulty)
                )
                rows = cursor.fetchall()
                conn.close()
                if rows:
                    for r in rows:
                        item = dict(r)
                        item["question_type"] = batch_type
                        item["difficulty"] = difficulty
                        batch_questions.append(item)
            except Exception as db_err:
                print(f"[Database Seed Bank Warning] {db_err}")

        # 3. Dedicated Fallback Arrays if still insufficient
        if len(batch_questions) < batch_count:
            if batch_type.lower() == "hr":
                pool_source = FALLBACK_HR_QUESTIONS
            elif batch_type.lower() == "behavioral":
                pool_source = FALLBACK_BEHAVIORAL_QUESTIONS
            else:
                pool_source = FALLBACK_TECHNICAL_QUESTIONS

            pool = list(pool_source)
            random.shuffle(pool)
            while len(batch_questions) < batch_count:
                item = random.choice(pool).copy()
                item["question_type"] = batch_type
                item["difficulty"] = difficulty
                batch_questions.append(item)

        result_questions.extend(batch_questions[:batch_count])

    # Deduplicate questions
    final_questions = deduplicate_questions(result_questions)

    # Fill if deduplication reduced below total_questions
    if len(final_questions) < total_questions:
        if target_type.lower() == "hr":
            extra_pool = FALLBACK_HR_QUESTIONS
        elif target_type.lower() == "behavioral":
            extra_pool = FALLBACK_BEHAVIORAL_QUESTIONS
        else:
            extra_pool = FALLBACK_TECHNICAL_QUESTIONS

        for item in extra_pool:
            if len(final_questions) >= total_questions:
                break
            candidate = item.copy()
            candidate["question_type"] = target_type
            candidate["difficulty"] = difficulty
            final_questions.append(candidate)

    # Assign order indices
    for idx, q in enumerate(final_questions[:total_questions]):
        q["question_order"] = idx + 1
        if "question_type" not in q:
            q["question_type"] = target_type
        if "difficulty" not in q:
            q["difficulty"] = difficulty

    return final_questions[:total_questions]
