import requests
import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

def buildSaveVector():
    pdf_url = "https://raw.githubusercontent.com/pradeepthiduggaraju/loan-risk-evaluator/main/comprehensive_loan_policy_document.pdf"
    response = requests.get(pdf_url)

    with open("PolicyDocument.pdf", "wb") as f:
        f.write(response.content)

    doc = fitz.open("PolicyDocument.pdf")
    text = "".join([page.get_text() for page in doc])
    doc.close()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_text(text)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)

    client = chromadb.PersistentClient(path="storage/")  # Or use chromadb.Client()
    collection = client.get_or_create_collection("loan_policy_rules")
    

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"chunk_{i}"],
            embeddings=[embeddings[i].tolist()]
        )
    print("ChromaDB document count:", collection.count())
    print("PolicyDocument indexed and stored in vector DB at ./storage/")
    all_ids = [f"chunk_{i}" for i in range(collection.count())]

    # Query all documents by ID
    results = collection.get(ids=all_ids)

    # Print each chunk
    for i, doc in enumerate(results["documents"]):
        print(f"\n--- Chunk {i} ---\n{doc}")

if __name__ == "__main__":
    buildSaveVector()
