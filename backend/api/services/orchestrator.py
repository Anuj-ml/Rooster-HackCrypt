# backend/api/services/orchestrator.py

"""
Service orchestration layer.
Wraps existing backend services with async-friendly interfaces for FastAPI.
"""

import asyncio
from typing import Dict, Any, List, Optional
from functools import lru_cache

# Import existing backend services
from src.rag.ingestion_main import (
    IngestionService,
    upload_material as _upload_material,
    get_knowledge_base as _get_knowledge_base
)
from src.features.quiz_generation_main import (
    QuizService,
    start_student_session as _start_student_session,
    start_grind_session as _start_grind_session,
    get_next_quiz_batch as _get_next_quiz_batch,
    submit_quiz_results as _submit_quiz_results,
    get_session_stats as _get_session_stats,
    list_active_sessions as _list_active_sessions,
    delete_session as _delete_session
)
from src.loaders.youtube_loader import YouTubeLoader


class IngestionOrchestrator:
    """
    Orchestrates document ingestion operations.
    Provides async wrappers around synchronous backend services.
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self._youtube_loader = YouTubeLoader()
    
    async def ingest_pdf(
        self, 
        file_path: str, 
        source_id: str
    ) -> Dict[str, Any]:
        """
        Ingest a PDF file into the knowledge base.
        
        Args:
            file_path: Path to the PDF file
            source_id: Unique identifier for this source
        
        Returns:
            Dict with source_id, num_documents, num_propositions, success
        """
        # Run synchronous operation in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: _upload_material(
                material_type="PDF",
                content=file_path,
                source_id=source_id
            )
        )
        return result
    
    async def ingest_youtube(
        self, 
        url: str, 
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest a YouTube video transcript.
        
        Args:
            url: YouTube video URL
            source_id: Optional custom identifier (auto-generated if not provided)
        
        Returns:
            Dict with source_id, num_documents, num_propositions, success
        """
        # Extract video ID for auto source_id
        if not source_id:
            video_id = self._youtube_loader.extract_video_id(url)
            source_id = f"youtube_{video_id}" if video_id else "youtube_video"
        
        # Run synchronous operation in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: _upload_material(
                material_type="YOUTUBE",
                content=url,
                source_id=source_id
            )
        )
        return result
    
    async def ingest_syllabus(
        self, 
        topic: str, 
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate and ingest syllabus content for a topic.
        
        Args:
            topic: Topic to generate content for
            source_id: Optional custom identifier (auto-generated if not provided)
        
        Returns:
            Dict with source_id, num_documents, num_propositions, success
        """
        # Generate source_id if not provided
        if not source_id:
            clean_topic = "".join(c if c.isalnum() or c in "_-" else "_" for c in topic.lower())
            source_id = f"syllabus_{clean_topic[:30]}"
        
        # Run synchronous operation in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: _upload_material(
                material_type="SYLLABUS",
                content=topic,
                source_id=source_id
            )
        )
        return result


class QuizOrchestrator:
    """
    Orchestrates quiz and session operations.
    Provides async wrappers around synchronous backend services.
    """
    
    async def create_adaptive_session(
        self,
        user_id: str,
        source_id: str,
        topic: str,
        initial_difficulty: str
    ) -> Dict[str, Any]:
        """
        Create a new adaptive learning session.
        
        Args:
            user_id: User identifier
            source_id: Material source identifier
            topic: Quiz topic
            initial_difficulty: Starting difficulty level
        
        Returns:
            Dict with session_id
        """
        loop = asyncio.get_event_loop()
        session_id = await loop.run_in_executor(
            None,
            lambda: _start_student_session(
                user_id=user_id,
                pdf_id=source_id,
                topic=topic,
                initial_difficulty=initial_difficulty
            )
        )
        return {"session_id": session_id}
    
    async def create_grind_session(
        self,
        user_id: str,
        source_id: str,
        topic: str,
        difficulty: str,
        dynamic_difficulty: bool
    ) -> Dict[str, Any]:
        """
        Create a new grind mode session.
        
        Args:
            user_id: User identifier
            source_id: Material source identifier
            topic: Quiz topic
            difficulty: Fixed difficulty level
            dynamic_difficulty: Whether to slowly adjust difficulty
        
        Returns:
            Dict with session_id
        """
        loop = asyncio.get_event_loop()
        session_id = await loop.run_in_executor(
            None,
            lambda: _start_grind_session(
                user_id=user_id,
                pdf_id=source_id,
                topic=topic,
                difficulty=difficulty,
                dynamic_difficulty=dynamic_difficulty
            )
        )
        return {"session_id": session_id}
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active sessions with metadata.
        
        Returns:
            List of session info dictionaries
        """
        loop = asyncio.get_event_loop()
        session_ids = await loop.run_in_executor(None, _list_active_sessions)
        
        sessions = []
        for sid in session_ids:
            try:
                stats = await loop.run_in_executor(
                    None, 
                    lambda s=sid: _get_session_stats(s)
                )
                sessions.append({
                    "session_id": sid,
                    "user_id": stats.get("user_id", "unknown"),
                    "source_id": stats.get("pdf_source_id", "unknown"),
                    "topic": stats.get("topic", "unknown"),
                    "mode": stats.get("mode", "ADAPTIVE"),
                    "current_difficulty": stats.get("current_difficulty", "EASY")
                })
            except Exception:
                sessions.append({
                    "session_id": sid,
                    "user_id": "unknown",
                    "source_id": "unknown",
                    "topic": "unknown",
                    "mode": "UNKNOWN",
                    "current_difficulty": "UNKNOWN"
                })
        
        return sessions
    
    async def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed statistics for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dict with session statistics or None if not found
        """
        loop = asyncio.get_event_loop()
        try:
            stats = await loop.run_in_executor(
                None,
                lambda: _get_session_stats(session_id)
            )
            
            if not stats:
                return None
            
            return {
                "session_id": session_id,
                "mode": stats.get("mode", "ADAPTIVE"),
                "current_difficulty": stats.get("current_difficulty", "EASY"),
                "total_questions": stats.get("total_questions", 0),
                "correct_answers": stats.get("correct_answers", 0),
                "mastery_score": stats.get("mastery_score", 0.0),
                "streak": stats.get("streak", 0),
                "difficulty_history": stats.get("difficulty_history", [])
            }
        except Exception:
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if deleted, False if not found
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: _delete_session(session_id)
        )
    
    async def generate_quiz(
        self, 
        session_id: str, 
        num_questions: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a quiz for the session.
        
        Args:
            session_id: Session identifier
            num_questions: Number of questions to generate
        
        Returns:
            Dict with questions and difficulty, or None if failed
        """
        loop = asyncio.get_event_loop()
        
        # Get current difficulty
        stats = await self.get_session_stats(session_id)
        if not stats:
            return None
        
        difficulty = stats.get("current_difficulty", "EASY")
        
        # Generate quiz
        quiz = await loop.run_in_executor(
            None,
            lambda: _get_next_quiz_batch(session_id, num_questions)
        )
        
        if not quiz or not quiz.questions:
            return None
        
        return {
            "questions": quiz.questions,
            "difficulty": difficulty
        }
    
    async def submit_results(
        self, 
        session_id: str, 
        answers: List[bool]
    ) -> Optional[Dict[str, Any]]:
        """
        Submit quiz answers and get feedback.
        
        Args:
            session_id: Session identifier
            answers: List of boolean results (True=correct)
        
        Returns:
            Dict with feedback and updated stats
        """
        loop = asyncio.get_event_loop()
        
        # Get stats before submission
        stats_before = await self.get_session_stats(session_id)
        if not stats_before:
            return None
        
        difficulty_before = stats_before.get("current_difficulty", "EASY")
        
        # Submit results
        result = await loop.run_in_executor(
            None,
            lambda: _submit_quiz_results(session_id, answers)
        )
        
        # Get stats after submission
        stats_after = await self.get_session_stats(session_id)
        
        # Calculate score
        correct_count = sum(answers)
        total_count = len(answers)
        score_pct = (correct_count / total_count * 100) if total_count > 0 else 0
        
        # Check if difficulty changed
        new_difficulty = stats_after.get("current_difficulty", difficulty_before) if stats_after else difficulty_before
        difficulty_changed = new_difficulty != difficulty_before
        
        # Generate feedback message
        if score_pct >= 80:
            feedback = "Excellent work! You're mastering this material."
        elif score_pct >= 60:
            feedback = "Good job! Keep practicing to improve further."
        elif score_pct >= 40:
            feedback = "You're making progress. Review the material and try again."
        else:
            feedback = "This topic needs more study. Don't give up!"
        
        if difficulty_changed:
            if new_difficulty > difficulty_before:
                feedback += f" 📈 Difficulty increased to {new_difficulty}!"
            else:
                feedback += f" 📉 Difficulty adjusted to {new_difficulty}."
        
        return {
            "correct_count": correct_count,
            "total_count": total_count,
            "score_percentage": round(score_pct, 1),
            "new_difficulty": new_difficulty,
            "mastery_score": stats_after.get("mastery_score", 0.0) if stats_after else 0.0,
            "streak": stats_after.get("streak", 0) if stats_after else 0,
            "difficulty_changed": difficulty_changed,
            "feedback_message": feedback
        }


# Singleton instances
_ingestion_orchestrator: Optional[IngestionOrchestrator] = None
_quiz_orchestrator: Optional[QuizOrchestrator] = None


def get_ingestion_orchestrator() -> IngestionOrchestrator:
    """Get or create the IngestionOrchestrator singleton."""
    global _ingestion_orchestrator
    if _ingestion_orchestrator is None:
        _ingestion_orchestrator = IngestionOrchestrator()
    return _ingestion_orchestrator


def get_quiz_orchestrator() -> QuizOrchestrator:
    """Get or create the QuizOrchestrator singleton."""
    global _quiz_orchestrator
    if _quiz_orchestrator is None:
        _quiz_orchestrator = QuizOrchestrator()
    return _quiz_orchestrator
