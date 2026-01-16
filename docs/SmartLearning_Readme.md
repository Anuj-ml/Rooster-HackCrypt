# Smart Learning Features 🧠

## Overview

The Smart Learning module provides advanced pedagogical techniques to enhance student learning through:

1. **Socratic Hints** - Guiding questions that promote critical thinking
2. **AI Sensei** - Personalized session analysis and learning recommendations

Both features leverage AI to create an adaptive, student-centered learning experience.

---

## Features

### 1. Socratic Hints 💡

**What it does:**
- Generates guiding questions instead of revealing answers directly
- Applies the Socratic Method to promote active learning
- Keeps hints under 20 words for conciseness

**When to use:**
- Student gets a quiz question wrong
- Student needs help without spoiling the answer
- Encouraging independent problem-solving

**How it works:**
1. Accepts: question, correct answer, and optionally the student's wrong answer
2. Analyzes the gap between student understanding and correct answer
3. Generates a carefully crafted guiding question
4. Returns hint that nudges thinking in the right direction

**Example:**

```json
// Request
{
  "question": "What is the capital of France?",
  "correct_answer": "Paris",
  "student_answer": "London"
}

// Response
{
  "success": true,
  "data": {
    "hint": "Which city is home to the Eiffel Tower?"
  },
  "message": "Hint generated successfully"
}
```

**Educational Benefits:**
- Promotes deeper understanding vs. memorization
- Builds problem-solving skills
- Increases retention through active recall
- Maintains student engagement

---

### 2. AI Sensei (Session Analyzer) 📊

**What it does:**
- Analyzes complete quiz session performance
- Identifies patterns in correct/incorrect answers
- Provides actionable feedback in 2-3 sentences
- Highlights key concepts that need reinforcement

**When to use:**
- After completing a quiz session
- When reviewing student progress
- To identify knowledge gaps
- For personalized study recommendations

**How it works:**
1. Accepts array of quiz results (question, correctness, answers)
2. Analyzes performance patterns across all questions
3. Identifies core concepts from incorrect answers
4. Generates concise, actionable recommendations
5. Optimized: Skips LLM call if all answers are correct

**Example:**

```json
// Request
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

// Response
{
  "success": true,
  "data": {
    "analysis": "You have a foundational understanding of cellular biology but need to strengthen your grasp of photosynthesis mechanics. Review the inputs (light, water, CO₂) and outputs (glucose, oxygen) of photosynthesis, focusing on the light-dependent and light-independent reactions. Practice distinguishing between cellular respiration and photosynthesis to solidify these core concepts."
  },
  "message": "Session analyzed successfully"
}
```

**Analysis Features:**
- **Pattern Recognition**: Identifies common misconceptions across multiple questions
- **Concept Extraction**: Pinpoints specific topics needing review
- **Actionable Advice**: Provides clear next steps for improvement
- **Positive Reinforcement**: Acknowledges strengths while addressing weaknesses
- **Performance Optimization**: Returns congratulations message instantly for perfect scores

---

## API Endpoints

### Generate Socratic Hint

**Endpoint:** `POST /api/v1/hint/socratic`

**Request Body:**
```json
{
  "question": "string (required)",
  "correct_answer": "string (required)",
  "student_answer": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "hint": "string (guiding question)"
  },
  "message": "string"
}
```

---

### Analyze Quiz Session

**Endpoint:** `POST /api/v1/analyze-session`

**Request Body:**
```json
{
  "results": [
    {
      "question": "string",
      "is_correct": true,
      "user_answer": "string",
      "correct_answer": "string"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis": "string (2-3 sentences)"
  },
  "message": "string"
}
```

---

## Architecture

### Service Classes

**SocraticTutor** (`backend/src/features/smart_learning.py`)
- **Purpose**: Generate guiding questions using Socratic method
- **Method**: `generate_hint(question, correct_answer, student_answer)`
- **LLM Prompt**: Instructs model to create brief guiding questions
- **Output**: Single question under 20 words

