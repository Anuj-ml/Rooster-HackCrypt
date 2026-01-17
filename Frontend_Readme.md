# 🎨 Frontend Documentation - Kwest (Rooster-HackCrypt UI)

## Overview

The frontend for Rooster-HackCrypt is a **cyber-futuristic, gamified coding education platform** called **Kwest**. It features a Single Page Application (SPA) architecture with an immersive visual design inspired by platforms like Codedex, combining modern web technologies with retro gaming aesthetics.

**Status:** 🚧 In Progress (v1.0.0)  
**Tech Stack:** Vanilla HTML/CSS/JavaScript (No framework dependencies)  
**Design Philosophy:** Cyber/Cozy aesthetic with real-time feedback and gamification

---

## 📁 Project Structure

```
fontend/
├── index.html                 # Main entry point (landing page)
├── dashboard.html             # Student dashboard
├── login.html                 # Authentication page (login)
├── signup.html                # User registration page
├── teacher.html               # Teacher dashboard
├── teacher.js                 # Teacher functionality
├── teacher.css                # Teacher-specific styles
├── start_server.py            # Local development server
├── .env                       # Environment variables
├── README.md                  # Project overview
│
├── styles/                    # CSS Modules
│   ├── cyber-engine.css       # Core cyber theme & animations
│   ├── hero-effects.css       # Landing page hero effects
│   ├── components.css         # Reusable UI components
│   ├── gamification.css       # XP, badges, progress bars
│   ├── ide-cozy.css           # Code editor styling
│   ├── ui-engine.css          # UI interaction styles
│   ├── theme.css              # Color variables & themes
│   ├── codedex.css            # Codedex-inspired styles
│   ├── codedex-clone.css      # Additional Codedex elements
│   ├── app.css                # Application-wide styles
│   ├── pixel-icons.css        # Pixel art icon styles
│   └── mobile.css             # Responsive mobile styles
│
├── scripts/                   # JavaScript Modules
│   ├── main.js                # Application entry point
│   ├── app.js                 # Main application logic
│   ├── bootloader.js          # Initialization sequence
│   ├── cyber-app.js           # Cyber theme controller
│   ├── app-codedex.js         # Codedex-style interactions
│   ├── minecode.js            # Code editor logic
│   ├── lattice.js             # Background grid effects
│   ├── supabase-client.js     # Supabase integration
│   ├── remove_bg.py           # Image processing utility
│   │
│   ├── core/                  # Core modules
│   │   ├── config.js          # Configuration settings
│   │   ├── router.js          # SPA routing
│   │   ├── nav.js             # Navigation logic
│   │   └── supabase.js        # Supabase client setup
│   │
│   ├── modules/               # Feature modules
│   │   └── [curriculum, auth, gamification modules]
│   │
│   ├── data/                  # Static data & curriculum
│   │   └── [course content, exercises, lessons]
│   │
│   └── effects/               # Visual effects
│       └── [particle systems, animations]
│
├── assets/                    # Media files
│   ├── images/                # Graphics & icons
│   ├── videos/                # Background videos
│   └── audio/                 # Sound effects
│
├── fonts/                     # Custom font files
│   └── [Minecraft, pixel fonts]
│
└── blueprint/                 # Design documents
    └── the blueprint.txt      # Detailed feature specs
```

---

## 🎯 Key Features & Pages

### 1. **Landing Page** (`index.html`)

**Purpose:** First impression, hero section, course catalog preview

**Layout:**
- **Hero Section**
  - Animated Matrix-style background canvas
  - CRT overlay with scanlines effect
  - Floating particles
  - Central call-to-action button
  
- **Navigation Bar**
  - Brand logo with cyber glow effect
  - Course catalog dropdown
  - Login/Signup buttons
  - User profile (when authenticated)

- **Course Showcase**
  - Card-based layout
  - Course thumbnails with hover effects
  - Progress indicators
  - Badge displays

