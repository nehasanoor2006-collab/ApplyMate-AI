"""
Pre-packaged sample data for hackathon demos and instant zero-friction evaluations.
"""

SAMPLE_RESUMES = {
    "tech_intern": {
        "title": "Alex Chen - Full Stack & AI Candidate",
        "parsed_data": {
            "name": "Alex Chen",
            "email": "alex.chen.dev@example.edu",
            "phone": "+1 (555) 234-5678",
            "location": "San Francisco, CA / Remote",
            "linkedin": "https://linkedin.com/in/alexchen-dev",
            "github": "https://github.com/alexchen-tech",
            "summary": "Passionate 3rd-year Computer Science student at UC Berkeley with hands-on experience building full-stack web applications, REST APIs, and integrating Generative AI pipelines. Experienced in Django, Python, TypeScript, React, and cloud deployments.",
            "skills": {
                "programming_languages": ["Python", "JavaScript", "TypeScript", "C++", "SQL", "HTML5", "CSS3"],
                "frameworks_and_libraries": ["Django", "FastAPI", "React", "Node.js", "Tailwind CSS", "Bootstrap", "PyTorch"],
                "tools_and_infrastructure": ["Git", "Docker", "PostgreSQL", "SQLite", "Redis", "AWS (S3, EC2)", "Linux"],
                "ai_and_data": ["Gemini API", "OpenAI API", "LangChain", "Vector Databases", "Prompt Engineering", "Pandas", "NumPy"]
            },
            "education": [
                {
                    "degree": "B.S. in Computer Science",
                    "institution": "University of California, Berkeley",
                    "year": "Expected May 2027",
                    "gpa": "3.84 / 4.0",
                    "details": "Relevant Coursework: Data Structures & Algorithms, Artificial Intelligence, Database Systems, Computer Networking."
                }
            ],
            "experience": [
                {
                    "role": "Software Engineering Intern",
                    "company": "Kinetik Labs",
                    "duration": "Jun 2025 – Aug 2025",
                    "location": "San Francisco, CA",
                    "description": "Architected asynchronous REST microservices using Python, Django, and Celery, reducing API response times by 35%. Integrated Gemini LLM embeddings for automated customer ticket classification."
                },
                {
                    "role": "Undergraduate Teaching Assistant (CS61B: Data Structures)",
                    "company": "UC Berkeley EECS",
                    "duration": "Jan 2025 – May 2025",
                    "location": "Berkeley, CA",
                    "description": "Mentored 80+ undergraduate students in Java, algorithmic analysis, asymptotic complexity, and graph search paradigms. Conducted bi-weekly lab sessions."
                }
            ],
            "projects": [
                {
                    "title": "ApplyMate AI - Smart Opportunity & Grant Tracker",
                    "tech": "Python, Django, Gemini API, SQLite, Bootstrap 5",
                    "description": "Engineered an intelligent web agent that compares applicant resumes with internships and scholarships, producing tailored skill gap audits, roadmaps, and cover letters."
                },
                {
                    "title": "DocuQuery - Multi-Modal Document RAG Engine",
                    "tech": "FastAPI, React, LangChain, ChromaDB, Docker",
                    "description": "Developed a document search engine utilizing semantic search over 10,000+ research papers, cutting query latency to sub-100ms with hybrid BM25 and vector reranking."
                }
            ],
            "certifications": [
                "AWS Certified Cloud Practitioner (2025)",
                "DeepLearning.AI Deep Learning Specialization"
            ]
        },
        "raw_text": """ALEX CHEN
San Francisco, CA | alex.chen.dev@example.edu | +1 (555) 234-5678 | github.com/alexchen-tech | linkedin.com/in/alexchen-dev

EDUCATION
University of California, Berkeley
Bachelor of Science in Computer Science | Expected Graduation: May 2027 | GPA: 3.84/4.0
Relevant Coursework: Data Structures & Algorithms, Operating Systems, Database Systems, Artificial Intelligence.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, C++, SQL, HTML/CSS
Frameworks: Django, FastAPI, React.js, Node.js, Bootstrap, Tailwind CSS, PyTorch
Tools & Cloud: Git, Docker, PostgreSQL, Redis, AWS (S3, EC2), SQLite, Linux
AI/ML: Gemini API, LangChain, Prompt Engineering, Vector Search, Pandas, NumPy

WORK EXPERIENCE
Kinetik Labs | Software Engineering Intern | Jun 2025 – Aug 2025 | San Francisco, CA
- Architected asynchronous REST microservices using Python and Django, reducing API response times by 35%.
- Integrated Gemini LLM embeddings for automated customer ticket classification, boosting support throughput by 40%.
- Designed automated CI/CD unit testing suites with 92% coverage across core business workflows.

UC Berkeley EECS | Teaching Assistant (CS61B Data Structures) | Jan 2025 – May 2025 | Berkeley, CA
- Mentored 80+ undergraduate students in Java, algorithmic analysis, and tree/graph search paradigms.
- Led weekly discussion sections and graded algorithmic assignments.

PROJECTS
ApplyMate AI | Python, Django, Gemini API, Bootstrap
- Built full-featured opportunity matcher evaluating resumes against internship and fellowship requirements.
- Developed dynamic eligibility scoring, skill gap diagnostics, and automated application cover letter generation.

DocuQuery RAG Engine | FastAPI, React, LangChain, ChromaDB
- Developed semantic search engine indexing 10,000+ PDF research documents with sub-100ms query response.
"""
    },

    "research_scholar": {
        "title": "Priya Sharma - AI & Data Science Scholar",
        "parsed_data": {
            "name": "Priya Sharma",
            "email": "priya.sharma.research@example.org",
            "phone": "+1 (555) 987-6543",
            "location": "Boston, MA / Remote",
            "linkedin": "https://linkedin.com/in/priyasharma-ai",
            "github": "https://github.com/priyasharma-science",
            "summary": "Master's student in Data Science with a focus on ethical AI, Natural Language Processing, and healthcare analytics. Proven academic track record with 2 peer-reviewed workshop publications, fellowship recipient, and passionate advocate for accessible higher education.",
            "skills": {
                "data_and_ml": ["Python", "PyTorch", "Hugging Face", "Scikit-Learn", "SciPy", "Pandas", "Matplotlib", "Seaborn"],
                "research_methods": ["A/B Testing", "Statistical Modeling", "Literature Reviews", "Experimental Design", "Data Ethics"],
                "tools_and_languages": ["R", "SQL", "Git", "LaTeX", "Bash", "Jupyter", "Docker"]
            },
            "education": [
                {
                    "degree": "M.S. in Data Science & Artificial Intelligence",
                    "institution": "Boston University",
                    "year": "Expected Dec 2026",
                    "gpa": "3.92 / 4.0",
                    "details": "Graduate Dean's Merit Scholar. Thesis: Bias Mitigation in Clinical NLP Foundation Models."
                },
                {
                    "degree": "B.S. in Applied Mathematics & Statistics",
                    "institution": "University of Washington",
                    "year": "Graduated May 2024",
                    "gpa": "3.88 / 4.0",
                    "details": "Summa Cum Laude, Phi Beta Kappa Honor Society."
                }
            ],
            "experience": [
                {
                    "role": "Graduate Research Assistant",
                    "company": "BU Computational Health Informatics Program",
                    "duration": "Sep 2024 – Present",
                    "location": "Boston, MA",
                    "description": "Investigating demographic representation in large clinical language models; trained transformer models on 500k+ de-identified clinical notes."
                }
            ],
            "projects": [
                {
                    "title": "BioFairness - Clinical Bias Audit Toolkit",
                    "tech": "Python, Hugging Face Transformers, Streamlit",
                    "description": "Open-source Python library to evaluate disparate impact in medical NLP benchmarks, adopted by 3 academic labs."
                }
            ],
            "certifications": [
                "Responsible AI & Algorithmic Fairness Specialization",
                "CITI Human Subjects Research Certified"
            ]
        },
        "raw_text": """PRIYA SHARMA
Boston, MA | priya.sharma.research@example.org | linkedin.com/in/priyasharma-ai

EDUCATION
Boston University | M.S. in Data Science & AI | Expected Dec 2026 | GPA: 3.92/4.0
University of Washington | B.S. in Applied Mathematics | May 2024 | GPA: 3.88/4.0 | Summa Cum Laude

RESEARCH INTERESTS
Natural Language Processing, Foundation Models, Algorithmic Fairness, Healthcare AI, Open Science

SKILLS
Programming & Libraries: Python, R, PyTorch, Hugging Face, Scikit-learn, SQL, Pandas, NumPy
Research Tools: LaTeX, Git, Docker, Jupyter, CITI Research Ethics
"""
    }
}

