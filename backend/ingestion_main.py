# backend/ingestion_main.py

"""
Rooster-HackCrypt: Document Ingestion Module

This module handles ONLY document ingestion operations:
1. PDF upload and processing
2. Proposition decomposition
3. Knowledge base indexing

For quiz generation and session management, use quiz_generation_main.py
For grind mode functionality, use grind_mode.py
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# --- Model Configuration ---
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# GROQ CONFIGURATION (FREE & FAST)
LLM_MODEL = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# HuggingFace Embeddings (FREE & LOCAL)
EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# --- Import Custom Modules ---
from pre_processor import DocumentProcessor
from storage import KnowledgeBase

# --- Initialize Components ---
processor = DocumentProcessor(llm_model=LLM_MODEL)
kb = KnowledgeBase(embedding_model=EMBEDDING_MODEL)


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT INGESTION
# ═══════════════════════════════════════════════════════════════════════════════

def upload_new_material(
    pdf_path: str,
    source_id: str,
    chunk_size: int = 3000,
    chunk_overlap: int = 200
):
    """
    Teacher uploads a PDF for quiz generation.
    
    Process:
    1. Load PDF and split into chunks
    2. Generate propositions (atomic facts) using LLM
    3. Index in knowledge base (ChromaDB + Pickle)
    
    Args:
        pdf_path: Path to the PDF file
        source_id: Unique identifier for this PDF
        chunk_size: Size of text chunks for processing (default: 3000)
        chunk_overlap: Overlap between chunks (default: 200)
        
    Returns:
        Dictionary with upload statistics
        
    Example:
        upload_new_material("ip_data/Module 3.pdf", "eco_101")
    """
    print(f"\n{'='*60}")
    print(f"📄 UPLOADING PDF: {pdf_path}")
    print(f"{'='*60}")
    
    # Step 1: Load & Split
    print("\n📖 Step 1: Loading and splitting PDF...")
    parent_docs = processor.load_and_split(pdf_path)
    print(f"   ✓ Split into {len(parent_docs)} parent chunks")
    
    # Step 2: Decompose into propositions
    print("\n🔬 Step 2: Decomposing into propositions...")
    propositions = processor.generate_propositions(parent_docs)
    total_props = sum(len(p) for p in propositions)
    print(f"   ✓ Generated {total_props} propositions")
    
    # Step 3: Index in knowledge base
    print("\n💾 Step 3: Indexing in knowledge base...")
    kb.index_document(parent_docs, propositions, source_id)
    
    print(f"\n{'='*60}")
    print(f"✅ Upload Complete!")
    print(f"   Source ID: {source_id}")
    print(f"   Documents: {len(parent_docs)}")
    print(f"   Propositions: {total_props}")
    print(f"{'='*60}")
    
    return {
        "source_id": source_id,
        "num_documents": len(parent_docs),
        "num_propositions": total_props,
        "pdf_path": pdf_path
    }


def list_indexed_pdfs() -> List[str]:
    """
    List all indexed PDF source IDs.
    
    Returns:
        List of PDF source IDs
    """
    sources = kb.get_all_pdf_sources()
    
    print(f"\n📚 Indexed PDFs: {len(sources)}")
    for src in sources:
        print(f"   • {src}")
    
    return sources


def get_indexed_count() -> int:
    """
    Get the count of indexed PDFs.
    
    Returns:
        Number of indexed PDFs
    """
    return len(kb.get_all_pdf_sources())


def is_pdf_indexed(source_id: str) -> bool:
    """
    Check if a PDF is already indexed.
    
    Args:
        source_id: PDF source identifier to check
        
    Returns:
        True if indexed, False otherwise
    """
    sources = kb.get_all_pdf_sources()
    return source_id in sources


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE ACCESS
# ═══════════════════════════════════════════════════════════════════════════════

def get_knowledge_base() -> KnowledgeBase:
    """
    Get the knowledge base instance for direct access.
    
    Useful for advanced queries or when other modules need KB access.
    
    Returns:
        KnowledgeBase instance
    """
    return kb


def get_processor() -> DocumentProcessor:
    """
    Get the document processor instance for direct access.
    
    Useful for custom processing workflows.
    
    Returns:
        DocumentProcessor instance
    """
    return processor


def get_llm_model():
    """
    Get the LLM model instance.
    
    Returns:
        ChatGroq LLM instance
    """
    return LLM_MODEL


def get_embedding_model():
    """
    Get the embedding model instance.
    
    Returns:
        HuggingFaceEmbeddings instance
    """
    return EMBEDDING_MODEL


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def run_demo():
    """Run a quick ingestion demo."""
    print(f"\n{'═'*60}")
    print(f"🐓 ROOSTER-HACKCRYPT - INGESTION MODULE")
    print(f"{'═'*60}")
    
    # Check indexed PDFs
    sources = list_indexed_pdfs()
    
    if not sources:
        print("\n⚠️ No PDFs indexed!")
        print("   Run: upload_new_material('path/to/file.pdf', 'source_id')")
        print("\n   Example:")
        print("   >>> from ingestion_main import upload_new_material")
        print("   >>> upload_new_material('ip_data/Module 3.pdf', 'eco_101')")
    else:
        print(f"\n✅ {len(sources)} PDF(s) indexed and ready for quiz generation.")
        print("\n   To generate quizzes, use quiz_generation_main.py:")
        print("   >>> from quiz_generation_main import start_student_session, get_next_quiz_batch")
        print(f"   >>> session = start_student_session('user', '{sources[0]}', 'your_topic')")
        print("   >>> quiz = get_next_quiz_batch(session)")


if __name__ == "__main__":
    run_demo()
