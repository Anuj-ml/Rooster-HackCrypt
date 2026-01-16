import sys
import os

# Add current directory to path so imports work
sys.path.insert(0, '.')

from backend.src.features.quiz_generation_main import (
    start_student_session, 
    list_active_sessions, 
    get_session_stats,
    get_next_quiz_batch
)
from backend.src.rag.ingestion_main import list_indexed_pdfs

def run_test():
    print("\n════════════════════════════════════════════════════════════")
    print("🔍 REPRODUCING USER SESSION (AUTOMATED TEST)")
    print("════════════════════════════════════════════════════════════")

    # 1. Verify PDF is available (from your previous session)
    print("\n[Step 1] Verifying PDF Index...")
    sources = list_indexed_pdfs()
    target_source = "Eco_3"
    
    if target_source not in sources:
        print(f"⚠️ Warning: '{target_source}' not found in index. Using first available or creating dummy.")
        if sources:
            target_source = sources[0]
            print(f"-> Using existing source: {target_source}")
        else:
            print("❌ No sources. Test might fail if generation requires content.")
    else:
        print(f"✅ Found source '{target_source}'")

    # 2. Start Session (Your Inputs: user_002, Topic, EASY)
    print("\n[Step 2] Starting Session...")
    try:
        session_id = start_student_session(
            user_id="user_002",
            pdf_id=target_source,
            topic="Measures taken to grow Indian Economy",
            initial_difficulty="EASY"
        )
        print(f"✅ Session Started. ID: {session_id}")
    except Exception as e:
        print(f"❌ Failed to start session: {e}")
        return

    # 3. List Sessions (This was the CRASH POINT)
    # The previous error occurred because this returned objects instead of ID strings
    print("\n[Step 3] Listing Sessions (The Crash Point)...")
    try:
        active_sessions = list_active_sessions()
        print(f"-> Raw output from list_active_sessions: {active_sessions}")
        
        # Verify type
        if active_sessions and isinstance(active_sessions[0], str):
             print("✅ Success: Returned list of strings (IDs).")
        elif active_sessions and isinstance(active_sessions[0], dict):
             print("❌ FAIL: Returned list of dicts (Objects). This will crash demo.py.")
        else:
             print("-> List is empty or unknown type.")

    except Exception as e:
        print(f"❌ Crash during listing: {e}")
        return

    # 4. Retrieve Stats (Simulating demo.py menu behavior)
    print("\n[Step 4] Retrieving Stats for Session...")
    try:
        # demo.py does: for sid in list_active_sessions(): get_session_stats(sid)
        if not active_sessions:
            print("❌ No active sessions to test.")
            return

        target_sid = active_sessions[-1] # Get the one we just made
        print(f"-> Fetching stats for: {target_sid}")
        
        stats = get_session_stats(target_sid)
        print("✅ Success! Stats retrieved:")
        print(f"   Mode: {stats['mode']}")
        print(f"   Difficulty: {stats['current_difficulty']}")
        print(f"   Topic: {stats['topic']}")
        
    except TypeError as e:
        print(f"❌ TYPE ERROR DETECTED: {e}")
        print("   (This confirms the 'unhashable type: dict' error if present)")
    except Exception as e:
        print(f"❌ Failed to get stats: {e}")

    # 5. Generate Quiz (Final validation)
    print("\n[Step 5] Generating Quiz Batch...")
    try:
        quiz = get_next_quiz_batch(session_id)
        if quiz:
            print(f"✅ Quiz generated with {len(quiz.questions)} questions.")
        else:
            print("⚠️ Quiz generation returned None (might be API or Content issue).")
    except Exception as e:
        print(f"❌ Quiz generation failed: {e}")

    print("\n════════════════════════════════════════════════════════════")
    print("✅ TEST COMPLETE")
    print("════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    run_test()
