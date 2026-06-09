"""
Tests unitaires — connecteurs API (MobileBankingConnector, CoreAPIConnector, PIConnector).

Stratégie :
- Toutes les requêtes HTTP sont mockées ; aucun appel réseau réel.
- Les délais tenacity sont court-circuités via le fixture ``instant_retries``.
- Les tests ``collect`` utilisent la vraie base (pytest.mark.django_db) pour
  vérifier que bulk_create persiste correctement dans les modèles Django.
- Les tests ``_map_to_model`` sont purement en mémoire (pas de DB).
"""

import time
from datetime import date
from unittest.mock import Mock, patch, call

import pytest
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout

from apps.connectors.base import BaseConnector
from apps.connectors.core_api import CoreAPIConnector
from apps.connectors.mobile_banking import MobileBankingConnector
from apps.connectors.pi import PIConnector
from apps.core.models import (
    ConfigurationBatch,
    CyclePI,
    DirectionPIChoices,
    ReconciliationSession,
    TransactionCBS,
    TransactionMB,
    TypeFluxChoices,
)

# ═══════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════

TARGET_DATE = date(2024, 1, 15)


# ═══════════════════════════════════════════════════════════════
# FIXTURES GLOBALES
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def instant_retries():
    """
    Court-circuite les délais d'attente tenacity pour l'ensemble des tests.
    Tenacity stocke le callable sleep dans l'instance Retrying attachée à
    chaque fonction décorée (func.retry.sleep). On le remplace par un no-op.
    """
    no_sleep = lambda x: None  # noqa: E731
    originals = {}
    for func_name in ("_do_authenticate", "_get"):
        func = getattr(BaseConnector, func_name)
        originals[func_name] = func.retry.sleep
        func.retry.sleep = no_sleep
    yield
    for func_name, orig in originals.items():
        getattr(BaseConnector, func_name).retry.sleep = orig


@pytest.fixture
def cfg(db):
    return ConfigurationBatch.objects.create(nom="cfg-test")


@pytest.fixture
def session(db, cfg):
    return ReconciliationSession.objects.create(
        date_traitement=TARGET_DATE,
        configuration=cfg,
    )


# ── Helpers HTTP ─────────────────────────────────────────────────────────────

def _ok(body: dict) -> Mock:
    r = Mock()
    r.status_code = 200
    r.json.return_value = body
    r.raise_for_status = Mock()
    return r


def _err(status: int) -> Mock:
    r = Mock()
    r.status_code = status
    r.raise_for_status = Mock(side_effect=HTTPError(response=r))
    return r


def auth_resp(token: str = "tok-test", expires_in: int = 28800) -> Mock:
    return _ok({"access_token": token, "expires_in": expires_in})


def page_resp(items: list, next_url=None) -> Mock:
    return _ok({"results": items, "next": next_url, "count": len(items)})


# ── Payloads API ─────────────────────────────────────────────────────────────

def mb_payload(**kw) -> dict:
    return {
        "message_id": "MSG-001",
        "end_to_end_id": "E2E-001",
        "montant": "10000.00",
        "compte_debiteur": "BF0001",
        "compte_crediteur": "BF0002",
        "statut": "EXECUTED",
        "type_flux": "CBS_SIMPLE",
        "date_operation": "2024-01-15",
        **kw,
    }


def cbs_payload(**kw) -> dict:
    return {
        "msg_id": "CBS-001",
        "end_to_end_id": "E2E-001",
        "montant": "10000.00",
        "debtor_account": "BF0001",
        "creditor_account": "BF0002",
        "transaction_status": "ACSC",
        "is_pi_transfer": False,
        "timestamp": "2024-01-15T08:00:00Z",
        **kw,
    }


def pi_payload(**kw) -> dict:
    return {
        "message_id": "PI-001",
        "end_to_end_id": "E2E-001",
        "direction": "EMISSION",
        "montant": "5000.00",
        "statut": "COMPLETED",
        "date_operation": "2024-01-15",
        "specific_data": {
            "funds_reserved": True,
            "funds_debited": True,
            "funds_credited": False,
        },
        **kw,
    }


