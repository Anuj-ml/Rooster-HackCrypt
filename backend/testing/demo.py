# backend/demo.py

"""
Rooster-HackCrypt: Menu-Driven CLI Demo

This script provides an interactive command-line interface for:
1. Document Ingestion - Upload and index PDFs
2. Adaptive Mode - Auto-adjusting difficulty quizzes
3. Grind Mode - Fixed/slow-dynamic difficulty practice

All features are accessible through a user-friendly menu system.
"""

# Suppress TensorFlow warnings BEFORE any imports
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import sys
import random

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from src.rag.ingestion_main import (
    upload_new_material,
    list_indexed_pdfs,
    get_knowledge_base,
    get_llm_model,
    get_embedding_model
)

from src.features.quiz_generation_main import (
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
    get_kb,
    get_agent,
    get_adaptive_engine
)

from src.features.grind_mode import GrindMode, grind_practice_loop
from src.core.difficulty_engine import DEFAULT_QUIZ_CONFIG, DEFAULT_GRIND_CONFIG


class MenuDisplay:
    """Class for displaying menus and UI elements."""
    
    @staticmethod
    def print_header():
        """Print the application header."""
        print(f"\n{'═'*60}")
        print(f"🐓 ROOSTER-HACKCRYPT")
        print(f"   AI-Powered Adaptive Quiz Generator")
        print(f"{'═'*60}")
    
    @staticmethod
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
    
    @staticmethod
    def print_ingestion_menu():
        """Print document ingestion menu options."""
        print(f"\n{'─'*40}")
        print("📄 DOCUMENT INGESTION")
        print(f"{'─'*40}")
        print("  1. Upload PDF")
        print("  2. Load from YouTube URL")
        print("  3. Generate Syllabus Content")
        print("  4. List indexed PDFs")
        print("  0. Back to main menu")
        print(f"{'─'*40}")
    
    @staticmethod
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
    
    @staticmethod
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
    
    @staticmethod
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


