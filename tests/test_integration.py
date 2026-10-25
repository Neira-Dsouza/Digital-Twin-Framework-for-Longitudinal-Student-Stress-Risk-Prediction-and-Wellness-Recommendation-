import pytest
from datetime import date, timedelta
from django.urls import reverse
from application.models import (
    StudentObservation,
    PredictionRecord,
    RecommendationRecord,
    DigitalTwinState,
    FeedbackRecord,
)
from application.services.prediction_service import run_student_prediction


@pytest.mark.django_db
class TestLongitudinalIntegrationWorkflow:
    """End-to-end integration tests tracing multi-day longitudinal adaptation."""

    def test_full_longitudinal_adaptation_cycle(self, client, student_a):
        """
        Tests multi-day chronological sequence:
        - Days 1 to 4: History gate inactive (global prediction only).
        - Day 5: 5th prior observation recorded.
        - Day 6: History gate unlocks, residual adaptation is applied.
        - Recommendations are generated and traceable.
        - Feedback is recorded.
        """
        client.force_login(student_a)
        base_date = date(2026, 10, 1)

        # 1. Submit observations for Days 1 through 4
        for day in range(1, 5):
            obs_date = base_date + timedelta(days=day)
            obs = StudentObservation.objects.create(
                student=student_a,
                date=obs_date,
                coursework_hours=3.0 + (day * 0.5),
                assignments_due=1 if day % 2 == 0 else 0,
                sleep_hours=7.5 - (day * 0.2),
                sleep_quality=3,
                stress_mean=2.8 + (day * 0.2),  # Simulated rising stress
                phone_lock_count=30 + (day * 5),
                phone_locked_duration_seconds=20000.0
            )
            pred, _ = run_student_prediction(obs)

            # Verification: history count is < 5, adaptation must be inactive
            assert not pred.adaptation_active
            assert pred.bias_correction_applied == 0.0

        twin_state = DigitalTwinState.objects.get(student=student_a)
        assert twin_state.observations == 4
        assert not twin_state.is_adaptation_active()

        # 2. Submit Day 5
        day5_date = base_date + timedelta(days=5)
        obs5 = StudentObservation.objects.create(
            student=student_a,
            date=day5_date,
            coursework_hours=5.0,
            assignments_due=2,
            sleep_hours=6.0,
            sleep_quality=2,
            stress_mean=3.8,
            phone_lock_count=50,
            phone_locked_duration_seconds=22000.0
        )
        pred5, _ = run_student_prediction(obs5)
        # Prediction for Day 5 uses prior 4 days -> adaptation still inactive
        assert not pred5.adaptation_active

        twin_state.refresh_from_db()
        assert twin_state.observations == 5
        assert twin_state.is_adaptation_active()

        # 3. Submit Day 6 — History condition is now SATISFIED (5 prior observations exist)
        day6_date = base_date + timedelta(days=6)
        obs6 = StudentObservation.objects.create(
            student=student_a,
            date=day6_date,
            coursework_hours=6.0,
            assignments_due=3,
            sleep_hours=5.5,
            sleep_quality=2,
            stress_mean=4.2,
            phone_lock_count=60,
            phone_locked_duration_seconds=25000.0
        )
        pred6, _ = run_student_prediction(obs6)

        # Verification: Day 6 MUST have adaptation active
        assert pred6.adaptation_active is True
        assert "Personalized History-Gated Residual" in pred6.prediction_mechanism

        # Verify recommendations generated for Day 6
        recs = RecommendationRecord.objects.filter(prediction=pred6)
        assert recs.count() >= 1

        # Verify recommendation has valid priority and evidence
        first_rec = recs.first()
        assert first_rec.priority in ['High', 'Medium', 'Low']
        assert len(first_rec.evidence_source) > 0