def _connector_with_valid_token(cls):
    """Instancie un connecteur avec un token déjà valide (évite l'appel auth)."""
    c = cls()
    c._token = "tok-valid"
    c._token_expires_at = time.monotonic() + 3600
    return c


# ═══════════════════════════════════════════════════════════════
# AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════════

class TestAuthentication:
    """Acquisition, mise en cache et renouvellement du token API-AUTH."""

    @patch("apps.connectors.base.requests.post")
    def test_token_acquired_on_first_call(self, mock_post):
        mock_post.return_value = auth_resp("tok-abc")
        c = MobileBankingConnector()
        c._ensure_token()
        assert c._token == "tok-abc"
        mock_post.assert_called_once()

    @patch("apps.connectors.base.requests.post")
    def test_token_cached_no_double_auth(self, mock_post):
        mock_post.return_value = auth_resp("tok-abc")
        c = MobileBankingConnector()
        c._ensure_token()
        c._ensure_token()          # deuxième appel → pas de requête supplémentaire
        mock_post.assert_called_once()

    @patch("apps.connectors.base.requests.post")
    def test_expired_token_triggers_reauth(self, mock_post):
        mock_post.return_value = auth_resp("tok-new")
        c = MobileBankingConnector()
        c._token = "tok-old"
        c._token_expires_at = time.monotonic() - 1   # expiré
        c._ensure_token()
        assert c._token == "tok-new"
        mock_post.assert_called_once()

    @patch("apps.connectors.base.requests.post")
    def test_auth_retries_on_network_error(self, mock_post):
        mock_post.side_effect = [
            ConnectionError("réseau indisponible"),
            ConnectionError("réseau indisponible"),
            auth_resp("tok-ok"),
        ]
        c = MobileBankingConnector()
        c._ensure_token()
        assert c._token == "tok-ok"
        assert mock_post.call_count == 3

    @patch("apps.connectors.base.requests.post")
    def test_auth_raises_after_3_consecutive_failures(self, mock_post):
        mock_post.side_effect = ConnectionError("réseau indisponible")
        c = MobileBankingConnector()
        with pytest.raises(ConnectionError):
            c._ensure_token()
        assert mock_post.call_count == 3

    @patch("apps.connectors.base.requests.post")
    def test_auth_raises_on_http_503(self, mock_post):
        mock_post.return_value = _err(503)
        c = MobileBankingConnector()
        with pytest.raises(HTTPError):
            c._ensure_token()

    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_401_response_forces_reauth_before_retry(self, mock_post, mock_get):
        """Un 401 mid-session invalide le token et force une re-auth au prochain essai."""
        mock_post.return_value = auth_resp("tok-refreshed")
        mock_get.side_effect = [_err(401), page_resp([])]

        c = MobileBankingConnector()
        c._token = "tok-expired"
        c._token_expires_at = time.monotonic() + 3600

        result = c._get("http://api.test/transactions")

        assert result["results"] == []
        mock_post.assert_called_once()          # re-auth effectuée
        assert mock_get.call_count == 2         # tentative initiale + retry


# ═══════════════════════════════════════════════════════════════
# PAGINATION
# ═══════════════════════════════════════════════════════════════

