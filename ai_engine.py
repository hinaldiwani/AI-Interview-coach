import os
import json
import random
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Comprehensive Local Question Bank covering all Roles, Experience Levels, Types & Difficulties
QUESTION_BANK = {
    "Python Developer": {
        "Technical": {
            "Easy": [
                {
                    "question": "What are the main features of Python as a programming language?",
                    "topic": "Python Fundamentals",
                    "ideal_answer": "Python is an interpreted, high-level, dynamically typed language that supports object-oriented, procedural, and functional programming. Key features include clean syntax, automatic memory management (garbage collection), extensive standard library, dynamic typing, and cross-platform compatibility.",
                    "key_concepts": "Interpreted, High-level, Dynamic Typing, Garbage Collection, Standard Library"
                },
                {
                    "question": "What is the difference between a list and a tuple in Python?",
                    "topic": "Data Structures",
                    "ideal_answer": "Lists are mutable sequences defined using square brackets [], meaning their elements can be modified, added, or removed. Tuples are immutable sequences defined using parentheses (), meaning once created, their elements cannot be changed. Tuples are faster and consume less memory.",
                    "key_concepts": "Mutability, Immutability, Memory Efficiency, Performance"
                },
                {
                    "question": "What is the difference between `==` and `is` operators in Python?",
                    "topic": "Operators & Memory",
                    "ideal_answer": "The `==` operator checks for value equality (whether the contents of two objects are identical), whereas the `is` operator checks for identity equality (whether two variables refer to the exact same object in memory address).",
                    "key_concepts": "Value Equality, Identity Equality, Memory References, Object ID"
                },
                {
                    "question": "Explain how exception handling works in Python using try, except, else, and finally.",
                    "topic": "Error Handling",
                    "ideal_answer": "Exceptions are handled using try-except blocks. Code that might raise an error goes inside `try`. The `except` block catches and handles specific exceptions. The `else` block runs if no exception occurred, and `finally` runs unconditionally (often used for cleanup like closing files or connections).",
                    "key_concepts": "Try-Except, Exception Hierarchy, Cleanup, Else and Finally blocks"
                },
                {
                    "question": "What are Python list comprehensions and how do they differ from traditional loops?",
                    "topic": "Pythonic Syntax",
                    "ideal_answer": "List comprehensions offer a concise syntax to create lists based on existing iterables, formatted as `[expression for item in iterable if condition]`. They are generally faster and more readable than traditional `for` loops for simple mapping and filtering operations.",
                    "key_concepts": "Syntactic Sugar, Iterables, Mapping & Filtering, Performance"
                }
            ],
            "Medium": [
                {
                    "question": "Explain Python decorators and provide a practical use case.",
                    "topic": "Advanced Python",
                    "ideal_answer": "A decorator is a function that takes another function as an argument, extends its behavior without modifying it directly, and returns a new function. Practical use cases include logging execution time, authentication checks, caching/memoization, and input validation.",
                    "key_concepts": "First-class functions, Higher-order functions, Wrappers, @syntax, Logging/Auth"
                },
                {
                    "question": "What are Python generators and iterators? How does `yield` differ from `return`?",
                    "topic": "Memory & Concurrency",
                    "ideal_answer": "Iterators implement `__iter__()` and `__next__()` methods. Generators are simple functions that yield values one at a time using the `yield` keyword. Unlike `return`, which terminates execution and returns a single value, `yield` pauses the function state and resumes upon the next call, producing high memory efficiency for large streams.",
                    "key_concepts": "Lazy Evaluation, Yield Keyword, Memory Efficiency, State Preservation"
                },
                {
                    "question": "How does Python handle memory management and Garbage Collection?",
                    "topic": "Internal Architecture",
                    "ideal_answer": "Python manages memory automatically using Reference Counting and a Generational Garbage Collector. Every object retains a reference count. When it drops to zero, memory is freed immediately. For cyclic references (e.g. A references B and B references A), Python's cyclic garbage collector checks generations 0, 1, and 2 periodically.",
                    "key_concepts": "Reference Counting, Generational GC, Cyclic References, Memory Management"
                },
                {
                    "question": "Explain the Global Interpreter Lock (GIL) in Python and its impact on multithreading.",
                    "topic": "Concurrency",
                    "ideal_answer": "The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at the same time in CPython. This means multithreaded Python code is bound to a single CPU core for CPU-bound tasks. For concurrency, `multiprocessing` or `asyncio` is preferred.",
                    "key_concepts": "GIL, CPython, CPU-bound vs IO-bound, Multiprocessing, AsyncIO"
                },
                {
                    "question": "What is the difference between shallow copy and deep copy in Python?",
                    "topic": "Data Structures",
                    "ideal_answer": "A shallow copy (`copy.copy()`) creates a new object but inserts references to the objects contained in the original. A deep copy (`copy.deepcopy()`) creates a new object and recursively copies all nested objects inside it, ensuring complete independence from the original object structure.",
                    "key_concepts": "Copy Module, Nested Structures, Object References, Independence"
                }
            ],
            "Hard": [
                {
                    "question": "How do Python Metaclasses work and when should you use them?",
                    "topic": "Metaprogramming",
                    "ideal_answer": "A metaclass is a 'class of a class'. Just as objects are instances of classes, classes are instances of metaclasses (default is `type`). Metaclasses allow customization of class creation behavior, validation of class attributes, registering classes automatically, and implementing singleton patterns at definition time.",
                    "key_concepts": "Type, Metaclass, Class Creation, __new__ vs __init__, Framework Design"
                },
                {
                    "question": "Explain Python's `asyncio` event loop architecture and how cooperative multitasking functions under the hood.",
                    "topic": "Asynchronous Programming",
                    "ideal_answer": "Asyncio uses a single-threaded event loop to execute coroutines. Coroutines yield control back to the event loop using `await` when encountering non-blocking I/O operations (sockets, files). The loop manages task queues, handles I/O notifications via OS selectors (epoll/kqueue), and resumes coroutines when data is ready.",
                    "key_concepts": "Event Loop, Coroutines, Non-blocking I/O, Epoll/Kqueue, Tasks & Futures"
                },
                {
                    "question": "Analyze Python's Method Resolution Order (MRO) and C3 Linearization algorithm in multiple inheritance.",
                    "topic": "OOP Architecture",
                    "ideal_answer": "MRO defines the order in which Python looks for methods in a class hierarchy with multiple inheritance. Python 3 uses the C3 Linearization algorithm, which guarantees monotonic class lookup, respects local precedence order, and prevents inconsistent attribute resolution across complex inheritance trees. Inspected via `ClassName.mro()`.",
                    "key_concepts": "Multiple Inheritance, C3 Linearization, Super(), Precedence Order"
                }
            ]
        }
    },
    "Java Developer": {
        "Technical": {
            "Easy": [
                {
                    "question": "What are the core OOP principles in Java?",
                    "topic": "OOP Fundamentals",
                    "ideal_answer": "The four main OOP principles in Java are Encapsulation (hiding implementation details using access modifiers), Inheritance (reusing code via parent-child classes), Polymorphism (method overloading and overriding), and Abstraction (exposing only essential features via abstract classes and interfaces).",
                    "key_concepts": "Encapsulation, Inheritance, Polymorphism, Abstraction"
                },
                {
                    "question": "What is the difference between JDK, JRE, and JVM?",
                    "topic": "Java Architecture",
                    "ideal_answer": "JDK (Java Development Kit) contains tools needed to develop Java programs including javac compiler. JRE (Java Runtime Environment) provides libraries and the environment to execute Java programs. JVM (Java Virtual Machine) is the abstract execution engine that executes bytecode on specific operating systems.",
                    "key_concepts": "JDK, JRE, JVM, Bytecode Execution, Platform Independence"
                },
                {
                    "question": "What is the difference between String, StringBuilder, and StringBuffer in Java?",
                    "topic": "Memory & Strings",
                    "ideal_answer": "String is immutable and stored in the String Constant Pool. StringBuilder is mutable, non-thread-safe, and provides fast string modifications in single-threaded environments. StringBuffer is mutable and thread-safe because its methods are synchronized, though slightly slower.",
                    "key_concepts": "Immutability, Thread-safety, Synchronization, Memory Efficiency"
                }
            ],
            "Medium": [
                {
                    "question": "How does the Java HashMap work internally under Java 8+?",
                    "topic": "Collections Framework",
                    "ideal_answer": "HashMap uses an array of Nodes (buckets) based on hashing (`hashCode()`). When keys hash to the same index (collision), items are stored in a linked list. In Java 8+, if a bucket's linked list length exceeds 8 items (and total capacity >= 64), it converts into a Red-Black Tree to improve lookup time from O(n) to O(log n).",
                    "key_concepts": "Hash Buckets, Hash Collision, Red-Black Trees, O(log n) performance"
                },
                {
                    "question": "Explain Java Garbage Collection algorithms and the concept of Young/Old generations.",
                    "topic": "JVM Internals",
                    "ideal_answer": "Java memory is divided into Young Generation (Eden, Survivor spaces S0/S1) and Old (Tenured) Generation. Short-lived objects are allocated in Eden and collected by Minor GC. Survived objects promote to Old Generation, collected by Major/Full GC using collectors like G1, ZGC, or Parallel GC.",
                    "key_concepts": "Eden, Survivor Spaces, Minor GC, Major GC, G1 GC, ZGC"
                }
            ],
            "Hard": [
                {
                    "question": "Explain Java Memory Model (JMM), volatile keyword, and happens-before relationships.",
                    "topic": "Concurrency & Memory",
                    "ideal_answer": "JMM defines how threads interact through main memory and CPU L1/L2 caches. The `volatile` keyword guarantees visibility (flushing changes directly to main memory) and prevents instruction reordering by compiler/CPU using memory barriers, establishing a 'happens-before' ordering.",
                    "key_concepts": "JMM, Cache Coherency, Volatile, Memory Barriers, Happens-Before"
                }
            ]
        }
    },
    "Web Developer": {
        "Technical": {
            "Easy": [
                {
                    "question": "What is the difference between HTML inline, block, and inline-block elements?",
                    "topic": "HTML & Layout",
                    "ideal_answer": "Block elements (like <div>, <p>) take up the full available width and start on a new line. Inline elements (like <span>, <a>) wrap content and do not start on a new line or accept custom height/width. Inline-block elements sit inline with text but allow custom height and width styling.",
                    "key_concepts": "Block, Inline, Inline-block, Box Model"
                },
                {
                    "question": "Explain the CSS Box Model and how `box-sizing: border-box` works.",
                    "topic": "CSS Architecture",
                    "ideal_answer": "The CSS Box Model consists of Content, Padding, Border, and Margin. By default (`content-box`), width only applies to content. With `box-sizing: border-box`, padding and border are included within the specified width and height, preventing layout breakage.",
                    "key_concepts": "Content, Padding, Border, Margin, Border-Box"
                },
                {
                    "question": "What are JavaScript Promises and how do `async/await` work?",
                    "topic": "Async JavaScript",
                    "ideal_answer": "Promises represent eventual completion or failure of asynchronous operations (states: pending, fulfilled, rejected). `async/await` is syntactic sugar over Promises that allows writing asynchronous code in a clean, synchronous style with try/catch error handling.",
                    "key_concepts": "Promises, Async/Await, Non-blocking, Event Loop"
                }
            ],
            "Medium": [
                {
                    "question": "How does the browser rendering engine work (Critical Rendering Path)?",
                    "topic": "Browser Architecture",
                    "ideal_answer": "The browser parses HTML to construct the DOM tree and CSS to construct the CSSOM tree. It combines both into a Render Tree, computes exact positions via Layout/Reflow, and paints pixels onto the screen (Painting & Compositing). Optimizing styles and minimizing DOM reflows speeds up performance.",
                    "key_concepts": "DOM, CSSOM, Render Tree, Layout/Reflow, Paint, Compositing"
                },
                {
                    "question": "Explain JavaScript closures and provide a real-world application.",
                    "topic": "JavaScript Core",
                    "ideal_answer": "A closure is a function bundled together with references to its surrounding lexical environment, allowing an inner function to access variables from an outer scope even after the outer function has executed. Used for data privacy/encapsulation, event handlers, and function currying.",
                    "key_concepts": "Lexical Scope, Data Encapsulation, State Preservation, Outer Scope"
                }
            ],
            "Hard": [
                {
                    "question": "How would you optimize Core Web Vitals (LCP, INP, CLS) for a high-traffic web portal?",
                    "topic": "Web Performance",
                    "ideal_answer": "To optimize Largest Contentful Paint (LCP): use CDN, optimize images (WebP/AVIF), prioritize critical CSS. Interaction to Next Paint (INP): break long tasks, defer non-essential JS, minimize main thread blocking. Cumulative Layout Shift (CLS): set explicit dimensions on images/iframes, reserve font spaces with font-display: swap.",
                    "key_concepts": "Core Web Vitals, LCP, INP, CLS, Asset Optimization, Main Thread"
                }
            ]
        }
    },
    "Full Stack Developer": {
        "Technical": {
            "Easy": [
                {
                    "question": "What is the REST architectural style and what are standard HTTP methods?",
                    "topic": "API Architecture",
                    "ideal_answer": "REST (Representational State Transfer) is an architectural style for stateless, scalable web APIs. Standard HTTP methods include GET (retrieve resource), POST (create resource), PUT (update/replace resource), PATCH (partial update), and DELETE (remove resource).",
                    "key_concepts": "REST, Statelessness, GET, POST, PUT, DELETE, HTTP Status Codes"
                },
                {
                    "question": "What is CORS (Cross-Origin Resource Sharing) and how is it configured?",
                    "topic": "Web Security",
                    "ideal_answer": "CORS is a browser security mechanism that restricts HTTP requests initiated from scripts running in one origin to resources in another origin. The backend configured headers like `Access-Control-Allow-Origin` to allow trusted frontends to consume APIs.",
                    "key_concepts": "Cross-Origin, Browser Preflight, Access-Control Headers, Same-Origin Policy"
                }
            ],
            "Medium": [
                {
                    "question": "Compare Relational Databases (SQL) vs NoSQL Databases for Full Stack applications.",
                    "topic": "Database Design",
                    "ideal_answer": "SQL databases (MySQL, PostgreSQL) use structured schemas, ACID transactions, and relationships via foreign keys — best for transactional integrity (e.g. e-commerce, finance). NoSQL databases (MongoDB, Redis) use flexible document/key-value schemas and horizontal scaling — best for unstructured, rapidly evolving data.",
                    "key_concepts": "ACID vs BASE, Structured vs Flexible, Indexing, Joins, Horizontal Scaling"
                },
                {
                    "question": "How does JWT (JSON Web Token) authentication work across Client and Server?",
                    "topic": "Security & Auth",
                    "ideal_answer": "The client sends credentials to server; upon successful login, server generates a signed JWT containing header, payload, and signature. Client stores token (HTTPOnly cookie or localStorage) and sends it in `Authorization: Bearer <token>` header. Server verifies signature statelessly without database lookup.",
                    "key_concepts": "Stateless Auth, Bearer Header, Token Signature, HTTPOnly Cookies, Expiration"
                }
            ],
            "Hard": [
                {
                    "question": "Design a resilient microservices communication architecture using API Gateways and Message Queues.",
                    "topic": "System Architecture",
                    "ideal_answer": "An API Gateway acts as single entry point handling rate limiting, SSL termination, routing, and auth. Services communicate synchronously via gRPC/REST for read operations, and asynchronously via message brokers (Kafka/RabbitMQ) for event-driven decoupled writes with circuit breakers (e.g. Resilience4j) to prevent cascading failures.",
                    "key_concepts": "API Gateway, Message Brokers, Event-Driven, Circuit Breakers, Service Mesh"
                }
            ]
        }
    },
    "Data Analyst": {
        "Technical": {
            "Easy": [
                {
                    "question": "What is the difference between WHERE and HAVING clauses in SQL?",
                    "topic": "SQL Queries",
                    "ideal_answer": "WHERE is used to filter individual rows before any grouping occurs. HAVING is used to filter aggregated groups of rows after the GROUP BY clause has been applied.",
                    "key_concepts": "WHERE vs HAVING, GROUP BY, Aggregate Functions, Filtering"
                },
                {
                    "question": "What are the common types of SQL JOINs?",
                    "topic": "SQL Joins",
                    "ideal_answer": "INNER JOIN (matching rows in both tables), LEFT JOIN (all rows from left table + matching from right), RIGHT JOIN (all rows from right table + matching from left), FULL OUTER JOIN (all rows from both tables), and CROSS JOIN (cartesian product).",
                    "key_concepts": "Inner Join, Left Join, Right Join, Full Join, Cartesian Product"
                }
            ],
            "Medium": [
                {
                    "question": "How do SQL Window Functions (`ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`) differ?",
                    "topic": "Advanced SQL",
                    "ideal_answer": "Window functions perform calculations across related rows without collapsing them into a single row. `ROW_NUMBER()` gives unique sequential integers. `RANK()` leaves gaps in rank numbering after ties. `DENSE_RANK()` does not leave gaps after tied rankings.",
                    "key_concepts": "OVER(), PARTITION BY, Row_Number, Rank, Dense_Rank, Gaps in Ranking"
                }
            ],
            "Hard": [
                {
                    "question": "How do you handle missing or noisy data in large analytical datasets?",
                    "topic": "Data Cleaning & Prep",
                    "ideal_answer": "Missing data can be handled via deletion (if MCAR and small %), imputation (mean/median for numerical, mode for categorical, KNN or regression models for predictive imputation). Outliers are detected using IQR or Z-score and treated with capping/winsorization or domain-specific filtering.",
                    "key_concepts": "MCAR/MAR, Imputation, IQR/Z-score, Winsorization, Data Integrity"
                }
            ]
        }
    },
    "Data Scientist": {
        "Technical": {
            "Easy": [
                {
                    "question": "What is the difference between Supervised and Unsupervised Learning?",
                    "topic": "Machine Learning",
                    "ideal_answer": "Supervised learning uses labeled training datasets to predict targets (e.g. Classification, Regression). Unsupervised learning works on unlabeled datasets to discover underlying patterns, groupings, or structures (e.g. Clustering with K-Means, Dimensionality Reduction with PCA).",
                    "key_concepts": "Labeled vs Unlabeled Data, Regression, Classification, Clustering, PCA"
                }
            ],
            "Medium": [
                {
                    "question": "Explain Bias-Variance Tradeoff and how to prevent Overfitting.",
                    "topic": "ML Models",
                    "ideal_answer": "Bias error stems from oversimplified model assumptions (underfitting). Variance error stems from sensitivity to noise in training data (overfitting). To prevent overfitting: cross-validation, regularization (L1 Lasso / L2 Ridge), pruning trees, dropout in neural networks, and increasing data.",
                    "key_concepts": "Bias vs Variance, Underfitting/Overfitting, Regularization L1/L2, Cross-Validation"
                }
            ],
            "Hard": [
                {
                    "question": "Explain the architecture of Transformer models and the Self-Attention mechanism.",
                    "topic": "Deep Learning & AI",
                    "ideal_answer": "Transformers rely on Self-Attention to compute relationships between all words in a sequence simultaneously using Query (Q), Key (K), and Value (V) matrix projections: `Attention(Q,K,V) = softmax(Q K^T / sqrt(d_k)) V`. Multi-Head Attention allows focusing on multiple positional representations concurrently.",
                    "key_concepts": "Transformers, Self-Attention, Query-Key-Value Matrices, Softmax Scaling"
                }
            ]
        }
    },
    "Software Developer": {
        "Technical": {
            "Easy": [
                {
                    "question": "What is Version Control and why is Git widely used?",
                    "topic": "Development Tools",
                    "ideal_answer": "Version control tracks changes to software codebase over time. Git is a distributed version control system allowing multiple developers to work concurrently via branching, merging, pull requests, and atomic commits without reliance on a central server.",
                    "key_concepts": "Distributed VCS, Branching, Merging, Commits, Collaboration"
                }
            ],
            "Medium": [
                {
                    "question": "Explain the SOLID principles of Object-Oriented Design.",
                    "topic": "Software Design",
                    "ideal_answer": "SOLID stands for: Single Responsibility (one reason to change), Open/Closed (open for extension, closed for modification), Liskov Substitution (subtypes replaceable for base types), Interface Segregation (small, specific interfaces), and Dependency Inversion (depend on abstractions, not concretions).",
                    "key_concepts": "Single Responsibility, Open-Closed, Liskov, Interface Segregation, Dependency Inversion"
                }
            ],
            "Hard": [
                {
                    "question": "Explain the CAP Theorem in Distributed Systems.",
                    "topic": "System Architecture",
                    "ideal_answer": "CAP theorem states that a distributed data store can simultaneously provide at most two out of three guarantees: Consistency (all nodes see same data), Availability (every request receives non-error response), and Partition Tolerance (system operates despite network breaks). Since network partitions happen, systems choose CP or AP.",
                    "key_concepts": "Consistency, Availability, Partition Tolerance, CP vs AP systems"
                }
            ]
        }
    }
}

