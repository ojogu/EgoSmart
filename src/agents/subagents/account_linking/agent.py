from google.adk.agents import LlmAgent
from .prompt import SYSTEM_PROMPT
from google.adk.tools.agent_tool import AgentTool
from src.agents.subagents.account_linking import account_linking_tool
linking_agent = LlmAgent(
        name="account_linking_agent",
        model="gemini-2.5-flash",
        description=(
        "Handles the entire account authorization and data retrieval flow: "
        "checking link status, initiating OAuth, fetching balances, "
        "transactions, summaries, and unlinking."
    ),
        # output_key="finance_linking",
        instruction=SYSTEM_PROMPT, 
        tools=[account_linking_tool.check_link_status_tool, account_linking_tool.initiate_account_link_tool, account_linking_tool.verify_link_completion_tool]
)

#convert this agent to a tool for the root agent

linking_tool = AgentTool(linking_agent)