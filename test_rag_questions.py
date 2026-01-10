# test_rag_questions.py
import sys
from pathlib import Path

# Add project to path
BASE_DIR = BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

# Import from your pipeline
from rag import rag_query

print("=" * 70)
print("🧪 TESTING RAG WITH CUSTOM QUESTIONS")
print("=" * 70)

# Test questions organized by document
test_sets = {
    "Basel LCR": [
        "What is the Liquidity Coverage Ratio?",
        "What are high-quality liquid assets?",
        "What is the minimum LCR requirement?"
    ],
    
    "FATF 40 Recommendations": [
        "What is Customer Due Diligence?",
        "When should enhanced due diligence be applied?",
        "What are Politically Exposed Persons?"
    ],
    
    "Risk-Based Approach": [
        "What is the risk-based approach in banking?",
        "How should banks assess money laundering risks?",
        "What are red flags for suspicious transactions?"
    ],
    
    "Cross-Document": [
        "How do FATF recommendations relate to Basel requirements?",
        "What are common compliance requirements in banking?"
    ]
}

# Run tests
for category, questions in test_sets.items():
    print(f"\n{'='*70}")
    print(f"📋 CATEGORY: {category}")
    print(f"{'='*70}")
    
    for i, question in enumerate(questions, 1):
        print(f"\n❓ Question {i}: {question}")
        print("-" * 70)
        
        try:
            result = rag_query(question, top_k=3)
            
            print(f"\n💡 ANSWER:")
            # Print first 300 characters
            answer = result['answer']
            if len(answer) > 300:
                print(f"{answer[:300]}...")
            else:
                print(answer)
            
            print(f"\n📚 SOURCES:")
            for j, source in enumerate(result['sources'], 1):
                print(f"   {j}. {source['source']} - {source['regulator']}")
        
        except Exception as e:
            print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ TESTING COMPLETE!")
print("=" * 70)