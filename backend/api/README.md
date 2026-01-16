# Rooster-HackCrypt FastAPI Backend

## Quick Start

```bash
# From backend directory
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the API server
python -m api.main
# OR
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Endpoints Overview

### Health
- `GET /api/health` - Full health check
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/live` - Liveness probe

### Materials
- `GET /api/v1/materials` - List all indexed sources
- `GET /api/v1/materials/{source_id}` - Get source details

### Ingestion
- `POST /api/v1/ingest/pdf` - Upload PDF (multipart/form-data)
- `POST /api/v1/ingest/youtube` - Ingest YouTube transcript
- `POST /api/v1/ingest/syllabus` - Generate syllabus content

### Sessions & Quizzes
- `POST /api/v1/sessions/adaptive` - Create adaptive session
- `POST /api/v1/sessions/grind` - Create grind session
- `GET /api/v1/sessions` - List active sessions
- `GET /api/v1/sessions/{id}` - Get session stats
- `DELETE /api/v1/sessions/{id}` - Delete session
- `POST /api/v1/sessions/{id}/quiz` - Generate quiz
- `POST /api/v1/sessions/{id}/submit` - Submit answers

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DEBUG=true
API_PORT=8000
```

## File Structure

```
api/
├── main.py              # FastAPI app entry point
├── config.py            # Settings management
├── dependencies.py      # Dependency injection
├── models/
│   ├── requests.py      # Request validation models
│   └── responses.py     # Response models
├── routers/
│   ├── health.py        # Health check endpoints
│   ├── materials.py     # Material management
│   ├── ingestion.py     # Document ingestion
│   └── quiz.py          # Sessions and quizzes
├── services/
│   ├── file_handler.py  # Temp file management
│   └── orchestrator.py  # Backend service wrappers
├── middleware/
│   └── error_handler.py # Global error handling
└── temp_uploads/        # Temporary file storage (auto-created)
```
