from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
from contextlib import asynccontextmanager
from typing import List, Optional
import logging
import time
import json

# LangChain imports
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ANUCDE-Bot")

# Local imports
from schemas import Query, Response
from llm_utils import ChatManager

# Global variables for resources
embeddings = None
vectorstore = None
chat_manager = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global embeddings, vectorstore, chat_manager
    print("Loading resources on startup...", flush=True)
    try:
        print("Loading HuggingFace embeddings model...", flush=True)
        embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
        print("Embeddings model loaded successfully.", flush=True)

        print(f"Loading LangChain FAISS index from {INDEX_DIR}...", flush=True)
        if os.path.exists(INDEX_DIR):
            vectorstore = FAISS.load_local(
                INDEX_DIR, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            print(f"Vector store loaded successfully.", flush=True)
        else:
            print(f"WARNING: Index directory {INDEX_DIR} not found! Run indexer.py first.", flush=True)
        
        print("Initializing LangChain Chat Manager (Streaming)...", flush=True)
        chat_manager = ChatManager() # Default to Qwen 2.5 3B via Ollama
        print("Chat Manager ready.", flush=True)

    except Exception as e:
        print(f"CRITICAL ERROR during startup: {e}", flush=True)
    yield
    print("Shutting down...", flush=True)

app = FastAPI(title="ANUCDE FAQ Bot API (LangChain Streaming)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ANUCDE Assistant API (LangChain Streaming) is running. Visit /docs for documentation."}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

# --- FAQ & CHATBOT LOGIC ---

@app.post("/faq")
async def get_faq(query: Query):
    try:
        text = query.text.lower()
        
        # Service links with explicit https://
        service_links = {
            "result": "You can check your general results on the official portal here: [ANUCDE Results](https://anucde.info/Results.php). For personal result details, please contact our WhatsApp Support.",
            "hall ticket": "You can download your hall ticket directly from here: [ANUCDE Hall Tickets](https://anucde.info/HallTickets.php)",
            "exam schedule": "The examination schedule and notifications are available here: [Exam Notifications](https://anucde.info/Notifications.php)",
            "fee": "Information regarding fee structure and general dues can be found here: [Fee Details](https://anucde.info/FeeStructure.php). For personal fee payment status, please use our WhatsApp Support.",
            "dues": "Information regarding fee structure and general dues can be found here: [Fee Details](https://anucde.info/FeeStructure.php). For personal fee payment status, please use our WhatsApp Support.",
            "assignment": "Assignment question papers and instructions are available here: [Assignments](https://anucde.info/Assignments.php)",
            "notification": "The examination schedule and latest notifications are available here: [Exam Notifications](https://anucde.info/Notifications.php)",
            "admission": "Information regarding the admission process can be found on our official portal here: [Admission Info](https://anucde.info/index.php). For specific admission queries, please use our WhatsApp Support.",
            "course": "You can explore the list of available courses and eligibility criteria here: [Available Courses](https://anucde.info/index.php#courses). For detailed counseling, reach out to our WhatsApp Support.",
            "complaint": "For grievances or specific complaints, please reach out to our official WhatsApp Support: [Contact Support](https://wa.me/91XXXXXXXXXX)",
            "grievance": "For grievances or specific complaints, please reach out to our official WhatsApp Support: [Contact Support](https://wa.me/91XXXXXXXXXX)",
            "human": "You can speak with our support staff directly via WhatsApp: [Contact Support](https://wa.me/91XXXXXXXXXX)",
            "staff": "You can speak with our support staff directly via WhatsApp: [Contact Support](https://wa.me/91XXXXXXXXXX)",
            "support": "Our team is available on WhatsApp for further assistance: [Contact Support](https://wa.me/91XXXXXXXXXX)"
        }

        # Check for direct service keywords first
        found_link = None
        for key, link in service_links.items():
            if key in text:
                found_link = link
                break

        # 1. Search Vector Store for public FAQs
        search_start = time.time()
        faq_context = ""
        SIMILARITY_THRESHOLD = 0.9 # Stricter threshold (L2 distance: lower is better)
        
        if vectorstore:
            results = vectorstore.similarity_search_with_score(query.text, k=1)
            if results:
                doc, dist = results[0]
                if dist <= SIMILARITY_THRESHOLD: 
                    faq_context = f"Question: {doc.page_content}\nProposed Answer: {doc.metadata.get('answer')}"
        
        search_duration = time.time() - search_start
        logger.info(f"PERF: Vector Search Latency: {search_duration:.4f}s")
        
        if not faq_context and found_link:
            faq_context = f"Direct Link Provided: {found_link}"

        # 2. Streaming Generator
        async def event_generator():
            logger.info(f"PERF: Starting Steam for Query: {query.text} | Session: {query.session_id}")
            start_stream_time = time.time()
            token_count = 0
            
            async for token in chat_manager.get_response_stream(
                session_id=query.session_id,
                user_query=query.text,
                context=faq_context
            ):
                if token_count == 0:
                    ttft = time.time() - start_stream_time
                    logger.info(f"PERF: Time to First Token (TTFT): {ttft:.4f}s")
                
                token_count += 1
                yield token
            
            total_stream_duration = time.time() - start_stream_time
            logger.info(f"PERF: Total Stream Duration: {total_stream_duration:.4f}s | Tokens: {token_count}")

        return StreamingResponse(event_generator(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Error in /faq: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