# HR & Behavioral Question Pool
HR_QUESTIONS = [
    {
        "question": "Tell me about yourself and your professional background.",
        "topic": "Introduction",
        "ideal_answer": "Candidate should present a structured 60-90 second elevator pitch: concise summary of educational background, relevant work experience, key accomplishments, and passion for the specific role.",
        "key_concepts": "Elevator Pitch, Relevant Highlights, Passion, Professional Tone"
    },
    {
        "question": "Why do you want to work for our organization?",
        "topic": "Motivation & Alignment",
        "ideal_answer": "Candidate should connect company mission, tech stack, or recent initiatives with personal career growth goals, demonstrating prior research and genuine enthusiasm.",
        "key_concepts": "Company Alignment, Career Trajectory, Mutual Value"
    },
    {
        "question": "What are your greatest strengths and areas of improvement?",
        "topic": "Self Awareness",
        "ideal_answer": "Strengths should be backed by concrete achievements (e.g. problem solving, adaptability). Areas for improvement should showcase self-awareness and active steps taken to improve.",
        "key_concepts": "Self-awareness, Actionable Growth, Balance, Authenticity"
    },
    {
        "question": "Where do you see yourself in 3 to 5 years?",
        "topic": "Career Goals",
        "ideal_answer": "Candidate should articulate realistic career growth goals, such as mastering advanced technical domains, taking on tech lead responsibilities, and driving strategic projects.",
        "key_concepts": "Growth Mindset, Leadership Ambition, Long-term Vision"
    }
]

