"""
Multiplayer features package.
Includes competitive race mode and real-time multiplayer functionality.
"""

from .state_manager import GlobalState, get_global_state
from .room_manager import RoomManager, get_room_manager

__all__ = [
    "GlobalState",
    "get_global_state",
    "RoomManager",
    "get_room_manager"
]
