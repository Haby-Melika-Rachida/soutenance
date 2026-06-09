"""Tests de démarrage du projet Django."""

from django.test import TestCase


class TestDjangoSetup(TestCase):
    """Vérifie que le projet Django démarre sans erreur."""

    def test_django_settings_loaded(self):
        """Les settings Django sont correctement chargés."""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        self.assertIn('apps.core', settings.INSTALLED_APPS)
        self.assertIn('apps.matching', settings.INSTALLED_APPS)

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
        import apps.connectors  # noqa: F401

    def test_import_engine(self):
        """Le package engine est importable."""
        import apps.matching.engine  # noqa: F401

    def test_import_batch(self):
        """Le package batch est importable."""
        import apps.batch  # noqa: F401

    def test_import_models(self):
        """Le package models est importable."""
        import apps.core.models  # noqa: F401

    def test_import_api(self):
        """Le package api est importable."""
        import apps.api  # noqa: F401

    def test_import_notifications(self):
        """Le package notifications est importable."""
        import apps.notifications  # noqa: F401

    def test_import_reports(self):
        """Le package reports est importable."""
        import apps.reports  # noqa: F401
