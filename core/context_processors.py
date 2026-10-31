from .models import Resume, Opportunity
from .services.gemini_service import is_gemini_configured

def global_context(request):
    """Provides project-wide variables to all templates."""
    active_resume = Resume.objects.filter(is_active=True).first()
    if not active_resume:
        active_resume = Resume.objects.order_by('-created_at').first()

    total_opps = Opportunity.objects.count()
    saved_count = Opportunity.objects.filter(status='saved').count()
    in_progress_count = Opportunity.objects.filter(status='applying').count()
    applied_count = Opportunity.objects.filter(status='applied').count()
    interview_count = Opportunity.objects.filter(status='interviewing').count()

    return {
        'is_gemini_configured': is_gemini_configured(),
        'active_resume': active_resume,
        'global_total_opps': total_opps,
        'global_saved_count': saved_count,
        'global_in_progress_count': in_progress_count,
        'global_applied_count': applied_count,
        'global_interview_count': interview_count,
    }
