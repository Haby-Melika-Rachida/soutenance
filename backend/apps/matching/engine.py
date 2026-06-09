"""
MatchingEngine — détecte les 6 types d'écarts entre MB, CBS et PI.

Chaque méthode publique persiste les EcartDetecte dans la base et retourne
le nombre d'écarts créés.

Clé de rapprochement : end_to_end_id.
Tolérance de date    : configurée dans ConfigurationBatch.date_tolerance_days ;
                       utilisée pour le filtrage CBS par fenêtre temporelle.
"""

import logging
from datetime import timedelta

from django.db.models import Count

from apps.core.models import (
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

logger = logging.getLogger(__name__)


class MatchingEngine:
    """
    Moteur de rapprochement MB / CBS / PI pour une session donnée.

    Usage::

        engine = MatchingEngine(session)
        total = (
            engine.detecter_fantomes_mb()
            + engine.detecter_fantomes_cbs()
            + engine.detecter_doublons()
            + engine.analyser_cycles_pi()
        )
    """

    def __init__(self, session: ReconciliationSession) -> None:
        self.session = session
        self._tolerance = timedelta(
            days=session.configuration.date_tolerance_days
        )

    # ════════════════════════════════════════════════════════════════════
    # MÉTHODES PUBLIQUES
    # ════════════════════════════════════════════════════════════════════

    def detecter_fantomes_mb(self) -> int:
        """
        EC-01 : Transaction MB lettrée dans le MB mais absente du CBS.

        Pour chaque TransactionMB de la session, vérifie qu'il existe au moins
        une TransactionCBS avec le même end_to_end_id dans la fenêtre temporelle
        ± date_tolerance_days autour de la date de traitement.
        """
        cbs_ids = self._cbs_ids_in_window()
        ecarts: list[EcartDetecte] = []

        for tx in TransactionMB.objects.filter(session=self.session):
            if tx.end_to_end_id not in cbs_ids:
                ecarts.append(self._make_ecart(
                    type_ecart=TypeEcartChoices.EC_01,
                    criticite=CriticiteChoices.CRITIQUE,
                    type_flux=tx.type_flux,
                    reference=tx.end_to_end_id,
                    montant=tx.montant,
                    compte=tx.compte_debiteur,
                    description=(
                        f"Transaction MB '{tx.end_to_end_id}' présente dans le MB "
                        f"(date : {tx.date_operation}) mais absente du CBS."
                    ),
                ))

        if ecarts:
            EcartDetecte.objects.bulk_create(ecarts)

        logger.info(
            "[MatchingEngine] EC-01 : %d fantôme(s) MB (session %d)",
            len(ecarts), self.session.pk,
        )
        return len(ecarts)

    def detecter_fantomes_cbs(self) -> int:
        """
        EC-02 : Écriture CBS sans ordre MB correspondant.

        Pour chaque TransactionCBS de la session, vérifie qu'il existe au moins
        une TransactionMB avec le même end_to_end_id.
        """
        mb_ids = self._mb_ids()
        ecarts: list[EcartDetecte] = []

        for tx in TransactionCBS.objects.filter(session=self.session):
            if tx.end_to_end_id not in mb_ids:
                ecarts.append(self._make_ecart(
                    type_ecart=TypeEcartChoices.EC_02,
                    criticite=CriticiteChoices.CRITIQUE,
                    type_flux=(
                        TypeFluxChoices.PI_EMISSION
                        if tx.is_pi_transfer
                        else TypeFluxChoices.CBS_SIMPLE
                    ),
                    reference=tx.end_to_end_id,
                    montant=tx.montant,
                    compte=tx.debtor_account,
                    description=(
                        f"Écriture CBS '{tx.end_to_end_id}' présente dans le CBS "
                        f"mais sans ordre MB correspondant (horodatage : {tx.timestamp})."
                    ),
                ))

        if ecarts:
            EcartDetecte.objects.bulk_create(ecarts)

        logger.info(
            "[MatchingEngine] EC-02 : %d fantôme(s) CBS (session %d)",
            len(ecarts), self.session.pk,
        )
        return len(ecarts)

    def detecter_doublons(self) -> int:
        """
        EC-03 : ≥ 2 ordres MB pour une même écriture CBS (doublon MB).
        EC-04 : ≥ 2 écritures CBS pour un même ordre MB (doublon CBS).

        Un écart est créé par end_to_end_id dupliqué, pas par transaction.
        Seuls les end_to_end_ids présents des deux côtés sont considérés.
        """
        ecarts_03 = self._detecter_doublons_mb()
        ecarts_04 = self._detecter_doublons_cbs()
        all_ecarts = ecarts_03 + ecarts_04

        if all_ecarts:
            EcartDetecte.objects.bulk_create(all_ecarts)

        logger.info(
            "[MatchingEngine] Doublons : %d EC-03, %d EC-04 (session %d)",
            len(ecarts_03), len(ecarts_04), self.session.pk,
        )
        return len(all_ecarts)

    def analyser_cycles_pi(self) -> int:
        """
        EC-05 : Cycle PI IRREVOCABLE avec funds_debited = False.
        EC-06 : Cycle PI IRREVOCABLE avec funds_credited = False.

        Un même cycle peut déclencher les deux écarts simultanément.
        """
        ecarts: list[EcartDetecte] = []

        cycles = CyclePI.objects.filter(
            session=self.session,
            statut__iexact="IRREVOCABLE",
        )

        for cycle in cycles:
            flux = (
                TypeFluxChoices.PI_EMISSION
                if cycle.direction == DirectionPIChoices.EMISSION
                else TypeFluxChoices.PI_RECEPTION
            )

            if not cycle.funds_debited:
                ecarts.append(self._make_ecart(
                    type_ecart=TypeEcartChoices.EC_05,
                    criticite=CriticiteChoices.CRITIQUE,
                    type_flux=flux,
                    reference=cycle.end_to_end_id,
                    montant=cycle.montant,
                    compte="",
                    description=(
                        f"Cycle PI '{cycle.end_to_end_id}' irrévocable "
                        f"mais non débité (direction : {cycle.direction})."
                    ),
                ))

            if not cycle.funds_credited:
                ecarts.append(self._make_ecart(
                    type_ecart=TypeEcartChoices.EC_06,
                    criticite=CriticiteChoices.CRITIQUE,
                    type_flux=flux,
                    reference=cycle.end_to_end_id,
                    montant=cycle.montant,
                    compte="",
                    description=(
                        f"Cycle PI '{cycle.end_to_end_id}' irrévocable "
                        f"mais non crédité (direction : {cycle.direction})."
                    ),
                ))

        if ecarts:
            EcartDetecte.objects.bulk_create(ecarts)

        logger.info(
            "[MatchingEngine] EC-05/06 : %d anomalie(s) PI (session %d)",
            len(ecarts), self.session.pk,
        )
        return len(ecarts)

    # ════════════════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ════════════════════════════════════════════════════════════════════

    def _mb_ids(self) -> set[str]:
        return set(
            TransactionMB.objects.filter(session=self.session)
            .values_list("end_to_end_id", flat=True)
        )

    def _cbs_ids_in_window(self) -> set[str]:
        """
        Retourne les end_to_end_ids CBS dans la fenêtre
        [date_traitement - tolerance, date_traitement + tolerance].
        Avec tolerance=0 (défaut), inclut uniquement le jour exact.
        """
        date_min = self.session.date_traitement - self._tolerance
        date_max = self.session.date_traitement + self._tolerance
        return set(
            TransactionCBS.objects.filter(
                session=self.session,
                timestamp__date__gte=date_min,
                timestamp__date__lte=date_max,
            ).values_list("end_to_end_id", flat=True)
        )

    def _make_ecart(self, **kwargs) -> EcartDetecte:
        return EcartDetecte(session=self.session, **kwargs)

    def _detecter_doublons_mb(self) -> list[EcartDetecte]:
        """EC-03 : end_to_end_ids présents côté CBS et qui apparaissent ≥ 2 fois côté MB."""
        cbs_ids = self._cbs_ids_in_window()

        rows = (
            TransactionMB.objects.filter(
                session=self.session,
                end_to_end_id__in=cbs_ids,
            )
            .values("end_to_end_id")
            .annotate(cnt=Count("id"))
            .filter(cnt__gte=2)
        )

        ecarts = []
        for row in rows:
            e2e = row["end_to_end_id"]
            ref_tx = (
                TransactionMB.objects.filter(session=self.session, end_to_end_id=e2e)
                .first()
            )
            ecarts.append(self._make_ecart(
                type_ecart=TypeEcartChoices.EC_03,
                criticite=CriticiteChoices.CRITIQUE,
                type_flux=ref_tx.type_flux,
                reference=e2e,
                montant=ref_tx.montant,
                compte=ref_tx.compte_debiteur,
                description=(
                    f"{row['cnt']} ordres MB trouvés pour l'écriture CBS '{e2e}'."
                ),
            ))

        return ecarts

    def _detecter_doublons_cbs(self) -> list[EcartDetecte]:
        """EC-04 : end_to_end_ids présents côté MB et qui apparaissent ≥ 2 fois côté CBS."""
        mb_ids = self._mb_ids()

        rows = (
            TransactionCBS.objects.filter(
                session=self.session,
                end_to_end_id__in=mb_ids,
            )
            .values("end_to_end_id")
            .annotate(cnt=Count("id"))
            .filter(cnt__gte=2)
        )

        ecarts = []
        for row in rows:
            e2e = row["end_to_end_id"]
            ref_tx = (
                TransactionCBS.objects.filter(session=self.session, end_to_end_id=e2e)
                .first()
            )
            ecarts.append(self._make_ecart(
                type_ecart=TypeEcartChoices.EC_04,
                criticite=CriticiteChoices.CRITIQUE,
                type_flux=(
                    TypeFluxChoices.PI_EMISSION
                    if ref_tx.is_pi_transfer
                    else TypeFluxChoices.CBS_SIMPLE
                ),
                reference=e2e,
                montant=ref_tx.montant,
                compte=ref_tx.debtor_account,
                description=(
                    f"{row['cnt']} écritures CBS trouvées pour l'ordre MB '{e2e}'."
                ),
            ))

        return ecarts
