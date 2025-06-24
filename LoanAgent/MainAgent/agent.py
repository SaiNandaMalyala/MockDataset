from google.adk.agents import LlmAgent
# from google.adk.tools import google_search
from . import prompt
from google.adk.tools.agent_tool import AgentTool
from .Subagents.RiskAgent import RiskAnalystAgent
from .Subagents.SummaryAgent import SummarizedAgent
from .Subagents.Data import DataAgent

MODEL = "gemini-2.0-flash"
LoanProcessingAgent = LlmAgent(
   name = "LoanProcessingAgent",
   model = MODEL,
   description = "This is a orchestration agent that coordinates the loan processing workflow and gives the reviwed summary of the user details of the loan application.",
   instruction = prompt.AGENT_UNDERSTANDING,
   output_key="ID",
   tools=[
       AgentTool(agent = RiskAnalystAgent),
       AgentTool(agent = DataAgent),
       AgentTool(agent = SummarizedAgent)

   ]

)
root_agent = LoanProcessingAgent
