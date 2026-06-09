"""
Tests unitaires — MatchingEngine.

Chaque méthode est testée en isolation avec des données contrôlées.
Tous les tests accèdent à la DB (pytest.mark.django_db) : l'engine écrit
directement des EcartDetecte via bulk_create.
"""

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from apps.core.models import (
    ConfigurationBatch,
    CriticiteChoices,
    CyclePI,
    DirectionPIChoices,
    EcartDetecte,
    ReconciliationSession,
    TransactionCBS,
    TransactionMB,
    TypeEcartChoices,
    TypeFluxChoices,
)
from apps.matching.engine import MatchingEngine


# ═══════════════════════════════════════════════════════════════
# FIXTURES & FACTORIES
# ═══════════════════════════════════════════════════════════════

DATE = date(2024, 1, 15)
TS = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)


@pytest.fixture
def cfg(db):
    return ConfigurationBatch.objects.create(nom="test", date_tolerance_days=0)


@pytest.fixture
def session(db, cfg):
    return ReconciliationSession.objects.create(
        date_traitement=DATE,
        configuration=cfg,
    )


@pytest.fixture
def engine(session):
    return MatchingEngine(session)


# ── Factories ────────────────────────────────────────────────────────────────

def make_mb(session, e2e="E2E-001", type_flux=TypeFluxChoices.CBS_SIMPLE, **kw):
    return TransactionMB.objects.create(
        session=session,
        message_id=f"{e2e}-MSG",
        end_to_end_id=e2e,
        montant=Decimal("1000.00"),
        compte_debiteur="BF-DEBIT",
        statut="EXECUTED",
        type_flux=type_flux,
        date_operation=DATE,
        **kw,
    )


def make_cbs(session, e2e="E2E-001", is_pi=False, ts=None, **kw):
    return TransactionCBS.objects.create(
        session=session,
        msg_id=f"{e2e}-CBS",
        end_to_end_id=e2e,
        montant=Decimal("1000.00"),
        debtor_account="BF-DEBIT",
        transaction_status="ACSC",
        is_pi_transfer=is_pi,
        timestamp=ts or TS,
        **kw,
    )


def make_pi(
    session,
    e2e="E2E-PI-001",
    direction=DirectionPIChoices.EMISSION,
    statut="COMPLETED",
    funds_reserved=True,
    funds_debited=True,
    funds_credited=True,
    **kw,
):
    return CyclePI.objects.create(
        session=session,
        message_id=f"{e2e}-PI",
        end_to_end_id=e2e,
        direction=direction,
        montant=Decimal("5000.00"),
        funds_reserved=funds_reserved,
        funds_debited=funds_debited,
        funds_credited=funds_credited,
        statut=statut,
        date_operation=DATE,
        **kw,
    )


