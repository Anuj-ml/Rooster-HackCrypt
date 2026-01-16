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

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Load environment variables
load_dotenv()

# --- Model Configuration ---
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# --- Import Custom Modules ---
from src.rag.storage import KnowledgeBase
from src.agents.agent import QuizAgent
from src.core.logic_engine import AdaptiveLogic
from src.core.difficulty_engine import (
    DEFAULT_QUIZ_CONFIG,
    DEFAULT_GRIND_CONFIG,
    get_quiz_config,
    get_grind_config
)


class QuizServiceModelFactory:
    """Factory for creating and caching ML model instances for quiz service."""
    
    _llm_model = None
    _embedding_model = None
    
    @classmethod
    def get_llm_model(cls):
        """Get or create the LLM model instance."""
        if cls._llm_model is None:
            cls._llm_model = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0,
                groq_api_key=os.getenv("GROQ_API_KEY")
            )
        return cls._llm_model
    
    @classmethod
    def get_embedding_model(cls):
        """Get or create the embedding model instance."""
        if cls._embedding_model is None:
            # Use backend directory's data folder
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cache_dir = os.path.join(backend_dir, "data", "embeddings_cache")
            os.makedirs(cache_dir, exist_ok=True)
            cls._embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-MiniLM-L3-v2",
                cache_folder=cache_dir,
                model_kwargs={'local_files_only': True}
            )
        return cls._embedding_model


