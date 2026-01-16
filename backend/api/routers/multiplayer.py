"""
Multiplayer Race Mode API Router

Provides REST endpoints and WebSocket for competitive multiplayer quiz battles.
"""

import asyncio
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any

from ..models.responses import APIResponse
from ..socket_handler import get_connection_manager, ConnectionManager
from src.models.schemas import CreateRoomRequest, JoinRoomRequest, SubmitAnswerRequest
from src.features.multiplayer.room_manager import get_room_manager, RoomManager
from src.features.multiplayer.state_manager import get_global_state, GlobalState


router = APIRouter(prefix="/multiplayer", tags=["Multiplayer"])


# Dependency injection
async def get_room_mgr() -> RoomManager:
    """Dependency for RoomManager."""
    return get_room_manager()


async def get_state() -> GlobalState:
    """Dependency for GlobalState."""
    return get_global_state()


async def get_conn_mgr() -> ConnectionManager:
    """Dependency for ConnectionManager."""
    return get_connection_manager()


# ==================== REST ENDPOINTS ====================

@router.post("/rooms/create")
async def create_room(
    request: CreateRoomRequest,
    room_mgr: RoomManager = Depends(get_room_mgr)
) -> APIResponse:
    """
    Create a new multiplayer room with pre-generated quiz.
    
    **Flow:**
    1. Generates a 5-question quiz immediately
    2. Creates a unique room code
    3. Adds host as first player
    4. Returns room code and quiz preview
    
    **Use Case:**
    - Student wants to start a competitive quiz race
    - Quiz is generated once and shared with all players
    
    **Example Request:**
    ```json
    {
        "host_id": "user_123",
        "topic": "photosynthesis",
        "pdf_source_id": "biology_textbook",
        "num_questions": 5
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "room_code": "ABC123",
            "quiz_preview": {
                "total_questions": 5,
                "topic": "photosynthesis"
            }
        }
    }
    ```
    """
    try:
        result = await room_mgr.create_room(
            host_id=request.host_id,
            topic=request.topic,
            pdf_source_id=request.pdf_source_id,
            num_questions=request.num_questions
        )
        
        return APIResponse(
            success=True,
            message="Room created successfully",
            data={
                "room_code": result["room_code"],
                "quiz_preview": result["quiz_preview"]
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")


@router.post("/rooms/join")
async def join_room(
    request: JoinRoomRequest,
    room_mgr: RoomManager = Depends(get_room_mgr)
) -> APIResponse:
    """
    Join an existing multiplayer room.
    
    **Requirements:**
    - Room must exist
    - Game must not have started yet
    
    **Example Request:**
    ```json
    {
        "room_code": "ABC123",
        "user_id": "user_456"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "room_code": "ABC123",
            "players": ["user_123", "user_456"],
            "status": "WAITING"
        }
    }
    ```
    """
    try:
        result = room_mgr.join_room(request.room_code, request.user_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to join room"))
        
        return APIResponse(
            success=True,
            message="Joined room successfully",
            data=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join room: {str(e)}")


@router.get("/rooms/{room_code}")
async def get_room_info(
    room_code: str,
    room_mgr: RoomManager = Depends(get_room_mgr)
) -> APIResponse:
    """
    Get detailed information about a room.
    
    **Returns:**
    - Host ID
    - Player count
    - Game status
    - Quiz metadata
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "room_code": "ABC123",
            "host": "user_123",
            "status": "WAITING",
            "player_count": 2,
            "total_questions": 5
        }
    }
    ```
    """
    try:
        result = room_mgr.get_room_info(room_code)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return APIResponse(
            success=True,
            data=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms")
async def list_rooms(
    state: GlobalState = Depends(get_state)
) -> APIResponse:
    """
    List all active rooms (lobby browsing).
    
    **Returns:**
    - List of rooms with metadata
    - Useful for discovering joinable games
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "rooms": [
                {
                    "room_code": "ABC123",
                    "host": "user_123",
                    "status": "WAITING",
                    "player_count": 2,
                    "topic": "photosynthesis"
                }
            ],
            "total": 1
        }
    }
    ```
    """
    try:
        rooms = state.list_rooms()
        
        return APIResponse(
            success=True,
            data={
                "rooms": rooms,
                "total": len(rooms)
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_code}/leaderboard")
async def get_leaderboard(
    room_code: str,
    room_mgr: RoomManager = Depends(get_room_mgr)
) -> APIResponse:
    """
    Get current leaderboard for a room.
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "leaderboard": [
                {
                    "user_id": "user_123",
                    "score": 450,
                    "answers_count": 5
                },
                {
                    "user_id": "user_456",
                    "score": 380,
                    "answers_count": 4
                }
            ]
        }
    }
    ```
    """
    try:
        result = room_mgr.get_leaderboard(room_code)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return APIResponse(
            success=True,
            data=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/stats")
async def get_user_stats(
    user_id: str,
    state: GlobalState = Depends(get_state)
) -> APIResponse:
    """
    Get user statistics.
    
    **Returns:**
    - Grind points
    - Badges
    - Games played
    - Win rate
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "user_id": "user_123",
            "grind_points": 1050,
            "badges": ["First Win", "Speed Demon"],
            "games_played": 10,
            "wins": 3
        }
    }
    ```
    """
    try:
        user = state.get_user(user_id)
        
        return APIResponse(
            success=True,
            data=user
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WEBSOCKET ENDPOINT ====================

@router.websocket("/ws/race/{room_code}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_code: str,
    user_id: str,
    conn_mgr: ConnectionManager = Depends(get_conn_mgr)
):
    """
    WebSocket endpoint for real-time multiplayer communication.
    
    **Connection Flow:**
    1. Client connects with room_code and user_id
    2. Server accepts connection and broadcasts PLAYER_JOINED
    3. Host can send START_GAME message
    4. Players send SUBMIT_ANSWER messages
    5. Server broadcasts LEADERBOARD_UPDATE after each answer
    
    **Message Types (Client → Server):**
    - `START_GAME`: Start the game (host only)
    - `SUBMIT_ANSWER`: Submit answer {question_index, answer, time_taken}
    - `GET_QUESTION`: Request question {question_index}
    - `CHAT_MESSAGE`: Send chat {text}
    - `END_GAME`: End the game (host only)
    
    **Message Types (Server → Client):**
    - `PLAYER_JOINED`: New player joined {user_id}
    - `GAME_STARTED`: Game has started
    - `QUESTION`: Next question data
    - `ANSWER_RESULT`: Your answer result {is_correct, score}
    - `LEADERBOARD_UPDATE`: Updated leaderboard
    - `GAME_ENDED`: Game finished {winner, final_leaderboard}
    - `ERROR`: Error message
    
    **Example Client Message:**
    ```json
    {
        "type": "SUBMIT_ANSWER",
        "question_index": 0,
        "answer": "Mitochondria",
        "time_taken": 5.3
    }
    ```
    
    **Example Server Broadcast:**
    ```json
    {
        "type": "LEADERBOARD_UPDATE",
        "leaderboard": [
            {"user_id": "user_123", "score": 92},
            {"user_id": "user_456", "score": 88}
        ]
    }
    ```
    """
    try:
        # Connect user
        await conn_mgr.connect(websocket, room_code, user_id)
        
        # Broadcast player joined
        await conn_mgr.broadcast_to_room(room_code, {
            "type": "PLAYER_JOINED",
            "user_id": user_id,
            "connected_players": conn_mgr.get_room_connections(room_code)
        }, exclude=user_id)
        
        # Send confirmation to user
        await conn_mgr.send_personal_message({
            "type": "CONNECTED",
            "room_code": room_code,
            "user_id": user_id
        }, websocket)
        
        # Message loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Handle message
            await conn_mgr.handle_message(websocket, room_code, user_id, data)
    
    except WebSocketDisconnect:
        # Clean disconnect
        await conn_mgr.disconnect(room_code, user_id)
        
        # Notify other players
        await conn_mgr.broadcast_to_room(room_code, {
            "type": "PLAYER_LEFT",
            "user_id": user_id
        })
    
    except Exception as e:
        # Error disconnect
        await conn_mgr.disconnect(room_code, user_id)
        print(f"WebSocket error for {user_id} in {room_code}: {str(e)}")