SAMPLE_OPPORTUNITIES = [
    {
        "title": "Software Engineering Intern - Cloud & AI Platforms",
        "organization": "Google",
        "category": "internship",
        "location": "Mountain View, CA / Hybrid",
        "deadline": "November 15, 2026",
        "url": "https://careers.google.com/jobs/results/",
        "priority": "high",
        "description": """Google is looking for energetic, curious Software Engineering Interns to join our Cloud & AI Platform organization. In this role, you will collaborate with cross-functional teams of engineers and product managers to build scalable, fault-tolerant cloud services and machine learning developer interfaces.

Key Responsibilities:
- Design, test, deploy, and maintain software solutions across our cloud microservices.
- Write clean, maintainable, and well-tested code in Python, C++, Go, or Java.
- Integrate modern machine learning and LLM capabilities (such as Gemini models) into enterprise tooling.
- Collaborate with senior engineers on system architecture design reviews and performance benchmarking.

Minimum Qualifications:
- Currently pursuing a BS, MS, or PhD in Computer Science, Software Engineering, or related technical field.
- Experience with one or more general-purpose programming languages (Python, Java, C++, TypeScript).
- Solid foundational understanding of data structures, algorithms, and software design principles.

Preferred Qualifications:
- Experience building RESTful web services using frameworks like Django, FastAPI, or Flask.
- Familiarity with cloud platforms (GCP, AWS) and containerization technologies (Docker, Kubernetes).
- Hands-on experience integrating Generative AI APIs or building NLP applications.
- Strong problem-solving abilities, communication skills, and collaborative mindset.""",
        "requirements": "Pursuing CS degree, Python/C++/Java proficiency, Data structures & algorithms, Web services (Django/FastAPI) or Cloud familiarity."
    },
    {
        "title": "Fulbright Foreign Student Fellowship & Global Grant",
        "organization": "U.S. Department of State & IIE",
        "category": "scholarship",
        "location": "Global / International Study",
        "deadline": "October 30, 2026",
        "url": "https://foreign.fulbrightonline.org/",
        "priority": "high",
        "description": """The Fulbright Foreign Student Program enables graduate students, young professionals, and artists from abroad to research and study in the United States or partner nations. The scholarship covers full tuition, living stipend, roundtrip airfare, and health insurance for up to two academic years.

Eligibility & Criteria:
- Strong academic track record with demonstrated intellectual rigor and research promise.
- Clear articulation of study/research goals and their potential impact on international collaboration or societal advancement.
- Demonstrated leadership qualities, community service, and ambassadorial potential.
- Proficiency in English and strong cross-cultural adaptability.

Application Requirements:
- Comprehensive Statement of Purpose / Academic Objective detailing proposed research and long-term vision.
- Personal Statement exploring formative experiences, challenges overcome, and commitment to cross-cultural dialogue.
- Three letters of recommendation and verified academic transcripts.""",
        "requirements": "Strong academic record, research experience, clear statement of purpose, leadership & cross-cultural engagement."
    },
    {
        "title": "Backend Infrastructure & API Engineering Intern",
        "organization": "Stripe",
        "category": "internship",
        "location": "San Francisco, CA / Remote (US)",
        "deadline": "Rolling Admissions",
        "url": "https://stripe.com/jobs",
        "priority": "medium",
        "description": """At Stripe, our infrastructure handles hundreds of billions of dollars in payments annually. As a Backend Infrastructure Intern, you will work on the core systems that ensure 99.999% reliability, high concurrency, and airtight security.

What You'll Do:
- Build and optimize critical backend services using Python, Ruby, or Go.
- Enhance database schemas, query performance, and distributed caching with Redis and PostgreSQL.
- Contribute to Stripe's developer-facing APIs with rigorous documentation and defensive error handling.

Requirements:
- Enrolled in an undergraduate or graduate degree in CS or equivalent experience.
- Strong software engineering foundation with Python, SQL, and Git.
- Curiosity about distributed systems, API design, and scalable infrastructure.""",
        "requirements": "Enrolled in CS degree, strong Python and SQL skills, understanding of databases and distributed systems."
    },
    {
        "title": "OpenAI Emerging AI Fellows Program",
        "organization": "OpenAI",
        "category": "fellowship",
        "location": "San Francisco, CA",
        "deadline": "December 1, 2026",
        "url": "https://openai.com/careers",
        "priority": "high",
        "description": """The OpenAI Emerging Fellows Program is an intensive 6-month research and engineering residency designed for talented individuals passionate about artificial general intelligence and beneficial AI systems.

Fellows work alongside leading researchers to advance frontiers in large language models, alignment, evaluation frameworks, and multimodal reasoning.

We Look For:
- Proven programming prowess in Python and PyTorch.
- Familiarity with transformer architectures, fine-tuning, and prompt optimization.
- Genuine curiosity, intellectual humility, and commitment to ethical AI stewardship.""",
        "requirements": "Deep Python and PyTorch proficiency, understanding of transformers and LLM fine-tuning, strong research mindset."
    }
]
