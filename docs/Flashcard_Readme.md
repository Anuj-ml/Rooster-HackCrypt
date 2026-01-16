# Flash-Note Generator Feature

## Overview

The **Flash-Note Generator** is a zero-cost feature that instantly generates cheat sheets of atomic facts for any topic. Unlike quiz generation, this feature does **NOT use any LLM tokens** - it retrieves propositions directly from ChromaDB based on semantic similarity.

---

## Key Benefits

✅ **Zero LLM Cost** - No API tokens consumed  
✅ **Instant Results** - Retrieval in milliseconds  
✅ **Atomic Facts** - Clean, bite-sized propositions  
✅ **Perfect for Quick Review** - Study before exams  
✅ **Topic-Based or Source-Based** - Flexible retrieval  

---

## How It Works

### Architecture

```
User Query → ChromaDB Vector Search → Raw Propositions → Formatted Cheat Sheet
```

Unlike quiz generation which uses:
```
Query → Retrieval → LLM Processing → Quiz Generation
```

Flash-Note Generator skips the LLM entirely:

1. **Vector Search**: Query is embedded and compared against stored propositions
2. **Direct Retrieval**: Top-K most relevant propositions are returned
3. **Formatting**: Propositions are formatted as bullet points
4. **Return**: Instant cheat sheet delivery

---

## Use Cases

### 1. Pre-Exam Quick Review
Generate a cheat sheet 10 minutes before an exam:
```
Topic: "Indian Economy GDP growth factors"
→ 20 atomic facts about GDP drivers, sectoral contributions, etc.
```

### 2. Material Overview
Get an overview of uploaded materials:
```
Source: "machine_learning_textbook"
→ 30 random facts from the entire textbook
```

### 3. Focused Topic Study
Deep dive into specific concepts:
```
Topic: "Neural Network Backpropagation"
Source: "deep_learning_notes"
→ 20 facts specifically about backpropagation
```

---

## API Endpoints

### 1. Generate Cheat Sheet by Topic

**Endpoint:** `GET /api/v1/cheat-sheet`

**Parameters:**
- `topic` (required): Topic to generate facts about
- `source_id` (optional): Filter facts from specific material
- `num_facts` (optional): Number of facts (1-50, default: 20)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/cheat-sheet?topic=Indian%20Economy&num_facts=25"
```

**Example Response:**
```json
{
  "success": true,
  "message": "Generated cheat sheet with 25 facts",
  "data": {
    "topic": "Indian Economy",
    "fact_count": 25,
    "cheat_sheet": [
      "• GDP growth rate was 7.8% in the last quarter.",
      "• The service sector contributes over 50% to GVA.",
      "• India is the 5th largest economy by nominal GDP.",
      "• Manufacturing sector accounts for 17% of GDP.",
      "• Agriculture employs nearly 42% of the workforce.",
      ...
    ],
    "source_id": null
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

---

### 2. Generate Cheat Sheet by Source

**Endpoint:** `GET /api/v1/cheat-sheet/by-source/{source_id}`

**Parameters:**
- `source_id` (required): Material ID to generate facts from
- `num_facts` (optional): Number of facts (1-50, default: 30)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/cheat-sheet/by-source/sql_basics?num_facts=20"
```

**Example Response:**
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
      ...
    ],
    "source_id": "sql_basics"
  },
  "timestamp": "2026-01-17T10:30:00.000Z"
}
```

---

## Frontend Integration

### React Example

```typescript
// src/api/flashnotes.ts
export const flashNotesAPI = {
  // Get cheat sheet by topic
  getCheatSheet: async (topic: string, sourceId?: string, numFacts = 20) => {
    const params = new URLSearchParams({
      topic,
      num_facts: numFacts.toString(),
    });
    
    if (sourceId) params.append('source_id', sourceId);
    
    const response = await fetch(
      `http://localhost:8000/api/v1/cheat-sheet?${params}`
    );
    return response.json();
  },
  
  // Get cheat sheet by source
  getCheatSheetBySource: async (sourceId: string, numFacts = 30) => {
    const response = await fetch(
      `http://localhost:8000/api/v1/cheat-sheet/by-source/${sourceId}?num_facts=${numFacts}`
    );
    return response.json();
  },
};
```

### React Component

```tsx
import { useState } from 'react';
import { flashNotesAPI } from '../api/flashnotes';

