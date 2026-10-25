import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from application.models import StudentProfile, DigitalTwinState


@pytest.mark.django_db
class TestAuthenticationModule:
    """Test cases for registration, login, profile initialization, and logout."""

    def test_user_registration_and_twin_initialization(self, client):
        """Verify registration automatically creates StudentProfile and DigitalTwinState."""
        reg_url = reverse('register')
        post_data = {
            'username': 'new_student',
            'email': 'new_student@university.edu',
            'display_name': 'New Student User',
            'department': 'Electrical Engineering',
            'year_of_study': 'Year 2',
            'password1': 'StrongP@ssw0rd2026!',
            'password2': 'StrongP@ssw0rd2026!',
        }

        response = client.post(reg_url, data=post_data, follow=True)
        assert response.status_code == 200

        # Verify User created
        user = User.objects.get(username='new_student')
        assert user.email == 'new_student@university.edu'

        # Verify StudentProfile created
        profile = StudentProfile.objects.get(user=user)
        assert profile.display_name == 'New Student User'
        assert profile.department == 'Electrical Engineering'

        # Verify DigitalTwinState initialized
        twin = DigitalTwinState.objects.get(student=user)
        assert twin.observations == 0
        assert not twin.is_adaptation_active()