class QuizService:
    """
    Service for quiz generation and session management.
    
    Handles:
    - Adaptive and Grind mode sessions
    - Quiz generation via QuizAgent
    - Result submission and feedback
    - Session statistics
    """
    
    _instance = None
    
    def __init__(
        self,
        knowledge_base: Optional[KnowledgeBase] = None,
        agent: Optional[QuizAgent] = None,
        adaptive_engine: Optional[AdaptiveLogic] = None
    ):
        """
        Initialize the quiz service.
        
        Args:
            knowledge_base: Optional KnowledgeBase instance
            agent: Optional QuizAgent instance
            adaptive_engine: Optional AdaptiveLogic instance
        """
        self._kb = knowledge_base
        self._agent = agent
        self._adaptive_engine = adaptive_engine
    
    @property
    def kb(self) -> KnowledgeBase:
        """Lazy initialization of knowledge base."""
        if self._kb is None:
            self._kb = KnowledgeBase(
                embedding_model=QuizServiceModelFactory.get_embedding_model()
            )
        return self._kb
    
    @property
    def agent(self) -> QuizAgent:
        """Lazy initialization of quiz agent."""
        if self._agent is None:
            self._agent = QuizAgent(
                llm=QuizServiceModelFactory.get_llm_model(),
                knowledge_base=self.kb
            )
        return self._agent
    
    @property
    def adaptive_engine(self) -> AdaptiveLogic:
        """Lazy initialization of adaptive logic engine."""
        if self._adaptive_engine is None:
            self._adaptive_engine = AdaptiveLogic()
        return self._adaptive_engine
    
    def start_student_session(
        self,
        user_id: str,
        pdf_id: str,
        topic: str,
        initial_difficulty: str = "EASY",
        config: Dict[str, Any] = None
    ) -> str:
        """
        Start an ADAPTIVE learning session.
        
        Args:
            user_id: User identifier
            pdf_id: PDF source identifier
            topic: Topic for quiz generation
            initial_difficulty: Starting difficulty (EASY/MEDIUM/HARD)
            config: Optional configuration overrides
            
        Returns:
            session_id: Use this for subsequent quiz calls
        """
        if config is None:
            config = DEFAULT_QUIZ_CONFIG
        
        session_id = self.adaptive_engine.create_session(
            user_id=user_id,
            pdf_source_id=pdf_id,
            topic=topic,
            mode="ADAPTIVE",
            initial_difficulty=initial_difficulty.upper()
        )
        
        # Store config in session for later use
        state = self.adaptive_engine.get_session_state(session_id)
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
        self,
        user_id: str,
        pdf_id: str,
        topic: str,
        difficulty: str = "EASY",
        dynamic_difficulty: bool = True,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Start a GRIND mode session.
        
        Args:
            user_id: User identifier
            pdf_id: PDF source identifier
            topic: Topic for quiz generation
            difficulty: Starting difficulty (EASY/MEDIUM/HARD)
            dynamic_difficulty: Whether to enable dynamic difficulty
            config: Optional configuration overrides
            
        Returns:
            session_id: Use this for subsequent quiz calls
        """
        if config is None:
            config = get_grind_config(dynamic_enabled=dynamic_difficulty)
        
        session_id = self.adaptive_engine.create_session(
            user_id=user_id,
            pdf_source_id=pdf_id,
            topic=topic,
            mode="GRIND",
            initial_difficulty=difficulty.upper()
        )
        
        # Store config in session for later use
        state = self.adaptive_engine.get_session_state(session_id)
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
    
    def get_next_quiz_batch(self, session_id: str, num_questions: int = 5):
        """
        Generate the next quiz batch based on current session state.
        
        Args:
            session_id: Session identifier
            num_questions: Number of questions to generate
            
        Returns:
            QuizOutput: Contains questions with options and explanations
        """
        state = self.adaptive_engine.get_session_state(session_id)
        
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
        
        result = self.agent.run_session(input_data)
        quiz = result.get('generated_quiz')
        
        if quiz:
            print(f"   ✓ Generated {len(quiz.questions)} questions")
        else:
            print(f"   ✗ Failed to generate quiz")
        print(f"{'─'*50}")
        
        return quiz
    
    def submit_quiz_results(self, session_id: str, results: List[bool]) -> dict:
        """
        Submit quiz results and get feedback.
        
        Args:
            session_id: Session identifier
            results: List of booleans (True = correct answer)
            
        Returns:
            Feedback dict with accuracy, mastery, difficulty changes, etc.
        """
        feedback = self.adaptive_engine.process_batch_results(session_id, results)
        
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
    
    def get_session_stats(self, session_id: str) -> dict:
        """Get detailed statistics for a session."""
        return self.adaptive_engine.get_session_stats(session_id)
    
    def list_active_sessions(self) -> List[str]:
        """List all active session IDs."""
        sessions = self.adaptive_engine.list_sessions()
        return [s['session_id'] for s in sessions]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        return self.adaptive_engine.delete_session(session_id)
    
    def get_indexed_pdfs(self) -> List[str]:
        """Get list of all indexed PDF source IDs."""
        return self.kb.get_all_pdf_sources()
    
    def print_session_summary(self, session_id: str):
        """Print a formatted summary of session statistics."""
        stats = self.get_session_stats(session_id)
        
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
    
    @classmethod
    def get_instance(cls) -> 'QuizService':
        """Get the singleton instance of QuizService."""
        if cls._instance is None:
            cls._instance = QuizService()
        return cls._instance


class QuizDisplayHelper:
    """Helper class for quiz display formatting."""
    
    DEFAULT_LETTERS = ['a', 'b', 'c', 'd']
    
    @staticmethod
    def clean_option_text(option: str) -> str:
        """Remove any existing prefixes from option text."""
        opt = option.strip()
        
        patterns = [
            r'^[A-Da-d][\.\)\:]?\s*',
            r'^[1-4][\.\)\:]?\s*',
            r'^\([A-Da-d1-4]\)\s*',
        ]
        
        for pattern in patterns:
            opt = re.sub(pattern, '', opt)
        
        return opt.strip()
    
    @staticmethod
    def find_correct_letter(options: List[str], correct_answer: str) -> str:
        """Find the letter corresponding to the correct answer."""
        letters = QuizDisplayHelper.DEFAULT_LETTERS
        correct_lower = correct_answer.lower().strip()
        
        for j, opt in enumerate(options[:4]):
            opt_clean = QuizDisplayHelper.clean_option_text(opt).lower()
            
            if opt_clean == correct_lower or correct_lower in opt_clean or opt_clean in correct_lower:
                return letters[j]
        
        return "?"
    
    @classmethod
    def format_quiz_for_display(
        cls,
        quiz_output,
        show_answers: bool = True,
        letters: List[str] = None
    ):
        """Format quiz for clean console display."""
        if not quiz_output or not quiz_output.questions:
            print("\n⚠️ No quiz to display.")
            return
        
        if letters is None:
            letters = cls.DEFAULT_LETTERS
        
        print(f"\n{'═'*60}")
        print(f"📝 QUIZ ({len(quiz_output.questions)} Questions)")
        print(f"{'═'*60}")
        
        for i, q in enumerate(quiz_output.questions, 1):
            print(f"\n{'─'*60}")
            print(f"Q{i}: {q.question}")
            print()
            
            # Ensure we have exactly 4 options
            opts = q.options[:4]
            while len(opts) < 4:
                opts.append("[Option not generated - please skip]")
            
            for j, opt in enumerate(opts):
                clean_opt = cls.clean_option_text(opt)
                print(f"   {letters[j]}) {clean_opt}")
            
            if show_answers:
                correct_letter = cls.find_correct_letter(q.options, q.correct_answer)
                print(f"\n   ✓ Answer: {correct_letter}) {q.correct_answer}")
                print(f"   📖 {q.explanation}")
        
        print(f"\n{'═'*60}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL FUNCTIONS (Backward Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

def get_llm_model():
    """Get the LLM model instance."""
    return QuizServiceModelFactory.get_llm_model()


def get_embedding_model():
    """Get the embedding model instance."""
    return QuizServiceModelFactory.get_embedding_model()


def get_kb():
    """Get the knowledge base instance."""
    return QuizService.get_instance().kb


def get_agent():
    """Get the quiz agent instance."""
    return QuizService.get_instance().agent


def get_adaptive_engine():
    """Get the adaptive logic engine instance."""
    return QuizService.get_instance().adaptive_engine


# Backward compatibility aliases
kb = get_kb
agent = get_agent
ADAPTIVE_ENGINE = get_adaptive_engine


def start_student_session(
    user_id: str,
    pdf_id: str,
    topic: str,
    initial_difficulty: str = "EASY",
    config: Dict[str, Any] = None
) -> str:
    """Start an ADAPTIVE learning session."""
    return QuizService.get_instance().start_student_session(
        user_id, pdf_id, topic, initial_difficulty, config
    )


def start_grind_session(
    user_id: str,
    pdf_id: str,
    topic: str,
    difficulty: str = "EASY",
    dynamic_difficulty: bool = True,
    config: Dict[str, Any] = None
) -> str:
    """Start a GRIND mode session."""
    return QuizService.get_instance().start_grind_session(
        user_id, pdf_id, topic, difficulty, dynamic_difficulty, config
    )


def get_next_quiz_batch(session_id: str, num_questions: int = 5):
    """Generate the next quiz batch."""
    return QuizService.get_instance().get_next_quiz_batch(session_id, num_questions)


def submit_quiz_results(session_id: str, results: List[bool]) -> dict:
    """Submit quiz results and get feedback."""
    return QuizService.get_instance().submit_quiz_results(session_id, results)


def get_session_stats(session_id: str) -> dict:
    """Get detailed statistics for a session."""
    return QuizService.get_instance().get_session_stats(session_id)


def list_active_sessions() -> List[str]:
    """List all active session IDs."""
    return QuizService.get_instance().list_active_sessions()


def delete_session(session_id: str) -> bool:
    """Delete a session."""
    return QuizService.get_instance().delete_session(session_id)


def format_quiz_for_display(
    quiz_output,
    show_answers: bool = True,
    letters: List[str] = None
):
    """Format quiz for clean console display."""
    QuizDisplayHelper.format_quiz_for_display(quiz_output, show_answers, letters)


def _clean_option_text(option: str) -> str:
    """Remove any existing prefixes from option text."""
    return QuizDisplayHelper.clean_option_text(option)


def _find_correct_letter(options: List[str], correct_answer: str) -> str:
    """Find the letter corresponding to the correct answer."""
    return QuizDisplayHelper.find_correct_letter(options, correct_answer)


def get_indexed_pdfs() -> List[str]:
    """Get list of all indexed PDF source IDs."""
    return QuizService.get_instance().get_indexed_pdfs()


def print_session_summary(session_id: str):
    """Print a formatted summary of session statistics."""
    QuizService.get_instance().print_session_summary(session_id)
