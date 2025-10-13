from google.adk.agents import LlmAgent
from .prompt import SYSTEM_PROMPT
from google.adk.tools.agent_tool import AgentTool

linking_agent = LlmAgent(
        name="account_linking_agent",
        description=(
        "Handles the entire account authorization and data retrieval flow: "
        "checking link status, initiating OAuth, fetching balances, "
        "transactions, summaries, and unlinking."
    ),
        output_key="finance_linking",
        instruction=SYSTEM_PROMPT
)

linking_tool = AgentTool(linking_agent)