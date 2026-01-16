# backend/grind_mode.py

"""
Rooster-HackCrypt: Grind Mode Module

This module provides dedicated grind mode functionality with:
- Optional dynamic difficulty (slower interval than quiz mode)
- Streak tracking for motivation
- Detailed practice statistics
- All configuration parameterized

Default: Difficulty changes every 4 batches (vs 2 in quiz mode)
"""

from typing import List, Dict, Any, Optional
import random

from difficulty_engine import (
    apply_grind_difficulty,
    calculate_streak,
    calculate_mastery_score,
    get_grind_config,
    DEFAULT_GRIND_CONFIG
)


class GrindMode:
    """
    Grind Mode: Practice with optional dynamic difficulty and streak tracking.
    
    Unlike Adaptive mode, difficulty adjustment is:
    - Optional (can be disabled)
    - Slower (every 4 batches by default vs 2 in quiz mode)
    - Based on average performance over recent batches
    
    This is useful for:
    - Mastering a specific difficulty level
    - Building confidence before moving up
    - Targeted practice on weak areas
    """
    
    def __init__(
        self,
        agent,
        engine,
        config: Dict[str, Any] = None
    ):
        """
        Initialize Grind Mode.
        
        Args:
            agent: QuizAgent instance for generating quizzes
            engine: AdaptiveLogic engine for session management
            config: Grind mode configuration (from get_grind_config())
        """
        self.agent = agent
        self.engine = engine
        self.config = config if config is not None else DEFAULT_GRIND_CONFIG.copy()
        
        # Track recent accuracies per session for averaging
        self._session_accuracies: Dict[str, List[float]] = {}
    
    def start_grind_session(
        self,
        user_id: str,
        pdf_id: str,
        topic: str,
        difficulty: str = "EASY",
        dynamic_difficulty: bool = None,
        evaluation_interval: int = None,
        level_up_threshold: float = None,
        level_down_threshold: float = None,
        streak_threshold: float = None
    ) -> str:
        """
        Start a grind session with configurable difficulty behavior.
        
        Args:
            user_id: User identifier
            pdf_id: PDF source identifier
            topic: Topic for quiz generation
            difficulty: Starting difficulty level (EASY/MEDIUM/HARD)
            dynamic_difficulty: Whether difficulty can change (default: from config)
            evaluation_interval: Batches between difficulty evaluation (default: 4)
            level_up_threshold: Accuracy to level up (default: 0.8)
            level_down_threshold: Accuracy to level down (default: 0.4)
            streak_threshold: Accuracy to maintain streak (default: 0.8)
            
        Returns:
            session_id: New session identifier
        """
        # Build session config with overrides
        session_config = self.config.copy()
        if dynamic_difficulty is not None:
            session_config["dynamic_enabled"] = dynamic_difficulty
        if evaluation_interval is not None:
            session_config["evaluation_interval"] = evaluation_interval
        if level_up_threshold is not None:
            session_config["level_up_threshold"] = level_up_threshold
        if level_down_threshold is not None:
            session_config["level_down_threshold"] = level_down_threshold
        if streak_threshold is not None:
            session_config["streak_threshold"] = streak_threshold
        
        session_id = self.engine.create_session(
            user_id=user_id,
            pdf_source_id=pdf_id,
            topic=topic,
            mode="GRIND",
            initial_difficulty=difficulty.upper()
        )
        
        # Store config in session state
        state = self.engine.get_session_state(session_id)
        state["grind_config"] = session_config
        
        # Initialize accuracy tracking
        self._session_accuracies[session_id] = []
        
        dynamic_str = "ON" if session_config.get("dynamic_enabled", True) else "OFF"
        
        print(f"\n{'─'*50}")
        print(f"🏋️ GRIND SESSION STARTED")
        print(f"{'─'*50}")
        print(f"   Session ID: {session_id}")
        print(f"   Topic: {topic}")
        print(f"   Starting Difficulty: {difficulty.upper()}")
        print(f"   Dynamic Difficulty: {dynamic_str}")
        if session_config.get("dynamic_enabled", True):
            print(f"   Evaluation Interval: {session_config['evaluation_interval']} batches")
        print(f"{'─'*50}")
        
        return session_id
    
    def get_grind_quiz(
        self,
        session_id: str,
        num_questions: int = 5
    ):
        """
        Generate a quiz at the current difficulty level.
        
        Args:
            session_id: Session identifier
            num_questions: Number of questions (default: 5)
            
        Returns:
            QuizOutput with questions
        """
        state = self.engine.get_session_state(session_id)
        config = state.get("grind_config", self.config)
        
        dynamic_str = "dynamic" if config.get("dynamic_enabled", True) else "fixed"
        
        print(f"\n{'─'*50}")
        print(f"📝 GENERATING GRIND QUIZ")
        print(f"{'─'*50}")
        print(f"   Difficulty: {state['current_difficulty']} ({dynamic_str})")
        print(f"   Current Streak: {state['streak']}")
        print(f"   Mastery: {state['mastery_score']:.2%}")
        
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
    
    def submit_grind_results(
        self,
        session_id: str,
        results: List[bool]
    ) -> Dict[str, Any]:
        """
        Submit quiz results and update session state.
        
        For grind mode:
        - Streak updates based on performance
        - Difficulty may change if dynamic_enabled (every N batches)
        - Mastery score updates with difficulty weighting
        
        Args:
            session_id: Session identifier
            results: List of boolean results (True = correct)
            
        Returns:
            Feedback dictionary with streak, difficulty, and mastery info
        """
        state = self.engine.get_session_state(session_id)
        config = state.get("grind_config", self.config)
        
        # Calculate accuracy
        correct = sum(results)
        total = len(results)
        accuracy = correct / total if total > 0 else 0.0
        
        # Track accuracy for this session
        if session_id not in self._session_accuracies:
            self._session_accuracies[session_id] = []
        self._session_accuracies[session_id].append(accuracy)
        
        # Keep only recent accuracies for averaging
        max_history = config.get("evaluation_interval", 4) * 2
        if len(self._session_accuracies[session_id]) > max_history:
            self._session_accuracies[session_id] = self._session_accuracies[session_id][-max_history:]
        
        # Calculate streak
        streak_result = calculate_streak(
            accuracy=accuracy,
            current_streak=state["streak"],
            streak_threshold=config.get("streak_threshold", 0.8)
        )
        
        # Calculate mastery
        new_mastery = calculate_mastery_score(
            accuracy=accuracy,
            current_mastery=state["mastery_score"],
            current_difficulty=state["current_difficulty"],
            weight_new=config.get("mastery_weight", 0.3)
        )
        
        # Determine difficulty change
        old_difficulty = state["current_difficulty"]
        batch_count = len(state.get("history", [])) + 1
        
        difficulty_result = apply_grind_difficulty(
            recent_accuracies=self._session_accuracies[session_id],
            current_difficulty=old_difficulty,
            batch_count=batch_count,
            evaluation_interval=config.get("evaluation_interval", 4),
            level_up_threshold=config.get("level_up_threshold", 0.8),
            level_down_threshold=config.get("level_down_threshold", 0.4),
            dynamic_enabled=config.get("dynamic_enabled", True)
        )
        
        new_difficulty = difficulty_result["new_difficulty"]
        
        # Update state
        state["streak"] = streak_result["new_streak"]
        if streak_result["new_streak"] > state["best_streak"]:
            state["best_streak"] = streak_result["new_streak"]
        state["mastery_score"] = new_mastery
        state["current_difficulty"] = new_difficulty
        state["total_questions"] += total
        state["total_correct"] += correct
        
        # Add to history
        state["history"].append({
            "accuracy": accuracy,
            "difficulty": old_difficulty,
            "streak_before": state["streak"] - streak_result["new_streak"] if streak_result["streak_continued"] else state["streak"],
            "streak_after": streak_result["new_streak"]
        })
        
        # Build message
        if streak_result["streak_broken"]:
            message = f"💔 Streak broken! Starting fresh."
        elif streak_result["streak_continued"]:
            message = f"🔥 Streak: {streak_result['new_streak']}! Keep it going!"
        else:
            message = f"Keep practicing to build your streak!"
        
        if difficulty_result["difficulty_changed"]:
            message += f" Difficulty adjusted: {old_difficulty} → {new_difficulty}"
        
        feedback = {
            "session_id": session_id,
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
            "streak": streak_result["new_streak"],
            "streak_broken": streak_result["streak_broken"],
            "streak_continued": streak_result["streak_continued"],
            "mastery": new_mastery,
            "old_difficulty": old_difficulty,
            "new_difficulty": new_difficulty,
            "difficulty_changed": difficulty_result["difficulty_changed"],
            "difficulty_reason": difficulty_result["reason"],
            "message": message
        }
        
        print(f"\n{'─'*50}")
        print(f"📊 GRIND RESULTS")
        print(f"{'─'*50}")
        print(f"   Score: {correct}/{total} ({accuracy*100:.0f}%)")
        print(f"   Streak: {streak_result['new_streak']}")
        print(f"   Mastery: {new_mastery:.2%}")
        
        if difficulty_result["difficulty_changed"]:
            print(f"   Difficulty: {old_difficulty} → {new_difficulty}")
        else:
            print(f"   Difficulty: {new_difficulty} (unchanged)")
        
        print(f"\n   {message}")
        print(f"{'─'*50}")
        
        return feedback
    
    def get_grind_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed practice statistics.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Statistics dictionary
        """
        return self.engine.get_session_stats(session_id)
    
    def display_stats(self, session_id: str):
        """
        Display formatted statistics for a grind session.
        
        Args:
            session_id: Session identifier
        """
        stats = self.get_grind_stats(session_id)
        state = self.engine.get_session_state(session_id)
        config = state.get("grind_config", self.config)
        
        dynamic_str = "Dynamic" if config.get("dynamic_enabled", True) else "Fixed"
        
        print(f"\n{'═'*50}")
        print(f"📊 GRIND MODE STATISTICS")
        print(f"{'═'*50}")
        print(f"  Session: {stats['session_id']}")
        print(f"  Topic: {stats['topic']}")
        print(f"  Difficulty: {stats['current_difficulty']} ({dynamic_str})")
        print(f"  ")
        print(f"  🔥 Current Streak: {stats['current_streak']}")
        print(f"  🏆 Best Streak: {stats['best_streak']}")
        print(f"  📈 Mastery Score: {stats['mastery_score']:.2%}")
        print(f"  ")
        print(f"  📝 Total Quizzes: {stats['total_quizzes']}")
        print(f"  ❓ Total Questions: {stats['total_questions']}")
        print(f"  ✓ Total Correct: {stats['total_correct']}")
        print(f"  📊 Overall Accuracy: {stats['overall_accuracy']:.2%}")
        print(f"{'═'*50}")


# ═══════════════════════════════════════════════════════════════════════════════
# PRACTICE LOOP HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def grind_practice_loop(
    grind_mode: GrindMode,
    session_id: str,
    num_rounds: int = 3,
    simulate_performance: float = 0.8,
    questions_per_round: int = 5
):
    """
    Automated practice loop for demonstration or testing.
    
    Args:
        grind_mode: GrindMode instance
        session_id: Session identifier
        num_rounds: Number of quiz rounds (default: 3)
        simulate_performance: Probability of correct answer (default: 0.8)
        questions_per_round: Questions per quiz (default: 5)
    """
    print(f"\n{'═'*60}")
    print(f"🏋️ GRIND ZONE - {num_rounds} Rounds")
    print(f"{'═'*60}")
    
    state = grind_mode.engine.get_session_state(session_id)
    config = state.get("grind_config", grind_mode.config)
    
    dynamic_str = "dynamic" if config.get("dynamic_enabled", True) else "fixed"
    print(f"  Difficulty: {state['current_difficulty']} ({dynamic_str})")
    print(f"  Topic: {state['topic']}")
    
    initial_difficulty = state["current_difficulty"]
    
    for round_num in range(1, num_rounds + 1):
        print(f"\n{'─'*40}")
        print(f"📝 Round {round_num}/{num_rounds}")
        print(f"{'─'*40}")
        
        quiz = grind_mode.get_grind_quiz(session_id, num_questions=questions_per_round)
        
        if not quiz:
            print("❌ Failed to generate quiz")
            continue
        
        # Simulate answers based on performance probability
        results = [random.random() < simulate_performance for _ in quiz.questions]
        
        grind_mode.submit_grind_results(session_id, results)
    
    # Final stats
    print(f"\n{'═'*60}")
    print(f"🏁 GRIND SESSION COMPLETE")
    print(f"{'═'*60}")
    grind_mode.display_stats(session_id)


def quick_grind_demo(
    agent,
    engine,
    pdf_id: str,
    topic: str,
    difficulty: str = "MEDIUM",
    dynamic_difficulty: bool = True,
    num_rounds: int = 3
):
    """
    Quick demo of grind mode functionality.
    
    Args:
        agent: QuizAgent instance
        engine: AdaptiveLogic engine
        pdf_id: PDF source identifier
        topic: Topic for quizzes
        difficulty: Starting difficulty (default: MEDIUM)
        dynamic_difficulty: Enable dynamic difficulty (default: True)
        num_rounds: Number of quiz rounds (default: 3)
        
    Returns:
        session_id: The demo session ID
    """
    grind = GrindMode(agent, engine)
    
    print(f"\n{'═'*60}")
    print(f"🏋️ QUICK GRIND DEMO")
    print(f"{'═'*60}")
    
    session = grind.start_grind_session(
        user_id="demo_user",
        pdf_id=pdf_id,
        topic=topic,
        difficulty=difficulty,
        dynamic_difficulty=dynamic_difficulty
    )
    
    grind_practice_loop(grind, session, num_rounds=num_rounds, simulate_performance=0.8)
    
    return session
