#root/orchestrator agent
from google.adk.agents import LlmAgent
from .prompt import SYSTEM_PROMPT
from src.utils.log import setup_logger
from src.utils.config import config, setting
from src.agents.subagents.account_linking.agent import linking_agent_tool
logger = setup_logger(__name__, file_path="agent.log")




root_agent = LlmAgent(
    name= setting.PROJECT_NAME,
    model="gemini-2.5-flash",
    description=setting.PROJECT_DESCRIPTION,
    instruction=SYSTEM_PROMPT,
    tools=[linking_agent_tool],

)
