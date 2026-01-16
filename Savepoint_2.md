# Savepoint 2: Refactoring & Stabilization

**Date:** January 16, 2026  
**Status:** ✅ Stable / Tested  

## 1. Project Overview
**Rooster-HackCrypt** is an AI-powered educational platform that generates adaptive quizzes from PDF documents. It uses Retrieval Augmented Generation (RAG) to create questions tailored to the user's performance level.

## 2. Architecture Snapshot

### Backend (`/backend`)
*   **Core Logic**: Python 3.13+
*   **LLM Integration**: LangChain + Groq / Google GenAI
*   **Database**: ChromaDB (Vector Store) for document embeddings.
*   **Framework**: Modular script-based architecture (CLI demo available).

### Key Modules
| File | Purpose |
| :--- | :--- |
| **`ingestion_main.py`** | Handles PDF uploading, chunking, and indexing into ChromaDB. |
| **`quiz_generation_main.py`** | Manages user sessions, quiz state, and orchestrates question generation based on difficulty. |
| **`demo.py`** | The main CLI entry point. User-friendly menu for Ingestion, Adaptive Mode, and Grind Mode. |
| **`storage.py`** | Centralized vector database configuration and access. |
| **`agent.py`** | Wrappers for LLM interactions (Groq). |
| **`schemas.py`** | Pydantic models for data validation. |

## 3. Recent Critical Changes

### A. Refactoring (Modularization)
*   **Split `ingestion_main.py`**: Separated monolithic logic into distinct concerns (`quiz_generation_main.py`, `grind_mode.py`, `difficulty_engine.py`).
*   **Circular Imports**: Resolved dependency cycles between storage, logic, and ingestion modules.

### B. Bug Fixes
*   **Crash in `list_active_sessions`**: Fixed a `TypeError` where listing sessions returned full dictionaries (unhashable) instead of ID strings.
    *   *Fix*: Updated return type to `List[str]`.
*   **Dependency Hell**:
    *   Resolved conflicts with `tf-keras` (Keras 3 vs Transformers).
    *   Added missing `langchain-chroma` and `langchain-community` packages.

## 4. Environment & Usage

### Prerequisites
*   Python 3.10+ (Tested on 3.13)
*   `.env` file with `GROQ_API_KEY` (or Google API key).

### Installation
```bash
pip install -r backend/requirements.txt
# Note: You may need to manually install 'langchain-chroma' and 'tf-keras' if not in requirements.
pip install langchain-chroma tf-keras langchain-community
```

### Running the Project
The logic is now verified via `demo.py` (interactive) and `test_reproduction.py` (automated).

**Interactive Mode:**
```bash
cd backend
python demo.py
```
*Flow*: Ingest PDF -> Start Adaptive Session -> Take Quiz.

## 5. Next Steps
*   Frontend integration (connecting React to these Python scripts/API).
*   Refining the difficulty adjustment algorithm in `difficulty_engine.py`.
