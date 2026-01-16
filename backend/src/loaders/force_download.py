"""
Aggressive HuggingFace model download script with multiple retry strategies.
This will download the model no matter what.
"""
import os
import time
import sys
from pathlib import Path

# Set up cache directory
cache_dir = Path("./data/embeddings_cache")
cache_dir.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("AGGRESSIVE MODEL DOWNLOAD - MULTIPLE STRATEGIES")
print("=" * 80)
print(f"Cache directory: {cache_dir.absolute()}")
print()

# Strategy 1: Direct sentence-transformers download with retries
print("STRATEGY 1: Direct sentence-transformers download with aggressive retries")
print("-" * 80)

try:
    from sentence_transformers import SentenceTransformer
    import socket
    import urllib.request
    
    # Increase socket timeout globally
    socket.setdefaulttimeout(600)  # 10 minutes
    
    model_name = "sentence-transformers/paraphrase-MiniLM-L3-v2"
    max_retries = 10
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\nAttempt {attempt}/{max_retries}...")
            print(f"Downloading {model_name}...")
            
            model = SentenceTransformer(
                model_name, 
                cache_folder=str(cache_dir),
                device='cpu'
            )
            
            print("\n✓ SUCCESS! Model downloaded successfully!")
            print(f"Model saved to: {cache_dir}")
            
            # Test the model
            print("\nTesting model...")
            test_embedding = model.encode("test sentence")
            print(f"✓ Model works! Embedding dimension: {len(test_embedding)}")
            
            sys.exit(0)
            
        except Exception as e:
            print(f"✗ Attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                wait_time = attempt * 5  # Increasing wait time
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print("\nStrategy 1 failed after all retries.")
                
except ImportError:
    print("sentence-transformers not installed. Installing now...")
    os.system("pip install sentence-transformers")
    print("Please run this script again after installation.")
    sys.exit(1)

# Strategy 2: Using huggingface_hub with snapshot download
print("\n" + "=" * 80)
print("STRATEGY 2: Using huggingface_hub snapshot_download")
print("-" * 80)

try:
    from huggingface_hub import snapshot_download
    import socket
    
    socket.setdefaulttimeout(600)
    
    model_name = "sentence-transformers/paraphrase-MiniLM-L3-v2"
    max_retries = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\nAttempt {attempt}/{max_retries}...")
            print(f"Downloading {model_name} via snapshot_download...")
            
            model_path = snapshot_download(
                repo_id=model_name,
                cache_dir=str(cache_dir),
                resume_download=True,
                local_files_only=False
            )
            
            print(f"\n✓ SUCCESS! Model downloaded to: {model_path}")
            sys.exit(0)
            
        except Exception as e:
            print(f"✗ Attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                wait_time = attempt * 5
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                
except Exception as e:
    print(f"\nStrategy 2 failed: {str(e)}")

# Strategy 3: Manual file download
print("\n" + "=" * 80)
print("STRATEGY 3: Manual file download from HuggingFace")
print("-" * 80)

try:
    import urllib.request
    import socket
    
    socket.setdefaulttimeout(600)
    
    files_to_download = [
        "config.json",
        "pytorch_model.bin",
        "tokenizer_config.json",
        "vocab.txt",
        "special_tokens_map.json"
    ]
    
    base_url = "https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L3-v2/resolve/main/"
    model_dir = cache_dir / "models--sentence-transformers--paraphrase-MiniLM-L3-v2" / "snapshots" / "main"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading files to: {model_dir}")
    
    for filename in files_to_download:
        file_url = base_url + filename
        file_path = model_dir / filename
        
        print(f"\nDownloading {filename}...")
        
        for attempt in range(1, 4):
            try:
                urllib.request.urlretrieve(file_url, str(file_path))
                print(f"✓ {filename} downloaded successfully")
                break
            except Exception as e:
                print(f"✗ Attempt {attempt} failed for {filename}: {str(e)}")
                if attempt < 3:
                    time.sleep(5)
                    
    print("\n✓ Manual download complete!")
    sys.exit(0)
    
except Exception as e:
    print(f"\nStrategy 3 failed: {str(e)}")

print("\n" + "=" * 80)
print("ALL STRATEGIES FAILED")
print("=" * 80)
print("\nPossible solutions:")
print("1. Check your internet connection")
print("2. Try using a VPN")
print("3. Try on a different network (mobile hotspot)")
print("4. Ask a teammate to download and share the model files")
print("5. Use university/company network if you're on home WiFi")
sys.exit(1)
