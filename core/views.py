import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Count, Q
from django.views.decorators.http import require_POST, require_http_methods

from .models import Resume, Opportunity, Analysis
from .services.pdf_parser import extract_text_from_pdf, PDFExtractionError
from .services.gemini_service import (
    parse_resume_content,
    analyze_opportunity_fit,
    is_gemini_configured
)
from .services.sample_data import SAMPLE_RESUMES, SAMPLE_OPPORTUNITIES
from .services.discovery_service import (
    discover_opportunities_for_resume,
    get_discovery_by_id,
    CURATED_DISCOVERY_OPPORTUNITIES
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# DASHBOARD
# -------------------------------------------------------------------------

def dashboard(request):
    """Main application dashboard with application metrics, recent analyses, and quick actions."""
    active_resume = Resume.objects.filter(is_active=True).first() or Resume.objects.order_by('-created_at').first()
    
    total_opportunities = Opportunity.objects.count()
    analyses_count = Analysis.objects.count()
    
    # Calculate average match score
    avg_score_val = Analysis.objects.aggregate(avg=Avg('match_score'))['avg']
    avg_match_score = round(avg_score_val) if avg_score_val is not None else None
    
    # Opportunities by status
    status_counts = {
        'saved': Opportunity.objects.filter(status='saved').count(),
        'applying': Opportunity.objects.filter(status='applying').count(),
        'applied': Opportunity.objects.filter(status='applied').count(),
        'interviewing': Opportunity.objects.filter(status='interviewing').count(),
        'offered': Opportunity.objects.filter(status='offered').count(),
        'rejected': Opportunity.objects.filter(status='rejected').count(),
    }
    
    # Opportunities by category
    category_counts = {
        'internship': Opportunity.objects.filter(category='internship').count(),
        'scholarship': Opportunity.objects.filter(category='scholarship').count(),
        'job': Opportunity.objects.filter(category='job').count(),
        'fellowship': Opportunity.objects.filter(category='fellowship').count(),
        'research': Opportunity.objects.filter(category='research').count(),
    }
    
    # Recent analyzed opportunities
    recent_analyses = Analysis.objects.select_related('opportunity', 'resume').order_by('-created_at')[:4]
    
    # Recent opportunities for table
    recent_opportunities = Opportunity.objects.prefetch_related('analyses').order_by('-created_at')[:6]
    
    context = {
        'active_resume': active_resume,
        'total_opportunities': total_opportunities,
        'analyses_count': analyses_count,
        'avg_match_score': avg_match_score,
        'status_counts': status_counts,
        'category_counts': category_counts,
        'recent_analyses': recent_analyses,
        'recent_opportunities': recent_opportunities,
        'is_gemini_active': is_gemini_configured(),
    }
    return render(request, 'core/dashboard.html', context)


# -------------------------------------------------------------------------
# RESUME MANAGEMENT
# -------------------------------------------------------------------------

def resume_view(request):
    """View active resume profile, extracted sections, skills breakdown, and upload controls."""
    active_resume = Resume.objects.filter(is_active=True).first() or Resume.objects.order_by('-created_at').first()
    all_resumes = Resume.objects.order_by('-created_at')
    
    context = {
        'active_resume': active_resume,
        'all_resumes': all_resumes,
        'is_gemini_active': is_gemini_configured(),
    }
    return render(request, 'core/resume.html', context)


@require_POST
def resume_upload(request):
    """Handles PDF resume upload, PyPDF2 text extraction, and AI structured parsing."""
    if 'resume_file' not in request.FILES:
        messages.error(request, "Please select a PDF resume file to upload.")
        return redirect('resume')
        
    uploaded_file = request.FILES['resume_file']
    
    # Validate extension
    if not uploaded_file.name.lower().endswith('.pdf'):
        messages.error(request, "Invalid file format. Only .pdf files are supported.")
        return redirect('resume')
        
    # Validate file size (limit to 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        messages.error(request, "File size exceeds the 10MB limit. Please upload a smaller PDF.")
        return redirect('resume')
        
    try:
        # Extract text via PyPDF2
        extracted_text = extract_text_from_pdf(uploaded_file)
        
        # Parse into structured sections via Gemini or heuristic engine
        parsed_data, is_demo_mode = parse_resume_content(extracted_text)
        
        # Create Resume model instance
        title = request.POST.get('title', '').strip() or f"Resume - {uploaded_file.name}"
        resume = Resume(
            title=title,
            file=uploaded_file,
            raw_text=extracted_text,
            parsed_data=parsed_data,
            is_active=True
        )
        resume.save()
        
        engine_msg = "via Demo Engine" if is_demo_mode else "via Live Gemini API"
        candidate_name = resume.get_candidate_name()
        messages.success(
            request,
            f"Successfully parsed and extracted resume for {candidate_name} ({engine_msg})!"
        )
        return redirect('resume')
        
    except PDFExtractionError as e:
        messages.error(request, str(e))
        return redirect('resume')
    except Exception as e:
        logger.exception("Unexpected error processing resume upload")
        messages.error(request, f"An unexpected error occurred while analyzing the resume: {str(e)}")
        return redirect('resume')


@require_POST
def resume_select_active(request, pk):
    """Sets the chosen resume as the active resume for opportunities."""
    resume = get_object_or_404(Resume, pk=pk)
    resume.is_active = True
    resume.save()
    messages.success(request, f"'{resume.title}' is now your active resume.")
    return redirect('resume')


@require_POST
def resume_delete(request, pk):
    """Deletes a resume record."""
    resume = get_object_or_404(Resume, pk=pk)
    title = resume.title
    resume.delete()
    
    # Ensure at least one remaining resume is marked active
    remaining = Resume.objects.order_by('-created_at').first()
    if remaining:
        remaining.is_active = True
        remaining.save()
        
    messages.success(request, f"Resume '{title}' deleted.")
    return redirect('resume')


def resume_load_sample(request, sample_type="tech_intern"):
    """Loads a rich pre-configured sample resume into the database."""
    sample = SAMPLE_RESUMES.get(sample_type, SAMPLE_RESUMES["tech_intern"])
    
    resume = Resume.objects.create(
        title=sample["title"],
        raw_text=sample["raw_text"],
        parsed_data=sample["parsed_data"],
        is_active=True
    )
    
    messages.success(
        request,
        f"Loaded sample profile: '{sample['title']}'! Ready to analyze opportunities."
    )
    return redirect('resume')


# -------------------------------------------------------------------------
# OPPORTUNITY MANAGEMENT & TRACKING
# -------------------------------------------------------------------------

def opportunity_list(request):
    """Filterable opportunity tracking board and list view."""
    opportunities = Opportunity.objects.prefetch_related('analyses').all()
    
    # Filter by category
    category = request.GET.get('category', '').strip()
    if category and category != 'all':
        opportunities = opportunities.filter(category=category)
        
    # Filter by status
    status = request.GET.get('status', '').strip()
    if status and status != 'all':
        opportunities = opportunities.filter(status=status)
        
    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        opportunities = opportunities.filter(
            Q(title__icontains=query) |
            Q(organization__icontains=query) |
            Q(description__icontains=query) |
            Q(requirements__icontains=query)
        )
        
    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        opportunities = opportunities.order_by('created_at')
    elif sort == 'deadline':
        opportunities = opportunities.order_by('deadline')
    else:
        opportunities = opportunities.order_by('-created_at')
        
    context = {
        'opportunities': opportunities,
        'selected_category': category or 'all',
        'selected_status': status or 'all',
        'search_query': query,
        'sort_by': sort,
        'categories': Opportunity.CATEGORY_CHOICES,
        'statuses': Opportunity.STATUS_CHOICES,
    }
    return render(request, 'core/opportunity_list.html', context)


def opportunity_create(request):
    """Create a new opportunity with manual input or 1-click sample template pre-fills."""
    active_resume = Resume.objects.filter(is_active=True).first() or Resume.objects.order_by('-created_at').first()
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        organization = request.POST.get('organization', '').strip()
        category = request.POST.get('category', 'internship').strip()
        location = request.POST.get('location', 'Remote / Flexible').strip()
        deadline = request.POST.get('deadline', 'Rolling').strip()
        url = request.POST.get('url', '').strip()
        description = request.POST.get('description', '').strip()
        requirements = request.POST.get('requirements', '').strip()
        priority = request.POST.get('priority', 'medium').strip()
        
        if not title or not organization or not description:
            messages.error(request, "Please provide the Opportunity Title, Organization, and Description.")
            return render(request, 'core/opportunity_form.html', {
                'categories': Opportunity.CATEGORY_CHOICES,
                'priorities': Opportunity.PRIORITY_CHOICES,
                'sample_opportunities': SAMPLE_OPPORTUNITIES,
                'active_resume': active_resume,
            })
            
        opp = Opportunity.objects.create(
            title=title,
            organization=organization,
            category=category,
            location=location,
            deadline=deadline,
            url=url,
            description=description,
            requirements=requirements,
            priority=priority,
            status='saved'
        )
        
        # If user checked "Analyze Immediately" and active resume exists:
        auto_analyze = request.POST.get('auto_analyze') == 'on'
        if auto_analyze and active_resume:
            draft_type = "Scholarship Statement" if category in ['scholarship', 'fellowship'] else "Cover Letter"
            analysis_data, is_demo_mode = analyze_opportunity_fit(active_resume, opp, draft_type=draft_type)
            Analysis.objects.create(
                opportunity=opp,
                resume=active_resume,
                match_score=analysis_data.get('match_score', 75),
                verdict=analysis_data.get('verdict', 'Competitive Match'),
                summary=analysis_data.get('summary', ''),
                strengths=analysis_data.get('strengths', []),
                skill_gaps=analysis_data.get('skill_gaps', []),
                roadmap=analysis_data.get('roadmap', []),
                application_draft=analysis_data.get('application_draft', ''),
                draft_type=draft_type,
                is_demo_mode=is_demo_mode
            )
            messages.success(request, f"Opportunity created and AI Eligibility analysis completed!")
            return redirect('opportunity_detail', pk=opp.pk)
            
        messages.success(request, f"Opportunity '{opp.title}' saved successfully.")
        return redirect('opportunity_detail', pk=opp.pk)
        
    return render(request, 'core/opportunity_form.html', {
        'categories': Opportunity.CATEGORY_CHOICES,
        'priorities': Opportunity.PRIORITY_CHOICES,
        'sample_opportunities': SAMPLE_OPPORTUNITIES,
        'active_resume': active_resume,
    })


def opportunity_detail(request, pk):
    """Detailed view showing Opportunity information, AI Match Score, Skill Gaps, Roadmap & Draft."""
    opp = get_object_or_404(Opportunity, pk=pk)
    active_resume = Resume.objects.filter(is_active=True).first() or Resume.objects.order_by('-created_at').first()
    latest_analysis = opp.analyses.order_by('-created_at').first()
    
    context = {
        'opp': opp,
        'analysis': latest_analysis,
        'active_resume': active_resume,
        'statuses': Opportunity.STATUS_CHOICES,
        'is_gemini_active': is_gemini_configured(),
    }
    return render(request, 'core/opportunity_detail.html', context)


@require_POST
def opportunity_analyze(request, pk):
    """Runs or re-runs AI eligibility analysis for an opportunity against the active resume."""
    opp = get_object_or_404(Opportunity, pk=pk)
    active_resume = Resume.objects.filter(is_active=True).first() or Resume.objects.order_by('-created_at').first()
    
    if not active_resume:
        messages.warning(
            request,
            "Please upload or load a sample resume first before running the AI Eligibility Checker."
        )
        return redirect('resume')
        
    draft_type = request.POST.get('draft_type', 'Cover Letter')
    if opp.category in ['scholarship', 'fellowship'] and draft_type == 'Cover Letter':
        draft_type = "Scholarship Statement"
        
    analysis_data, is_demo_mode = analyze_opportunity_fit(active_resume, opp, draft_type=draft_type)
    
    analysis = Analysis.objects.create(
        opportunity=opp,
        resume=active_resume,
        match_score=analysis_data.get('match_score', 75),
        verdict=analysis_data.get('verdict', 'Competitive Match'),
        summary=analysis_data.get('summary', ''),
        strengths=analysis_data.get('strengths', []),
        skill_gaps=analysis_data.get('skill_gaps', []),
        roadmap=analysis_data.get('roadmap', []),
        application_draft=analysis_data.get('application_draft', ''),
        draft_type=draft_type,
        is_demo_mode=is_demo_mode
    )
    
    engine_note = "Demo Mode" if is_demo_mode else "Live Gemini AI"
    messages.success(
        request,
        f"AI Opportunity Analysis completed ({engine_note})! Eligibility Match: {analysis.match_score}%."
    )
    return redirect('opportunity_detail', pk=opp.pk)


@require_POST
def opportunity_regenerate_draft(request, pk):
    """Regenerates only the application draft with a new draft type (Cover Letter, Scholarship Statement, Cold Email)."""
    opp = get_object_or_404(Opportunity, pk=pk)
    active_resume = Resume.objects.filter(is_active=True).first() or Resume.objects.order_by('-created_at').first()
    draft_type = request.POST.get('draft_type', 'Cover Letter')
    
    if not active_resume:
        messages.error(request, "Active resume is required to generate tailored drafts.")
        return redirect('opportunity_detail', pk=opp.pk)
        
    analysis_data, is_demo_mode = analyze_opportunity_fit(active_resume, opp, draft_type=draft_type)
    
    latest_analysis = opp.analyses.order_by('-created_at').first()
    if latest_analysis:
        latest_analysis.application_draft = analysis_data.get('application_draft', '')
        latest_analysis.draft_type = draft_type
        latest_analysis.is_demo_mode = is_demo_mode
        latest_analysis.save()
    else:
        Analysis.objects.create(
            opportunity=opp,
            resume=active_resume,
            match_score=analysis_data.get('match_score', 75),
            verdict=analysis_data.get('verdict', 'Competitive Match'),
            summary=analysis_data.get('summary', ''),
            strengths=analysis_data.get('strengths', []),
            skill_gaps=analysis_data.get('skill_gaps', []),
            roadmap=analysis_data.get('roadmap', []),
            application_draft=analysis_data.get('application_draft', ''),
            draft_type=draft_type,
            is_demo_mode=is_demo_mode
        )
        
    messages.success(request, f"Application draft regenerated as '{draft_type}'!")
    return redirect('opportunity_detail', pk=opp.pk)


@require_POST
def opportunity_status_update(request, pk):
    """Updates opportunity tracking status (saved, applying, applied, interviewing, offered, rejected)."""
    opp = get_object_or_404(Opportunity, pk=pk)
    new_status = request.POST.get('status', '').strip()
    
    valid_statuses = [choice[0] for choice in Opportunity.STATUS_CHOICES]
    if new_status in valid_statuses:
        opp.status = new_status
        opp.save()
        messages.success(request, f"Updated '{opp.title}' status to '{opp.get_status_display()}'.")
    else:
        messages.error(request, "Invalid status selected.")
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'new_status': opp.status, 'display': opp.get_status_display()})
        
    return redirect(request.META.get('HTTP_REFERER', 'opportunity_list'))


