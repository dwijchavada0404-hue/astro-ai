from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core import auth_tokens
from app.core.auth_tokens import AuthenticationError, decode_bearer_token
from app.core.settings import Settings


ISSUER = "https://identity.example.com"
AUDIENCE = "astroai-api"


def _settings(**overrides) -> Settings:
    values = {
        "environment": "test",
        "auth_enabled": True,
        "auth_jwks_url": f"{ISSUER}/.well-known/jwks.json",
        "auth_jwt_algorithm": "RS256",
        "auth_jwt_issuer": ISSUER,
        "auth_jwt_audience": AUDIENCE,
    }
    values.update(overrides)
    return Settings(**values)


def _token(private_key, **overrides) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": "oidc_user_123",
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=10),
    }
    claims.update(overrides)
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": "key-1"})


def test_jwks_token_is_verified_without_symmetric_secret(monkeypatch):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    client = SimpleNamespace(
        get_signing_key_from_jwt=lambda token: SimpleNamespace(key=private_key.public_key())
    )
    monkeypatch.setattr(auth_tokens, "_jwks_client", lambda url: client)

    payload = decode_bearer_token(_token(private_key), _settings())

    assert payload["sub"] == "oidc_user_123"


def test_jwks_token_still_enforces_audience(monkeypatch):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    client = SimpleNamespace(
        get_signing_key_from_jwt=lambda token: SimpleNamespace(key=private_key.public_key())
    )
    monkeypatch.setattr(auth_tokens, "_jwks_client", lambda url: client)

    with pytest.raises(AuthenticationError, match="Invalid authentication token"):
        decode_bearer_token(_token(private_key, aud="another-api"), _settings())


def test_jwks_lookup_failure_is_reported_as_authentication_error(monkeypatch):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def signing_key_failure(token):
        raise jwt.PyJWKClientError("Unable to fetch signing keys")

    client = SimpleNamespace(get_signing_key_from_jwt=signing_key_failure)
    monkeypatch.setattr(auth_tokens, "_jwks_client", lambda url: client)

    with pytest.raises(AuthenticationError, match="Invalid authentication token"):
        decode_bearer_token(_token(private_key), _settings())


def test_deployed_jwks_url_must_use_https():
    with pytest.raises(ValueError, match="must use HTTPS"):
        _settings(environment="staging", auth_jwks_url="http://identity.example.com/jwks.json")


def test_jwks_rejects_symmetric_algorithm():
    with pytest.raises(ValueError, match="must be asymmetric"):
        _settings(auth_jwt_algorithm="HS256")


def test_asymmetric_algorithm_requires_jwks_url():
    with pytest.raises(ValueError, match="JWKS_URL is required"):
        _settings(auth_jwks_url="")
