"""
Room Manager for Competitive Multiplayer

Handles room creation, quiz generation, answer validation, and scoring logic.
"""

import asyncio
import string
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from .state_manager import GlobalState, get_global_state


class RoomManager:
    """
    Manages multiplayer game rooms.
    
    Responsibilities:
    - Create rooms with pre-generated quizzes
    - Validate answers and calculate scores
    - Manage leaderboards
    - Handle game flow
    """
    
    def __init__(self, global_state: GlobalState = None):
        """
        Initialize room manager.
        
        Args:
            global_state: Global state instance (injected for testing)
        """
        self.state = global_state or get_global_state()
    
    @staticmethod
    def generate_room_code(length: int = 6) -> str:
        """
        Generate a unique room code.
        
        Args:
            length: Code length (default 6)
            
        Returns:
            Random alphanumeric code
        """
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=length))
    
    async def create_room(
        self,
        host_id: str,
        topic: str,
        pdf_source_id: str,
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """
        Create a new multiplayer room with pre-generated quiz.
        
        This immediately generates a quiz using the QuizAgent so all players
        get the same questions. The quiz is stored in the room state.
        
        Args:
            host_id: User ID of the room creator
            topic: Quiz topic (can be "default" for full source)
            pdf_source_id: Source material ID
            num_questions: Number of questions to generate
            
        Returns:
            Room data with room_code, quiz_data, etc.
            
        Raises:
            ValueError: If quiz generation fails
        """
        # Import here to avoid circular dependency
        from src.agents.agent import QuizAgent
        from src.rag.ingestion_main import get_knowledge_base
        from src.models.schemas import AgentState
        from src.models.model_factory import ModelFactory
        
        # Generate unique room code
        room_code = self.generate_room_code()
        while self.state.get_room(room_code) is not None:
            room_code = self.generate_room_code()
        
        # Get knowledge base
        kb = get_knowledge_base()
        
        # Verify source exists
        all_sources = kb.get_all_pdf_sources()
        if pdf_source_id not in all_sources:
            raise ValueError(
                f"PDF source '{pdf_source_id}' not found in knowledge base. "
                f"Available sources: {all_sources}. "
                f"Please upload the PDF first."
            )
        
        # Get LLM and initialize quiz agent
        llm = ModelFactory.get_llm_model()
        quiz_agent = QuizAgent(llm, kb)
        
        try:
            # Create initial state for QuizAgent
            initial_state = AgentState(
                session_id=room_code,  # Use room code as session ID
                pdf_source_id=pdf_source_id,
                current_difficulty="MEDIUM",  # Default for multiplayer
                topic=topic,
                retrieved_docs=[],
                generated_quiz=None
            )
            
            # Generate quiz using QuizAgent's LangGraph workflow
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                quiz_agent.graph.invoke,
                initial_state.dict()  # Convert Pydantic model to dict
            )
            
            if result.get("error"):
                raise ValueError(f"Quiz generation error: {result['error']}")
            
            quiz_output = result.get("generated_quiz")
            if not quiz_output or not quiz_output.questions:
                raise ValueError("QuizAgent did not return valid quiz_output")
            
            # Structure quiz data for room storage
            quiz_data = [
                {
                    "question_index": idx,
                    "question": q.question,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation or "",
                    "difficulty": q.difficulty
                }
                for idx, q in enumerate(quiz_output.questions)
            ]
            
            # Create room in global state
            room_data = self.state.create_room(
                room_code=room_code,
                host_id=host_id,
                topic=topic,
                pdf_source_id=pdf_source_id,
                quiz_data=quiz_data
            )
            
            return {
                "success": True,
                "room_code": room_code,
                "room_data": room_data,
                "quiz_preview": {
                    "total_questions": len(quiz_data),
                    "topic": topic,
                    "source": pdf_source_id
                }
            }
            
        except Exception as e:
            raise ValueError(f"Quiz generation failed: {str(e)}")
    
    def join_room(self, room_code: str, user_id: str) -> Dict[str, Any]:
        """
        Add a player to an existing room.
        
        Args:
            room_code: Room to join
            user_id: User joining
            
        Returns:
            Success status and room data
        """
        room = self.state.get_room(room_code)
        
        if not room:
            return {
                "success": False,
                "error": "Room not found"
            }
        
        if room["status"] != "WAITING":
            return {
                "success": False,
                "error": "Game already in progress"
            }
        
        # Add player
        success = self.state.add_player(room_code, user_id)
        
        if not success:
            return {
                "success": False,
                "error": "Failed to join room"
            }
        
        return {
            "success": True,
            "room_code": room_code,
            "players": list(room["players"].keys()),
            "status": room["status"]
        }
    
    def start_game(self, room_code: str, requester_id: str) -> Dict[str, Any]:
        """
        Start the game (only host can do this).
        
        Args:
            room_code: Room to start
            requester_id: User requesting start
            
        Returns:
            Success status
        """
        room = self.state.get_room(room_code)
        
        if not room:
            return {"success": False, "error": "Room not found"}
        
        # Only host can start
        if room["host"] != requester_id:
            return {"success": False, "error": "Only host can start game"}
        
        if room["status"] != "WAITING":
            return {"success": False, "error": "Game already started"}
        
        # Update status
        self.state.update_room_status(room_code, "ACTIVE")
        
        return {
            "success": True,
            "message": "Game started",
            "player_count": len(room["players"])
        }
    
    def handle_answer(
        self,
        room_code: str,
        user_id: str,
        question_index: int,
        answer_text: str,
        time_taken: float
    ) -> Dict[str, Any]:
        """
        Process a player's answer and update scores.
        
        Scoring Logic:
        - Correct: 100 - (2 * time_taken) points (minimum 10)
        - Incorrect: 0 points
        
        Args:
            room_code: Room identifier
            user_id: Player submitting answer
            question_index: Index of the question answered
            answer_text: Player's answer
            time_taken: Time in seconds to answer
            
        Returns:
            Answer validation result and updated leaderboard
        """
        room = self.state.get_room(room_code)
        
        if not room:
            return {"success": False, "error": "Room not found"}
        
        if room["status"] != "ACTIVE":
            return {"success": False, "error": "Game not active"}
        
        # Get the question
        if question_index >= len(room["quiz_data"]):
            return {"success": False, "error": "Invalid question index"}
        
        question_data = room["quiz_data"][question_index]
        correct_answer = question_data["correct_answer"]
        
        # Validate answer
        is_correct = (answer_text.strip().lower() == correct_answer.strip().lower())
        
        # Calculate score
        if is_correct:
            # Score decreases with time (max 100, min 10)
            score = max(10, int(100 - (2 * time_taken)))
        else:
            score = 0
        
        # Record answer
        answer_data = {
            "question_index": question_index,
            "answer": answer_text,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "time_taken": time_taken,
            "score": score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update player score
        self.state.update_player_score(room_code, user_id, score, answer_data)
        
        # Get updated leaderboard
        leaderboard = self.state.get_leaderboard(room_code)
        
        return {
            "success": True,
            "is_correct": is_correct,
            "score": score,
            "correct_answer": correct_answer if not is_correct else None,
            "explanation": question_data.get("explanation", ""),
            "leaderboard": leaderboard
        }
    
    def get_question(self, room_code: str, question_index: int) -> Dict[str, Any]:
        """
        Get a specific question from the room's quiz.
        
        Args:
            room_code: Room identifier
            question_index: Question index
            
        Returns:
            Question data (without correct answer)
        """
        room = self.state.get_room(room_code)
        
        if not room:
            return {"success": False, "error": "Room not found"}
        
        if question_index >= len(room["quiz_data"]):
            return {"success": False, "error": "Invalid question index"}
        
        question = room["quiz_data"][question_index]
        
        # Return question without revealing answer
        return {
            "success": True,
            "question_index": question_index,
            "question": question["question"],
            "options": question["options"],
            "total_questions": len(room["quiz_data"])
        }
    
    def get_leaderboard(self, room_code: str) -> Dict[str, Any]:
        """Get current leaderboard for a room."""
        leaderboard = self.state.get_leaderboard(room_code)
        
        if leaderboard is None:
            return {"success": False, "error": "Room not found"}
        
        return {
            "success": True,
            "leaderboard": leaderboard
        }
    
    def end_game(self, room_code: str) -> Dict[str, Any]:
        """
        End the game and calculate final results.
        
        Args:
            room_code: Room to end
            
        Returns:
            Final results with winner
        """
        room = self.state.get_room(room_code)
        
        if not room:
            return {"success": False, "error": "Room not found"}
        
        # Update status
        self.state.update_room_status(room_code, "FINISHED")
        
        # Get final leaderboard
        leaderboard = self.state.get_leaderboard(room_code)
        
        # Determine winner
        winner = leaderboard[0] if leaderboard else None
        
        # Award points to winner
        if winner:
            self.state.update_user_stats(winner["user_id"], points_delta=50, won=True)
        
        # Update all players' stats
        for player in leaderboard[1:]:  # Non-winners
            self.state.update_user_stats(player["user_id"], points_delta=10, won=False)
        
        return {
            "success": True,
            "status": "FINISHED",
            "winner": winner,
            "final_leaderboard": leaderboard
        }
    
    def get_room_info(self, room_code: str) -> Dict[str, Any]:
        """Get detailed room information."""
        room = self.state.get_room(room_code)
        
        if not room:
            return {"success": False, "error": "Room not found"}
        
        return {
            "success": True,
            "room_code": room_code,
            "host": room["host"],
            "topic": room["topic"],
            "status": room["status"],
            "player_count": len(room["players"]),
            "total_questions": len(room["quiz_data"]),
            "created_at": room["created_at"]
        }


# Singleton instance
_room_manager_instance = None

def get_room_manager() -> RoomManager:
    """Get the room manager singleton instance."""
    global _room_manager_instance
    if _room_manager_instance is None:
        _room_manager_instance = RoomManager()
    return _room_manager_instance
