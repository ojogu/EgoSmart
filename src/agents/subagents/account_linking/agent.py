from src.agents.agent import AgentManager, call_agent_and_log
import logging
from .prompt import account_linking_prompt

from src.utils.log import setup_logger  # noqa: E402
logger = setup_logger(__name__, file_path="agent.log")

async def account_linking_agent(msg:str, user_id:str, session_id:str):
    agent_manager = AgentManager()
    await agent_manager.async_init() 
    session = await agent_manager.get_or_create_session(user_id, session_id)
    agent = await agent_manager.create_agent(
        name="account_linking_agent",
        description=(
        "Handles the entire account authorization and data retrieval flow: "
        "checking link status, initiating OAuth, fetching balances, "
        "transactions, summaries, and unlinking."
    ),
        output_key="finance_linking",
        instruction=account_linking_prompt()
    )
    
    runner = await agent_manager.create_runner(agent, agent_manager.app_name)
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