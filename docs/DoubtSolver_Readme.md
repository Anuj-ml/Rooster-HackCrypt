# Doubt Solver Feature

## Overview

The **Doubt Solver** is an AI-powered tutoring feature that provides ELI5 (Explain Like I'm 5) explanations for student questions. Unlike typical chatbots, this feature is **strictly grounded in your uploaded study material** and uses simple, conversational language with real-world analogies.

---

## Key Benefits

✅ **ELI5 Explanations** - Simplifies complex concepts  
✅ **Grounded Answers** - Only uses your uploaded materials  
✅ **Real-World Analogies** - Makes abstract ideas relatable  
✅ **Conversational Tone** - Friendly and encouraging  
✅ **No Hallucinations** - Won't make up information  

---

## How It Works

### Architecture

```
Student Question → ChromaDB Search → Relevant Context → LLM (ELI5 Prompt) → Simplified Answer
```

The system uses LangGraph to orchestrate a two-step workflow:

1. **Retrieval Node**: Searches for relevant content in your uploaded materials
2. **Explanation Node**: Generates a simplified, conversational answer

### Example Flow

**Student asks:**
> "What is backpropagation in neural networks?"

**System:**
1. 🔍 Searches `neural_networks_textbook` for relevant passages
2. 📚 Retrieves 5 most relevant document chunks
3. 🧠 LLM generates ELI5 explanation with analogies
4. ✨ Returns: *"Backpropagation is like learning from mistakes. Imagine you're playing darts..."*

---

## Use Cases

### 1. Quick Concept Clarification
**Before exam:**
```
Question: "What's the difference between supervised and unsupervised learning?"
Answer: "Think of it like learning with or without a teacher..."
```

### 2. Breaking Down Complex Ideas
**During study session:**
```
Question: "How does gradient descent work?"
Answer: "Imagine you're hiking down a foggy mountain and can only see your immediate surroundings..."
```

### 3. Real-World Connections
**Applying theory:**
```
Question: "Why do we need activation functions?"
Answer: "Without activation functions, neural networks would be like a fancy calculator that can only do addition..."
```

---

## API Endpoint

### POST `/api/v1/solve-doubt`

**Request Body:**
```json
{
  "question": "What is photosynthesis?",
  "pdf_source_id": "biology_textbook",
  "session_id": "optional-uuid"
}
```

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

### GET `/api/v1/solve-doubt/sources`

List all available materials for doubt solving.

**Response:**
```json
{
  "success": true,
  "message": "Found 3 available materials",
  "data": {
    "sources": ["biology_textbook", "chemistry_notes", "physics_lecture"],
    "count": 3
  }
}
```

---

## Frontend Integration

### React Example

```typescript
// src/api/doubtSolver.ts
export const doubtSolverAPI = {
  solveDoubt: async (question: string, sourceId: string) => {
    const response = await fetch('http://localhost:8000/api/v1/solve-doubt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        pdf_source_id: sourceId,
      }),
    });
    return response.json();
  },
  
  getAvailableSources: async () => {
    const response = await fetch('http://localhost:8000/api/v1/solve-doubt/sources');
    return response.json();
  },
};
```

### React Component

```tsx
import { useState } from 'react';
import { doubtSolverAPI } from '../api/doubtSolver';

export function DoubtSolver({ sourceId }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    setLoading(true);
    try {
      const result = await doubtSolverAPI.solveDoubt(question, sourceId);
      if (result.success) {
        setAnswer(result.data.answer);
      }
    } catch (error) {
      alert('Failed to get answer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="doubt-solver">
      <h2>💡 Ask Your Doubt</h2>
      
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="What would you like to understand better?"
        rows={4}
      />
      
      <button onClick={askQuestion} disabled={loading}>
        {loading ? 'Thinking...' : 'Get Explanation'}
      </button>
      
      {answer && (
        <div className="answer-box">
          <h3>📚 Explanation:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}
```

---

## Technical Implementation

### Backend Components

#### 1. **schemas.py** - Data Models
```python
class DoubtInput(BaseModel):
    question: str
    pdf_source_id: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class DoubtState(BaseModel):
    session_id: str
    pdf_source_id: str
    user_query: str
    retrieved_docs: List[Document] = []
    answer: str = ""
    simplification_level: str = "ELI5"
```

#### 2. **doubt_solver.py** - LangGraph Agent
```python
class DoubtSolverAgent:
    def __init__(self, llm, knowledge_base):
        self.llm = llm
        self.kb = knowledge_base
        self.graph = self._build_graph()
    
    def _retrieve_node(self, state: DoubtState):
        # Fetch relevant documents from knowledge base
        docs = self.kb.retrieve_context(
            query=state.user_query,
            pdf_source_id=state.pdf_source_id,
            k=5
        )
        return {"retrieved_docs": docs}
    
    def _generate_explanation_node(self, state: DoubtState):
        # Generate ELI5 explanation using LLM
        prompt = """You are a friendly, patient tutor.
        Context: {context}
        Question: {user_query}
        Task: Explain simply with analogies..."""
        # ... LLM call
        return {"answer": explanation}
```

#### 3. **doubt_solver.py (router)** - FastAPI Endpoint
```python
@router.post("", response_model=APIResponse)
async def solve_doubt(
    input_data: DoubtInput,
    agent: DoubtSolverAgent = Depends(get_doubt_solver_agent)
):
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        agent.solve_doubt,
        input_data
    )
    return APIResponse(success=True, data=result)
```

---

## The ELI5 Prompt

The secret sauce is the prompt design:

```
You are a friendly, patient tutor helping a student understand their study material.

CONTEXT FROM TEXTBOOK:
{retrieved context}

STUDENT'S QUESTION:
{user query}

YOUR TASK:
1. Answer using ONLY the provided context
2. Explain as if to a 5-year-old (ELI5 style)
3. Use everyday analogies
4. Break complicated ideas into simple steps
5. Be conversational and encouraging
6. If answer not in context, say "I couldn't find that in your study material"

IMPORTANT:
- Use simple words and short sentences
- Give real-world examples
- Make it easy to understand
- Stay positive
- Never make up information
```

---

## Comparison: Doubt Solver vs Quiz Generator

| Feature | Quiz Generator | Doubt Solver |
|---------|---------------|--------------|
| **Purpose** | Test knowledge | Explain concepts |
| **Output** | MCQs with options | Conversational explanation |
| **Tone** | Formal/Academic | Friendly/Simple |
| **Analogies** | Rare | Frequently used |
| **Use Case** | Active practice | Passive learning |
| **Speed** | 5-10 seconds | 3-5 seconds |

---

## Best Practices

### 1. Be Specific in Questions
```
✅ Good: "How does the Krebs cycle produce ATP?"
❌ Bad: "Tell me about biology"
```

### 2. One Concept at a Time
```
✅ Good: "What is mitosis?"
❌ Bad: "Explain mitosis, meiosis, and DNA replication"
```

### 3. Use for Clarification, Not Discovery
```
✅ Good: "I don't understand why enzymes denature at high temperatures"
❌ Bad: "What topics are in Chapter 5?"
```

### 4. Select the Right Material
```python
# Make sure you're asking about content from the correct source
solveDoubt("What is recursion?", "computer_science_textbook")
# Not: "biology_notes"
```

---

## Error Handling

### No Context Found

**Request:**
```json
{
  "question": "What is quantum entanglement?",
  "pdf_source_id": "biology_textbook"
}
```

**Response:**
```json
{
  "success": true,
  "message": "No relevant context found in the material",
  "data": {
    "answer": "I couldn't find that information in your study material. Could you try rephrasing your question or check if the right material is uploaded?",
    "context_found": false
  }
}
```

### Wrong Material Selected

If you ask about physics from a biology textbook, the system will:
1. Search the biology material
2. Find no relevant context
3. Politely say it couldn't find the answer

---

## Performance

### Benchmarks

| Operation | Time | Cost |
|-----------|------|------|
| Context Retrieval | ~200ms | $0.00 |
| LLM Explanation | ~3s | ~$0.002 |
| **Total** | **~3-5s** | **~$0.002** |

### Optimization Tips

1. **Chunk Size**: Keep document chunks ~1000-2000 chars for better context
2. **Retrieval Count**: 5 documents is optimal (more = slower, fewer = less context)
3. **Caching**: Consider caching frequently asked questions

---

## Future Enhancements

1. **Multi-Turn Conversations** - Follow-up questions in the same session
2. **Difficulty Levels** - "ELI5", "ELI10", "College Level"
3. **Visual Aids** - Generate diagrams for complex concepts
4. **Voice Input** - Ask questions via speech
5. **Save Favorites** - Bookmark helpful explanations

---

## FAQ

### Q: Can I ask questions not in my material?
**A:** No, the system only answers based on uploaded content. This prevents hallucinations and keeps answers grounded.

### Q: How is this different from ChatGPT?
**A:** ChatGPT uses general knowledge (which can be outdated or wrong). Doubt Solver uses YOUR specific study material, ensuring accurate, relevant answers.

### Q: Can I use this for exam questions?
**A:** Yes! It's perfect for understanding concepts you'll be tested on. However, use it alongside quiz generation for active practice.

### Q: What if the explanation is too simple?
**A:** Currently, all explanations use ELI5 style. Future versions will support difficulty levels (coming soon).

### Q: Does it work with YouTube transcripts?
**A:** Yes! Any uploaded material (PDF, YouTube, Syllabus) can be used for doubt solving.

---

## Conclusion

The Doubt Solver feature provides **personalized, grounded, and simplified explanations** for any concept in your study material. It's like having a patient tutor available 24/7 who explains things in a way that makes sense to you.

**Perfect for:**
- 🤔 Understanding confusing concepts
- 📖 Breaking down complex topics
- 🔗 Connecting theory to real-world examples
- 💡 Quick clarifications during study sessions

**Combine with:**
- 📝 Flash-Note Generator → Quick facts
- 💡 Doubt Solver → Deep understanding
- 🎯 Quiz Generator → Test knowledge

---

*Last updated: January 17, 2026*
