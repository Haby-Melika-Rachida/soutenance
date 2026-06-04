"""
tests/test_smoke.py
Tests de démarrage — vérifient que le projet Django se charge correctement.
Ces tests seront enrichis au fur et à mesure du développement des modules.
"""

import pytest
from django.test import TestCase


class TestDjangoSetup(TestCase):
    """Vérifie que le projet Django démarre sans erreur."""

    def test_django_settings_loaded(self):
        """Les settings Django sont correctement chargés."""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        self.assertIn('reconciliation', settings.INSTALLED_APPS)

    def test_database_connection(self):
        """La connexion à la base de données fonctionne."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        self.assertEqual(result[0], 1)


class TestProjectStructure(TestCase):
    """Vérifie que tous les packages du module sont importables."""

    def test_import_connectors(self):
        """Le package connectors est importable."""
        import reconciliation.connectors  # noqa: F401

    def test_import_engine(self):
        """Le package engine est importable."""
        import reconciliation.engine  # noqa: F401

    def test_import_batch(self):
        """Le package batch est importable."""
        import reconciliation.batch  # noqa: F401

    def test_import_models(self):
        """Le package models est importable."""
        import reconciliation.models  # noqa: F401

    def test_import_api(self):
        """Le package api est importable."""
        import reconciliation.api  # noqa: F401

    def test_import_notifications(self):
        """Le package notifications est importable."""
        import reconciliation.notifications  # noqa: F401

    def test_import_reports(self):
        """Le package reports est importable."""
        import reconciliation.reports  # noqa: F401
