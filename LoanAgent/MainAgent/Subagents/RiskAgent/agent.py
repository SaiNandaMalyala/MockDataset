from google.adk import Agent 
from . import prompt
from google.adk.tools import FunctionTool
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import os

# Load ChromaDB and retriever
storage_path = os.path.abspath("storage")
client = chromadb.PersistentClient(path=storage_path)
collection = client.get_or_create_collection("loan_policy_rules")
print(collection.count())

# Use the same embedding model used for saving
model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_policy_chunks(query: str, top_k: int = 3):
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0]  # list of top_k text chunks

def evaluate_eligibility(user_data: dict) -> dict:
    # user_data = {
    #     "Monthly Income": 63000,
    #     "credit score": 780,
    #     "Existing Loans": 1,
    #     "Total EMI": 9000,
    #     "Average Monthly Balance": 25000,
    #     "Missed EMI": 0,
    #     "Savings": 1000000,
    #     "credit card utilization": 20,
    #     "RequestedLoanAmount": 500000,
    #     "Loan Type": "PersonalLoan",
    #     "Tenure Years": 5
    # }
    # Prepare a query string with the user's attributes
    # query = (
    #     f"Loan eligibility criteria for "
    #     f"age: {user_data['age']}, "
    #     f"Monthly Income: {user_data['MonthlyIncome']}, "
    #     f"credit score: {user_data['CreditScore']},"
    #     f"Existing Loans: {user_data['ExistingLoans']},"
    #     f"Total EMI: {user_data['TotalEMI']},"
    #     f"Average Monthly Balance{user_data['AvgMonthlyBalance']},"
    #     f"Missed EMI: {user_data['MissedEMI']},"
    #     f"Savings: {user_data['Savings']},"
    #     f"credit card utilization: {user_data['CreditCardUtilization']},"
    #     f"RequestedLoanAmount: {user_data['RequestedLoanAmount']},"
    #     f"Loan Type: {user_data['LoanType']},"
    #     f"Tenure Years: {user_data['TenureYears']},"
    # )
    query = ", ".join([f"{k}: {v}" for k, v in user_data.items()])
    # Retrieve policy text from vector store
    policy_chunks = retrieve_policy_chunks(query ,top_k=5)
    policy_text = "\n\n".join(policy_chunks) 
    print(policy_text)
    return {
        "policy_text": policy_text
        
    }



MODEL = "gemini-2.0-flash"

RiskAnalystAgent = Agent(
    name = "RiskAnalystAgent",
    model = MODEL,
    description = "This agent will analyze the Policies based on the data provided by DataRetrivalAgent. then Checks the Eligibility, Rate of Interest and Risk Categorization.",
    instruction= prompt.Risk,
    tools=[FunctionTool(
            func=evaluate_eligibility,
            #input_key="user_data",       
   # Optional: custom output key
        )],
    output_key = "riskanalysis", 


)