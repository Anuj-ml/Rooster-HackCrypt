import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Import your custom modules
from processor import DocumentProcessor
from storage import KnowledgeBase
from agent import QuizAgent

# Load environment variables
load_dotenv()

# --- 1. Configuration ---
# Gemini 1.5 Flash is excellent for high-volume tasks like RAG and Quizzing
LLM_MODEL = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    convert_system_message_to_human=True # Sometimes needed for older LangChain versions
)

# Use Google's optimized embedding model
EMBEDDING_MODEL = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004" # Or "models/embedding-001"
)

# --- 2. Dependency Injection ---
# Initialize Processor with Gemini
processor = DocumentProcessor(llm_model=LLM_MODEL)

# Initialize KnowledgeBase with Google Embeddings
# (Note: We pass the embedding model here to keep storage.py clean)
kb = KnowledgeBase(embedding_model=EMBEDDING_MODEL)

# Initialize Agent with Gemini and the KB
agent = QuizAgent(llm=LLM_MODEL, knowledge_base=kb)

# --- 3. Workflow Functions ---

def upload_new_material(pdf_path: str, source_id: str):
    """
    Teacher uploads a PDF.
    """
    print(f"--- Processing: {pdf_path} ---")
    
    # Step 1: Load & Split
    parent_docs = processor.load_and_split(pdf_path)
    print(f"Split into {len(parent_docs)} parent chunks.")
    
    # Step 2: Decompose (Using Gemini 1.5 Flash)
    # Flash is very fast at this specific task
    propositions = processor.generate_propositions(parent_docs)
    
    # Step 3: Index
    kb.index_document(parent_docs, propositions, source_id)
    print("Upload and Indexing Complete!")

def student_request_quiz(session_id: str, pdf_id: str, topic: str):
    """
    Student requests a quiz in the Adaptive Session.
    """
    print(f"--- Starting Quiz Session: {topic} ---")
    
    input_data = {
        "session_id": session_id,
        "pdf_source_id": pdf_id,
        "current_difficulty": "HARD", # In a real app, fetch this from your 'AdaptiveSessions' DB
        "topic": topic
    }
    
    result = agent.run_session(input_data)
    
    # The result contains the Pydantic object
    final_quiz = result['generated_quiz']
    
    if final_quiz:
        print(f"Successfully generated {len(final_quiz.questions)} questions.")
        # Debug: Print first question
        print(f"Q1: {final_quiz.questions[0].question}")
    else:
        print("Failed to generate quiz (No context found or LLM error).")
        
    return final_quiz

# --- 4. Execution ---
if __name__ == "__main__":
    # Example Workflow
    
    # 1. Simulate Teacher Upload
    # upload_new_material("data/physics_chapter_4.pdf", "phy_004")
    
    # 2. Simulate Student Quiz
    # quiz = student_request_quiz("sess_user_123", "phy_004", "Newton's Third Law")
    pass