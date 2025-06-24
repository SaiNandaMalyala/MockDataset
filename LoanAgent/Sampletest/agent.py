from google.adk.agents import LlmAgent 
from google.adk.tools import FunctionTool
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import os 

# Load ChromaDB and retriever
storage_path = os.path.abspath("storage")
client = chromadb.PersistentClient(path=storage_path)
collection = client.get_or_create_collection("loan_policy_rules")
print("Document count in ChromaDB:", collection.count())
model = SentenceTransformer("all-MiniLM-L6-v2")
def retrieve_policy_chunks(query: str, top_k: int = 3):
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0]  # list of top_k text chunks

def evaluate_eligibility() -> dict:
    user_data = {
        "Monthly Income": 63000,
        "credit score": 780,
        "Existing Loans": 1,
        "Total EMI": 9000,
        "Average Monthly Balance": 25000,
        "Missed EMI": 0,
        "Savings": 1000000,
        "credit card utilization": 20,
        "RequestedLoanAmount": 500000,
        "Loan Type": "PersonalLoan",
        "Tenure Years": 5
    }
    # query = (
    #     f"Loan eligibility criteria for "
    #     f"Monthly Income: {user_data['Monthly Income']}, "
    #     f"Credit Score: {user_data['credit score']}, "
    #     f"Existing Loans: {user_data['Existing Loans']}, "
    #     f"Total EMI: {user_data['Total EMI']}, "
    #     f"Average Monthly Balance: {user_data['Average Monthly Balance']}, "
    #     f"Missed EMI: {user_data['Missed EMI']}, "
    #     f"Savings: {user_data['Savings']}, "
    #     f"Credit Card Utilization: {user_data['credit card utilization']}, "
    #     f"Requested Loan Amount: {user_data['RequestedLoanAmount']}, "
    #     f"Loan Type: {user_data['Loan Type']}, "
    #     f"Tenure Years: {user_data['Tenure Years']}"
    # )
    query_str = ", ".join([f"{k}: {v}" for k, v in user_data.items()])
    # Prepare a query string with the user's attributes
    Maximum_Loan_Amount =  user_data["Monthly Income"] * 20
    # Retrieve policy text from vector store
    query = "loan eligibility rules based on income, credit score, EMI, savings, and tenure"

    policy_chunks = retrieve_policy_chunks(query, top_k=5)
    policy_text = "\n\n".join(policy_chunks)
    if not policy_chunks:
        print("⚠️ No chunks found")
    return {
    "policy_text": policy_text,
    "MaximumLoanAmount": Maximum_Loan_Amount
}

prompt= """
You are an Eligibility Assessment Agent in a loan processing system.

### Objective:
Assess a customer's loan eligibility based **only** on the official bank policy rules retrieved from the vector store.

### Task:
1. Call the `evaluate_eligibility` function — it returns:
   - `policy_text`: the official loan rules from the policy document
   - `MaximumLoanAmount`: the maximum loan amount calculated for the user

2. Carefully read the `policy_text` and extract the rules that determine eligibility.

3. Use only the explicitly mentioned rules from `policy_text` to assess if the user qualifies.

4. Do **not** make assumptions or invent rules.

5. Use this format to return the result:
'''json
{
  "EligibilityStatus": "Eligible" | "Not Eligible",
  "Reasons": [
    "Reason 1 based on specific policy rule",
    "Reason 2 based on specific policy rule",
    ...
  ],
  "ApprovedLoanTerms": {
    "MaximumLoanAmount": " if eligible or null",
    "InterestRate": "Value((strictly based on PolicyDocument Interest Rate policy criteria, donot ssume anything)) or null",
   
  }
}
"""






MODEL = "gemini-2.0-flash"

RiskAnalystAgent = LlmAgent(
    name = "RiskAnalystAgent",
    model = MODEL,
    description = "This agent will analyze the risk based on the data provided by using policy document. It will assess the user's financial situation and provide insights on potential risks associated with the loan application.",
    instruction= prompt,
    tools=[FunctionTool(evaluate_eligibility)],
    output_key = "riskanalysis", 


)

root_agent = RiskAnalystAgent