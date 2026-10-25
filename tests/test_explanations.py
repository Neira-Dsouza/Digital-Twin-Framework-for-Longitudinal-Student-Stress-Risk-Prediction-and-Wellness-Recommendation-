import pytest
import pandas as pd
from application.services.model_loader import load_research_model
from application.services.feature_builder import build_feature_vector
from application.services.explanation_service import explain_prediction


class TestExplanationService:
    """Test cases for SHAP feature attribution and graceful degradation."""

    def test_shap_explanation_generation(self):
        """Verify SHAP produces valid feature attributions and expected value."""
        model, _ = load_research_model()
        obs_dict = {
            'coursework_hours': 6.0,
            'assignments_due': 3,
            'sleep_hours': 5.0,
            'stress_mean': 3.5,
        }
        feature_df = build_feature_vector(obs_dict, prior_observations_qs=[])
        explanation = explain_prediction(model, feature_df)

        assert explanation['available'] is True
        assert 'expected_value' in explanation
        assert len(explanation['top_factors']) > 0
        assert explanation['primary_factor'] is not None

        # Check factor structure
        top = explanation['top_factors'][0]
        assert 'feature' in top
        assert 'shap_value' in top
        assert 'direction' in top
        assert top['direction'] in ['increases', 'decreases']

    def test_tc12_missing_explanation_graceful(self):
        """TC12 — Verify that unavailable SHAP output is handled gracefully without inventing values."""
        # Pass a mock or object that cannot compute tree SHAP
        dummy_model = None
        feature_df = pd.DataFrame([{'dummy': 1.0}])

        explanation = explain_prediction(dummy_model, feature_df)

        assert explanation['available'] is False
        assert len(explanation['top_factors']) == 0
        assert explanation['primary_factor'] is None
        assert 'unavailable' in explanation.get('message', '').lower()
