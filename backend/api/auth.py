from fastapi import APIRouter,HTTPException,Body
import requests

auth_router=APIRouter()

AUTH0_DOMAIN = "dev-dh4evfod0ajyzd7e.us.auth0.com"
CLIENT_ID = "Ui0TSbmBvEVEEgChreQQXuuhN8JOn9DF"
CLIENT_SECRET = "oYbU29M_u7JZ1V4ZMU9YJd2_gOgmTDGxUUHqmZ03fowBYqrmjK50bKZAw3yAyBhU"
API_AUDIENCE="https://dev-LegalMind/login"

@auth_router.post("/login")
def login(data: dict = Body(...)):

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    url = f"https://{AUTH0_DOMAIN}/oauth/token"

    payload = {
        "grant_type": "password",
        "username": email,
        "password": password,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": API_AUDIENCE,
        "scope": "openid profile email",
        "realm": "Username-Password-Authentication"
    }

    headers = {
        "content-type": "application/json"
    }

    res = requests.post(url, json=payload, headers=headers)

    if res.status_code != 200:
        # return Auth0 error to help debugging
        try:
            error_data = res.json()
        except:
            error_data = {"error": res.text}

        raise HTTPException(
            status_code=401,
            detail=error_data
        )

    token_data = res.json()

    return {
        "access_token": token_data.get("access_token"),
        "id_token": token_data.get("id_token"),
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type")
    }
