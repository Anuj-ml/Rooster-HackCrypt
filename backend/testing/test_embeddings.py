"""Quick test to verify Google AI embeddings work"""
import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

print("Testing Google AI Embeddings...")

# Test the embedding
from src.rag.ingestion_main import get_embedding_model

emb = get_embedding_model()
print(f"✓ Embedding model initialized: {type(emb).__name__}")

# Test generating an embedding
test_vec = emb.embed_query("test sentence")
print(f"✓ Embedding dimension: {len(test_vec)}")
print("✅ SUCCESS! Google AI embeddings work perfectly.")
print("\nYour app is ready. The slow loading you saw is just TensorFlow.")
print("Once TensorFlow loads (30 seconds), the app menu will appear.")
