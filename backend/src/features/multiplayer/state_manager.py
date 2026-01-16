"""
Global State Manager for Multiplayer Features

In-memory state storage for rooms, users, study groups, and resources.
This is a placeholder before migrating to a proper database (Supabase).
"""

import threading
from datetime import datetime
from typing import Dict, List, Optional, Any


class GlobalState:
    """
    Singleton class to manage global application state.
    
    This stores all multiplayer game rooms, user stats, study groups,
    and resource metadata in memory. Thread-safe with locks.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize state dictionaries (only once)."""
        if self._initialized:
            return
        
        # Room state for competitive multiplayer
        # Structure: { "ROOM_CODE": { "host": "user_id", "players": {}, "quiz_data": [], "status": "WAITING", "created_at": timestamp } }
        self.rooms: Dict[str, Dict[str, Any]] = {}
        
        # User stats and progression (mock persistence)
        # Structure: { "user_id": { "grind_points": 1000, "badges": [] } }
        self.users: Dict[str, Dict[str, Any]] = {}
        
        # Study groups (2 students max for now)
        # Structure: { "group_id": { "name": str, "members": [], "resources": [] } }
        self.study_groups: Dict[str, Dict[str, Any]] = {}
        
        # Resource metadata mapping
        # Structure: { "pdf_source_id": { "title": str, "uploaded_by": str, "group_id": str } }
        self.resources: Dict[str, Dict[str, Any]] = {}
        
        # Thread locks for concurrent access
        self._rooms_lock = threading.Lock()
        self._users_lock = threading.Lock()
        self._groups_lock = threading.Lock()
        self._resources_lock = threading.Lock()
        
        self._initialized = True
    
    # ==================== ROOM MANAGEMENT ====================
    
    def create_room(self, room_code: str, host_id: str, topic: str, 
                    pdf_source_id: str, quiz_data: List[Dict]) -> Dict[str, Any]:
        """
        Create a new multiplayer room.
        
        Args:
            room_code: Unique 6-character room identifier
            host_id: User ID of the room host
            topic: Quiz topic
            pdf_source_id: Source material ID
            quiz_data: Pre-generated quiz questions
            
        Returns:
            Room data dictionary
        """
        with self._rooms_lock:
            room_data = {
                "room_code": room_code,
                "host": host_id,
                "topic": topic,
                "pdf_source_id": pdf_source_id,
                "players": {
                    host_id: {
                        "user_id": host_id,
                        "score": 0,
                        "answers": [],
                        "joined_at": datetime.utcnow().isoformat()
                    }
                },
                "quiz_data": quiz_data,
                "status": "WAITING",  # WAITING, ACTIVE, FINISHED
                "created_at": datetime.utcnow().isoformat(),
                "current_question": 0
            }
            self.rooms[room_code] = room_data
            return room_data
    
    def get_room(self, room_code: str) -> Optional[Dict[str, Any]]:
        """Get room data by code."""
        with self._rooms_lock:
            return self.rooms.get(room_code)
    
    def add_player(self, room_code: str, user_id: str) -> bool:
        """
        Add a player to an existing room.
        
        Returns:
            True if player added successfully, False otherwise
        """
        with self._rooms_lock:
            if room_code not in self.rooms:
                return False
            
            room = self.rooms[room_code]
            
            # Don't allow joining if game already started
            if room["status"] != "WAITING":
                return False
            
            # Add player
            room["players"][user_id] = {
                "user_id": user_id,
                "score": 0,
                "answers": [],
                "joined_at": datetime.utcnow().isoformat()
            }
            return True
    
    def update_room_status(self, room_code: str, status: str) -> bool:
        """Update room status (WAITING, ACTIVE, FINISHED)."""
        with self._rooms_lock:
            if room_code in self.rooms:
                self.rooms[room_code]["status"] = status
                return True
            return False
    
    def update_player_score(self, room_code: str, user_id: str, 
                           score_delta: int, answer_data: Dict) -> bool:
        """
        Update a player's score and record their answer.
        
        Args:
            room_code: Room identifier
            user_id: Player's user ID
            score_delta: Points to add
            answer_data: Answer metadata (question_index, answer, is_correct, time_taken)
            
        Returns:
            True if updated successfully
        """
        with self._rooms_lock:
            if room_code not in self.rooms:
                return False
            
            room = self.rooms[room_code]
            if user_id not in room["players"]:
                return False
            
            player = room["players"][user_id]
            player["score"] += score_delta
            player["answers"].append(answer_data)
            return True
    
    def get_leaderboard(self, room_code: str) -> List[Dict[str, Any]]:
        """
        Get sorted leaderboard for a room.
        
        Returns:
            List of players sorted by score (descending)
        """
        with self._rooms_lock:
            if room_code not in self.rooms:
                return []
            
            room = self.rooms[room_code]
            players = [
                {
                    "user_id": p["user_id"],
                    "score": p["score"],
                    "answers_count": len(p["answers"])
                }
                for p in room["players"].values()
            ]
            
            # Sort by score descending
            return sorted(players, key=lambda x: x["score"], reverse=True)
    
    def delete_room(self, room_code: str) -> bool:
        """Delete a room (cleanup after game ends)."""
        with self._rooms_lock:
            if room_code in self.rooms:
                del self.rooms[room_code]
                return True
            return False
    
    def list_rooms(self) -> List[Dict[str, Any]]:
        """List all active rooms (for lobby browsing)."""
        with self._rooms_lock:
            return [
                {
                    "room_code": code,
                    "host": room["host"],
                    "topic": room["topic"],
                    "status": room["status"],
                    "player_count": len(room["players"]),
                    "created_at": room["created_at"]
                }
                for code, room in self.rooms.items()
            ]
    
    # ==================== USER MANAGEMENT ====================
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user stats, create if doesn't exist."""
        with self._users_lock:
            if user_id not in self.users:
                self.users[user_id] = {
                    "user_id": user_id,
                    "grind_points": 1000,
                    "badges": [],
                    "games_played": 0,
                    "wins": 0
                }
            return self.users[user_id]
    
    def update_user_stats(self, user_id: str, points_delta: int = 0, 
                         won: bool = False) -> Dict[str, Any]:
        """Update user stats after a game."""
        with self._users_lock:
            user = self.get_user(user_id)
            user["grind_points"] += points_delta
            user["games_played"] += 1
            if won:
                user["wins"] += 1
            return user
    
    def add_badge(self, user_id: str, badge_name: str) -> bool:
        """Award a badge to a user."""
        with self._users_lock:
            user = self.get_user(user_id)
            if badge_name not in user["badges"]:
                user["badges"].append(badge_name)
                return True
            return False
    
    # ==================== STUDY GROUP MANAGEMENT ====================
    
    def create_study_group(self, group_id: str, name: str, creator_id: str) -> Dict[str, Any]:
        """Create a new study group."""
        with self._groups_lock:
            group_data = {
                "group_id": group_id,
                "name": name,
                "members": [creator_id],
                "resources": [],
                "created_at": datetime.utcnow().isoformat(),
                "max_members": 2  # Only 2 students for now
            }
            self.study_groups[group_id] = group_data
            return group_data
    
    def get_study_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get study group data."""
        with self._groups_lock:
            return self.study_groups.get(group_id)
    
    def add_group_member(self, group_id: str, user_id: str) -> bool:
        """Add a member to a study group."""
        with self._groups_lock:
            if group_id not in self.study_groups:
                return False
            
            group = self.study_groups[group_id]
            
            # Check max members
            if len(group["members"]) >= group["max_members"]:
                return False
            
            if user_id not in group["members"]:
                group["members"].append(user_id)
                return True
            return False
    
    def add_group_resource(self, group_id: str, pdf_source_id: str) -> bool:
        """Add a resource to a study group."""
        with self._groups_lock:
            if group_id not in self.study_groups:
                return False
            
            group = self.study_groups[group_id]
            if pdf_source_id not in group["resources"]:
                group["resources"].append(pdf_source_id)
                return True
            return False
    
    def list_study_groups(self) -> List[Dict[str, Any]]:
        """List all study groups."""
        with self._groups_lock:
            return list(self.study_groups.values())
    
    # ==================== RESOURCE MANAGEMENT ====================
    
    def add_resource(self, pdf_source_id: str, title: str, 
                    uploaded_by: str, group_id: str) -> Dict[str, Any]:
        """Register a new resource."""
        with self._resources_lock:
            resource_data = {
                "pdf_source_id": pdf_source_id,
                "title": title,
                "uploaded_by": uploaded_by,
                "group_id": group_id,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            self.resources[pdf_source_id] = resource_data
            return resource_data
    
    def get_resource(self, pdf_source_id: str) -> Optional[Dict[str, Any]]:
        """Get resource metadata."""
        with self._resources_lock:
            return self.resources.get(pdf_source_id)
    
    def list_group_resources(self, group_id: str) -> List[Dict[str, Any]]:
        """List all resources for a group."""
        with self._resources_lock:
            return [
                resource for resource in self.resources.values()
                if resource["group_id"] == group_id
            ]


# Singleton instance getter
_global_state_instance = None

def get_global_state() -> GlobalState:
    """Get the global state singleton instance."""
    global _global_state_instance
    if _global_state_instance is None:
        _global_state_instance = GlobalState()
    return _global_state_instance