**SessionAnalyzer** (`backend/src/features/smart_learning.py`)
- **Purpose**: Analyze quiz performance and provide feedback
- **Method**: `analyze_session(results)`
- **Optimization**: Bypasses LLM for perfect scores
- **LLM Prompt**: Instructs model to identify patterns and provide 2-3 sentence feedback
- **Output**: Concise analysis with actionable recommendations

### Schemas

**HintRequest** (`backend/src/models/schemas.py`)
```python
class HintRequest(BaseModel):
    question: str
    correct_answer: str
    student_answer: Optional[str] = None
```

**QuizResultItem** (`backend/src/models/schemas.py`)
```python
class QuizResultItem(BaseModel):
    question: str
    is_correct: bool
    user_answer: str
    correct_answer: str
```

**AnalysisRequest** (`backend/src/models/schemas.py`)
```python
class AnalysisRequest(BaseModel):
    results: List[QuizResultItem]
```

---

## Integration Guide

### Using Socratic Hints

```python
import requests

# After a student gets a question wrong
response = requests.post(
    "http://localhost:8000/api/v1/hint/socratic",
    json={
        "question": "What is the derivative of x²?",
        "correct_answer": "2x",
        "student_answer": "x"
    }
)

hint = response.json()["data"]["hint"]
print(f"Hint: {hint}")
# Output: "What happens when you multiply the exponent by the coefficient?"
```

### Using Session Analysis

```python
import requests

# After completing a quiz
quiz_results = [
    {
        "question": "What is 2 + 2?",
        "is_correct": True,
        "user_answer": "4",
        "correct_answer": "4"
    },
    {
        "question": "What is 5 × 7?",
        "is_correct": False,
        "user_answer": "30",
        "correct_answer": "35"
    }
]

response = requests.post(
    "http://localhost:8000/api/v1/analyze-session",
    json={"results": quiz_results}
)

analysis = response.json()["data"]["analysis"]
print(f"Feedback: {analysis}")
```

---

## Comparison with Other Features

| Feature | Purpose | Output Type | Best For |
|---------|---------|-------------|----------|
| **Flash Notes** | Zero-cost fact retrieval | Concise answers | Quick information lookup |
| **Doubt Solver** | ELI5 explanations | Simplified explanations | Understanding complex concepts |
| **Socratic Hints** | Guided discovery | Guiding questions | Active problem-solving |
| **AI Sensei** | Performance analysis | Session feedback | Progress tracking & study planning |

---

## Best Practices

### For Socratic Hints:
- Provide student's wrong answer when available for better context
- Use after first incorrect attempt, not immediately
- Combine with time limits to encourage thinking before revealing
- Track which hints are most effective for future optimization

### For Session Analysis:
- Submit complete quiz sessions, not individual questions
- Use analysis to guide next study session topics
- Combine with spaced repetition for maximum retention
- Re-analyze after remedial study to track improvement

---

## Technical Notes

### Performance
- **Socratic Hints**: ~1-2 seconds per request (LLM-dependent)
- **Session Analysis**: 
  - 0 incorrect: Instant (no LLM call)
  - 1+ incorrect: ~2-3 seconds (LLM-dependent)

### Singleton Pattern
Both service classes use singleton instances to avoid re-initialization overhead.

### Error Handling
- Validates all input data with Pydantic schemas
- Returns standardized APIResponse format
- Handles LLM failures gracefully with error messages

---

## Future Enhancements

- **Multi-language support**: Hints and analysis in different languages
- **Difficulty adaptation**: Adjust hint specificity based on student level
- **Historical tracking**: Compare current session with past performance
- **Concept mapping**: Visual representation of knowledge gaps
- **Collaborative learning**: Group session analysis

---

## References

- **Socratic Method**: Ancient Greek pedagogical technique using questions to stimulate critical thinking
- **Formative Assessment**: Using analysis to inform teaching/learning strategies
- **Metacognition**: Helping students understand their own learning process

---

For API implementation details, see [API_README.md](../API_README.md)
For complete feature list, see [README.md](../README.md)
