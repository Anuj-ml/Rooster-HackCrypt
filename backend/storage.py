import uuid
from typing import List, Dict
from langchain.storage import InMemoryByteStore
from langchain_chroma import Chroma
from langchain_core.documents import Document


class KnowledgeBase:
    def __init__(self, embedding_model):
        # 1. The Vector Store (Indices Propositions)
        self.vectorstore = Chroma(
            collection_name="propositions_db",
            embedding_function=embedding_model ## NEED TO CHANGE THIS EMBEDDIGNS AS OPENAI WILL NOT BE USED
        )
        # 2. The Doc Store (Holds Full Parent Content)
        # Note: In production, swap InMemoryByteStore for RedisStore
        self.docstore = InMemoryByteStore()
        
        self.id_key = "doc_id"

    def index_document(self, parent_docs: List[Document], all_propositions: List[List[str]], pdf_source_id: str):
        """
        Orchestrates the linking and storage of Parents and Propositions.
        """
        doc_ids = [str(uuid.uuid4()) for _ in parent_docs]
        proposition_docs = []

        for i, (parent_doc, propositions) in enumerate(zip(parent_docs, all_propositions)):
            parent_id = doc_ids[i]
            
            # Tag Parent with source ID
            parent_doc.metadata["pdf_source_id"] = pdf_source_id
            
            # Create Proposition Documents linking to Parent
            for prop in propositions:
                new_doc = Document(
                    page_content=prop,
                    metadata={
                        self.id_key: parent_id,
                        "pdf_source_id": pdf_source_id # Critical for filtering
                    }
                )
                proposition_docs.append(new_doc)

        # A. Store Parents in DocStore (Key = UUID, Value = Doc)
        self.docstore.mset(list(zip(doc_ids, parent_docs)))

        # B. Store Propositions in VectorDB
        self.vectorstore.add_documents(proposition_docs)
        print(f"Indexed {len(proposition_docs)} propositions for Source: {pdf_source_id}")

    def retrieve_context(self, query: str, pdf_source_id: str, k: int = 5) -> List[Document]:
        """
        Manual Multi-Vector Retrieval Logic:
        1. Search VectorDB for Propositions (filtered by source).
        2. Extract Parent IDs.
        3. Fetch Parent Docs from DocStore.
        """
        # 1. Vector Search
        results = self.vectorstore.similarity_search(
            query, 
            k=k,
            filter={"pdf_source_id": pdf_source_id}
        )
        
        # 2. Extract Unique Parent IDs
        parent_ids = list(set([doc.metadata[self.id_key] for doc in results]))
        
        # 3. Fetch Full Context
        if not parent_ids:
            return []
            
        return self.docstore.mget(parent_ids)