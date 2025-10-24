from google.adk.runners import Runner
from google.genai import types
from src.utils.config import config, setting
from src.agents.session import  SessionManager
from src.utils.exception import format_error
from .orchestrator import root_agent
import json

from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="agent.log")


def clean_json_string(raw: str) -> str:
    """
    Cleans a raw string by robustly isolating the main JSON object content,
    stripping surrounding text, Markdown fences (```json), and whitespace.
    
    This method works even if descriptive text surrounds the JSON block.
    
    Args:
        raw: The raw text output potentially containing JSON.
        
    Returns:
        A cleaned string containing only the valid JSON content, or an empty string.
    """
    if not raw:
        return ""
        
    # Step 1: Strip common artifacts regardless of their position (e.g., ```json, ```)
    # This turns '```json\n{\n...\n}\n```' into '{\n...\n}'
    cleaned = raw.replace('```json', '').replace('```', '')
    
    # Step 2: Locate the boundaries of the JSON object ({...})
    # This is the most critical step to isolate the actual data.
    start_index = cleaned.find('{')
    end_index = cleaned.rfind('}')
    
    # Check for validity of indices
    if start_index == -1 or end_index == -1 or start_index >= end_index:
        logger.warning("Could not find valid '{...}' delimiters in the cleaned string.")
        return ""
    
    # Step 3: Extract the content between the first '{' and the last '}' (inclusive)
    json_content = cleaned[start_index : end_index + 1]
    
    # Step 4: Return the final string, stripped of remaining surrounding whitespace
    return json_content.strip()

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
            clean_response = clean_json_string(final_response)
            response = json.loads(clean_response)
            # Extracting the user_facing_response
            user_message = response["payload"]["user_facing_response"]
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
