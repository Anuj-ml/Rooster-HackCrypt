# 🗄️ Supabase Migration Guide

## Overview

This document provides SQL migration scripts to move from **in-memory Python dictionaries** to a **persistent Supabase (PostgreSQL) database**. This migration enables:

- ✅ **Data persistence** across server restarts
- ✅ **Scalability** for large user bases
- ✅ **Advanced querying** (JOIN, aggregations, etc.)
- ✅ **Real-time subscriptions** via Supabase Realtime
- ✅ **Row-level security** for multi-tenancy

---

## 📋 Prerequisites

1. **Supabase account**: [https://supabase.com](https://supabase.com)
2. **Project created** in Supabase dashboard
3. **API URL and API Key** from project settings
4. **Python client**: `pip install supabase`

---

## 🛠️ Database Schema

### 1. Users Table

Stores user profiles, stats, and badges.

```sql
-- Create users table
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT,
    email TEXT UNIQUE,
    grind_points INTEGER DEFAULT 0,
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    badges TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX idx_users_grind_points ON users(grind_points DESC);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

### 2. Rooms Table

Stores quiz room metadata.

```sql
-- Create rooms table
CREATE TABLE rooms (
    room_code TEXT PRIMARY KEY,
    host_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    pdf_source_id TEXT,
    status TEXT CHECK (status IN ('WAITING', 'ACTIVE', 'FINISHED')) DEFAULT 'WAITING',
    num_questions INTEGER DEFAULT 5,
    quiz_data JSONB,  -- Stores full quiz JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX idx_rooms_status ON rooms(status);
CREATE INDEX idx_rooms_host_id ON rooms(host_id);
CREATE INDEX idx_rooms_created_at ON rooms(created_at DESC);
```

---

### 3. Room Players Table

Junction table for room participants with scores.

```sql
-- Create room_players table
CREATE TABLE room_players (
    id SERIAL PRIMARY KEY,
    room_code TEXT NOT NULL REFERENCES rooms(room_code) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    score INTEGER DEFAULT 0,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(room_code, user_id)
);

-- Create indexes
CREATE INDEX idx_room_players_room_code ON room_players(room_code);
CREATE INDEX idx_room_players_user_id ON room_players(user_id);
CREATE INDEX idx_room_players_score ON room_players(score DESC);
```

---

### 4. Study Groups Table

Stores study group information.

```sql
-- Create study_groups table
CREATE TABLE study_groups (
    group_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    creator_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    max_members INTEGER DEFAULT 2,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index
CREATE INDEX idx_study_groups_creator_id ON study_groups(creator_id);
```

---

### 5. Group Members Table

Junction table for group membership.

```sql
-- Create group_members table
CREATE TABLE group_members (
    id SERIAL PRIMARY KEY,
    group_id TEXT NOT NULL REFERENCES study_groups(group_id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(group_id, user_id)
);

-- Create indexes
CREATE INDEX idx_group_members_group_id ON group_members(group_id);
CREATE INDEX idx_group_members_user_id ON group_members(user_id);

-- Add constraint to enforce max_members
CREATE OR REPLACE FUNCTION check_group_max_members()
RETURNS TRIGGER AS $$
DECLARE
    current_count INTEGER;
    max_allowed INTEGER;
BEGIN
    SELECT COUNT(*), sg.max_members
    INTO current_count, max_allowed
    FROM group_members gm
    JOIN study_groups sg ON sg.group_id = gm.group_id
    WHERE gm.group_id = NEW.group_id
    GROUP BY sg.max_members;
    
    IF current_count >= max_allowed THEN
        RAISE EXCEPTION 'Group is full (max % members)', max_allowed;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_group_capacity
BEFORE INSERT ON group_members
FOR EACH ROW
EXECUTE FUNCTION check_group_max_members();
```

---

### 6. Resources Table

Stores PDF resource metadata.

```sql
-- Create resources table
CREATE TABLE resources (
    pdf_source_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    uploaded_by TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    group_id TEXT REFERENCES study_groups(group_id) ON DELETE CASCADE,
    file_path TEXT,
    file_size INTEGER,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_resources_group_id ON resources(group_id);
CREATE INDEX idx_resources_uploaded_by ON resources(uploaded_by);
CREATE INDEX idx_resources_uploaded_at ON resources(uploaded_at DESC);
```

---

### 7. Game History Table

Stores completed game records for analytics.

```sql
-- Create game_history table
CREATE TABLE game_history (
    game_id SERIAL PRIMARY KEY,
    room_code TEXT NOT NULL,
    winner_id TEXT REFERENCES users(user_id) ON DELETE SET NULL,
    players JSONB,  -- Array of player_id + score
    quiz_topic TEXT,
    num_questions INTEGER,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER
);

-- Create indexes
CREATE INDEX idx_game_history_winner_id ON game_history(winner_id);
CREATE INDEX idx_game_history_ended_at ON game_history(ended_at DESC);
```

---

## 🔐 Row-Level Security (RLS)

Enable RLS for secure multi-tenant access.

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE room_players ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;

-- Users: Can only read/update own profile
CREATE POLICY "Users can view own profile"
ON users FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
ON users FOR UPDATE
USING (auth.uid() = user_id);

-- Rooms: All users can view, only host can update
CREATE POLICY "Anyone can view rooms"
ON rooms FOR SELECT
USING (true);

CREATE POLICY "Host can update room"
ON rooms FOR UPDATE
USING (auth.uid() = host_id);

-- Room Players: Players can view room participants
CREATE POLICY "Room players can view participants"
ON room_players FOR SELECT
USING (
    user_id = auth.uid() OR
    room_code IN (SELECT room_code FROM room_players WHERE user_id = auth.uid())
);

-- Study Groups: Members can view group info
CREATE POLICY "Group members can view group"
ON study_groups FOR SELECT
USING (
    group_id IN (SELECT group_id FROM group_members WHERE user_id = auth.uid())
);

-- Resources: Group members can view resources
CREATE POLICY "Group members can view resources"
ON resources FOR SELECT
USING (
    group_id IN (SELECT group_id FROM group_members WHERE user_id = auth.uid())
);
```

---

## 🐍 Python Integration

### 1. Install Supabase Client

```bash
pip install supabase
```

### 2. Create Supabase Client

**File**: `backend/api/services/supabase_client.py`

```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase() -> Client:
    """Dependency for Supabase client."""
    return supabase
```

**Add to `.env`**:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

---

### 3. Update State Manager

Replace in-memory dictionaries with Supabase queries.

**Example**: `create_room` method

```python
# OLD (in-memory)
def create_room(self, room_code, host_id, topic, pdf_source_id, num_questions):
    with self.lock:
        self.rooms[room_code] = {
            "host_id": host_id,
            "players": [host_id],
            "status": "WAITING",
            ...
        }

# NEW (Supabase)
async def create_room(self, room_code, host_id, topic, pdf_source_id, num_questions):
    # Insert room
    room_data = supabase.table("rooms").insert({
        "room_code": room_code,
        "host_id": host_id,
        "topic": topic,
        "pdf_source_id": pdf_source_id,
        "status": "WAITING",
        "num_questions": num_questions
    }).execute()
    
    # Add host as first player
    supabase.table("room_players").insert({
        "room_code": room_code,
        "user_id": host_id,
        "score": 0
    }).execute()
    
    return room_data.data[0]
```

---

### 4. Example Queries

#### Get User Stats

```python
def get_user_stats(user_id: str):
    result = supabase.table("users") \
        .select("*") \
        .eq("user_id", user_id) \
        .single() \
        .execute()
    
    return result.data
```

#### Get Room Leaderboard

```python
def get_room_leaderboard(room_code: str):
    result = supabase.table("room_players") \
        .select("user_id, score, users(username)") \
        .eq("room_code", room_code) \
        .order("score", desc=True) \
        .execute()
    
    return result.data
```

#### List Study Groups with Member Count

```python
def list_study_groups():
    result = supabase.rpc("get_study_groups_with_counts").execute()
    return result.data
```

**SQL Function**:
```sql
CREATE OR REPLACE FUNCTION get_study_groups_with_counts()
RETURNS TABLE (
    group_id TEXT,
    name TEXT,
    member_count BIGINT,
    max_members INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sg.group_id,
        sg.name,
        COUNT(gm.user_id) AS member_count,
        sg.max_members
    FROM study_groups sg
    LEFT JOIN group_members gm ON sg.group_id = gm.group_id
    GROUP BY sg.group_id, sg.name, sg.max_members;
END;
$$ LANGUAGE plpgsql;
```

---

## 🔄 Migration Script

Run this script to populate Supabase with existing in-memory data.

**File**: `backend/scripts/migrate_to_supabase.py`

```python
import asyncio
from src.features.multiplayer.state_manager import get_global_state
from api.services.supabase_client import supabase

async def migrate():
    state = get_global_state()
    
    # Migrate users
    print("Migrating users...")
    for user_id, user_data in state.users.items():
        supabase.table("users").upsert({
            "user_id": user_id,
            "grind_points": user_data["grind_points"],
            "games_played": user_data["games_played"],
            "wins": user_data["wins"],
            "badges": user_data["badges"]
        }).execute()
    
    # Migrate study groups
    print("Migrating study groups...")
    for group_id, group_data in state.study_groups.items():
        supabase.table("study_groups").upsert({
            "group_id": group_id,
            "name": group_data["name"],
            "creator_id": group_data["members"][0],  # First member is creator
            "max_members": group_data["max_members"]
        }).execute()
        
        # Migrate group members
        for member_id in group_data["members"]:
            supabase.table("group_members").upsert({
                "group_id": group_id,
                "user_id": member_id
            }).execute()
    
    # Migrate resources
    print("Migrating resources...")
    for pdf_id, resource_data in state.resources.items():
        supabase.table("resources").upsert({
            "pdf_source_id": pdf_id,
            "title": resource_data["title"],
            "uploaded_by": resource_data["uploaded_by"],
            "group_id": resource_data["group_id"]
        }).execute()
    
    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())
```

**Run**:
```bash
python backend/scripts/migrate_to_supabase.py
```

---

## 🔔 Real-Time Features

Supabase Realtime enables WebSocket-like subscriptions.

**Example**: Subscribe to leaderboard updates

```python
# Frontend (JavaScript)
const leaderboard = supabase
    .channel('room_ABC123_leaderboard')
    .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'room_players',
        filter: `room_code=eq.ABC123`
    }, (payload) => {
        console.log('Leaderboard updated:', payload);
        updateLeaderboardUI();
    })
    .subscribe();
```

---

## 📊 Performance Optimization

### Indexes

Already created in schema above. Key indexes:

- `idx_users_grind_points` - Fast leaderboard queries
- `idx_rooms_status` - Filter by active/waiting rooms
- `idx_room_players_score` - Sort by score
- `idx_resources_group_id` - Group resource lookup

### Connection Pooling

**File**: `backend/api/services/supabase_client.py`

```python
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

options = ClientOptions(
    auto_refresh_token=True,
    persist_session=True,
    max_connections=20  # Connection pool size
)

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options=options
)
```

---

## 🧪 Testing

### 1. Test Connection

```python
def test_supabase_connection():
    result = supabase.table("users").select("*").limit(1).execute()
    assert result.data is not None
    print("✅ Supabase connected!")
```

### 2. Test User Creation

```python
def test_create_user():
    user = supabase.table("users").insert({
        "user_id": "test_user_123",
        "username": "TestUser",
        "email": "test@example.com"
    }).execute()
    
    assert user.data[0]["user_id"] == "test_user_123"
    print("✅ User created!")
```

---

## 🚀 Deployment Checklist

- [ ] Run all SQL schema scripts in Supabase SQL editor
- [ ] Enable RLS policies
- [ ] Add `SUPABASE_URL` and `SUPABASE_KEY` to `.env`
- [ ] Update `state_manager.py` with Supabase queries
- [ ] Run migration script to transfer existing data
- [ ] Test all endpoints with Supabase backend
- [ ] Update frontend to use Supabase Realtime (optional)
- [ ] Setup database backups in Supabase dashboard

---

## 🛡️ Security Best Practices

1. **Use RLS policies** for all tables
2. **Never expose `service_role` key** in frontend
3. **Validate user input** before database insertion
4. **Use parameterized queries** to prevent SQL injection
5. **Enable 2FA** on Supabase account
6. **Rotate API keys** periodically

---

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [FastAPI + Supabase Tutorial](https://supabase.com/docs/guides/api)

---

## 🎉 Conclusion

This migration guide provides everything needed to transition from in-memory storage to a production-ready Supabase database. The schema is optimized for the Rooster-HackCrypt multiplayer features with proper indexing, constraints, and RLS policies.

**Next Steps**:
1. Create Supabase project
2. Run SQL scripts
3. Update Python code
4. Test thoroughly
5. Deploy! 🚀
