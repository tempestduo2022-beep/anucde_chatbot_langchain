import json
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

def build_index():
    # Load FAQ data from multiple sources
    faq_files = ["faqs.json", "program_faqs.json"]
    all_faqs = []
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    for filename in faq_files:
        path = os.path.join(BASE_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_faqs.extend(data)
                print(f"Loaded {len(data)} entries from {filename}")

    if not all_faqs:
        print("Error: No FAQ data found!")
        return

    # Convert FAQ data to LangChain Document objects
    # We store the question as page_content and the answer in metadata
    documents = [
        Document(
            page_content=faq["question"],
            metadata={"answer": faq["answer"]}
        ) for faq in all_faqs
    ]

    # Initialize HuggingFace embeddings
    print("Loading HuggingFace embeddings model...")
    embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

    # Build FAISS index from documents
    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vector store to a folder
    INDEX_NAME = "faiss_index"
    save_path = os.path.join(BASE_DIR, INDEX_NAME)
    vectorstore.save_local(save_path)

    print(f"Index built and saved successfully to '{save_path}' folder.")

if __name__ == "__main__":
    build_index()
