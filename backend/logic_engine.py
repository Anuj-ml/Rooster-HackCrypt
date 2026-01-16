# backend/logic_engine.py

"""
Logic Engine: Central session management and adaptive difficulty adjustment.
Supports both ADAPTIVE (auto-adjust) and GRIND (fixed difficulty) modes.
"""

import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime


class AdaptiveLogic:
    """
    Central engine for session management and adaptive difficulty.
    
    Features:
    - In-memory session state storage
    - Difficulty progression logic (EASY → MEDIUM → HARD)
    - Mastery score calculation (70% history + 30% recent)
    - Streak tracking for grind mode
    - Dual mode support (ADAPTIVE vs GRIND)
    """
    
    DIFFICULTY_LEVELS = ["EASY", "MEDIUM", "HARD"]
    
    def __init__(self):
        """Initialize the adaptive logic engine."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        print("✓ AdaptiveLogic engine initialized")
    
    def create_session(
        self, 
        user_id: str, 
        pdf_source_id: str, 
        topic: str,
        mode: str = "ADAPTIVE",
        initial_difficulty: str = "EASY"
    ) -> str:
        """
        Create a new learning session.
        
        Args:
            user_id: Unique identifier for the user
            pdf_source_id: ID of the indexed PDF
            topic: Topic for quiz generation
            mode: "ADAPTIVE" (auto-adjust) or "GRIND" (fixed)
            initial_difficulty: Starting difficulty level
            
        Returns:
            session_id: Unique session identifier
        """
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        
        # Validate mode
        if mode not in ["ADAPTIVE", "GRIND"]:
            raise ValueError(f"Invalid mode: {mode}. Use 'ADAPTIVE' or 'GRIND'")
        
        # Validate difficulty
        if initial_difficulty.upper() not in self.DIFFICULTY_LEVELS:
            raise ValueError(f"Invalid difficulty: {initial_difficulty}")
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "pdf_source_id": pdf_source_id,
            "topic": topic,
            "mode": mode.upper(),
            "current_difficulty": initial_difficulty.upper(),
            "mastery_score": 0.0,
            "streak": 0,
            "best_streak": 0,
            "history": [],
            "created_at": datetime.now().isoformat(),
            "total_questions": 0,
            "total_correct": 0
        }
        
        return session_id
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve session state.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session state dictionary
            
        Raises:
            ValueError: If session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all sessions, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of session states
        """
        if user_id:
            return [s for s in self.sessions.values() if s["user_id"] == user_id]
        return list(self.sessions.values())
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def process_batch_results(
        self, 
        session_id: str, 
        results: List[bool]
    ) -> Dict[str, Any]:
        """
        Process quiz results and update session state.
        
        For ADAPTIVE mode: Difficulty may change based on accuracy.
        For GRIND mode: Only streak and mastery update, difficulty stays fixed.
        
        Args:
            session_id: Session identifier
            results: List of boolean results (True = correct)
            
        Returns:
            Feedback dictionary with accuracy, mastery, difficulty changes, etc.
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        state = self.sessions[session_id]
        
        # Calculate accuracy
        if not results:
            accuracy = 0.0
        else:
            accuracy = sum(results) / len(results)
        
        # Update totals
        state["total_questions"] += len(results)
        state["total_correct"] += sum(results)
        
        # Update history
        state["history"].append({
            "accuracy": accuracy,
            "difficulty": state["current_difficulty"],
            "num_questions": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
        # Update mastery (weighted average: 70% history + 30% recent)
        old_mastery = state["mastery_score"]
        state["mastery_score"] = (old_mastery * 0.7) + (accuracy * 0.3)
        
        # Prepare feedback
        feedback = {
            "accuracy": accuracy,
            "correct": sum(results),
            "total": len(results),
            "mastery": state["mastery_score"],
            "old_difficulty": state["current_difficulty"],
            "new_difficulty": state["current_difficulty"],
            "streak": state["streak"],
            "best_streak": state["best_streak"],
            "mode": state["mode"],
            "message": ""
        }
        
        # Apply mode-specific logic
        if state["mode"] == "ADAPTIVE":
            feedback = self._apply_adaptive_logic(state, accuracy, feedback)
        else:  # GRIND mode
            feedback = self._apply_grind_logic(state, accuracy, feedback)
        
        # Update best streak
        if state["streak"] > state["best_streak"]:
            state["best_streak"] = state["streak"]
            feedback["best_streak"] = state["best_streak"]
        
        return feedback
    
    def _apply_adaptive_logic(
        self, 
        state: Dict[str, Any], 
        accuracy: float,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply adaptive difficulty adjustment.
        
        Rules:
        - accuracy >= 0.8: Level up (if not at HARD)
        - accuracy <= 0.4: Level down (if not at EASY)
        - Otherwise: Stay at current level
        """
        current_idx = self.DIFFICULTY_LEVELS.index(state["current_difficulty"])
        
        if accuracy >= 0.8:
            # Good performance
            state["streak"] += 1
            
            if current_idx < 2:  # Not at HARD yet
                # Level up
                state["current_difficulty"] = self.DIFFICULTY_LEVELS[current_idx + 1]
                feedback["new_difficulty"] = state["current_difficulty"]
                feedback["message"] = f"🎉 Excellent! Leveling up to {state['current_difficulty']}!"
            else:
                # Already at HARD
                feedback["message"] = f"🏆 Outstanding! You've mastered {state['current_difficulty']} level!"
                
        elif accuracy <= 0.4:
            # Poor performance
            state["streak"] = 0
            
            if current_idx > 0:  # Not at EASY yet
                # Level down
                state["current_difficulty"] = self.DIFFICULTY_LEVELS[current_idx - 1]
                feedback["new_difficulty"] = state["current_difficulty"]
                feedback["message"] = f"📉 Moving to {state['current_difficulty']} for more practice."
            else:
                # Already at EASY
                feedback["message"] = f"💪 Keep practicing at {state['current_difficulty']}. You'll improve!"
        else:
            # Moderate performance (40% < accuracy < 80%)
            if accuracy >= 0.6:
                state["streak"] += 1
                feedback["message"] = f"📊 Good job! Stay at {state['current_difficulty']} to strengthen skills."
            else:
                state["streak"] = 0
                feedback["message"] = f"📚 Keep studying! Practice makes perfect."
        
        feedback["streak"] = state["streak"]
        return feedback
    
    def _apply_grind_logic(
        self, 
        state: Dict[str, Any], 
        accuracy: float,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply grind mode logic.
        
        In GRIND mode:
        - Difficulty NEVER changes
        - Streak builds on >= 80% accuracy
        - Streak resets on < 80% accuracy
        """
        if accuracy >= 0.8:
            state["streak"] += 1
            if state["streak"] >= 5:
                feedback["message"] = f"🔥🔥 UNSTOPPABLE! Streak: {state['streak']}!"
            elif state["streak"] >= 3:
                feedback["message"] = f"🔥 On fire! Streak: {state['streak']}"
            else:
                feedback["message"] = f"✨ Nice! Streak: {state['streak']}"
        else:
            old_streak = state["streak"]
            state["streak"] = 0
            if old_streak >= 3:
                feedback["message"] = f"💔 Streak broken ({old_streak}). Keep grinding at {state['current_difficulty']}!"
            else:
                feedback["message"] = f"💪 Keep grinding at {state['current_difficulty']}!"
        
        feedback["streak"] = state["streak"]
        # Difficulty NEVER changes in GRIND mode
        feedback["new_difficulty"] = state["current_difficulty"]
        return feedback
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Detailed statistics dictionary
        """
        state = self.get_session_state(session_id)
        
        # Calculate average accuracy from history
        if state["history"]:
            avg_accuracy = sum(h["accuracy"] for h in state["history"]) / len(state["history"])
        else:
            avg_accuracy = 0.0
        
        # Calculate overall accuracy
        if state["total_questions"] > 0:
            overall_accuracy = state["total_correct"] / state["total_questions"]
        else:
            overall_accuracy = 0.0
        
        return {
            "session_id": session_id,
            "mode": state["mode"],
            "current_difficulty": state["current_difficulty"],
            "mastery_score": state["mastery_score"],
            "current_streak": state["streak"],
            "best_streak": state["best_streak"],
            "total_quizzes": len(state["history"]),
            "total_questions": state["total_questions"],
            "total_correct": state["total_correct"],
            "overall_accuracy": overall_accuracy,
            "average_quiz_accuracy": avg_accuracy,
            "topic": state["topic"],
            "created_at": state["created_at"]
        }


# Singleton instance for global access
_engine_instance = None

def get_engine() -> AdaptiveLogic:
    """Get or create the singleton AdaptiveLogic instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AdaptiveLogic()
    return _engine_instance
