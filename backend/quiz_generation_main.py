# backend/quiz_generation_main.py

"""
Rooster-HackCrypt: Quiz Generation & Session Management Module

This module handles all quiz-related operations:
1. Session management (ADAPTIVE and GRIND modes)
2. Quiz generation orchestration
3. Result submission and feedback
4. Quiz display formatting

All configuration is parameterized - nothing is hardcoded.
"""

import os
import re
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Model Configuration ---
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# GROQ CONFIGURATION (FREE & FAST)
LLM_MODEL = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# HuggingFace Embeddings (FREE & LOCAL)
EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# --- Import Custom Modules ---
from storage import KnowledgeBase
from agent import QuizAgent
from logic_engine import AdaptiveLogic
from difficulty_engine import (
    DEFAULT_QUIZ_CONFIG,
    DEFAULT_GRIND_CONFIG,
    get_quiz_config,
    get_grind_config
)

# --- Initialize Components ---
kb = KnowledgeBase(embedding_model=EMBEDDING_MODEL)
agent = QuizAgent(llm=LLM_MODEL, knowledge_base=kb)

# Global Adaptive Engine (in-memory sessions)
ADAPTIVE_ENGINE = AdaptiveLogic()


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def start_student_session(
    user_id: str,
    pdf_id: str,
    topic: str,
    initial_difficulty: str = "EASY",
    config: Dict[str, Any] = None
) -> str:
    """
    Start an ADAPTIVE learning session.
    
    In Adaptive mode:
    - Starts at specified difficulty (default: EASY)
    - Auto-adjusts based on performance:
      - ≥80% correct → Level up (EASY→MEDIUM→HARD)
      - ≤40% correct → Level down (HARD→MEDIUM→EASY)
    - Difficulty evaluated every N batches (default: 2)
    
    Args:
        user_id: User identifier
        pdf_id: PDF source identifier (from upload_new_material)
        topic: Topic for quiz generation
        initial_difficulty: Starting difficulty (EASY/MEDIUM/HARD)
        config: Optional configuration overrides (from get_quiz_config())
        
    Returns:
        session_id: Use this for subsequent quiz calls
        
    Example:
        session = start_student_session("user_123", "eco_101", "Indian Economy")
        quiz = get_next_quiz_batch(session)
    """
    if config is None:
        config = DEFAULT_QUIZ_CONFIG
    
    session_id = ADAPTIVE_ENGINE.create_session(
        user_id=user_id,
        pdf_source_id=pdf_id,
        topic=topic,
        mode="ADAPTIVE",
        initial_difficulty=initial_difficulty.upper()
    )
    
    # Store config in session for later use
    state = ADAPTIVE_ENGINE.get_session_state(session_id)
    state["config"] = config
    
    print(f"\n{'─'*50}")
    print(f"🎯 ADAPTIVE SESSION STARTED")
    print(f"{'─'*50}")
    print(f"   Session ID: {session_id}")
    print(f"   Topic: {topic}")
    print(f"   Starting Difficulty: {initial_difficulty.upper()}")
    print(f"   Mode: ADAPTIVE (difficulty auto-adjusts)")
    print(f"   Evaluation Interval: {config['evaluation_interval']} batches")
    print(f"{'─'*50}")
    
    return session_id


def start_grind_session(
    user_id: str,
    pdf_id: str,
    topic: str,
    difficulty: str = "EASY",
    dynamic_difficulty: bool = True,
    config: Dict[str, Any] = None
) -> str:
    """
    Start a GRIND mode session.
    
    In Grind mode:
    - Difficulty can be fixed or dynamic (slower adjustment)
    - Great for mastering a specific level
    - Streak tracking for motivation
    - Dynamic difficulty evaluated every N batches (default: 4)
    
    Args:
        user_id: User identifier
        pdf_id: PDF source identifier
        topic: Topic for quiz generation
        difficulty: Starting difficulty (EASY/MEDIUM/HARD)
        dynamic_difficulty: Whether to enable dynamic difficulty (default: True)
        config: Optional configuration overrides (from get_grind_config())
        
    Returns:
        session_id: Use this for subsequent quiz calls
        
    Example:
        session = start_grind_session("user_123", "eco_101", "GDP", "HARD")
        quiz = get_next_quiz_batch(session)
    """
    if config is None:
        config = get_grind_config(dynamic_enabled=dynamic_difficulty)
    
    session_id = ADAPTIVE_ENGINE.create_session(
        user_id=user_id,
        pdf_source_id=pdf_id,
        topic=topic,
        mode="GRIND",
        initial_difficulty=difficulty.upper()
    )
    
    # Store config in session for later use
    state = ADAPTIVE_ENGINE.get_session_state(session_id)
    state["config"] = config
    
    dynamic_str = "ON" if config.get("dynamic_enabled", True) else "OFF"
    
    print(f"\n{'─'*50}")
    print(f"🏋️ GRIND SESSION STARTED")
    print(f"{'─'*50}")
    print(f"   Session ID: {session_id}")
    print(f"   Topic: {topic}")
    print(f"   Starting Difficulty: {difficulty.upper()}")
    print(f"   Mode: GRIND (dynamic difficulty: {dynamic_str})")
    if config.get("dynamic_enabled", True):
        print(f"   Evaluation Interval: {config['evaluation_interval']} batches")
    print(f"{'─'*50}")
    
    return session_id


