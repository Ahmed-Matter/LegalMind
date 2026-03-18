from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests

security = HTTPBearer()

AUTH0_DOMAIN = "dev-dh4evfod0ajyzd7e.us.auth0.com"
API_AUDIENCE = "https://dev-LegalMind/login"
ALGORITHMS = ["RS256"]


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials

    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()

    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token header")

    rsa_key = {}

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    if not rsa_key:
        raise HTTPException(status_code=401, detail="Public key not found")

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.JWTClaimsError as e:
        raise HTTPException(status_code=401, detail=f"Invalid claims: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
#valdate token from query string
def verify_token_from_query(token: str):

    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()

    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    rsa_key = {}

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        audience=API_AUDIENCE,
        issuer=f"https://{AUTH0_DOMAIN}/",
    )
    return payload