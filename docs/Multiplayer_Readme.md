# 🎮 Competitive Multiplayer & Study Groups

## Overview

The Rooster-HackCrypt multiplayer features enable **competitive quiz racing** and **collaborative study groups**. Students can compete in real-time quiz battles or collaborate with peers by sharing learning resources.

---

## 🏁 Race Mode (Competitive Multiplayer)

### Concept

Players join quiz rooms and compete to answer questions **fastest** and **most accurately**. Points are awarded based on speed and correctness.

### Key Features

- **Real-time WebSocket communication** for instant updates
- **Auto-generated quizzes** using QuizAgent from uploaded PDFs
- **Scoring algorithm**: `Score = 100 - (2 × time_taken)` (minimum 10 points if correct)
- **Live leaderboard** updates after each answer
- **6-character room codes** for easy joining

---

## 🎯 Race Mode Flow

### 1. Create Room

**Endpoint**: `POST /api/v1/multiplayer/rooms/create`

**Request**:
```json
{
  "host_id": "user_123",
  "topic": "Photosynthesis",
  "pdf_source_id": "bio_textbook_001",
  "num_questions": 5
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "room_code": "ABC123",
    "host_id": "user_123",
    "status": "WAITING",
    "quiz_ready": true,
    "num_questions": 5
  }
}
```

**What Happens**:
- Room is created with unique 6-character code
- Quiz is **immediately generated** using QuizAgent
- Room status is `WAITING` for players

---

### 2. Join Room

**Endpoint**: `POST /api/v1/multiplayer/rooms/join`

**Request**:
```json
{
  "room_code": "ABC123",
  "user_id": "user_456"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "room_code": "ABC123",
    "players": ["user_123", "user_456"]
  }
}
```

---

### 3. Connect to WebSocket

**Endpoint**: `WS /api/v1/multiplayer/ws/race/{room_code}/{user_id}`

**Example** (JavaScript):
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/multiplayer/ws/race/ABC123/user_456');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'GAME_STARTED':
      console.log('Game started!');
      break;
    case 'QUESTION':
      displayQuestion(message.question);
      break;
    case 'LEADERBOARD_UPDATE':
      updateLeaderboard(message.leaderboard);
      break;
    case 'GAME_ENDED':
      showWinner(message.winner);
      break;
  }
};
```

---

### 4. Start Game (Host Only)

**WebSocket Message**:
```json
{
  "type": "START_GAME"
}
```

**Broadcast to All**:
```json
{
  "type": "GAME_STARTED",
  "message": "Quiz started! Good luck!"
}
```

**Then Immediately**:
```json
{
  "type": "QUESTION",
  "question": {
    "index": 0,
    "question": "What is photosynthesis?",
    "options": ["A", "B", "C", "D"]
  }
}
```

---

### 5. Submit Answer

**WebSocket Message**:
```json
{
  "type": "SUBMIT_ANSWER",
  "question_index": 0,
  "answer": "C",
  "time_taken": 12.5
}
```

**Scoring Logic**:
```python
if answer_correct:
    score = max(10, 100 - (2 * time_taken))
else:
    score = 0
```

**Broadcast to All**:
```json
{
  "type": "LEADERBOARD_UPDATE",
  "leaderboard": [
    {"user_id": "user_456", "score": 75},
    {"user_id": "user_123", "score": 50}
  ]
}
```

---

### 6. End Game

**WebSocket Message** (Host or Auto-triggered):
```json
{
  "type": "END_GAME"
}
```

**Broadcast to All**:
```json
{
  "type": "GAME_ENDED",
  "winner": "user_456",
  "final_leaderboard": [
    {"user_id": "user_456", "score": 450},
    {"user_id": "user_123", "score": 380}
  ]
}
```

**Points Awarded**:
- **Winner**: +50 Grind Points
- **Others**: +10 Grind Points (participation)

---

## 📊 Leaderboard & User Stats

### Get User Stats

**Endpoint**: `GET /api/v1/multiplayer/users/{user_id}/stats`

**Response**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_456",
    "grind_points": 150,
    "games_played": 3,
    "wins": 2,
    "badges": ["First Win", "Speed Demon"]
  }
}
```

