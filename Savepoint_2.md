# Rooster-HackCrypt: AI-Powered Adaptive Learning Engine

**Date:** January 16, 2026
**Status:** ✅ MVP Stable / Verified

---

## 🚀 Project Vision
**Rooster-HackCrypt** transforms static educational content (PDFs) into dynamic, personalized learning experiences. Unlike standard quiz generators, it features an **Adaptive Logic Engine** that "learns the learner," automatically adjusting difficulty based on real-time performance to maintain the optimal "flow state" for students.

It is built for **speed, cost-efficiency, and accuracy**, utilizing highly optimized open-source models (Llama-3 via Groq) and local vector storage to ensure zero-cost operation during development.

---

## 🌟 Core MVP Features

### 1. 🧠 Intelligent Document Ingestion
Turns raw PDFs into a structured knowledge base.
*   **Proposition Decomposition**: Instead of just chunking text, it extracts atomic facts ("propositions") to improve retrieval accuracy.
*   **Hybrid Indexing**: Uses ChromaDB for semantic search and local storage for document reconstruction.
*   **Tech**: `Unstructured` for parsing, `Llama-3` for proposition extraction.

### 2. 🎯 Adaptive Logic Engine
The "brain" that manages student progression.
*   **Dynamic Difficulty**: Automatically promotes users (Easy → Medium → Hard) as they master topics.
*   **Mastery Tracking**: Calculates a weighted mastery score (70% historical performance + 30% recent blitz).
*   **Session State**: Maintains context across multiple quiz batches, ensuring continuity.

### 3. 🤖 LangGraph Agent Workflow
A sophisticated state-machine agent for generating content.
*   **RAG (Retrieval Augmented Generation)**: Fetches *only* relevant context from the uploaded material to ground every question in facts (Hallucination reduction).
*   **Structured Output**: Generates strictly formatted JSON quizzes compatible with frontend rendering.
*   **Contextual Awareness**: Generates questions specifically targeted at the user's current difficulty level.

### 4. 🏋️ Grind Mode
A "Gym" for your brain.
*   **Practice Sandbox**: Allows users to manually overwrite the adaptive engine.
*   **Spaced Repetition Ready**: Designed to support rapid-fire practice on weak areas.

---

## 🏗️ Technical Architecture

### High-Level Stack
| Component | Technology | Reasoning |
| :--- | :--- | :--- |
| **LLM Inference** | **Groq API** (Llama-3-8b-instant) | **500+ tokens/sec** speed for real-time interactivity. |
| **Embeddings** | **HuggingFace** (`all-MiniLM-L6-v2`) | High-performance, **local execution**, zero API cost. |
| **Vector DB** | **ChromaDB** | Local, persistent vector storage for semantic retrieval. |
| **Orchestration** | **LangChain** + **LangGraph** | Manages complex RAG flows and stateful agent behaviors. |

### Data Flow Pipeline

#### A. Ingestion Pipeline (`ingestion_main.py`)
1.  **Teacher uploads PDF** -> `DocumentProcessor` parses text.
2.  **Splitting**: Text is divided into parent chunks (~3000 chars).
3.  **Proposition Extraction**: LLM converts chunks into atomic statements (improves matching).
4.  **Indexing**: Embeddings are generated and stored in `KnowledgeBase` (ChromaDB).

#### B. Quiz Generation Loop (`quiz_generation_main.py`)
1.  **User Request**: Defined by Topic & Session ID.
2.  **State Check**: `AdaptiveLogic` checks current Mastery Score.
    *   *If Mastery > 80% & Streak > 2* → **Increase Difficulty**.
    *   *If Mastery < 40% & Streak < -2* → **Decrease Difficulty**.
3.  **Retrieval**: `QuizAgent` searches Vector DB for topic-relevant chunks.
4.  **Generation**: LLM generates 5 formatted questions based *only* on retrieved context.
5.  **Feedback**: User answers are scored; `AdaptiveLogic` updates the session state.

---

## 📂 Project Structure Map

```text
backend/
├── logic_engine.py         # 🧠 The Brain: State machine for difficulty & mastery
├── agent.py                # 🤖 The Worker: LangGraph agent for RAG & Generation
├── ingestion_main.py       # 📥 The Mouth: Parsing & Indexing pipeline
├── quiz_generation_main.py # 🎮 The Controller: Session management & User flow
├── storage.py              # 🗄️ The Memory: ChromaDB wrapper
├── schemas.py              # 📏 The Rules: Pydantic data models
└── demo.py                 # 🖥️ The Interface: CLI for testing the full loop
```

## 🛠️ Setup & Run

### Prerequisites
*   Python 3.10+
*   `.env` file with `GROQ_API_KEY`

### Quick Start
```bash
# 1. Install Dependencies
pip install -r backend/requirements.txt
# (Ensure langchain-chroma and tf-keras are installed)

# 2. Run the Interactive Demo
python backend/demo.py
```
*   **Option 1 (Ingestion)**: Upload new learning material.
*   **Option 2 (Adaptive Mode)**: Experience the AI adjusting to your skill level.
*   **Option 3 (Grind Mode)**: Practice the topics in which you struggle
