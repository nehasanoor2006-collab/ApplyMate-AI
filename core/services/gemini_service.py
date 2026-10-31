"""
AI Service handling Resume Parsing, Opportunity Eligibility Analysis,
Skill Gap Diagnostics, Roadmap Generation, and Application Drafting.

Gracefully handles live Gemini API execution or intelligent offline Demo Mode.
"""

import json
import logging
import os
import re
from django.conf import settings

logger = logging.getLogger(__name__)

# Common tech/domain keywords dictionary for heuristic matching
TECH_TAXONOMY = {
    "languages": [
        "python", "javascript", "typescript", "c++", "c#", "java", "ruby", "go",
        "golang", "rust", "php", "swift", "kotlin", "sql", "r", "scala", "html", "css"
    ],
    "frameworks": [
        "django", "fastapi", "flask", "react", "react.js", "next.js", "vue", "angular",
        "node.js", "express", "pytorch", "tensorflow", "keras", "scikit-learn",
        "pandas", "numpy", "spring boot", "tailwind", "bootstrap"
    ],
    "tools": [
        "git", "github", "docker", "kubernetes", "aws", "gcp", "azure", "linux",
        "postgresql", "mysql", "mongodb", "sqlite", "redis", "celery", "graphql",
        "rest api", "ci/cd", "terraform", "langchain", "gemini", "openai"
    ],
    "domains": [
        "machine learning", "artificial intelligence", "nlp", "computer vision",
        "deep learning", "distributed systems", "microservices", "cloud computing",
        "data structures", "algorithms", "data science", "cybersecurity", "web development"
    ]
}


def is_gemini_configured() -> bool:
    """Returns True if a valid-looking GEMINI_API_KEY is present in settings."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
    return bool(api_key and len(api_key.strip()) > 15)


def clean_json_response(raw_text: str) -> dict:
    """Extracts and parses JSON from markdown code blocks or raw response text."""
    text = raw_text.strip()
    
    # Strip markdown fences if present
    fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if fence_match:
        text = fence_match.group(1).strip()
    
    # Attempt direct json load
    try:
        return json.loads(text)
    except Exception:
        # Try finding outer curly brackets
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            sub = text[first_brace:last_brace + 1]
            try:
                return json.loads(sub)
            except Exception:
                pass
        raise ValueError("Failed to parse valid JSON from AI response.")


# -------------------------------------------------------------------------
# RESUME PARSER
# -------------------------------------------------------------------------

def parse_resume_content(raw_text: str) -> tuple[dict, bool]:
    """
    Parses resume plain text into structured candidate profile data.
    Returns: (parsed_data_dict, is_demo_mode: bool)
    """
    if is_gemini_configured():
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            prompt = f"""
You are an expert HR recruiter and technical talent evaluator.
Extract structured information from this candidate's resume plain text.
Return ONLY a valid JSON object with the exact keys:
{{
  "name": "Candidate Full Name or Applicant",
  "email": "Email address or empty",
  "phone": "Phone number or empty",
  "location": "City, State / Remote or empty",
  "linkedin": "LinkedIn URL or empty",
  "github": "GitHub URL or empty",
  "summary": "2-3 sentence professional summary highlighting strengths",
  "skills": {{
    "programming_languages": ["list of languages"],
    "frameworks_and_libraries": ["list of frameworks"],
    "tools_and_infrastructure": ["list of developer tools, clouds, databases"],
    "concepts_and_domain": ["core topics like ML, Algorithms, etc."]
  }},
  "education": [
    {{
      "degree": "Degree name",
      "institution": "University / College",
      "year": "Graduation year or dates",
      "gpa": "GPA or empty",
      "details": "Major courses or honors"
    }}
  ],
  "experience": [
    {{
      "role": "Job / Internship Role",
      "company": "Company / Organization",
      "duration": "Dates (e.g. May 2024 - Aug 2024)",
      "location": "Location or Remote",
      "description": "Concise bullet description of achievements"
    }}
  ],
  "projects": [
    {{
      "title": "Project Title",
      "tech": "Technologies used",
      "description": "What it is and key accomplishments"
    }}
  ],
  "certifications": ["List of any certificates or awards"]
}}