**Key Components:**
```html
<div class="cyber-bg">
  <canvas id="matrix-canvas"></canvas>
  <div class="crt-overlay"></div>
  <div class="grid-overlay"></div>
  <div class="floating-particles"></div>
</div>
```

**Scripts:**
- `cyber-engine.css` - Main theme
- `hero-effects.css` - Landing animations
- `lattice.js` - Grid background
- `main.js` - App initialization

---

### 2. **Dashboard** (`dashboard.html`)

**Purpose:** Student learning hub, progress tracking, course navigation

**Layout:**
- **Sidebar Navigation**
  - Course list with icons
  - Lesson tree/chapters
  - Progress percentage
  - Quick stats (XP, streak, badges)

- **Main Content Area**
  - Active lesson display
  - Code editor workspace
  - Terminal output section
  - Hint system panel

- **Stats Panel (Right)**
  - Total XP counter
  - Current streak
  - Badges earned
  - Leaderboard position

**Gamification Elements:**
- **XP System** - Points for completing lessons
- **Streak Counter** - Daily coding habit tracker
- **Badge Unlocks** - Achievement system
- **Progress Bars** - Visual completion tracking

**Key Features:**
```javascript
// Example: XP tracking
const updateXP = (points) => {
  currentXP += points;
  animateXPGain(points);
  checkLevelUp();
  updateProgressBar();
};
```

---

### 3. **Interactive Code Editor**

**Purpose:** In-browser coding environment with real-time feedback

**Components:**
- **Code Workspace**
  - Syntax highlighting
  - Line numbers
  - Auto-indentation
  - Monaco Editor integration (optional)

- **Terminal Output**
  - Simulated Python execution
  - Console.log display
  - Error messages
  - Test case results

- **Controls**
  - Run button
  - Reset button
  - Submit solution
  - Request hint

**Styling:**
```css
/* ide-cozy.css */
.code-editor {
  background: #1e1e2e;
  border: 2px solid var(--cyber-blue);
  font-family: 'Fira Code', monospace;
  border-radius: 8px;
}
```

**Functionality:**
- Real-time syntax validation
- Simulated Python interpreter
- Test case validation
- Smart hints (not direct answers)

---

### 4. **Authentication Pages**

#### `login.html`
- Email/password fields
- OAuth options (Google, GitHub)
- "Forgot password" link
- Redirect to signup

#### `signup.html`
- Username creation
- Email registration
- Password strength meter
- Terms acceptance
- Redirect to dashboard

**Supabase Integration:**
```javascript
// supabase-client.js
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)

// Login
await supabase.auth.signInWithPassword({
  email: email,
  password: password
})
```

---

### 5. **Teacher Dashboard** (`teacher.html`)

**Purpose:** Instructor view for managing courses and students

**Features:**
- Student progress analytics
- Assignment creation
- Grade management
- Announcement system
- Resource uploads

**Layout:**
- Class roster table
- Analytics charts
- Content management panel
- Communication tools

---

## 🎨 Design System

### Color Palette

```css
/* theme.css */
:root {
  /* Primary Colors */
  --cyber-blue: #00d4ff;
  --cyber-purple: #a855f7;
  --cyber-pink: #ec4899;
  --neon-green: #00ff88;
  --warning-orange: #ffc800;
  
  /* Background */
  --bg-dark: #0a0a0f;
  --bg-card: #1a1a2e;
  --bg-input: #16213e;
  
  /* Text */
  --text-primary: #ffffff;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  
  /* Accent */
  --glow-blue: rgba(0, 212, 255, 0.5);
  --glow-purple: rgba(168, 85, 247, 0.5);
}
```

### Typography

```css
/* Fonts */
--font-heading: 'Press Start 2P', cursive;  /* Retro pixel font */
--font-body: 'Inter', 'Outfit', sans-serif; /* Modern readable */
--font-code: 'Fira Code', monospace;         /* Code editor */
```

### Components Library

#### Buttons
```css
.cyber-button {
  background: linear-gradient(135deg, var(--cyber-blue), var(--cyber-purple));
  border: 2px solid var(--cyber-blue);
  box-shadow: 0 0 20px var(--glow-blue);
  transition: all 0.3s ease;
}

.cyber-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px var(--glow-blue);
}
```

