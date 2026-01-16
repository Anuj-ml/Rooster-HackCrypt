# Quick Start Guide - YouTube & Syllabus Support

## ✨ What's New?

Rooster-HackCrypt now generates quizzes from:
1. ✅ **PDF Documents** (original)
2. 🆕 **YouTube Videos** (fetch transcripts)
3. 🆕 **Any Topic** (LLM generates educational content)

## 🚀 Quick Setup

### 1. Install New Dependency

```bash
pip install youtube-transcript-api
```

### 2. Test the System

**Option A: Automated Test (Syllabus)**
```bash
cd backend
python test_loaders_simple.py
```

**Option B: Interactive Demo**
```bash
cd backend/testing
python demo.py
```

## 📖 Usage Examples

### Example 1: Generate Quiz from YouTube Video

**Step 1:** Open demo
```bash
cd backend/testing
python demo.py
```

**Step 2:** Load YouTube video
```
Main Menu → 1 (Document Ingestion)
           → 2 (Load from YouTube URL)

Enter YouTube URL: https://www.youtube.com/watch?v=HXV3zeQKqGY
Source ID: sql_basics
```

**Step 3:** Generate quiz
```
Main Menu → 2 (Adaptive Mode)
           → 1 (Start new session)

PDF ID: sql_basics
Topic: SQL
Difficulty: MEDIUM
```

**Result:** Quiz questions about SQL from the video! ✨

---

### Example 2: Generate Quiz from Any Topic

**Step 1:** Open demo
```bash
cd backend/testing
python demo.py
```

**Step 2:** Generate content
```
Main Menu → 1 (Document Ingestion)
           → 3 (Generate Syllabus Content)

Enter topic: Neural Networks
Source ID: neural_networks
```

**Step 3:** Generate quiz
```
Main Menu → 2 (Adaptive Mode)
           → 1 (Start new session)

PDF ID: neural_networks
Topic: Neural Networks
Difficulty: MEDIUM
```

**Result:** Quiz questions about Neural Networks! ✨

---

## 🎯 Command Line Usage

### YouTube Video

```python
from src.rag.ingestion_main import upload_material
from src.features.quiz_generation_main import start_student_session, get_next_quiz_batch

# 1. Load YouTube video
result = upload_material(
    material_type="YOUTUBE",
    content="https://www.youtube.com/watch?v=VIDEO_ID",
    source_id="my_video"
)

# 2. Start quiz session
session = start_student_session(
    user_id="student_001",
    pdf_id="my_video",
    topic="Video Topic",
    initial_difficulty="MEDIUM"
)

# 3. Generate quiz
quiz = get_next_quiz_batch(session)

# 4. Display questions
for i, q in enumerate(quiz, 1):
    print(f"\nQ{i}: {q.question}")
    for j, opt in enumerate(q.options, 1):
        print(f"  {j}. {opt}")
```

### Syllabus Topic

```python
from src.rag.ingestion_main import upload_material
from src.features.quiz_generation_main import start_student_session, get_next_quiz_batch

# 1. Generate content for topic
result = upload_material(
    material_type="SYLLABUS",
    content="Machine Learning",
    source_id="ml_basics"
)

# 2. Start quiz session
session = start_student_session(
    user_id="student_001",
    pdf_id="ml_basics",
    topic="Machine Learning",
    initial_difficulty="MEDIUM"
)

# 3. Generate quiz
quiz = get_next_quiz_batch(session)
```

---

## 🔧 Troubleshooting

### "No documents found for topic"

**Problem:** Quiz generation fails with no context available.

**Solutions:**
1. Check the `source_id` you used when uploading matches the `pdf_id` in session
2. View indexed materials: Demo Menu → 1 → 4
3. Try a broader topic keyword

### YouTube: "No transcript found"

**Problem:** Video doesn't have captions.

**Solutions:**
1. Use videos with captions enabled (most educational videos do)
2. Try a different video

### Syllabus: "Generated content too short"

**Problem:** LLM returned insufficient content.

**Solutions:**
1. Use more specific topics ("Neural Network Architectures" vs "AI")
2. Retry the generation (sometimes LLM response varies)

---

## 💡 Best Practices

### YouTube Videos
- ✅ Educational videos (lectures, tutorials)
- ✅ Videos with good captions
- ✅ 10-30 minute videos work best
- ❌ Avoid music videos, vlogs

### Syllabus Topics
- ✅ Specific but not too narrow
  - Good: "Convolutional Neural Networks"
  - Bad: "AI" (too broad)
- ✅ Standard academic terms
- ✅ One topic at a time

### Quiz Topics
- ✅ Use keywords from your content
- ✅ Match topic to what you indexed
- ✅ Start with MEDIUM difficulty

---

## 📊 What Happens Behind the Scenes?

### YouTube Pipeline
```
YouTube URL
  ↓ Extract video ID
  ↓ Fetch transcript (youtube-transcript-api)
  ↓ Clean & combine segments
  ↓ Create Document
  ↓ Split into chunks (3000 chars)
  ↓ Generate atomic propositions (Groq LLM)
  ↓ Index in ChromaDB
  ↓ Ready for quiz generation!
```

### Syllabus Pipeline
```
Topic Name
  ↓ Create "textbook writer" prompt
  ↓ Generate content (Groq LLM, 1500-2000 words)
  ↓ Create Document
  ↓ Split into chunks (3000 chars)
  ↓ Generate atomic propositions (Groq LLM)
  ↓ Index in ChromaDB
  ↓ Ready for quiz generation!
```

---

## 🎉 You're Ready!

The system now supports:
- ✅ PDF documents
- ✅ YouTube videos
- ✅ Any educational topic

All using the **same quiz generation logic** with adaptive difficulty! 🚀
