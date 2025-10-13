import asyncio
from google.adk.sessions import DatabaseSessionService, Session
from src.utils.log import setup_logger
from src.utils.config import config, setting
from datetime import datetime, timedelta, timezone

logger = setup_logger(__name__, "session.log")
LAST_UPDATED_EXPIRATION_DAYS = 2
SESSION_AGE_EXPIRATION_DAYS = 2
APP_NAME = setting.PROJECT_NAME




class SessionManager:
    def __init__(self):
        self.session_service = DatabaseSessionService(config.DATABASE_SESSION_URL)
        self.app_name = APP_NAME
        self.LAST_UPDATED_EXPIRATION_DAYS = int(LAST_UPDATED_EXPIRATION_DAYS)
        self.SESSION_AGE_EXPIRATION_DAYS = int(SESSION_AGE_EXPIRATION_DAYS)
        
    # "sqlite:///./test.db"
    @staticmethod
    async def run_in_thread(func, *args, **kwargs):
        #helper method to run sync code in an async context
        return await asyncio.to_thread(lambda: func(*args, **kwargs))
    
    async def get_or_create_session(self, phone_number: str, username: str | None = None, role: str | None = None) -> Session:
        """
        Retrieve an active session or create a new one.
        """
        user_id = phone_number

        response = await (self.session_service.list_sessions(app_name=self.app_name, user_id=user_id))

        valid_session = None
        initial_state = {
            "user:phone_number":phone_number,
            "user:role": role if role else "unknown",
            "user:username": username if username else "",
        }
        # Access the list of sessions from the response object
        all_sessions_list = response.sessions if response and response.sessions else []
        
        if all_sessions_list:
            all_sessions_list.sort(key=lambda s: float(s.id), reverse=True)

            for session in all_sessions_list:
                if not self._is_expired(session):
                    valid_session = session
                    break

        if not valid_session:
            valid_session =(await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=str(datetime.now(timezone.utc).timestamp()), 
                state=initial_state
            ))
            
        return valid_session

    def _is_expired(self, session: Session) -> bool:
        now = datetime.now(timezone.utc)
        last_updated_time = datetime.fromtimestamp(session.last_update_time, tz=timezone.utc)
        created_at = datetime.fromtimestamp(float(session.id), tz=timezone.utc)

        if (now - last_updated_time) > timedelta(days=self.LAST_UPDATED_EXPIRATION_DAYS):
            return True

        if (now - created_at) > timedelta(days=self.SESSION_AGE_EXPIRATION_DAYS):
            return True

        return False

# session_manager = SessionManager()