### Get Room Leaderboard

**Endpoint**: `GET /api/v1/multiplayer/rooms/{room_code}/leaderboard`

**Response**:
```json
{
  "success": true,
  "data": {
    "leaderboard": [
      {"user_id": "user_456", "score": 450},
      {"user_id": "user_123", "score": 380}
    ]
  }
}
```

---

## 👥 Study Groups

### Concept

Students form **groups of 2** to share learning materials. Uploaded PDFs are indexed and accessible to all group members.

### Key Features

- **Maximum 2 members** per group
- **Shared PDF resources** with automatic ingestion
- **Resource metadata tracking** (title, uploader, timestamp)
- **Group-based access control**

---

## 📚 Study Groups Flow

### 1. Create Group

**Endpoint**: `POST /api/v1/groups/create`

**Request**:
```json
{
  "name": "Biology Study Group",
  "creator_id": "user_123"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "group_id": "grp_abc123",
    "name": "Biology Study Group",
    "members": ["user_123"],
    "max_members": 2
  }
}
```

---

### 2. Join Group

**Endpoint**: `POST /api/v1/groups/join`

**Request**:
```json
{
  "group_id": "grp_abc123",
  "user_id": "user_456"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "group_id": "grp_abc123",
    "members": ["user_123", "user_456"]
  }
}
```

---

### 3. Upload Resource

**Endpoint**: `POST /api/v1/groups/{group_id}/upload`

**Request** (multipart/form-data):
```
file: biology_chapter5.pdf
uploaded_by: user_123
title: Chapter 5 - Photosynthesis
```

**Response**:
```json
{
  "success": true,
  "data": {
    "pdf_source_id": "grp_abc123_8a7b3c1d",
    "title": "Chapter 5 - Photosynthesis",
    "group_id": "grp_abc123",
    "uploaded_by": "user_123"
  }
}
```

**What Happens**:
- PDF is ingested into ChromaDB
- Resource is linked to group
- All members can now use this `pdf_source_id` for quizzes

---

### 4. List Resources

**Endpoint**: `GET /api/v1/groups/{group_id}/resources`

**Response**:
```json
{
  "success": true,
  "data": {
    "resources": [
      {
        "pdf_source_id": "grp_abc123_8a7b3c1d",
        "title": "Chapter 5 - Photosynthesis",
        "uploaded_by": "user_123",
        "uploaded_at": "2026-01-17T10:30:00Z"
      }
    ],
    "total": 1
  }
}
```

---

## 🔗 Integration with Existing Features

### Quiz Generation

Group resources can be used for:
- **Competitive quizzes** in Race Mode
- **Flash-Notes generation**
- **Grind Mode practice**
- **Doubt Solver queries**

**Example**:
```json
POST /api/v1/multiplayer/rooms/create
{
  "host_id": "user_123",
  "topic": "Photosynthesis",
  "pdf_source_id": "grp_abc123_8a7b3c1d",  // Group resource
  "num_questions": 5
}
```

---

## 🗄️ State Management

### Current Implementation

**In-Memory Storage** using Python dictionaries:

```python
# GlobalState singleton
state = {
    "rooms": {},           # { room_code: room_data }
    "users": {},           # { user_id: user_stats }
    "study_groups": {},    # { group_id: group_data }
    "resources": {}        # { pdf_source_id: metadata }
}
```

### Thread Safety

- Uses `threading.Lock` for concurrent access
- Safe for multi-threaded FastAPI workers

---

## 🚀 Future Migration to Supabase

See [SUPABASE_SETUP.md](../SUPABASE_SETUP.md) for SQL migration scripts.

**Benefits**:
- Persistent storage (survives server restarts)
- Scalable for large user bases
- Advanced querying capabilities
- Real-time subscriptions

---

## 🎮 WebSocket Message Protocol

### Client → Server

| Type | Description | Payload |
|------|-------------|---------|
| `START_GAME` | Host starts game | None |
| `SUBMIT_ANSWER` | Submit answer | `question_index`, `answer`, `time_taken` |
| `GET_QUESTION` | Request next question | `question_index` |
| `CHAT_MESSAGE` | Send chat message | `message` |
| `END_GAME` | End game | None |

