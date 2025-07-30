from fastapi import Response, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import logging 
# from src.schemas.schema import User 
from src.utils.config import config


logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/google.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

class GoogleAuthService:
    SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file"
    ]
    CLIENT_ID = config.CLIENT_ID
    CLIENT_SECRET = config.CLIENT_SECRET


    def __init__(self, client_secret_file, redirect_uri):
        self.client_secret_file = client_secret_file
        self.redirect_uri = redirect_uri
        self.flow = None


    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    def login_with_google(self):
        try:
            logger.info("Initializing OAuth flow for Google authentication.")
            flow = Flow.from_client_secrets_file(
                self.client_secret_file,
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            logger.info(f"Generated Google OAuth authorization URL: {auth_url}")
            # Save state in cookie (http-only for security)
            redirect_response = RedirectResponse(auth_url)
            redirect_response.set_cookie(
                key="oauth_state", 
                value=state, 
                httponly=True, 
                secure=True, 
                samesite="Lax"  # "Lax" works with most OAuth flows. "Strict" may block it.
            )
            # logger.info(f"OAuth state saved in cookie.,value:{state}")
            return auth_url
        except FileNotFoundError as fnf_error:
            logger.error(f"Client secret file not found: {self.client_secret_file} - {fnf_error}")
            return {"error": "Client secret file not found."}
        except Exception as e:
            logger.exception(f"Error generating Google OAuth authorization URL: {e}")
            return {"error": str(e)}

    def handle_callback(self, request: Request):
        try:
         
            logger.info(f"cookies, {request.cookies}")
            # state = request.cookies.get("oauth_state")
            # if not state:
            #     logger.info(f"state, {state}")
            #     state_from_query = request.query_params.get('state')
            #     logger.info(f"state from query_params; {state_from_query}")
            #     logger.warning("State missing in cookies during OAuth callback.")
            #     # return {"error": "State missing in cookies"}
            
             #Rebuild flow with correct state
            flow = Flow.from_client_secrets_file(
                self.client_secret_file,
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri,
                state=request.query_params.get("state")
            )

            # # Set the state in the flow to validate
            # self.flow.state = state

            # FastAPI's request.url is a Starlette URL object; convert to str
            # logger.info(f"request.url, {request.url}")
            authorization_response = str(request.url)

            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials

            logger.info(f"OAuth callback handled successfully")
            cred =  {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "id_token": credentials.id_token
            }
            logger.info(f"cred generated")
            # logger.info(f"credentials, {cred}")
            return cred
        except Exception as e:
            logger.exception("Error handling OAuth callback: %s", e)
            return {"error": str(e)}
        
    
    def verify_id(self, id_code):
        # Verify and decode
        info = id_token.verify_oauth2_token(
            id_code,
            requests.Request(),
            self.CLIENT_ID,
            clock_skew_in_seconds=10
            )
        logger.info(f"info generated") 
        # logger.info(f"info for user, {id_code}: {info}") 
        return info


    @staticmethod
    def refresh_credentials(access_token, refresh_token, client_id, client_secret, scopes):
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds


from pathlib import Path
import logging
CLIENT_SECRET_PATH = Path(__file__).resolve().parent.parent.parent / "client_secret.json"
google_service = GoogleAuthService(client_secret_file=str(CLIENT_SECRET_PATH), redirect_uri="https://egosmart.loca.lt")