# ═══════════════════════════════════════════════════════════════════════════════
# QUIZ GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_next_quiz_batch(session_id: str, num_questions: int = 5):
    """
    Generate the next quiz batch based on current session state.
    
    Uses the current difficulty from the adaptive engine.
    For ADAPTIVE mode: difficulty may have changed from last batch.
    For GRIND mode: difficulty depends on dynamic_enabled setting.
    
    Args:
        session_id: Session identifier from start_*_session()
        num_questions: Number of questions to generate (default: 5)
        
    Returns:
        QuizOutput: Contains questions with options and explanations
        
    Example:
        quiz = get_next_quiz_batch(session_id)
        format_quiz_for_display(quiz)
    """
    state = ADAPTIVE_ENGINE.get_session_state(session_id)
    
    print(f"\n{'─'*50}")
    print(f"📝 GENERATING QUIZ")
    print(f"{'─'*50}")
    print(f"   Mode: {state['mode']}")
    print(f"   Difficulty: {state['current_difficulty']}")
    print(f"   Mastery: {state['mastery_score']:.2%}")
    print(f"   Streak: {state['streak']}")
    
    input_data = {
        "session_id": session_id,
        "pdf_source_id": state["pdf_source_id"],
        "current_difficulty": state["current_difficulty"],
        "topic": state["topic"],
        "num_questions": num_questions
    }
    
    result = agent.run_session(input_data)
    quiz = result.get('generated_quiz')
    
    if quiz:
        print(f"   ✓ Generated {len(quiz.questions)} questions")
    else:
        print(f"   ✗ Failed to generate quiz")
    print(f"{'─'*50}")
    
    return quiz


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT SUBMISSION
# ═══════════════════════════════════════════════════════════════════════════════

def submit_quiz_results(session_id: str, results: List[bool]) -> dict:
    """
    Submit quiz results and get feedback.
    
    For ADAPTIVE mode:
    - Difficulty evaluated every N batches (default: 2)
    - ≥80% correct → Level up
    - ≤40% correct → Level down
    - Updates mastery score
    
    For GRIND mode:
    - ≥80% correct → Streak increases
    - <80% correct → Streak resets
    - If dynamic_difficulty enabled: evaluated every N batches (default: 4)
    
    Args:
        session_id: Session identifier
        results: List of booleans (True = correct answer)
        
    Returns:
        Feedback dict with accuracy, mastery, difficulty changes, etc.
        
    Example:
        results = [True, True, False, True, True]  # 4/5 correct
        feedback = submit_quiz_results(session_id, results)
    """
    feedback = ADAPTIVE_ENGINE.process_batch_results(session_id, results)
    
    print(f"\n{'─'*50}")
    print(f"📊 QUIZ RESULTS")
    print(f"{'─'*50}")
    print(f"   Score: {feedback['correct']}/{feedback['total']} ({feedback['accuracy']*100:.0f}%)")
    print(f"   Mastery: {feedback['mastery']:.2%}")
    print(f"   Streak: {feedback['streak']}")
    
    if feedback['old_difficulty'] != feedback['new_difficulty']:
        print(f"   Difficulty: {feedback['old_difficulty']} → {feedback['new_difficulty']}")
    else:
        print(f"   Difficulty: {feedback['new_difficulty']} (unchanged)")
    
    print(f"\n   {feedback['message']}")
    print(f"{'─'*50}")
    
    return feedback


def get_session_stats(session_id: str) -> dict:
    """
    Get detailed statistics for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with session statistics:
        - session_id, mode, current_difficulty
        - mastery_score, current_streak, best_streak
        - total_quizzes, total_questions, total_correct
        - overall_accuracy, average_quiz_accuracy
        - topic, created_at
    """
    return ADAPTIVE_ENGINE.get_session_stats(session_id)


