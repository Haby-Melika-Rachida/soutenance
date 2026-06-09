"""
MobileBankingConnector — collecte les transactions depuis l'API-MOBILE.
Persiste les données dans le modèle TransactionMB.
"""
import logging
from datetime import date

from django.conf import settings

from apps.core.models import TransactionMB, TypeFluxChoices
from .base import BaseConnector

logger = logging.getLogger(__name__)

# Correspondance entre les valeurs renvoyées par l'API et les choix du modèle
_FLUX_MAP: dict[str, str] = {
    "CBS_SIMPLE": TypeFluxChoices.CBS_SIMPLE,
    "PI_EMISSION": TypeFluxChoices.PI_EMISSION,
    "PI_RECEPTION": TypeFluxChoices.PI_RECEPTION,
}


class MobileBankingConnector(BaseConnector):
    """
    Connecteur pour l'API-MOBILE (Mobile Banking LICELI).

    Endpoint cible : GET {API_MOBILE_BASE_URL}/transactions?date=YYYY-MM-DD
    Résultats persistés dans : TransactionMB
    """

    def __init__(self) -> None:
        super().__init__()
        self._base_url: str = settings.API_MOBILE_BASE_URL.rstrip("/")

    def collect(self, session, target_date: date) -> int:
        """
        Collecte l'intégralité des transactions MB pour ``target_date``.
        Insère en base par lot (bulk_create) et retourne le nombre de lignes créées.
        """
        logger.info(
            "[MobileBankingConnector] Début collecte transactions MB — date : %s",
            target_date,
        )
        to_create: list[TransactionMB] = []

        for page in self._paginate(
            f"{self._base_url}/transactions",
            params={"date": target_date.isoformat(), "page_size": 100},
        ):
            for item in page:
                to_create.append(self._map_to_model(session, item))

        if to_create:
            TransactionMB.objects.bulk_create(to_create)

        logger.info(
            "[MobileBankingConnector] %d transactions MB insérées (session_id=%d)",
            len(to_create),
            session.pk,
        )
        return len(to_create)

    # ── Mapping API → modèle ─────────────────────────────────────────────

    def _map_to_model(self, session, item: dict) -> TransactionMB:
        return TransactionMB(
            session=session,
            message_id=item["message_id"],
            end_to_end_id=item["end_to_end_id"],
            montant=item["montant"],
            compte_debiteur=item["compte_debiteur"],
            compte_crediteur=item.get("compte_crediteur", ""),
            statut=item["statut"],
            type_flux=_FLUX_MAP.get(item["type_flux"], item["type_flux"]),
            date_operation=item["date_operation"],
        )
