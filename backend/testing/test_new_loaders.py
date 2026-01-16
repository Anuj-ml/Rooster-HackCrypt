# backend/test_new_loaders.py

"""
Quick test script for YouTube and Syllabus loaders.
"""

import os
import sys
from dotenv import load_dotenv

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.ingestion_main import upload_material
from src.features.quiz_generation_main import QuizService, start_student_session, get_next_quiz_batch

def test_youtube_loader():
    """Test YouTube video loading and quiz generation."""
    print("\n" + "="*60)
    print("TEST 1: YOUTUBE VIDEO LOADER")
    print("="*60)
    
    # Example: A short educational video about SQL
    youtube_url = input("\nEnter YouTube URL (or press Enter for demo): ").strip()
    
    if not youtube_url:
        print("Skipping YouTube test (no URL provided)")
        return False
    
    # Upload YouTube video
    result = upload_material(
        material_type="YOUTUBE",
        content=youtube_url,
        source_id="youtube_test_sql"
    )
    
    if not result.get("success"):
        print("\n❌ Failed to load YouTube video")
        return False
    
    print(f"\n✅ YouTube video indexed: {result['num_propositions']} propositions")
    
    # Try generating a quiz
    print("\n" + "─"*60)
    print("Testing Quiz Generation from YouTube content...")
    print("─"*60)
    
    session = start_student_session(
        user_id="test_user",
        pdf_id="youtube_test_sql",
        topic="SQL",
        initial_difficulty="MEDIUM"
    )
    
    quiz = get_next_quiz_batch(session)
    
    if quiz and len(quiz) > 0:
        print(f"\n✅ Successfully generated {len(quiz)} questions from YouTube video!")
        print(f"\nSample Question:")
        print(f"Q: {quiz[0].question}")
        for i, opt in enumerate(quiz[0].options, 1):
            print(f"   {i}. {opt}")
        return True
    else:
        print("\n❌ Failed to generate quiz from YouTube content")
        return False


def test_syllabus_loader():
    """Test syllabus content generation and quiz generation."""
    print("\n" + "="*60)
    print("TEST 2: SYLLABUS CONTENT GENERATOR")
    print("="*60)
    
    topic = input("\nEnter topic (or press Enter for 'Neural Networks'): ").strip()
    topic = topic or "Neural Networks"
    
    print(f"\nGenerating content for topic: {topic}")
    print("⏳ This may take 30-60 seconds...")
    
    # Generate and upload syllabus content
    result = upload_material(
        material_type="SYLLABUS",
        content=topic,
        source_id=f"syllabus_{topic.lower().replace(' ', '_')}"
    )
    
    if not result.get("success"):
        print("\n❌ Failed to generate syllabus content")
        return False
    
    print(f"\n✅ Syllabus content indexed: {result['num_propositions']} propositions")
    
    # Try generating a quiz
    print("\n" + "─"*60)
    print("Testing Quiz Generation from Syllabus content...")
    print("─"*60)
    
    session = start_student_session(
        user_id="test_user",
        pdf_id=result['source_id'],
        topic=topic,
        initial_difficulty="MEDIUM"
    )
    
    quiz = get_next_quiz_batch(session)
    
    if quiz and len(quiz) > 0:
        print(f"\n✅ Successfully generated {len(quiz)} questions from syllabus!")
        print(f"\nSample Question:")
        print(f"Q: {quiz[0].question}")
        for i, opt in enumerate(quiz[0].options, 1):
            print(f"   {i}. {opt}")
        return True
    else:
        print("\n❌ Failed to generate quiz from syllabus content")
        return False


if __name__ == "__main__":
    print("\n🐓 ROOSTER-HACKCRYPT: NEW LOADERS TEST")
    print("="*60)
    
    print("\nThis script tests:")
    print("  1. YouTube video transcript loading")
    print("  2. Syllabus content generation (using Groq LLM)")
    print("  3. Quiz generation from both sources")
    
    print("\n" + "─"*60)
    choice = input("\nWhich test? (1=YouTube, 2=Syllabus, 3=Both, 0=Exit): ").strip()
    
    if choice == '1':
        test_youtube_loader()
    elif choice == '2':
        test_syllabus_loader()
    elif choice == '3':
        test_youtube_loader()
        test_syllabus_loader()
    elif choice == '0':
        print("\nExiting...")
    else:
        print("\nInvalid choice")
    
    print("\n" + "="*60)
    print("✅ Test Complete!")
    print("="*60)
