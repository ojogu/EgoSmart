#root/orchestrator agent
from google.adk.agents import LlmAgent
from .prompt import SYSTEM_PROMPT
from src.utils.log import setup_logger
from src.utils.config import config, setting
logger = setup_logger(__name__, file_path="agent.log")

root_agent = LlmAgent(
    name= setting.PROJECT_NAME,
    model="gemini-2.5-flash",
    description=setting.PROJECT_DESCRIPTION,
    instruction=SYSTEM_PROMPT,
    # tools=[fetch_user_details.fetch_user_details, delivery_history.fetch_user_deliveries],
    # sub_agents=[delivery_agent],
    # before_model_callback=callback.on_model_start,
    # after_model_callback=callback.on_model_end
)