# ═══════════════════════════════════════════════════════════════
# EC-01 : FANTÔMES MB
# ═══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestDetecterFantomesMB:

    def test_no_ecart_when_all_mb_matched(self, engine, session):
        make_mb(session, "E1")
        make_cbs(session, "E1")
        assert engine.detecter_fantomes_mb() == 0
        assert EcartDetecte.objects.filter(session=session).count() == 0

    def test_ec01_created_for_unmatched_mb(self, engine, session):
        make_mb(session, "E1")   # pas de CBS correspondant
        count = engine.detecter_fantomes_mb()
        assert count == 1
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_ecart == TypeEcartChoices.EC_01
        assert ecart.reference == "E1"

    def test_ec01_only_for_unmatched_mb(self, engine, session):
        make_mb(session, "E1")   # matchée
        make_cbs(session, "E1")
        make_mb(session, "E2")   # fantôme
        count = engine.detecter_fantomes_mb()
        assert count == 1
        assert EcartDetecte.objects.filter(type_ecart=TypeEcartChoices.EC_01).count() == 1

    def test_ec01_multiple_unmatched_mb(self, engine, session):
        for i in range(3):
            make_mb(session, f"E{i}")
        assert engine.detecter_fantomes_mb() == 3

    def test_ec01_criticite_is_critique(self, engine, session):
        make_mb(session, "E1")
        engine.detecter_fantomes_mb()
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.criticite == CriticiteChoices.CRITIQUE

    def test_ec01_type_flux_from_mb(self, engine, session):
        make_mb(session, "E1", type_flux=TypeFluxChoices.PI_EMISSION)
        engine.detecter_fantomes_mb()
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_flux == TypeFluxChoices.PI_EMISSION

    def test_ec01_reference_and_montant(self, engine, session):
        make_mb(session, "E1", montant=Decimal("9999.99"))
        engine.detecter_fantomes_mb()
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.reference == "E1"
        assert ecart.montant == Decimal("9999.99")

    def test_ec01_no_ecart_when_no_mb_transactions(self, engine, session):
        assert engine.detecter_fantomes_mb() == 0

    def test_ec01_returns_count(self, engine, session):
        make_mb(session, "E1")
        make_mb(session, "E2")
        assert engine.detecter_fantomes_mb() == 2

    def test_ec01_uses_date_tolerance(self, cfg, session):
        """CBS daté J+1 doit être ignoré avec tolerance=0."""
        cfg.date_tolerance_days = 0
        cfg.save()
        ts_tomorrow = datetime(2024, 1, 16, 10, 0, tzinfo=timezone.utc)
        make_mb(session, "E1")
        make_cbs(session, "E1", ts=ts_tomorrow)   # hors fenêtre J±0
        count = MatchingEngine(session).detecter_fantomes_mb()
        assert count == 1  # CBS hors fenêtre → MB toujours considéré fantôme


# ═══════════════════════════════════════════════════════════════
# EC-02 : FANTÔMES CBS
# ═══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestDetecterFantomesCBS:

    def test_no_ecart_when_all_cbs_matched(self, engine, session):
        make_mb(session, "E1")
        make_cbs(session, "E1")
        assert engine.detecter_fantomes_cbs() == 0

    def test_ec02_created_for_unmatched_cbs(self, engine, session):
        make_cbs(session, "E1")   # pas de MB correspondant
        count = engine.detecter_fantomes_cbs()
        assert count == 1
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_ecart == TypeEcartChoices.EC_02
        assert ecart.reference == "E1"

    def test_ec02_only_for_unmatched_cbs(self, engine, session):
        make_mb(session, "E1")
        make_cbs(session, "E1")   # matchée
        make_cbs(session, "E2")   # fantôme
        assert engine.detecter_fantomes_cbs() == 1

    def test_ec02_multiple_unmatched_cbs(self, engine, session):
        for i in range(4):
            make_cbs(session, f"E{i}")
        assert engine.detecter_fantomes_cbs() == 4

    def test_ec02_type_flux_cbs_simple_when_not_pi(self, engine, session):
        make_cbs(session, "E1", is_pi=False)
        engine.detecter_fantomes_cbs()
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_flux == TypeFluxChoices.CBS_SIMPLE

    def test_ec02_type_flux_pi_emission_when_is_pi(self, engine, session):
        make_cbs(session, "E1", is_pi=True)
        engine.detecter_fantomes_cbs()
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_flux == TypeFluxChoices.PI_EMISSION

    def test_ec02_criticite_is_critique(self, engine, session):
        make_cbs(session, "E1")
        engine.detecter_fantomes_cbs()
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.criticite == CriticiteChoices.CRITIQUE

    def test_ec02_no_ecart_when_no_cbs_transactions(self, engine, session):
        assert engine.detecter_fantomes_cbs() == 0


