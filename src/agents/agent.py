import json
import logging
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.tools import FunctionTool
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from pydantic import BaseModel, Field
from src.utils.config import config
import google.generativeai as genai
from google.adk.models.lite_llm import LiteLlm
genai.configure(api_key=config.GEMINI_KEY)
from google.genai import types


logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/agent.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

class AgentManager:
    def __init__(self):
        self.app_name = "Egosmart"

    async def async_init(self):
        try:
            self.session_service = DatabaseSessionService(db_url=config.DATABASE_URL)
            await self.session_service.initialize_tables()
            logger.info("Session service initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize session service: {e}", exc_info=True)
            raise
        return self
    # "sqlite:///./test.db"
    
    async def get_or_create_session(self, user_id: str, session_id: str):
        """
        Retrieve a session if it exists, otherwise create a new one.
        """
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )
        if session is None:
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
        return session
    async def get_session(self, app_name: str, user_id: str, session_id: str):
        """
        Retrieve a session from the session service.
        """
        return await self.session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )

    async def create_model(self):
        return LiteLlm(
            model=config.MODEL_NAME,
            api_key=config.GEMINI_KEY,
        )

    async def create_agent(
        self,
        name: str,
        description: str,
        instruction: str,
        input_schema: BaseModel = None,
        output_schema: BaseModel = None,
        output_key: str = None
        
    ):
        logger.info(f"Creating agent: name='{name}', description='{description}'")
        model = await self.create_model()
        return LlmAgent(
            model=model,
            name=name,
            description=description,
            instruction=instruction,
            input_schema=input_schema,
            output_schema=output_schema,
            output_key=output_key,
        )

    async def create_runner(self, agent: LlmAgent, app_name):
        logger.info(f"Creating runner for agent: '{agent.name}'")
        return Runner(
            agent=agent,
            app_name=app_name,
            session_service=self.session_service
        )



async def call_agent_and_log(session, agent: LlmAgent, runner: Runner, query_json: str):
    logger.info(f"Calling agent '{agent.name}' with query: {query_json}")
    user_content = types.Content(role='user', parts=[types.Part(text=query_json)])

    final_response_content = "No final response received."
    try:
        async for event in runner.run_async(user_id=session.user_id, session_id=session.id, new_message=user_content):
            logger.info(event)
            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text
                logger.info(f"Agent '{agent.name}' final response: {final_response_content}")
                return final_response_content
        
    except Exception as e:
        logger.error(f"Error during agent '{agent.name}' call: {e}", exc_info=True)
        final_response_content = f"Error: {e}"

    # Use AgentManager to get the session
    # agent_manager = AgentManager()
    # current_session = agent_manager.get_session(
    #     app_name=session.app_name,
    #     user_id=session.user_id,
    #     session_id=session.session_id
    # )
    # stored_output = current_session.state.get(agent.output_key)
    # logger.info(f"stored output: {stored_output}")

    # parsed_output = None
    # if stored_output is not None:
    #     try:
    #         parsed_output = json.loads(stored_output)
    #         logger.info(f"Session state for key '{agent.output_key}': {json.dumps(parsed_output)}")
    #     except (json.JSONDecodeError, TypeError):
    #         parsed_output = stored_output
    #         logger.warning(f"Session state for key '{agent.output_key}' is not valid JSON: {stored_output}")
    # else:
    #     parsed_output = None
    #     logger.warning(f"No session state found for key '{agent.output_key}'")

    # logger.info(f"Returning response and session state for agent '{agent.name}'")
    # response =  {
    #     "agent_name": agent.name,
    #     "query": query_json,
    #     "final_response": final_response_content,
    #     "session_state": parsed_output
    # }
    # logger.info(response)
    # return response
