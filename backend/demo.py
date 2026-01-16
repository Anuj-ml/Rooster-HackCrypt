# backend/demo.py

"""
Rooster-HackCrypt: Menu-Driven CLI Demo

This script provides an interactive command-line interface for:
1. Document Ingestion - Upload and index PDFs
2. Adaptive Mode - Auto-adjusting difficulty quizzes
3. Grind Mode - Fixed/slow-dynamic difficulty practice

All features are accessible through a user-friendly menu system.
"""

import sys
import os

# Add parent to path for imports
sys.path.insert(0, '.')

from ingestion_main import (
    upload_new_material,
    list_indexed_pdfs,
    get_knowledge_base,
    get_llm_model,
    get_embedding_model
)

from quiz_generation_main import (
    start_student_session,
    start_grind_session,
    get_next_quiz_batch,
    submit_quiz_results,
    format_quiz_for_display,
    get_session_stats,
    print_session_summary,
    list_active_sessions,
    delete_session,
    get_quiz_config,
    get_grind_config,
    kb,
    agent,
    ADAPTIVE_ENGINE
)

from grind_mode import GrindMode, grind_practice_loop
from difficulty_engine import DEFAULT_QUIZ_CONFIG, DEFAULT_GRIND_CONFIG


# ═══════════════════════════════════════════════════════════════════════════════
# MENU DISPLAY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def print_header():
    """Print the application header."""
    print(f"\n{'═'*60}")
    print(f"🐓 ROOSTER-HACKCRYPT")
    print(f"   AI-Powered Adaptive Quiz Generator")
    print(f"{'═'*60}")


def print_main_menu():
    """Print the main menu options."""
    print(f"\n{'─'*40}")
    print("📋 MAIN MENU")
    print(f"{'─'*40}")
    print("  1. 📄 Document Ingestion")
    print("  2. 🎯 Adaptive Mode (Quiz)")
    print("  3. 🏋️ Grind Mode (Practice)")
    print("  4. 📊 Session Management")
    print("  5. ⚙️ View Configuration")
    print("  0. 🚪 Exit")
    print(f"{'─'*40}")


def print_ingestion_menu():
    """Print document ingestion menu options."""
    print(f"\n{'─'*40}")
    print("📄 DOCUMENT INGESTION")
    print(f"{'─'*40}")
    print("  1. Upload new PDF")
    print("  2. List indexed PDFs")
    print("  0. Back to main menu")
    print(f"{'─'*40}")


def print_adaptive_menu():
    """Print adaptive mode menu options."""
    print(f"\n{'─'*40}")
    print("🎯 ADAPTIVE MODE")
    print(f"{'─'*40}")
    print("  1. Start new adaptive session")
    print("  2. Take a quiz (requires active session)")
    print("  3. View session stats")
    print("  4. Run demo (automated)")
    print("  0. Back to main menu")
    print(f"{'─'*40}")


def print_grind_menu():
    """Print grind mode menu options."""
    print(f"\n{'─'*40}")
    print("🏋️ GRIND MODE")
    print(f"{'─'*40}")
    print("  1. Start new grind session")
    print("  2. Take a quiz (requires active session)")
    print("  3. View session stats")
    print("  4. Run demo (automated)")
    print("  0. Back to main menu")
    print(f"{'─'*40}")


def print_session_menu():
    """Print session management menu options."""
    print(f"\n{'─'*40}")
    print("📊 SESSION MANAGEMENT")
    print(f"{'─'*40}")
    print("  1. List all sessions")
    print("  2. View session details")
    print("  3. Delete a session")
    print("  0. Back to main menu")
    print(f"{'─'*40}")


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_menu_choice(prompt: str = "Enter choice: ", valid_options: list = None) -> str:
    """Get a menu choice from the user."""
    while True:
        choice = input(prompt).strip()
        if valid_options is None or choice in valid_options:
            return choice
        print(f"Invalid choice. Please enter one of: {', '.join(valid_options)}")


