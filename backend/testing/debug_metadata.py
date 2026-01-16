# Quick test script to debug metadata issue
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.storage import KnowledgeBase
from src.rag.ingestion_main import ModelFactory

# Initialize
embedding_model = ModelFactory.get_embedding_model()
kb = KnowledgeBase(embedding_model=embedding_model)

print("\n" + "="*60)
print("DEBUGGING DOCSTORE METADATA")
print("="*60)

# Check documents
print(f"\nTotal documents in docstore: {len(kb.docstore)}")

# Check metadata for each document
source_counts = {}
for doc_id, doc in kb.docstore.items():
    source_id = doc.metadata.get("pdf_source_id", "MISSING")
    if source_id not in source_counts:
        source_counts[source_id] = 0
    source_counts[source_id] += 1

print("\nDocuments by source_id:")
for source_id, count in source_counts.items():
    print(f"  {source_id}: {count} documents")

# Test retrieve_all_documents for "SQL"
print("\n" + "-"*60)
print("Testing retrieve_all_documents for 'SQL':")
sql_docs = kb.retrieve_all_documents("SQL", k=5)
print(f"Retrieved: {len(sql_docs)} documents")

if sql_docs:
    for i, doc in enumerate(sql_docs, 1):
        print(f"\nDoc {i}:")
        print(f"  Content: {doc.page_content[:100]}...")
        print(f"  Metadata: {doc.metadata}")
else:
    print("  No documents found!")
    print("\n  Checking what's in docstore with 'SQL':")
    for doc_id, doc in kb.docstore.items():
        if doc.metadata.get("pdf_source_id") == "SQL":
            print(f"    Found doc {doc_id}: {doc.page_content[:50]}...")

print("\n" + "="*60)
