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
| **Flash-Note Generator** | ⚡ **NEW**: Instant cheat sheets with zero LLM cost |
| **Progress Tracking** | Submit answers and track mastery scores |

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
