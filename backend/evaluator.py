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
    difficulty: str = "Medium",
    question_type: str = "Technical"
) -> Dict[str, Any]:
    """Evaluates candidate response with category-aware scoring (Technical, HR, Behavioral)."""

    q_type = (question_type or "Technical").strip().title()
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
            "strengths": "Attempted submission.",
            "improvement_suggestion": f"Provide a complete response addressing the {q_type.lower()} question.",
            "ideal_answer": ideal_answer,
            "key_concepts": key_concepts
        }

    # 1. Try Gemini API if available
    if AI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=AI_API_KEY)

            if q_type == "Hr":
                eval_criteria = """
                Evaluate this HR / Recruitment interview response.
                Focus evaluation on:
                - Communication & Professionalism
                - Clarity & Motivation
                - Alignment with career goals & company culture
                - Self-awareness and relevance
                Do NOT penalize for lack of technical code syntax.
                """
            elif q_type == "Behavioral":
                eval_criteria = """
                Evaluate this Behavioral / Situational interview response.
                Focus evaluation on:
                - STAR method structure (Situation, Task, Action taken, Result achieved)
                - Problem-solving skills and teamwork under pressure
                - Decision-making, accountability, and practical learning from past experience
                Do NOT penalize for lack of code syntax.
                """
            else:
                eval_criteria = """
                Evaluate this Technical interview response.
                Focus evaluation on:
                - Technical accuracy and depth of explanation
                - Use of relevant language/domain terminology
                - Correctness of concepts and practical engineering awareness
                """

            prompt = f"""
            Evaluate the following candidate response for a {role} position ({difficulty} difficulty):

            Question Type: {q_type}
            Question: {question_text}
            Candidate Answer: {cleaned_answer}
            Reference Ideal Answer: {ideal_answer}
            Key Concepts / Criteria: {key_concepts}

            {eval_criteria}

            Provide ratings from 0.0 to 10.0 for:
            - correctness_score
            - relevance_score
            - technical_score
            - clarity_score
            - completeness_score
            - overall score (0.0 to 10.0)

            Return strict JSON with keys:
            "score", "correctness_score", "relevance_score", "technical_score", "clarity_score", "completeness_score",
            "feedback", "strengths", "improvement_suggestion", "ideal_answer", "key_concepts"
            Do NOT return markdown.
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
            print(f"[AI Evaluator Warning] API call failed ({e}). Using Category-Aware Local Evaluator.")

    # 2. Local Rule-Based NLP Evaluator
    concepts = [c.strip().lower() for c in key_concepts.replace(",", " ").split() if len(c.strip()) > 2]
    matched = [c for c in concepts if c in cleaned_answer.lower()]
    concept_ratio = len(matched) / max(len(concepts), 1)

    words = cleaned_answer.split()
    word_count = len(words)

    if word_count < 12:
        completeness = 4.0
        clarity = 5.5
    elif word_count < 35:
        completeness = 7.0
        clarity = 7.5
    elif word_count < 80:
        completeness = 8.5
        clarity = 8.5
    else:
        completeness = 9.5
        clarity = 9.0

    if q_type == "Hr":
        relevance = min(10.0, round(6.0 + (min(word_count, 60) / 20), 1))
        correctness = min(10.0, round(6.5 + (concept_ratio * 3.5), 1))
        technical = min(10.0, round(7.0 + (concept_ratio * 3.0), 1))
        overall = round((clarity * 0.35 + relevance * 0.30 + completeness * 0.20 + correctness * 0.15), 1)
        
        if overall >= 7.5:
            strengths = "Articulate, professional response demonstrating strong motivation and team fit."
            improvement = "Elaborate further with specific professional accomplishments."
            feedback = "Excellent HR interview answer!"
        else:
            strengths = "Clear response."
            improvement = "Structure your answer to highlight career motivation and core interpersonal strengths."
            feedback = "Satisfactory answer with room for detail."

    elif q_type == "Behavioral":
        star_terms = ['situation', 'task', 'action', 'result', 'led', 'decided', 'learned', 'outcome', 'resolved', 'challenge']
        star_matches = sum(1 for t in star_terms if t in cleaned_answer.lower())
        star_bonus = min(2.5, star_matches * 0.6)

        relevance = min(10.0, round(5.5 + star_bonus + (concept_ratio * 2.5), 1))
        correctness = min(10.0, round(6.0 + star_bonus, 1))
        technical = min(10.0, round(6.0 + (concept_ratio * 3.0), 1))
        overall = round((clarity * 0.30 + relevance * 0.30 + completeness * 0.25 + correctness * 0.15), 1)

        if overall >= 7.5:
            strengths = "Great situational narrative using key STAR elements (Situation, Task, Action, Result)."
            improvement = "Conclude with quantified impact or concrete lessons learned."
            feedback = "Strong behavioral response!"
        else:
            strengths = "Good description of past experience."
            improvement = "Use the STAR method: describe the Situation, Task, Action taken, and final Result."
            feedback = "Satisfactory response. Structure your story clearly."

    else: # Technical
        correctness = min(10.0, round(4.0 + (concept_ratio * 5.0) + (min(word_count, 50) / 25), 1))
        relevance = min(10.0, round(5.0 + (concept_ratio * 4.5), 1))
        technical = min(10.0, round(3.5 + (concept_ratio * 5.5) + (1.0 if any(t in cleaned_answer.lower() for t in ['example', 'code', 'memory', 'performance', 'function', 'class']) else 0.0), 1))
        overall = round((correctness * 0.30 + relevance * 0.20 + technical * 0.25 + completeness * 0.15 + clarity * 0.10), 1)

        if overall >= 7.5:
            strengths = "Clear, accurate explanation showing strong technical depth."
            improvement = "Provide a small code snippet or real-world architectural trade-off example."
            feedback = "Excellent technical response!"
        else:
            strengths = "Good fundamental attempt covering basic concepts."
            improvement = f"Review core documentation for {role} and elaborate on: {key_concepts}."
            feedback = "Satisfactory answer with room for technical depth."

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
