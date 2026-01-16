# Rooster-HackCrypt

AI-powered adaptive learning engine that turns learning material into grounded quizzes.

**Date:** January 17, 2026  
**Status:** ✅ Production-Ready MVP with Full API Suite

---

## What This Project Is

Rooster-HackCrypt converts learning material into a searchable knowledge base and generates quizzes that:

- Are **grounded in your source content** via Retrieval-Augmented Generation (RAG)
- Support **adaptive difficulty** (keeps learners in “flow”) or fixed **grind mode** practice
- Provide **instant flash-note generation** (zero LLM cost cheat sheets)
- Offer **AI-powered doubt solving** with ELI5 explanations
- Include **Smart Learning features** (Socratic hints + session analysis)
- Work from multiple material sources:
    - **PDFs**
    - **YouTube videos** (transcripts)
    - **Syllabus topics** (LLM-generated chapter text)

The core idea: store *semantic facts* (propositions) for retrieval, enable both quiz generation and instant fact access.

---

## ✨ Key Features

### 🎯 Quiz Generation
- **Adaptive Mode**: Automatically adjusts difficulty based on performance
- **Grind Mode**: Practice at fixed difficulty levels
- **RAG-Grounded**: Questions sourced from your actual learning materials

### ⚡ Flash-Note Generator
- **Zero LLM Cost**: Retrieves facts directly from vector store
- **Instant Cheat Sheets**: Get quick summaries without waiting for LLM
- **Context-Aware**: Uses semantic search for relevant information

### 🤔 Doubt Solver (AI Tutor)
- **ELI5 Explanations**: Breaks down complex concepts into simple terms
- **Interactive Learning**: Uses LangGraph for stateful conversations
- **Contextual Help**: Answers based on your uploaded materials

### 🧠 Smart Learning
- **Socratic Hints**: Get guiding questions instead of direct answers
- **AI Sensei**: Session analysis with personalized feedback
- **Pattern Recognition**: Identifies knowledge gaps and misconceptions

---

## Core Concepts (The “Why”)

### Proposition Decomposition
Instead of embedding raw chunks only, the ingestion pipeline can decompose text into atomic facts ("propositions").
This increases retrieval precision because the vector DB matches to fine-grained factual statements.

### Hybrid Storage (RAG + Reconstruction)
Rooster uses a two-tier store:

- **ChromaDB** stores proposition embeddings for fast semantic search
- A persistent **docstore** (pickle) stores the original “parent” chunks so retrieval can return full context

### Adaptive Learning
An adaptive engine tracks performance and adjusts difficulty over time for a given session, topic, and source.
You can also bypass adaptation and do fixed-difficulty practice (grind mode).

---

## Tech Stack

### Backend
- **Python** (CLI-driven MVP)
- **LangChain + LangGraph**: RAG orchestration and stateful agent workflow
- **Groq (langchain-groq)**: LLM inference (configured as `llama-3.1-8b-instant`)
- **HuggingFace Embeddings (langchain-huggingface)**: local embeddings
    - Model: `sentence-transformers/paraphrase-MiniLM-L3-v2`
- **ChromaDB**: persistent local vector DB

### Document / Content Ingestion
- **PyPDFLoader** (LangChain community)
- **unstructured[pdf]** + OCR utilities (optional): `pytesseract`, `pdf2image`, `pillow`
- **youtube-transcript-api**: transcript retrieval
- **requests + beautifulsoup4**: URL scraping utilities (used by URL loader patterns)

---

## System Architecture (High Level)

At a high level, the system is split into:

1. **Ingestion service**: takes source material → produces parent chunks + propositions → indexes storage
2. **Knowledge base**: persistent store for retrieval (vector + docstore)
3. **Quiz agent**: retrieves context + prompts LLM → structured quiz output
4. **Flash-note generator**: retrieves raw propositions for instant cheat sheets (zero LLM cost)
5. **Doubt solver**: AI tutor that provides ELI5 explanations for student questions
6. **Smart learning**: Socratic hints and session analysis for advanced pedagogy
7. **Session engines**: track learner state, difficulty, mastery over time
8. **FastAPI REST API**: Exposes all features via HTTP endpoints
9. **CLI demo**: ties everything together end-to-end

### Component Map

