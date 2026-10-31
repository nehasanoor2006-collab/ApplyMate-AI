from django.contrib import admin
from .models import Resume, Opportunity, Analysis

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_candidate_name', 'skills_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'raw_text')

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'category', 'status', 'deadline', 'priority', 'created_at')
    list_filter = ('category', 'status', 'priority')
    search_fields = ('title', 'organization', 'description', 'requirements')

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'resume', 'match_score', 'verdict', 'is_demo_mode', 'created_at')
    list_filter = ('verdict', 'is_demo_mode', 'created_at')
    search_fields = ('opportunity__title', 'summary')