def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def get_difficulty_choice() -> str:
    """Get difficulty choice from user."""
    print("\n  Select difficulty:")
    print("    1. EASY")
    print("    2. MEDIUM")
    print("    3. HARD")
    choice = get_menu_choice("  Choice (1/2/3): ", ['1', '2', '3'])
    return {'1': 'EASY', '2': 'MEDIUM', '3': 'HARD'}[choice]


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input from user."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    if not response:
        return default
    return response in ['y', 'yes', '1', 'true']


def select_pdf() -> str:
    """Let user select a PDF from indexed list."""
    sources = kb.get_all_pdf_sources()
    
    if not sources:
        print("\n⚠️ No PDFs indexed! Please upload a PDF first.")
        return None
    
    print(f"\n📚 Available PDFs:")
    for i, src in enumerate(sources, 1):
        print(f"    {i}. {src}")
    
    if len(sources) == 1:
        print(f"\n  Using: {sources[0]}")
        return sources[0]
    
    while True:
        choice = input(f"  Select PDF (1-{len(sources)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sources):
                return sources[idx]
        except ValueError:
            pass
        print(f"  Invalid choice. Enter a number between 1 and {len(sources)}")


def select_session() -> str:
    """Let user select an active session."""
    sessions = list_active_sessions()
    
    if not sessions:
        print("\n⚠️ No active sessions! Please start a session first.")
        return None
    
    print(f"\n📋 Active Sessions:")
    for i, sid in enumerate(sessions, 1):
        try:
            stats = get_session_stats(sid)
            print(f"    {i}. {sid[:20]}... ({stats['mode']}, {stats['current_difficulty']})")
        except:
            print(f"    {i}. {sid[:20]}...")
    
    if len(sessions) == 1:
        print(f"\n  Using: {sessions[0][:30]}...")
        return sessions[0]
    
    while True:
        choice = input(f"  Select session (1-{len(sessions)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sessions):
                return sessions[idx]
        except ValueError:
            pass
        print(f"  Invalid choice. Enter a number between 1 and {len(sessions)}")


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT INGESTION HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def handle_upload_pdf():
    """Handle PDF upload process."""
    print("\n📄 UPLOAD NEW PDF")
    print(f"{'─'*40}")
    
    pdf_path = get_input("Enter PDF path (e.g., ip_data/file.pdf)")
    
    if not os.path.exists(pdf_path):
        print(f"\n❌ File not found: {pdf_path}")
        return
    
    source_id = get_input("Enter source ID (unique identifier)", 
                          os.path.splitext(os.path.basename(pdf_path))[0])
    
    try:
        upload_new_material(pdf_path, source_id)
        print("\n✅ PDF uploaded successfully!")
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")


def handle_ingestion_menu():
    """Handle document ingestion submenu."""
    while True:
        print_ingestion_menu()
        choice = get_menu_choice("Enter choice: ", ['0', '1', '2'])
        
        if choice == '0':
            return
        elif choice == '1':
            handle_upload_pdf()
        elif choice == '2':
            list_indexed_pdfs()


# ═══════════════════════════════════════════════════════════════════════════════
# ADAPTIVE MODE HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def handle_start_adaptive_session():
    """Handle starting a new adaptive session."""
    print("\n🎯 START ADAPTIVE SESSION")
    print(f"{'─'*40}")
    
    pdf_id = select_pdf()
    if not pdf_id:
        return None
    
    user_id = get_input("Enter user ID", "user_001")
    topic = get_input("Enter topic for quiz generation")
    
    if not topic:
        print("\n❌ Topic is required!")
        return None
    
    print("\n  Starting difficulty:")
    difficulty = get_difficulty_choice()
    
    session = start_student_session(
        user_id=user_id,
        pdf_id=pdf_id,
        topic=topic,
        initial_difficulty=difficulty
    )
    
    return session


def handle_take_adaptive_quiz():
    """Handle taking an adaptive quiz."""
    session_id = select_session()
    if not session_id:
        return
    
    # Generate quiz
    quiz = get_next_quiz_batch(session_id)
    
    if not quiz:
        print("\n❌ Failed to generate quiz!")
        return
    
    # Display quiz
    format_quiz_for_display(quiz, show_answers=False)
    
    # Get answers
    print("\n📝 SUBMIT YOUR ANSWERS")
    print("  Enter 'a', 'b', 'c', or 'd' for each question")
    print("  Press Enter to skip (counts as wrong)")
    
    results = []
    letters = ['a', 'b', 'c', 'd']
    
    for i, q in enumerate(quiz.questions, 1):
        # Find correct answer letter
        correct_letter = 'a'  # Default
        correct_lower = q.correct_answer.lower().strip()
        for j, opt in enumerate(q.options[:4]):
            if correct_lower in opt.lower():
                correct_letter = letters[j]
                break
        
        answer = input(f"  Q{i}: ").strip().lower()
        is_correct = answer == correct_letter
        results.append(is_correct)
        
        if is_correct:
            print(f"      ✓ Correct!")
        else:
            print(f"      ✗ Wrong! Answer was: {correct_letter}) {q.correct_answer}")
    
    # Submit results
    submit_quiz_results(session_id, results)


def handle_adaptive_demo():
    """Run automated adaptive mode demo."""
    print("\n🎯 ADAPTIVE MODE DEMO")
    print(f"{'─'*40}")
    
    pdf_id = select_pdf()
    if not pdf_id:
        return
    
    topic = get_input("Enter topic", "General Knowledge")
    num_rounds = int(get_input("Number of rounds", "3"))
    
    # Start session
    session = start_student_session(
        user_id="demo_user",
        pdf_id=pdf_id,
        topic=topic
    )
    
    # Run rounds
    import random
    for round_num in range(1, num_rounds + 1):
        print(f"\n{'─'*40}")
        print(f"📝 ROUND {round_num}/{num_rounds}")
        print(f"{'─'*40}")
        
        quiz = get_next_quiz_batch(session)
        
        if not quiz:
            print("Failed to generate quiz.")
            continue
        
        # Simulate performance (80% accuracy)
        results = [random.random() < 0.8 for _ in quiz.questions]
        submit_quiz_results(session, results)
    
    # Show final stats
    print_session_summary(session)


def handle_adaptive_menu():
    """Handle adaptive mode submenu."""
    while True:
        print_adaptive_menu()
        choice = get_menu_choice("Enter choice: ", ['0', '1', '2', '3', '4'])
        
        if choice == '0':
            return
        elif choice == '1':
            handle_start_adaptive_session()
        elif choice == '2':
            handle_take_adaptive_quiz()
        elif choice == '3':
            session_id = select_session()
            if session_id:
                print_session_summary(session_id)
        elif choice == '4':
            handle_adaptive_demo()


# ═══════════════════════════════════════════════════════════════════════════════
# GRIND MODE HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def handle_start_grind_session():
    """Handle starting a new grind session."""
    print("\n🏋️ START GRIND SESSION")
    print(f"{'─'*40}")
    
    pdf_id = select_pdf()
    if not pdf_id:
        return None
    
    user_id = get_input("Enter user ID", "user_001")
    topic = get_input("Enter topic for quiz generation")
    
    if not topic:
        print("\n❌ Topic is required!")
        return None
    
    difficulty = get_difficulty_choice()
    
    dynamic = get_yes_no("Enable dynamic difficulty (slower than adaptive)?", default=True)
    
    session = start_grind_session(
        user_id=user_id,
        pdf_id=pdf_id,
        topic=topic,
        difficulty=difficulty,
        dynamic_difficulty=dynamic
    )
    
    return session


def handle_take_grind_quiz():
    """Handle taking a grind quiz."""
    # Reuse adaptive quiz handler - same flow
    handle_take_adaptive_quiz()


def handle_grind_demo():
    """Run automated grind mode demo."""
    print("\n🏋️ GRIND MODE DEMO")
    print(f"{'─'*40}")
    
    pdf_id = select_pdf()
    if not pdf_id:
        return
    
    topic = get_input("Enter topic", "General Knowledge")
    difficulty = get_difficulty_choice()
    dynamic = get_yes_no("Enable dynamic difficulty?", default=True)
    num_rounds = int(get_input("Number of rounds", "4"))
    
    # Create grind mode instance
    grind = GrindMode(agent, ADAPTIVE_ENGINE)
    
    # Start session
    session = grind.start_grind_session(
        user_id="demo_user",
        pdf_id=pdf_id,
        topic=topic,
        difficulty=difficulty,
        dynamic_difficulty=dynamic
    )
    
    # Run practice loop
    grind_practice_loop(grind, session, num_rounds=num_rounds, simulate_performance=0.75)


def handle_grind_menu():
    """Handle grind mode submenu."""
    while True:
        print_grind_menu()
        choice = get_menu_choice("Enter choice: ", ['0', '1', '2', '3', '4'])
        
        if choice == '0':
            return
        elif choice == '1':
            handle_start_grind_session()
        elif choice == '2':
            handle_take_grind_quiz()
        elif choice == '3':
            session_id = select_session()
            if session_id:
                print_session_summary(session_id)
        elif choice == '4':
            handle_grind_demo()


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def handle_list_sessions():
    """List all active sessions."""
    sessions = list_active_sessions()
    
    print(f"\n📋 ACTIVE SESSIONS: {len(sessions)}")
    print(f"{'─'*60}")
    
    if not sessions:
        print("  No active sessions.")
        return
    
    for sid in sessions:
        try:
            stats = get_session_stats(sid)
            print(f"\n  📌 {sid[:40]}...")
            print(f"     Mode: {stats['mode']}")
            print(f"     Difficulty: {stats['current_difficulty']}")
            print(f"     Topic: {stats['topic']}")
            print(f"     Quizzes: {stats['total_quizzes']}")
            print(f"     Accuracy: {stats['overall_accuracy']:.2%}")
        except Exception as e:
            print(f"\n  📌 {sid[:40]}... (error reading stats)")


def handle_delete_session():
    """Delete a session."""
    session_id = select_session()
    if not session_id:
        return
    
    confirm = get_yes_no(f"Delete session {session_id[:30]}...?", default=False)
    
    if confirm:
        if delete_session(session_id):
            print("\n✅ Session deleted!")
        else:
            print("\n❌ Failed to delete session.")
    else:
        print("\n  Cancelled.")


def handle_session_menu():
    """Handle session management submenu."""
    while True:
        print_session_menu()
        choice = get_menu_choice("Enter choice: ", ['0', '1', '2', '3'])
        
        if choice == '0':
            return
        elif choice == '1':
            handle_list_sessions()
        elif choice == '2':
            session_id = select_session()
            if session_id:
                print_session_summary(session_id)
        elif choice == '3':
            handle_delete_session()


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def handle_view_config():
    """Display current configuration."""
    print(f"\n{'═'*60}")
    print("⚙️ CURRENT CONFIGURATION")
    print(f"{'═'*60}")
    
    print(f"\n📊 QUIZ MODE (Adaptive):")
    for key, value in DEFAULT_QUIZ_CONFIG.items():
        print(f"   {key}: {value}")
    
    print(f"\n🏋️ GRIND MODE:")
    for key, value in DEFAULT_GRIND_CONFIG.items():
        print(f"   {key}: {value}")
    
    print(f"\n📚 INDEXED PDFs:")
    sources = kb.get_all_pdf_sources()
    if sources:
        for src in sources:
            print(f"   • {src}")
    else:
        print("   None")
    
    print(f"{'═'*60}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point."""
    print_header()
    
    # Check for indexed PDFs
    sources = kb.get_all_pdf_sources()
    if not sources:
        print("\n⚠️ No PDFs indexed!")
        print("   Use option 1 (Document Ingestion) to upload a PDF first.")
    else:
        print(f"\n✅ {len(sources)} PDF(s) ready for quiz generation.")
    
    while True:
        print_main_menu()
        choice = get_menu_choice("Enter choice: ", ['0', '1', '2', '3', '4', '5'])
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == '1':
            handle_ingestion_menu()
        elif choice == '2':
            handle_adaptive_menu()
        elif choice == '3':
            handle_grind_menu()
        elif choice == '4':
            handle_session_menu()
        elif choice == '5':
            handle_view_config()


if __name__ == "__main__":
    main()
