from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Resume Management
    path('resume/', views.resume_view, name='resume'),
    path('resume/upload/', views.resume_upload, name='resume_upload'),
    path('resume/<int:pk>/active/', views.resume_select_active, name='resume_select_active'),
    path('resume/<int:pk>/delete/', views.resume_delete, name='resume_delete'),
    path('resume/sample/<str:sample_type>/', views.resume_load_sample, name='resume_load_sample'),
    
    # Opportunities & AI Tracking
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/new/', views.opportunity_create, name='opportunity_create'),
    path('opportunities/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:pk>/analyze/', views.opportunity_analyze, name='opportunity_analyze'),
    path('opportunities/<int:pk>/draft/', views.opportunity_regenerate_draft, name='opportunity_regenerate_draft'),
    path('opportunities/<int:pk>/status/', views.opportunity_status_update, name='opportunity_status_update'),
    path('opportunities/<int:pk>/delete/', views.opportunity_delete, name='opportunity_delete'),
    
    # Opportunity Discovery Agent
    path('discover/', views.discover_opportunities, name='discover_opportunities'),
    path('discover/save/', views.discover_save_opportunity, name='discover_save_opportunity'),
    path('discover/analyze/', views.discover_analyze_opportunity, name='discover_analyze_opportunity'),
    
    # 1-Click Showcase Seeder
    path('demo/seed/', views.load_demo_dataset, name='load_demo_dataset'),
]
