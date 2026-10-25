import pytest
import numpy as np
from datetime import date, timedelta
from application.models import DigitalTwinState, StudentObservation, PredictionRecord
from application.services.digital_twin_service import (
    calculate_new_baseline,
    calculate_new_bias,
    calculate_feedback_signal,
    determine_response_pattern,
    is_adaptation_eligible,
    update_digital_twin_state,
    BASELINE_RATE,
    BIAS_RATE,
    MAX_BIAS,
    MIN_HISTORY,
)


@pytest.mark.django_db
class TestDigitalTwinStateModule:
    """
    Automated test cases for Digital Twin state-management and adaptation logic.
    """

    def test_tc03_minimum_history_gate(self, student_a):
        """TC03 — Verify personalization is not active before min history (5) is satisfied."""
        assert not is_adaptation_eligible(0)
        assert not is_adaptation_eligible(1)
        assert not is_adaptation_eligible(4)

        twin_state = student_a.digital_twin_state
        twin_state.observations = 3
        assert not twin_state.is_adaptation_active()

    def test_tc04_history_threshold_transition(self, student_a):
        """TC04 — Verify threshold behavior at exactly 5 and beyond."""
        assert is_adaptation_eligible(5)
        assert is_adaptation_eligible(6)
        assert is_adaptation_eligible(20)

        twin_state = student_a.digital_twin_state
        twin_state.observations = 5
        assert twin_state.is_adaptation_active()

        twin_state.observations = 10
        assert twin_state.is_adaptation_active()

    def test_tc05_residual_adaptation_equation(self):
        """
        TC05 — Verify residual update equation against independently calculated expected values:
        new_bias = (1 - 0.30) * old_bias + 0.30 * error
        """
        old_bias = 0.0
        error = 0.50
        # Expected: 0.70 * 0.0 + 0.30 * 0.50 = 0.150
        computed = calculate_new_bias(old_bias, error)
        assert pytest.approx(computed, abs=1e-5) == 0.150

        # Step 2:
        # new_bias = 0.70 * 0.150 + 0.30 * 0.20 = 0.105 + 0.060 = 0.165
        step2 = calculate_new_bias(computed, 0.20)
        assert pytest.approx(step2, abs=1e-5) == 0.165

    def test_tc06_adaptation_bounds(self):
        """TC06 — Verify that residual correction respects MAX_BIAS = 1.0 bounds."""
        # Extreme positive error
        extreme_pos = calculate_new_bias(0.8, 5.0)
        assert extreme_pos == MAX_BIAS

        # Extreme negative error
        extreme_neg = calculate_new_bias(-0.8, -5.0)
        assert extreme_neg == -MAX_BIAS

    def test_tc07_prediction_chronology_no_leakage(self, student_a):
        """
        TC07 — Verify current outcome is not used to generate its own prediction,
        and state updates occur only after prediction.
        """
        twin_state = student_a.digital_twin_state
        initial_bias = twin_state.bias_correction
        initial_obs = twin_state.observations

        # Before observation update, state is unchanged
        assert initial_bias == 0.0
        assert initial_obs == 0

        # Incorporate observation outcome
        update_digital_twin_state(
            twin_state,
            current_observed_stress=4.0,
            previous_prediction=None
        )

        assert twin_state.observations == 1
        assert twin_state.last_observed_stress == 4.0
        assert twin_state.personal_baseline_stress == 4.0

    def test_tc08_persistent_state_in_database(self, student_a):
        """TC08 — Verify state is saved and restored accurately from SQLite database."""
        twin_state = student_a.digital_twin_state
        twin_state.bias_correction = 0.25
        twin_state.personal_baseline_stress = 3.2
        twin_state.positive_feedback_count = 3
        twin_state.negative_feedback_count = 1
        twin_state.observations = 6
        twin_state.response_pattern = "Positive"
        twin_state.save()

        # Reload fresh instance from DB
        reloaded = DigitalTwinState.objects.get(student=student_a)
        assert pytest.approx(reloaded.bias_correction) == 0.25
        assert pytest.approx(reloaded.personal_baseline_stress) == 3.2
        assert reloaded.positive_feedback_count == 3
        assert reloaded.observations == 6
        assert reloaded.response_pattern == "Positive"
        assert reloaded.is_adaptation_active()

    def test_baseline_ema_update(self):
        """Verify personal baseline EMA: (1 - 0.20)*old + 0.20*observed."""
        # Initial baseline
        b0 = calculate_new_baseline(None, 3.0)
        assert b0 == 3.0

        # Update with 4.0: 0.8 * 3.0 + 0.2 * 4.0 = 2.4 + 0.8 = 3.2
        b1 = calculate_new_baseline(b0, 4.0)
        assert pytest.approx(b1, abs=1e-5) == 3.2

    def test_directional_feedback_and_patterns(self):
        """Verify directional adaptation signal and pattern classification."""
        assert calculate_feedback_signal(-0.5) == 1   # Decreased stress
        assert calculate_feedback_signal(0.4) == -1   # Increased stress
        assert calculate_feedback_signal(0.0) == 0    # No change

        assert determine_response_pattern(0, 0) == "Insufficient history"
        assert determine_response_pattern(4, 1) == "Positive"  # 4 > 1.5 * 1
        assert determine_response_pattern(1, 4) == "Negative"  # 4 > 1.5 * 1
        assert determine_response_pattern(2, 2) == "Mixed"
