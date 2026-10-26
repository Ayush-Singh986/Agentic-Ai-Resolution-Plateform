from functools import lru_cache
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import settings


bearer_scheme = HTTPBearer(auto_error=False)
APPROVER_GROUP = settings.COGNITO_APPROVER_GROUP


def _issuer_url() -> str:
    if not settings.COGNITO_ISSUER_URL or not settings.COGNITO_APP_CLIENT_ID:
        raise HTTPException(
            status_code=503,
            detail="Cognito authentication is not configured.",
        )
    return settings.COGNITO_ISSUER_URL.rstrip("/")


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    return PyJWKClient(f"{_issuer_url()}/.well-known/jwks.json")


def require_cognito_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Sign in with AWS Cognito to use remediation approval.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    issuer = _issuer_url()
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(
            credentials.credentials
        )
        claims = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.COGNITO_APP_CLIENT_ID,
            issuer=issuer,
            options={"require": ["exp", "iat", "sub", "token_use"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=401,
            detail="Cognito session expired. Sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.PyJWKClientConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not reach the Cognito signing-key endpoint.",
        ) from exc
    except jwt.PyJWKClientError as exc:
        raise HTTPException(
            status_code=401,
            detail="Cognito token signing key is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=401,
            detail="Cognito token is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if claims.get("token_use") != "id":
        raise HTTPException(
            status_code=401,
            detail="A Cognito ID token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return claims


def require_approver(
    claims: dict[str, Any] = Depends(require_cognito_user),
) -> dict[str, Any]:
    groups = claims.get("cognito:groups", [])
    if APPROVER_GROUP not in groups:
        raise HTTPException(
            status_code=403,
            detail="Your Cognito user is not a member of the approver group.",
        )
    return claims
