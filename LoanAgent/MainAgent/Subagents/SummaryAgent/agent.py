from google.adk import Agent
from . import prompt

MODEL = "gemini-2.0-flash"
SummarizedAgent = Agent(
    name="SummarizedAgent",
    model=MODEL,
    description="This agent will collect output of DataRetrival Agent and Risk Analyst Agent to summarize the loan details.",
    instruction=prompt.SUMMARIZATION,
    output_key="summary",
)