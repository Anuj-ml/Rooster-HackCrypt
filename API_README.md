# Rooster-HackCrypt API Documentation

Complete REST API for the AI-Powered Adaptive Learning Engine.

---

## Table of Contents

- [Quick Start](#quick-start)
- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Health](#health-endpoints)
  - [Materials](#materials-endpoints)
  - [Ingestion](#ingestion-endpoints)
  - [Sessions & Quizzes](#sessions--quizzes-endpoints)
  - [Doubt Solver](#doubt-solver-endpoints)
  - [Smart Learning](#smart-learning-endpoints)
  - [Study Groups](#study-groups-endpoints)
- [Request/Response Formats](#requestresponse-formats)
- [Error Handling](#error-handling)
- [Frontend Integration Guide](#frontend-integration-guide)
- [Code Examples](#code-examples)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Python 3.10+
- Virtual environment with dependencies installed
- `.env` file with `GROQ_API_KEY`

### Running the API Server

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (Windows)
..\venv\Scripts\activate

# Run the API server with uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

#### Additional Uvicorn Options

```bash
# Development mode with auto-reload
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Specify number of workers (production)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Custom port
uvicorn api.main:app --host 0.0.0.0 --port 3001
```

The server will start at `http://localhost:8000`

### Verify It's Running

```bash
# Check health endpoint
curl http://localhost:8000/api/health
```

### Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API Overview

The Rooster-HackCrypt API provides endpoints for:

| Feature | Description |
|---------|-------------|
| **Document Ingestion** | Upload PDFs, YouTube videos, or generate syllabus content |
| **Material Management** | List and manage indexed learning materials |
| **Session Management** | Create adaptive or grind mode learning sessions |
| **Quiz Generation** | Generate AI-powered quizzes from your materials |
| **Flash-Note Generator** | ⚡ Instant cheat sheets with zero LLM cost |
| **Doubt Solver** | 💡 ELI5 explanations for student questions |
| **Smart Learning** | 🧠 **NEW**: Socratic hints + session analysis |
| **Study Groups** | 👥 **NEW**: Collaborative learning with shared resources |
| **Progress Tracking** | Submit answers and track mastery scores |

---

## Backend Architecture & Logic Flow

To understand how the API processes requests, it helps to know the underlying logic flow.

### 1. Request Lifecycle
All requests follow a standard path:
`Client` → `FastAPI Router` → `Service Layer` → `Core Logic/Agent` → `Database/Response`

- **Routers** (`api/routers/`): Handle HTTP request validation and response formatting.
- **Services** (`api/services/`): Coordinate business logic and call core engines.
- **Core Engines** (`src/core/`): Pure logic components (e.g., adaptive difficulty calculation).
- **Agents** (`src/agents/`): Stateful LangGraph agents for complex AI tasks (Quiz Generation, Doubt Solving).

### 2. Logic Engine (Adaptive Difficulty)
The "Brain" of the adaptive learning system is the `LogicEngine` and `DifficultyEngine`.
- **Input**: User's current session state, difficulty history, and last answer correctness.
- **Process**: Calculates a "Mastery Score" (0-100) and determines the next difficulty level.
- **Output**: Updated session state and difficulty parameters for the next question.

### 3. AI Agents (LangGraph)
Complex tasks use LangGraph state machines:
- **Quiz Agent**: Retrieves documents → Formulates questions → Validates against source material.
- **Doubt Solver**: Retrieves context → Reasons about the answer → Generates ELI5 explanation.

This separation ensures that the API is just an interface to a robust, modular backend system.

---

## Authentication

> **Note**: Authentication is not yet implemented. All endpoints are currently open.
> Future versions will support JWT-based authentication.

---

## Base URL

```
Development: http://localhost:8000
Production:  https://your-domain.com
```

All API endpoints are prefixed with `/api/v1/` except health checks which use `/api/`.

---

## Endpoints

### Health Endpoints

#### `GET /api/health`

Full health check of all system components.

**Response:**
```json
{
  "success": true,
  "message": "System status: healthy",
  "data": {
    "status": "healthy",
    "components": {
      "api": "ok",
      "llm": "ok",
      "data_directory": "ok",
      "temp_uploads": "ok"
    },
    "version": "1.0.0",
    "timestamp": "2026-01-17T10:30:00.000Z"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `GET /api/health/ready`

Kubernetes-style readiness probe.

**Response:**
```json
{"status": "ready"}
```

#### `GET /api/health/live`

Kubernetes-style liveness probe.

**Response:**
```json
{"status": "alive"}
```

---

### Materials Endpoints

#### `GET /api/v1/materials`

List all indexed learning materials.

**Response:**
```json
{
  "success": true,
  "message": "Found 5 indexed materials",
  "data": {
    "sources": ["sql_basics", "neural_networks", "youtube_abc123"],
    "count": 3
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `GET /api/v1/materials/{source_id}`

Get details about a specific material.

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| `source_id` | string | path | Material identifier |

**Response:**
```json
{
  "success": true,
  "message": "Material 'sql_basics' found",
  "data": {
    "source_id": "sql_basics",
    "document_count": 15,
    "exists": true
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

---

### Ingestion Endpoints

#### `POST /api/v1/ingest/pdf`

Upload and process a PDF file.

**Content-Type:** `multipart/form-data`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file` | file | Yes | PDF file to upload (max 50MB) |
| `source_id` | string | No | Custom identifier (defaults to filename) |

**Example (JavaScript/Fetch):**
```javascript
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('source_id', 'my_document');

const response = await fetch('/api/v1/ingest/pdf', {
  method: 'POST',
  body: formData
});
```

**Response:**
```json
{
  "success": true,
  "message": "PDF 'document.pdf' ingested successfully",
  "data": {
    "source_id": "my_document",
    "material_type": "PDF",
    "num_documents": 12,
    "num_propositions": 156
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `POST /api/v1/ingest/youtube`

Ingest a YouTube video transcript.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "source_id": "my_video"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "YouTube video transcript ingested successfully",
  "data": {
    "source_id": "youtube_dQw4w9WgXcQ",
    "material_type": "YOUTUBE",
    "num_documents": 8,
    "num_propositions": 94
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `POST /api/v1/ingest/syllabus`

Generate educational content for a topic using AI.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "topic": "Introduction to Machine Learning",
  "source_id": "ml_intro"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Syllabus content for 'Introduction to Machine Learning' generated and indexed",
  "data": {
    "source_id": "syllabus_introduction_to_machine_l",
    "material_type": "SYLLABUS",
    "num_documents": 3,
    "num_propositions": 47
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

> **Note:** Syllabus generation may take 30-60 seconds.

---

### Sessions & Quizzes Endpoints

#### `POST /api/v1/sessions/adaptive`

Create an adaptive learning session with auto-adjusting difficulty.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "user_id": "user_123",
  "source_id": "sql_basics",
  "topic": "default",
  "initial_difficulty": "EASY"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `user_id` | string | Yes | - | Unique user identifier |
| `source_id` | string | Yes | - | Material to quiz from |
| `topic` | string | No | "default" | Topic focus ("default" = entire document) |
| `initial_difficulty` | enum | No | "EASY" | EASY, MEDIUM, or HARD |

**Response:**
```json
{
  "success": true,
  "message": "Adaptive session created successfully",
  "data": {
    "session_id": "sess_abc123def456",
    "mode": "ADAPTIVE",
    "initial_difficulty": "EASY",
    "topic": "default",
    "source_id": "sql_basics"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `POST /api/v1/sessions/grind`

Create a grind mode session for focused practice.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "user_id": "user_123",
  "source_id": "sql_basics",
  "topic": "SELECT statements",
  "difficulty": "MEDIUM",
  "dynamic_difficulty": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `user_id` | string | Yes | - | Unique user identifier |
| `source_id` | string | Yes | - | Material to quiz from |
| `topic` | string | No | "default" | Topic focus |
| `difficulty` | enum | No | "EASY" | EASY, MEDIUM, or HARD |
| `dynamic_difficulty` | boolean | No | true | Slowly adjust based on performance |

**Response:**
```json
{
  "success": true,
  "message": "Grind session created successfully",
  "data": {
    "session_id": "sess_xyz789abc012",
    "mode": "GRIND",
    "initial_difficulty": "MEDIUM",
    "topic": "SELECT statements",
    "source_id": "sql_basics"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `GET /api/v1/sessions`

List all active sessions.

**Response:**
```json
{
  "success": true,
  "message": "Found 2 active sessions",
  "data": {
    "sessions": [
      {
        "session_id": "sess_abc123",
        "user_id": "user_123",
        "source_id": "sql_basics",
        "topic": "default",
        "mode": "ADAPTIVE",
        "current_difficulty": "MEDIUM"
      }
    ],
    "count": 1
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `GET /api/v1/sessions/{session_id}`

Get detailed statistics for a session.

**Response:**
```json
{
  "success": true,
  "message": "Session stats retrieved",
  "data": {
    "session_id": "sess_abc123",
    "mode": "ADAPTIVE",
    "current_difficulty": "MEDIUM",
    "total_questions": 25,
    "correct_answers": 18,
    "mastery_score": 72.0,
    "streak": 3,
    "difficulty_history": ["EASY", "EASY", "MEDIUM"]
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `DELETE /api/v1/sessions/{session_id}`

Delete a session.

**Response:**
```json
{
  "success": true,
  "message": "Session 'sess_abc123' deleted successfully",
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `POST /api/v1/sessions/{session_id}/quiz`

Generate a quiz for the session.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "num_questions": 5
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `num_questions` | integer | No | 5 | 1-20 questions |

**Response:**
```json
{
  "success": true,
  "message": "Generated 5 questions",
  "data": {
    "session_id": "sess_abc123",
    "difficulty": "MEDIUM",
    "questions": [
      {
        "question": "What SQL keyword is used to retrieve data from a database?",
        "options": [
          "a) INSERT",
          "b) SELECT",
          "c) UPDATE",
          "d) DELETE"
        ],
        "correct_answer": "SELECT",
        "explanation": "SELECT is the SQL command used to retrieve data from one or more tables."
      }
    ],
    "question_count": 5
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `POST /api/v1/sessions/{session_id}/submit`

Submit quiz answers and get feedback.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "answers": [true, false, true, true, false]
}
```

> **Note:** `answers` is an array of booleans where `true` = correct, `false` = incorrect.
> The order must match the questions from the quiz.

**Response:**
```json
{
  "success": true,
  "message": "Quiz submitted successfully",
  "data": {
    "session_id": "sess_abc123",
    "correct_count": 3,
    "total_count": 5,
    "score_percentage": 60.0,
    "new_difficulty": "MEDIUM",
    "mastery_score": 65.5,
    "streak": 1,
    "difficulty_changed": false,
    "feedback_message": "Good job! Keep practicing to improve further."
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

---

### Doubt Solver Endpoints

#### `POST /api/v1/solve-doubt`

Solve a student's doubt with an ELI5 (Explain Like I'm 5) explanation.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "question": "What is photosynthesis?",
  "pdf_source_id": "biology_textbook",
  "session_id": "optional-uuid"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | Student's question about the material |
| `pdf_source_id` | string | Yes | Which material to search for answer |
| `session_id` | string | No | Auto-generated if not provided |

**Response:**
```json
{
  "success": true,
  "message": "Doubt solved successfully",
  "data": {
    "session_id": "abc-123-def-456",
    "question": "What is photosynthesis?",
    "answer": "Photosynthesis is like a plant's kitchen! Just like you need ingredients to make food, plants use sunlight (their main ingredient), water, and carbon dioxide from the air. They mix these together in their leaves to make sugar (their food) and release oxygen as a byproduct. It's like the plant is cooking its own meal using sunlight as the stove!",
    "source_id": "biology_textbook",
    "context_found": true
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Key Features:**
- ✅ **ELI5 Explanations** - Simple, conversational language
- ✅ **Grounded Answers** - Only uses uploaded material
- ✅ **Real-World Analogies** - Makes concepts relatable
- ✅ **No Hallucinations** - Won't make up information

#### `GET /api/v1/solve-doubt/sources`

List all available materials for doubt solving.

**Response:**
```json
{
  "success": true,
  "message": "Found 3 available materials",
  "data": {
    "sources": ["biology_textbook", "chemistry_notes", "physics_lecture"],
    "count": 3
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

---

### Smart Learning Endpoints

#### `POST /api/v1/hint/socratic`

Generate a Socratic hint - a guiding question instead of a direct answer.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "question": "What is the capital of France?",
  "correct_answer": "Paris",
  "student_answer": "London"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | The quiz question |
| `correct_answer` | string | Yes | The correct answer |
| `student_answer` | string | No | Student's wrong answer (helps contextualize hint) |

**Response:**
```json
{
  "success": true,
  "message": "Hint generated successfully",
  "data": {
    "hint": "Which city is home to the Eiffel Tower?"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Key Features:**
- ✅ **Socratic Method** - Guides thinking without revealing answer
- ✅ **Concise** - Hints under 20 words
- ✅ **Context-Aware** - Uses student's wrong answer to tailor guidance
- ✅ **Promotes Learning** - Encourages active problem-solving

**Use Cases:**
- Student gets quiz question wrong
- Want to guide without spoiling
- Building critical thinking skills
- Maintaining student engagement

---

#### `POST /api/v1/analyze-session`

Analyze a complete quiz session and provide personalized feedback.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "results": [
    {
      "question": "What is photosynthesis?",
      "is_correct": false,
      "user_answer": "Plants breathing",
      "correct_answer": "Process where plants convert light energy into chemical energy"
    },
    {
      "question": "What do plants need for photosynthesis?",
      "is_correct": false,
      "user_answer": "Just water",
      "correct_answer": "Sunlight, water, and carbon dioxide"
    },
    {
      "question": "What is the powerhouse of the cell?",
      "is_correct": true,
      "user_answer": "Mitochondria",
      "correct_answer": "Mitochondria"
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `results` | array | Yes | Array of quiz results with questions, answers, correctness |
| `results[].question` | string | Yes | The quiz question |
| `results[].is_correct` | boolean | Yes | Whether answer was correct |
| `results[].user_answer` | string | Yes | Student's answer |
| `results[].correct_answer` | string | Yes | The correct answer |

**Response:**
```json
{
  "success": true,
  "message": "Session analyzed successfully",
  "data": {
    "analysis": "You have a foundational understanding of cellular biology but need to strengthen your grasp of photosynthesis mechanics. Review the inputs (light, water, CO₂) and outputs (glucose, oxygen) of photosynthesis, focusing on the light-dependent and light-independent reactions. Practice distinguishing between cellular respiration and photosynthesis to solidify these core concepts."
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Analysis Response (Perfect Score):**
```json
{
  "success": true,
  "message": "Session analyzed successfully",
  "data": {
    "analysis": "Excellent work! You answered all questions correctly. Keep up the great work!"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Key Features:**
- ✅ **Pattern Recognition** - Identifies common misconceptions
- ✅ **Concept Extraction** - Pinpoints specific topics needing review
- ✅ **Actionable Advice** - 2-3 sentences with clear next steps
- ✅ **Positive Reinforcement** - Acknowledges strengths
- ✅ **Performance Optimized** - Instant response for perfect scores (skips LLM)

**Use Cases:**
- After completing a quiz
- Reviewing student progress
- Identifying knowledge gaps
- Personalized study recommendations
- Tracking improvement over time

---

### Flash-Note Generator Endpoints

#### `GET /api/v1/cheat-sheet`

⚡ **NEW**: Generate instant cheat sheets of atomic facts with **zero LLM cost**.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `topic` | string | Yes | - | Topic to generate facts about |
| `source_id` | string | No | null | Filter facts from specific material |
| `num_facts` | integer | No | 20 | Number of facts (1-50) |

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/cheat-sheet?topic=Neural%20Networks&num_facts=25"
```

**Response:**
```json
{
  "success": true,
  "message": "Generated cheat sheet with 25 facts",
  "data": {
    "topic": "Neural Networks",
    "fact_count": 25,
    "cheat_sheet": [
      "• A neural network consists of interconnected layers of neurons.",
      "• The input layer receives raw data for processing.",
      "• Hidden layers perform feature extraction and transformation.",
      "• The output layer produces the final prediction or classification.",
      "• Weights determine the strength of connections between neurons.",
      "• Biases allow neurons to activate even with zero input.",
      "• Activation functions introduce non-linearity into the network.",
      "• Backpropagation calculates gradients for weight updates.",
      "• The learning rate controls the step size during optimization.",
      "• Overfitting occurs when a model memorizes training data.",
      ...
    ],
    "source_id": null
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

#### `GET /api/v1/cheat-sheet/by-source/{source_id}`

Generate comprehensive cheat sheet from an entire material source.

**Parameters:**
| Name | Type | Location | Required | Default | Description |
|------|------|----------|----------|---------|-------------|
| `source_id` | string | path | Yes | - | Material ID to generate facts from |
| `num_facts` | integer | query | No | 30 | Number of facts (1-50) |

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/cheat-sheet/by-source/sql_basics?num_facts=20"
```

**Response:**
```json
{
  "success": true,
  "message": "Generated cheat sheet with 20 facts from 'sql_basics'",
  "data": {
    "topic": "default",
    "fact_count": 20,
    "cheat_sheet": [
      "• SELECT statement retrieves data from database tables.",
      "• WHERE clause filters rows based on conditions.",
      "• JOIN combines rows from two or more tables.",
      "• PRIMARY KEY uniquely identifies each row in a table.",
      "• FOREIGN KEY establishes relationships between tables.",
      ...
    ],
    "source_id": "sql_basics"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Key Features:**
- ⚡ **Instant retrieval** (< 1 second)
- 💰 **Zero LLM cost** - Direct ChromaDB retrieval
- 📚 **Semantic search** - Most relevant facts first
- 🎯 **Topic-based or source-based** retrieval

**Use Cases:**
- Pre-exam quick review
- Material overview
- Study note generation
- Concept refresher

For detailed documentation, see [docs/Flashcard_Readme.md](docs/Flashcard_Readme.md).

---

### Study Groups Endpoints

👥 **NEW**: Collaborative learning feature allowing students to form groups and share learning resources.

**Key Features:**
- ✅ **Group Creation** - Form study groups with up to 2 members
- ✅ **Resource Sharing** - Upload PDFs that all group members can access
- ✅ **Automatic Indexing** - Uploaded resources are ingested into ChromaDB
- ✅ **Group Management** - Create, join, and manage study groups

**Use Cases:**
- Partner study sessions
- Shared resource libraries
- Collaborative learning
- Peer teaching

---

#### `POST /api/v1/groups/create`

Create a new study group.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "name": "Biology Study Group",
  "creator_id": "user_123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Group name (3-50 characters) |
| `creator_id` | string | Yes | User ID of the creator |

**Response:**
```json
{
  "success": true,
  "message": "Study group created successfully",
  "data": {
    "group_id": "grp_abc123",
    "name": "Biology Study Group",
    "members": ["user_123"],
    "max_members": 2,
    "resources": [],
    "created_at": "2026-01-17T10:30:00Z"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Constraints:**
- Maximum 2 students per group
- Creator is automatically added as first member
- Group names must be unique

---

#### `POST /api/v1/groups/join`

Join an existing study group.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "group_id": "grp_abc123",
  "user_id": "user_456"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `group_id` | string | Yes | ID of the group to join |
| `user_id` | string | Yes | User ID of the joining member |

**Response:**
```json
{
  "success": true,
  "message": "Joined study group successfully",
  "data": {
    "group_id": "grp_abc123",
    "name": "Biology Study Group",
    "members": ["user_123", "user_456"],
    "max_members": 2,
    "resources": ["bio_textbook_001"],
    "created_at": "2026-01-17T10:30:00Z"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Error Cases:**
- `404`: Group not found
- `400`: Group is full (max 2 members)
- `400`: User is already a member

---

#### `GET /api/v1/groups`

List all study groups.

**Response:**
```json
{
  "success": true,
  "data": {
    "groups": [
      {
        "group_id": "grp_abc123",
        "name": "Biology Study Group",
        "member_count": 2,
        "max_members": 2,
        "has_space": false
      },
      {
        "group_id": "grp_xyz789",
        "name": "Chemistry Lab Partners",
        "member_count": 1,
        "max_members": 2,
        "has_space": true
      }
    ],
    "total": 2
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Use Cases:**
- Browse available groups
- Find groups with open spots
- Discover study partners

---

#### `GET /api/v1/groups/{group_id}`

Get detailed information about a specific study group.

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| `group_id` | string | path | Group identifier |

**Response:**
```json
{
  "success": true,
  "data": {
    "group_id": "grp_abc123",
    "name": "Biology Study Group",
    "members": ["user_123", "user_456"],
    "max_members": 2,
    "resources": ["bio_textbook_001", "bio_notes_002"],
    "created_at": "2026-01-17T10:30:00Z"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Error Cases:**
- `404`: Group not found

---

#### `POST /api/v1/groups/{group_id}/upload`

Upload a PDF resource to a study group. The PDF is automatically ingested and made available to all group members.

**Content-Type:** `multipart/form-data`

**Parameters:**
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `group_id` | string | path | Yes | Group identifier |
| `file` | file | body | Yes | PDF file to upload |
| `uploaded_by` | string | body | Yes | User ID uploading the file |
| `title` | string | body | No | Optional resource title |

**Example (JavaScript/Fetch):**
```javascript
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('uploaded_by', 'user_123');
formData.append('title', 'Chapter 5 - Photosynthesis');

const response = await fetch('/api/v1/groups/grp_abc123/upload', {
  method: 'POST',
  body: formData
});
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/groups/grp_abc123/upload \
  -F "file=@biology_chapter5.pdf" \
  -F "uploaded_by=user_123" \
  -F "title=Chapter 5 - Photosynthesis"
```

**Response:**
```json
{
  "success": true,
  "message": "Resource uploaded and indexed successfully",
  "data": {
    "pdf_source_id": "grp_abc123_8a7b3c1d",
    "title": "Chapter 5 - Photosynthesis",
    "group_id": "grp_abc123",
    "uploaded_by": "user_123",
    "ingestion_result": {
      "num_documents": 12,
      "num_propositions": 156,
      "processing_time": "8.5s"
    }
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**What Happens:**
1. File is uploaded and temporarily stored
2. PDF is ingested using the ingestion pipeline
3. Documents are indexed in ChromaDB
4. Resource is linked to the group
5. All group members can now use `pdf_source_id` for quizzes

**Error Cases:**
- `404`: Group not found
- `403`: Only group members can upload
- `400`: Invalid file type (only PDFs allowed)
- `413`: File too large (max 50MB)

**Use Cases:**
- Share textbook chapters
- Upload class notes
- Provide study materials
- Create shared resource library

---

#### `GET /api/v1/groups/{group_id}/resources`

List all resources uploaded to a study group.

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| `group_id` | string | path | Group identifier |

**Response:**
```json
{
  "success": true,
  "data": {
    "resources": [
      {
        "pdf_source_id": "grp_abc123_8a7b3c1d",
        "title": "Chapter 5 - Photosynthesis",
        "uploaded_by": "user_123",
        "uploaded_at": "2026-01-17T10:30:00Z"
      },
      {
        "pdf_source_id": "grp_abc123_9b8c4d2e",
        "title": "Cellular Respiration Notes",
        "uploaded_by": "user_456",
        "uploaded_at": "2026-01-17T11:45:00Z"
      }
    ],
    "total": 2
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

**Using Resources:**
After uploading, any group member can use the `pdf_source_id` to:
- Generate quizzes
- Create flash notes
- Ask doubt solver questions

**Example - Generate Quiz from Group Resource:**
```json
POST /api/v1/sessions/adaptive
{
  "user_id": "user_456",
  "source_id": "grp_abc123_8a7b3c1d",
  "topic": "photosynthesis",
  "initial_difficulty": "MEDIUM"
}
```

**Error Cases:**
- `404`: Group not found

---

### Study Groups - Complete Workflow Example

**1. User A creates a group:**
```bash
POST /api/v1/groups/create
{
  "name": "AP Biology Study Partners",
  "creator_id": "alice_123"
}
# Response: group_id = "grp_bio001"
```

**2. User B joins the group:**
```bash
POST /api/v1/groups/join
{
  "group_id": "grp_bio001",
  "user_id": "bob_456"
}
```

**3. User A uploads a textbook chapter:**
```bash
POST /api/v1/groups/grp_bio001/upload
- file: biology_ch5.pdf
- uploaded_by: alice_123
- title: "Chapter 5 - Photosynthesis"
# Response: pdf_source_id = "grp_bio001_abc123"
```

**4. User B generates a quiz from the shared resource:**
```bash
POST /api/v1/sessions/adaptive
{
  "user_id": "bob_456",
  "source_id": "grp_bio001_abc123",
  "topic": "default",
  "initial_difficulty": "MEDIUM"
}
# Response: session_id = "sess_xyz789"
```

**5. Generate quiz questions:**
```bash
POST /api/v1/sessions/sess_xyz789/quiz
{
  "num_questions": 5
}
# Both users can now study from the same material!
```

**6. View all group resources:**
```bash
GET /api/v1/groups/grp_bio001/resources
# Shows all PDFs uploaded by group members
```

---

## Request/Response Formats

### Standard Response Wrapper

All responses follow this structure:

```typescript
interface APIResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  timestamp: string;  // ISO 8601 format
}
```

### Content Types

| Endpoint Type | Content-Type |
|---------------|--------------|
| JSON endpoints | `application/json` |
| File upload | `multipart/form-data` |

---

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 413 | Payload Too Large - File exceeds 50MB |
| 422 | Validation Error - Invalid request format |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "success": false,
  "message": "Validation error",
  "error": "Invalid request data",
  "details": [
    {
      "field": "url",
      "message": "Must be a valid YouTube URL",
      "type": "value_error"
    }
  ],
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

---

## Frontend Integration Guide

### CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)
- `http://127.0.0.1:3000`

To add more origins, set the `CORS_ORIGINS` environment variable:
```env
CORS_ORIGINS=http://localhost:3000,http://your-frontend.com
```

### React Integration Example

#### 1. Create an API Client

```typescript
// src/api/client.ts
const API_BASE = 'http://localhost:8000/api/v1';

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || data.message);
  }
  
  return data.data;
}

export const api = {
  // Materials
  getMaterials: () => apiRequest<{sources: string[], count: number}>('/materials'),
  
  // Ingestion
  uploadPDF: async (file: File, sourceId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (sourceId) formData.append('source_id', sourceId);
    
    const response = await fetch(`${API_BASE}/ingest/pdf`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },
  
  ingestYouTube: (url: string, sourceId?: string) =>
    apiRequest('/ingest/youtube', {
      method: 'POST',
      body: JSON.stringify({ url, source_id: sourceId }),
    }),
  
  // Sessions
  createAdaptiveSession: (userId: string, sourceId: string, topic = 'default') =>
    apiRequest('/sessions/adaptive', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        source_id: sourceId,
        topic,
        initial_difficulty: 'EASY',
      }),
    }),
  
  // Quiz
  generateQuiz: (sessionId: string, numQuestions = 5) =>
    apiRequest(`/sessions/${sessionId}/quiz`, {
      method: 'POST',
      body: JSON.stringify({ num_questions: numQuestions }),
    }),
  
  submitAnswers: (sessionId: string, answers: boolean[]) =>
    apiRequest(`/sessions/${sessionId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    }),
  
  // Flash-Notes (NEW)
  getCheatSheet: (topic: string, sourceId?: string, numFacts = 20) => {
    const params = new URLSearchParams({ topic, num_facts: numFacts.toString() });
    if (sourceId) params.append('source_id', sourceId);
    return apiRequest(`/cheat-sheet?${params}`);
  },
  
  getCheatSheetBySource: (sourceId: string, numFacts = 30) =>
    apiRequest(`/cheat-sheet/by-source/${sourceId}?num_facts=${numFacts}`),
  
  // Doubt Solver
  solveDoubt: (question: string, sourceId: string, sessionId?: string) =>
    apiRequest('/solve-doubt', {
      method: 'POST',
      body: JSON.stringify({
        question,
        pdf_source_id: sourceId,
        session_id: sessionId,
      }),
    }),
  
  getDoubtSources: () => apiRequest('/solve-doubt/sources'),
  
  // Smart Learning (NEW)
  generateSocraticHint: (question: string, correctAnswer: string, studentAnswer?: string) =>
    apiRequest('/hint/socratic', {
      method: 'POST',
      body: JSON.stringify({
        question,
        correct_answer: correctAnswer,
        student_answer: studentAnswer,
      }),
    }),
  
  analyzeSession: (results: Array<{
    question: string;
    is_correct: boolean;
    user_answer: string;
    correct_answer: string;
  }>) =>
    apiRequest('/analyze-session', {
      method: 'POST',
      body: JSON.stringify({ results }),
    }),
};
```

#### 2. File Upload Component (Drag & Drop)

```tsx
// src/components/FileUpload.tsx
import { useState, useCallback } from 'react';
import { api } from '../api/client';

export function FileUpload({ onSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (!file || !file.name.endsWith('.pdf')) {
      alert('Please upload a PDF file');
      return;
    }
    
    setUploading(true);
    try {
      const result = await api.uploadPDF(file);
      onSuccess(result);
    } catch (error) {
      alert(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  }, [onSuccess]);

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      style={{
        border: `2px dashed ${isDragging ? '#4CAF50' : '#ccc'}`,
        padding: '40px',
        textAlign: 'center',
        borderRadius: '8px',
      }}
    >
      {uploading ? (
        <p>Uploading...</p>
      ) : (
        <p>Drag & drop a PDF here, or click to select</p>
      )}
    </div>
  );
}
```

#### 3. Quiz Component

```tsx
// src/components/Quiz.tsx
import { useState } from 'react';
import { api } from '../api/client';

interface Question {
  question: string;
  options: string[];
  correct_answer: string;
}

export function Quiz({ sessionId }) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<(number | null)[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const loadQuiz = async () => {
    const data = await api.generateQuiz(sessionId);
    setQuestions(data.questions);
    setAnswers(new Array(data.questions.length).fill(null));
    setSubmitted(false);
    setFeedback(null);
  };

  const handleSubmit = async () => {
    // Convert selected indices to boolean (correct/incorrect)
    const results = questions.map((q, i) => {
      const selectedOption = q.options[answers[i]];
      return selectedOption?.includes(q.correct_answer) || false;
    });
    
    const response = await api.submitAnswers(sessionId, results);
    setFeedback(response);
    setSubmitted(true);
  };

  return (
    <div>
      <button onClick={loadQuiz}>Generate Quiz</button>
      
      {questions.map((q, qIndex) => (
        <div key={qIndex}>
          <h3>{q.question}</h3>
          {q.options.map((option, oIndex) => (
            <label key={oIndex}>
              <input
                type="radio"
                name={`q${qIndex}`}
                checked={answers[qIndex] === oIndex}
                onChange={() => {
                  const newAnswers = [...answers];
                  newAnswers[qIndex] = oIndex;
                  setAnswers(newAnswers);
                }}
                disabled={submitted}
              />
              {option}
            </label>
          ))}
        </div>
      ))}
      
      {questions.length > 0 && !submitted && (
        <button onClick={handleSubmit}>Submit Answers</button>
      )}
      
      {feedback && (
        <div>
          <h3>Results</h3>
          <p>Score: {feedback.score_percentage}%</p>
          <p>{feedback.feedback_message}</p>
        </div>
      )}
    </div>
  );
}
```

### Vue.js Integration

```javascript
// src/api/rooster.js
import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

export default {
  getMaterials: () => client.get('/materials'),
  
  uploadPDF: (file, sourceId) => {
    const formData = new FormData();
    formData.append('file', file);
    if (sourceId) formData.append('source_id', sourceId);
    return client.post('/ingest/pdf', formData);
  },
  
  createSession: (userId, sourceId, topic = 'default') =>
    client.post('/sessions/adaptive', {
      user_id: userId,
      source_id: sourceId,
      topic,
    }),
  
  getQuiz: (sessionId, numQuestions = 5) =>
    client.post(`/sessions/${sessionId}/quiz`, { num_questions: numQuestions }),
  
  submitAnswers: (sessionId, answers) =>
    client.post(`/sessions/${sessionId}/submit`, { answers }),
  
  // Flash-Notes (NEW)
  getCheatSheet: (topic, sourceId, numFacts = 20) => {
    const params = { topic, num_facts: numFacts };
    if (sourceId) params.source_id = sourceId;
    return client.get('/cheat-sheet', { params });
  },
  
  getCheatSheetBySource: (sourceId, numFacts = 30) =>
    client.get(`/cheat-sheet/by-source/${sourceId}`, { params: { num_facts: numFacts } }),
  
  // Doubt Solver
  solveDoubt: (question, sourceId, sessionId) =>
    client.post('/solve-doubt', {
      question,
      pdf_source_id: sourceId,
      session_id: sessionId,
    }),
  
  getDoubtSources: () => client.get('/solve-doubt/sources'),
  
  // Smart Learning (NEW)
  generateSocraticHint: (question, correctAnswer, studentAnswer) =>
    client.post('/hint/socratic', {
      question,
      correct_answer: correctAnswer,
      student_answer: studentAnswer,
    }),
  
  analyzeSession: (results) =>
    client.post('/analyze-session', { results }),
};
  
  getQuiz: (sessionId, numQuestions = 5) =>
    client.post(`/sessions/${sessionId}/quiz`, { num_questions: numQuestions }),
  
  submitAnswers: (sessionId, answers) =>
    client.post(`/sessions/${sessionId}/submit`, { answers }),
};
```

---

## Code Examples

### cURL Examples

```bash
# List materials
curl http://localhost:8000/api/v1/materials

# Upload PDF
curl -X POST http://localhost:8000/api/v1/ingest/pdf \
  -F "file=@./document.pdf" \
  -F "source_id=my_doc"

# Ingest YouTube
curl -X POST http://localhost:8000/api/v1/ingest/youtube \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=abc123"}'

# Create session
curl -X POST http://localhost:8000/api/v1/sessions/adaptive \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "source_id": "my_doc", "topic": "default"}'

# Generate quiz
curl -X POST http://localhost:8000/api/v1/sessions/SESSION_ID/quiz \
  -H "Content-Type: application/json" \
  -d '{"num_questions": 5}'

# Submit answers
curl -X POST http://localhost:8000/api/v1/sessions/SESSION_ID/submit \
  -H "Content-Type: application/json" \
  -d '{"answers": [true, false, true, true, false]}'

# Generate cheat sheet (NEW)
curl "http://localhost:8000/api/v1/cheat-sheet?topic=Neural%20Networks&num_facts=20"

# Generate cheat sheet by source (NEW)
curl "http://localhost:8000/api/v1/cheat-sheet/by-source/my_doc?num_facts=25"

# Solve a doubt (NEW)
curl -X POST http://localhost:8000/api/v1/solve-doubt \
  -H "Content-Type: application/json" \
  -d '{"question": "What is photosynthesis?", "pdf_source_id": "biology_textbook"}'

# List sources for doubt solving (NEW)
curl http://localhost:8000/api/v1/solve-doubt/sources
```

### Python Examples

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# Upload PDF
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"{API_BASE}/ingest/pdf",
        files={"file": f},
        data={"source_id": "my_doc"}
    )
    print(response.json())

# Create session and take quiz
session = requests.post(
    f"{API_BASE}/sessions/adaptive",
    json={
        "user_id": "user1",
        "source_id": "my_doc",
        "topic": "default"
    }
).json()

session_id = session["data"]["session_id"]

# Generate quiz
quiz = requests.post(
    f"{API_BASE}/sessions/{session_id}/quiz",
    json={"num_questions": 5}
).json()

# ... answer questions ...

# Submit results
result = requests.post(
    f"{API_BASE}/sessions/{session_id}/submit",
    json={"answers": [True, False, True, True, False]}
).json()

print(f"Score: {result['data']['score_percentage']}%")

# Generate cheat sheet (NEW)
cheat_sheet = requests.get(
    f"{API_BASE}/cheat-sheet",
    params={"topic": "Machine Learning", "num_facts": 25}
).json()

print(f"Cheat Sheet ({cheat_sheet['data']['fact_count']} facts):")
for fact in cheat_sheet['data']['cheat_sheet']:
    print(fact)

# Solve a doubt (NEW)
doubt = requests.post(
    f"{API_BASE}/solve-doubt",
    json={
        "question": "What is photosynthesis?",
        "pdf_source_id": "biology_textbook"
    }
).json()

print(f"Question: {doubt['data']['question']}")
print(f"Answer: {doubt['data']['answer']}")
```

---

## Troubleshooting

### Server Won't Start

**Error:** `ModuleNotFoundError: No module named 'api'`

**Solution:** Make sure you're running from the `backend` directory:
```bash
cd backend
python run_api.py
```

### CORS Errors

**Error:** `Access to fetch blocked by CORS policy`

**Solution:** Add your frontend origin to the `.env` file:
```env
CORS_ORIGINS=http://localhost:3000,http://your-frontend-url.com
```

### File Upload Fails

**Error:** `413 Payload Too Large`

**Solution:** The default limit is 50MB. For larger files, modify `MAX_FILE_SIZE_MB` in `.env`.

### No Materials Found

**Error:** `"sources": []` returned from `/materials`

**Solution:** Upload some content first using the ingestion endpoints.

### Quiz Generation Fails

**Error:** `"Failed to generate quiz. No context available."`

**Solutions:**
1. Ensure the `source_id` exists (check `/materials`)
2. Try using `"topic": "default"` to quiz from entire document
3. Check that the source has indexed documents

### YouTube Ingestion Fails

**Error:** `"Failed to fetch YouTube transcript"`

**Solutions:**
1. Ensure the video has captions enabled
2. Some videos are region-restricted
3. Age-restricted videos may not work

---

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DEBUG=false
API_PORT=8000
API_HOST=0.0.0.0
MAX_FILE_SIZE_MB=50
```

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the interactive docs at `/docs`
3. Check server logs for detailed error messages

---

*Last updated: January 17, 2026*
