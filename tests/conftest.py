import pytest
from django.contrib.auth.models import User
from application.models import StudentProfile, DigitalTwinState


@pytest.fixture
def student_a(db):
    user = User.objects.create_user(
        username="student_alice",
        email="alice@university.edu",
        password="ValidPassword123!"
    )
    StudentProfile.objects.create(
        user=user,
        student_id="u01",
        display_name="Alice Student",
        department="Computer Science",
        year_of_study="Year 3"
    )
    DigitalTwinState.objects.create(student=user)
    return user


@pytest.fixture
def student_b(db):
    user = User.objects.create_user(
        username="student_bob",
        email="bob@university.edu",
        password="ValidPassword123!"
    )
    StudentProfile.objects.create(
        user=user,
        student_id="u02",
        display_name="Bob Student",
        department="Psychology",
        year_of_study="Year 2"
    )
    DigitalTwinState.objects.create(student=user)
    return user
