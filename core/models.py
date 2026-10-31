from django.db import models
from django.urls import reverse

class Resume(models.Model):
    """Stores uploaded resumes and extracted structured candidate profiles."""
    title = models.CharField(max_length=200, default="Primary Resume")
    file = models.FileField(upload_to="resumes/", null=True, blank=True)
    raw_text = models.TextField(blank=True)
    parsed_data = models.JSONField(default=dict, blank=True)
    skills_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        candidate_name = self.parsed_data.get('name') if isinstance(self.parsed_data, dict) else None
        return f"{self.title} ({candidate_name or 'Candidate'})"

    def save(self, *args, **kwargs):
        # Ensure only one resume is marked active if is_active is True
        if self.is_active:
            Resume.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        
        # Calculate skills count if available
        if isinstance(self.parsed_data, dict):
            skills = self.parsed_data.get('skills', [])
            if isinstance(skills, list):
                self.skills_count = len(skills)
            elif isinstance(skills, dict):
                self.skills_count = sum(len(v) for v in skills.values() if isinstance(v, list))
        super().save(*args, **kwargs)

    def get_candidate_name(self):
        if isinstance(self.parsed_data, dict):
            return self.parsed_data.get('name') or "Applicant"
        return "Applicant"

    def get_all_skills_flat(self):
        """Returns a flat list of unique skills for matching."""
        if not isinstance(self.parsed_data, dict):
            return []
        skills_data = self.parsed_data.get('skills', [])
        if isinstance(skills_data, list):
            return [str(s).strip() for s in skills_data if s]
        elif isinstance(skills_data, dict):
            flat = []
            for category_skills in skills_data.values():
                if isinstance(category_skills, list):
                    flat.extend([str(s).strip() for s in category_skills if s])
            return list(dict.fromkeys(flat))
        return []

    def get_education_list(self):
        if isinstance(self.parsed_data, dict):
            return self.parsed_data.get('education', [])
        return []

    def get_experience_list(self):
        if isinstance(self.parsed_data, dict):
            return self.parsed_data.get('experience', [])
        return []

    def get_projects_list(self):
        if isinstance(self.parsed_data, dict):
            return self.parsed_data.get('projects', [])
        return []


class Opportunity(models.Model):
    """Stores internship, scholarship, job, or fellowship opportunities."""
    CATEGORY_CHOICES = [
        ('internship', 'Internship'),
        ('scholarship', 'Scholarship'),
        ('job', 'Full-time Job'),
        ('fellowship', 'Fellowship'),
        ('research', 'Research / Grant'),
    ]

    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('applying', 'In Progress'),
        ('applied', 'Applied'),
        ('interviewing', 'Interviewing'),
        ('offered', 'Offer Received'),
        ('rejected', 'Not Selected'),
    ]

    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]

    title = models.CharField(max_length=255, help_text="e.g. Software Engineering Intern, Rhodes Scholarship")
    organization = models.CharField(max_length=255, help_text="e.g. Google, Oxford, Stripe, Gates Foundation")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='internship')
    location = models.CharField(max_length=255, blank=True, default='Remote / Flexible')
    deadline = models.CharField(max_length=100, blank=True, default='Rolling / Not Specified')
    url = models.URLField(blank=True, max_length=500)
    description = models.TextField(help_text="Paste the job or scholarship posting description and requirements here.")
    requirements = models.TextField(blank=True, help_text="Key requirements or eligibility criteria.")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='saved')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Opportunities"

    def __str__(self):
        return f"{self.title} at {self.organization}"

    def get_absolute_url(self):
        return reverse('opportunity_detail', kwargs={'pk': self.pk})

    @property
    def latest_analysis(self):
        return self.analyses.order_by('-created_at').first()

    @property
    def match_score(self):
        la = self.latest_analysis
        return la.match_score if la else None

    @property
    def status_badge_class(self):
        mapping = {
            'saved': 'bg-secondary-subtle text-secondary border border-secondary-subtle',
            'applying': 'bg-primary-subtle text-primary border border-primary-subtle',
            'applied': 'bg-info-subtle text-info border border-info-subtle',
            'interviewing': 'bg-warning-subtle text-warning border border-warning-subtle',
            'offered': 'bg-success-subtle text-success border border-success-subtle',
            'rejected': 'bg-danger-subtle text-danger border border-danger-subtle',
        }
        return mapping.get(self.status, 'bg-light text-dark')

    @property
    def category_badge_class(self):
        mapping = {
            'internship': 'badge-internship',
            'scholarship': 'badge-scholarship',
            'job': 'badge-job',
            'fellowship': 'badge-fellowship',
            'research': 'badge-research',
        }
        return mapping.get(self.category, 'badge-default')


class Analysis(models.Model):
    """Stores AI analysis results comparing a Resume against an Opportunity."""
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='analyses')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name='analyses')
    match_score = models.IntegerField(default=0, help_text="Calculated match score percentage (0-100)")
    verdict = models.CharField(max_length=100, default='Moderate Match')
    summary = models.TextField(blank=True, help_text="AI summary of applicant fit and overall assessment.")
    strengths = models.JSONField(default=list, blank=True, help_text="List of matching skills, experiences, and advantages.")
    skill_gaps = models.JSONField(default=list, blank=True, help_text="List of missing skills with advice and recommended learning.")
    roadmap = models.JSONField(default=list, blank=True, help_text="List of actionable step-by-step application milestones.")
    application_draft = models.TextField(blank=True, help_text="AI generated cover letter or personal statement.")
    draft_type = models.CharField(max_length=50, default='Cover Letter')
    is_demo_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Analyses"

    def __str__(self):
        return f"Analysis: {self.opportunity.title} ({self.match_score}%)"

    @property
    def score_color_class(self):
        if self.match_score >= 80:
            return 'success'
        elif self.match_score >= 60:
            return 'primary'
        elif self.match_score >= 40:
            return 'warning'
        return 'danger'
