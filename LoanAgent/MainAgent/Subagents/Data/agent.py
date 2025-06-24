from google.adk import Agent
from google.adk.tools import FunctionTool
from . import prompt
import pandas as pd


def dataretrival(customerid : str) -> dict:
    df = pd.read_csv("C:/Users/SaiNandaSekhar/Desktop/LoanAgent/MainAgent/Subagents/Data/customer_financial_data.csv")
    customer = df[df['CustomerID'] == customerid]
    if customer.empty:
        return {"error":"Customer not found"}
    else:
        return customer.iloc[0].to_dict()
    
# def datagathering() -> dict:
#     """
#     Function to gather user data for loan eligibility evaluation.
#     Returns a dictionary with user data.
#     """
#     return {
#         "MonthlyIncome": 63000,
#         "CreditScore": 710,
#         "ExistingLoans": 1,
#         "TotalEMI": 9000,
#         "AvgMonthlyBalance": 25000,
#         "MissedEMI": 0,
#         "Savings": 1000000,
#         "CreditCardUtilization": 20,
#         "RequestedLoanAmount": 500000,
#         "LoanType": "PersonalLoan",
#         "TenureYears": 5
#     }


MODEL = "gemini-2.0-flash"
DataAgent = Agent(
    name="DataAgent",
    model=MODEL,
    description="This agent gathers user data for loan eligibility evaluation.",
    instruction=prompt.Data,
    output_key="user_data",
    tools=[FunctionTool(dataretrival)]
)