BEHAVIORAL_QUESTIONS = [
    {
        "question": "Describe a situation where you faced a tight deadline or high pressure. How did you handle it?",
        "topic": "Stress Management",
        "ideal_answer": "Should follow STAR technique (Situation, Task, Action, Result): highlight prioritization, clear team communication, breaking down tasks, and delivering quality results.",
        "key_concepts": "STAR Method, Prioritization, Team Communication, Calm Resilience"
    },
    {
        "question": "Give an example of a conflict with a team member or stakeholder and how you resolved it.",
        "topic": "Conflict Resolution",
        "ideal_answer": "Focus on active listening, empathy, focusing on objective project goals rather than personal ego, and reaching a collaborative win-win consensus.",
        "key_concepts": "Active Listening, Empathy, Data-Driven Consensus, Professionalism"
    },
    {
        "question": "Describe a time when a project or code deployment failed. What went wrong and what did you learn?",
        "topic": "Accountability & Growth",
        "ideal_answer": "Demonstrate ownership without shifting blame, performing root cause analysis (RCA), writing blameless post-mortems, and implementing automated safeguards to prevent recurrence.",
        "key_concepts": "Accountability, Root Cause Analysis, Post-mortem, Prevention"
    }
]


def generate_interview_questions(
    role: str,
    experience: str,
    interview_type: str,
    difficulty: str,
    num_questions: int = 5
) -> List[Dict[str, Any]]:
    """Generates a tailored list of interview questions using AI API or Local Fallback."""
    
    # Try Gemini API if available
    if GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = f"""
            Generate exactly {num_questions} realistic, highly technical and contextual interview questions for:
            - Role: {role}
            - Experience Level: {experience}
            - Interview Type: {interview_type}
            - Difficulty: {difficulty}

            Return strict JSON array of objects with keys:
            "question", "topic", "ideal_answer", "key_concepts".
            Do NOT return any markdown formatting outside JSON.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            raw_text = response.text.strip()
            # Clean JSON markdown blocks if returned
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
                raw_text = re.sub(r"\n?```$", "", raw_text)
            parsed = json.loads(raw_text)
            if isinstance(parsed, list) and len(parsed) > 0:
                for idx, item in enumerate(parsed):
                    item["question_number"] = idx + 1
                    item["difficulty"] = difficulty
                return parsed[:num_questions]
        except Exception as e:
            print(f"[AI Engine API Warning] Gemini API call failed or unconfigured ({e}). Utilizing Local Engine.")

    # Local Engine Fallback
    selected_questions = []
    
    # 1. Pool selection according to type
    if interview_type == "HR":
        pool = HR_QUESTIONS
    elif interview_type == "Behavioral":
        pool = BEHAVIORAL_QUESTIONS
    elif interview_type == "Mixed":
        tech_pool = QUESTION_BANK.get(role, {}).get("Technical", {}).get(difficulty, [])
        if not tech_pool:
            tech_pool = QUESTION_BANK.get("Python Developer")["Technical"]["Medium"]
        pool = tech_pool + HR_QUESTIONS + BEHAVIORAL_QUESTIONS
    else: # Technical
        role_bank = QUESTION_BANK.get(role, QUESTION_BANK["Python Developer"])
        tech_dict = role_bank.get("Technical", {})
        pool = tech_dict.get(difficulty, [])
        if not pool:
            # Fallback across difficulties
            for diff in ["Medium", "Easy", "Hard"]:
                if tech_dict.get(diff):
                    pool += tech_dict[diff]

    if not pool:
        pool = QUESTION_BANK["Python Developer"]["Technical"]["Easy"]

    # Shuffle to ensure freshness
    shuffled_pool = list(pool)
    random.shuffle(shuffled_pool)

    # Multiply pool if requested count exceeds available template questions
    while len(shuffled_pool) < num_questions:
        shuffled_pool.extend(pool)

    for i in range(num_questions):
        item = shuffled_pool[i].copy()
        item["question_number"] = i + 1
        item["difficulty"] = difficulty
        selected_questions.append(item)

    return selected_questions


def evaluate_user_answer(
    question_text: str,
    user_answer: str,
    ideal_answer: str,
    key_concepts: str,
    role: str = "Software Developer",
    difficulty: str = "Medium"
) -> Dict[str, Any]:
    """Evaluates a single answer using Gemini API or Local NLP Evaluation Engine."""

    # Handle blank/empty answers immediately
    cleaned_user_ans = (user_answer or "").strip()
    if not cleaned_user_ans or len(cleaned_user_ans) < 3:
        return {
            "score": 0.0,
            "status": "Incorrect",
            "correctness_score": 0.0,
            "relevance_score": 0.0,
            "technical_score": 0.0,
            "completeness_score": 0.0,
            "clarity_score": 0.0,
            "confidence_score": 0.0,
            "what_went_well": "Attempted to submit an answer.",
            "areas_for_improvement": "No meaningful response provided. Ensure you explain concepts with clear definitions, examples, and technical detail.",
            "ideal_answer": ideal_answer,
            "key_concepts": key_concepts,
            "detailed_feedback": "The response was left blank or contained insufficient content to evaluate candidate knowledge."
        }

    # Try Gemini API if available
    if GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = f"""
            Evaluate the following candidate response in a job interview:

            Question: {question_text}
            Candidate Answer: {cleaned_user_ans}
            Reference Ideal Answer: {ideal_answer}
            Key Concepts Expected: {key_concepts}

            Evaluate across:
            - Correctness (0-10)
            - Relevance (0-10)
            - Technical Knowledge (0-10)
            - Completeness (0-10)
            - Clarity (0-10)
            - Confidence (0-10)

            Return strict JSON with keys:
            "score" (overall 0-10),
            "status" ("Correct", "Partially Correct", "Incorrect"),
            "correctness_score", "relevance_score", "technical_score", "completeness_score", "clarity_score", "confidence_score",
            "what_went_well",
            "areas_for_improvement",
            "ideal_answer",
            "key_concepts",
            "detailed_feedback"
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
            print(f"[AI Engine API Warning] Gemini Evaluation failed ({e}). Using Local NLP Evaluator.")

    # Local Evaluation Engine
    # Extract keywords from key_concepts and ideal_answer
    raw_concepts = [c.strip().lower() for c in key_concepts.replace(",", " ").split() if len(c.strip()) > 2]
    matched_concepts = [c for c in raw_concepts if c in cleaned_user_ans.lower()]
    concept_ratio = len(matched_concepts) / max(len(raw_concepts), 1)

    # Word count & completeness score
    words = cleaned_user_ans.split()
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

    # Calculate sub-scores
    correctness = min(10.0, round(4.0 + (concept_ratio * 5.0) + (min(word_count, 50) / 25), 1))
    relevance = min(10.0, round(5.0 + (concept_ratio * 4.5), 1))
    technical = min(10.0, round(3.5 + (concept_ratio * 5.5) + (1.0 if any(term in cleaned_user_ans.lower() for term in ['example', 'memory', 'performance', 'code', 'function', 'object', 'data']) else 0.0), 1))
    confidence = min(10.0, round(6.0 + (min(word_count, 40) / 10), 1))

    # Overall score out of 10
    overall_score = round((correctness * 0.30 + relevance * 0.20 + technical * 0.25 + completeness * 0.15 + clarity * 0.10), 1)

    if overall_score >= 7.5:
        status = "Correct"
        what_went_well = "Strong explanation! You demonstrated solid understanding of key technical concepts and articulated your thoughts clearly."
        areas_to_improve = "To reach absolute mastery, consider including a brief code example or real-world scenario."
    elif overall_score >= 5.0:
        status = "Partially Correct"
        what_went_well = "Good initial attempt. You grasped the fundamental premise of the question."
        areas_to_improve = f"Expand further on key terms such as ({key_concepts}). Elaborate on underlying architecture or practical use cases."
    else:
        status = "Incorrect"
        what_went_well = "You attempted the question and provided a basic overview."
        areas_to_improve = f"The response lacked technical depth. Review core concepts: {key_concepts}. Compare your response with the ideal answer below."

    detailed_fb = f"Scored {overall_score}/10. Keyword alignment: {int(concept_ratio * 100)}%. Word count: {word_count} words."

    return {
        "score": overall_score,
        "status": status,
        "correctness_score": correctness,
        "relevance_score": relevance,
        "technical_score": technical,
        "completeness_score": completeness,
        "clarity_score": clarity,
        "confidence_score": confidence,
        "what_went_well": what_went_well,
        "areas_for_improvement": areas_to_improve,
        "ideal_answer": ideal_answer,
        "key_concepts": key_concepts,
        "detailed_feedback": detailed_fb
    }