@require_POST
def opportunity_delete(request, pk):
    """Deletes an opportunity and associated analyses."""
    opp = get_object_or_404(Opportunity, pk=pk)
    title = opp.title
    opp.delete()
    messages.success(request, f"Opportunity '{title}' deleted.")
    return redirect('opportunity_list')


# -------------------------------------------------------------------------
# 1-CLICK DEMO DATASET SEEDER
# -------------------------------------------------------------------------

def load_demo_dataset(request):
    """
    Seeds a complete, realistic demo environment with 1 click:
    - Alex Chen Resume (Tech Intern Profile)
    - 4 Sample Opportunities (Google SWE, Fulbright Scholarship, Stripe Systems, OpenAI Fellowship)
    - Automatically executes AI analysis for each so all dashboards, gauges, and drafts are fully populated!
    """
    # 1. Create or ensure Alex Chen resume
    alex_sample = SAMPLE_RESUMES["tech_intern"]
    resume, _ = Resume.objects.get_or_create(
        title=alex_sample["title"],
        defaults={
            "raw_text": alex_sample["raw_text"],
            "parsed_data": alex_sample["parsed_data"],
            "is_active": True
        }
    )
    resume.is_active = True
    resume.save()
    
    # 2. Seed opportunities
    created_count = 0
    for sample in SAMPLE_OPPORTUNITIES:
        opp, created = Opportunity.objects.get_or_create(
            title=sample["title"],
            organization=sample["organization"],
            defaults={
                "category": sample["category"],
                "location": sample["location"],
                "deadline": sample["deadline"],
                "url": sample.get("url", ""),
                "priority": sample.get("priority", "medium"),
                "description": sample["description"],
                "requirements": sample.get("requirements", ""),
                "status": "applied" if "Google" in sample["title"] else ("applying" if "Fulbright" in sample["title"] else "saved")
            }
        )
        if created:
            created_count += 1
            
        # Run AI analysis if not already analyzed
        if not opp.analyses.exists():
            draft_type = "Scholarship Statement" if opp.category in ['scholarship', 'fellowship'] else "Cover Letter"
            analysis_data, is_demo_mode = analyze_opportunity_fit(resume, opp, draft_type=draft_type)
            Analysis.objects.create(
                opportunity=opp,
                resume=resume,
                match_score=analysis_data.get('match_score', 80),
                verdict=analysis_data.get('verdict', 'Competitive Match'),
                summary=analysis_data.get('summary', ''),
                strengths=analysis_data.get('strengths', []),
                skill_gaps=analysis_data.get('skill_gaps', []),
                roadmap=analysis_data.get('roadmap', []),
                application_draft=analysis_data.get('application_draft', ''),
                draft_type=draft_type,
                is_demo_mode=is_demo_mode
            )

    messages.success(
        request,
        f"Demo dataset initialized! Loaded candidate profile and {len(SAMPLE_OPPORTUNITIES)} fully analyzed opportunities."
    )
    return redirect('dashboard')


