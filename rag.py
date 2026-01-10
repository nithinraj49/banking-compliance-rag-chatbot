# rag_pipeline_groq.py
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv
import chromadb

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

print("=" * 70)
print("🤖 PHASE 3: RAG PIPELINE WITH GROQ (FREE!)")
print("=" * 70)

# ============================================================
# CONFIGURATION
# ============================================================
BASE_DIR = BASE_DIR = Path(__file__).parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

# Groq Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"  # Free, high quality
TEMPERATURE = 0.1
MAX_TOKENS = 2000

# ============================================================
# STEP 1: LOAD HYBRID RETRIEVER
# ============================================================
print("\n📂 STEP 1: Loading retriever components...")

chunks_file = PROCESSED_DIR / "chunks.pkl"
with open(chunks_file, "rb") as f:
    chunks = pickle.load(f)
print(f"✅ Loaded {len(chunks)} chunks")

bm25_file = PROCESSED_DIR / "bm25_index.pkl"
with open(bm25_file, "rb") as f:
    bm25 = pickle.load(f)
print(f"✅ Loaded BM25 index")

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_collection(name="banking_compliance")
print(f"✅ Connected to ChromaDB ({collection.count()} vectors)")

# ============================================================
# STEP 2: IMPORT HYBRID RETRIEVER
# ============================================================
print("\n🔧 STEP 2: Initializing Hybrid Retriever...")

import sys
sys.path.append(str(BASE_DIR))

from hybrid_search import HybridRetriever

retriever = HybridRetriever(
    collection=collection,
    bm25=bm25,
    chunks=chunks,
    alpha=0.5
)

print("✅ Hybrid Retriever ready")

# ============================================================
# STEP 3: INITIALIZE GROQ (FREE!)
# ============================================================
print("\n🤖 STEP 3: Initializing Groq (FREE API)...")

api_key = "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"

if not api_key or api_key == "your_groq_key_here":
    print("❌ ERROR: No Groq API key found!")
    print("\n📝 Steps to fix:")
    print("   1. Get FREE API key at: https://console.groq.com/")
    print("   2. Add to .env file: GROQ_API_KEY=gsk-your-key-here")
    print("   3. Re-run this script")
    llm = None
else:
    try:
        llm = ChatGroq(
            model=GROQ_MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            api_key=api_key
        )
        print(f"✅ Groq initialized successfully!")
        print(f"   Model: {GROQ_MODEL} (FREE)")
        print(f"   Status: Unlimited free tier!")
    except Exception as e:
        print(f"❌ Error: {e}")
        llm = None

# ============================================================
# STEP 4: CREATE RAG PROMPT
# ============================================================
print("\n📝 STEP 4: Creating RAG prompt template...")

RAG_PROMPT = ChatPromptTemplate.from_template("""
You are a senior banking compliance advisor. Provide precise, professional answers about banking regulations, loan policies, KYC/AML compliance, Basel liquidity standards and FATF AML/CFT guidelines. Provide precise, professional answers.

CONTEXT FROM REGULATORY DOCUMENTS:
{context}

USER QUESTION:
{question}


GUIDELINES:
- Keep answer between 80-120 words (be concise and direct)
- State facts clearly without unnecessary elaboration
- Cite sources professionally using regulator names:
  * "The Basel Committee requires..." or "Basel standards state..."
  * "FATF Recommendations require..." or "FATF guidelines mandate..."
  * "UAE Central Bank circulars state..." (if applicable)
- DO NOT say "Document 1" or "Document 3"
- Use bullet points for multiple items (if needed)
- Skip unnecessary phrases
- Get straight to the point
- If information is insufficient, state it briefly

CONCISE PROFESSIONAL ANSWER (80-120 words):
""")

print("✅ Prompt template created")

# ============================================================
# STEP 5: CREATE RAG CHAIN
# ============================================================
print("\n🔗 STEP 5: Building RAG chain...")

def format_documents(docs):
    formatted = []
    for i, doc in enumerate(docs, 1):
        formatted.append(f"""
Document {i}:
Source: {doc['source']}
Regulator: {doc['regulator']}
Jurisdiction: {doc['jurisdiction']}

Content:
{doc['content']}
---
""")
    return "\n".join(formatted)

def rag_query(question, top_k=3, filter_metadata=None):
    print(f"\n🔍 Retrieving relevant documents...")
    
    retrieved_docs = retriever.hybrid_search(
        query=question,
        top_k=top_k,
        filter_metadata=filter_metadata
    )
    
    if not retrieved_docs:
        return {
            'answer': "I couldn't find any relevant information.",
            'sources': []
        }
    
    print(f"✅ Retrieved {len(retrieved_docs)} documents")
    
    context = format_documents(retrieved_docs)
    
    if llm is None:
        answer = "[No API key - Add Groq key to .env file]"
    else:
        print(f"🤖 Generating answer with Groq (FREE!)...")
        
        messages = RAG_PROMPT.format_messages(
            context=context,
            question=question
        )
        
        response = llm.invoke(messages)
        answer = response.content
        print("✅ Answer generated")
    
    return {
        'answer': answer,
        'sources': [
            {
                'source': doc['source'],
                'regulator': doc['regulator'],
                'score': doc['score']
            }
            for doc in retrieved_docs
        ]
    }

print("✅ RAG chain ready")

# ============================================================
# STEP 6: TEST
# ============================================================
print("\n" + "=" * 70)
print("🧪 TESTING RAG PIPELINE")
print("=" * 70)

test_questions = [
    "What is the minimum CET1 capital adequacy ratio under Basel III?",
    "What are the KYC requirements for opening a bank account?",
]

for i, question in enumerate(test_questions, 1):
    print(f"\n{'='*70}")
    print(f"❓ Question {i}: {question}")
    print(f"{'='*70}")
    
    result = rag_query(question, top_k=3)
    
    print(f"\n💡 ANSWER:")
    print(f"{result['answer']}")
    
    print(f"\n📚 SOURCES:")
    for j, source in enumerate(result['sources'], 1):
        print(f"   {j}. {source['source']} - Score: {source['score']:.3f}")

print("\n" + "=" * 70)
print("✅ PHASE 3 COMPLETE!")
print("=" * 70)
print("\n🎉 Using FREE Groq API - Unlimited queries!")
print("🚀 Ready for Phase 4: Streamlit UI!")
print("=" * 70)