import os
from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
# Import your custom modules
from pre_processor import DocumentProcessor
from storage import KnowledgeBase
from agent import QuizAgent

# Load environment variables
load_dotenv()

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# GROQ CONFIGURATION (FREE & FAST)
LLM_MODEL = ChatGroq(
    model="llama-3.1-8b-instant",  # Best for reasoning
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# For embeddings, use HuggingFace (free & local)
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
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

def main():
    ch = int(input("Enter what to do"))
    if ch == 1:
        upload_new_material('C:/College/Hackathons/HackCrypt/Rooster-HackCrypt/backend/data/',1)
    else:
        topic = None
        student_request_quiz(1,1,topic)


# --- 4. Execution ---
if __name__ == "__main__":
    # Example Workflow
    
    # 1. Simulate Teacher Upload
    # upload_new_material(r"C:\College\Hackathons\HackCrypt\Rooster-HackCrypt\backend\ip_data\Module 3.pdf", "eco_003")
    
    # 2. Simulate Student Quiz
    # quiz = student_request_quiz("sess_user_123", "eco_003", "Measures taken to grow Indian Economy ")
    # print(quiz)
    pass