# ANUCDE Langchain Chatbot

This project hosts the RAG (Retrieval-Augmented Generation) based chatbot application for ANUCDE, answering student questions regarding their faqs, examinations, grading, and more.

## 📂 Project Structure

The codebase is divided into clear Client and Server responsibilities:

### Server-Side
- `/backend`: The core Python/FastAPI backend logic. It integrates with Langchain, Ollama, and FAISS vector databases. The endpoints process streams, rate limiting, and serve interactions to the frontend.
- `/nginx`: Contains Nginx server proxy configurations to handle rate-limiting limits globally and route frontend traffic cleanly in Docker setups.
- `docker-compose.yml` / `Dockerfile`: Environment configurations for building the entire backend system and database into cohesive containers.

### Client-Side
- `/frontend`: Contains the UI. It hosts simple static files like `test-integration.html` and `chatbot-widget.js`. There are no thick frameworks (React/Vue) currently in use; it is pure HTML/CSS/Javascript designed to be easily embedded directly into the main university's existing site.

---

## 🛠️ Server-Side Guide (Backend)

The server is built in Python with FastAPI, leveraging local Ollama.

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) running locally or accessible remotely.
- Node model downloaded in Ollama: e.g. `ollama run qwen2.5:3b`

### 1. Installation
Navigate into the backend folder and create a virtual environment, then install dependencies:
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt
```

### 2. Running the Server
Before running requests, make sure the index representations of your `faqs.json` exist. If absent, generate them first!
```bash
# Generate the FAISS semantic search local cache
python indexer.py

# Run the FastAPI server natively
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*(IMPORTANT: You can just run `docker-compose up --build` from the root repository directory to bundle everything at once instead of the above steps to automate the process).*

### 3. Testing 
The repository includes a complete automated unit & performance test suite located in `backend/tests/`.

We implemented a robust testing strategy tailored for LLM/Chatbot applications to ensure quality and reliability:
- **API Tests (`test_api.py`)**: Verifies that the FastAPI endpoints (`/ping`, `/faq`) are responsive and properly handle CORS policies so the frontend can securely communicate with the backend.
- **Session & Logic Tests (`test_chat_manager.py`)**: Ensures that LangChain's conversational memory correctly captures user context and properly resets/clears sessions when required, preventing conversation data bleeding across different users.
- **RAG Fidelity Tests (`test_rag_quality.py`)**: Tests whether the chatbot accurately prioritizes explicit keywords (e.g., returning the direct Hall Ticket URL) and validates "Faithfulness"—ensuring the bot admits when it doesn't know an answer rather than hallucinating false information from outside the university's context.
- **Performance Tests (`test_performance.py`)**: Simulates user load and measures Latency to guarantee the time-to-first-token (TTFT) remains within acceptable limits.

To run the suite:
```bash
cd backend
pytest tests/
# Or for coverage percentage check:
pytest --cov=. tests/
```

---

## 🌐 Client-Side Guide (Frontend)

The frontend is a lightweight, Vanilla JavaScript drop-in widget embedded via an HTML file.

### 1. Installation
**None required.** There are no `node_modules`, `webpack`, or external UI compilers necessary. It uses standard DOM manipulation making it independent and highly compatible with legacy platforms.

### 2. Running the App
Because it makes API calls (`fetch()` requests) to `localhost:8000`, browsers may block the Javascript if you just double-click the HTML file natively due to CORS. 
You can serve the frontend in development using any basic web-server. 
- Using Python: `python -m http.server 3000` (from inside the `frontend` directory)
- Or simply use the "Live Server" extension in VS Code on `test-integration.html`.

### 3. Testing
Currently, the frontend uses **Manual Testing**. 
As the UI is just an integrable overlay component running simple Javascript DOM updates, testing should be done by opening `test-integration.html`, interacting with the bot popup, and ensuring the backend returns streamed responses correctly. (If the UI grows in complexity in the future, standard automated tools like Playwright or Cypress can be integrated).
