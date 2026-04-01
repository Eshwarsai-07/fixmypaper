import json
import urllib.request
from jose import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings

class CognitoAuthenticator:
    def __init__(self):
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID
        self.region = settings.AWS_REGION
        self.issuer = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
        self.jwks_url = f"{self.issuer}/.well-known/jwks.json"
        self._jwks = None

    def get_jwks(self):
        if not self._jwks:
            with urllib.request.urlopen(self.jwks_url) as response:
                self._jwks = json.loads(response.read().decode('utf-8'))
        return self._jwks

    def verify_token(self, auth: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        token = auth.credentials
        try:
            header = jwt.get_unverified_header(token)
            jwks = self.get_jwks()
            
            key = next((k for k in jwks['keys'] if k['kid'] == header['kid']), None)
            if not key:
                raise HTTPException(status_code=401, detail="Invalid token kid")

            # Verify and decode
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=self.issuer
            )
            return payload # Returns the 'sub' (user_id) among other claims
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

cognito_auth = CognitoAuthenticator()
