"""
Connecteur de base — authentification API-AUTH, pagination et retries tenacity.
Toutes les classes de connecteurs héritent de BaseConnector.
"""
import logging
import time
from abc import ABC, abstractmethod
from datetime import date

import requests
from django.conf import settings
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class ConnectorAuthError(Exception):
    """Échec d'authentification auprès d'API-AUTH après épuisement des tentatives."""


class ConnectorAPIError(Exception):
    """Erreur non-récupérable lors d'un appel à une API externe."""


class BaseConnector(ABC):
    """
    Classe abstraite commune aux trois connecteurs API LICELI.

    Responsabilités :
      - Obtenir et renouveler le token Bearer via API-AUTH (3 retries, backoff expo).
      - Effectuer des GET paginés avec retry automatique.
      - Exposer `collect(session, target_date)` à implémenter dans chaque sous-classe.
    """

    def __init__(self) -> None:
        self._auth_url: str = settings.API_AUTH_BASE_URL.rstrip("/")
        self._service_id: str = settings.API_AUTH_SERVICE_ID
        self._service_key: str = settings.API_AUTH_SERVICE_KEY
        self._timeout: int = settings.API_TIMEOUT_SECONDS
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    # ── Authentification ─────────────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        reraise=True,
    )
    def _do_authenticate(self) -> None:
        """Appelle POST /token sur API-AUTH et stocke le token en mémoire."""
        resp = requests.post(
            f"{self._auth_url}/token",
            json={
                "service_id": self._service_id,
                "service_key": self._service_key,
            },
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        # Renouvellement proactif 5 min avant expiration (par défaut 8 h)
        expires_in = data.get("expires_in", 28800)
        self._token_expires_at = time.monotonic() + expires_in - 300

    def _ensure_token(self) -> None:
        """Acquiert (ou renouvelle) le token si nécessaire."""
        if not self._token or time.monotonic() >= self._token_expires_at:
            logger.info("[%s] Acquisition du token API-AUTH", self.__class__.__name__)
            self._do_authenticate()

    def _auth_headers(self) -> dict:
        """Retourne les en-têtes HTTP incluant le Bearer token."""
        self._ensure_token()
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }

    # ── Requêtes HTTP avec retry tenacity ────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        reraise=True,
    )
    def _get(self, url: str, params: dict | None = None) -> dict:
        """
        GET avec retry exponentiel (3 tentatives).
        Un 401 provoque un renouvellement forcé du token avant le prochain essai.
        """
        resp = requests.get(
            url,
            headers=self._auth_headers(),
            params=params,
            timeout=self._timeout,
        )
        if resp.status_code == 401:
            # Le token a expiré côté serveur — réinitialisation pour forcer re-auth
            self._token = None
            self._token_expires_at = 0.0
            resp.raise_for_status()  # Lève HTTPError → tenacity retente
        resp.raise_for_status()
        return resp.json()

    def _paginate(self, url: str, params: dict | None = None):
        """
        Générateur paginé compatible avec le format DRF standard.

        L'API doit retourner un objet JSON avec :
          - ``results`` (ou ``data``) : liste des éléments de la page courante.
          - ``next`` : URL de la page suivante, ``null`` si dernière page.

        Yields une liste d'items à chaque page.
        """
        current_url: str | None = url
        current_params = params
        page_num = 1

        while current_url:
            logger.debug(
                "[%s] Récupération page %d : %s",
                self.__class__.__name__,
                page_num,
                current_url,
            )
            data = self._get(current_url, current_params)
            results = data.get("results") or data.get("data") or []
            yield results
            # À partir de la 2ème page, les params sont encodés dans `next`
            current_url = data.get("next") or None
            current_params = None
            page_num += 1

    # ── Interface à implémenter dans chaque connecteur ───────────────────

    @abstractmethod
    def collect(self, session, target_date: date) -> int:
        """
        Collecte toutes les données pour ``target_date``, les persiste en base
        via les modèles Django rattachés à ``session``.

        Retourne le nombre d'enregistrements insérés.
        """
        raise NotImplementedError
