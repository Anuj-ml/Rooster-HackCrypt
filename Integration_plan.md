# 🔗 Frontend-Backend Integration Plan

**Status:** ❓ Questions Phase  
**Date:** January 17, 2026  
**Context:** Hackathon Sprint - Student Priority

---

## Current State Summary

| Component | Status |
|-----------|--------|
| Backend API | ✅ Fully functional (8 routers, 25+ endpoints) |
| Frontend UI | ✅ Styled and interactive (Kwest platform) |
| Integration | ❌ **ZERO** - No API calls exist between them |

---

## 🔐 Section 1: Authentication

**Current State:** Frontend uses localStorage (`kwest_user`), backend has no auth.

### Q1.1: Authentication Approach
Which authentication should we use?
- [ ] A) Supabase Auth (already configured in frontend)
- [ ] B) Custom JWT (backend issues tokens)
- [y] C) Keep localStorage only (no real auth for hackathon)
- [ ] D) Other: _______________

### Q1.2: User Roles
Frontend has Student/Teacher roles. How should backend handle this?
- [ ] A) Enforce roles (different permissions)
- [y] B) Ignore roles (anyone can access anything)
- [ ] C) Soft roles (frontend controls, backend is open)

### Q1.3: Where does user_id come from?
- [ ] A) Use localStorage username as user_id
- [y] B) Generate UUID on first visit
- [ ] C) Require login to get user_id
- [ ] D) Other: _______________

---

## 📚 Section 2: Materials & Ingestion

### Q2.1: Who can upload materials?
- [ ] A) Teachers only
- [y] B) Both students and teachers
- [ ] C) Students only in study groups, teachers globally
- [ ] D) Anyone (open for hackathon demo)

### Q2.2: Where should PDF upload UI be?
- [ ] A) Teacher dashboard only (exists but not connected)
- [ ] B) Student dashboard too
- [y] C) Dedicated "Library" page
- [ ] D) Study Groups section only

### Q2.3: Should students be able to ingest YouTube videos?
- [y] A) Yes, anywhere
- [ ] B) Yes, but only in study groups
- [ ] C) No, teacher-only feature
- [ ] D) Skip YouTube for hackathon

### Q2.4: Should students be able to generate syllabus topics?
- [y] A) Yes
- [ ] B) No, teacher-only
- [ ] C) Skip for hackathon

### Q2.5: Material browser UI - where should it appear?
- [ ] A) Dedicated page
- [ ] B) Within dashboard sidebar
- [y] C) Only shown during quiz setup
- [ ] D) Skip - pre-load some demo materials

---

## 🎯 Section 3: Quiz System (CORE FEATURE)

### Q3.1: Where should quiz-taking happen?
- [ ] A) New dedicated page (`quiz.html`)
- [ ] B) Modal/overlay within dashboard
- [ ] C) Replace current code editor area
- [ ] D) New view/section in dashboard (like courses view)
- [y] E) in the "Practice mode"

### Q3.2: How do students start a quiz?
- [y] A) Select material → topic → difficulty → Start
- [ ] B) Click "Quick Quiz" (use defaults)
- [ ] C) Both options
- [ ] D) Other: _______________

### Q3.3: Should we show Adaptive vs Grind mode choice?
- [ ] A) Yes, let user choose
- [ ] B) Default to Adaptive, hide Grind
- [ ] C) Default to Grind, hide Adaptive
- [y] D) Show both but explain difference

### Q3.4: How many questions per quiz by default?
- [ ] A) 5 questions
- [ ] B) 10 questions
- [y] C) Let user choose (slider/dropdown) but by default 4 questions per batch
- [ ] D) Other: _______________

### Q3.5: Question display format?
- [y] A) One question at a time (with next button)
- [ ] B) All questions on one page (scroll)
- [ ] C) One at a time with timer
- [ ] D) Other: _______________

### Q3.6: After answering a question, what happens?
- [ ] A) Immediately show correct/incorrect
- [ ] B) Wait until end to show all results
- [y] C) Show correct/incorrect + explanation immediately
- [ ] D) Let user configure this

### Q3.7: What should quiz results screen show?
(Select all that apply)
- [y] Score percentage
- [y] Correct/incorrect per question
- [y] Explanations for wrong answers
- [y] Difficulty change info
- [y] Mastery score
- [y] AI Sensei analysis
- [y] XP earned

### Q3.8: Should quiz results integrate with frontend XP system?
- [y] A) Yes, award XP based on score
- [ ] B) No, keep systems separate
- [ ] C) Yes, but track separately (show both)

---

## 🧠 Section 4: Smart Learning Features

### Q4.1: Socratic Hints - when to offer?
- [ ] A) Button on each question ("Get Hint")
- [ ] B) Only after wrong answer
- [y] C) Both - button always visible, auto-show after wrong
- [ ] D) Skip for hackathon

### Q4.2: AI Sensei (session analysis) - when to show?
- [ ] A) Automatically after every quiz
- [ ] B) Button on results page ("Get AI Feedback")
- [y] C) Both - auto-show but collapsible
- [ ] D) Skip for hackathon

---

## 🤔 Section 5: Doubt Solver

### Q5.1: Where should Doubt Solver UI appear?
- [ ] A) Floating chat widget (always visible)
- [ ] B) Dedicated page
- [ ] C) Panel within dashboard
- [y] D) Only accessible during quiz
- [ ] E) Skip for hackathon

### Q5.2: If chat widget, which corner?
- [ ] A) Bottom-right
- [ ] B) Bottom-left
- [ ] C) Top-right
- [y] D) N/A (not using widget)

### Q5.3: Should doubt solver require selecting a material first?
- [ ] A) Yes, dropdown to select source
- [y] B) Auto-use current quiz material if in quiz
- [ ] C) Search all materials (no selection needed)

