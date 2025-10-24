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


# Model Name,Purpose,API Model ID
# Gemini 2.5 Pro,Most advanced reasoning and coding.,gemini-2.5-pro
# Gemini 2.5 Flash,Best balance of speed and performance.,gemini-2.5-flash
# Gemini 2.5 Flash-Lite,Fastest and most cost-efficient.,gemini-2.5-flash-lite