### Server → Client

| Type | Description | Payload |
|------|-------------|---------|
| `GAME_STARTED` | Game has started | `message` |
| `QUESTION` | Quiz question | `index`, `question`, `options` |
| `LEADERBOARD_UPDATE` | Score update | `leaderboard` array |
| `CHAT_MESSAGE` | Chat broadcast | `user_id`, `message` |
| `GAME_ENDED` | Game finished | `winner`, `final_leaderboard` |
| `ERROR` | Error occurred | `message` |

---

## 📝 Example Frontend Flow

```javascript
// 1. Create room
const createResponse = await fetch('/api/v1/multiplayer/rooms/create', {
  method: 'POST',
  body: JSON.stringify({
    host_id: 'user_123',
    topic: 'Biology',
    pdf_source_id: 'bio_001',
    num_questions: 5
  })
});
const { room_code } = await createResponse.json();

// 2. Connect WebSocket
const ws = new WebSocket(`ws://localhost:8000/api/v1/multiplayer/ws/race/${room_code}/user_123`);

// 3. Wait for players to join...

// 4. Start game (host only)
ws.send(JSON.stringify({ type: 'START_GAME' }));

// 5. Handle questions
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  if (msg.type === 'QUESTION') {
    // Display question
    const startTime = Date.now();
    
    // User selects answer
    const answer = getUserAnswer();
    const time_taken = (Date.now() - startTime) / 1000;
    
    // Submit answer
    ws.send(JSON.stringify({
      type: 'SUBMIT_ANSWER',
      question_index: msg.question.index,
      answer: answer,
      time_taken: time_taken
    }));
  }
  
  if (msg.type === 'LEADERBOARD_UPDATE') {
    updateUI(msg.leaderboard);
  }
  
  if (msg.type === 'GAME_ENDED') {
    showResults(msg.winner, msg.final_leaderboard);
  }
};
```

---

## 🛡️ Security Considerations

### Current State

- **No authentication** (placeholder `user_id` strings)
- **No room passwords** (anyone with code can join)
- **No rate limiting**

### Future Enhancements

1. **JWT-based authentication**
2. **Room passwords** for private games
3. **Anti-cheat measures** (server-side answer validation)
4. **Rate limiting** on WebSocket messages

---

## 🎯 Best Practices

### For Hosts

1. Wait for all players to join before starting
2. Use meaningful room codes (share via chat/link)
3. Choose appropriate quiz difficulty

### For Players

1. Connect WebSocket **before** game starts
2. Handle disconnections gracefully (reconnect logic)
3. Submit answers promptly (time-based scoring)

### For Developers

1. Always validate user input (answer format, time_taken)
2. Handle WebSocket disconnects cleanly
3. Use try-except blocks for all state operations
4. Test with multiple concurrent connections

---

## 📊 Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Quiz Generation Time | < 10s | ~5-8s |
| WebSocket Latency | < 100ms | ~50ms (local) |
| Max Concurrent Players | 10+ per room | Tested: 5 |
| State Access Time | < 1ms | ~0.5ms (in-memory) |

---

## 🐛 Troubleshooting

### Issue: "Room not found"

- Verify room code is correct (case-sensitive)
- Check if room was deleted after game ended

### Issue: WebSocket disconnects

- Network instability (implement reconnect logic)
- Server restart (in-memory state is lost)

### Issue: Quiz not generating

- Check if `pdf_source_id` exists in ChromaDB
- Verify Groq API key is configured
- Check server logs for errors

---

## 📚 API Reference

See [API_README.md](./API_README.md) for complete endpoint documentation.

**Quick Links**:
- [Multiplayer Endpoints](#)
- [Study Group Endpoints](#)
- [WebSocket Protocol](#)

---

## 🎉 Conclusion

The Competitive Multiplayer and Study Groups features transform Rooster-HackCrypt from a solo learning tool into a **collaborative, competitive platform**. Students can now:

- **Compete** in real-time quiz battles
- **Collaborate** by sharing study materials
- **Track** their progress with stats and badges
- **Engage** in a gamified learning experience

**Next Steps**: Migrate to Supabase for persistent storage and scalability!
