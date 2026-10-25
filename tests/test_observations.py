import pytest
from datetime import date
from django.core.exceptions import ValidationError
from application.models import StudentObservation
from application.forms import StudentObservationForm
from application.services.prediction_service import run_student_prediction


@pytest.mark.django_db
class TestObservationModule:
    """Test cases for observation validation, persistence, and repeat submission handling."""

    def test_tc10_invalid_input_ranges_rejected(self, student_a):
        """TC10 — Verify out-of-range stress or sleep values fail form validation."""
        # 1. Stress > 5.0
        form_high_stress = StudentObservationForm(data={
            'date': '2026-10-15',
            'stress_mean': 6.5,  # Exceeds max 5.0
            'sleep_hours': 7.0,
        })
        assert not form_high_stress.is_valid()
        assert 'stress_mean' in form_high_stress.errors

        # 2. Stress < 1.0
        form_low_stress = StudentObservationForm(data={
            'date': '2026-10-15',
            'stress_mean': 0.5,  # Below min 1.0
            'sleep_hours': 7.0,
        })
        assert not form_low_stress.is_valid()
        assert 'stress_mean' in form_low_stress.errors

        # 3. Sleep > 24 hours
        form_extreme_sleep = StudentObservationForm(data={
            'date': '2026-10-15',
            'stress_mean': 3.0,
            'sleep_hours': 26.0,  # Impossible sleep
        })
        assert not form_extreme_sleep.is_valid()
        assert 'sleep_hours' in form_extreme_sleep.errors

    def test_tc09_repeat_submission_safe(self, student_a):
        """TC09 — Verify duplicate requests for the same date safely update rather than duplicate."""
        obs_date = date(2026, 10, 15)

        # First submission
        obs1 = StudentObservation.objects.create(
            student=student_a,
            date=obs_date,
            coursework_hours=3.0,
            stress_mean=2.5,
            sleep_hours=8.0
        )
        pred1, _ = run_student_prediction(obs1)

        # Repeat submission for same date
        obs1.coursework_hours = 4.0
        obs1.stress_mean = 3.0
        obs1.save()
        pred2, _ = run_student_prediction(obs1)

        # Observations count for student on this date should remain exactly 1
        count = StudentObservation.objects.filter(student=student_a, date=obs_date).count()
        assert count == 1

        # Prediction records for this date should update in-place, count = 1
        pred_count = student_a.predictions.filter(date=obs_date).count()
        assert pred_count == 1
