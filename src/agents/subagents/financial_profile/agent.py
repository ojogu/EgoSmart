from google.adk.agents import LlmAgent
from .prompt import SYSTEM_PROMPT
from google.adk.tools.agent_tool import AgentTool
from .financial_profile_tool import read_user_financial_profile_tool, update_user_financial_profile_tool

financial_profile_agent = LlmAgent(
        name="financial_profile_agent",
        model="gemini-2.5-flash",
        description="""Collects and verifies user income and financial profiles for financial planning.
        This agent systematically gathers essential financial information, validates profile completeness, and maintains accurate income records. It serves as the mandatory first step, focusing exclusively on income profile collection and verification. It does NOT handle budget creation, expense tracking, spending analysis, or financial advice. Users are handed off to the Budgeting Agent after profile verification.
""",
        # output_key="finance_linking",
        instruction=SYSTEM_PROMPT, 
        tools=[update_user_financial_profile_tool, read_user_financial_profile_tool],
)

#convert this agent to a tool for the root agent

financial_profile_agent_tool = AgentTool(financial_profile_agent)
