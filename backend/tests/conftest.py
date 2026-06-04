"""
Fixtures pytest globales pour le module de rapprochement.
"""
import pytest
from django.contrib.auth.models import User


@pytest.fixture
def admin_user(db):
    """Crée un utilisateur admin pour les tests."""
    return User.objects.create_superuser(
        username='admin_test',
        password='testpass123',
        email='admin@test.com'
    )
