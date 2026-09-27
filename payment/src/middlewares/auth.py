import requests
from os import environ
from flask import request, g

def checkJwt():
    """
        Middleware fired before any payment request, validating the
        bearer JWT against the auth service and exposing the
        authenticated user and token on flask.g
    """
    if (request.method == "OPTIONS" or request.path.startswith("/openapi")):
        return None

    header = request.headers.get("Authorization", "")
    if (not header.startswith("Bearer ")):
        return {"message": "Missing authorization token"}, 401

    token = header.removeprefix("Bearer ").strip()
    try:
        response = requests.get(
            f"{environ.get('AUTH_API_URL')}user",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
    except Exception:
        return {"message": "Auth service unavailable"}, 503

    if (response.status_code != 200):
        return {"message": "Invalid or expired token"}, 401

    g.user = response.json()
    g.token = token
    return None
