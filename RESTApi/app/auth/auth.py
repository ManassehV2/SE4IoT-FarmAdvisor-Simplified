import os
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
import requests

# Custom Authentication Error
class AuthError(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

# Auth0 Configuration
AUTH0_DOMAIN =  os.getenv('AUTH0_DOMAIN')
API_AUDIENCE = os.getenv('AUTH0_AUDIENCE')
ALGORITHMS = ["RS256"]

# HTTP Bearer Dependency
http_bearer = HTTPBearer()

def verify_jwt(token: str) -> dict:
    """
    Verify the JWT using Auth0's public keys.
    """
    try:
        # Fetch JWKS (JSON Web Key Set) from Auth0
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()
        unverified_header = jwt.get_unverified_header(token)

        # Find the matching RSA key
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break

        if not rsa_key:
            raise AuthError(status_code=401, detail="Unable to find the appropriate key.")

        # Decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload

    except JWTError:
        raise AuthError(status_code=401, detail="Invalid token.")
    except requests.exceptions.RequestException:
        raise AuthError(status_code=500, detail="Unable to verify token.")

def get_current_user(token: str = Security(http_bearer)):
    """
    Extract and verify the JWT token from the request.
    """
    try:
        return verify_jwt(token.credentials)
    except AuthError as e:
        raise e  # Return a 401 Unauthorized if the token is invalid
    
