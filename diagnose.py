# diagnose.py
from pathlib import Path
import pickle

print("🔍 DIAGNOSING THE ISSUE...\n")

BASE_DIR = BASE_DIR = Path(__file__).parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

# Check 1: Chunks file
chunks_file = PROCESSED_DIR / "chunks.pkl"
print(f"1. Checking chunks file: {chunks_file}")
if chunks_file.exists():
    with open(chunks_file, "rb") as f:
        chunks = pickle.load(f)
    print(f"   ✅ File exists")
    print(f"   ✅ Contains {len(chunks)} chunks")
    print(f"\n   Sample chunk:")
    print(f"   Source: {chunks[0]['source']}")
    print(f"   Content length: {len(chunks[0]['content'])} chars")
else:
    print(f"   ❌ File NOT found!")

# Check 2: ChromaDB directory
print(f"\n2. Checking ChromaDB directory: {CHROMA_DIR}")
if CHROMA_DIR.exists():
    print(f"   ✅ Directory exists")
    files = list(CHROMA_DIR.glob("*"))
    print(f"   Files inside: {len(files)}")
    for f in files:
        print(f"      - {f.name}")
else:
    print(f"   ❌ Directory NOT found!")

# Check 3: Try to load ChromaDB
print(f"\n3. Checking ChromaDB contents:")
try:
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # List all collections
    collections = client.list_collections()
    print(f"   Collections found: {len(collections)}")
    
    if collections:
        for coll in collections:
            print(f"   - {coll.name}: {coll.count()} items")
    else:
        print(f"   ⚠️  No collections found!")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)