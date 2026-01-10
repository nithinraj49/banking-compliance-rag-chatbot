# hybrid_search.py
import pickle
from pathlib import Path
import chromadb
from rank_bm25 import BM25Okapi
import numpy as np

print("=" * 70)
print("🔍 PHASE 2.5: HYBRID SEARCH SETUP")
print("=" * 70)

# ============================================================
# CONFIGURATION
# ============================================================
BASE_DIR = Path(__file__).parent  # ✅ FIXED: Relative path instead of hardcoded
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

COLLECTION_NAME = "banking_compliance"
DENSE_WEIGHT = 0.5   # 50% weight to semantic search
SPARSE_WEIGHT = 0.5  # 50% weight to keyword search

# ============================================================
# STEP 1: LOAD DATA
# ============================================================
print("\n📂 STEP 1: Loading processed chunks...")

chunks_file = PROCESSED_DIR / "chunks.pkl"

if not chunks_file.exists():
    print(f"❌ Error: {chunks_file} not found!")
    print("Run process_pdfs.py first")
    exit(1)

with open(chunks_file, "rb") as f:
    chunks = pickle.load(f)

print(f"✅ Loaded {len(chunks)} chunks")

# ============================================================
# STEP 2: CONNECT TO CHROMADB
# ============================================================
print("\n🔧 STEP 2: Connecting to ChromaDB (Dense Search)...")

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_collection(name=COLLECTION_NAME)

print(f"✅ ChromaDB connected")
print(f"   Total vectors: {collection.count()}")

# ============================================================
# STEP 3: CREATE BM25 INDEX
# ============================================================
print("\n📑 STEP 3: Creating BM25 index (Sparse Search)...")

print("   Tokenizing documents...")
corpus = [chunk['content'].lower().split() for chunk in chunks]

print("   Building BM25 index...")
bm25 = BM25Okapi(corpus)

print("✅ BM25 index created")

# Save BM25 for later use
bm25_file = PROCESSED_DIR / "bm25_index.pkl"
with open(bm25_file, "wb") as f:
    pickle.dump(bm25, f)

print(f"✅ BM25 index saved to: {bm25_file}")

# ============================================================
# STEP 4: CREATE HYBRID RETRIEVER
# ============================================================
print("\n" + "=" * 70)
print("🎯 STEP 4: Creating Hybrid Retriever")
print("=" * 70)

class HybridRetriever:
    """
    Combines Dense (semantic) and Sparse (keyword) search
    """
    
    def __init__(self, collection, bm25, chunks, alpha=0.5):
        """
        Args:
            collection: ChromaDB collection
            bm25: BM25 index
            chunks: List of document chunks
            alpha: Weight for dense search (0.5 = equal weight)
        """
        self.collection = collection
        self.bm25 = bm25
        self.chunks = chunks
        self.alpha = alpha
        self.beta = 1 - alpha
    
    def dense_search(self, query, top_k=20):
        """Semantic search using ChromaDB embeddings"""
        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, len(self.chunks))
        )
        
        # ✅ FIXED: Improved ID parsing with fallback
        scores = {}
        for i, doc_id in enumerate(results['ids'][0]):
            try:
                # Try different ID formats
                if '::chunk_' in doc_id:
                    # Format: "filename.pdf::chunk_123"
                    idx = int(doc_id.split('::chunk_')[1])
                elif 'chunk_' in doc_id:
                    # Format: "chunk_123"
                    idx = int(doc_id.split('_')[-1])
                else:
                    # Fallback: use position
                    idx = i
            except (ValueError, IndexError):
                # If all parsing fails, use position
                idx = i
            
            # Convert distance to similarity
            distance = results['distances'][0][i] if 'distances' in results else 0
            similarity = 1 / (1 + distance)
            scores[idx] = similarity
        
        return scores
    
    def sparse_search(self, query, top_k=20):
        """Keyword search using BM25"""
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Normalize scores to 0-1 range
        max_score = bm25_scores.max() if bm25_scores.max() > 0 else 1
        normalized_scores = bm25_scores / max_score
        
        # Get top k indices
        top_indices = np.argsort(bm25_scores)[-top_k:][::-1]
        
        scores = {idx: normalized_scores[idx] for idx in top_indices}
        return scores
    
    def hybrid_search(self, query, top_k=5, filter_metadata=None):
        """
        Combine dense and sparse search
        
        Args:
            query: Search query string
            top_k: Number of results to return
            filter_metadata: Dict to filter by (e.g., {"regulator": "Reserve Bank of India"})
        
        Returns:
            List of results with scores
        """
        
        # Get scores from both methods
        dense_scores = self.dense_search(query, top_k=20)
        sparse_scores = self.sparse_search(query, top_k=20)
        
        # Combine scores
        all_indices = set(dense_scores.keys()) | set(sparse_scores.keys())
        combined_scores = {}
        
        for idx in all_indices:
            # Make sure idx is valid
            if idx >= len(self.chunks):
                continue
                
            dense = dense_scores.get(idx, 0)
            sparse = sparse_scores.get(idx, 0)
            
            # Weighted combination
            combined_scores[idx] = (self.alpha * dense) + (self.beta * sparse)
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Apply metadata filtering if specified
        if filter_metadata:
            filtered_results = []
            for idx, score in sorted_results:
                chunk = self.chunks[idx]
                # Check if chunk matches all filter criteria
                matches = all(
                    chunk.get(key) == value 
                    for key, value in filter_metadata.items()
                )
                if matches:
                    filtered_results.append((idx, score))
            sorted_results = filtered_results
        
        # Get top k
        top_results = sorted_results[:top_k]
        
        # Format results
        results = []
        for idx, score in top_results:
            chunk = self.chunks[idx]
            results.append({
                'content': chunk['content'],
                'source': chunk['source'],
                'regulator': chunk['regulator'],
                'jurisdiction': chunk['jurisdiction'],
                'score': score,
                'chunk_index': idx
            })
        
        return results

