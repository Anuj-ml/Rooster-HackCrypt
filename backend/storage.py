from langchain_chroma import Chroma
from langchain_core.documents import Document
import uuid
import os
import pickle
import json

class KnowledgeBase:
    """
    Multi-Vector Retrieval with FULL PERSISTENCE:
    - Propositions/embeddings → ChromaDB (disk)
    - Parent documents → Pickle file (disk)
    """
    
    def __init__(self, embedding_model, 
                 persist_directory="./data/chroma_db",
                 docstore_directory="./data/docstore"):
        """
        Initialize with fully persistent storage.
        
        Args:
            embedding_model: Embedding model for vectorization
            persist_directory: Where to save ChromaDB data
            docstore_directory: Where to save parent documents
        """
        # Create directories if they don't exist
        os.makedirs(persist_directory, exist_ok=True)
        os.makedirs(docstore_directory, exist_ok=True)
        
        # PERSISTENT ChromaDB - embeddings and propositions
        self.vectorstore = Chroma(
            collection_name="propositions_db",
            embedding_function=embedding_model,
            persist_directory=persist_directory
        )
        
        # PERSISTENT Document Store - parent documents
        self.docstore_path = os.path.join(docstore_directory, "documents.pkl")
        self.docstore = self._load_docstore()
        
        self.id_key = "doc_id"
        
        print(f"✓ KnowledgeBase initialized")
        print(f"  - ChromaDB: {persist_directory}")
        print(f"  - DocStore: {self.docstore_path}")
        print(f"  - Loaded {len(self.docstore)} documents from disk")

    def _load_docstore(self):
        """Load document store from disk."""
        if os.path.exists(self.docstore_path):
            try:
                with open(self.docstore_path, 'rb') as f:
                    docstore = pickle.load(f)
                print(f"✓ Loaded existing docstore with {len(docstore)} documents")
                return docstore
            except Exception as e:
                print(f"⚠ Error loading docstore: {e}")
                print("  Starting with empty docstore")
                return {}
        else:
            print("✓ No existing docstore found, starting fresh")
            return {}
    
    def _save_docstore(self):
        """Save document store to disk."""
        try:
            with open(self.docstore_path, 'wb') as f:
                pickle.dump(self.docstore, f)
            print(f"✓ Saved docstore with {len(self.docstore)} documents to disk")
        except Exception as e:
            print(f"✗ Error saving docstore: {e}")

    def index_document(self, parent_docs, all_propositions, pdf_source_id):
        """
        Index parent documents and their child propositions.
        Both are now stored persistently.
        """
        doc_ids = [str(uuid.uuid4()) for _ in parent_docs]
        
        # Tag parent docs with metadata
        for i, parent_doc in enumerate(parent_docs):
            parent_doc.metadata["pdf_source_id"] = pdf_source_id
        
        # Link propositions to their parents
        proposition_docs = []
        for i, (parent_doc, propositions) in enumerate(zip(parent_docs, all_propositions)):
            parent_id = doc_ids[i]
            for prop in propositions:
                new_doc = Document(
                    page_content=prop,
                    metadata={
                        self.id_key: parent_id,
                        "pdf_source_id": pdf_source_id
                    }
                )
                proposition_docs.append(new_doc)
        
        # Store parent documents in persistent pickle file
        for doc_id, doc in zip(doc_ids, parent_docs):
            self.docstore[doc_id] = doc
        self._save_docstore()
        
        # Store propositions in persistent ChromaDB
        self.vectorstore.add_documents(proposition_docs)
        
        print(f"✓ Indexed {len(parent_docs)} parent docs → {len(proposition_docs)} propositions")
        print(f"✓ Total documents in storage: {len(self.docstore)}")

    def retrieve_context(self, query, pdf_source_id, k=5):
        """
        Retrieve full parent documents based on proposition similarity.
        Reads from persistent storage.
        """
        # Step 1: Search propositions in ChromaDB
        results = self.vectorstore.similarity_search(
            query, 
            k=k,
            filter={"pdf_source_id": pdf_source_id}
        )
        
        if not results:
            print(f"⚠ No results found for query: '{query}' in pdf_source_id: {pdf_source_id}")
            return []
        
        # Step 2: Get unique parent IDs
        parent_ids = list(set([doc.metadata[self.id_key] for doc in results]))
        print(f"✓ Found {len(parent_ids)} relevant parent documents")
        
        # Step 3: Fetch full parent documents from persistent store
        retrieved_docs = [self.docstore.get(pid) for pid in parent_ids if pid in self.docstore]
        
        return retrieved_docs
    
    def get_all_pdf_sources(self):
        """Get list of all indexed PDF source IDs."""
        # Get unique pdf_source_ids from vectorstore
        all_docs = self.vectorstore.get()
        if all_docs and 'metadatas' in all_docs:
            source_ids = set()
            for metadata in all_docs['metadatas']:
                if 'pdf_source_id' in metadata:
                    source_ids.add(metadata['pdf_source_id'])
            return list(source_ids)
        return []
    
    def clear_all(self):
        """Clear all data (useful for testing)."""
        # Clear ChromaDB
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            collection_name="propositions_db",
            embedding_function=self.vectorstore._embedding_function,
            persist_directory=self.vectorstore._persist_directory
        )
        
        # Clear docstore
        self.docstore = {}
        self._save_docstore()
        
        print("✓ All data cleared")