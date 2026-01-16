"""
WebSocket Connection Manager for Real-Time Multiplayer

Handles WebSocket connections, broadcasts, and real-time communication.
"""

from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

from src.features.multiplayer.state_manager import get_global_state
from src.features.multiplayer.room_manager import get_room_manager


class ConnectionManager:
    """
    Manages WebSocket connections for multiplayer rooms.
    
    Tracks active connections per room and handles broadcasting
    messages to all connected clients.
    """
    
    def __init__(self):
        """Initialize connection manager."""
        # Structure: { room_code: { user_id: WebSocket } }
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
        
        self.state = get_global_state()
        self.room_manager = get_room_manager()
    
    async def connect(self, websocket: WebSocket, room_code: str, user_id: str):
        """
        Accept a new WebSocket connection and add user to room.
        
        Args:
            websocket: WebSocket connection
            room_code: Room to join
            user_id: User connecting
        """
        await websocket.accept()
        
        async with self._lock:
            if room_code not in self.active_connections:
                self.active_connections[room_code] = {}
            
            self.active_connections[room_code][user_id] = websocket
    
    async def disconnect(self, room_code: str, user_id: str):
        """
        Remove a user's connection from a room.
        
        Args:
            room_code: Room code
            user_id: User disconnecting
        """
        async with self._lock:
            if room_code in self.active_connections:
                if user_id in self.active_connections[room_code]:
                    del self.active_connections[room_code][user_id]
                
                # Clean up empty rooms
                if not self.active_connections[room_code]:
                    del self.active_connections[room_code]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific connection.
        
        Args:
            message: Message dictionary
            websocket: Target WebSocket
        """
        await websocket.send_json(message)
    
    async def broadcast_to_room(self, room_code: str, message: dict, exclude: str = None):
        """
        Broadcast a message to all connections in a room.
        
        Args:
            room_code: Room to broadcast to
            message: Message dictionary
            exclude: Optional user_id to exclude from broadcast
        """
        if room_code not in self.active_connections:
            return
        
        disconnected = []
        
        for user_id, connection in self.active_connections[room_code].items():
            # Skip excluded user
            if exclude and user_id == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except Exception:
                # Mark for disconnection
                disconnected.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected:
            await self.disconnect(room_code, user_id)
    
    async def handle_message(
        self,
        websocket: WebSocket,
        room_code: str,
        user_id: str,
        message: dict
    ):
        """
        Handle incoming WebSocket messages.
        
        Message Types:
        - START_GAME: Host starts the game
        - SUBMIT_ANSWER: Player submits an answer
        - GET_QUESTION: Request next question
        - CHAT_MESSAGE: Send chat message
        
        Args:
            websocket: Sender's WebSocket
            room_code: Current room
            user_id: Sender's user ID
            message: Message data
        """
        msg_type = message.get("type")
        
        if msg_type == "START_GAME":
            await self._handle_start_game(room_code, user_id)
        
        elif msg_type == "SUBMIT_ANSWER":
            await self._handle_submit_answer(
                room_code,
                user_id,
                message.get("question_index"),
                message.get("answer"),
                message.get("time_taken", 0)
            )
        
        elif msg_type == "GET_QUESTION":
            await self._handle_get_question(
                websocket,
                room_code,
                message.get("question_index", 0)
            )
        
        elif msg_type == "CHAT_MESSAGE":
            await self._handle_chat_message(
                room_code,
                user_id,
                message.get("text", "")
            )
        
        elif msg_type == "END_GAME":
            await self._handle_end_game(room_code, user_id)
    
    async def _handle_start_game(self, room_code: str, user_id: str):
        """Handle START_GAME message (host only)."""
        result = self.room_manager.start_game(room_code, user_id)
        
        if result["success"]:
            # Broadcast game started to all players
            await self.broadcast_to_room(room_code, {
                "type": "GAME_STARTED",
                "message": "Game is starting!",
                "player_count": result["player_count"]
            })
            
            # Send first question to all players
            question = self.room_manager.get_question(room_code, 0)
            if question["success"]:
                await self.broadcast_to_room(room_code, {
                    "type": "QUESTION",
                    "data": question
                })
        else:
            # Send error to requester
            room = self.state.get_room(room_code)
            if room and user_id in self.active_connections.get(room_code, {}):
                await self.send_personal_message({
                    "type": "ERROR",
                    "message": result.get("error", "Failed to start game")
                }, self.active_connections[room_code][user_id])
    
    async def _handle_submit_answer(
        self,
        room_code: str,
        user_id: str,
        question_index: int,
        answer: str,
        time_taken: float
    ):
        """Handle SUBMIT_ANSWER message."""
        result = self.room_manager.handle_answer(
            room_code,
            user_id,
            question_index,
            answer,
            time_taken
        )
        
        if result["success"]:
            # Broadcast leaderboard update to all players
            await self.broadcast_to_room(room_code, {
                "type": "LEADERBOARD_UPDATE",
                "leaderboard": result["leaderboard"],
                "answered_by": user_id
            })
            
            # Send answer feedback to the player who answered
            if room_code in self.active_connections and user_id in self.active_connections[room_code]:
                await self.send_personal_message({
                    "type": "ANSWER_RESULT",
                    "is_correct": result["is_correct"],
                    "score": result["score"],
                    "correct_answer": result.get("correct_answer"),
                    "explanation": result.get("explanation")
                }, self.active_connections[room_code][user_id])
        else:
            # Send error to player
            if room_code in self.active_connections and user_id in self.active_connections[room_code]:
                await self.send_personal_message({
                    "type": "ERROR",
                    "message": result.get("error", "Failed to submit answer")
                }, self.active_connections[room_code][user_id])
    
    async def _handle_get_question(
        self,
        websocket: WebSocket,
        room_code: str,
        question_index: int
    ):
        """Handle GET_QUESTION request."""
        result = self.room_manager.get_question(room_code, question_index)
        
        await self.send_personal_message({
            "type": "QUESTION",
            "data": result
        }, websocket)
    
    async def _handle_chat_message(
        self,
        room_code: str,
        user_id: str,
        text: str
    ):
        """Handle CHAT_MESSAGE."""
        await self.broadcast_to_room(room_code, {
            "type": "CHAT",
            "user_id": user_id,
            "text": text,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        })
    
    async def _handle_end_game(self, room_code: str, user_id: str):
        """Handle END_GAME request."""
        result = self.room_manager.end_game(room_code)
        
        if result["success"]:
            # Broadcast final results
            await self.broadcast_to_room(room_code, {
                "type": "GAME_ENDED",
                "winner": result["winner"],
                "final_leaderboard": result["final_leaderboard"]
            })
    
    def get_room_connections(self, room_code: str) -> List[str]:
        """Get list of connected user IDs in a room."""
        if room_code in self.active_connections:
            return list(self.active_connections[room_code].keys())
        return []


# Singleton instance
_connection_manager_instance = None

def get_connection_manager() -> ConnectionManager:
    """Get the connection manager singleton instance."""
    global _connection_manager_instance
    if _connection_manager_instance is None:
        _connection_manager_instance = ConnectionManager()
    return _connection_manager_instance