RESUME TEXT:
{raw_text[:8000]}
"""
            model_names = ['gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']
            for m in model_names:
                try:
                    model = genai.GenerativeModel(m)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        parsed = clean_json_response(response.text)
                        return parsed, False
                except Exception as model_err:
                    logger.warning(f"Gemini model {m} failed: {model_err}")
                    continue
        except Exception as e:
            logger.warning(f"Live Gemini resume parsing failed, fallback to heuristic engine: {e}")

    # Fallback heuristic parser
    return heuristic_parse_resume(raw_text), True


def heuristic_parse_resume(raw_text: str) -> dict:
    """Heuristic extraction of resume sections using regex and keyword mapping."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    # Extract Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    email = email_match.group(0) if email_match else ""
    
    # Extract Phone
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', raw_text)
    phone = phone_match.group(0) if phone_match else ""
    
    # Extract GitHub / LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', raw_text, re.IGNORECASE)
    linkedin = f"https://{linkedin_match.group(0)}" if linkedin_match else ""
    
    github_match = re.search(r'github\.com/[\w-]+', raw_text, re.IGNORECASE)
    github = f"https://{github_match.group(0)}" if github_match else ""
    
    # Name: assume first line without email or phone is candidate name
    name = "Candidate"
    for line in lines[:5]:
        if not re.search(r'[@\d]', line) and len(line) < 50:
            name = line.title()
            break
            
    # Detect Skills from taxonomy
    lower_text = raw_text.lower()
    found_languages = [lang.title() for lang in TECH_TAXONOMY["languages"] if re.search(r'\b' + re.escape(lang) + r'\b', lower_text)]
    found_frameworks = [fw.title() for fw in TECH_TAXONOMY["frameworks"] if re.search(r'\b' + re.escape(fw) + r'\b', lower_text)]
    found_tools = [tool.title() for tool in TECH_TAXONOMY["tools"] if re.search(r'\b' + re.escape(tool) + r'\b', lower_text)]
    found_domains = [dom.title() for dom in TECH_TAXONOMY["domains"] if re.search(r'\b' + re.escape(dom) + r'\b', lower_text)]
    
    # Degree detection
    education = []
    edu_patterns = [
        r'(Bachelor(?:[\'\w\s]+)?|B\.?S\.?|B\.?A\.?|Master(?:[\'\w\s]+)?|M\.?S\.?|Ph\.?D\.?)\s*(?:in|of)?\s*([A-Za-z\s,]+)',
    ]
    for pattern in edu_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            education.append({
                "degree": match.group(0).strip()[:80],
                "institution": "University / College",
                "year": "2024 - 2027",
                "gpa": "3.8 / 4.0",
                "details": "Computer Science & Engineering Studies"
            })
            break
            
    if not education:
        education.append({
            "degree": "B.S. in Computer Science / Related Field",
            "institution": "Accredited University",
            "year": "Present",
            "gpa": "3.75",
            "details": "Core Coursework in Computing & Analysis"
        })

    # Summary
    summary = (
        f"{name} is a results-driven technologist with core strengths in "
        f"{', '.join(found_languages[:3]) or 'software development'}"
        f"{' and ' + found_frameworks[0] if found_frameworks else ''}. "
        f"Demonstrated competence in technical problem-solving and software development."
    )

    return {
        "name": name,
        "email": email or "applicant@example.edu",
        "phone": phone or "+1 (555) 019-2834",
        "location": "Available for Remote & On-site",
        "linkedin": linkedin or "https://linkedin.com",
        "github": github or "https://github.com",
        "summary": summary,
        "skills": {
            "programming_languages": found_languages or ["Python", "JavaScript", "SQL"],
            "frameworks_and_libraries": found_frameworks or ["Django", "React", "Node.js"],
            "tools_and_infrastructure": found_tools or ["Git", "Docker", "PostgreSQL"],
            "concepts_and_domain": found_domains or ["Data Structures", "Algorithms", "Web Development"]
        },
        "education": education,
        "experience": [
            {
                "role": "Software Engineering Contributor",
                "company": "Open Source & Academic Projects",
                "duration": "Recent",
                "location": "Hybrid",
                "description": "Built full-stack modules and implemented data pipelines with automated test coverage."
            }
        ],
        "projects": [
            {
                "title": "Full-Stack Web Application",
                "tech": ", ".join(found_languages[:2] + found_frameworks[:2]) or "Python, Django, React",
                "description": "Architected end-to-end responsive application with relational data models and RESTful API endpoints."
            }
        ],
        "certifications": ["Verified Technical Problem Solver"]
    }


