# create_embeddings.py
import pickle
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

print("=" * 70)
print("🧠 PHASE 2: CREATING VECTOR EMBEDDINGS")
print("=" * 70)

BASE_DIR = BASE_DIR = Path(__file__).parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

COLLECTION_NAME = "banking_compliance"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # ✅ FIX
BATCH_SIZE = 100

print(f"\n📁 Using ChromaDB path: {CHROMA_DIR}")

# Load chunks
chunks_file = PROCESSED_DIR / "chunks.pkl"
with open(chunks_file, "rb") as f:
    chunks = pickle.load(f)

print(f"✅ Loaded {len(chunks)} chunks")

# Init Chroma
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

print("Loading embedding model (lightweight)...")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
print("✅ Embedding model loaded")

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)

# Prepare data
documents, metadatas, ids = [], [], []

for i, chunk in enumerate(chunks):
    documents.append(chunk["content"])
    metadatas.append({
        "source": chunk["source"],
        "regulator": chunk["regulator"],
        "jurisdiction": chunk["jurisdiction"],
    })
    ids.append(f"{chunk['source']}::chunk_{i}")

# Insert
for start in range(0, len(documents), BATCH_SIZE):
    end = min(start + BATCH_SIZE, len(documents))
    collection.add(
        documents=documents[start:end],
        metadatas=metadatas[start:end],
        ids=ids[start:end]
    )
    print(f"✔ Indexed {end}/{len(documents)}")

# Verify
print("\nFINAL COUNT:", collection.count())
print("COLLECTIONS:", client.list_collections())

print("\n🎉 Embeddings created successfully")
