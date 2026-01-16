# "Default" Topic Mode - Generate Questions from Entire Document

## 🎯 Feature Overview

You can now use **"default"** as the topic to generate quiz questions from the **entire document** instead of searching for a specific topic.

## 📝 How to Use

### Option 1: Interactive Demo

```bash
cd backend/testing
python demo.py
```

**Steps:**
1. Choose: **Adaptive Mode** (option 2) or **Grind Mode** (option 3)
2. Select: **Start new session** (option 1)
3. Choose your PDF/material
4. When asked for topic, enter: **`default`**
5. Select difficulty level

**Example:**
```
Enter topic for quiz generation (or 'default' for whole document): default
```

### Option 2: Command Line

```python
from src.features.quiz_generation_main import start_student_session, get_next_quiz_batch

# Start session with "default" topic
session = start_student_session(
    user_id="student_001",
    pdf_id="your_pdf_id",
    topic="default",  # <-- Use "default" for entire document
    initial_difficulty="MEDIUM"
)

# Generate quiz
quiz = get_next_quiz_batch(session)
```

## 🔍 How It Works

### Normal Topic Mode (Specific Topic)
```
Topic: "Neural Networks"
   ↓
Search for relevant sections about Neural Networks
   ↓
Generate questions from those specific sections
```

### Default Mode (Entire Document)
```
Topic: "default"
   ↓
Randomly select sections from entire document
   ↓
Generate questions from diverse topics in the material
```

## 💡 When to Use Each Mode

### Use Specific Topic When:
- ✅ You want to focus on a particular subject
- ✅ Studying for an exam on specific topics
- ✅ Reviewing a particular chapter or concept
- ✅ You know what you need to practice

**Example topics:**
- "Linear Regression"
- "Convolutional Neural Networks"
- "SQL Joins"
- "Machine Learning Algorithms"

### Use "Default" Mode When:
- ✅ You want comprehensive coverage of the entire material
- ✅ Doing a general review before an exam
- ✅ Testing overall understanding
- ✅ The document covers a single cohesive topic
- ✅ You want variety in questions

## 📊 Behavior Comparison

| Aspect | Specific Topic | Default Mode |
|--------|---------------|--------------|
| **Retrieval** | Semantic search for topic | Random selection |
| **Coverage** | Narrow (topic-focused) | Broad (entire document) |
| **Question Variety** | Similar themes | Diverse topics |
| **Best For** | Targeted practice | Comprehensive review |
| **Example Output** | 5 questions on "Neural Networks" | 5 questions on different sections |

## 🎓 Example Scenarios

### Scenario 1: YouTube Video about SQL
```
Material: YouTube SQL tutorial (45 minutes)
Topic: "default"
Result: Questions covering SELECT, JOIN, WHERE, GROUP BY, etc.
```

### Scenario 2: Machine Learning PDF
```
Material: ML textbook chapter
Topic: "default"
Result: Questions mixing regression, classification, neural networks
```

### Scenario 3: Generated Syllabus Content
```
Material: LLM-generated content on "Data Structures"
Topic: "default"
Result: Questions on arrays, linked lists, trees, graphs, etc.
```

## 🔧 Implementation Details

### Modified Files

1. **[src/rag/storage.py](c:\College\Hackathons\HackCrypt\Rooster-HackCrypt\backend\src\rag\storage.py)**
   - Added: `retrieve_all_documents()` method
   - Updated: `retrieve_context()` to detect "default" keyword
   - Uses: `random.sample()` for document selection

2. **[src/agents/agent.py](c:\College\Hackathons\HackCrypt\Rooster-HackCrypt\backend\src\agents\agent.py)**
   - Updated: `_retrieve_node()` to show better messages for default mode
   - Displays: "ENTIRE DOCUMENT (default mode)" in console

3. **[testing/demo.py](c:\College\Hackathons\HackCrypt\Rooster-HackCrypt\backend\testing\demo.py)**
   - Added: Tip message about "default" option
   - Updated: Both Adaptive and Grind mode handlers

## 💻 Code Example

### Before (Specific Topic)
```python
session = start_student_session(
    user_id="user_001",
    pdf_id="ml_textbook",
    topic="Neural Networks",  # Specific topic
    initial_difficulty="MEDIUM"
)
```

**Output:**
```
🔍 Retrieving context for: Neural Networks
✓ Retrieved 5 relevant documents
✓ Generated 5 questions
```

### After (Default Mode)
```python
session = start_student_session(
    user_id="user_001",
    pdf_id="ml_textbook",
    topic="default",  # Entire document
    initial_difficulty="MEDIUM"
)
```

**Output:**
```
🔍 Retrieving context from: ENTIRE DOCUMENT (default mode)
📚 Retrieving from entire document (default mode)
✓ Retrieved 5 random documents from entire source
✓ Generated 5 questions
```

## ⚡ Performance Notes

- **Speed:** Default mode is typically faster (no semantic search needed)
- **Randomness:** Each quiz batch will have different topics
- **Coverage:** Over multiple quizzes, you'll see all sections of the document
- **Fairness:** Random selection ensures equal representation of all sections

## 🎯 Tips for Best Results

1. **Use with comprehensive materials:** Works best with well-structured documents
2. **Combine both modes:** Use specific topics for weak areas, default for review
3. **Multiple attempts:** Run several quizzes in default mode for full coverage
4. **Track progress:** Your mastery score will reflect understanding across all topics

## ✅ Testing

Test the feature:

```bash
cd backend/testing
python demo.py

# Menu flow:
# 2 (Adaptive Mode) → 1 (Start session) → Select PDF → Enter "default" → Choose difficulty
```

Expected behavior:
- ✅ No "No documents found" error
- ✅ Questions from various sections
- ✅ Console shows "ENTIRE DOCUMENT (default mode)"
- ✅ Questions are still difficulty-appropriate

---

**Summary:** Enter **"default"** as the topic to generate questions from your entire document! 🎉
