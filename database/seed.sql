-- Pre-populate Seed Question Bank for offline / database-driven fallback mode
USE ai_interview_coach;

INSERT INTO question_bank (role, interview_type, difficulty, question_text, topic, ideal_answer, key_concepts) VALUES
-- Python Developer Questions
('Python Developer', 'Technical', 'Easy', 'What are the main features of Python as a programming language?', 'Python Fundamentals', 'Python is an interpreted, high-level, dynamically typed language with simple syntax, automatic memory management, extensive standard library, and cross-platform support.', 'Interpreted, High-level, Dynamic Typing, Standard Library'),
('Python Developer', 'Technical', 'Easy', 'What is the difference between a list and a tuple in Python?', 'Data Structures', 'Lists are mutable sequences defined using [], whereas tuples are immutable sequences defined using (). Tuples are faster and consume less memory.', 'Mutability, Immutability, Memory Efficiency'),
('Python Developer', 'Technical', 'Medium', 'Explain Python decorators and provide a practical use case.', 'Advanced Python', 'A decorator is a higher-order function that takes another function, extends its functionality without modifying it, and returns the modified function. Used for logging, authentication, and caching.', 'First-class functions, Higher-order functions, Wrappers, @syntax'),
('Python Developer', 'Technical', 'Medium', 'What is the difference between shallow copy and deep copy in Python?', 'Memory Management', 'Shallow copy creates a new object but references nested objects. Deep copy recursively duplicates all nested objects ensuring total independence.', 'Copy module, Object references, Deepcopy'),
('Python Developer', 'Technical', 'Hard', 'Explain the Global Interpreter Lock (GIL) in Python and its impact on multithreading.', 'Concurrency', 'The GIL is a mutex protecting access to Python objects, restricting execution to a single native thread per process in CPython, binding CPU-bound tasks to one core.', 'GIL, CPython, Multiprocessing, AsyncIO'),

-- Java Developer Questions
('Java Developer', 'Technical', 'Easy', 'What are the four core OOP principles in Java?', 'OOP Fundamentals', 'Encapsulation, Inheritance, Polymorphism, and Abstraction.', 'Encapsulation, Inheritance, Polymorphism, Abstraction'),
('Java Developer', 'Technical', 'Medium', 'How does HashMap work internally under Java 8+?', 'Collections', 'HashMap uses an array of bucket nodes with hash coding. Bucket collisions form linked lists; if bucket size exceeds 8, it converts into a Red-Black tree O(log n).', 'Hashcode, Buckets, Red-Black Trees, Collisions'),
('Java Developer', 'Technical', 'Hard', 'Explain the Java Memory Model (JMM) and the volatile keyword.', 'Concurrency', 'JMM defines thread memory interactions. Volatile forces reads/writes directly to main memory and prevents instruction reordering.', 'JMM, Volatile, Visibility, Memory Barriers'),

-- Web Developer Questions
('Web Developer', 'Technical', 'Easy', 'Explain the CSS Box Model and box-sizing property.', 'CSS', 'Consists of content, padding, border, and margin. box-sizing: border-box includes padding and border in element total width.', 'Content, Padding, Border, Margin, Border-box'),
('Web Developer', 'Technical', 'Medium', 'What are JavaScript Closures and how do they preserve lexical scope?', 'JavaScript Core', 'A closure gives an inner function access to an outer function scope even after outer execution completes.', 'Lexical scope, Closure, Data encapsulation'),

-- Full Stack Developer Questions
('Full Stack Developer', 'Technical', 'Medium', 'How does JWT (JSON Web Token) authentication work statelessly?', 'Security & Auth', 'Server returns signed JWT on login; client sends token in Authorization header; server verifies signature without database lookup.', 'Stateless, JWT, Signature, Bearer token'),

-- Data Analyst Questions
('Data Analyst', 'Technical', 'Easy', 'What is the difference between WHERE and HAVING clauses in SQL?', 'SQL Queries', 'WHERE filters individual rows before grouping; HAVING filters aggregated groups after GROUP BY.', 'WHERE, HAVING, GROUP BY, Aggregation'),

-- Data Scientist Questions
('Data Scientist', 'Technical', 'Medium', 'Explain the Bias-Variance Tradeoff and how to prevent overfitting.', 'Machine Learning', 'High bias causes underfitting; high variance causes overfitting. Prevent via regularization L1/L2, cross-validation, and pruning.', 'Bias, Variance, Regularization, Overfitting'),

-- Software Developer Questions
('Software Developer', 'Technical', 'Medium', 'Explain the SOLID principles of Object-Oriented Design.', 'Software Design', 'Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.', 'SOLID, System Design, OOP');