# -------------------------------------------------------------------------
# OPPORTUNITY DISCOVERY AGENT
# -------------------------------------------------------------------------

def discover_opportunities(request):
    """
    Opportunity Discovery Agent Dashboard.
    Scans candidate's active resume and recommends matching internships,
    scholarships, and fellowships from official portals (AICTE, NSP, Tech Portals).
    Ranks opportunities into Best Matches, Good Matches, and Opportunities to Explore.
    """
    active_resume = Resume.objects.filter(is_active=True).first() or Resume.objects.order_by('-created_at').first()
    
    # Query parameters
    category = request.GET.get('category', 'all').strip()
    tier_filter = request.GET.get('tier', 'all').strip()
    query = request.GET.get('q', '').strip()
    
    # Retrieve all matched opportunities for active profile
    all_discovered = discover_opportunities_for_resume(
        resume_obj=active_resume,
        category_filter=category if category != 'all' else None,
        search_query=query if query else None
    )
    
    # Calculate tier counts
    best_count = sum(1 for o in all_discovered if o['match_tier'] == 'best')
    good_count = sum(1 for o in all_discovered if o['match_tier'] == 'good')
    explore_count = sum(1 for o in all_discovered if o['match_tier'] == 'explore')
    total_count = len(all_discovered)
    
    # Apply tier filter if selected
    if tier_filter in ['best', 'good', 'explore']:
        displayed_opportunities = [o for o in all_discovered if o['match_tier'] == tier_filter]
    else:
        displayed_opportunities = all_discovered
        
    context = {
        'active_resume': active_resume,
        'opportunities': displayed_opportunities,
        'all_opportunities': all_discovered,
        'total_count': total_count,
        'best_count': best_count,
        'good_count': good_count,
        'explore_count': explore_count,
        'selected_category': category,
        'selected_tier': tier_filter,
        'search_query': query,
        'categories': Opportunity.CATEGORY_CHOICES,
        'is_gemini_active': is_gemini_configured(),
    }
    return render(request, 'core/discover.html', context)