# ═══════════════════════════════════════════════════════════════
# EC-03 / EC-04 : DOUBLONS
# ═══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestDetecterDoublons:

    def test_no_ecart_when_no_duplicates(self, engine, session):
        make_mb(session, "E1")
        make_cbs(session, "E1")
        assert engine.detecter_doublons() == 0

    def test_no_ecart_when_no_transactions(self, engine, session):
        assert engine.detecter_doublons() == 0

    # ── EC-03 : doublons MB ───────────────────────────────────────────────

    def test_ec03_two_mb_for_one_cbs(self, engine, session):
        make_mb(session, "E1")
        make_mb(session, "E1")   # doublon
        make_cbs(session, "E1")
        count = engine.detecter_doublons()
        assert count == 1
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_ecart == TypeEcartChoices.EC_03
        assert ecart.reference == "E1"

    def test_ec03_three_mb_for_one_cbs(self, engine, session):
        """3 MB pour 1 CBS → toujours 1 seul EC-03 (par e2e)."""
        for _ in range(3):
            make_mb(session, "E1")
        make_cbs(session, "E1")
        assert engine.detecter_doublons() == 1

    def test_ec03_not_raised_without_cbs_counterpart(self, engine, session):
        """2 MB sans CBS → pas d'EC-03 (serait EC-01, pas le rôle de detecter_doublons)."""
        make_mb(session, "E1")
        make_mb(session, "E1")
        assert engine.detecter_doublons() == 0

    def test_ec03_criticite_is_critique(self, engine, session):
        make_mb(session, "E1")
        make_mb(session, "E1")
        make_cbs(session, "E1")
        engine.detecter_doublons()
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.criticite == CriticiteChoices.CRITIQUE

    # ── EC-04 : doublons CBS ──────────────────────────────────────────────

    def test_ec04_two_cbs_for_one_mb(self, engine, session):
        make_mb(session, "E1")
        make_cbs(session, "E1")
        make_cbs(session, "E1")   # doublon
        count = engine.detecter_doublons()
        assert count == 1
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_ecart == TypeEcartChoices.EC_04
        assert ecart.reference == "E1"

    def test_ec04_not_raised_without_mb_counterpart(self, engine, session):
        """2 CBS sans MB → pas d'EC-04."""
        make_cbs(session, "E1")
        make_cbs(session, "E1")
        assert engine.detecter_doublons() == 0

    def test_ec04_type_flux_cbs_simple_when_not_pi(self, engine, session):
        make_mb(session, "E1")
        make_cbs(session, "E1", is_pi=False)
        make_cbs(session, "E1", is_pi=False)
        engine.detecter_doublons()
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_flux == TypeFluxChoices.CBS_SIMPLE

    def test_ec04_type_flux_pi_emission_when_pi(self, engine, session):
        make_mb(session, "E1")
        make_cbs(session, "E1", is_pi=True)
        make_cbs(session, "E1", is_pi=True)
        engine.detecter_doublons()
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_flux == TypeFluxChoices.PI_EMISSION

    # ── EC-03 + EC-04 simultanés ──────────────────────────────────────────

    def test_ec03_and_ec04_detected_together(self, engine, session):
        # E1 : 2 MB, 1 CBS → EC-03
        make_mb(session, "E1")
        make_mb(session, "E1")
        make_cbs(session, "E1")
        # E2 : 1 MB, 2 CBS → EC-04
        make_mb(session, "E2")
        make_cbs(session, "E2")
        make_cbs(session, "E2")

        count = engine.detecter_doublons()

        assert count == 2
        assert EcartDetecte.objects.filter(type_ecart=TypeEcartChoices.EC_03).count() == 1
        assert EcartDetecte.objects.filter(type_ecart=TypeEcartChoices.EC_04).count() == 1

    def test_doublons_returns_total_count(self, engine, session):
        """La valeur de retour est la somme EC-03 + EC-04."""
        make_mb(session, "E1"); make_mb(session, "E1"); make_cbs(session, "E1")
        make_mb(session, "E2"); make_cbs(session, "E2"); make_cbs(session, "E2")
        assert engine.detecter_doublons() == 2


