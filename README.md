# ApplyMate AI — Your Personal Opportunity Agent

> **An intelligent, modern web application that matches candidates with internships, scholarships, and jobs. Built for hackathons, students, and early-career talent.**

![Tech Stack](https://img.shields.io/badge/Backend-Django_5.2-green.svg)
![Frontend](https://img.shields.io/badge/Frontend-Bootstrap_5.3_|_Custom_SaaS_CSS-purple.svg)
![AI Engine](https://img.shields.io/badge/AI-Google_Gemini_|_Smart_Demo_Engine-blue.svg)
![PDF Parser](https://img.shields.io/badge/PDF_Extraction-PyPDF2-red.svg)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)

---

## 🌟 Key Features

1. **Opportunity Discovery Agent (Candidate-Based Auto-Matching)**:
   - Scans active resume profile and auto-recommends matching opportunities from reliable official sources:
     - **AICTE National Internship Portal** (`https://internship.aicte-india.org/internships`)
     - **National Scholarship Portal (NSP)** (`https://scholarships.gov.in/All-Scholarships`)
     - Verified industry research and technical internships (Google, Stripe, Microsoft Research, OpenAI).
   - Multi-factor match scoring (0–100%) based on technical skills, education criteria, and projects.
   - Categorized ranking into **Best Matches** (&ge; 75%), **Good Matches** (55%–74%), and **Opportunities to Explore** (&lt; 55%).
   - Seamless one-click **"Analyze Opportunity"** integration into roadmap and draft generation, plus **"Save to Tracker"**.
2. **SaaS Dashboard & Application Tracker**:
   - Application pipeline metrics (Saved, In Progress, Applied, Interviewing, Offers).
   - Average eligibility match score gauge.
   - Active resume profile widget and quick actions.
3. **Resume PDF Upload & Analysis (PyPDF2 + AI)**:
   - Drag-and-drop or file upload with PDF validation.
   - Structured extraction: Contact info, Summary, Categorized Skills (Languages, Frameworks, Tools, Domains), Experience, Education, and Projects.
   - 1-Click Sample Candidate Profiles (`Alex Chen - SWE Intern`, `Priya Sharma - Data Science Scholar`).
4. **Opportunity Analyzer (Internships & Scholarships)**:
   - Input job or grant descriptions with metadata (Organization, Location, Deadline, Priority).
   - 1-Click quick test presets: *Google Cloud & AI Intern*, *Fulbright Global Scholarship*, *Stripe Backend Intern*, *OpenAI Fellowship*.
5. **AI Eligibility Checker**:
   - Animated circular score gauge (0–100%).
   - Candidate verdict (*Strong Match*, *Competitive Match*, *Moderate Match*, *Reach Opportunity*).
   - Core strengths highlighting matching coursework, projects, and skills.
6. **Skill Gap Diagnostics**:
   - Identifies missing skills and requirements.
   - Priority classification (*High*, *Medium*).
   - Actionable preparation advice and recommended learning resources.
7. **Personalized 4-Phase Application Roadmap**:
   - Phase 1: Resume & Profile Alignment (Days 1–3).
   - Phase 2: Skill Gap Closure & Proof of Concept (Days 4–7).
   - Phase 3: Strategic Outreach & Referral Building (Days 8–10).
   - Phase 4: Application Submission & Interview Sprint (Days 11–14).
   - Interactive completion checkboxes.
8. **AI-Generated Application Drafts**:
   - Bespoke cover letters, scholarship motivation statements, and cold recruiter outreach emails tailored to the candidate's exact background.
   - 1-Click Copy to Clipboard and Download as `.txt`.
   - Multi-format switcher (*Cover Letter*, *Scholarship Statement*, *Cold Outreach Email*).
9. **Dual AI Mode (Live Gemini + Offline Demo Engine)**:
   - **Live Gemini API**: Activated automatically when `GEMINI_API_KEY` is present in `.env`.
   - **Intelligent Demo Mode**: If no key is set or quota is exceeded, ApplyMate runs an intelligent offline heuristic analyzer so the hackathon presentation never breaks!

---

## 🚀 Quick Start Guide

### 1. Activate Environment

```bash
# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Configure Environment Variables (Optional)

Create a `.env` file in the root directory (or copy `.env.example`):

```bash
cp .env.example .env
```

To enable live Google Gemini AI generation:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DEBUG=True
```
*(If left empty, ApplyMate seamlessly activates its intelligent offline Demo Mode!)*

### 3. Run Migrations & Seed Demo Data

```bash
python manage.py migrate
```

To initialize the demo database with sample data (Alex Chen candidate profile + 4 analyzed opportunities):
Visit `http://127.0.0.1:8000/demo/seed/` or click **"Load Demo Data"** in the sidebar.

### 4. Start the Development Server

```bash
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`.

---

## 🧪 Running the Test Suite

ApplyMate comes with an automated test suite verifying all views, AI services, models, and status updates:

```bash
python manage.py test core
```

---

## 📁 Project Architecture

```
ApplyMate_AI/
├── config/                  # Django project configuration
│   ├── settings.py          # Settings with dotenv and Gemini configuration
│   ├── urls.py              # Root routing with media/static handlers
│   └── wsgi.py
├── core/                    # Main application app
│   ├── models.py            # Resume, Opportunity, and Analysis models
│   ├── views.py             # Views for dashboard, resume, opportunities
│   ├── urls.py              # URL routes
│   ├── context_processors.py# Global status and active resume context
│   ├── admin.py             # Admin registration
│   ├── tests.py             # Automated unit tests
│   └── services/
│       ├── pdf_parser.py    # PyPDF2 extraction and sanitization
│       ├── gemini_service.py# Live Gemini API & Smart Demo fallback engine
│       └── sample_data.py   # Pre-configured candidate profiles and roles
├── static/
│   ├── css/style.css        # Premium SaaS custom CSS (Plus Jakarta Sans)
│   └── js/main.js           # Score animation, copy-to-clipboard, prefill
├── templates/
│   ├── base.html            # Core layout with sidebar & top navbar
│   └── core/
│       ├── dashboard.html   # Main overview & application pipeline
│       ├── resume.html      # Skills matrix & experience timeline
│       ├── opportunity_list.html # Tracker board with category filters
│       ├── opportunity_form.html # Add form with 1-click test pre-fills
│       └── opportunity_detail.html # Flagship AI fit analysis & roadmap
├── media/resumes/           # Uploaded PDF resumes
├── db.sqlite3               # SQLite database
├── manage.py
└── requirements.txt
```

---

## 🎨 Design System

- **Colors**: Deep Indigo (`#6366f1`), Royal Purple (`#8b5cf6`), Electric Blue (`#3b82f6`), Emerald Green (`#10b981`), Clean Canvas (`#f8fafc`).
- **Typography**: `Plus Jakarta Sans` for titles & navigation, `Inter` for document reading.
- **Card Styling**: `border-radius: 18px`, soft multi-layered shadows, glassmorphism top navigation.
- **Responsive**: Fully responsive with collapsible sidebar on tablet and mobile viewports.
