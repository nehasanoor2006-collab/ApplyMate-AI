from django.test import TestCase, Client
from django.urls import reverse
from core.models import Resume, Opportunity, Analysis
from core.services.sample_data import SAMPLE_RESUMES, SAMPLE_OPPORTUNITIES
from core.services.gemini_service import analyze_opportunity_fit, parse_resume_content

class ApplyMateCoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Seed test resume
        sample = SAMPLE_RESUMES["tech_intern"]
        self.resume = Resume.objects.create(
            title=sample["title"],
            raw_text=sample["raw_text"],
            parsed_data=sample["parsed_data"],
            is_active=True
        )
        
        # Seed test opportunity
        opp_sample = SAMPLE_OPPORTUNITIES[0]
        self.opportunity = Opportunity.objects.create(
            title=opp_sample["title"],
            organization=opp_sample["organization"],
            category=opp_sample["category"],
            location=opp_sample["location"],
            deadline=opp_sample["deadline"],
            description=opp_sample["description"],
            requirements=opp_sample["requirements"],
            status="saved"
        )

    def test_dashboard_view(self):
        """Test dashboard renders successfully."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ApplyMate")
        self.assertContains(response, self.resume.get_candidate_name())

    def test_resume_view(self):
        """Test resume page renders active resume information."""
        response = self.client.get(reverse('resume'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alex Chen")
        self.assertContains(response, "UC Berkeley")

    def test_opportunity_list_view(self):
        """Test opportunities list view."""
        response = self.client.get(reverse('opportunity_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.opportunity.organization)
        self.assertContains(response, "Software Engineering Intern")

    def test_opportunity_create_view(self):
        """Test creating a new opportunity."""
        post_data = {
            'title': 'Test Machine Learning Engineer Intern',
            'organization': 'DeepMind',
            'category': 'internship',
            'location': 'London / Remote',
            'deadline': 'Dec 15, 2026',
            'url': 'https://deepmind.google',
            'description': 'Work with DeepMind researchers on frontier reasoning models using Python, PyTorch, and reinforcement learning.',
            'requirements': 'Python, PyTorch, Deep Learning foundation',
            'priority': 'high',
            'auto_analyze': 'on',
        }
        response = self.client.post(reverse('opportunity_create'), data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        new_opp = Opportunity.objects.filter(organization='DeepMind').first()
        self.assertIsNotNone(new_opp)
        # Should have auto-analyzed
        self.assertTrue(new_opp.analyses.exists())
        latest = new_opp.latest_analysis
        self.assertGreater(latest.match_score, 0)
        self.assertTrue(len(latest.strengths) > 0)
        self.assertTrue(len(latest.roadmap) > 0)
        self.assertTrue(len(latest.application_draft) > 50)

    def test_analysis_service(self):
        """Test AI fit analyzer produces complete structured diagnostics."""
        analysis_data, is_demo = analyze_opportunity_fit(self.resume, self.opportunity, draft_type="Cover Letter")
        self.assertIn('match_score', analysis_data)
        self.assertIn('verdict', analysis_data)
        self.assertIn('strengths', analysis_data)
        self.assertIn('skill_gaps', analysis_data)
        self.assertIn('roadmap', analysis_data)
        self.assertIn('application_draft', analysis_data)
        self.assertGreaterEqual(analysis_data['match_score'], 0)
        self.assertLessEqual(analysis_data['match_score'], 100)

    def test_opportunity_status_update(self):
        """Test updating opportunity status."""
        response = self.client.post(
            reverse('opportunity_status_update', kwargs={'pk': self.opportunity.pk}),
            {'status': 'interviewing'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.status, 'interviewing')

    def test_demo_dataset_seeder(self):
        """Test 1-click showcase seeder initializes full environment."""
        response = self.client.get(reverse('load_demo_dataset'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(Opportunity.objects.count(), 4)
        self.assertGreaterEqual(Analysis.objects.count(), 4)

    def test_discovery_service_matching(self):
        """Test opportunity discovery engine matches and ranks opportunities for candidate profile."""
        from core.services.discovery_service import discover_opportunities_for_resume
        results = discover_opportunities_for_resume(self.resume)
        self.assertTrue(len(results) > 0)
        # Check sorted descending
        scores = [r['match_score'] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Verify official sources are present
        source_names = [r.get('source_name') for r in results]
        self.assertTrue(any('AICTE' in str(s) for s in source_names))
        self.assertTrue(any('National Scholarship Portal' in str(s) for s in source_names))
        
        # Verify item fields
        top = results[0]
        self.assertIn('match_score', top)
        self.assertIn('match_tier', top)
        self.assertIn('matching_skills', top)
        self.assertIn('missing_skills', top)
        self.assertIn('explanation', top)
        self.assertIn('url', top)

    def test_discover_opportunities_view(self):
        """Test discovery dashboard page renders with ranked opportunities and sources."""
        response = self.client.get(reverse('discover_opportunities'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Opportunity Discovery Agent")
        self.assertContains(response, "AICTE National Internship Portal")
        self.assertContains(response, "National Scholarship Portal")
        self.assertContains(response, "Best Matches")

    def test_discover_save_opportunity(self):
        """Test saving a discovered opportunity directly into user's tracker."""
        response = self.client.post(
            reverse('discover_save_opportunity'),
            {'opportunity_id': 'aicte-cisco-cybersecurity'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        saved = Opportunity.objects.filter(title__icontains='CISCO').first()
        self.assertIsNotNone(saved)
        self.assertEqual(saved.status, 'saved')
        self.assertIn('AICTE', saved.organization)

    def test_discover_analyze_opportunity(self):
        """Test analyzing a discovered opportunity seamlessly creates opportunity and analysis."""
        response = self.client.post(
            reverse('discover_analyze_opportunity'),
            {'opportunity_id': 'aicte-ibm-cloud-ai'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        analyzed_opp = Opportunity.objects.filter(title__icontains='IBM').first()
        self.assertIsNotNone(analyzed_opp)
        self.assertTrue(analyzed_opp.analyses.exists())
        latest = analyzed_opp.latest_analysis
        self.assertGreater(latest.match_score, 0)
        self.assertContains(response, "AICTE - IBM SkillsBuild")