# ═══════════════════════════════════════════════════════════════
# EC-05 / EC-06 : CYCLES PI
# ═══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestAnalyserCyclesPI:

    def test_no_ecart_when_all_cycles_complete(self, engine, session):
        make_pi(session, funds_debited=True, funds_credited=True, statut="IRREVOCABLE")
        assert engine.analyser_cycles_pi() == 0

    def test_no_ecart_for_non_irrevocable_statut(self, engine, session):
        """Cycles non-IRREVOCABLE ignorés même si funds manquants."""
        make_pi(session, statut="PENDING", funds_debited=False, funds_credited=False)
        make_pi(session, statut="COMPLETED", funds_debited=False, funds_credited=False)
        make_pi(session, statut="REJECTED", funds_debited=False, funds_credited=False)
        assert engine.analyser_cycles_pi() == 0

    def test_no_ecart_when_no_pi_cycles(self, engine, session):
        assert engine.analyser_cycles_pi() == 0

    # ── EC-05 : non débité ────────────────────────────────────────────────

    def test_ec05_irrevocable_funds_not_debited(self, engine, session):
        make_pi(session, statut="IRREVOCABLE", funds_debited=False, funds_credited=True)
        count = engine.analyser_cycles_pi()
        assert count == 1
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_ecart == TypeEcartChoices.EC_05

    def test_ec05_reference_and_montant(self, engine, session):
        make_pi(session, "PI-42", statut="IRREVOCABLE",
                funds_debited=False, funds_credited=True, montant=Decimal("7777.00"))
        engine.analyser_cycles_pi()
        ecart = EcartDetecte.objects.get(type_ecart=TypeEcartChoices.EC_05)
        assert ecart.reference == "PI-42"
        assert ecart.montant == Decimal("7777.00")

    # ── EC-06 : non crédité ───────────────────────────────────────────────

    def test_ec06_irrevocable_funds_not_credited(self, engine, session):
        make_pi(session, statut="IRREVOCABLE", funds_debited=True, funds_credited=False)
        count = engine.analyser_cycles_pi()
        assert count == 1
        ecart = EcartDetecte.objects.get(session=session)
        assert ecart.type_ecart == TypeEcartChoices.EC_06

    def test_ec06_reference_and_montant(self, engine, session):
        make_pi(session, "PI-99", statut="IRREVOCABLE",
                funds_debited=True, funds_credited=False, montant=Decimal("3333.00"))
        engine.analyser_cycles_pi()
        ecart = EcartDetecte.objects.get(type_ecart=TypeEcartChoices.EC_06)
        assert ecart.reference == "PI-99"
        assert ecart.montant == Decimal("3333.00")

    # ── EC-05 + EC-06 sur le même cycle ──────────────────────────────────

    def test_ec05_and_ec06_both_raised_on_same_cycle(self, engine, session):
        """Un cycle IRREVOCABLE avec funds_debited=False ET funds_credited=False
        génère deux écarts distincts."""
        make_pi(session, "PI-BOTH", statut="IRREVOCABLE",
                funds_debited=False, funds_credited=False)

        count = engine.analyser_cycles_pi()

        assert count == 2
        assert EcartDetecte.objects.filter(
            type_ecart=TypeEcartChoices.EC_05, reference="PI-BOTH"
        ).count() == 1
        assert EcartDetecte.objects.filter(
            type_ecart=TypeEcartChoices.EC_06, reference="PI-BOTH"
        ).count() == 1

    # ── Direction → type_flux ─────────────────────────────────────────────

    def test_ec05_direction_emission_sets_pi_emission(self, engine, session):
        make_pi(session, direction=DirectionPIChoices.EMISSION,
                statut="IRREVOCABLE", funds_debited=False, funds_credited=True)
        engine.analyser_cycles_pi()
        ecart = EcartDetecte.objects.get(type_ecart=TypeEcartChoices.EC_05)
        assert ecart.type_flux == TypeFluxChoices.PI_EMISSION

    def test_ec05_direction_reception_sets_pi_reception(self, engine, session):
        make_pi(session, direction=DirectionPIChoices.RECEPTION,
                statut="IRREVOCABLE", funds_debited=False, funds_credited=True)
        engine.analyser_cycles_pi()
        ecart = EcartDetecte.objects.get(type_ecart=TypeEcartChoices.EC_05)
        assert ecart.type_flux == TypeFluxChoices.PI_RECEPTION

    def test_ec06_direction_reception_sets_pi_reception(self, engine, session):
        make_pi(session, direction=DirectionPIChoices.RECEPTION,
                statut="IRREVOCABLE", funds_debited=True, funds_credited=False)
        engine.analyser_cycles_pi()
        ecart = EcartDetecte.objects.get(type_ecart=TypeEcartChoices.EC_06)
        assert ecart.type_flux == TypeFluxChoices.PI_RECEPTION

    def test_statut_irrevocable_case_insensitive(self, engine, session):
        """'irrevocable' (minuscules) doit être traité comme 'IRREVOCABLE'."""
        make_pi(session, statut="irrevocable", funds_debited=False, funds_credited=True)
        assert engine.analyser_cycles_pi() == 1

    def test_all_ecarts_criticite_is_critique(self, engine, session):
        make_pi(session, statut="IRREVOCABLE", funds_debited=False, funds_credited=False)
        engine.analyser_cycles_pi()
        ecarts = EcartDetecte.objects.filter(session=session)
        assert all(e.criticite == CriticiteChoices.CRITIQUE for e in ecarts)

    def test_multiple_cycles_multiple_ecarts(self, engine, session):
        make_pi(session, "P1", statut="IRREVOCABLE", funds_debited=False, funds_credited=True)
        make_pi(session, "P2", statut="IRREVOCABLE", funds_debited=True, funds_credited=False)
        assert engine.analyser_cycles_pi() == 2


