# backend/ingestion_main.py

"""
Rooster-HackCrypt: Document Ingestion Module

This module handles document ingestion operations:
1. PDF upload and processing
2. Proposition decomposition
3. Knowledge base indexing

For quiz generation and session management, use quiz_generation_main.py
For grind mode functionality, use grind_mode.py
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# --- Model Configuration ---
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# --- Import Custom Modules ---
from src.rag.pre_processor import DocumentProcessor
from src.rag.storage import KnowledgeBase
from src.loaders.youtube_loader import YouTubeLoader
from src.loaders.syllabus_loader import SyllabusLoader


class ModelFactory:
    """Factory for creating and caching ML model instances."""
    
    _llm_model = None
    _embedding_model = None
    
    @classmethod
    def get_llm_model(cls):
        """Get or create the LLM model instance."""
        if cls._llm_model is None:
            cls._llm_model = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0,
                groq_api_key=os.getenv("GROQ_API_KEY")
            )
        return cls._llm_model
    
    @classmethod
    def get_embedding_model(cls):
        """Get or create the embedding model instance."""
        if cls._embedding_model is None:
            # Use backend directory's data folder
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cache_dir = os.path.join(backend_dir, "data", "embeddings_cache")
            os.makedirs(cache_dir, exist_ok=True)
            cls._embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-MiniLM-L3-v2",
                cache_folder=cache_dir,
                model_kwargs={'local_files_only': True}
            )
        return cls._embedding_model


class IngestionService:
    """
    Service for document ingestion operations.
    
    Handles PDF upload, processing, and indexing into the knowledge base.
    Uses lazy initialization for dependencies.
    """
    
    _instance = None
    
    def __init__(
        self,
        llm_model=None,
        embedding_model=None,
        processor: Optional[DocumentProcessor] = None,
        knowledge_base: Optional[KnowledgeBase] = None
    ):
        """
        Initialize the ingestion service.
        
        Args:
            llm_model: Optional LLM model (lazy loaded if not provided)
            embedding_model: Optional embedding model (lazy loaded if not provided)
            processor: Optional DocumentProcessor (created if not provided)
            knowledge_base: Optional KnowledgeBase (created if not provided)
        """
        self._llm_model = llm_model
        self._embedding_model = embedding_model
        self._processor = processor
        self._kb = knowledge_base
        self._youtube_loader = None
        self._syllabus_loader = None
    
    @property
    def llm_model(self):
        """Lazy initialization of LLM model."""
        if self._llm_model is None:
            self._llm_model = ModelFactory.get_llm_model()
        return self._llm_model
    
    @property
    def embedding_model(self):
        """Lazy initialization of embedding model."""
        if self._embedding_model is None:
            self._embedding_model = ModelFactory.get_embedding_model()
        return self._embedding_model
    
    @property
    def processor(self) -> DocumentProcessor:
        """Lazy initialization of document processor."""
        if self._processor is None:
            self._processor = DocumentProcessor(llm_model=self.llm_model)
        return self._processor
    
    @property
    def knowledge_base(self) -> KnowledgeBase:
        """Lazy initialization of knowledge base."""
        if self._kb is None:
            self._kb = KnowledgeBase(embedding_model=self.embedding_model)
        return self._kb
    
    @property
    def youtube_loader(self) -> YouTubeLoader:
        """Lazy initialization of YouTube loader."""
        if self._youtube_loader is None:
            self._youtube_loader = YouTubeLoader()
        return self._youtube_loader
    
    @property
    def syllabus_loader(self) -> SyllabusLoader:
        """Lazy initialization of syllabus loader."""
        if self._syllabus_loader is None:
            self._syllabus_loader = SyllabusLoader(llm=self.llm_model)
        return self._syllabus_loader
    
    def upload_new_material(
        self,
        pdf_path: str,
        source_id: str,
        chunk_size: int = 3000,
        chunk_overlap: int = 200
    ) -> Dict[str, Any]:
        """
        Upload a PDF for quiz generation.
        
        Process:
        1. Load PDF and split into chunks
        2. Generate propositions (atomic facts) using LLM
        3. Index in knowledge base (ChromaDB + Pickle)
        
        Args:
            pdf_path: Path to the PDF file
            source_id: Unique identifier for this PDF
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
            
        Returns:
            Dictionary with upload statistics
        """
        print(f"\n{'='*60}")
        print(f"📄 UPLOADING PDF: {pdf_path}")
        print(f"{'='*60}")
        
        # Step 1: Load & Split
        print("\n📖 Step 1: Loading and splitting PDF...")
        parent_docs = self.processor.load_and_split(pdf_path)
        print(f"   ✓ Split into {len(parent_docs)} parent chunks")
        
        # Step 2: Decompose into propositions
        print("\n🔬 Step 2: Decomposing into propositions...")
        propositions = self.processor.generate_propositions(parent_docs)
        total_props = sum(len(p) for p in propositions)
        print(f"   ✓ Generated {total_props} propositions")
        
        # Step 3: Index in knowledge base
        print("\n💾 Step 3: Indexing in knowledge base...")
        self.knowledge_base.index_document(parent_docs, propositions, source_id)
        
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
    
    def upload_material(
        self,
        material_type: str,
        content: str,
        source_id: str
    ) -> Dict[str, Any]:
        """
        Upload material of any type (PDF, YouTube, or Syllabus).
        
        Process:
        1. Load content based on material type
        2. Generate propositions using the EXISTING processor logic
        3. Index in knowledge base
        
        Args:
            material_type: Type of material ("PDF", "YOUTUBE", "SYLLABUS")
            content: Path to PDF, YouTube URL, or Syllabus topic
            source_id: Unique identifier for this material
            
        Returns:
            Dictionary with upload statistics
        """
        material_type = material_type.upper()
        
        print(f"\n{'='*60}")
        print(f"📥 UPLOADING MATERIAL: {material_type}")
        print(f"{'='*60}")
        print(f"   Source ID: {source_id}")
        
        # Step 1: Load content based on type
        if material_type == "PDF":
            print("\n📖 Step 1: Loading PDF...")
            parent_docs = self.processor.load_and_split(content)
            print(f"   ✓ Loaded {len(parent_docs)} chunks")
            
        elif material_type == "YOUTUBE":
            print("\n🎥 Step 1: Loading YouTube video...")
            docs = self.youtube_loader.load_transcript(content)
            
            if not docs:
                print(f"\n{'='*60}")
                print(f"❌ Failed to load YouTube video!")
                print(f"{'='*60}")
                return {
                    "source_id": source_id,
                    "num_documents": 0,
                    "num_propositions": 0,
                    "material_type": material_type,
                    "success": False
                }
            
            # Split the transcript into chunks
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
            parent_docs = splitter.split_documents(docs)
            # Ensure metadata has pdf_source_id
            for doc in parent_docs:
                doc.metadata["pdf_source_id"] = source_id
            print(f"   ✓ Split into {len(parent_docs)} chunks")
            
        elif material_type == "SYLLABUS":
            print("\n📚 Step 1: Generating syllabus content...")
            docs = self.syllabus_loader.generate_content(content)
            
            if not docs:
                print(f"\n{'='*60}")
                print(f"❌ Failed to generate syllabus content!")
                print(f"{'='*60}")
                return {
                    "source_id": source_id,
                    "num_documents": 0,
                    "num_propositions": 0,
                    "material_type": material_type,
                    "success": False
                }
            
            # Split the generated content into chunks
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
            parent_docs = splitter.split_documents(docs)
            # Ensure metadata has pdf_source_id
            for doc in parent_docs:
                doc.metadata["pdf_source_id"] = source_id
            print(f"   ✓ Split into {len(parent_docs)} chunks")
            
        else:
            print(f"   ✗ Unsupported material type: {material_type}")
            print(f"   Supported: PDF, YOUTUBE, SYLLABUS")
            return {
                "source_id": source_id,
                "num_documents": 0,
                "num_propositions": 0,
                "material_type": material_type,
                "success": False
            }
        
        # Step 2: Decompose into propositions using EXISTING logic
        print("\n🔬 Step 2: Decomposing into propositions...")
        propositions = self.processor.generate_propositions(parent_docs)
        total_props = sum(len(p) for p in propositions)
        print(f"   ✓ Generated {total_props} propositions")
        
        # Step 3: Index in knowledge base
        print("\n💾 Step 3: Indexing in knowledge base...")
        self.knowledge_base.index_document(parent_docs, propositions, source_id)
        
        print(f"\n{'='*60}")
        print(f"✅ Upload Complete!")
        print(f"   Type: {material_type}")
        print(f"   Source ID: {source_id}")
        print(f"   Documents: {len(parent_docs)}")
        print(f"   Propositions: {total_props}")
        print(f"{'='*60}")
        
        return {
            "source_id": source_id,
            "num_documents": len(parent_docs),
            "num_propositions": total_props,
            "material_type": material_type,
            "success": True
        }
    
    def list_indexed_pdfs(self) -> List[str]:
        """
        List all indexed PDF source IDs.
        
        Returns:
            List of PDF source IDs
        """
        sources = self.knowledge_base.get_all_pdf_sources()
        
        print(f"\n📚 Indexed PDFs: {len(sources)}")
        for src in sources:
            print(f"   • {src}")
        
        return sources
    
    def get_indexed_count(self) -> int:
        """Get the count of indexed PDFs."""
        return len(self.knowledge_base.get_all_pdf_sources())
    
    def is_pdf_indexed(self, source_id: str) -> bool:
        """Check if a PDF is already indexed."""
        sources = self.knowledge_base.get_all_pdf_sources()
        return source_id in sources
    
    @classmethod
    def get_instance(cls) -> 'IngestionService':
        """Get the singleton instance of IngestionService."""
        if cls._instance is None:
            cls._instance = IngestionService()
        return cls._instance


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL FUNCTIONS (Backward Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

def get_llm_model():
    """Get the LLM model instance."""
    return ModelFactory.get_llm_model()


def get_embedding_model():
    """Get the embedding model instance."""
    return ModelFactory.get_embedding_model()


def get_processor() -> DocumentProcessor:
    """Get the document processor instance."""
    return IngestionService.get_instance().processor


def get_knowledge_base() -> KnowledgeBase:
    """Get the knowledge base instance."""
    return IngestionService.get_instance().knowledge_base


def upload_new_material(
    pdf_path: str,
    source_id: str,
    chunk_size: int = 3000,
    chunk_overlap: int = 200
) -> Dict[str, Any]:
    """Upload a PDF for quiz generation."""
    return IngestionService.get_instance().upload_new_material(
        pdf_path, source_id, chunk_size, chunk_overlap
    )


def upload_material(
    material_type: str,
    content: str,
    source_id: str
) -> Dict[str, Any]:
    """
    Upload material of any type (PDF, YouTube, or Syllabus).
    
    Args:
        material_type: Type of material ("PDF", "YOUTUBE", "SYLLABUS")
        content: Path to PDF, YouTube URL, or Syllabus topic
        source_id: Unique identifier for this material
        
    Returns:
        Dictionary with upload statistics
    """
    return IngestionService.get_instance().upload_material(
        material_type, content, source_id
    )


def list_indexed_pdfs() -> List[str]:
    """List all indexed PDF source IDs."""
    return IngestionService.get_instance().list_indexed_pdfs()


def get_indexed_count() -> int:
    """Get the count of indexed PDFs."""
    return IngestionService.get_instance().get_indexed_count()


def is_pdf_indexed(source_id: str) -> bool:
    """Check if a PDF is already indexed."""
    return IngestionService.get_instance().is_pdf_indexed(source_id)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def run_demo():
    """Run a quick ingestion demo."""
    print(f"\n{'═'*60}")
    print(f"🐓 ROOSTER-HACKCRYPT - INGESTION MODULE")
    print(f"{'═'*60}")
    
    service = IngestionService.get_instance()
    sources = service.list_indexed_pdfs()
    
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