class TestPagination:
    """Générateur _paginate : navigation entre pages et gestion des cas limites."""

    @patch("apps.connectors.base.requests.get")
    def test_single_page_terminates_loop(self, mock_get):
        mock_get.return_value = page_resp([mb_payload()])
        c = _connector_with_valid_token(MobileBankingConnector)
        pages = list(c._paginate("http://api/transactions"))
        assert len(pages) == 1
        assert len(pages[0]) == 1
        mock_get.assert_called_once()

    @patch("apps.connectors.base.requests.get")
    def test_multi_page_follows_next_url(self, mock_get):
        mock_get.side_effect = [
            page_resp([mb_payload(end_to_end_id="E1")], next_url="http://api/p2"),
            page_resp([mb_payload(end_to_end_id="E2")]),
        ]
        c = _connector_with_valid_token(MobileBankingConnector)
        pages = list(c._paginate("http://api/p1"))
        assert len(pages) == 2
        assert pages[0][0]["end_to_end_id"] == "E1"
        assert pages[1][0]["end_to_end_id"] == "E2"

    @patch("apps.connectors.base.requests.get")
    def test_second_page_called_with_next_url_no_extra_params(self, mock_get):
        mock_get.side_effect = [
            page_resp([mb_payload()], next_url="http://api/p2?cursor=xyz"),
            page_resp([]),
        ]
        c = _connector_with_valid_token(MobileBankingConnector)
        list(c._paginate("http://api/p1", params={"date": "2024-01-15"}))
        second_call_url = mock_get.call_args_list[1].args[0]
        second_call_params = mock_get.call_args_list[1].kwargs.get("params")
        assert second_call_url == "http://api/p2?cursor=xyz"
        assert second_call_params is None   # params ne sont pas répétés sur les pages suivantes

    @patch("apps.connectors.base.requests.get")
    def test_empty_page_yields_empty_list(self, mock_get):
        mock_get.return_value = page_resp([])
        c = _connector_with_valid_token(MobileBankingConnector)
        pages = list(c._paginate("http://api/transactions"))
        assert pages == [[]]

    @patch("apps.connectors.base.requests.get")
    def test_data_key_fallback_when_results_absent(self, mock_get):
        """Supporte la clé 'data' si 'results' est absent de la réponse."""
        mock_get.return_value = _ok({"data": [mb_payload()], "next": None})
        c = _connector_with_valid_token(MobileBankingConnector)
        pages = list(c._paginate("http://api/transactions"))
        assert len(pages[0]) == 1

    @patch("apps.connectors.base.requests.get")
    def test_get_retries_on_connection_error(self, mock_get):
        mock_get.side_effect = [
            ConnectionError("timeout"),
            ConnectionError("timeout"),
            page_resp([]),
        ]
        c = _connector_with_valid_token(MobileBankingConnector)
        c._get("http://api/transactions")
        assert mock_get.call_count == 3

    @patch("apps.connectors.base.requests.get")
    def test_get_raises_after_3_consecutive_failures(self, mock_get):
        mock_get.side_effect = Timeout("timeout réseau")
        c = _connector_with_valid_token(MobileBankingConnector)
        with pytest.raises(Timeout):
            c._get("http://api/transactions")
        assert mock_get.call_count == 3


# ═══════════════════════════════════════════════════════════════
# MOBILE BANKING CONNECTOR
# ═══════════════════════════════════════════════════════════════

