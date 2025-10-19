from typing import Optional
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

    
    async def get_or_create_session(self, whatsapp_phone_number: str, username: str | None = None, role: str | None = None) -> Session:
        """
        Retrieve an active session or create a new one.
        """
        logger.info(f"Attempting to get or create session for WhatsApp number: {whatsapp_phone_number}")

        logger.info(f"Listing sessions for app: {self.app_name}, user_id: {whatsapp_phone_number}")
        response = await (self.session_service.list_sessions(app_name=self.app_name, user_id=whatsapp_phone_number))
        
        all_sessions_list = response.sessions if response and response.sessions else []
        logger.info(f"Found {len(all_sessions_list)} sessions for user {whatsapp_phone_number}")

        valid_session = None
        initial_state = {
            "user:whatsapp_phone_number":whatsapp_phone_number,
            "user:role": role if role else "unknown",
            "user:username": username if username else "",
        }
        
        if all_sessions_list:
            all_sessions_list.sort(key=lambda s: float(s.id), reverse=True)

            for session in all_sessions_list:
                if not self._is_expired(session):
                    valid_session = session
                    logger.info(f"Found valid session with ID: {session.id} for user: {whatsapp_phone_number} with state: {session.state}")
                    break

        if not valid_session:
            logger.info(f"No valid session found for user: {whatsapp_phone_number}. Creating a new session.")
            valid_session =(await self.session_service.create_session(
                app_name=self.app_name,
                user_id=whatsapp_phone_number,
                session_id=str(datetime.now(timezone.utc).timestamp()), 
                state=initial_state
            ))
            logger.info(f"New session created with ID: {valid_session.id} for user: {whatsapp_phone_number}, with state: {valid_session.state}")
            
        return valid_session

    def _is_expired(self, session: Session) -> bool:
        logger.debug(f"Checking expiration for session ID: {session.id}")
        now = datetime.now(timezone.utc)
        last_updated_time = datetime.fromtimestamp(session.last_update_time, tz=timezone.utc)
        created_at = datetime.fromtimestamp(float(session.id), tz=timezone.utc)

        if (now - last_updated_time) > timedelta(days=self.LAST_UPDATED_EXPIRATION_DAYS):
            logger.info(f"Session ID: {session.id} expired due to last updated time. Last updated: {last_updated_time}")
            return True

        if (now - created_at) > timedelta(days=self.SESSION_AGE_EXPIRATION_DAYS):
            logger.info(f"Session ID: {session.id} expired due to session age. Created at: {created_at}")
            return True
        
        logger.debug(f"Session ID: {session.id} is not expired.")
        return False
    


    async def delete_single_session(
        self,
        user_id: str,
        session_id: str
    ) -> None:
        """Deletes a specific session and all its associated events and state."""
        
        logger.info(f"Attempting to delete session: {session_id} for user: {user_id}...")
        
        try:
            # The delete_session() method handles the database transaction
            await self.session_service.delete_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"Successfully deleted session: {session_id}")
        except Exception as e:
            logger.info(f"Error deleting session {session_id}: {e}")
            
    
    
    async def delete_all_sessions(
        self,
        user_id: Optional[str] = None
    ) -> int:
        """
        Fetches all sessions for the configured app_name (and optional user_id) 
        and deletes them sequentially, logging progress.
        
        Args:
            user_id: The ID of the user whose sessions should be deleted. 
                     If None, attempts to fetch and delete all sessions for self.app_name.
            
        Returns:
            The count of sessions successfully deleted.
        """
        
        target = f"user: {user_id}" if user_id else f"app: {self.app_name}"
        logger.info(f"Attempting to fetch and delete all sessions for {target}...")
        
        try:
            # 1. Fetch all matching sessions (service returns a response with .sessions)
            response = await self.session_service.list_sessions(
                app_name=self.app_name,
                user_id=user_id
            )
            sessions_to_delete: list[Session] = response.sessions if response and response.sessions else []
        except Exception as e:
            logger.error(f"Failed to list sessions for deletion: {e}")
            return 0
        
        if not sessions_to_delete:
            logger.info("No sessions found to delete.")
            return 0

        count = 0
        total_found = len(sessions_to_delete)
        logger.info(f"Found {total_found} sessions. Starting sequential deletion.")
        
        # 2. Iterate and delete each one
        for session in sessions_to_delete:
            try:
                # Use the service's delete_session method directly
                await self.session_service.delete_session(
                    app_name=session.app_name,
                    user_id=session.user_id,
                    session_id=session.id
                )
                count += 1
                logger.debug(f"Successfully deleted session: {session.id}")
            except Exception as e:
                # Log a warning, but continue with the rest of the sessions
                logger.warning(f"Failed to delete session {session.id}. Error: {e}")
                
        logger.info(f"Deletion complete for {target}. Total deleted: {count} out of {total_found} found.")
        return count