def list_active_sessions() -> List[str]:
    """
    List all active session IDs.
    
    Returns:
        List of session IDs
    """
    sessions = ADAPTIVE_ENGINE.list_sessions()
    return [s['session_id'] for s in sessions]


def delete_session(session_id: str) -> bool:
    """
    Delete a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        True if deleted, False if not found
    """
    return ADAPTIVE_ENGINE.delete_session(session_id)


# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def format_quiz_for_display(
    quiz_output,
    show_answers: bool = True,
    letters: List[str] = None
):
    """
    Format quiz for clean console display.
    
    Adds letter prefixes (a, b, c, d) at display time.
    Options are stored without prefixes in the quiz data.
    
    Args:
        quiz_output: QuizOutput from get_next_quiz_batch()
        show_answers: Whether to show correct answers (default: True)
        letters: Custom letter prefixes (default: ['a', 'b', 'c', 'd'])
        
    Example:
        quiz = get_next_quiz_batch(session_id)
        format_quiz_for_display(quiz)
    """
    if not quiz_output or not quiz_output.questions:
        print("\n⚠️ No quiz to display.")
        return
    
    if letters is None:
        letters = ['a', 'b', 'c', 'd']
    
    print(f"\n{'═'*60}")
    print(f"📝 QUIZ ({len(quiz_output.questions)} Questions)")
    print(f"{'═'*60}")
    
    for i, q in enumerate(quiz_output.questions, 1):
        print(f"\n{'─'*60}")
        print(f"Q{i}: {q.question}")
        print()
        
        # Display options with letter prefixes
        for j, opt in enumerate(q.options[:4]):
            # Clean any existing prefixes from option text
            clean_opt = _clean_option_text(opt)
            print(f"   {letters[j]}) {clean_opt}")
        
        if show_answers:
            # Find correct answer letter
            correct_letter = _find_correct_letter(q.options, q.correct_answer)
            print(f"\n   ✓ Answer: {correct_letter}) {q.correct_answer}")
            print(f"   📖 {q.explanation}")
    
    print(f"\n{'═'*60}")


def _clean_option_text(option: str) -> str:
    """Remove any existing prefixes from option text."""
    opt = option.strip()
    
    # Remove common prefixes like "A)", "1.", "(a)", etc.
    patterns = [
        r'^[A-Da-d][\.\)\:]?\s*',  # A. A) A:
        r'^[1-4][\.\)\:]?\s*',     # 1. 1) 1:
        r'^\([A-Da-d1-4]\)\s*',    # (A) (1)
    ]
    
    for pattern in patterns:
        opt = re.sub(pattern, '', opt)
    
    return opt.strip()


def _find_correct_letter(options: List[str], correct_answer: str) -> str:
    """Find the letter corresponding to the correct answer."""
    letters = ['a', 'b', 'c', 'd']
    correct_lower = correct_answer.lower().strip()
    
    for j, opt in enumerate(options[:4]):
        opt_clean = _clean_option_text(opt).lower()
        
        # Check for exact or partial match
        if opt_clean == correct_lower or correct_lower in opt_clean or opt_clean in correct_lower:
            return letters[j]
    
    return "?"


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_indexed_pdfs() -> List[str]:
    """
    Get list of all indexed PDF source IDs.
    
    Returns:
        List of PDF source IDs
    """
    return kb.get_all_pdf_sources()


def print_session_summary(session_id: str):
    """
    Print a formatted summary of session statistics.
    
    Args:
        session_id: Session identifier
    """
    stats = get_session_stats(session_id)
    
    print(f"\n{'═'*60}")
    print(f"📊 SESSION SUMMARY: {session_id}")
    print(f"{'═'*60}")
    print(f"   Mode: {stats['mode']}")
    print(f"   Topic: {stats['topic']}")
    print(f"   Current Difficulty: {stats['current_difficulty']}")
    print(f"{'─'*60}")
    print(f"   Total Quizzes: {stats['total_quizzes']}")
    print(f"   Total Questions: {stats['total_questions']}")
    print(f"   Correct Answers: {stats['total_correct']}")
    print(f"   Overall Accuracy: {stats['overall_accuracy']:.2%}")
    print(f"   Average Quiz Accuracy: {stats['average_quiz_accuracy']:.2%}")
    print(f"{'─'*60}")
    print(f"   Current Streak: {stats['current_streak']}")
    print(f"   Best Streak: {stats['best_streak']}")
    print(f"   Mastery Score: {stats['mastery_score']:.2%}")
    print(f"{'═'*60}")