# -------------------------------------------------------------------------
# OPPORTUNITY ANALYZER & ELIGIBILITY CHECKER
# -------------------------------------------------------------------------

def analyze_opportunity_fit(resume_obj, opportunity_obj, draft_type="Cover Letter") -> tuple[dict, bool]:
    """
    Compares candidate's resume with opportunity specifications.
    Generates:
    - match_score (0-100)
    - verdict
    - fit summary
    - strengths (matching points)
    - skill gaps (missing skills + actionable advice + resource recommendations)
    - application roadmap (4 phases with timeline and steps)
    - application draft (custom cover letter or statement)
    
    Returns: (analysis_data_dict, is_demo_mode: bool)
    """
    resume_text = resume_obj.raw_text if resume_obj else ""
    candidate_name = resume_obj.get_candidate_name() if resume_obj else "Applicant"
    parsed_data = resume_obj.parsed_data if resume_obj else {}
    
    opp_title = opportunity_obj.title
    opp_org = opportunity_obj.organization
    opp_desc = opportunity_obj.description
    opp_req = opportunity_obj.requirements
    opp_cat = opportunity_obj.category

    if is_gemini_configured():
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            prompt = f"""
You are an expert AI Career Coach and Opportunity Evaluator.
Analyze the fit between the Candidate's Resume and the Opportunity Requirements.

CANDIDATE NAME: {candidate_name}
RESUME DATA:
{json.dumps(parsed_data, indent=2)[:4000]}
RESUME TEXT:
{resume_text[:3000]}

OPPORTUNITY DETAILS:
Title: {opp_title}
Organization: {opp_org}
Category: {opp_cat}
Requirements: {opp_req}
Full Description:
{opp_desc[:4000]}

REQUESTED APPLICATION DRAFT TYPE: {draft_type}

Return a single VALID JSON object ONLY (no markdown text outside the JSON) with this exact schema:
{{
  "match_score": 82, // integer between 0 and 100 representing realistic eligibility
  "verdict": "Strong Match" | "Competitive Match" | "Moderate Match" | "Reach Opportunity",
  "summary": "2-3 sentences evaluating the applicant's competitiveness for this opportunity.",
  "strengths": [
    "Specific matching skill/experience 1 from resume",
    "Specific matching project or achievement 2",
    "Specific matching credential or background aspect 3",
    "Specific matching alignment with role 4"
  ],
  "skill_gaps": [
    {{
      "skill": "Name of missing skill, tool, or qualification",
      "importance": "High" | "Medium" | "Low",
      "advice": "Actionable advice on how to quickly bridge this gap before applying",
      "resource": "Specific recommended tutorial, documentation, course, or project idea"
    }}
  ],
  "roadmap": [
    {{
      "phase": "Phase 1: Resume & Profile Alignment",
      "timeline": "Days 1-3",
      "step_title": "Tailor Application Assets",
      "action_items": [
        "Action item 1 tailored to {opp_org}",
        "Action item 2"
      ]
    }},
    {{
      "phase": "Phase 2: Skill Gap Closure & Proof of Concept",
      "timeline": "Days 4-7",
      "step_title": "Build Targeted Artifact",
      "action_items": [
        "Action item 1",
        "Action item 2"
      ]
    }},
    {{
      "phase": "Phase 3: Strategic Outreach & Referral",
      "timeline": "Days 8-10",
      "step_title": "Connect with Decision Makers",
      "action_items": [
        "Action item 1",
        "Action item 2"
      ]
    }},
    {{
      "phase": "Phase 4: Final Submission & Interview Sprint",
      "timeline": "Days 11-14",
      "step_title": "Submit and Prepare Case Studies",
      "action_items": [
        "Action item 1",
        "Action item 2"
      ]
    }}
  ],
  "application_draft": "Full professional {draft_type} drafted specifically for {opp_title} at {opp_org}, referencing candidate's specific background and accomplishments."
}}
"""
            model_names = ['gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']
            for m in model_names:
                try:
                    model = genai.GenerativeModel(m)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        parsed = clean_json_response(response.text)
                        # Sanitize fields
                        parsed['match_score'] = int(max(10, min(99, parsed.get('match_score', 75))))
                        return parsed, False
                except Exception as model_err:
                    logger.warning(f"Gemini opportunity analysis failed with {m}: {model_err}")
                    continue
        except Exception as e:
            logger.warning(f"Live Gemini analysis failed, using fallback heuristic engine: {e}")

    # Fallback to intelligent deterministic heuristic analyzer
    return heuristic_analyze_opportunity(resume_obj, opportunity_obj, draft_type), True


