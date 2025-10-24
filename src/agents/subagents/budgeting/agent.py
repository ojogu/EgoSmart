from google.adk.agents import LlmAgent
from .prompt import SYSTEM_PROMPT
from google.adk.tools.agent_tool import AgentTool


budgeting_agent = LlmAgent(
        name="account_linking_agent",
        model="gemini-2.5-flash",
        description=(
            "Monitors budget compliance and spending limits: "
            "setting and updating budget limits per category, tracking real-time "
            "spending against budgets, detecting when thresholds are approached or "
            "exceeded, and sending timely alerts and notifications to users."
),
        # output_key="finance_linking",
        instruction=SYSTEM_PROMPT, 
        tools=[],
   
)

#convert this agent to a tool for the root agent

linking_agent_tool = AgentTool(budgeting_agent)