# backend/test_loaders_simple.py

"""
Simple automated test for new loaders - no user input required.
Tests Syllabus loader only (YouTube requires actual video URL).
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
from src.features.quiz_generation_main import start_student_session, get_next_quiz_batch

def test_syllabus_automatic():
    """Automated test for syllabus content generation."""
    print("\n" + "="*60)
    print("🧪 AUTOMATED TEST: SYLLABUS CONTENT GENERATION")
    print("="*60)
    
    topic = "Neural Networks"
    print(f"\nTopic: {topic}")
    print("⏳ Generating content (30-60 seconds)...\n")
    
    # Generate and upload syllabus content
    try:
        result = upload_material(
            material_type="SYLLABUS",
            content=topic,
            source_id="test_neural_networks"
        )
        
        if not result.get("success"):
            print("\n❌ TEST FAILED: Could not generate syllabus content")
            return False
        
        print(f"\n✅ SUCCESS: Syllabus indexed")
        print(f"   Documents: {result['num_documents']}")
        print(f"   Propositions: {result['num_propositions']}")
        
        # Try generating a quiz
        print("\n" + "─"*60)
        print("Testing Quiz Generation...")
        print("─"*60)
        
        session = start_student_session(
            user_id="test_user",
            pdf_id="test_neural_networks",
            topic=topic,
            initial_difficulty="MEDIUM"
        )
        
        quiz = get_next_quiz_batch(session)
        
        if quiz and len(quiz) > 0:
            print(f"\n✅ SUCCESS: Generated {len(quiz)} questions!")
            print(f"\nSample Question:")
            print(f"━" * 50)
            print(f"{quiz[0].question}")
            for i, opt in enumerate(quiz[0].options, 1):
                marker = "✓" if i == quiz[0].correct_answer else " "
                print(f"  [{marker}] {i}. {opt}")
            print(f"━" * 50)
            
            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED!")
            print("="*60)
            print("\nThe system successfully:")
            print("  1. Generated educational content using Groq LLM")
            print("  2. Split content into chunks")
            print("  3. Created atomic propositions")
            print("  4. Indexed in ChromaDB")
            print("  5. Generated quiz questions from the content")
            return True
        else:
            print("\n❌ TEST FAILED: Could not generate quiz")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_syllabus_automatic()
    sys.exit(0 if success else 1)
