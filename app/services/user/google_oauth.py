from fastapi import Request, HTTPException
from starlette.responses import RedirectResponse
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.integrations.starlette_client import OAuth

from app.core.response.success import Success, prepare_json_data
from app.core.settings import settings
from app.core.token_manager import TokenManager
from app.crud import user_crud

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    scope="openid email profile",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleOAuth:
    def __init__(self):
        self.redirect_uri = settings.REDIRECT_URI
        self.frontend = settings.FRONTEND_URL

    async def login_browser(self, request: Request):
        """
        Handles browser-based login:
        1. Redirects to Google if no code.
        2. Exchanges code and redirects back to frontend with tokens + user info.
        """
        code = request.query_params.get("code")

        if not code:
            return await oauth.google.authorize_redirect(request, self.redirect_uri)

        result = await self.exchange(code)

        # Encode user safely for URL
        encoded_user = self._encode(result['user'])
        url = f"{self.frontend}/auth/success?access_token={result['access']}&refresh_token={result['refresh']}&user={encoded_user}"
        return RedirectResponse(url)

    async def login_api(self, request: Request):
        """
        Handles API login:
        - If code is provided, exchange for tokens
        - Otherwise, return authorization URL
        """
        body = await request.json()
        if "code" in body:
            result = await self.exchange(body["code"])
            return Success.login_success(
                access_token=result['access'],
                refresh_token=result['refresh'],
                user=result['user']
            )

        client = AsyncOAuth2Client(client_id=oauth.google.client_id)
        auth_url, _ = client.create_authorization_url(
            "https://accounts.google.com/o/oauth2/auth",
            redirect_uri=self.redirect_uri,
            scope="openid email profile",
        )
        return {"authorization_url": auth_url}

    async def exchange(self, code: str) -> dict:
        """
        Exchange Google auth code for access & refresh tokens.
        Returns a dict with 'access', 'refresh', 'user'.
        """
        client = AsyncOAuth2Client(
            client_id=oauth.google.client_id,
            client_secret=oauth.google.client_secret,
        )

        token = await client.fetch_token(TOKEN_URL, code=code, redirect_uri=self.redirect_uri)
        if "access_token" not in token:
            raise HTTPException(400, "Invalid Google token")

        info = await client.get(USERINFO_URL)
        data = info.json()
        email, gid = data.get("email"), data.get("sub")

        if not email:
            raise HTTPException(400, "Email missing")

        # Create or update user
        user = await user_crud.get_by_email(email)
        if user:
            if not getattr(user, "google_user_id", None):
                user = await user_crud.update(user.id, {"google_user_id": gid})
        else:
            user = await user_crud.create(
                email=email, google_user_id=gid, is_email_verified=True, user_role="user"
            )

        await user_crud.update_last_login(user.id)
        access, refresh = await TokenManager.generate_token_pair(user)

        # Return plain dict with serialized user
        return {
            "access_token": access,
            "refresh_token": refresh,
            "user": prepare_json_data(user)
        }

    @staticmethod
    def _encode(data: dict) -> str:
        """
        Safely encode any dict (user info) for URLs.
        Handles datetime, UUID, enums, Pydantic models, ORM objects.
        """
        import base64, json
        safe_data = prepare_json_data(data)
        return base64.urlsafe_b64encode(json.dumps(safe_data).encode()).decode()


# Singleton instance
google_oauth = GoogleOAuth()
