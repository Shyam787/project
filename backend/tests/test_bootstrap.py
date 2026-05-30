import json
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient
from jwt.algorithms import RSAAlgorithm

from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import Settings, get_settings
from app.core.pipeline import GOVERNED_PIPELINE_ORDER
from app.main import create_app


def _security_test_client(claim_overrides: dict | None = None) -> tuple[TestClient, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = json.loads(RSAAlgorithm.to_jwk(private_key.public_key()))
    public_jwk["kid"] = "test-key"
    issuer = "http://keycloak:8080/realms/enterprise-rag"
    audience = "enterprise-rag-api"
    claims = {
        "sub": "user-1",
        "tenant_id": "tenant-a",
        "roles": ["viewer"],
        "iss": issuer,
        "aud": audience,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    claims.update(claim_overrides or {})
    token = jwt.encode(
        claims,
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )
    settings = Settings(
        keycloak_issuer_url=issuer,
        keycloak_audience=audience,
        auth_jwks_json=json.dumps({"keys": [public_jwk]}),
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app), token


def test_health_response_contract():
    client = TestClient(create_app())

    response = client.get("/api/v1/health", headers={"x-request-id": "test-id"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-id"
    body = response.json()
    assert body["success"] is True
    assert body["payload"]["status"] == "ok"
    assert body["metadata"]["request_id"] == "test-id"
    assert body["error"] is None


def test_ready_exposes_governed_pipeline_order():
    client = TestClient(create_app())

    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json()["payload"]["pipeline_order"] == GOVERNED_PIPELINE_ORDER


def test_metrics_endpoint_available():
    client = TestClient(create_app())

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "enterprise_rag_api_requests_total" in response.text


def test_auth_me_returns_tenant_and_rbac_context():
    client, token = _security_test_client()

    response = client.get(
        "/api/v1/auth/me",
        headers={"authorization": f"Bearer {token}", "x-request-id": "auth-test"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["payload"]["user_id"] == "user-1"
    assert body["payload"]["tenant_id"] == "tenant-a"
    assert body["payload"]["tenant_namespace"] == "tenant_tenant-a"
    assert body["payload"]["roles"] == ["viewer"]
    assert body["payload"]["permissions"] == ["document_read"]
    assert body["metadata"]["request_id"] == "auth-test"


def test_auth_me_rejects_missing_bearer_token():
    client, _ = _security_test_client()

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"


def test_auth_me_rejects_missing_tenant_claim():
    client, token = _security_test_client({"tenant_id": None})

    response = client.get(
        "/api/v1/auth/me",
        headers={"authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"