```
                    ┌───────────────────────┐
                    │   CLI Demo (Menu)     │
                    │ backend/testing/demo.py│
                    └───────────┬───────────┘
                                │
                 ┌──────────────┴───────────────┐
                 │                              │
                 ▼                              ▼
┌─────────────────────────────┐   ┌────────────────────────────┐
│ IngestionService            │   │ FastAPI REST API           │
│ src/rag/ingestion_main.py   │   │ backend/api/main.py        │
└───────────┬─────────────────┘   └────────────┬───────────────┘
            │ produces                          │
            │ parent chunks + propositions      │
            ▼                                   │
┌───────────────────────────────┐              │
│ KnowledgeBase                 │◄─────────────┘
│ src/rag/storage.py            │
│  - ChromaDB (propositions)    │
│  - Docstore (parent docs)     │
└───────────┬───────────────────┘
            │ retrieves context
            ▼
┌───────────────────────────────┐  ┌────────────────────────────┐
│ QuizAgent (LangGraph)         │  │ FlashNoteGenerator         │
│ src/agents/agent.py           │  │ src/features/flash_note... │
└───────────┬───────────────────┘  └────────────┬───────────────┘
            │ generates quizzes                 │ zero-cost facts
            ▼                                   ▼
┌───────────────────────────────┐  ┌────────────────────────────┐
│ AdaptiveLogic / Difficulty    │  │ DoubtSolverAgent           │
│ src/core/logic_engine.py      │  │ src/features/doubt_solver  │
│ src/core/difficulty_engine.py │  │ ELI5 explanations          │
└───────────────────────────────┘  └────────────────────────────┘
                                   ┌────────────────────────────┐
                                   │ Smart Learning (NEW)       │
                                   │ src/features/smart_learn.. │
                                   │ - Socratic Hints           │
                                   │ - Session Analysis         │
                                   └────────────────────────────┘
```

---

## Data Flow (End-to-End)

### 1) Ingestion Pipeline
Entry points: `src/rag/ingestion_main.py`

**For PDF**
1. Load PDF → split into parent chunks (~3000 chars)
2. Decompose chunks into propositions (LLM) with rate-limit-aware fallbacks
3. Store:
     - propositions → ChromaDB (with `pdf_source_id` metadata)
     - parent chunks → docstore pickle (with `pdf_source_id` metadata)

**For YouTube**
1. Extract video ID from URL
2. Fetch transcript text
3. Split into parent chunks → index like PDFs (with `pdf_source_id`)

**For Syllabus**
1. LLM generates a chapter-style document for the topic
2. Split into parent chunks → index like PDFs (with `pdf_source_id`)

### 2) Retrieval + Quiz Generation
Entry points: `src/features/quiz_generation_main.py`, `src/agents/agent.py`

1. User starts a session: `pdf_source_id` + `topic` + mode
2. Agent retrieves context:
     - If `topic == "default"`: sample random parent docs from the selected source
     - Else: semantic search propositions in ChromaDB → map to parent docs in docstore
3. LLM generates a quiz from retrieved context (structured JSON format)
4. Session engine updates mastery/difficulty based on results

---

## Persistence & Data Directories (Important)

The knowledge base stores data on disk:

- ChromaDB: `./data/chroma_db`
- Docstore: `./data/docstore/documents.pkl`

**These paths are relative to your current working directory when you run the program.**

That means if you run the demo from different folders, you can accidentally create multiple independent databases.

Recommended approach:

- Always run the CLI from the same directory (see “Run” below)

---

## Repository Structure (Actual)

```
.
├─ README.md
├─ API_README.md                 # FastAPI documentation
├─ backend/
│  ├─ requirements.txt
│  ├─ run_api.py                 # API server launcher
│  ├─ api/                       # FastAPI application
│  │  ├─ main.py                 # API entry point
│  │  ├─ config.py               # Settings/environment
│  │  ├─ routers/                # Endpoint routers
│  │  │  ├─ health.py            # Health checks
│  │  │  ├─ materials.py         # Material listing
│  │  │  ├─ ingestion.py         # PDF/YouTube/Syllabus upload
│  │  │  ├─ quiz.py              # Quiz & session management
│  │  │  ├─ flashnotes.py        # Flash-note generation
│  │  │  ├─ doubt_solver.py      # Doubt solver
│  │  │  └─ smart_learning.py    # Socratic hints + session analysis (NEW)
│  │  ├─ services/               # Business logic
│  │  ├─ models/                 # Pydantic request/response models
│  │  └─ middleware/             # Error handling
│  ├─ src/
│  │  ├─ agents/                 # LangGraph quiz agent
│  │  ├─ core/                   # Adaptive engine + difficulty config
│  │  ├─ features/               # Quiz/session + flash-note generator
│  │  │  ├─ quiz_generation_main.py
│  │  │  ├─ flash_note_generator.py
│  │  │  ├─ doubt_solver.py      # AI tutor
│  │  │  └─ smart_learning.py    # Socratic hints + session analysis (NEW)
│  │  ├─ loaders/                # PDF/YouTube/Syllabus loaders
│  │  ├─ rag/                    # ingestion + storage + preprocessing
│  │  └─ models/                 # pydantic schemas
│  ├─ testing/                   # CLI demo + dev scripts
│  └─ data/                      # embedding cache (and optional local data)
├─ data/                         # additional caches/data (workspace-level)
└─ docs/                         # design notes, checkpoints
   ├─ Flashcard_Readme.md        # Flash-note feature documentation
   ├─ DoubtSolver_Readme.md      # Doubt solver feature documentation
   ├─ SmartLearning_Readme.md    # Smart Learning features documentation (NEW)
   └─ ...
```

