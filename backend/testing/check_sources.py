import os
import sys

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from src.features.quiz_generation_main import get_kb

kb = get_kb()

# Get sources from vectorstore
vector_sources = kb.get_all_pdf_sources()
print("=" * 60)
print("SOURCES IN VECTORSTORE:")
print("=" * 60)
for src in sorted(vector_sources):
    print(f"  • {src}")
print(f"\nTotal: {len(vector_sources)}")

# Get sources from docstore
print("\n" + "=" * 60)
print("SOURCES IN DOCSTORE:")
print("=" * 60)
doc_by_source = {}
for doc_id, doc in kb.docstore.items():
    source_id = doc.metadata.get("pdf_source_id", "NO_SOURCE")
    if source_id not in doc_by_source:
        doc_by_source[source_id] = 0
    doc_by_source[source_id] += 1

for src in sorted(doc_by_source.keys()):
    print(f"  • {src}: {doc_by_source[src]} docs")
print(f"\nTotal docs: {len(kb.docstore)}")

# Check mismatch
print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)
vector_set = set(vector_sources)
docstore_set = set(doc_by_source.keys())

if vector_set == docstore_set:
    print("✓ Vectorstore and docstore are in sync!")
else:
    only_vector = vector_set - docstore_set
    only_docstore = docstore_set - vector_set
    
    if only_vector:
        print(f"⚠ Sources ONLY in vectorstore (missing from docstore):")
        for src in only_vector:
            print(f"    - {src}")
    
    if only_docstore:
        print(f"⚠ Sources ONLY in docstore (missing from vectorstore):")
        for src in only_docstore:
            print(f"    - {src}")
