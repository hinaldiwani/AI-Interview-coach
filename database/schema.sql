-- =========================================================================
-- AI INTERVIEW COACH - MYSQL DATABASE SCHEMA DEFINITIONS
-- =========================================================================

CREATE DATABASE IF NOT EXISTS ai_interview_coach CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_interview_coach;

-- Table 1: Users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 2: Interviews
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role VARCHAR(100) NOT NULL,
    experience VARCHAR(50) NOT NULL,
    interview_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    total_questions INT NOT NULL DEFAULT 5,
    overall_score FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'in_progress',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    CONSTRAINT fk_interviews_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_interviews_user (user_id),
    INDEX idx_interviews_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 3: Questions
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'Technical',
    difficulty VARCHAR(50) DEFAULT 'Medium',
    question_order INT NOT NULL DEFAULT 1,
    ideal_answer TEXT,
    key_concepts TEXT,
    CONSTRAINT fk_questions_interview FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    INDEX idx_questions_interview (interview_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 4: Answers
CREATE TABLE IF NOT EXISTS answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    question_id INT NOT NULL,
    user_answer TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_answers_interview FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    CONSTRAINT fk_answers_question FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_answers_interview (interview_id),
    INDEX idx_answers_question (question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 5: Evaluations
CREATE TABLE IF NOT EXISTS evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    answer_id INT NOT NULL,
    score FLOAT DEFAULT 0.0,
    correctness_score FLOAT DEFAULT 0.0,
    relevance_score FLOAT DEFAULT 0.0,
    technical_score FLOAT DEFAULT 0.0,
    clarity_score FLOAT DEFAULT 0.0,
    completeness_score FLOAT DEFAULT 0.0,
    feedback TEXT,
    ideal_answer TEXT,
    improvement_suggestion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluations_answer FOREIGN KEY (answer_id) REFERENCES answers(id) ON DELETE CASCADE,
    INDEX idx_evaluations_answer (answer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 6: Interview Results
CREATE TABLE IF NOT EXISTS interview_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    technical_score FLOAT DEFAULT 0.0,
    correctness_score FLOAT DEFAULT 0.0,
    communication_score FLOAT DEFAULT 0.0,
    completeness_score FLOAT DEFAULT 0.0,
    overall_score FLOAT DEFAULT 0.0,
    performance_category VARCHAR(50) DEFAULT 'Pending',
    strengths TEXT,
    weak_areas TEXT,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_results_interview FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    INDEX idx_results_interview (interview_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 7: Question Bank
CREATE TABLE IF NOT EXISTS question_bank (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(100) NOT NULL,
    interview_type VARCHAR(50) NOT NULL DEFAULT 'Technical',
    difficulty VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    topic VARCHAR(100) DEFAULT 'General',
    ideal_answer TEXT NOT NULL,
    key_concepts TEXT NOT NULL,
    INDEX idx_question_bank_role_diff (role, difficulty),
    INDEX idx_question_bank_type (interview_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