---

## Setup

### Prerequisites
- Python 3.10+
- A `.env` file containing:

```
GROQ_API_KEY=...
```

### Install

From repo root:

```bash
pip install -r backend/requirements.txt
```

---

## Run (CLI Demo)

The primary testing UI is the menu-driven CLI:

```bash
cd backend/testing
python demo.py
```

From the menu you can:

- Ingest PDFs
- Ingest YouTube transcript URLs
- Generate syllabus content
- Start Adaptive sessions and generate quizzes
- Run Grind Mode practice

Tip: when prompted for topic, type `default` to generate questions from the entire selected source.

---

## Run (FastAPI Server)

For frontend integration or API access:

```bash
cd backend

# Activate virtual environment (Windows)
..\venv\Scripts\Activate.ps1

# Run the API server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Server will start at `http://localhost:8000`

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Key Endpoints:**
- `POST /api/v1/ingest/pdf` - Upload PDF files
- `POST /api/v1/ingest/youtube` - Ingest YouTube videos
- `POST /api/v1/sessions/adaptive` - Create adaptive quiz session
- `POST /api/v1/sessions/{id}/quiz` - Generate quiz
- `GET /api/v1/cheat-sheet` - **Flash-note generator**
- `POST /api/v1/solve-doubt` - **AI tutor for doubts**
- `POST /api/v1/hint/socratic` - **Socratic hints**
- `POST /api/v1/analyze-session` - **Session analysis**

See [API_README.md](API_README.md) for complete API documentation.

---

## Troubleshooting

### “No documents found in source”
- Make sure you are selecting the correct `pdf_source_id` from the menu.
- Ensure you’re running the demo from the same working directory you used when ingesting.
    - Example: If you ingested while in `backend/testing`, run quizzes from `backend/testing` too.

### YouTube transcript issues
- Some videos have captions disabled or unavailable.
- The loader depends on `youtube-transcript-api`, which can fail for:
    - transcripts disabled
    - region restrictions
    - age-restricted videos

### Embeddings model not found
Embeddings are configured with `local_files_only=True`. Ensure the model is cached under:

- `backend/data/embeddings_cache/`

If you’re moving machines, you may need to download the model once (via normal HuggingFace behavior) and keep it cached.

---

## Project Status & Roadmap

### ✅ Completed (v1.0 - Current)

**Core Infrastructure:**
- ✅ RAG-based ingestion pipeline (PDF, YouTube, Syllabus)
- ✅ ChromaDB vector storage + Docstore
- ✅ Proposition decomposition for semantic search
- ✅ FastAPI REST API with 7 routers, 15+ endpoints
- ✅ CLI demo interface

**Learning Features:**
- ✅ Adaptive quiz generation with difficulty tracking
- ✅ Grind mode (fixed difficulty practice)
- ✅ Flash-note generator (zero-cost fact retrieval)
- ✅ Doubt Solver (ELI5 AI tutor with LangGraph)
- ✅ Socratic Hints (guided learning questions)
- ✅ AI Sensei (session analysis & feedback)

**Documentation:**
- ✅ Complete API documentation ([API_README.md](API_README.md))
- ✅ Feature-specific guides ([docs/](docs/))
- ✅ Integration examples (React, Python)

### 🚧 Future Enhancements

**Frontend:**
- [ ] React/Next.js web application
- [ ] Student dashboard with progress tracking
- [ ] Material upload interface
- [ ] Interactive quiz interface

**Features:**
- [ ] Multi-language support
- [ ] Collaborative learning (group sessions)
- [ ] Visual analytics and progress charts
- [ ] Spaced repetition integration
- [ ] Export/import study materials

**Infrastructure:**
- [ ] User authentication (JWT)
- [ ] PostgreSQL for user data
- [ ] Redis caching layer
- [ ] Deployment guides (Docker, cloud)

---

## Notes

- Backend is fully functional and production-ready
- API designed for easy frontend integration
- All features thoroughly documented
- Session management supports stateful learning workflows
