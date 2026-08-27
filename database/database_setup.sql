-- =========================================================================
-- AI INTERVIEW COACH - COMPLETE MYSQL DATABASE SETUP SCRIPT
-- Directly executable from MySQL Command Line Client, MySQL Workbench, or phpMyAdmin
-- Usage in MySQL CLI: SOURCE C:/FULL/PATH/TO/database/database_setup.sql;
-- =========================================================================

-- 1. Create Database
CREATE DATABASE IF NOT EXISTS ai_interview_coach CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Select Database
USE ai_interview_coach;

-- =========================================================================
-- 3. CREATE TABLES WITH PRIMARY KEYS, FOREIGN KEYS, INDEXES & CONSTRAINTS
-- =========================================================================

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
    termination_reason VARCHAR(50) DEFAULT NULL,
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

-- Table 7: Question Bank (Pre-populated Seed Questions)
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

-- =========================================================================
-- 4. INSERT SAMPLE INTERVIEW QUESTIONS (7 ROLES: EASY, MEDIUM, HARD & TYPES)
-- =========================================================================

TRUNCATE TABLE question_bank;

INSERT INTO question_bank (role, interview_type, difficulty, question_text, topic, ideal_answer, key_concepts) VALUES
('Python Developer', 'Technical', 'Easy', 'What are the main features of Python as a programming language?', 'Python Fundamentals', 'Python is an interpreted, high-level, dynamically typed language with simple syntax, automatic memory management via garbage collection, an extensive standard library, and cross-platform support.', 'Interpreted, High-level, Dynamic Typing, Standard Library, Garbage Collection'),
('Python Developer', 'Technical', 'Easy', 'What is the difference between a list and a tuple in Python?', 'Data Structures', 'Lists are mutable sequences defined using [], whereas tuples are immutable sequences defined using (). Tuples are faster, consume less memory, and can be used as dictionary keys if elements are hashable.', 'Mutability, Immutability, Memory Efficiency, Hashability'),
('Python Developer', 'Technical', 'Medium', 'Explain Python decorators and provide a practical use case.', 'Advanced Python', 'A decorator is a higher-order function that takes another function as an argument, extends its behavior without modifying original source code, and returns the modified function. Practical uses include logging, authentication, rate limiting, and caching.', 'First-class functions, Higher-order functions, Wrappers, @syntax, Closures'),
('Python Developer', 'Technical', 'Medium', 'What is the difference between shallow copy and deep copy in Python?', 'Memory Management', 'A shallow copy creates a new compound object but inserts references to original objects. A deep copy recursively duplicates all nested objects, ensuring complete independence from the original structure.', 'Copy module, Object references, Shallow vs Deep, Recursion'),
('Python Developer', 'Technical', 'Hard', 'Explain the Global Interpreter Lock (GIL) in Python and its impact on multithreading.', 'Concurrency', 'The GIL is a mutex in CPython that prevents multiple native threads from executing Python bytecodes concurrently on multi-core CPUs. CPU-bound tasks do not benefit from multithreading - multiprocessing or asyncio must be used instead.', 'GIL, CPython, Threading vs Multiprocessing, CPU-bound vs IO-bound, Mutex'),
('Python Developer', 'Technical', 'Hard', 'How does Python manage memory internally using Reference Counting and Generational Garbage Collection?', 'Memory Internals', 'Python tracks object references using a counter. When reference count drops to 0, memory is freed immediately. Cyclic references that cannot be freed by reference counting are detected and collected by a 3-generation cycle detector.', 'Reference Counting, Cyclic References, Generational GC, PyObject, Memory Allocation'),
('Java Developer', 'Technical', 'Easy', 'What are the four core Object-Oriented Programming (OOP) principles in Java?', 'OOP Fundamentals', 'Encapsulation (bundling data and methods), Inheritance (reusing attributes/methods from parent class), Polymorphism (overloading/overriding methods), and Abstraction (hiding implementation details using abstract classes/interfaces).', 'Encapsulation, Inheritance, Polymorphism, Abstraction'),
('Java Developer', 'Technical', 'Easy', 'What is the difference between the == operator and the .equals() method in Java?', 'Core Java', 'The == operator compares primitive values or reference memory addresses (checking if two objects point to the same memory location). The .equals() method checks logical value equality between objects when overridden.', 'Primitive vs Reference, Memory Address, Value Equality, Method Overriding'),
('Java Developer', 'Technical', 'Medium', 'How does HashMap work internally in Java 8 and above?', 'Collections Framework', 'HashMap uses an array of bucket nodes based on hash key calculation. When bucket collisions occur, items form a linked list. In Java 8+, if a bucket list length exceeds 8, it converts into a Red-Black Tree O(log n) for faster lookup.', 'Hashcode, Buckets, Red-Black Trees, Collisions, Rehash, O(log n)'),
('Java Developer', 'Technical', 'Medium', 'Explain the difference between an Abstract Class and an Interface in Java.', 'Object-Oriented Design', 'An abstract class can have instance fields, constructors, and method implementations. An interface defines contracts - since Java 8 it supports default/static methods and since Java 9 private methods. A class can extend only one class but implement multiple interfaces.', 'Abstract Class, Interface, Multiple Inheritance, Default Methods, Contract'),
('Java Developer', 'Technical', 'Hard', 'Explain the Java Memory Model (JMM), thread visibility, and the volatile keyword.', 'Concurrency & JMM', 'JMM defines how threads interact through memory. The volatile keyword forces reads and writes directly to main memory (preventing CPU L1/L2 cache stale reads) and establishes a happens-before relationship preventing instruction reordering.', 'JMM, Volatile, Memory Barrier, Instruction Reordering, Thread Visibility, Cache Coherence'),
('Java Developer', 'Technical', 'Hard', 'How does the G1 Garbage Collector work and how do you diagnose memory leaks in Java applications?', 'JVM Tuning', 'G1 GC divides JVM heap into equal-sized regions and performs incremental collection targeting regions with maximum garbage. Memory leaks in Java occur when unreferenced objects remain reachable through static fields or thread pools, diagnosed using heap dumps and Profilers.', 'G1 GC, JVM Heap Regions, Heap Dump, Memory Leak, Static References, Garbage Collector'),
('Web Developer', 'Technical', 'Easy', 'Explain the CSS Box Model and the box-sizing property.', 'CSS & Layout', 'The CSS Box Model consists of content, padding, border, and margin. By default (content-box), width excludes padding and border. Setting box-sizing: border-box includes padding and border within the element total width and height.', 'Content, Padding, Border, Margin, box-sizing, border-box'),
('Web Developer', 'Technical', 'Easy', 'What is the difference between HTML semantic elements and non-semantic elements?', 'HTML5', 'Semantic elements (such as header, nav, article, section, footer) clearly describe their meaning to developer, browser, and search engines. Non-semantic elements (like div, span) convey no information about contents.', 'Semantic HTML, Accessibility, SEO, DOM Structure'),
('Web Developer', 'Technical', 'Medium', 'What are JavaScript Closures and how do they preserve lexical scope?', 'JavaScript Core', 'A closure is a function bundled together with references to its surrounding lexical environment. It allows an inner function to retain access to variables declared in its outer scope even after the outer function has finished executing.', 'Lexical Scope, Closure, Variable Lifetime, Encapsulation, State Retention'),
('Web Developer', 'Technical', 'Medium', 'Explain the JavaScript Event Loop, Microtasks, and Macrotasks.', 'Asynchronous JS', 'JS executes synchronous code on Call Stack. Async callbacks enter task queues: Microtask queue (Promises, queueMicrotask) has higher priority and drains completely before Event Loop processes the next Macrotask (setTimeout, setInterval, I/O).', 'Call Stack, Event Loop, Microtask Queue, Macrotask Queue, Promises, Asynchronous'),
('Web Developer', 'Technical', 'Hard', 'Explain Critical Rendering Path (CRP) optimization and how to minimize layout reflows and repaints.', 'Performance Optimization', 'CRP is the sequence of steps browser takes to convert HTML, CSS, JS into pixels on screen. Minimize reflows by avoiding inline style reads in loops, using transform/opacity for animations, and CSS containment.', 'DOM, CSSOM, Render Tree, Reflow, Repaint, Hardware Acceleration, CRP'),
('Web Developer', 'Technical', 'Hard', 'How do Service Workers, Cache API, and Web App Manifest enable Progressive Web Apps (PWAs)?', 'Modern Web Architecture', 'Service Workers act as client-side proxy scripts running background worker threads to intercept network requests and serve cached assets offline via Cache API. Manifest provides app installation metadata.', 'Service Worker, Cache API, Offline Capability, Manifest, PWA, Background Sync'),
('Full Stack Developer', 'Technical', 'Easy', 'What is the difference between Client-Side Rendering (CSR) and Server-Side Rendering (SSR)?', 'Architecture', 'In CSR, browser downloads minimal HTML and JavaScript builds UI dynamically on client. In SSR, server generates ready-to-render HTML for each request, offering better initial load speed and SEO.', 'CSR, SSR, SEO, Initial Load Time, Hydration'),
('Full Stack Developer', 'Technical', 'Easy', 'What are standard HTTP methods (GET, POST, PUT, DELETE, PATCH) and REST API conventions?', 'Web APIs', 'GET retrieves resources, POST creates new resources, PUT replaces existing resources, DELETE removes resources, and PATCH performs partial updates. RESTful conventions use noun URIs and proper HTTP status codes.', 'HTTP Verbs, RESTful Design, Idempotency, Status Codes'),
('Full Stack Developer', 'Technical', 'Medium', 'How does JWT (JSON Web Token) authentication work statelessly across frontend and backend?', 'Security & Auth', 'Upon successful login, server returns a signed JWT containing header, payload, and signature. Client attaches token to Authorization: Bearer header. Server verifies token cryptographic signature statelessly without querying database sessions.', 'JWT, Bearer Token, Cryptographic Signature, Stateless Auth, HTTP Headers'),
('Full Stack Developer', 'Technical', 'Medium', 'What is Cross-Origin Resource Sharing (CORS) and how do CORS preflight requests work?', 'Web Security', 'CORS is a security mechanism enforced by browsers that restricts cross-origin HTTP requests. For non-simple requests, browser sends an OPTIONS preflight request to verify server Access-Control-Allow headers before sending actual request.', 'CORS, Same-Origin Policy, OPTIONS Preflight, Access-Control Headers'),
('Full Stack Developer', 'Technical', 'Hard', 'Design a real-time notification system supporting concurrent WebSocket connections with Redis Pub/Sub.', 'Distributed Systems', 'Frontend maintains persistent WebSocket connection to gateway nodes. Backend services publish events to Redis Pub/Sub channels. Gateway nodes subscribe to user channels and push real-time payloads via WebSockets with fallback to SSE/Polling.', 'WebSockets, Redis Pub/Sub, System Design, Horizontal Scaling, Real-time Push'),
('Full Stack Developer', 'Technical', 'Hard', 'Explain database indexing strategies and query optimization techniques for high-traffic full-stack apps.', 'Database Performance', 'Optimizations include B-Tree composite indexes matching query WHERE/ORDER BY filters, avoiding SELECT *, implementing database connection pooling, query caching (Redis), read replicas, and partitioning large tables.', 'B-Tree Index, Composite Index, Connection Pooling, Query Plan, EXPLAIN, Caching'),
('Data Analyst', 'Technical', 'Easy', 'What is the difference between WHERE and HAVING clauses in SQL?', 'SQL Queries', 'WHERE filters individual records before any grouping or aggregation takes place. HAVING filters aggregated data groups after GROUP BY clause execution.', 'WHERE, HAVING, GROUP BY, Aggregation, SQL Order of Execution'),
('Data Analyst', 'Technical', 'Easy', 'Explain the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN in SQL.', 'Relational Data', 'INNER JOIN returns matching rows in both tables. LEFT JOIN returns all rows from left table and matching rows from right table (filling NULLs). RIGHT JOIN returns all rows from right table and matching from left.', 'INNER JOIN, LEFT JOIN, RIGHT JOIN, NULL Values, Table Relationships'),
('Data Analyst', 'Technical', 'Medium', 'Explain SQL Window Functions such as ROW_NUMBER(), RANK(), and DENSE_RANK().', 'Advanced SQL', 'Window functions perform calculations across related set of table rows without collapsing rows. ROW_NUMBER assigns sequential unique integers, RANK leaves gaps after duplicate ranks, and DENSE_RANK assigns consecutive numbers without gaps.', 'Window Functions, OVER(PARTITION BY), ROW_NUMBER, RANK, DENSE_RANK'),
('Data Analyst', 'Technical', 'Medium', 'How do you handle missing values and duplicate records during data cleaning in Python or SQL?', 'Data Cleaning', 'In Python Pandas, drop duplicates with drop_duplicates(), impute missing values with fillna() (mean/median/mode), or dropna(). In SQL, use DISTINCT, GROUP BY, or COALESCE() to handle NULLs.', 'Data Cleaning, Pandas, Missing Values, Imputation, Duplicates, COALESCE'),
('Data Analyst', 'Technical', 'Hard', 'How would you design an ETL data pipeline to process daily sales log files into a Data Warehouse?', 'Data Engineering', 'Extract log data via batch ingestion scripts, Transform data by validating schema, deduplicating, and normalizing tables, and Load data into dimensional star/snowflake schemas in Data Warehouse using automated schedulers.', 'ETL Pipeline, Data Warehouse, Star Schema, Batch Processing, Data Validation'),
('Data Analyst', 'Technical', 'Hard', 'Explain cohort analysis and customer retention rate calculation using complex SQL queries.', 'Business Analytics', 'Cohort analysis groups users by starting date/event and tracks behavior over time. SQL joins user signup cohort dates with activity logs, calculating retention percentage = (Active Users in Period N / Initial Cohort Count) * 100.', 'Cohort Analysis, Customer Retention, Time-Series SQL, Business Metrics, Retention Rate'),
('Data Scientist', 'Technical', 'Easy', 'What is the difference between Supervised and Unsupervised Machine Learning?', 'ML Fundamentals', 'Supervised learning trains models on labeled datasets with target answers (e.g. Classification, Regression). Unsupervised learning discovers hidden patterns or clusters in unlabeled data (e.g. K-Means, PCA).', 'Supervised, Unsupervised, Classification, Regression, Clustering'),
('Data Scientist', 'Technical', 'Easy', 'What are Precision, Recall, and F1-Score, and when would you prioritize Recall over Precision?', 'Model Evaluation', 'Precision measures true positives out of predicted positives. Recall measures true positives out of actual positives. F1-Score is harmonic mean of both. Prioritize Recall in medical diagnosis or fraud detection where missing a positive case is costly.', 'Precision, Recall, F1-Score, Confusion Matrix, Medical Diagnosis'),
('Data Scientist', 'Technical', 'Medium', 'Explain the Bias-Variance Tradeoff and techniques to prevent model overfitting.', 'Model Generalization', 'High bias causes underfitting (over-simple model) - high variance causes overfitting (memorizing training noise). Prevent overfitting using L1/L2 regularization, cross-validation, dropout, early stopping, and ensemble methods.', 'Bias, Variance, Overfitting, Underfitting, L1/L2 Regularization, Cross-Validation'),
('Data Scientist', 'Technical', 'Medium', 'How does a Random Forest classifier work and how does it differ from Gradient Boosting?', 'Ensemble Methods', 'Random Forest uses Bagging (bootstrap aggregating) to build independent decision trees in parallel and averages results. Gradient Boosting builds sequential decision trees sequentially, where each tree minimizes residual errors of previous trees.', 'Random Forest, Gradient Boosting, Bagging, Boosting, Decision Trees, Ensemble'),
('Data Scientist', 'Technical', 'Hard', 'Explain the Transformer architecture, Self-Attention mechanism, and Multi-Head Attention in LLMs.', 'Deep Learning & NLP', 'Transformers process sequences in parallel using Query, Key, Value vector projections. Self-Attention computes scaled dot-product attention scores measuring relationships between all tokens. Multi-Head Attention runs multiple attention heads.', 'Transformer, Self-Attention, Multi-Head Attention, QKV Vectors, Positional Encoding, LLM'),
('Data Scientist', 'Technical', 'Hard', 'How do you address severe class imbalance in machine learning models using SMOTE and cost-sensitive learning?', 'Imbalanced Learning', 'Address imbalance by resampling using SMOTE (Synthetic Minority Over-sampling Technique) to generate synthetic samples, adjusting decision thresholds, or using cost-sensitive learning algorithms that penalize minority class errors heavily.', 'Class Imbalance, SMOTE, Synthetic Sampling, Cost-Sensitive Learning, Focal Loss'),
('Software Developer', 'Technical', 'Easy', 'What is the difference between compiled languages and interpreted languages?', 'CS Fundamentals', 'Compiled languages (C, C++, Rust) translate source code directly into machine code prior to execution. Interpreted languages (Python, JavaScript) translate code line-by-line during runtime via an interpreter.', 'Compiled vs Interpreted, Bytecode, Machine Code, Compiler, JIT'),
('Software Developer', 'Technical', 'Easy', 'Explain Git branching strategies, merging, rebasing, and merge conflict resolution.', 'Version Control', 'Git branches isolate feature development. Merging combines branch history with a merge commit. Rebasing re-applies commits on top of another base tip for a linear history. Conflicts are resolved manually by choosing target lines in code.', 'Git, Branching, Merge vs Rebase, Merge Conflicts, Commit History'),
('Software Developer', 'Technical', 'Medium', 'Explain the SOLID principles of Object-Oriented Software Design.', 'Software Architecture', 'Single Responsibility, Open/Closed (open for extension, closed for modification), Liskov Substitution, Interface Segregation, and Dependency Inversion (depend on abstractions, not concretions).', 'SOLID, Single Responsibility, Open-Closed, Liskov, Interface Segregation, Dependency Inversion'),
('Software Developer', 'Technical', 'Medium', 'What is the difference between a Process and a Thread in Operating Systems?', 'Operating Systems', 'A Process is an independent executing program with its own dedicated memory space. A Thread is an execution unit within a process that shares memory and resources with other threads of the same process, having lower context switching overhead.', 'Process, Thread, Shared Memory, Context Switching, OS Scheduling'),
('Software Developer', 'Technical', 'Hard', 'Explain the CAP Theorem and how Eventual Consistency is achieved in distributed databases.', 'Distributed Systems', 'CAP Theorem states a distributed system can simultaneously provide at most two of Consistency, Availability, and Partition Tolerance. Eventual consistency guarantees that if no new updates occur, all replicas will eventually return the latest data using Vector Clocks.', 'CAP Theorem, Consistency, Availability, Partition Tolerance, Eventual Consistency, Vector Clocks'),
('Software Developer', 'Technical', 'Hard', 'How do you design a thread-safe Rate Limiter algorithm (Token Bucket vs Leaky Bucket) for microservices?', 'System Design', 'Token Bucket adds tokens to a bucket at fixed rate - requests consume tokens if available. Leaky Bucket queues requests and releases them at a steady rate. Implement using Redis atomic scripts (Lua) or atomic counters for high performance.', 'Rate Limiter, Token Bucket, Leaky Bucket, Redis Lua, Concurrency, Microservices'),
('Software Developer', 'HR', 'Easy', 'Tell me about yourself and your background in software engineering.', 'Introduction', 'Candidate should summarize education, core technical skills, key project achievements, and career passion clearly in 1-2 minutes.', 'Communication, Self-Introduction, Career Goals'),
('Web Developer', 'HR', 'Easy', 'Why do you want to work at our company as a Web Developer?', 'Company Fit', 'Candidate should mention specific products/culture of company, alignment of skill set, and desire to build user-centric applications.', 'Company Knowledge, Motivation, Fit'),
('Python Developer', 'HR', 'Medium', 'What are your greatest technical strengths and what areas are you actively working to improve?', 'Self Awareness', 'Candidate should highlight relevant strengths with examples (e.g. backend design) and discuss a real growth area with concrete steps taken to improve.', 'Self Reflection, Strengths, Continuous Learning'),
('Data Analyst', 'HR', 'Medium', 'Where do you see yourself in 3 to 5 years as a Data Professional?', 'Career Vision', 'Candidate should describe realistic career growth (e.g. Senior Data Analyst / Lead Analyst), mastering advanced analytics tools, and driving business impact.', 'Ambition, Career Growth, Vision'),
('Data Scientist', 'HR', 'Hard', 'Describe a situation where your technical recommendations were challenged by executive management. How did you handle it?', 'Executive Presence', 'Candidate should explain taking a data-driven approach, translating complex ML concepts into business ROI, listening actively, and reaching consensus.', 'Stakeholder Management, Communication, Business Impact'),
('Software Developer', 'Behavioral', 'Easy', 'Describe a time when you had to adapt quickly to a major requirement change mid-project.', 'Adaptability', 'Candidate should use STAR method: describe situation, task, action taken to refactor/reprioritize work, and positive outcome achieved.', 'STAR Method, Flexibility, Problem Solving'),
('Full Stack Developer', 'Behavioral', 'Medium', 'Describe a time when you experienced a critical production bug. How did you diagnose and resolve it under pressure?', 'Incident Management', 'Candidate should describe staying calm, isolating root cause via telemetry logs, deploying quick hotfix, performing post-mortem, and adding automated tests.', 'Debugging, Incident Response, Root Cause Analysis'),
('Java Developer', 'Behavioral', 'Medium', 'Tell me about a time you had a technical disagreement with a teammate. How did you resolve it?', 'Conflict Resolution', 'Candidate should highlight respectful debate, reviewing benchmark metrics or design trade-offs objectively, compromising, and committing to team goal.', 'Teamwork, Respect, Technical Debate'),
('Python Developer', 'Behavioral', 'Hard', 'Describe a complex project that missed a deadline or failed to meet expectations. What did you learn?', 'Accountability', 'Candidate should take ownership without blaming others, analyze root causes (scope creep, estimation errors), and detail how they altered future workflows.', 'Ownership, Retrospective, Growth Mindset'),
('Web Developer', 'Mixed', 'Medium', 'How do you balance writing clean, maintainable code with meeting tight product release deadlines?', 'Engineering Practices', 'Candidate should discuss MVP prioritization, test coverage for core paths, avoiding premature optimization, and scheduling tech debt refactoring.', 'Trade-offs, Clean Code, Agile Delivery'),
('Full Stack Developer', 'Mixed', 'Hard', 'Walk me through how you would onboard onto a legacy 500,000 line full-stack codebase with minimal documentation.', 'Codebase Navigation', 'Candidate should discuss running app locally, exploring high-level directory structure, reading core DB schemas and end-to-end tests, talking to senior devs, and updating docs as they learn.', 'Legacy Code, Systems Thinking, Onboarding');