@require_POST
def discover_save_opportunity(request):
    """
    Saves a discovered opportunity directly into the user's Opportunity tracker board.
    Reuses the existing Opportunity model and prevents duplicates.
    """
    opp_id = request.POST.get('opportunity_id', '').strip()
    opp_data = get_discovery_by_id(opp_id)
    
    if not opp_data:
        messages.error(request, "Opportunity definition not found.")
        return redirect('discover_opportunities')
        
    # Check if opportunity already exists by title & org
    opp, created = Opportunity.objects.get_or_create(
        title=opp_data['title'],
        organization=opp_data['organization'],
        defaults={
            'category': opp_data['category'],
            'location': opp_data.get('location', 'Remote / Flexible'),
            'deadline': opp_data.get('deadline', 'Rolling'),
            'url': opp_data.get('url', ''),
            'priority': opp_data.get('priority', 'medium'),
            'description': opp_data.get('description', ''),
            'requirements': opp_data.get('requirements', ''),
            'status': 'saved',
            'notes': f"Discovered via {opp_data.get('source_name', 'ApplyMate Discovery Agent')}."
        }
    )
    
    if created:
        messages.success(request, f"Saved '{opp.title}' to your application tracker!")
    else:
        messages.info(request, f"'{opp.title}' is already in your application tracker.")
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'created': created,
            'opp_id': opp.pk,
            'message': f"'{opp.title}' is saved in your tracker."
        })
        
    return redirect(request.META.get('HTTP_REFERER', 'discover_opportunities'))