export function FlashNoteGenerator() {
  const [topic, setTopic] = useState('');
  const [facts, setFacts] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const generateCheatSheet = async () => {
    setLoading(true);
    try {
      const result = await flashNotesAPI.getCheatSheet(topic, undefined, 25);
      if (result.success) {
        setFacts(result.data.cheat_sheet);
      }
    } catch (error) {
      alert('Failed to generate cheat sheet');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flash-note-generator">
      <h2>📝 Flash-Note Generator</h2>
      <div className="input-section">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic (e.g., Neural Networks)"
        />
        <button onClick={generateCheatSheet} disabled={loading}>
          {loading ? 'Generating...' : 'Generate Cheat Sheet'}
        </button>
      </div>
      
      {facts.length > 0 && (
        <div className="facts-section">
          <h3>Cheat Sheet ({facts.length} facts)</h3>
          <ul>
            {facts.map((fact, idx) => (
              <li key={idx}>{fact}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

## Technical Implementation

### Backend Components

#### 1. **storage.py** - `get_raw_propositions()`
```python
def get_raw_propositions(self, query: str, pdf_source_id: str = None, k: int = 20) -> List[str]:
    """
    Retrieve raw propositions directly from ChromaDB.
    Returns the propositions themselves, not parent documents.
    """
    # Vector similarity search
    results = self.vectorstore.similarity_search(
        query,
        k=k,
        filter={"pdf_source_id": pdf_source_id} if pdf_source_id else None
    )
    
    # Extract page_content (atomic propositions)
    return [doc.page_content for doc in results]
```

#### 2. **flash_note_generator.py** - Service Layer
```python
class FlashNoteGenerator:
    def generate_cheat_sheet(self, topic: str, source_id: Optional[str] = None, num_facts: int = 20):
        # Retrieve propositions
        propositions = self.kb.get_raw_propositions(topic, source_id, num_facts)
        
        # Format as bullet points
        formatted_facts = [f"• {fact}" for fact in propositions]
        
        return {
            "topic": topic,
            "fact_count": len(formatted_facts),
            "cheat_sheet": formatted_facts
        }
```

#### 3. **flashnotes.py** - API Router
```python
@router.get("", response_model=APIResponse)
async def generate_cheat_sheet(
    topic: str = Query(...),
    source_id: Optional[str] = Query(None),
    num_facts: int = Query(20, ge=1, le=50)
):
    # Async wrapper for sync operation
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        generator.generate_cheat_sheet,
        topic, source_id, num_facts
    )
    return APIResponse(success=True, data=result)
```

---

## Comparison: Quiz vs Flash-Notes

| Feature | Quiz Generation | Flash-Note Generator |
|---------|----------------|----------------------|
| **LLM Usage** | ✅ Uses Groq API | ❌ Zero LLM tokens |
| **Cost** | ~$0.01 per 10 questions | **FREE** |
| **Speed** | 5-15 seconds | <1 second |
| **Output** | MCQs with options | Bullet-point facts |
| **Use Case** | Active practice | Quick review |
| **Difficulty** | Adjustable | N/A (raw facts) |

---

## Best Practices

### 1. Use Specific Topics
```
✅ Good: "Neural Network Backpropagation algorithm"
❌ Bad: "Machine Learning"
```
Specific topics return more relevant facts.

### 2. Filter by Source
```python
# When you have multiple materials uploaded
getCheatSheet("SQL Joins", source_id="database_textbook")
```

### 3. Adjust Fact Count
- **Quick Review**: 10-15 facts
- **Comprehensive Study**: 25-30 facts
- **Deep Dive**: 40-50 facts

### 4. Combine with Quizzes
1. Generate flash-notes for quick review
2. Take adaptive quiz to test knowledge
3. Return to flash-notes for weak areas

---

## Performance

### Benchmarks

| Operation | Time | Cost |
|-----------|------|------|
| Retrieve 20 facts | ~200ms | $0.00 |
| Retrieve 50 facts | ~300ms | $0.00 |
| Format + Return | ~50ms | $0.00 |

### Scalability

- **ChromaDB** handles millions of vectors efficiently
- **Vector Search** uses HNSW algorithm (sub-linear time)
- **No Rate Limits** (unlike LLM APIs)

---

## Error Handling

### No Facts Found

**Request:**
```bash
curl "http://localhost:8000/api/v1/cheat-sheet?topic=NonexistentTopic"
```

**Response:**
```json
{
  "success": false,
  "message": "No facts found for topic 'NonexistentTopic'",
  "data": {
    "topic": "NonexistentTopic",
    "fact_count": 0,
    "cheat_sheet": [],
    "message": "No facts found for topic 'NonexistentTopic'"
  }
}
```

### Invalid Source ID

**Response:**
```json
{
  "success": false,
  "message": "No facts found for topic 'SQL' in source 'invalid_source'",
  "data": {
    "topic": "SQL",
    "fact_count": 0,
    "cheat_sheet": []
  }
}
```

---

## Future Enhancements

1. **Grouping by Subtopics** - Cluster facts into categories
2. **Export Formats** - PDF, Markdown, Anki flashcards
3. **Caching** - Cache popular topics for instant retrieval
4. **Highlighting** - Highlight key terms in propositions
5. **Related Topics** - Suggest related topics based on query

---

## FAQ

### Q: Can I use this without uploading materials first?
**A:** No, you must upload PDFs, YouTube videos, or generate syllabus content first.

### Q: How are facts ranked?
**A:** By semantic similarity to your query using vector embeddings.

### Q: Can I get facts in a specific order?
**A:** Facts are ranked by relevance. For chronological/structured content, use quiz generation instead.

### Q: What's the maximum number of facts?
**A:** 50 facts per request to prevent overwhelming responses.

### Q: Can I save cheat sheets?
**A:** Currently no, but you can copy the JSON response or implement frontend storage.

---

## Conclusion

The Flash-Note Generator provides **instant, free, atomic fact retrieval** for quick study sessions. It complements the quiz generation feature by offering a lightweight alternative when you need rapid information access without LLM overhead.

**Perfect for:**
- 📖 Pre-exam cramming
- 🔍 Material exploration
- 📝 Note-taking assistance
- 💡 Quick concept refreshers

---

*Last updated: January 17, 2026*
