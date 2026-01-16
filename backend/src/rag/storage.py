from langchain_chroma import Chroma
from langchain_core.documents import Document
import uuid
import os
import pickle
import json
from typing import List, Optional, Dict

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
        If query is "default", retrieves random documents from entire source.
        Reads from persistent storage.
        """
        # Handle "default" topic - retrieve from entire document
        if query.lower() == "default":
            print(f"   📚 Retrieving from entire document (default mode)")
            return self.retrieve_all_documents(pdf_source_id, k=k)
        
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
    
    def retrieve_all_documents(self, pdf_source_id, k=5):
        """
        Retrieve random documents from entire source (for 'default' topic).
        
        Args:
            pdf_source_id: Source identifier to filter by
            k: Number of documents to retrieve
            
        Returns:
            List of random parent documents from the source
        """
        import random
        
        print(f"   🔎 Searching docstore for source_id: '{pdf_source_id}'")
        print(f"   📊 Total documents in docstore: {len(self.docstore)}")
        
        # Get all documents for this source
        source_docs = [
            doc for doc_id, doc in self.docstore.items()
            if doc.metadata.get("pdf_source_id") == pdf_source_id
        ]
        
        if not source_docs:
            print(f"   ⚠ No documents found for source: '{pdf_source_id}'")
            print(f"   💡 Available sources in docstore:")
            available = set()
            for doc in self.docstore.values():
                sid = doc.metadata.get("pdf_source_id")
                if sid:
                    available.add(sid)
            for src in sorted(available):
                print(f"      - {src}")
            return []
        
        # Return random selection (or all if fewer than k)
        num_to_retrieve = min(k, len(source_docs))
        selected_docs = random.sample(source_docs, num_to_retrieve)
        
        print(f"   ✓ Retrieved {num_to_retrieve} random documents from entire source")
        return selected_docs
    
    def get_raw_propositions(self, query: str, pdf_source_id: str = None, k: int = 20) -> List[str]:
        """
        Retrieve raw propositions (atomic facts) directly from ChromaDB.
        Unlike retrieve_context(), this returns the propositions themselves, not parent documents.
        Perfect for flash-note generation without LLM tokens.
        
        Args:
            query: Search query or "default" for random facts
            pdf_source_id: Optional source filter
            k: Number of propositions to retrieve (default: 20)
            
        Returns:
            List of proposition strings
        """
        # Build filter if source specified
        filter_dict = {"pdf_source_id": pdf_source_id} if pdf_source_id else None
        
        # Handle "default" query - get random propositions
        if query.lower() == "default" and pdf_source_id:
            # Get all propositions for this source, then sample randomly
            try:
                all_results = self.vectorstore.get(
                    where=filter_dict,
                    limit=k * 3  # Get more to ensure enough after filtering
                )
                
                if all_results and 'documents' in all_results and all_results['documents']:
                    import random
                    documents = all_results['documents']
                    # Return random sample
                    num_to_return = min(k, len(documents))
                    return random.sample(documents, num_to_return)
                else:
                    print(f"⚠ No propositions found for source: '{pdf_source_id}'")
                    return []
            except Exception as e:
                print(f"⚠ Error retrieving propositions: {e}")
                # Fallback to similarity search with generic query
                query = "information facts key points"
        
        # Standard similarity search
        try:
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                filter=filter_dict
            )
            
            if not results:
                print(f"⚠ No propositions found for query: '{query}'")
                return []
            
            # Extract page_content (the propositions themselves)
            propositions = [doc.page_content for doc in results]
            print(f"✓ Retrieved {len(propositions)} propositions for '{query}'")
            
            return propositions
            
        except Exception as e:
            print(f"✗ Error in similarity search: {e}")
            return []
    
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