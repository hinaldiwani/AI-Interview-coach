import json
import re
from typing import Dict, Any
from .config import AI_API_KEY

def evaluate_answer(
    question_text: str,
    user_answer: str,
    ideal_answer: str,
    key_concepts: str,
    role: str = "Software Developer",
    difficulty: str = "Medium"
) -> Dict[str, Any]:
    """Evaluates answer using AI API or Local Rule-based Evaluation Engine."""

    cleaned_answer = (user_answer or "").strip()
    if not cleaned_answer or len(cleaned_answer) < 3:
        return {
            "score": 0.0,
            "correctness_score": 0.0,
            "relevance_score": 0.0,
            "technical_score": 0.0,
            "clarity_score": 0.0,
            "completeness_score": 0.0,
            "feedback": "No meaningful answer provided.",
            "strengths": "Attempted the submission.",
            "improvement_suggestion": "Ensure you type or speak a complete answer explaining core concepts.",
            "ideal_answer": ideal_answer,
            "key_concepts": key_concepts
        }

    # 1. Try Gemini API if available
    if AI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=AI_API_KEY)
            prompt = f"""
            Evaluate candidate answer for job interview:

            Question: {question_text}
            User Answer: {cleaned_answer}
            Reference Ideal Answer: {ideal_answer}
            Expected Key Concepts: {key_concepts}

            Evaluate (0-10):
            - correctness_score
            - relevance_score
            - technical_score
            - clarity_score
            - completeness_score
            - overall score (0-10)

            Return strict JSON with keys:
            "score", "correctness_score", "relevance_score", "technical_score", "clarity_score", "completeness_score",
            "feedback", "strengths", "improvement_suggestion", "ideal_answer", "key_concepts"
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
            if isinstance(parsed, dict) and "score" in parsed:
                return parsed
        except Exception as e:
            print(f"[AI Evaluator Warning] API call failed ({e}). Using Local Evaluator.")

    # 2. Local Rule-Based NLP Evaluator
    concepts = [c.strip().lower() for c in key_concepts.replace(",", " ").split() if len(c.strip()) > 2]
    matched = [c for c in concepts if c in cleaned_answer.lower()]
    concept_ratio = len(matched) / max(len(concepts), 1)

    words = cleaned_answer.split()
    word_count = len(words)

    if word_count < 10:
        completeness = 3.5
        clarity = 5.0
    elif word_count < 35:
        completeness = 6.5
        clarity = 7.5
    elif word_count < 80:
        completeness = 8.5
        clarity = 8.5
    else:
        completeness = 9.5
        clarity = 9.0

    correctness = min(10.0, round(4.0 + (concept_ratio * 5.0) + (min(word_count, 50) / 25), 1))
    relevance = min(10.0, round(5.0 + (concept_ratio * 4.5), 1))
    technical = min(10.0, round(3.5 + (concept_ratio * 5.5) + (1.0 if any(term in cleaned_answer.lower() for term in ['example', 'code', 'memory', 'performance', 'function']) else 0.0), 1))

    overall = round((correctness * 0.30 + relevance * 0.20 + technical * 0.25 + completeness * 0.15 + clarity * 0.10), 1)

    if overall >= 7.5:
        strengths = "Clear, accurate explanation showing strong grasp of key technical principles."
        improvement = "Include a small practical code snippet or real-world project example."
        feedback = "Excellent response!"
    elif overall >= 5.0:
        strengths = "Good fundamental attempt covering basic concepts."
        improvement = f"Elaborate further on key terms: {key_concepts}."
        feedback = "Satisfactory answer with room for technical depth."
    else:
        strengths = "Attempted the question."
        improvement = f"Review foundational documentation for {role} and focus on key concepts ({key_concepts})."
        feedback = "Response lacked technical detail."

    return {
        "score": overall,
        "correctness_score": correctness,
        "relevance_score": relevance,
        "technical_score": technical,
        "clarity_score": clarity,
        "completeness_score": completeness,
        "feedback": feedback,
        "strengths": strengths,
        "improvement_suggestion": improvement,
        "ideal_answer": ideal_answer,
        "key_concepts": key_concepts
    }