@require_POST
def discover_analyze_opportunity(request):
    """
    Initiates deep AI Eligibility analysis for a discovered opportunity against candidate's active resume.
    Seamlessly creates the Opportunity (if not already tracked) and runs analyze_opportunity_fit(),
    creating an Analysis instance and redirecting to the flagship Opportunity Detail page.
    """
    opp_id = request.POST.get('opportunity_id', '').strip()
    opp_data = get_discovery_by_id(opp_id)
    
    active_resume = Resume.objects.filter(is_active=True).first() or Resume.objects.order_by('-created_at').first()
    if not active_resume:
        messages.warning(request, "Please upload or select an active resume first to run AI fit analysis.")
        return redirect('resume')
        
    if not opp_data:
        messages.error(request, "Opportunity definition not found.")
        return redirect('discover_opportunities')
        
    # Get or create Opportunity model instance
    opp, _ = Opportunity.objects.get_or_create(
        title=opp_data['title'],
        organization=opp_data['organization'],
        defaults={
            'category': opp_data['category'],
            'location': opp_data.get('location', 'Remote / Flexible'),
            'deadline': opp_data.get('deadline', 'Rolling'),
            'url': opp_data.get('url', ''),
            'priority': opp_data.get('priority', 'medium'),
            'description': opp_data.get('description', ''),
            'requirements': opp_data.get('requirements', ''),
            'status': 'saved',
            'notes': f"Discovered via {opp_data.get('source_name', 'ApplyMate Discovery Agent')}."
        }
    )
    
    # Check if an analysis for this resume and opportunity already exists
    existing_analysis = opp.analyses.filter(resume=active_resume).order_by('-created_at').first()
    if existing_analysis:
        messages.info(request, f"Loaded existing AI evaluation for '{opp.title}'.")
        return redirect('opportunity_detail', pk=opp.pk)
        
    # Run AI Fit Analysis
    draft_type = "Scholarship Statement" if opp.category in ['scholarship', 'fellowship'] else "Cover Letter"
    analysis_data, is_demo_mode = analyze_opportunity_fit(active_resume, opp, draft_type=draft_type)
    
    analysis = Analysis.objects.create(
        opportunity=opp,
        resume=active_resume,
        match_score=analysis_data.get('match_score', 75),
        verdict=analysis_data.get('verdict', 'Competitive Match'),
        summary=analysis_data.get('summary', ''),
        strengths=analysis_data.get('strengths', []),
        skill_gaps=analysis_data.get('skill_gaps', []),
        roadmap=analysis_data.get('roadmap', []),
        application_draft=analysis_data.get('application_draft', ''),
        draft_type=draft_type,
        is_demo_mode=is_demo_mode
    )
    
    engine_note = "Demo Engine" if is_demo_mode else "Live Gemini AI"
    messages.success(
        request,
        f"AI Fit Diagnostics completed for '{opp.title}' ({engine_note})! Match Score: {analysis.match_score}%."
    )
    return redirect('opportunity_detail', pk=opp.pk)

