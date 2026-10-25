import pytest
from application.models import PredictionRecord
from application.services.recommendation_service import (
    generate_recommendations_for_prediction,
    get_stress_severity,
)


@pytest.mark.django_db
class TestRecommendationService:
    """Test cases for evidence-grounded recommendation engine."""

    def test_tc11_recommendation_traceability_and_grounding(self, student_a):
        """
        TC11 — Verify generated recommendations can be traced to actual identified factors
        and evidence metadata is grounded in verifiable sources rather than fabricated.
        """
        pred_record = PredictionRecord.objects.create(
            student=student_a,
            date='2026-10-15',
            global_prediction=3.8,
            adaptive_prediction=3.8,
            prediction_mechanism="Global Gradient Boosting"
        )

        top_factors = [
            {
                'feature': 'coursework_hours_rolling_7d',
                'label': 'Coursework Hours (7-day avg)',
                'category': 'Academic',
                'shap_value': 0.18,
                'direction': 'increases',
            },
            {
                'feature': 'sleep_hours_rolling_7d',
                'label': 'Sleep Hours (7-day avg)',
                'category': 'Wellness',
                'shap_value': 0.12,
                'direction': 'increases',
            }
        ]

        recs = generate_recommendations_for_prediction(pred_record, top_factors)

        assert len(recs) >= 1
        # First rec must correspond to academic factor
        rec1 = recs[0]
        assert 'Academic Workload' in rec1['category']
        assert 'Coursework' in rec1['factor_name']
        assert rec1['priority'] == 'High'  # Because stress 3.8 >= 3.5 High severity
        assert 'StudentLife' in rec1['evidence_source']
        assert 'contributing positively (+0.18)' in rec1['rationale']

    def test_stress_severity_classification(self):
        """Verify severity brackets."""
        assert get_stress_severity(1.8) == 'Low'
        assert get_stress_severity(3.0) == 'Moderate'
        assert get_stress_severity(3.8) == 'High'
        assert get_stress_severity(4.8) == 'Very High'