---

## ⚡ Section 6: Flash Notes

### Q6.1: Where should Flash Notes UI appear?
- [ ] A) Dedicated page
- [y] B) Panel in dashboard
- [ ] C) Pre-quiz option ("Study first")
- [ ] D) Post-quiz option ("Review weak areas")
- [ ] E) Multiple: Option C and D both
- [ ] F) Skip for hackathon

### Q6.2: Flash notes display format?
- [y] A) Simple bullet list
- [ ] B) Flip cards (flashcard style)
- [ ] C) Expandable sections
- [ ] D) Other: _______________

---

## 👥 Section 7: Study Groups

### Q7.1: Where should Study Groups UI appear?
- [ ] A) Dedicated page (`groups.html`)
- [y] B) Within existing "Collaborate" nav item
- [ ] C) Dashboard panel/tab
- [ ] D) Skip for hackathon

### Q7.2: How do users join groups?
- [ ] A) Browse list and click join
- [ ] B) Enter group ID/code
- [y] C) Both options
- [ ] D) Other: _______________

### Q7.3: What should group detail page show?
(Select all that apply)
- [y] Group name
- [y] Member list (max 2)
- [y] Shared resources list
- [y] Upload button for PDFs
- [y] "Start Quiz from group material" button
- [y] Leave group button

### Q7.4: Should group resources integrate with quiz flow?
- [ ] A) Yes, show group materials in quiz material selector
- [ ] B) Yes, separate "Group Quiz" button
- [y] C) No, keep separate
- [ ] D) Other: _______________

---

## 🏆 Section 8: Gamification Integration

### Q8.1: Should backend quiz scores affect frontend XP?
- [ ] A) Yes, directly add XP
- [y] B) Yes, with multipliers (difficulty bonus)
- [ ] C) No, keep systems separate
- [ ] D) Other: _______________

### Q8.2: Should quiz completion trigger badge checks?
- [ ] A) Yes, implement badge logic
- [ ] B) No, skip for hackathon
- [y] C) Show placeholder badge animation

### Q8.3: Should we show a leaderboard?
- [ ] A) Yes, global
- [ ] B) Yes, per-material
- [y] C) Yes, within study group
- [ ] D) No, skip for hackathon

---

## 🖥️ Section 9: UI/UX Decisions

### Q9.1: Loading states - how should they look?
- [ ] A) Full-page cyber-themed loader
- [ ] B) Inline spinners
- [ ] C) Skeleton screens
- [y] D) Simple text ("Loading...")

### Q9.2: Error handling - how to show errors?
- [y] A) Toast notifications (corner popup)
- [ ] B) Modal dialogs
- [ ] C) Inline error messages
- [ ] D) Other: _______________

### Q9.3: Backend connection status - show indicator?
- [ ] A) Yes, always visible (green/red dot)
- [ ] B) Only show when disconnected
- [y] C) No indicator needed

### Q9.4: Mobile support priority?
- [ ] A) Must work on mobile
- [ ] B) Desktop-first, mobile later
- [y] C) Desktop-only for hackathon

---

## 👩‍🏫 Section 10: Teacher Portal

### Q10.1: Teacher portal priority for hackathon?
- [y] A) Full integration (upload, view students, analytics)
- [ ] B) Just material upload connection
- [ ] C) Skip teacher portal, focus on student
- [ ] D) Other: _______________

### Q10.2: If including teacher features, which ones?
(Select all that apply)
- [y] Material upload (PDF)
- [ ] YouTube ingestion
- [y] Syllabus generation
- [y] View all materials
- [y] Student progress viewing
- [y] Analytics dashboard

---

## 🔧 Section 11: Technical Setup

### Q11.1: API base URL configuration?
- [ ] A) Hardcode `localhost:8000`
- [ ] B) Use `.env` file
- [ ] C) Auto-detect (localhost in dev, domain in prod)

### Q11.2: Should we add a "Demo Mode" with pre-loaded materials?
- [ ] A) Yes, include sample PDFs in backend
- [y] B) No, user must upload
- [ ] C) Yes, and skip upload UI entirely for demo

### Q11.3: CORS - is it configured on backend?
- [ ] A) Yes, already set up
- [ ] B) No, needs configuration
- [y] C) Unknown, need to check

---

## 📋 Section 12: Priority & Scope

### Q12.1: MVP Features - which are MUST HAVE?
(Rank 1-5, where 1 = highest priority)
- [y] Quiz system (start, take, results): ___
- [y] Material selector: ___
- [y] Doubt solver: ___
- [y] Flash notes: ___
- [y] Study groups: ___
- [y] AI Sensei analysis: ___
- [y] Socratic hints: ___
- [y] Teacher upload: ___
- [y] XP integration: ___

### Q12.2: What can we skip for hackathon?
(Select all that apply)
- [ ] Doubt solver
- [ ] Flash notes
- [ ] Study groups
- [ ] AI Sensei
- [ ] Socratic hints
- [ ] Teacher portal
- [y] Leaderboard
- [y] Mobile support

### Q12.3: Estimated time available?
- [y] A) 2-4 hours
- [ ] B) 4-8 hours
- [ ] C) 8-12 hours
- [ ] D) 12+ hours

---

## ✏️ Your Answers



**Please fill in your answers below using this format:**

```
Q1.1: C
Q1.2: C
Q1.3: A
Q2.1: D
Q2.2: D
...etc
```

**Or mark the checkboxes above directly.**

---

## Next Steps

Once you answer these questions, I will:
1. Create the complete implementation plan
2. Define file structure for new components
3. Build the integration in priority order
4. Test each feature as we go

**Ready when you are! 🚀**
