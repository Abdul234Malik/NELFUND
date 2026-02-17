# Backend Documentation - Student Loan NELFUND Chatbot

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Key Components Explained](#key-components-explained)
5. [How It Works](#how-it-works)
6. [Setup and Installation](#setup-and-installation)
7. [API Endpoints](#api-endpoints)
8. [Data Flow](#data-flow)

---

## Overview

This backend is a **FastAPI-based REST API** that powers an AI chatbot for answering questions about the Nigerian Student Loan (NELFUND). It uses:

- **RAG (Retrieval-Augmented Generation)**: Combines document retrieval with AI generation
- **LangGraph**: Creates a workflow/agent system to process queries intelligently
- **ChromaDB**: Vector database for storing and searching document embeddings
- **OpenAI**: For generating embeddings and AI responses

The system reads NELFUND documents, converts them into searchable vectors, and uses them to provide accurate, cited answers to user questions.

---

## Architecture

```
User Query → FastAPI → LangGraph Agent → RAG System → OpenAI LLM → Response
                                    ↓
                              ChromaDB (Vector Search)
```

### High-Level Flow:
1. User sends a question via the frontend
2. FastAPI receives the request
3. LangGraph agent processes it through multiple steps:
   - **Classifies intent** (greeting vs. policy question)
   - **Retrieves relevant documents** from ChromaDB
   - **Generates answer** using OpenAI with retrieved context
4. Response is sent back to the frontend with sources

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   └── config.py        # Configuration (API keys, environment variables)
│   ├── api/
│   │   └── chat.py          # API router (alternative endpoint structure)
│   ├── agents/
│   │   ├── agent.py         # Placeholder agent (not actively used)
│   │   ├── graph.py         # ⭐ MAIN: LangGraph agent workflow
│   │   ├── prompts.py       # System prompts for the AI
│   │   └── qa_chain.py      # Alternative QA chain (not actively used)
│   └── rag/
│       ├── ingest.py         # Document ingestion into ChromaDB
│       └── retriever.py     # Document retrieval from ChromaDB
├── chroma_db/               # Vector database storage (created after ingestion)
├── requirements.txt         # Python dependencies
└── download_nelfund_docs.py # Script to download documents (optional)
```

---

## Key Components Explained

### 1. `app/main.py` - FastAPI Application

**Purpose**: The main entry point that creates the web server and handles HTTP requests.

**Key Features**:
- **CORS Middleware**: Allows the frontend (running on different ports) to communicate with the backend
- **Request/Response Models**: Defines the structure of data sent and received
- **Chat Endpoint**: `/api/chat` - Main endpoint that processes user questions

**Code Breakdown**:
```python
# Creates the FastAPI application
app = FastAPI()

# Allows frontend to make requests (CORS = Cross-Origin Resource Sharing)
app.add_middleware(CORSMiddleware, ...)

# Defines what data the API expects
class ChatRequest(BaseModel):
    query: Optional[str] = None
    message: Optional[str] = None  # Frontend sends "message"
    session_id: Optional[str] = None

# Main chat endpoint
@app.post("/api/chat")
def chat(req: ChatRequest):
    # Gets the query from request
    query = req.query or req.message
    
    # Invokes the LangGraph agent (from graph.py)
    result = agent.invoke({"query": query})
    
    # Returns formatted response
    return {
        "answer": result.get("answer", "No answer generated"),
        "sources": result.get("sources", []),
        "citations": result.get("sources", [])
    }
```

**Why it matters**: This is the bridge between the frontend and the AI system. It handles HTTP requests, validates data, and formats responses.

---

### 2. `app/core/config.py` - Configuration

**Purpose**: Manages environment variables and API keys securely.

**What it does**:
- Loads the `.env` file (where your OpenAI API key is stored)
- Extracts the `OPENAI_API_KEY`
- Raises an error if the key is missing

**Code Breakdown**:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Reads .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment")
```

**Why it matters**: Keeps sensitive information (API keys) out of your code. You should never commit your `.env` file to version control.

---

### 3. `app/agents/graph.py` - LangGraph Agent ⭐ **MOST IMPORTANT**

**Purpose**: This is the "brain" of the system. It orchestrates the entire query processing workflow.

**What is LangGraph?**
LangGraph is a library that lets you build AI agents as **state machines** (workflows). Each step is a "node" that processes data and passes it to the next step.

**The Workflow**:
```
User Query
    ↓
[Classify Intent] → Is it a greeting or policy question?
    ↓
[Retrieve Documents] → Search ChromaDB for relevant info (only if policy question)
    ↓
[Generate Answer] → Use OpenAI to create response with context
    ↓
Return Answer + Sources
```

**Code Breakdown**:

#### State Definition
```python
class AgentState(TypedDict):
    query: str              # The user's question
    intent: Optional[str]   # "greeting" or "policy"
    context: Optional[str]  # Retrieved document chunks
    answer: Optional[str]   # Final AI-generated answer
    sources: List[str]      # List of source file names
```
This defines what data flows through the workflow.

#### Node 1: Classify Intent
```python
def classify_intent(state: AgentState):
    query = state["query"].lower()
    
    greetings = ["hello", "hi", "hey", "good morning", "good evening"]
    
    if any(greet in query for greet in greetings):
        return {"intent": "greeting"}
    
    return {"intent": "policy"}
```
**What it does**: Checks if the user is just saying hello or asking a real question. This helps skip document retrieval for simple greetings.

#### Node 2: Retrieve Documents
```python
def retrieve_docs(state: AgentState):
    query = state["query"]
    docs = retrieve(query)  # Calls retriever.py
    
    # Convert documents to text context
    context = "\n\n".join(
        [f"Source: {doc.metadata.get('source')}\n{doc.page_content}" 
         for doc in docs]
    )
    
    # Extract unique source file names
    sources = list(set(doc.metadata.get("source") for doc in docs))
    
    return {
        "context": context,
        "sources": sources
    }
```
**What it does**: 
- Takes the user's question
- Searches ChromaDB for similar document chunks
- Combines them into a single text context
- Tracks which files the chunks came from

#### Node 3: Generate Answer
```python
def generate_answer(state: AgentState):
    if state["intent"] == "greeting":
        return {
            "answer": "Hello 👋 I can help you understand...",
            "sources": []
        }
    
    context = state.get("context", "")
    query = state["query"]
    
    # Build prompt with context and question
    prompt = f"""
    You are an assistant answering questions about NELFUND.
    Rules:
    - Answer ONLY from the context provided
    - Be clear and helpful
    
    Context:
    {context}
    
    Question:
    {query}
    """
    
    # Call OpenAI
    response = llm.invoke(prompt)
    return {"answer": response.content}
```
**What it does**:
- If it's a greeting, returns a friendly message
- Otherwise, builds a prompt with the retrieved context
- Sends it to OpenAI GPT-4o-mini
- Returns the generated answer

#### Building the Graph
```python
graph = StateGraph(AgentState)

# Add nodes (steps)
graph.add_node("classify", classify_intent)
graph.add_node("retrieve", retrieve_docs)
graph.add_node("answer", generate_answer)

# Set entry point
graph.set_entry_point("classify")

# Define flow
graph.add_conditional_edges(
    "classify",
    lambda state: state["intent"],
    {
        "greeting": "answer",  # Skip retrieval for greetings
        "policy": "retrieve"   # Do retrieval for questions
    }
)

graph.add_edge("retrieve", "answer")
graph.add_edge("answer", END)

# Compile the graph into an executable agent
agent = graph.compile()
```

**Why it matters**: This is where the intelligence happens. It decides what steps to take based on the query and orchestrates the entire process.

---

### 4. `app/rag/ingest.py` - Document Ingestion

**Purpose**: Processes PDF and text files, converts them into vectors, and stores them in ChromaDB.

**What is Ingestion?**
Ingestion is the process of:
1. Reading documents (PDFs, text files)
2. Splitting them into smaller chunks
3. Converting chunks into vectors (embeddings)
4. Storing vectors in a database for fast searching

**Code Breakdown**:

#### Loading Documents
```python
def ingest():
    documents = []
    
    # Process PDF files
    for file in os.listdir(DATA_DIR):
        if file.lower().endswith(".pdf"):
            loader = PyPDFLoader(path)
            pages = loader.load()  # Extracts text from PDF
            documents.extend(pages)
        
        # Process text files
        elif file.lower().endswith(".txt"):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc = Document(page_content=content, metadata={"source": file})
            documents.append(doc)
```
**What it does**: Reads all PDF and text files from the `data/nelfund_docs/` folder.

#### Splitting into Chunks
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,      # Each chunk is ~900 characters
    chunk_overlap=200    # Overlap 200 chars between chunks
)

chunks = splitter.split_documents(documents)
```
**Why chunk?**
- Documents are too large to send to AI all at once
- Chunks allow searching for specific relevant sections
- Overlap ensures context isn't lost at boundaries

#### Creating Vector Database
```python
embeddings = OpenAIEmbeddings()  # Converts text to vectors

vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings,
    collection_name="langchain"
)

vectorstore.add_documents(chunks)  # Stores chunks as vectors
```
**What it does**:
- Uses OpenAI to convert each chunk into a vector (array of numbers)
- Stores vectors in ChromaDB
- Vectors represent the "meaning" of text - similar meanings = similar vectors

**Why it matters**: This is how the system "remembers" the documents. Without ingestion, there's nothing to search.

---

### 5. `app/rag/retriever.py` - Document Retrieval

**Purpose**: Searches ChromaDB to find document chunks relevant to a user's question.

**How Vector Search Works**:
1. User asks: "What is the eligibility criteria?"
2. Question is converted to a vector
3. ChromaDB finds chunks with similar vectors (semantic similarity)
4. Returns the most relevant chunks

**Code Breakdown**:

#### Initialization
```python
embeddings = OpenAIEmbeddings()
_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings
        )
    return _vectorstore
```
**What it does**: Lazy-loads the ChromaDB connection (only connects when needed).

#### Retrieval Function
```python
def retrieve(query: str, k: int = 4):
    vs = get_vectorstore()
    results = vs.similarity_search(query, k)  # k = number of chunks to return
    return results
```
**What it does**:
- Converts the query to a vector
- Searches for the k most similar chunks
- Returns them as Document objects

**Error Handling**:
The code includes fallback logic if ChromaDB has compatibility issues, trying direct access methods.

**Why it matters**: This is the "search engine" that finds relevant information from thousands of document chunks in milliseconds.

---

### 6. `app/agents/prompts.py` - System Prompts

**Purpose**: Defines the AI's behavior and instructions.

**Code**:
```python
SYSTEM_PROMPT = """
You are an AI assistant that helps Nigerian students understand the NELFUND
student loan scheme using ONLY official documents.

Rules:
- If documents are provided, you MUST use them.
- Answers must be clear, simple, and factual.
- Do NOT guess.
- Always cite sources at the end.
- If the answer is not in the documents, say so clearly.
"""
```

**Why it matters**: This tells the AI how to behave - to be factual, cite sources, and not make things up.

---

## How It Works (Step-by-Step Example)

**User asks**: "What are the eligibility requirements for NELFUND?"

### Step 1: Request Arrives
```
Frontend → POST /api/chat
Body: {"message": "What are the eligibility requirements for NELFUND?"}
```

### Step 2: FastAPI Receives Request
```python
# main.py
query = req.message  # "What are the eligibility requirements for NELFUND?"
result = agent.invoke({"query": query})
```

### Step 3: LangGraph Agent Processes

#### 3a. Classify Intent
```python
# classify_intent() runs
query = "what are the eligibility requirements for nelfund?"
# No greeting words found → intent = "policy"
```

#### 3b. Retrieve Documents
```python
# retrieve_docs() runs
docs = retrieve("What are the eligibility requirements for NELFUND?")
# ChromaDB searches and returns 4 relevant chunks:
# - Chunk from "NELFUND_Eligibility_Detailed.txt"
# - Chunk from "NELFUND_Comprehensive_Info.txt"
# - etc.

context = """
Source: NELFUND_Eligibility_Detailed.txt
To be eligible for NELFUND, students must:
1. Be Nigerian citizens
2. Be enrolled in accredited institutions
...

Source: NELFUND_Comprehensive_Info.txt
Eligibility criteria include...
"""
```

#### 3c. Generate Answer
```python
# generate_answer() runs
prompt = """
You are an assistant answering questions about NELFUND.
Answer ONLY from the context provided.

Context:
[The retrieved context above]

Question:
What are the eligibility requirements for NELFUND?

Answer:
"""

# OpenAI generates response
answer = "Based on the NELFUND documents, eligibility requirements include:
1. Nigerian citizenship
2. Enrollment in accredited institutions
..."
```

### Step 4: Response Sent
```json
{
  "answer": "Based on the NELFUND documents...",
  "sources": [
    "NELFUND_Eligibility_Detailed.txt",
    "NELFUND_Comprehensive_Info.txt"
  ],
  "citations": [...]
}
```

### Step 5: Frontend Displays
The frontend shows the answer with clickable source citations.

---

## Setup and Installation

### Python version (important)
**Use Python 3.12 or 3.13.** Python 3.14 is not yet supported by ChromaDB/LangChain (Pydantic v1 compatibility). If you see `ConfigError: unable to infer type for attribute "chroma_server_nofile"` or similar, install Python 3.12 or 3.13 from [python.org](https://www.python.org/downloads/) and use it for this project.

### Prerequisites
- Python 3.12 or 3.13 (see above)
- OpenAI API key
- Documents in `data/nelfund_docs/` folder

### Installation Steps

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set Up Environment Variables**
Create a `.env` file in the `backend/` directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. **Ingest Documents**
```bash
python -m app.rag.ingest
```
This will:
- Read all PDFs and text files from `data/nelfund_docs/`
- Convert them to vectors
- Store them in `chroma_db/`

4. **Run the Server**
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

---

## API Endpoints

### `GET /`
**Purpose**: Health check

**Response**:
```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

### `POST /api/chat`
**Purpose**: Main chat endpoint

**Request Body**:
```json
{
  "message": "What is NELFUND?",
  "session_id": "optional-session-id"
}
```

**Response**:
```json
{
  "answer": "NELFUND is the Nigerian Student Loan Fund...",
  "sources": ["NELFUND_Comprehensive_Info.txt"],
  "citations": ["NELFUND_Comprehensive_Info.txt"]
}
```

### `POST /api/sessions`
**Purpose**: Create a new session ID

**Response**:
```json
{
  "session_id": "uuid-here"
}
```

### `DELETE /api/sessions/{session_id}`
**Purpose**: Delete a session (placeholder)

---

## Data Flow

```
┌─────────────┐
│   Frontend  │
│  (React)    │
└──────┬──────┘
       │ HTTP POST /api/chat
       │ {"message": "question"}
       ↓
┌──────────────────┐
│   FastAPI        │
│   (main.py)      │
└──────┬───────────┘
       │ agent.invoke()
       ↓
┌──────────────────┐
│  LangGraph Agent │
│  (graph.py)      │
└──────┬───────────┘
       │
       ├─→ classify_intent()
       │   └─→ Returns: {"intent": "policy"}
       │
       ├─→ retrieve_docs()
       │   └─→ retrieve() from retriever.py
       │       └─→ ChromaDB similarity_search()
       │           └─→ Returns: [Document chunks]
       │
       └─→ generate_answer()
           └─→ OpenAI LLM.invoke()
               └─→ Returns: {"answer": "...", "sources": [...]}
       │
       ↓
┌──────────────────┐
│   Response       │
│   JSON           │
└──────────────────┘
```

---

## Key Concepts Explained

### What is RAG?
**RAG (Retrieval-Augmented Generation)** combines:
- **Retrieval**: Finding relevant information from documents
- **Augmentation**: Adding that information to the AI's prompt
- **Generation**: AI creates an answer using the retrieved context

**Why RAG?**
- AI models don't have all information memorized
- Documents can be updated without retraining the AI
- Answers are grounded in actual documents (citations possible)

### What are Embeddings?
**Embeddings** are numerical representations of text. Similar meanings = similar numbers.

Example:
- "What is eligibility?" → [0.1, 0.5, -0.3, ...]
- "Who can apply?" → [0.12, 0.48, -0.28, ...] (very similar!)
- "What's the weather?" → [0.9, -0.2, 0.7, ...] (very different!)

### What is ChromaDB?
**ChromaDB** is a vector database. It:
- Stores embeddings (vectors)
- Allows fast similarity search
- Persists data to disk

---

## Troubleshooting

### "No documents retrieved"
- **Cause**: ChromaDB is empty or not initialized
- **Fix**: Run `python -m app.rag.ingest` to populate the database

### "OPENAI_API_KEY not found"
- **Cause**: Missing `.env` file or incorrect key name
- **Fix**: Create `.env` file with `OPENAI_API_KEY=your_key`

### "ChromaDB compatibility issue"
- **Cause**: Version mismatch between ChromaDB and LangChain
- **Fix**: The retriever has fallback logic, but you may need to update packages

---

## Summary

This backend is a **RAG-powered chatbot** that:
1. Stores NELFUND documents as searchable vectors
2. Uses LangGraph to orchestrate query processing
3. Retrieves relevant document chunks for each question
4. Generates accurate, cited answers using OpenAI

The architecture is modular, making it easy to:
- Add new document types
- Modify the agent workflow
- Change the LLM model
- Add new features (e.g., conversation history)

---

## Additional Notes

- The `agent.py` and `qa_chain.py` files are placeholders/alternatives not currently used
- The `download_nelfund_docs.py` script is optional - you can manually add documents to `data/nelfund_docs/`
- The system is designed to be stateless (no conversation memory yet, but session_id is accepted for future use)