def heuristic_analyze_opportunity(resume_obj, opportunity_obj, draft_type="Cover Letter") -> dict:
    """
    Intelligent heuristic engine that compares candidate skills against opportunity text,
    calculates real overlap, discovers missing keywords, and crafts tailored output.
    """
    candidate_name = resume_obj.get_candidate_name() if resume_obj else "Applicant"
    resume_skills = [s.lower() for s in (resume_obj.get_all_skills_flat() if resume_obj else [])]
    resume_text = (resume_obj.raw_text if resume_obj else "").lower()
    
    opp_text = f"{opportunity_obj.title} {opportunity_obj.organization} {opportunity_obj.description} {opportunity_obj.requirements}".lower()
    
    # Find matching taxonomy keywords
    all_tech = []
    for cat in TECH_TAXONOMY.values():
        all_tech.extend(cat)
    all_tech = list(dict.fromkeys(all_tech))
    
    required_keywords = [k for k in all_tech if re.search(r'\b' + re.escape(k) + r'\b', opp_text)]
    if not required_keywords:
        # Default typical requirements based on category
        if opportunity_obj.category in ['scholarship', 'fellowship', 'research']:
            required_keywords = ["research", "nlp", "python", "data science", "statistics", "data structures"]
        else:
            required_keywords = ["python", "django", "git", "rest api", "sql", "docker"]
            
    matched_skills = []
    missing_skills = []
    
    for kw in required_keywords:
        if kw in resume_skills or re.search(r'\b' + re.escape(kw) + r'\b', resume_text):
            matched_skills.append(kw.title())
        else:
            missing_skills.append(kw.title())
            
    # Calculate score
    total_req = len(required_keywords)
    overlap_ratio = len(matched_skills) / max(total_req, 1)
    
    # Base score with realistic bounds
    base_score = int(55 + (overlap_ratio * 40))
    match_score = min(96, max(38, base_score))
    
    if match_score >= 85:
        verdict = "Strong Match"
    elif match_score >= 70:
        verdict = "Competitive Match"
    elif match_score >= 50:
        verdict = "Moderate Match"
    else:
        verdict = "Reach Opportunity"
        
    # Build strengths
    strengths = []
    if matched_skills:
        strengths.append(f"Direct proficiency in key technical requirements: {', '.join(matched_skills[:4])}.")
    if resume_obj and resume_obj.get_experience_list():
        exp = resume_obj.get_experience_list()[0]
        strengths.append(f"Prior hands-on experience as {exp.get('role', 'Developer')} at {exp.get('company', 'prior organization')}.")
    if resume_obj and resume_obj.get_projects_list():
        proj = resume_obj.get_projects_list()[0]
        strengths.append(f"Demonstrated project portfolio in: '{proj.get('title', 'Software System')}', proving end-to-end execution.")
    strengths.append(f"Strong academic foundation with relevant coursework aligned with {opportunity_obj.organization}'s engineering domain.")

    # Build skill gaps
    if not missing_skills:
        missing_skills = ["System Design & Benchmarking", "Cloud Deployment (AWS/GCP)", "CI/CD Pipeline Automation"]
        
    skill_gaps = []
    for idx, skill in enumerate(missing_skills[:3]):
        importance = "High" if idx == 0 else "Medium"
        skill_gaps.append({
            "skill": skill,
            "importance": importance,
            "advice": f"Review {skill} core concepts and build a small proof-of-concept module demonstrating integration before submitting.",
            "resource": f"Official documentation and interactive guides for {skill} (e.g. FreeCodeCamp, Coursera, or GitHub repos)."
        })
        
    # Build personalized Roadmap
    roadmap = [
        {
            "phase": "Phase 1: Resume & Profile Alignment",
            "timeline": "Days 1–3",
            "step_title": f"Tailor Profile for {opportunity_obj.organization}",
            "action_items": [
                f"Highlight {', '.join(matched_skills[:3]) if matched_skills else 'core skills'} in top resume bullet points.",
                f"Frame project metrics to match {opportunity_obj.organization}'s specific mission and technical stack.",
                "Update LinkedIn headline and GitHub pinned repositories to showcase related work."
            ]
        },
        {
            "phase": "Phase 2: Skill Gap Closure & Proof of Concept",
            "timeline": "Days 4–7",
            "step_title": f"Address Missing Qualification ({missing_skills[0]})",
            "action_items": [
                f"Complete a 3-hour crash tutorial on {missing_skills[0]}.",
                f"Push a working GitHub sample demonstrating {missing_skills[0]} to your public profile.",
                "Draft brief talking points explaining how your current toolkit transfers into this domain."
            ]
        },
        {
            "phase": "Phase 3: Strategic Outreach & Referral Building",
            "timeline": "Days 8–10",
            "step_title": f"Connect with {opportunity_obj.organization} Engineers & Alumni",
            "action_items": [
                f"Identify 2-3 current engineers or former interns at {opportunity_obj.organization} on LinkedIn.",
                "Send personalized informational coffee chat requests sharing admiration for their team's recent initiatives.",
                "Request internal referrals or insights on team culture."
            ]
        },
        {
            "phase": "Phase 4: Application Submission & Interview Sprint",
            "timeline": "Days 11–14",
            "step_title": "Submit Final Packet & Practice Technical Scenarios",
            "action_items": [
                f"Review the generated {draft_type} and submit through the official portal before the deadline ({opportunity_obj.deadline}).",
                f"Prepare answers to common behavioral questions tailored to {opportunity_obj.organization}'s core values.",
                "Complete 3 mock technical coding or domain problem sessions."
            ]
        }
    ]

    # Build Application Draft
    draft = generate_heuristic_draft(
        candidate_name=candidate_name,
        resume_obj=resume_obj,
        opportunity_obj=opportunity_obj,
        draft_type=draft_type,
        matched_skills=matched_skills
    )

    summary = (
        f"{candidate_name} presents a {verdict.lower()} for the {opportunity_obj.title} position at {opportunity_obj.organization}. "
        f"With validated competencies in {', '.join(matched_skills[:3]) if matched_skills else 'software engineering'} "
        f"and solid project experience, the candidate meets core baseline expectations. "
        f"Addressing {missing_skills[0]} through the recommended roadmap will substantially elevate candidacy."
    )

    return {
        "match_score": match_score,
        "verdict": verdict,
        "summary": summary,
        "strengths": strengths,
        "skill_gaps": skill_gaps,
        "roadmap": roadmap,
        "application_draft": draft
    }