class InputHelper:
    """Class for handling user input."""
    
    @staticmethod
    def get_menu_choice(prompt: str = "Enter choice: ", valid_options: list = None) -> str:
        """Get a menu choice from the user."""
        while True:
            choice = input(prompt).strip()
            if valid_options is None or choice in valid_options:
                return choice
            print(f"Invalid choice. Please enter one of: {', '.join(valid_options)}")
    
    @staticmethod
    def get_input(prompt: str, default: str = None) -> str:
        """Get user input with optional default value."""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        return input(f"{prompt}: ").strip()
    
    @staticmethod
    def get_difficulty_choice() -> str:
        """Get difficulty choice from user."""
        print("\n  Select difficulty:")
        print("    1. EASY")
        print("    2. MEDIUM")
        print("    3. HARD")
        choice = InputHelper.get_menu_choice("  Choice (1/2/3): ", ['1', '2', '3'])
        return {'1': 'EASY', '2': 'MEDIUM', '3': 'HARD'}[choice]
    
    @staticmethod
    def get_yes_no(prompt: str, default: bool = True) -> bool:
        """Get yes/no input from user."""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes', '1', 'true']
    
    @staticmethod
    def select_pdf() -> str:
        """Let user select a PDF from indexed list."""
        sources = get_kb().get_all_pdf_sources()
        
        if not sources:
            print("\n⚠️ No PDFs indexed! Please upload a PDF first.")
            return None
        
        # Sort sources for consistent display
        sources = sorted(sources)
        
        print(f"\n📚 Available Materials:")
        for i, src in enumerate(sources, 1):
            print(f"    {i}. {src}")
        
        if len(sources) == 1:
            print(f"\n  Using: {sources[0]}")
            return sources[0]
        
        while True:
            choice = input(f"  Select material (1-{len(sources)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(sources):
                    selected = sources[idx]
                    print(f"  ✓ Selected: {selected}")
                    return selected
            except ValueError:
                pass
            print(f"  Invalid choice. Enter a number between 1 and {len(sources)}")
    
    @staticmethod
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


class IngestionHandler:
    """Handler for document ingestion operations."""
    
    @staticmethod
    def handle_upload_pdf():
        """Handle PDF upload process."""
        print("\n📄 UPLOAD NEW PDF")
        print(f"{'─'*40}")
        
        pdf_path = InputHelper.get_input("Enter PDF path (e.g., ip_data/file.pdf)")
        
        if not os.path.exists(pdf_path):
            print(f"\n❌ File not found: {pdf_path}")
            return
        
        source_id = InputHelper.get_input(
            "Enter source ID (unique identifier)", 
            os.path.splitext(os.path.basename(pdf_path))[0]
        )
        
        try:
            upload_new_material(pdf_path, source_id)
            print("\n✅ PDF uploaded successfully!")
        except Exception as e:
            print(f"\n❌ Upload failed: {e}")
    
    @staticmethod
    def handle_upload_url():
        """Handle URL content loading (YouTube videos)."""
        print("\n🌐 LOAD FROM URL (YOUTUBE)")
        print(f"{'─'*40}")
        
        url = InputHelper.get_input("Enter YouTube URL")
        
        # Auto-extract video ID from URL
        from src.loaders.youtube_loader import YouTubeLoader
        loader = YouTubeLoader()
        video_id = loader.extract_video_id(url)
        
        if video_id:
            source_id = f"youtube_{video_id}"
            print(f"   ✓ Video ID detected: {video_id}")
            print(f"   ✓ Source ID: {source_id}")
        else:
            source_id = "youtube_video"
            print(f"   ⚠ Could not extract video ID, using default source ID")
        
        try:
            from src.rag.ingestion_main import upload_material
            
            # Upload YouTube video using unified pipeline
            result = upload_material(
                material_type="YOUTUBE",
                content=url,
                source_id=source_id
            )
            
            if result.get("success", False):
                print(f"\n✅ YouTube video indexed successfully!")
                print(f"   Documents: {result['num_documents']}")
                print(f"   Propositions: {result['num_propositions']}")
            else:
                print("\n❌ Failed to load YouTube video")
                
        except ImportError:
            print("\n❌ YouTube loader not available. Install: pip install youtube-transcript-api")
        except Exception as e:
            print(f"\n❌ Failed to load YouTube video: {e}")
    
    @staticmethod
    def handle_upload_syllabus():
        """Handle syllabus topic content generation."""
        print("\n📚 GENERATE SYLLABUS CONTENT")
        print(f"{'─'*40}")
        
        topic = InputHelper.get_input("Enter syllabus topic (e.g., 'Neural Networks', 'SQL Basics')")
        
        if not topic:
            print("\n❌ Topic is required!")
            return
        
        source_id = InputHelper.get_input(
            "Enter source ID",
            "syllabus_" + topic.lower().replace(' ', '_')[:30]
        )
        
        try:
            from src.rag.ingestion_main import upload_material
            
            print("\n   ⏳ This may take 30-60 seconds...")
            
            # Upload syllabus topic using unified pipeline
            result = upload_material(
                material_type="SYLLABUS",
                content=topic,
                source_id=source_id
            )
            
            if result.get("success", False):
                print(f"\n✅ Syllabus content indexed successfully!")
                print(f"   Documents: {result['num_documents']}")
                print(f"   Propositions: {result['num_propositions']}")
            else:
                print("\n❌ Failed to generate syllabus content")
                
        except Exception as e:
            print(f"\n❌ Failed to generate syllabus content: {e}")
    
    @staticmethod
    def handle_menu():
        """Handle document ingestion submenu."""
        while True:
            MenuDisplay.print_ingestion_menu()
            choice = InputHelper.get_menu_choice("Enter choice: ", ['0', '1', '2', '3', '4'])
            
            if choice == '0':
                return
            elif choice == '1':
                IngestionHandler.handle_upload_pdf()
            elif choice == '2':
                IngestionHandler.handle_upload_url()
            elif choice == '3':
                IngestionHandler.handle_upload_syllabus()
            elif choice == '4':
                list_indexed_pdfs()


class AdaptiveHandler:
    """Handler for adaptive mode operations."""
    
    @staticmethod
    def handle_start_session():
        """Handle starting a new adaptive session."""
        print("\n🎯 START ADAPTIVE SESSION")
        print(f"{'─'*40}")
        
        pdf_id = InputHelper.select_pdf()
        if not pdf_id:
            return None
        
        user_id = InputHelper.get_input("Enter user ID", "user_001")
        
        print("\n  💡 Tip: Enter 'default' to generate questions from entire document")
        topic = InputHelper.get_input("Enter topic for quiz generation (or 'default' for whole document)")
        
        if not topic:
            print("\n❌ Topic is required!")
            return None
        
        print("\n  Starting difficulty:")
        difficulty = InputHelper.get_difficulty_choice()
        
        session = start_student_session(
            user_id=user_id,
            pdf_id=pdf_id,
            topic=topic,
            initial_difficulty=difficulty
        )
        
        return session
    
    @staticmethod
    def handle_take_quiz():
        """Handle taking an adaptive quiz."""
        session_id = InputHelper.select_session()
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
    
    @staticmethod
    def handle_demo():
        """Run automated adaptive mode demo."""
        print("\n🎯 ADAPTIVE MODE DEMO")
        print(f"{'─'*40}")
        
        pdf_id = InputHelper.select_pdf()
        if not pdf_id:
            return
        
        topic = InputHelper.get_input("Enter topic", "General Knowledge")
        num_rounds = int(InputHelper.get_input("Number of rounds", "3"))
        
        # Start session
        session = start_student_session(
            user_id="demo_user",
            pdf_id=pdf_id,
            topic=topic
        )
        
        # Run rounds
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
    
    @staticmethod
    def handle_menu():
        """Handle adaptive mode submenu."""
        while True:
            MenuDisplay.print_adaptive_menu()
            choice = InputHelper.get_menu_choice("Enter choice: ", ['0', '1', '2', '3', '4'])
            
            if choice == '0':
                return
            elif choice == '1':
                AdaptiveHandler.handle_start_session()
            elif choice == '2':
                AdaptiveHandler.handle_take_quiz()
            elif choice == '3':
                session_id = InputHelper.select_session()
                if session_id:
                    print_session_summary(session_id)
            elif choice == '4':
                AdaptiveHandler.handle_demo()


class GrindHandler:
    """Handler for grind mode operations."""
    
    @staticmethod
    def handle_start_session():
        """Handle starting a new grind session."""
        print("\n🏋️ START GRIND SESSION")
        print(f"{'─'*40}")
        
        pdf_id = InputHelper.select_pdf()
        if not pdf_id:
            return None
        
        user_id = InputHelper.get_input("Enter user ID", "user_001")
        
        print("\n  💡 Tip: Enter 'default' to generate questions from entire document")
        topic = InputHelper.get_input("Enter topic for quiz generation (or 'default' for whole document)")
        
        if not topic:
            print("\n❌ Topic is required!")
            return None
        
        difficulty = InputHelper.get_difficulty_choice()
        dynamic = InputHelper.get_yes_no("Enable dynamic difficulty (slower than adaptive)?", default=True)
        
        session = start_grind_session(
            user_id=user_id,
            pdf_id=pdf_id,
            topic=topic,
            difficulty=difficulty,
            dynamic_difficulty=dynamic
        )
        
        return session
    
    @staticmethod
    def handle_take_quiz():
        """Handle taking a grind quiz."""
        # Reuse adaptive quiz handler - same flow
        AdaptiveHandler.handle_take_quiz()
    
    @staticmethod
    def handle_demo():
        """Run automated grind mode demo."""
        print("\n🏋️ GRIND MODE DEMO")
        print(f"{'─'*40}")
        
        pdf_id = InputHelper.select_pdf()
        if not pdf_id:
            return
        
        topic = InputHelper.get_input("Enter topic", "General Knowledge")
        difficulty = InputHelper.get_difficulty_choice()
        dynamic = InputHelper.get_yes_no("Enable dynamic difficulty?", default=True)
        num_rounds = int(InputHelper.get_input("Number of rounds", "4"))
        
        # Create grind mode instance
        grind = GrindMode(get_agent(), get_adaptive_engine())
        
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
    
    @staticmethod
    def handle_menu():
        """Handle grind mode submenu."""
        while True:
            MenuDisplay.print_grind_menu()
            choice = InputHelper.get_menu_choice("Enter choice: ", ['0', '1', '2', '3', '4'])
            
            if choice == '0':
                return
            elif choice == '1':
                GrindHandler.handle_start_session()
            elif choice == '2':
                GrindHandler.handle_take_quiz()
            elif choice == '3':
                session_id = InputHelper.select_session()
                if session_id:
                    print_session_summary(session_id)
            elif choice == '4':
                GrindHandler.handle_demo()


class SessionHandler:
    """Handler for session management operations."""
    
    @staticmethod
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
    
    @staticmethod
    def handle_delete_session():
        """Delete a session."""
        session_id = InputHelper.select_session()
        if not session_id:
            return
        
        confirm = InputHelper.get_yes_no(f"Delete session {session_id[:30]}...?", default=False)
        
        if confirm:
            if delete_session(session_id):
                print("\n✅ Session deleted!")
            else:
                print("\n❌ Failed to delete session.")
        else:
            print("\n  Cancelled.")
    
    @staticmethod
    def handle_menu():
        """Handle session management submenu."""
        while True:
            MenuDisplay.print_session_menu()
            choice = InputHelper.get_menu_choice("Enter choice: ", ['0', '1', '2', '3'])
            
            if choice == '0':
                return
            elif choice == '1':
                SessionHandler.handle_list_sessions()
            elif choice == '2':
                session_id = InputHelper.select_session()
                if session_id:
                    print_session_summary(session_id)
            elif choice == '3':
                SessionHandler.handle_delete_session()


class ConfigHandler:
    """Handler for configuration display."""
    
    @staticmethod
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
        sources = get_kb().get_all_pdf_sources()
        if sources:
            for src in sources:
                print(f"   • {src}")
        else:
            print("   None")
        
        print(f"{'═'*60}")


class DemoApplication:
    """Main application class for the CLI demo."""
    
    def __init__(self):
        """Initialize the demo application."""
        self.menu_display = MenuDisplay()
        self.input_helper = InputHelper()
    
    def run(self):
        """Run the main application loop."""
        MenuDisplay.print_header()
        
        # Check for indexed PDFs
        sources = get_kb().get_all_pdf_sources()
        if not sources:
            print("\n⚠️ No PDFs indexed!")
            print("   Use option 1 (Document Ingestion) to upload a PDF first.")
        else:
            print(f"\n✅ {len(sources)} PDF(s) ready for quiz generation.")
        
        while True:
            MenuDisplay.print_main_menu()
            choice = InputHelper.get_menu_choice("Enter choice: ", ['0', '1', '2', '3', '4', '5'])
            
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            elif choice == '1':
                IngestionHandler.handle_menu()
            elif choice == '2':
                AdaptiveHandler.handle_menu()
            elif choice == '3':
                GrindHandler.handle_menu()
            elif choice == '4':
                SessionHandler.handle_menu()
            elif choice == '5':
                ConfigHandler.handle_view_config()


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def print_header():
    """Print the application header."""
    MenuDisplay.print_header()

def print_main_menu():
    """Print the main menu options."""
    MenuDisplay.print_main_menu()

def print_ingestion_menu():
    """Print document ingestion menu options."""
    MenuDisplay.print_ingestion_menu()

def print_adaptive_menu():
    """Print adaptive mode menu options."""
    MenuDisplay.print_adaptive_menu()

def print_grind_menu():
    """Print grind mode menu options."""
    MenuDisplay.print_grind_menu()

def print_session_menu():
    """Print session management menu options."""
    MenuDisplay.print_session_menu()

def get_menu_choice(prompt: str = "Enter choice: ", valid_options: list = None) -> str:
    """Get a menu choice from the user."""
    return InputHelper.get_menu_choice(prompt, valid_options)

def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default value."""
    return InputHelper.get_input(prompt, default)

def get_difficulty_choice() -> str:
    """Get difficulty choice from user."""
    return InputHelper.get_difficulty_choice()

def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input from user."""
    return InputHelper.get_yes_no(prompt, default)

def select_pdf() -> str:
    """Let user select a PDF from indexed list."""
    return InputHelper.select_pdf()

def select_session() -> str:
    """Let user select an active session."""
    return InputHelper.select_session()

def handle_upload_pdf():
    """Handle PDF upload process."""
    IngestionHandler.handle_upload_pdf()

def handle_ingestion_menu():
    """Handle document ingestion submenu."""
    IngestionHandler.handle_menu()

def handle_start_adaptive_session():
    """Handle starting a new adaptive session."""
    return AdaptiveHandler.handle_start_session()

def handle_take_adaptive_quiz():
    """Handle taking an adaptive quiz."""
    AdaptiveHandler.handle_take_quiz()

def handle_adaptive_demo():
    """Run automated adaptive mode demo."""
    AdaptiveHandler.handle_demo()

def handle_adaptive_menu():
    """Handle adaptive mode submenu."""
    AdaptiveHandler.handle_menu()

def handle_start_grind_session():
    """Handle starting a new grind session."""
    return GrindHandler.handle_start_session()

def handle_take_grind_quiz():
    """Handle taking a grind quiz."""
    GrindHandler.handle_take_quiz()

def handle_grind_demo():
    """Run automated grind mode demo."""
    GrindHandler.handle_demo()

def handle_grind_menu():
    """Handle grind mode submenu."""
    GrindHandler.handle_menu()

def handle_list_sessions():
    """List all active sessions."""
    SessionHandler.handle_list_sessions()

def handle_delete_session():
    """Delete a session."""
    SessionHandler.handle_delete_session()

def handle_session_menu():
    """Handle session management submenu."""
    SessionHandler.handle_menu()

def handle_view_config():
    """Display current configuration."""
    ConfigHandler.handle_view_config()


def main():
    """Main application entry point."""
    app = DemoApplication()
    app.run()


if __name__ == "__main__":
    main()
