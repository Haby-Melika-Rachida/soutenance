"""
Fixtures pytest globales pour le module de rapprochement.
"""
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def admin_user(db):
    """Crée un utilisateur admin pour les tests."""
    return get_user_model().objects.create_superuser(
        username='admin_test',
        password='testpass123',
        email='admin@test.com'
    )
