# inspect_chunks.py
import pickle
from pathlib import Path

BASE_DIR = BASE_DIR = Path(__file__).parent
CHUNKS_FILE = BASE_DIR / "data" / "processed" / "chunks.pkl"

with open(CHUNKS_FILE, "rb") as f:
    chunks = pickle.load(f)

print(f"Total chunks loaded: {len(chunks)}")

# Print first 3 chunks
for i, chunk in enumerate(chunks[:3], 1):
    print("\n" + "=" * 80)
    print(f"CHUNK {i}")
    print("=" * 80)
    print(f"Source      : {chunk['source']}")
    print(f"Regulator   : {chunk['regulator']}")
    print(f"Section     : {chunk['section_title']}")
    print(f"Chunk index : {chunk['chunk_in_section']} / {chunk['total_section_chunks']}")
    print("\n--- CONTENT PREVIEW ---\n")
    print(chunk["content"][:800])
