# 📊 CHANGES.md - Feature Gap Analysis & Implementation Plan

## Rooster-HackCrypt: Current vs. Target System Comparison

**Created**: 2026-01-16  
**Purpose**: Detailed comparison between current implementation and target features with step-by-step implementation guide.

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [File Structure Comparison](#file-structure-comparison)
3. [Missing Files Analysis](#missing-files-analysis)
4. [Feature Gap Analysis](#feature-gap-analysis)
5. [Detailed Implementation Plan](#detailed-implementation-plan)
6. [Code Changes Per File](#code-changes-per-file)
7. [Priority Matrix](#priority-matrix)
8. [Testing Strategy](#testing-strategy)

---

## 🎯 Executive Summary

### Current System Status

| Component | Current State | Target State | Gap |
|-----------|--------------|--------------|-----|
| **PDF Processing** | ✅ Working | ✅ Complete | None |
| **RAG System** | ✅ Working | ✅ Complete | None |
| **Persistent Storage** | ✅ Working | ✅ Complete | None |
| **Quiz Generation** | ✅ Basic | ✅ With formatting | Minor improvements |
| **Adaptive Learning** | ❌ Missing | ✅ Complete | **MAJOR GAP** |
| **Grind Mode** | ❌ Missing | ✅ Complete | **MAJOR GAP** |
| **Logic Engine** | ❌ Missing | ✅ Complete | **MAJOR GAP** |
| **Demo Scripts** | ❌ Missing | ✅ Complete | Medium gap |
| **Documentation** | ⚠️ Partial | ✅ Complete | Medium gap |

### Key Findings

**✅ What You Have (Working):**
- PDF loading and chunking (3000 chars)
- LLM proposition decomposition with fallback
- ChromaDB + Pickle persistent storage
- Basic quiz generation with LangGraph
- Rate limiting and error handling

**❌ What's Missing (Critical):**
1. **`logic_engine.py`** - Session management, adaptive difficulty, mastery tracking
2. **`grind_mode.py`** - Fixed difficulty practice mode
3. **Session state management** - In-memory sessions with difficulty progression
4. **`start_student_session()`** - Adaptive mode entry point
5. **`start_grind_session()`** - Grind mode entry point
6. **`get_next_quiz_batch()`** - Difficulty-aware quiz generation
7. **`submit_quiz_results()`** - Results processing with difficulty adjustment
8. **`format_quiz_for_display()`** - Clean quiz formatting
9. **`demo.py`** - Demonstration scripts
10. **`test_grind.py`** - Test scripts

---

## 📁 File Structure Comparison

### Current Structure
```
c:\College\Hackathons\HackCrypt\Rooster-HackCrypt/
│
├── backend/
│   ├── agent.py               ✅ Exists (needs minor updates)
│   ├── ingestion_main.py      ✅ Exists (needs MAJOR updates)
│   ├── pre_processor.py       ✅ Exists (complete)
│   ├── storage.py             ✅ Exists (complete)
│   ├── schemas.py             ✅ Exists (complete)
│   ├── requirements.txt       ✅ Exists
│   ├── .gitignore             ✅ Exists
│   └── ip_data/               ✅ Exists
│
├── frontend/                  ⚠️ Empty
├── checkpoint.md              ✅ Exists
├── data/                      ✅ Exists (runtime)
└── .gitignore                 ✅ Exists
```

### Target Structure (What's Missing)
```
backend/
│   ├── logic_engine.py        ❌ MISSING - Session & Adaptive Logic
│   ├── grind_mode.py          ❌ MISSING - Practice Mode
│   ├── demo.py                ❌ MISSING - Demo Script
│   ├── test_grind.py          ❌ MISSING - Test Script
│
├── PROJECT_SUMMARY.md         ❌ MISSING - Documentation
├── QUICK_START.md             ❌ MISSING - Documentation
├── REFACTORING_SUMMARY.md     ❌ MISSING - Documentation
├── GRIND_ZONE_ENHANCEMENT.md  ❌ MISSING - Documentation
```

---

## 📄 Missing Files Analysis

### 1. `logic_engine.py` (CRITICAL - ~100 lines)

**Purpose**: Central session management and adaptive difficulty adjustment

**What It Provides**:
- In-memory session state storage
- Difficulty progression logic (EASY → MEDIUM → HARD)
- Mastery score calculation (70% history + 30% recent)
- Streak tracking for grind mode
- Dual mode support (ADAPTIVE vs GRIND)

**Key Classes/Functions**:
```python
class AdaptiveLogic:
    def __init__(self)                          # Initialize sessions dict
    def create_session(user_id, pdf_id, topic, mode, difficulty)
    def get_session_state(session_id)           
    def process_batch_results(session_id, results)
```

**Session State Structure**:
```python
{
    "user_id": str,
    "pdf_source_id": str,
    "topic": str,
    "mode": "ADAPTIVE" | "GRIND",
    "current_difficulty": "EASY" | "MEDIUM" | "HARD",
    "mastery_score": 0.0-1.0,
    "streak": int,
    "history": []
}
```

---

### 2. `grind_mode.py` (IMPORTANT - ~200 lines)

**Purpose**: Dedicated module for fixed-difficulty practice

**What It Provides**:
- Clean API separate from adaptive logic
- Streak tracking with reset on failure
- Mastery building at fixed difficulty
- Detailed statistics tracking

**Key Components**:
```python
class GrindMode:
    def start_grind_session(user_id, pdf_id, topic, difficulty)
    def get_grind_quiz(session_id)
    def submit_grind_results(session_id, results)
    def get_grind_stats(session_id)

def grind_practice_loop(agent, session_id, num_rounds)
```

---

### 3. `demo.py` (NICE TO HAVE - ~180 lines)

**Purpose**: Comprehensive demonstration of both modes

**What It Provides**:
- Visual demonstration of adaptive mode
- Visual demonstration of grind mode
- Formatted output examples
- Quick validation of system functionality

---

### 4. `test_grind.py` (NICE TO HAVE - ~200 lines)

**Purpose**: Testing and validation

**What It Provides**:
- Dependency checks
- PDF upload tests
- Grind mode functionality tests
- Output format verification

---

## 🔍 Feature Gap Analysis

### Gap 1: No Session Management

**Current Behavior**:
```python
# ingestion_main.py - Current
def student_request_quiz(session_id: str, pdf_id: str, topic: str):
    input_data = {
        "current_difficulty": "HARD",  # ⚠️ HARDCODED!
        ...
    }
```

**Target Behavior**:
```python
# ingestion_main.py - Target
def get_next_quiz_batch(session_id):
    state = ADAPTIVE_ENGINE.get_session_state(session_id)  # ✅ Dynamic
    input_data = {
        "current_difficulty": state["current_difficulty"],  # From engine
        ...
    }
```

**Impact**: System cannot adapt to student performance

---

### Gap 2: No Adaptive Difficulty Logic

**Current**: Difficulty is always "HARD" (hardcoded)

**Target**:
```python
# In logic_engine.py
def process_batch_results(session_id, results):
    accuracy = sum(results) / len(results)
    
    if mode == "ADAPTIVE":
        if accuracy >= 0.8:
            level_up()      # EASY → MEDIUM → HARD
        elif accuracy <= 0.4:
            level_down()    # HARD → MEDIUM → EASY
    
    # Update mastery score
    new_mastery = (old_mastery * 0.7) + (accuracy * 0.3)
```

---

### Gap 3: No Grind Mode

**Current**: Only basic quiz generation, no practice mode

**Target**: Fixed difficulty practice with streak tracking
```python
# Grind mode behavior
session = start_grind_session("user", "pdf", "topic", "MEDIUM")
quiz = get_next_quiz_batch(session)
feedback = submit_quiz_results(session, [True]*5)
# → Streak: 1, Difficulty stays MEDIUM (never changes)
```

---

### Gap 4: No Quiz Formatting

**Current**: Raw quiz output without formatting

**Target**:
```python
def format_quiz_for_display(quiz_output):
    """
    Q1: What is GDP?
    
       a) Gross Domestic Product
       b) General Development Plan
       c) Government Deficit Percentage
       d) Growth Demand Projection
    
    ✓ Answer: a) Gross Domestic Product
    📖 Explanation: GDP measures the total...
    """
```

---

### Gap 5: Agent Prompt Needs Improvement

**Current**:
```python
prompt = ChatPromptTemplate.from_template("""
You are a strict quiz generator.
Context: {context}
Task: Create 5 {difficulty} multiple choice questions about "{topic}".
""")
```

**Target** (Strict formatting):
```python
prompt = ChatPromptTemplate.from_template("""
You are a strict quiz generator. Create EXACTLY 5 questions.

CRITICAL FORMATTING RULES:
1. Options must be PLAIN TEXT only - NO prefixes like "A)", "1.", "(a)"
2. Each option should be a complete, standalone answer
3. correct_answer must EXACTLY match one of the options
4. Questions should be self-contained

Context: {context}
Difficulty: {difficulty}
Topic: {topic}
""")
```

---

## 📝 Detailed Implementation Plan

### Phase 1: Create Logic Engine (CRITICAL)

**File**: `backend/logic_engine.py`

**Step 1.1**: Create the AdaptiveLogic class
```python
# backend/logic_engine.py

import uuid
from typing import Dict, List, Any

class AdaptiveLogic:
    """
    Central engine for session management and adaptive difficulty.
    Supports both ADAPTIVE and GRIND modes.
    """
    
    DIFFICULTY_LEVELS = ["EASY", "MEDIUM", "HARD"]
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(
        self, 
        user_id: str, 
        pdf_source_id: str, 
        topic: str,
        mode: str = "ADAPTIVE",  # "ADAPTIVE" or "GRIND"
        initial_difficulty: str = "EASY"
    ) -> str:
        """Create a new learning session."""
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "pdf_source_id": pdf_source_id,
            "topic": topic,
            "mode": mode,
            "current_difficulty": initial_difficulty,
            "mastery_score": 0.0,
            "streak": 0,
            "history": []
        }
        
        return session_id
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Retrieve session state."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]
    
    def process_batch_results(
        self, 
        session_id: str, 
        results: List[bool]
    ) -> Dict[str, Any]:
        """
        Process quiz results and update session state.
        Returns feedback about difficulty changes.
        """
        state = self.sessions[session_id]
        accuracy = sum(results) / len(results)
        
        # Update history
        state["history"].append({
            "accuracy": accuracy,
            "difficulty": state["current_difficulty"]
        })
        
        # Update mastery (weighted average)
        old_mastery = state["mastery_score"]
        state["mastery_score"] = (old_mastery * 0.7) + (accuracy * 0.3)
        
        feedback = {
            "accuracy": accuracy,
            "mastery": state["mastery_score"],
            "old_difficulty": state["current_difficulty"],
            "new_difficulty": state["current_difficulty"],
            "streak": state["streak"],
            "message": ""
        }
        
        if state["mode"] == "ADAPTIVE":
            feedback = self._apply_adaptive_logic(state, accuracy, feedback)
        else:  # GRIND mode
            feedback = self._apply_grind_logic(state, accuracy, feedback)
        
        return feedback
    
    def _apply_adaptive_logic(
        self, 
        state: Dict, 
        accuracy: float,
        feedback: Dict
    ) -> Dict:
        """Apply adaptive difficulty adjustment."""
        current_idx = self.DIFFICULTY_LEVELS.index(state["current_difficulty"])
        
        if accuracy >= 0.8 and current_idx < 2:
            # Level up
            state["current_difficulty"] = self.DIFFICULTY_LEVELS[current_idx + 1]
            state["streak"] += 1
            feedback["new_difficulty"] = state["current_difficulty"]
            feedback["message"] = f"🎉 Leveling up to {state['current_difficulty']}!"
        elif accuracy <= 0.4 and current_idx > 0:
            # Level down
            state["current_difficulty"] = self.DIFFICULTY_LEVELS[current_idx - 1]
            state["streak"] = 0
            feedback["new_difficulty"] = state["current_difficulty"]
            feedback["message"] = f"📉 Moving to {state['current_difficulty']} for more practice."
        else:
            # Stay at current level
            if accuracy >= 0.8:
                state["streak"] += 1
            else:
                state["streak"] = 0
            feedback["message"] = f"📊 Staying at {state['current_difficulty']}. Keep practicing!"
        
        feedback["streak"] = state["streak"]
        return feedback
    
    def _apply_grind_logic(
        self, 
        state: Dict, 
        accuracy: float,
        feedback: Dict
    ) -> Dict:
        """Apply grind mode logic (difficulty NEVER changes)."""
        if accuracy >= 0.8:
            state["streak"] += 1
            feedback["message"] = f"🔥 Grind on fire! Streak: {state['streak']}"
        else:
            state["streak"] = 0
            feedback["message"] = f"💪 Keep grinding at {state['current_difficulty']}!"
        
        feedback["streak"] = state["streak"]
        # Difficulty stays the same in GRIND mode
        return feedback
```

---

### Phase 2: Update `ingestion_main.py` (CRITICAL)

**Step 2.1**: Add imports and initialize engine
```python
# Add at top of ingestion_main.py
from logic_engine import AdaptiveLogic

# After other initializations
ADAPTIVE_ENGINE = AdaptiveLogic()
```

**Step 2.2**: Add new workflow functions
```python
# Add these functions to ingestion_main.py

def start_student_session(user_id: str, pdf_id: str, topic: str) -> str:
    """
    Start an ADAPTIVE learning session.
    Difficulty auto-adjusts based on performance.
    """
    session_id = ADAPTIVE_ENGINE.create_session(
        user_id=user_id,
        pdf_source_id=pdf_id,
        topic=topic,
        mode="ADAPTIVE",
        initial_difficulty="EASY"
    )
    print(f"✓ Started ADAPTIVE session: {session_id}")
    print(f"  Topic: {topic}, Starting at: EASY")
    return session_id


def start_grind_session(
    user_id: str, 
    pdf_id: str, 
    topic: str, 
    difficulty: str = "EASY"
) -> str:
    """
    Start a GRIND mode session at fixed difficulty.
    Difficulty will NOT change regardless of performance.
    """
    session_id = ADAPTIVE_ENGINE.create_session(
        user_id=user_id,
        pdf_source_id=pdf_id,
        topic=topic,
        mode="GRIND",
        initial_difficulty=difficulty.upper()
    )
    print(f"✓ Started GRIND session: {session_id}")
    print(f"  Topic: {topic}, Fixed difficulty: {difficulty}")
    return session_id


def get_next_quiz_batch(session_id: str):
    """
    Generate next quiz batch based on current session state.
    Uses current difficulty from the adaptive engine.
    """
    state = ADAPTIVE_ENGINE.get_session_state(session_id)
    
    print(f"--- Generating Quiz ---")
    print(f"  Mode: {state['mode']}")
    print(f"  Difficulty: {state['current_difficulty']}")
    print(f"  Mastery: {state['mastery_score']:.2f}")
    
    input_data = {
        "session_id": session_id,
        "pdf_source_id": state["pdf_source_id"],
        "current_difficulty": state["current_difficulty"],
        "topic": state["topic"]
    }
    
    result = agent.run_session(input_data)
    return result.get('generated_quiz')


def submit_quiz_results(session_id: str, results: list) -> dict:
    """
    Submit quiz results and get feedback.
    For ADAPTIVE mode: difficulty may change.
    For GRIND mode: only streak updates.
    """
    feedback = ADAPTIVE_ENGINE.process_batch_results(session_id, results)
    
    print(f"\n--- Results ---")
    print(f"  Accuracy: {feedback['accuracy']*100:.0f}%")
    print(f"  Mastery: {feedback['mastery']:.2f}")
    print(f"  {feedback['message']}")
    
    if feedback['old_difficulty'] != feedback['new_difficulty']:
        print(f"  Difficulty: {feedback['old_difficulty']} → {feedback['new_difficulty']}")
    
    return feedback


def format_quiz_for_display(quiz_output):
    """
    Format quiz for clean console display.
    Adds letter prefixes (a, b, c, d) at display time.
    """
    if not quiz_output or not quiz_output.questions:
        print("No quiz to display.")
        return
    
    letters = ['a', 'b', 'c', 'd']
    
    print("\n" + "="*60)
    print("📝 QUIZ")
    print("="*60)
    
    for i, q in enumerate(quiz_output.questions, 1):
        print(f"\nQ{i}: {q.question}\n")
        
        for j, opt in enumerate(q.options[:4]):
            # Clean option text (remove any existing prefixes)
            clean_opt = opt.strip()
            if clean_opt and clean_opt[0] in "ABCDabcd1234" and len(clean_opt) > 1:
                if clean_opt[1] in ".):":
                    clean_opt = clean_opt[2:].strip()
            print(f"   {letters[j]}) {clean_opt}")
        
        # Find correct answer index
        correct_letter = "?"
        for j, opt in enumerate(q.options[:4]):
            if q.correct_answer.lower() in opt.lower() or opt.lower() in q.correct_answer.lower():
                correct_letter = letters[j]
                break
        
        print(f"\n   ✓ Answer: {correct_letter}) {q.correct_answer}")
        print(f"   📖 {q.explanation}")
    
    print("\n" + "="*60)
```

**Step 2.3**: Update main block for demo
```python
# Replace the if __name__ == "__main__" block

if __name__ == "__main__":
    print("="*60)
    print("🐓 ROOSTER-HACKCRYPT - Adaptive Quiz System")
    print("="*60)
    
    # Check for existing data
    sources = kb.get_all_pdf_sources()
    print(f"\n📚 Indexed PDFs: {sources}")
    
    # Demo: Grind Mode
    if sources:
        pdf_id = sources[0]
        print(f"\n--- Starting Grind Mode Demo ---")
        
        session = start_grind_session(
            user_id="demo_user",
            pdf_id=pdf_id,
            topic="Indian Economy",
            difficulty="MEDIUM"
        )
        
        quiz = get_next_quiz_batch(session)
        
        if quiz:
            format_quiz_for_display(quiz)
            
            # Simulate perfect answers
            results = [True, True, True, True, True]
            feedback = submit_quiz_results(session, results)
            
            print(f"\n🔥 Streak: {feedback['streak']}")
            print(f"📊 Mastery: {feedback['mastery']:.2f}")
    else:
        print("\n⚠️ No PDFs indexed. Run upload_new_material() first.")
        print("Example:")
        print('  upload_new_material("ip_data/Module 3.pdf", "eco_101")')
```

---

### Phase 3: Update `agent.py` (Minor)

**Step 3.1**: Improve quiz generation prompt
```python
# In agent.py, update _generate_node method

def _generate_node(self, state: AgentState):
    """Node: Generate Quiz JSON with strict formatting."""
    if not state.retrieved_docs:
        return {"generated_quiz": None}

    context_str = "\n\n".join([d.page_content for d in state.retrieved_docs if d])
    
    prompt = ChatPromptTemplate.from_template("""
You are a strict quiz generator. Create EXACTLY 5 multiple choice questions.

CRITICAL FORMATTING RULES:
1. Each question must have EXACTLY 4 options
2. Options must be PLAIN TEXT only - NO prefixes like "A)", "1.", "(a)", etc.
3. Each option should be a complete, standalone answer
4. correct_answer must EXACTLY match one of the 4 options (word for word)
5. Questions should be self-contained (don't reference "the passage")
6. Explanations should be concise but informative

Difficulty Level: {difficulty}
- EASY: Recall-based questions, straightforward facts
- MEDIUM: Understanding and application, some analysis
- HARD: Analysis, synthesis, complex reasoning

Context:
{context}

Topic: "{topic}"

Generate 5 {difficulty} questions about the topic using the context.
""")
    
    chain = prompt | self.llm.with_structured_output(QuizOutput)
    
    response = chain.invoke({
        "context": context_str,
        "difficulty": state.current_difficulty,
        "topic": state.topic
    })
    
    return {"generated_quiz": response}
```

---

### Phase 4: Create `grind_mode.py` (Optional but Recommended)

```python
# backend/grind_mode.py

"""
Dedicated Grind Mode module for fixed-difficulty practice.
Provides clean API separate from adaptive learning.
"""

from typing import List, Dict, Any

class GrindMode:
    """
    Grind Mode: Practice at fixed difficulty with streak tracking.
    """
    
    def __init__(self, agent, engine):
        self.agent = agent
        self.engine = engine
    
    def start_grind_session(
        self,
        user_id: str,
        pdf_id: str,
        topic: str,
        difficulty: str = "EASY"
    ) -> str:
        """Start a grind session at fixed difficulty."""
        return self.engine.create_session(
            user_id=user_id,
            pdf_source_id=pdf_id,
            topic=topic,
            mode="GRIND",
            initial_difficulty=difficulty.upper()
        )
    
    def get_grind_quiz(self, session_id: str):
        """Generate quiz at fixed difficulty."""
        state = self.engine.get_session_state(session_id)
        
        input_data = {
            "session_id": session_id,
            "pdf_source_id": state["pdf_source_id"],
            "current_difficulty": state["current_difficulty"],
            "topic": state["topic"]
        }
        
        result = self.agent.run_session(input_data)
        return result.get('generated_quiz')
    
    def submit_grind_results(
        self, 
        session_id: str, 
        results: List[bool]
    ) -> Dict[str, Any]:
        """Submit results and update streak."""
        return self.engine.process_batch_results(session_id, results)
    
    def get_grind_stats(self, session_id: str) -> Dict[str, Any]:
        """Get detailed practice statistics."""
        state = self.engine.get_session_state(session_id)
        
        return {
            "difficulty": state["current_difficulty"],
            "streak": state["streak"],
            "mastery": state["mastery_score"],
            "total_quizzes": len(state["history"]),
            "average_accuracy": (
                sum(h["accuracy"] for h in state["history"]) / len(state["history"])
                if state["history"] else 0
            )
        }


def grind_practice_loop(grind_mode, session_id: str, num_rounds: int = 3):
    """
    Automated practice loop for demonstration.
    Simulates multiple rounds with random performance.
    """
    import random
    
    print(f"\n{'='*50}")
    print(f"🏋️ GRIND ZONE - {num_rounds} Rounds")
    print(f"{'='*50}")
    
    for round_num in range(1, num_rounds + 1):
        print(f"\n--- Round {round_num}/{num_rounds} ---")
        
        quiz = grind_mode.get_grind_quiz(session_id)
        
        if not quiz:
            print("Failed to generate quiz")
            continue
        
        # Simulate answers (80% chance of correct for demo)
        results = [random.random() < 0.8 for _ in quiz.questions]
        
        feedback = grind_mode.submit_grind_results(session_id, results)
        
        correct = sum(results)
        print(f"  Score: {correct}/5 ({feedback['accuracy']*100:.0f}%)")
        print(f"  {feedback['message']}")
    
    # Final stats
    stats = grind_mode.get_grind_stats(session_id)
    
    print(f"\n{'='*50}")
    print(f"📊 FINAL STATS")
    print(f"{'='*50}")
    print(f"  Difficulty: {stats['difficulty']} (unchanged)")
    print(f"  Best Streak: {stats['streak']}")
    print(f"  Mastery: {stats['mastery']:.2%}")
    print(f"  Total Quizzes: {stats['total_quizzes']}")
    print(f"  Avg Accuracy: {stats['average_accuracy']:.2%}")
```

---

### Phase 5: Create Demo Scripts (Optional)

**File**: `backend/demo.py`
```python
# backend/demo.py

"""
Complete demonstration of Rooster-HackCrypt system.
Shows both Adaptive and Grind modes.
"""

import random
from ingestion_main import (
    start_student_session,
    start_grind_session,
    get_next_quiz_batch,
    submit_quiz_results,
    format_quiz_for_display,
    kb
)


def demo_adaptive_mode():
    """Demonstrate adaptive difficulty progression."""
    print("\n" + "="*60)
    print("🎯 ADAPTIVE MODE DEMO")
    print("="*60)
    
    sources = kb.get_all_pdf_sources()
    if not sources:
        print("No PDFs indexed!")
        return
    
    session = start_student_session("demo_user", sources[0], "Economy")
    
    # Round 1: Perfect score → Level up
    print("\n--- Round 1: Aiming for perfect ---")
    quiz = get_next_quiz_batch(session)
    if quiz:
        results = [True, True, True, True, True]  # 100%
        feedback = submit_quiz_results(session, results)
        print(f"  → Expected: Level up to MEDIUM")
    
    # Round 2: Perfect again → Level up to HARD
    print("\n--- Round 2: Perfect again ---")
    quiz = get_next_quiz_batch(session)
    if quiz:
        results = [True, True, True, True, True]  # 100%
        feedback = submit_quiz_results(session, results)
        print(f"  → Expected: Level up to HARD")
    
    # Round 3: Poor score → Level down
    print("\n--- Round 3: Struggling ---")
    quiz = get_next_quiz_batch(session)
    if quiz:
        results = [True, False, False, False, False]  # 20%
        feedback = submit_quiz_results(session, results)
        print(f"  → Expected: Level down to MEDIUM")


def demo_grind_mode():
    """Demonstrate grind mode with streak building."""
    print("\n" + "="*60)
    print("🏋️ GRIND MODE DEMO")
    print("="*60)
    
    sources = kb.get_all_pdf_sources()
    if not sources:
        print("No PDFs indexed!")
        return
    
    session = start_grind_session("demo_user", sources[0], "Economy", "HARD")
    
    # Multiple rounds at fixed difficulty
    for i in range(3):
        print(f"\n--- Grind Round {i+1} ---")
        quiz = get_next_quiz_batch(session)
        
        if quiz:
            # Simulate good performance
            results = [True, True, True, True, random.choice([True, False])]
            feedback = submit_quiz_results(session, results)
            print(f"  Difficulty: HARD (never changes)")
            print(f"  Streak: {feedback['streak']}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("🐓 ROOSTER-HACKCRYPT DEMO")
    print("="*60)
    
    demo_adaptive_mode()
    demo_grind_mode()
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
```

---

## 🔧 Code Changes Per File

### Summary Table

| File | Action | Lines to Add | Lines to Modify |
|------|--------|--------------|-----------------|
| `logic_engine.py` | **CREATE** | ~100 | 0 |
| `ingestion_main.py` | **UPDATE** | ~120 | ~30 |
| `agent.py` | **UPDATE** | ~20 | ~10 |
| `grind_mode.py` | **CREATE** (optional) | ~100 | 0 |
| `demo.py` | **CREATE** (optional) | ~80 | 0 |
| `test_grind.py` | **CREATE** (optional) | ~100 | 0 |

---

## 📊 Priority Matrix

### P0 - Critical (Must Have)

| Item | Effort | Impact | Status |
|------|--------|--------|--------|
| `logic_engine.py` | Medium | 🔴 Critical | ❌ Missing |
| Session management functions | Medium | 🔴 Critical | ❌ Missing |
| `start_student_session()` | Low | 🔴 Critical | ❌ Missing |
| `get_next_quiz_batch()` | Low | 🔴 Critical | ❌ Missing |
| `submit_quiz_results()` | Low | 🔴 Critical | ❌ Missing |

### P1 - High (Should Have)

| Item | Effort | Impact | Status |
|------|--------|--------|--------|
| `start_grind_session()` | Low | 🟠 High | ❌ Missing |
| `format_quiz_for_display()` | Low | 🟠 High | ❌ Missing |
| Agent prompt improvements | Low | 🟠 High | ⚠️ Partial |

### P2 - Medium (Nice to Have)

| Item | Effort | Impact | Status |
|------|--------|--------|--------|
| `grind_mode.py` | Medium | 🟡 Medium | ❌ Missing |
| `demo.py` | Low | 🟡 Medium | ❌ Missing |
| `test_grind.py` | Medium | 🟡 Medium | ❌ Missing |

### P3 - Low (Future)

| Item | Effort | Impact | Status |
|------|--------|--------|--------|
| Frontend UI | High | 🟢 Low (for now) | ❌ Missing |
| FastAPI endpoints | Medium | 🟢 Low (for now) | ❌ Missing |
| Persistent sessions (DB) | High | 🟢 Low (for now) | ❌ Missing |

---

## 🧪 Testing Strategy

### Unit Tests

```python
# Test logic_engine.py
def test_create_session():
    engine = AdaptiveLogic()
    session_id = engine.create_session("user1", "pdf1", "topic1", "ADAPTIVE", "EASY")
    assert session_id.startswith("sess_")
    state = engine.get_session_state(session_id)
    assert state["current_difficulty"] == "EASY"
    assert state["mode"] == "ADAPTIVE"

def test_adaptive_level_up():
    engine = AdaptiveLogic()
    session_id = engine.create_session("user1", "pdf1", "topic1", "ADAPTIVE", "EASY")
    feedback = engine.process_batch_results(session_id, [True]*5)  # 100%
    assert feedback["new_difficulty"] == "MEDIUM"

def test_grind_mode_no_level_change():
    engine = AdaptiveLogic()
    session_id = engine.create_session("user1", "pdf1", "topic1", "GRIND", "HARD")
    feedback = engine.process_batch_results(session_id, [False]*5)  # 0%
    assert feedback["new_difficulty"] == "HARD"  # Should NOT change
```

### Integration Tests

```python
def test_full_adaptive_flow():
    # 1. Upload PDF
    upload_new_material("ip_data/test.pdf", "test_001")
    
    # 2. Start session
    session = start_student_session("user", "test_001", "topic")
    
    # 3. Get quiz
    quiz = get_next_quiz_batch(session)
    assert quiz is not None
    assert len(quiz.questions) == 5
    
    # 4. Submit results
    feedback = submit_quiz_results(session, [True]*5)
    assert feedback["accuracy"] == 1.0
```

---

## ✅ Implementation Checklist

### Phase 1: Logic Engine (Day 1)
- [ ] Create `backend/logic_engine.py`
- [ ] Implement `AdaptiveLogic` class
- [ ] Implement `create_session()` method
- [ ] Implement `get_session_state()` method
- [ ] Implement `process_batch_results()` method
- [ ] Implement `_apply_adaptive_logic()` method
- [ ] Implement `_apply_grind_logic()` method
- [ ] Test with basic unit tests

### Phase 2: Update ingestion_main.py (Day 1-2)
- [ ] Add logic_engine import
- [ ] Initialize `ADAPTIVE_ENGINE`
- [ ] Implement `start_student_session()`
- [ ] Implement `start_grind_session()`
- [ ] Implement `get_next_quiz_batch()`
- [ ] Implement `submit_quiz_results()`
- [ ] Implement `format_quiz_for_display()`
- [ ] Update main block for demo
- [ ] Remove hardcoded difficulty

### Phase 3: Update agent.py (Day 2)
- [ ] Improve quiz generation prompt
- [ ] Add strict formatting rules
- [ ] Test quiz output format

### Phase 4: Create grind_mode.py (Day 2-3)
- [ ] Create `GrindMode` class
- [ ] Implement practice loop helper
- [ ] Test grind mode functionality

### Phase 5: Documentation & Testing (Day 3)
- [ ] Create `demo.py`
- [ ] Create `test_grind.py`
- [ ] Run full integration tests
- [ ] Update README/documentation

---

## 📈 Expected Outcome

After implementing all changes:

| Feature | Before | After |
|---------|--------|-------|
| Session Management | ❌ None | ✅ Full in-memory sessions |
| Adaptive Difficulty | ❌ Hardcoded | ✅ Auto-adjusts (EASY→MEDIUM→HARD) |
| Grind Mode | ❌ None | ✅ Fixed difficulty practice |
| Mastery Tracking | ❌ None | ✅ Weighted score (70/30) |
| Streak Tracking | ❌ None | ✅ Build streaks for motivation |
| Quiz Formatting | ❌ Raw output | ✅ Clean display with letters |
| Demo Scripts | ❌ None | ✅ Full demonstrations |

---

## 🚀 Quick Start After Implementation

```python
# Adaptive Learning (auto-adjusts difficulty)
from ingestion_main import *

session = start_student_session("user_123", "eco_101", "Indian Economy")
quiz = get_next_quiz_batch(session)
format_quiz_for_display(quiz)
feedback = submit_quiz_results(session, [True, True, False, True, True])
# → Difficulty may change based on performance

# Grind Mode (fixed difficulty practice)
session = start_grind_session("user_123", "eco_101", "GDP", "HARD")
quiz = get_next_quiz_batch(session)
format_quiz_for_display(quiz)
feedback = submit_quiz_results(session, [True, True, True, True, True])
# → Difficulty stays HARD, streak increases
```

---

**Document Version**: 1.0  
**Created**: 2026-01-16  
**Estimated Implementation Time**: 2-3 days  
**Total New Lines of Code**: ~500-600
