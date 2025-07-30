import json
from src.agents.agent import AgentManager, call_agent_and_log
from src.schemas.agent_schema import UserMessage, IntentResponse
from .prompt import parse_agent_prompt
import logging 
import regex as re 
from src.agents.subagents.account_linking.agent import account_linking_agent

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("src/logs/agent.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
logger.propagate = False

async def parse_message_generate_intent(msg: str, user_id: str, session_id: str):
    logger.info(f"Starting intent parsing for user_id={user_id}, session_id={session_id}")
    agent_manager = AgentManager()
    await agent_manager.async_init()
    session = await agent_manager.get_or_create_session(user_id, session_id)
    logger.debug(f"Session created: {session.id}")
    agent = await agent_manager.create_agent(
        name="intent_parsing_agent",
        description="Parses user request, parses the message, generates intent",
        input_schema=UserMessage,
        # output_schema=IntentResponse,
        output_key="user_intent",
        instruction=parse_agent_prompt()
    )
    logger.debug(f"Agent created: {agent.name}, {agent.description}")
    runner = await agent_manager.create_runner(agent, agent_manager.app_name)
    logger.debug(f"Runner created: {runner}")
    # session = await agent_manager.get_session(
    #     app_name=agent_manager.app_name,
    #     user_id=user_id,
    #     session_id=session_id
    # )
    logger.info(f"Calling agent for user_id={user_id}, session_id={session_id} with message: {msg}")
    try:
        response = await call_agent_and_log(
            session=session,
            agent=agent,
            runner=runner,
            query_json=msg
        )
        logger.info(f"Agent response for user_id={user_id}, session_id={session_id}: {response}")
    except Exception as e:
        logger.error(f"Error during intent parsing for user_id={user_id}, session_id={session_id}: {e}", exc_info=True)
        raise
    logger.info(f"response- {response}")
    # return response

    # Regex to find a JSON object enclosed within ```json ... ```
    # re.DOTALL makes '.' match newlines as well
    # The (.*?) is a non-greedy match for anything between the tags
    json_pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)

    match = json_pattern.search(response)

    json_string = None
    if match:
        json_string = match.group(1) # Extract the content of the first capturing group
        logger.info(f"--- Extracted JSON String (Regex) ---")
        logger.debug(repr(json_string))
    else:
        logger.error("Error: Could not find JSON wrapped in ```json ... ``` using regex.")
        # Fallback to the original response if regex doesn't match, though it's likely to fail
        json_string = response
        
    try:
        final_response = json.loads(json_string)
        logger.info(f"final response - {final_response}")
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e}")
        logger.error(f"Problematic string starts with: '{json_string[:50]}'")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise
    user_message = final_response['payload']['user_facing_response']
    logger.info(user_message)
    return user_message


