from flask import request
from flask_openapi3.blueprint import APIBlueprint
from flask_openapi3 import Tag
from schemas import *
from services import AuthService, UserService

# Tag for OpenAPI documentation
auth_tag = Tag(name="Auth", description="Authentication endpoints")

# Blueprint for auth routes
auth_blueprint = APIBlueprint('Auth', __name__, url_prefix='')

def bearerToken() -> str | None:
    """
        Extracts the token from the Authorization header
    """
    header = request.headers.get("Authorization", "")
    if (not header.startswith("Bearer ")):
        return None

    return header.removeprefix("Bearer ").strip()

@auth_blueprint.post("/login", summary="Authenticates an user", tags=[auth_tag], responses={200: LoginResponse, 401: ErrorSchema})
def login(body: LoginRequest):
    """
        Authenticates the user on the external store API and caches
        the token for 1 hour
    """
    try:
        token = AuthService().login(body.username, body.password)
    except Exception:
        return ErrorSchema(message="Invalid username or password").model_dump(), 401

    return LoginResponse(token=token).model_dump(), 200

@auth_blueprint.get("/user", summary="Gets the authenticated user info", tags=[auth_tag], responses={200: User, 401: ErrorSchema, 404: ErrorSchema})
def currentUser():
    """
        Validates the bearer token on the cache and returns the info
        of the user it belongs to
    """
    token = bearerToken()
    if (token == None):
        return ErrorSchema(message="Missing authorization token").model_dump(), 401

    entry = AuthService().getValidToken(token)
    if (entry == None):
        return ErrorSchema(message="Invalid or expired token").model_dump(), 401

    user = UserService().getUser(entry.user_id)
    if (user == None):
        return ErrorSchema(message="User not found").model_dump(), 404

    return user.model_dump(), 200

@auth_blueprint.post("/logout", summary="Invalidates the session token", tags=[auth_tag], responses={200: SuccessSchema, 401: ErrorSchema})
def logout():
    """
        Invalidates the bearer token
    """
    token = bearerToken()
    if (token == None):
        return ErrorSchema(message="Missing authorization token").model_dump(), 401

    if (AuthService().revokeToken(token)):
        return SuccessSchema(message="Logged out").model_dump(), 200

    return ErrorSchema(message="Invalid or expired token").model_dump(), 401
