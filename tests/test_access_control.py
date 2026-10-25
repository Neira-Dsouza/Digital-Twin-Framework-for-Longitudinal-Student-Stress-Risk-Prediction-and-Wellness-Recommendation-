import pytest
from django.urls import reverse
from datetime import date
from application.models import PredictionRecord, StudentObservation


@pytest.mark.django_db
class TestAccessControlAndIsolation:
    """Test cases for strict cross-student data isolation and authorization."""

    def test_tc13_cross_student_user_isolation(self, client, student_a, student_b):
        """TC13 — Verify that one student cannot retrieve another student's prediction record."""
        # Create prediction for Student A
        pred_a = PredictionRecord.objects.create(
            student=student_a,
            date=date(2026, 10, 15),
            global_prediction=3.2,
            adaptive_prediction=3.2,
            prediction_mechanism="Global Gradient Boosting"
        )

        # Log in as Student B
        client.force_login(student_b)

        # Attempt to access Student A's prediction detail
        url = reverse('prediction_detail', kwargs={'pk': pred_a.pk})
        response = client.get(url)

        # Must return 404 Not Found (or 403 Forbidden), never exposing Student A's data
        assert response.status_code == 404

    def test_tc14_dashboard_authentication_and_integration(self, client, student_a):
        """TC14 — Verify unauthenticated users are redirected, and authenticated users see own dashboard."""
        dash_url = reverse('dashboard')

        # 1. Unauthenticated request -> redirects to login
        res_anon = client.get(dash_url)
        assert res_anon.status_code == 302
        assert '/login/' in res_anon.url

        # 2. Authenticated request -> 200 OK with student's profile context
        client.force_login(student_a)
        res_auth = client.get(dash_url)
        assert res_auth.status_code == 200
        assert student_a.profile.display_name.encode() in res_auth.content

    def test_tc15_csv_export_student_scoped(self, client, student_a, student_b):
        """TC15 — Verify CSV export contains only records belonging to the requesting student."""
        # Create record for Student A
        PredictionRecord.objects.create(
            student=student_a,
            date=date(2026, 10, 15),
            global_prediction=2.85,
            adaptive_prediction=2.85,
            prediction_mechanism="Global Gradient Boosting",
            shap_top_factor="sleep_hours_rolling_7d"
        )

        # Create record for Student B
        PredictionRecord.objects.create(
            student=student_b,
            date=date(2026, 10, 15),
            global_prediction=4.15,
            adaptive_prediction=4.15,
            prediction_mechanism="Global Gradient Boosting",
            shap_top_factor="assignments_due_rolling_7d"
        )

        # Log in as Student A and download CSV
        client.force_login(student_a)
        export_url = reverse('export_csv')
        response = client.get(export_url)

        assert response.status_code == 200
        assert response['Content-Type'] == 'text/csv'
        content = response.content.decode('utf-8')

        # Must contain Student A's data
        assert "2.85" in content
        assert "sleep_hours_rolling_7d" in content

        # MUST NOT contain Student B's data
        assert "4.15" not in content
        assert "assignments_due_rolling_7d" not in content
