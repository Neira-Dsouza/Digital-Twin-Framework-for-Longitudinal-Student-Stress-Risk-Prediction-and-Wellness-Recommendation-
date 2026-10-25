import pytest
import numpy as np
import pandas as pd
from datetime import date
from application.models import StudentObservation, PredictionRecord
from application.services.model_loader import load_research_model, get_feature_names, EXPECTED_FEATURE_COUNT
from application.services.feature_builder import build_feature_vector
from application.services.prediction_service import run_student_prediction


@pytest.mark.django_db
class TestPredictionService:
    """Automated test cases for model loading, feature schemas, and inference."""

    def test_tc01_valid_prediction(self, student_a):
        """TC01 — Verify that valid model inputs produce a finite numerical prediction in [1.0, 5.0]."""
        obs = StudentObservation.objects.create(
            student=student_a,
            date=date(2026, 10, 15),
            coursework_hours=4.0,
            assignments_due=2,
            sleep_hours=7.0,
            sleep_quality=3,
            stress_mean=3.0,
            activity_0_hours=6.0,
            phone_lock_count=45,
            phone_locked_duration_seconds=24000.0
        )

        pred_record, explanation = run_student_prediction(obs)

        assert isinstance(pred_record.adaptive_prediction, float)
        assert np.isfinite(pred_record.adaptive_prediction)
        assert 1.0 <= pred_record.adaptive_prediction <= 5.0
        assert 1.0 <= pred_record.global_prediction <= 5.0
        assert pred_record.prediction_mechanism is not None

    def test_tc02_input_schema_and_feature_contract(self):
        """
        TC02 — Verify that the feature adapter produces exactly 53 features
        in the exact order expected by the model pipeline, and handles missing fields via imputer.
        """
        model, expected_features = load_research_model()
        assert len(expected_features) == EXPECTED_FEATURE_COUNT

        # Build feature vector with missing optional values
        partial_obs = {
            'coursework_hours': 3.5,
            'assignments_due': None,  # Missing
            'sleep_hours': None,      # Missing
            'stress_mean': None,       # Missing
        }

        feature_df = build_feature_vector(partial_obs, prior_observations_qs=[])

        # Verify exact column match and ordering
        assert list(feature_df.columns) == expected_features
        assert len(feature_df.columns) == 53

        # Verify imputer transforms missing values without error
        imputer = model.named_steps['imputer']
        X_imputed = imputer.transform(feature_df)
        assert X_imputed.shape == (1, 53)
        assert not np.isnan(X_imputed).any()

        # Verify model generates valid finite prediction
        pred = model.predict(feature_df)[0]
        assert np.isfinite(pred)
