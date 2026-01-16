# Rooster-HackCrypt

AI-powered adaptive learning engine that turns learning material into grounded quizzes.

**Date:** January 16, 2026  
**Status:** ✅ MVP Stable / Verified (CLI-first)

---

## What This Project Is

Rooster-HackCrypt converts learning material into a searchable knowledge base and generates quizzes that:

- Are **grounded in your source content** via Retrieval-Augmented Generation (RAG)
- Support **adaptive difficulty** (keeps learners in “flow”) or fixed **grind mode** practice
- Work from multiple material sources:
    - **PDFs**
    - **YouTube videos** (transcripts)
    - **Syllabus topics** (LLM-generated chapter text)

The core idea: store *semantic facts* (propositions) for retrieval, but present questions using full parent context.

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
4. **Session engines**: track learner state, difficulty, mastery over time
5. **CLI demo**: ties everything together end-to-end

### Component Map

```
                    ┌───────────────────────┐
                    │   CLI Demo (Menu)     │
                    │ backend/testing/demo.py│
                    └───────────┬───────────┘
                                            │
                                            ▼
                 ┌───────────────────────────┐
                 │ IngestionService           │
                 │ src/rag/ingestion_main.py  │
                 └───────────┬───────────────┘
                                         │  produces
                                         │  parent chunks + propositions
                                         ▼
            ┌───────────────────────────────┐
            │ KnowledgeBase                  │
            │ src/rag/storage.py             │
            │  - ChromaDB (propositions)     │
            │  - Docstore (parent docs)      │
            └───────────┬───────────────────┘
                                    │ retrieves context
                                    ▼
            ┌───────────────────────────────┐
            │ QuizAgent (LangGraph)          │
            │ src/agents/agent.py            │
            └───────────┬───────────────────┘
                                    │ generates quizzes
                                    ▼
            ┌───────────────────────────────┐
            │ AdaptiveLogic / Difficulty      │
            │ src/core/logic_engine.py        │
            │ src/core/difficulty_engine.py   │
            └───────────────────────────────┘
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
├─ backend/
│  ├─ requirements.txt
│  ├─ src/
│  │  ├─ agents/                 # LangGraph quiz agent
│  │  ├─ core/                   # Adaptive engine + difficulty config
│  │  ├─ features/               # Quiz/session orchestration
│  │  ├─ loaders/                # PDF/YouTube/Syllabus loaders
│  │  ├─ rag/                    # ingestion + storage + preprocessing
│  │  └─ models/                 # pydantic schemas
│  ├─ testing/                   # CLI demo + dev scripts
│  └─ data/                      # embedding cache (and optional local data)
├─ data/                         # additional caches/data (workspace-level)
└─ docs/                         # design notes, checkpoints
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

## MVP Scope / Notes

- This repository is currently backend + CLI Demo
- The system is designed so a frontend can be layered on later (sessions, quiz JSON output, etc.).