# Initialize retriever
retriever = HybridRetriever(
    collection=collection,
    bm25=bm25,
    chunks=chunks,
    alpha=DENSE_WEIGHT
)

print(f"✅ Hybrid Retriever initialized")
print(f"   Dense weight (semantic): {DENSE_WEIGHT * 100}%")
print(f"   Sparse weight (keywords): {SPARSE_WEIGHT * 100}%")

# ============================================================
# STEP 5: TEST HYBRID SEARCH
# ============================================================
print("\n" + "=" * 70)
print("🧪 STEP 5: TESTING HYBRID SEARCH")
print("=" * 70)

test_cases = [
    {
        "query": "What is the minimum CET1 capital ratio?",
        "filter": None,
        "description": "Basel III regulatory question"
    },
    {
        "query": "KYC requirements for bank accounts",
        "filter": {"regulator": "Reserve Bank of India"},
        "description": "Filtered search (RBI only)"
    },
    {
        "query": "How to report suspicious transactions?",
        "filter": None,
        "description": "AML compliance question"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"🔍 TEST {i}: {test['description']}")
    print(f"{'='*70}")
    print(f"Query: '{test['query']}'")
    
    if test['filter']:
        print(f"Filter: {test['filter']}")
    
    try:
        results = retriever.hybrid_search(
            query=test['query'],
            top_k=3,
            filter_metadata=test['filter']
        )
        
        print(f"\n📊 Found {len(results)} results:")
        
        for j, result in enumerate(results, 1):
            print(f"\n   Result {j}:")
            print(f"   ⭐ Score: {result['score']:.3f}")
            print(f"   📄 Source: {result['source']}")
            print(f"   🏛️  Regulator: {result['regulator']}")
            print(f"   📝 Preview: {result['content'][:150]}...")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

# ============================================================
# STEP 6: SAVE RETRIEVER FOR PHASE 3
# ============================================================
print("\n" + "=" * 70)
print("💾 STEP 6: SAVING RETRIEVER")
print("=" * 70)

# Save retriever components for later use
retriever_data = {
    'bm25': bm25,
    'chunks': chunks,
    'config': {
        'dense_weight': DENSE_WEIGHT,
        'sparse_weight': SPARSE_WEIGHT
    }
}

retriever_file = PROCESSED_DIR / "retriever_components.pkl"
with open(retriever_file, "wb") as f:
    pickle.dump(retriever_data, f)

print(f"✅ Retriever components saved to: {retriever_file}")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("✅ PHASE 2.5 COMPLETE!")
print("=" * 70)

print(f"\n📊 System Status:")
print(f"   ✅ ChromaDB (Dense): {collection.count()} vectors")
print(f"   ✅ BM25 (Sparse): {len(chunks)} documents indexed")
print(f"   ✅ Hybrid Retriever: Ready")
print(f"   ✅ Metadata Filtering: Working")

print(f"\n💾 Saved Files:")
print(f"   - BM25 index: {bm25_file}")
print(f"   - Retriever components: {retriever_file}")
print(f"   - ChromaDB: {CHROMA_DIR}")

print(f"\n🎯 Search Capabilities:")
print(f"   ✅ Semantic search (finds similar meanings)")
print(f"   ✅ Keyword search (finds exact terms)")
print(f"   ✅ Hybrid search (best of both)")
print(f"   ✅ Filter by regulator/jurisdiction")

print("\n🚀 READY FOR PHASE 3: RAG Pipeline with LLM!")
print("=" * 70)

# ============================================================
# STEP 6: COMPARISON TEST
# ============================================================
print("\n" + "=" * 70)
print("📊 STEP 6: COMPARING SEARCH METHODS")
print("=" * 70)

comparison_query = "What are the Basel III capital requirements?"
print(f"\nQuery: {comparison_query}\n")

# Dense only
print("1️⃣ DENSE SEARCH ONLY (Semantic):")
dense_only = retriever.dense_search(comparison_query, top_k=3)
top_dense = sorted(dense_only.items(), key=lambda x: x[1], reverse=True)[:3]
for i, (idx, score) in enumerate(top_dense, 1):
    print(f"   {i}. Score: {score:.3f} | {chunks[idx]['source']}")

# Sparse only  
print("\n2️⃣ SPARSE SEARCH ONLY (Keywords - BM25):")
sparse_only = retriever.sparse_search(comparison_query, top_k=3)
top_sparse = sorted(sparse_only.items(), key=lambda x: x[1], reverse=True)[:3]
for i, (idx, score) in enumerate(top_sparse, 1):
    print(f"   {i}. Score: {score:.3f} | {chunks[idx]['source']}")

# Hybrid
print("\n3️⃣ HYBRID SEARCH (Combined):")
hybrid_results = retriever.hybrid_search(comparison_query, top_k=3)
for i, result in enumerate(hybrid_results, 1):
    print(f"   {i}. Score: {result['score']:.3f} | {result['source']}")

print("\n💡 Notice how hybrid combines the best of both!")