from google.adk.runners import Runner
from google.genai import types
from src.utils.config import config, setting
from src.agents.session import  SessionManager
from src.utils.exception import format_error
from .orchestrator import root_agent
from .util import safe_json_loads
from src.utils.log import setup_logger  # noqa: E402

logger = setup_logger(__name__, file_path="agent.log")




class ProcessQueryService:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager


    async def process_query(self, whatsapp_phone_number: str, query: str, username: str | None = None, role: str | None = None, country: str | None = None):
        """
        Process a user query by managing sessions and delegating to the root agent.
        """
        logger.info(f"Processing query for whatsapp_phone_number: {whatsapp_phone_number}, query: {query}")
        try:
            session = await self.session_manager.get_or_create_session(
                whatsapp_phone_number=whatsapp_phone_number,
                username=username,
                role=role,
                country=country,
            )
            logger.info(f"Session created/retrieved for {whatsapp_phone_number} with ID: {session.id}")
            runner = Runner(agent=root_agent, session_service=self.session_manager.session_service, app_name=setting.PROJECT_NAME)

            content = types.Content(role='user', parts=[types.Part(text=query)])
            logger.info(f"Running agent for user: {whatsapp_phone_number}, session: {session.id}")
            events = runner.run_async(
                user_id=whatsapp_phone_number,
                session_id=session.id,
                new_message=content
            )

            final_response = None
            async for event in events:
                logger.info(event)
                if event.content and event.content.parts:
                    if event.is_final_response():
                        final_response = event.content.parts[0].text
            logger.info(f"Agent run completed for {whatsapp_phone_number}. Final response is: {final_response}, type is {type(final_response)}")
            clean_response = safe_json_loads(final_response)
            logger.info(f"clean response: {clean_response}")
            logger.info(f"type clean response: {type(clean_response)}")
            # Extracting the user_facing_response
            user_message = clean_response["payload"]["user_facing_response"]
            logger.info(f"User facing response for {whatsapp_phone_number}: {user_message}")
            return user_message if user_message else "I'm sorry, I couldn't process your request."


         
            
        except Exception as e:
            logger.error(f"Error processing query for {whatsapp_phone_number}: {e}", exc_info=True)
            return format_error(
                source=__name__,
                error=f"Error processing query from {whatsapp_phone_number}: {str(e)}",
                raise_exc=True
            )
            
            
session_manager = SessionManager()
process_query_service = ProcessQueryService(session_manager)