def generate_personalized_recommendations(
    interview_data: Dict[str, Any],
    evaluations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates personalized study tips, weak areas, and practice advice."""
    
    avg_score = interview_data.get("overall_score", 0.0)
    role = interview_data.get("role", "Software Developer")
    difficulty = interview_data.get("difficulty", "Medium")

    weak_topics = []
    strong_topics = []
    practice_suggestions = []

    for ev in evaluations:
        topic = ev.get("topic", "Core Fundamentals")
        score = ev.get("score", 0.0)
        if score < 6.5:
            if topic not in weak_topics:
                weak_topics.append(topic)
        else:
            if topic not in strong_topics:
                strong_topics.append(topic)

    if not weak_topics and evaluations:
        weak_topics = ["Advanced Performance Optimization", "Edge Case Testing"]

    # Practice suggestions based on performance
    if avg_score >= 80:
        next_diff = "Hard"
        practice_suggestions = [
            f"Practice high-level system design and architecture for {role}.",
            "Work on complex algorithmic optimizations and deep language internals.",
            "Conduct mock interviews focusing on leadership and architectural tradeoffs."
        ]
    elif avg_score >= 60:
        next_diff = difficulty
        practice_suggestions = [
            f"Revise weak core concepts: {', '.join(weak_topics[:3])}.",
            "Practice structuring answers using the STAR method for behavioral questions.",
            "Write mini code snippets to solidify technical definitions."
        ]
    else:
        next_diff = "Easy"
        practice_suggestions = [
            f"Review foundational documentation for {role}.",
            f"Focus on basic syntax, data structures, and core keywords ({', '.join(weak_topics[:2])}).",
            "Take 5-question Easy difficulty practice sessions to build confidence."
        ]

    return {
        "weak_topics": weak_topics[:4],
        "strong_topics": strong_topics[:4],
        "practice_suggestions": practice_suggestions,
        "recommended_difficulty": next_diff
    }
