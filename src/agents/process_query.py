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
    Cleans a raw string that may contain Markdown code block formatting (e.g. ```json ... ```).
    Returns a clean JSON string.
    """
    if not raw:
        return ""

    cleaned = raw.strip()

    # If it starts and ends with triple backticks, remove them
    if cleaned.startswith("```") and cleaned.endswith("```"):
        # Remove starting and ending backticks
        cleaned = cleaned.strip("`").strip()

        # Remove 'json' or any language identifier after the opening ```
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    return cleaned

class ProcessQueryService:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager


    async def process_query(self, phone_number: str, query: str, username: str | None = None, role: str | None = None):
        """
        Process a user query by managing sessions and delegating to the root agent.
        """
        try:
            session = await self.session_manager.get_or_create_session(
                phone_number=phone_number,
                username=username,
                role=role,
            )
            runner = Runner(agent=root_agent, session_service=self.session_manager.session_service, app_name=setting.PROJECT_NAME)

            content = types.Content(role='user', parts=[types.Part(text=query)])

            events = runner.run_async(
                user_id=phone_number,
                session_id=session.id,
                new_message=content
            )

            final_response = None
            async for event in events:
                if event.content and event.content.parts:
                    if event.is_final_response():
                        final_response = event.content.parts[0].text
            logger.info(f"final response is: {final_response}, type is {type(final_response)}")
            clean_response = clean_json_string(final_response)
            response = json.loads(clean_response)
            # Extracting the user_facing_response
            user_message = response.get("payload", {}).get("user_facing_response")
            return user_message if user_message else "I'm sorry, I couldn't process your request."


         
            
        except Exception as e:
            logger.error(f"Error processing query for {phone_number}: {e}")
            return format_error(
                source=__name__,
                error=f"Error processing query from {phone_number}: {str(e)}",
                raise_exc=True
            )
            
            
session_manager = SessionManager()
process_query_service = ProcessQueryService(session_manager)