class TestMobileBankingConnector:
    """MobileBankingConnector.collect() et _map_to_model()."""

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_inserts_one_transaction_mb(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([mb_payload()])
        count = MobileBankingConnector().collect(session, TARGET_DATE)
        assert count == 1
        assert TransactionMB.objects.filter(session=session).count() == 1

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_empty_response_returns_zero(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([])
        count = MobileBankingConnector().collect(session, TARGET_DATE)
        assert count == 0
        assert TransactionMB.objects.filter(session=session).count() == 0

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_multi_page_inserts_all(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.side_effect = [
            page_resp(
                [mb_payload(end_to_end_id="E1"), mb_payload(end_to_end_id="E2")],
                next_url="http://api/p2",
            ),
            page_resp([mb_payload(end_to_end_id="E3")]),
        ]
        count = MobileBankingConnector().collect(session, TARGET_DATE)
        assert count == 3
        assert TransactionMB.objects.filter(session=session).count() == 3

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_passes_date_as_iso_param(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([])
        MobileBankingConnector().collect(session, TARGET_DATE)
        params = mock_get.call_args.kwargs["params"]
        assert params["date"] == "2024-01-15"

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_links_transaction_to_session(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([mb_payload()])
        MobileBankingConnector().collect(session, TARGET_DATE)
        tx = TransactionMB.objects.get(session=session)
        assert tx.end_to_end_id == "E2E-001"
        assert tx.compte_debiteur == "BF0001"

    # ── Mapping ──────────────────────────────────────────────────────────

    @pytest.mark.parametrize("type_flux,expected", [
        ("CBS_SIMPLE", TypeFluxChoices.CBS_SIMPLE),
        ("PI_EMISSION", TypeFluxChoices.PI_EMISSION),
        ("PI_RECEPTION", TypeFluxChoices.PI_RECEPTION),
    ])
    def test_map_type_flux(self, type_flux, expected):
        c = _connector_with_valid_token(MobileBankingConnector)
        obj = c._map_to_model(Mock(pk=1), mb_payload(type_flux=type_flux))
        assert obj.type_flux == expected

    def test_map_compte_crediteur_optional(self):
        """compte_crediteur absent → chaîne vide (pas d'erreur)."""
        c = _connector_with_valid_token(MobileBankingConnector)
        payload = mb_payload()
        del payload["compte_crediteur"]
        obj = c._map_to_model(Mock(pk=1), payload)
        assert obj.compte_crediteur == ""

    def test_map_all_scalar_fields(self):
        c = _connector_with_valid_token(MobileBankingConnector)
        obj = c._map_to_model(Mock(pk=1), mb_payload())
        assert obj.message_id == "MSG-001"
        assert obj.end_to_end_id == "E2E-001"
        assert obj.statut == "EXECUTED"
        assert obj.date_operation == "2024-01-15"


# ═══════════════════════════════════════════════════════════════
# CORE API CONNECTOR
# ═══════════════════════════════════════════════════════════════

class TestCoreAPIConnector:
    """CoreAPIConnector.collect() et _map_to_model()."""

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_inserts_one_transaction_cbs(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([cbs_payload()])
        count = CoreAPIConnector().collect(session, TARGET_DATE)
        assert count == 1
        assert TransactionCBS.objects.filter(session=session).count() == 1

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_empty_response_returns_zero(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([])
        count = CoreAPIConnector().collect(session, TARGET_DATE)
        assert count == 0

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_multi_page_inserts_all(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.side_effect = [
            page_resp(
                [cbs_payload(msg_id="C1"), cbs_payload(msg_id="C2")],
                next_url="http://api/p2",
            ),
            page_resp([cbs_payload(msg_id="C3")]),
        ]
        count = CoreAPIConnector().collect(session, TARGET_DATE)
        assert count == 3
        assert TransactionCBS.objects.filter(session=session).count() == 3

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_passes_date_as_iso_param(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([])
        CoreAPIConnector().collect(session, TARGET_DATE)
        params = mock_get.call_args.kwargs["params"]
        assert params["date"] == "2024-01-15"

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_links_transaction_to_session(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([cbs_payload()])
        CoreAPIConnector().collect(session, TARGET_DATE)
        tx = TransactionCBS.objects.get(session=session)
        assert tx.msg_id == "CBS-001"
        assert tx.transaction_status == "ACSC"

    # ── Mapping ──────────────────────────────────────────────────────────

    def test_map_all_scalar_fields(self):
        c = _connector_with_valid_token(CoreAPIConnector)
        obj = c._map_to_model(Mock(pk=1), cbs_payload())
        assert obj.msg_id == "CBS-001"
        assert obj.end_to_end_id == "E2E-001"
        assert obj.debtor_account == "BF0001"
        assert obj.transaction_status == "ACSC"

    def test_map_is_pi_transfer_true(self):
        c = _connector_with_valid_token(CoreAPIConnector)
        obj = c._map_to_model(Mock(pk=1), cbs_payload(is_pi_transfer=True))
        assert obj.is_pi_transfer is True

    def test_map_is_pi_transfer_defaults_false_when_absent(self):
        """is_pi_transfer absent de la réponse → False (pas d'erreur)."""
        c = _connector_with_valid_token(CoreAPIConnector)
        payload = cbs_payload()
        del payload["is_pi_transfer"]
        obj = c._map_to_model(Mock(pk=1), payload)
        assert obj.is_pi_transfer is False

    def test_map_creditor_account_optional(self):
        c = _connector_with_valid_token(CoreAPIConnector)
        payload = cbs_payload()
        del payload["creditor_account"]
        obj = c._map_to_model(Mock(pk=1), payload)
        assert obj.creditor_account == ""


# ═══════════════════════════════════════════════════════════════
# PI CONNECTOR
# ═══════════════════════════════════════════════════════════════

class TestPIConnector:
    """PIConnector.collect() et _map_to_model()."""

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_inserts_one_cycle_pi(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([pi_payload()])
        count = PIConnector().collect(session, TARGET_DATE)
        assert count == 1
        assert CyclePI.objects.filter(session=session).count() == 1

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_empty_response_returns_zero(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([])
        count = PIConnector().collect(session, TARGET_DATE)
        assert count == 0

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_multi_page_inserts_all(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.side_effect = [
            page_resp(
                [pi_payload(end_to_end_id="P1"), pi_payload(end_to_end_id="P2")],
                next_url="http://api/p2",
            ),
            page_resp([pi_payload(end_to_end_id="P3")]),
        ]
        count = PIConnector().collect(session, TARGET_DATE)
        assert count == 3
        assert CyclePI.objects.filter(session=session).count() == 3

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_passes_date_as_iso_param(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([])
        PIConnector().collect(session, TARGET_DATE)
        params = mock_get.call_args.kwargs["params"]
        assert params["date"] == "2024-01-15"

    @pytest.mark.django_db
    @patch("apps.connectors.base.requests.get")
    @patch("apps.connectors.base.requests.post")
    def test_collect_links_cycle_to_session(self, mock_post, mock_get, session):
        mock_post.return_value = auth_resp()
        mock_get.return_value = page_resp([pi_payload()])
        PIConnector().collect(session, TARGET_DATE)
        cycle = CyclePI.objects.get(session=session)
        assert cycle.message_id == "PI-001"
        assert cycle.direction == DirectionPIChoices.EMISSION

    # ── Mapping ──────────────────────────────────────────────────────────

    @pytest.mark.parametrize("direction,expected", [
        ("EMISSION", DirectionPIChoices.EMISSION),
        ("RECEPTION", DirectionPIChoices.RECEPTION),
    ])
    def test_map_direction(self, direction, expected):
        c = _connector_with_valid_token(PIConnector)
        obj = c._map_to_model(Mock(pk=1), pi_payload(direction=direction))
        assert obj.direction == expected

    def test_map_specific_data_extracted(self):
        """Les booléens du cycle sont lus depuis specific_data."""
        c = _connector_with_valid_token(PIConnector)
        payload = pi_payload()
        payload["specific_data"] = {
            "funds_reserved": True,
            "funds_debited": True,
            "funds_credited": False,
        }
        obj = c._map_to_model(Mock(pk=1), payload)
        assert obj.funds_reserved is True
        assert obj.funds_debited is True
        assert obj.funds_credited is False

    def test_map_specific_data_missing_defaults_all_false(self):
        """specific_data absent → tous les booléens à False (pas d'erreur)."""
        c = _connector_with_valid_token(PIConnector)
        payload = pi_payload()
        del payload["specific_data"]
        obj = c._map_to_model(Mock(pk=1), payload)
        assert obj.funds_reserved is False
        assert obj.funds_debited is False
        assert obj.funds_credited is False

    def test_map_specific_data_partial_flags(self):
        """Seuls certains booléens présents dans specific_data → les autres à False."""
        c = _connector_with_valid_token(PIConnector)
        payload = pi_payload()
        payload["specific_data"] = {"funds_reserved": True}  # debited et credited absents
        obj = c._map_to_model(Mock(pk=1), payload)
        assert obj.funds_reserved is True
        assert obj.funds_debited is False
        assert obj.funds_credited is False

    def test_map_all_scalar_fields(self):
        c = _connector_with_valid_token(PIConnector)
        obj = c._map_to_model(Mock(pk=1), pi_payload())
        assert obj.message_id == "PI-001"
        assert obj.end_to_end_id == "E2E-001"
        assert obj.statut == "COMPLETED"
        assert obj.date_operation == "2024-01-15"
