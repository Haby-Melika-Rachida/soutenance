"""
PIConnector — collecte les cycles de Paiement Instantané depuis l'API-PI.
Persiste les données dans le modèle CyclePI.
"""
import logging
from datetime import date

from django.conf import settings

from apps.core.models import CyclePI, DirectionPIChoices
from .base import BaseConnector

logger = logging.getLogger(__name__)

# Correspondance entre les valeurs renvoyées par l'API et les choix du modèle
_DIRECTION_MAP: dict[str, str] = {
    "EMISSION": DirectionPIChoices.EMISSION,
    "RECEPTION": DirectionPIChoices.RECEPTION,
}


class PIConnector(BaseConnector):
    """
    Connecteur pour l'API-PI (Paiement Instantané BCEAO via LICELI).

    Endpoint cible : GET {API_PI_BASE_URL}/cycles?date=YYYY-MM-DD
    Résultats persistés dans : CyclePI

    Le champ ``specific_data`` de l'API porte les booléens du cycle PI
    (funds_reserved, funds_debited, funds_credited).
    """

    def __init__(self) -> None:
        super().__init__()
        self._base_url: str = settings.API_PI_BASE_URL.rstrip("/")

    def collect(self, session, target_date: date) -> int:
        """
        Collecte l'intégralité des cycles PI pour ``target_date``.
        Insère en base par lot (bulk_create) et retourne le nombre de lignes créées.
        """
        logger.info(
            "[PIConnector] Début collecte cycles PI — date : %s",
            target_date,
        )
        to_create: list[CyclePI] = []

        for page in self._paginate(
            f"{self._base_url}/cycles",
            params={"date": target_date.isoformat(), "page_size": 100},
        ):
            for item in page:
                to_create.append(self._map_to_model(session, item))

        if to_create:
            CyclePI.objects.bulk_create(to_create)

        logger.info(
            "[PIConnector] %d cycles PI insérés (session_id=%d)",
            len(to_create),
            session.pk,
        )
        return len(to_create)

    # ── Mapping API → modèle ─────────────────────────────────────────────

    def _map_to_model(self, session, item: dict) -> CyclePI:
        specific = item.get("specific_data") or {}
        return CyclePI(
            session=session,
            message_id=item["message_id"],
            end_to_end_id=item["end_to_end_id"],
            direction=_DIRECTION_MAP.get(item["direction"], item["direction"]),
            montant=item["montant"],
            funds_reserved=specific.get("funds_reserved", False),
            funds_debited=specific.get("funds_debited", False),
            funds_credited=specific.get("funds_credited", False),
            statut=item["statut"],
            date_operation=item["date_operation"],
        )