#### Cards
```css
.course-card {
  background: var(--bg-card);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  padding: 24px;
  backdrop-filter: blur(10px);
}
```

#### Progress Bars
```css
.progress-bar {
  background: var(--bg-input);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, var(--cyber-blue), var(--neon-green));
  height: 100%;
  transition: width 0.5s ease;
}
```

---

## ⚙️ Core Functionality

### SPA Router (`scripts/core/router.js`)

```javascript
// Client-side routing without page reloads
const routes = {
  '/': 'landing',
  '/dashboard': 'dashboard',
  '/courses/:id': 'courseDetail',
  '/lesson/:id': 'lesson',
  '/profile': 'profile'
};

function navigateTo(path) {
  history.pushState(null, null, path);
  renderRoute(path);
}
```

### Curriculum System (`scripts/modules/`)

**Structure:**
```javascript
const pythonCourse = {
  id: 'python-basics',
  title: 'The Legend of Python',
  chapters: [
    {
      id: 'ch1-hello-world',
      title: 'Chapter 1: Hello World',
      lessons: [
        {
          id: 'lesson-1',
          title: 'Your First Program',
          story: '...',
          exercises: [...],
          xpReward: 50
        }
      ]
    }
  ]
};
```

### Gamification Logic

```javascript
// XP System
function awardXP(userId, amount, reason) {
  const user = getUser(userId);
  user.xp += amount;
  
  // Check for level up
  const newLevel = calculateLevel(user.xp);
  if (newLevel > user.level) {
    triggerLevelUpAnimation();
    unlockBadge('level-' + newLevel);
  }
  
  // Update UI
  updateXPDisplay(user.xp);
}

// Streak Tracking
function checkStreak(userId) {
  const lastActive = getLastActiveDate(userId);
  const today = new Date();
  
  if (isConsecutiveDay(lastActive, today)) {
    incrementStreak(userId);
  } else {
    resetStreak(userId);
  }
}
```

---

## 🎭 Visual Effects

### Matrix Background

```javascript
// lattice.js
const canvas = document.getElementById('matrix-canvas');
const ctx = canvas.getContext('2d');

const characters = 'アイウエオカキクケコサシスセソタチツテト0123456789';
const fontSize = 16;
const columns = canvas.width / fontSize;
const drops = Array(Math.floor(columns)).fill(1);

function drawMatrix() {
  ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  ctx.fillStyle = '#0F0';
  ctx.font = fontSize + 'px monospace';
  
  for (let i = 0; i < drops.length; i++) {
    const text = characters.charAt(Math.floor(Math.random() * characters.length));
    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
    
    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
      drops[i] = 0;
    }
    drops[i]++;
  }
}

setInterval(drawMatrix, 33);
```

### Glow Effects

```css
/* Cyber glow animation */
@keyframes cyber-pulse {
  0%, 100% {
    box-shadow: 0 0 10px var(--cyber-blue),
                0 0 20px var(--cyber-blue),
                0 0 30px var(--cyber-blue);
  }
  50% {
    box-shadow: 0 0 20px var(--cyber-blue),
                0 0 40px var(--cyber-blue),
                0 0 60px var(--cyber-blue);
  }
}

.cyber-glow {
  animation: cyber-pulse 2s ease-in-out infinite;
}
```

### Particle System

```javascript
// effects/particles.js
class Particle {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.vx = (Math.random() - 0.5) * 2;
    this.vy = (Math.random() - 0.5) * 2;
    this.life = 100;
  }
  
  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.life--;
  }
  
  draw(ctx) {
    ctx.fillStyle = `rgba(0, 212, 255, ${this.life / 100})`;
    ctx.fillRect(this.x, this.y, 2, 2);
  }
}
```

---

## 🔗 Backend Integration

### API Endpoints