def generate_heuristic_draft(candidate_name: str, resume_obj, opportunity_obj, draft_type: str, matched_skills: list) -> str:
    """Generates tailored drafts (Cover Letter, Scholarship Statement, Cold Outreach)."""
    skills_str = ", ".join(matched_skills[:4]) if matched_skills else "Python, full-stack development, and modern software architectures"
    
    first_exp = ""
    if resume_obj and resume_obj.get_experience_list():
        e = resume_obj.get_experience_list()[0]
        first_exp = f"During my tenure as {e.get('role', 'Developer')} at {e.get('company', 'my previous team')}, I {e.get('description', 'developed scalable software solutions')}."
    else:
        first_exp = "Through intensive academic coursework and production-grade project development, I have built and optimized reliable software systems."

    first_proj = ""
    if resume_obj and resume_obj.get_projects_list():
        p = resume_obj.get_projects_list()[0]
        first_proj = f"For example, in my project '{p.get('title', 'Software Project')}', I utilized {p.get('tech', 'modern tools')} to solve real-world user challenges: {p.get('description', '')}."
        
    if draft_type == "Scholarship Statement" or opportunity_obj.category in ['scholarship', 'fellowship', 'research']:
        return f"""STATEMENT OF PURPOSE & ACADEMIC OBJECTIVES

Dear Selection Committee,

I am writing to express my enthusiastic application for the {opportunity_obj.title} with {opportunity_obj.organization}. As a dedicated student and researcher with a steadfast commitment to technological innovation and social impact, this opportunity represents the exact catalyst I seek to advance my academic and professional trajectory.

My academic journey has centered on developing robust solutions using {skills_str}. {first_exp} These formative experiences taught me the importance of analytical rigor, ethical inquiry, and collaborative problem-solving.

{first_proj}

What distinguishes the {opportunity_obj.title} at {opportunity_obj.organization} is its exceptional dedication to fostering leaders who bridge technical discovery with societal benefit. If selected, I intend to leverage this support to expand my research in accessible systems and contribute actively to the cohort's collaborative ethos.

Thank you for your consideration of my candidacy. I welcome the opportunity to discuss my qualifications and vision in greater detail.

Sincerely,

{candidate_name}
{resume_obj.parsed_data.get('email', '') if resume_obj else ''} | {resume_obj.parsed_data.get('phone', '') if resume_obj else ''}"""

    elif draft_type == "Cold Outreach Email":
        return f"""Subject: Expressing Interest in {opportunity_obj.title} - {candidate_name}

Hi {opportunity_obj.organization} Recruiting Team,

I hope you're having a wonderful week!

I recently came across the {opportunity_obj.title} opening at {opportunity_obj.organization} and was immediately drawn to your team's mission and engineering standards.

As a developer with experience in {skills_str}, I have built systems with a focus on performance and reliability. {first_exp}

I would welcome a brief 10-minute conversation to learn more about the team's upcoming challenges and share how my background could support your goals this term.

I have attached my resume for your review. Thank you for your time and consideration!

Best regards,

{candidate_name}
{resume_obj.parsed_data.get('email', '') if resume_obj else ''} | {resume_obj.parsed_data.get('linkedin', '') if resume_obj else ''}"""

    else: # Default Cover Letter
        return f"""COVER LETTER

Dear Hiring Team at {opportunity_obj.organization},

I am excited to submit my application for the {opportunity_obj.title} role at {opportunity_obj.organization}. With a strong foundation in {skills_str} and a passionate drive to build scalable, impactful software, I am eager to contribute immediately to your engineering objectives.

{first_exp}

{first_proj}

I admire {opportunity_obj.organization}'s commitment to technical excellence and user-centric design. The prospect of collaborating with your talented team on high-impact initiatives aligns seamlessly with my career aspirations and work ethic.

I am confident that my technical proficiency, proactive communication, and relentless curiosity will make me a valuable addition to your team. Thank you for considering my application. I look forward to the possibility of discussing my background in an interview.

Warm regards,

{candidate_name}
{resume_obj.parsed_data.get('email', '') if resume_obj else ''} | {resume_obj.parsed_data.get('phone', '') if resume_obj else ''}
{resume_obj.parsed_data.get('location', '') if resume_obj else ''}"""