# ═══════════════════════════════════════════════════════════════
# TESTS D'ISOLATION INTER-SESSIONS
# ═══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestSessionIsolation:
    """Vérifie que l'engine n'analyse que les données de sa propre session."""

    def test_ec01_ignores_other_session_cbs(self, cfg):
        s1 = ReconciliationSession.objects.create(
            date_traitement=date(2024, 1, 15), configuration=cfg
        )
        s2 = ReconciliationSession.objects.create(
            date_traitement=date(2024, 1, 16), configuration=cfg
        )
        make_mb(s1, "E1")
        make_cbs(s2, "E1")   # CBS dans une autre session → non visible pour s1

        count = MatchingEngine(s1).detecter_fantomes_mb()

        assert count == 1   # Le CBS de s2 n'est pas pris en compte

    def test_ec02_ignores_other_session_mb(self, cfg):
        s1 = ReconciliationSession.objects.create(
            date_traitement=date(2024, 1, 15), configuration=cfg
        )
        s2 = ReconciliationSession.objects.create(
            date_traitement=date(2024, 1, 16), configuration=cfg
        )
        make_cbs(s1, "E1")
        make_mb(s2, "E1")   # MB dans une autre session

        count = MatchingEngine(s1).detecter_fantomes_cbs()

        assert count == 1   # Le MB de s2 n'est pas pris en compte


# ═══════════════════════════════════════════════════════════════
# TEST D'INTÉGRATION : DONNÉES PROPRES
# ═══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestMatchingEngineIntegration:

    def test_no_ecarts_on_perfectly_matched_session(self, engine, session):
        """Session parfaitement équilibrée → aucun écart détecté."""
        for i in range(5):
            make_mb(session, f"E{i}")
            make_cbs(session, f"E{i}")
            make_pi(session, f"PI{i}", statut="COMPLETED",
                    funds_debited=True, funds_credited=True)

        total = (
            engine.detecter_fantomes_mb()
            + engine.detecter_fantomes_cbs()
            + engine.detecter_doublons()
            + engine.analyser_cycles_pi()
        )

        assert total == 0
        assert EcartDetecte.objects.filter(session=session).count() == 0

    def test_all_methods_return_correct_counts(self, engine, session):
        """Chaque méthode retourne exactement le nombre d'écarts qu'elle crée."""
        # 2 MB fantômes (E1, E2)
        make_mb(session, "E1")
        make_mb(session, "E2")
        # 1 CBS fantôme (E3)
        make_cbs(session, "E3")
        # 1 EC-03 : 2 MB pour 1 CBS (E4)
        make_mb(session, "E4"); make_mb(session, "E4"); make_cbs(session, "E4")
        # 1 EC-04 : 2 CBS pour 1 MB (E5)
        make_mb(session, "E5"); make_cbs(session, "E5"); make_cbs(session, "E5")
        # 1 EC-05 + 1 EC-06 sur même cycle
        make_pi(session, "PI1", statut="IRREVOCABLE",
                funds_debited=False, funds_credited=False)

        assert engine.detecter_fantomes_mb() == 2
        assert engine.detecter_fantomes_cbs() == 1
        assert engine.detecter_doublons() == 2
        assert engine.analyser_cycles_pi() == 2

        assert EcartDetecte.objects.filter(session=session).count() == 7
