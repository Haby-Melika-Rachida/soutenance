"""
CoreAPIConnector — collecte les logs d'audit depuis l'API-CORE (CBS).
Persiste les données dans le modèle TransactionCBS.
"""
import logging
from datetime import date

from django.conf import settings

from apps.core.models import TransactionCBS
from .base import BaseConnector

logger = logging.getLogger(__name__)


class CoreAPIConnector(BaseConnector):
    """
    Connecteur pour l'API-CORE (Core Banking System LICELI).

    Endpoint cible : GET {API_CORE_BASE_URL}/audit-logs?date=YYYY-MM-DD
    Résultats persistés dans : TransactionCBS
    """

    def __init__(self) -> None:
        super().__init__()
        self._base_url: str = settings.API_CORE_BASE_URL.rstrip("/")

    def collect(self, session, target_date: date) -> int:
        """
        Collecte l'intégralité des entrées d'audit CBS pour ``target_date``.
        Insère en base par lot (bulk_create) et retourne le nombre de lignes créées.
        """
        logger.info(
            "[CoreAPIConnector] Début collecte transactions CBS — date : %s",
            target_date,
        )
        to_create: list[TransactionCBS] = []

        for page in self._paginate(
            f"{self._base_url}/audit-logs",
            params={"date": target_date.isoformat(), "page_size": 100},
        ):
            for item in page:
                to_create.append(self._map_to_model(session, item))

        if to_create:
            TransactionCBS.objects.bulk_create(to_create)

        logger.info(
            "[CoreAPIConnector] %d transactions CBS insérées (session_id=%d)",
            len(to_create),
            session.pk,
        )
        return len(to_create)

    # ── Mapping API → modèle ─────────────────────────────────────────────

    def _map_to_model(self, session, item: dict) -> TransactionCBS:
        return TransactionCBS(
            session=session,
            msg_id=item["msg_id"],
            end_to_end_id=item["end_to_end_id"],
            montant=item["montant"],
            debtor_account=item["debtor_account"],
            creditor_account=item.get("creditor_account", ""),
            transaction_status=item["transaction_status"],
            is_pi_transfer=item.get("is_pi_transfer", False),
            timestamp=item["timestamp"],
        )