```javascript
// config.js
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Fetch user progress
async function getUserProgress(userId) {
  const response = await fetch(`${API_BASE_URL}/users/${userId}/progress`);
  return await response.json();
}

// Submit exercise
async function submitExercise(exerciseId, code) {
  const response = await fetch(`${API_BASE_URL}/exercises/${exerciseId}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code })
  });
  return await response.json();
}
```

### Supabase Integration

```javascript
// Real-time subscriptions
const progressChannel = supabase
  .channel('user-progress')
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'user_progress',
    filter: `user_id=eq.${userId}`
  }, (payload) => {
    updateProgressUI(payload.new);
  })
  .subscribe();
```

---

## 📱 Responsive Design

### Breakpoints

```css
/* mobile.css */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    position: fixed;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .code-editor {
    height: 300px; /* Smaller on mobile */
  }
}

@media (max-width: 480px) {
  .nav-brand {
    font-size: 16px;
  }
  
  .course-card {
    padding: 16px;
  }
}
```

### Mobile Navigation

```javascript
// Hamburger menu
const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.getElementById('sidebar');

menuToggle.addEventListener('click', () => {
  sidebar.classList.toggle('open');
});
```

---

## 🚀 Development Workflow

### Local Development

```bash
# Start development server
python start_server.py

# Server runs on http://localhost:8080
```

### File Watching

```javascript
// Auto-reload on file changes (if using build tools)
// Currently: Manual refresh required
```

### Testing

```javascript
// Unit tests for core functions
describe('XP System', () => {
  test('awards correct XP amount', () => {
    const user = { xp: 0 };
    awardXP(user.id, 50, 'lesson-complete');
    expect(user.xp).toBe(50);
  });
});
```

---

## 🎯 Future Enhancements

### Planned Features
- [ ] **React Migration** - Move to React for better state management
- [ ] **Monaco Editor** - Replace custom editor with VS Code's editor
- [ ] **WebSocket Support** - Real-time multiplayer coding challenges
- [ ] **AR Mode** - A-Frame integration for VR lessons
- [ ] **Audio Integration** - Background music and sound effects
- [ ] **Mobile App** - React Native version
- [ ] **AI Hints** - GPT-powered smart hints
- [ ] **Code Replay** - Record and replay coding sessions

### Performance Optimizations
- [ ] Lazy loading for course content
- [ ] Image optimization and WebP conversion
- [ ] CSS/JS minification
- [ ] Service worker for offline support
- [ ] IndexedDB for local storage

---

## 🐛 Known Issues

1. **Safari Compatibility** - Some CSS grid features don't work on older Safari
2. **Mobile Performance** - Matrix background can lag on low-end devices
3. **Font Loading** - Flash of unstyled text (FOUT) on slow connections
4. **Auth Persistence** - Refresh clears session (needs localStorage)

---

## 📚 Dependencies

### External Libraries
- **Anime.js** - Animation library
- **Lucide Icons** - Icon set
- **Pixel Art Icons** - Retro icon pack
- **Supabase JS** - Backend client
- **Google Fonts** - Typography

### CDN Links
```html
<script src="https://unpkg.com/lucide@latest"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.2/anime.min.js"></script>
<link href="https://unpkg.com/pixelarticons@1.8.1/css/pixelarticons.css" rel="stylesheet">
```

---

## 🤝 Contributing

### Code Style
- Use 2-space indentation
- Follow BEM naming for CSS classes
- Add JSDoc comments for functions
- Keep files under 500 lines

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-lesson

# Make changes and commit
git add .
git commit -m "Add Python loops lesson"

# Push to remote
git push origin feature/new-lesson
```

---

## 📄 License

MIT License - Free to use, modify, and distribute.

---

## 📞 Support

- **Documentation:** [Full Docs](./blueprint/the%20blueprint.txt)
- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Discord:** [Join Community](#)
- **Email:** support@kwest.dev

---

**Version:** 1.0.0  
**Last Updated:** January 17, 2026  
**Maintained by:** Kwest Team

---

*Built with ❤️ for the next generation of coders*
