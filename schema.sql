-- AI Interview Coach Database Schema
CREATE DATABASE IF NOT EXISTS ai_interview_coach CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_interview_coach;

-- Table 1: Users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 2: Interviews
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role VARCHAR(100) NOT NULL,
    experience_level VARCHAR(50) NOT NULL,
    interview_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    num_questions INT NOT NULL DEFAULT 5,
    overall_score FLOAT DEFAULT 0.0,
    performance_category VARCHAR(50) DEFAULT 'Pending',
    technical_score FLOAT DEFAULT 0.0,
    correctness_score FLOAT DEFAULT 0.0,
    relevance_score FLOAT DEFAULT 0.0,
    communication_score FLOAT DEFAULT 0.0,
    completeness_score FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_interviews_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 3: Questions
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    question_number INT NOT NULL,
    question_text TEXT NOT NULL,
    topic VARCHAR(100) DEFAULT 'General',
    difficulty VARCHAR(50) DEFAULT 'Medium',
    ideal_answer TEXT,
    key_concepts TEXT,
    CONSTRAINT fk_questions_interview FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 4: Answers
CREATE TABLE IF NOT EXISTS answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    question_id INT NOT NULL,
    user_answer TEXT,
    time_taken_seconds INT DEFAULT 0,
    score FLOAT DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'Evaluated',
    what_went_well TEXT,
    areas_for_improvement TEXT,
    ideal_answer TEXT,
    key_concepts TEXT,
    feedback_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_answers_interview FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    CONSTRAINT fk_answers_question FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 5: Evaluations
CREATE TABLE IF NOT EXISTS evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    answer_id INT NOT NULL,
    correctness_score FLOAT DEFAULT 0.0,
    relevance_score FLOAT DEFAULT 0.0,
    technical_score FLOAT DEFAULT 0.0,
    completeness_score FLOAT DEFAULT 0.0,
    clarity_score FLOAT DEFAULT 0.0,
    confidence_score FLOAT DEFAULT 0.0,
    detailed_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluations_answer FOREIGN KEY (answer_id) REFERENCES answers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 6: Recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    weak_topics_json TEXT,
    strong_topics_json TEXT,
    practice_suggestions_json TEXT,
    recommended_difficulty VARCHAR(50) DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_recommendations_interview FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
