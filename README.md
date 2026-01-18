# 🏦 Banking Policy & Compliance RAG Chatbot

An AI-driven Retrieval-Augmented Generation (RAG) chatbot designed for banking regulation and compliance inquiries. Developed using LangChain, ChromaDB, Groq AI, and Streamlit, it enables intelligent querying across Basel, FATF, RBI, and UAE regulatory frameworks, with an in-depth approach to document chunking for improved accuracy and context retrieval.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.40-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Features

- **Hybrid Search**: Combines semantic (dense) and keyword (BM25) search for accurate results
- **Multiple Regulators**: Supports Basel Committee, FATF, RBI, UAE Central Bank documents
- **Source Citations**: Every answer includes source documents with download options
- **Professional UI**: Clean, enterprise-grade Streamlit interface
- **Free AI Model**: Uses Groq's Llama 3.3 (70B) for intelligent responses

## 📚 Supported Documents

- Basel III Liquidity Coverage Ratio (LCR)
- FATF 40 Recommendations
- FATF Risk-Based Approach for Banking
- RBI Basel III Capital Guidelines
- RBI KYC Master Direction
- RBI Priority Sector Lending
- UAE AML/CFT Framework
- UAE Consumer Protection
- UAE Digital Banks Guidelines

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/nithinraj49/banking-compliance-rag.git
cd banking-compliance-rag
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at: https://console.groq.com/

5. **Process PDF documents** (if not already done)
```bash
python process_pdfs.py
python create_embeddings.py
python hybrid_search.py
```

6. **Run the application**
```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

## 📖 Usage

### Ask Questions

 Questions about banking regulations:
- "What is the Liquidity Coverage Ratio?"
- "What are KYC requirements for corporate accounts?"
- "How should banks report suspicious transactions?"

### View Sources

Click "Reference Documents" to see which regulatory documents were used and download them.

### Clear History

Use the "Clear History" button in the sidebar to reset the conversation.

## 🏗️ Architecture
```
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Streamlit│
    │    UI    │
    └────┬─────┘
         │
    ┌────▼──────────┐
    │ RAG Pipeline  │
    │  (LangChain)  │
    └───┬───────┬───┘
        │       │
   ┌────▼───┐ ┌▼────────┐
   │Hybrid  │ │  Groq   │
   │Retriever│ │  LLM    │
   └────┬───┘ └─────────┘
        │
   ┌────▼─────────┐
   │  ChromaDB    │
   │  (Vector DB) │
   └──────────────┘
```

## 🛠️ Tech Stack

- **LLM**: Groq (Llama 3.3 70B)
- **Framework**: LangChain
- **Vector DB**: ChromaDB
- **Embeddings**: sentence-transformers/all-mpnet-base-v2
- **Search**: Hybrid (ChromaDB + BM25)
- **UI**: Streamlit
- **PDF Processing**: PyPDF

## 📁 Project Structure
```
banking-compliance-rag/
├── data/
│   ├── *.pdf                          # Source regulatory PDFs (9 files)
│   ├── processed/
│   │   ├── chunks.pkl                 # Processed text chunks
│   │   ├── bm25_index.pkl             # BM25 search index
│   │   ├── retriever_components.pkl   # Retriever state
│   │   └── summary.txt                # Processing summary
│   └── chroma_db/                     # Vector database
│       └── chroma.sqlite3
├── app.py                             # Streamlit UI (main app)
├── process_pdfs.py                    # PDF text extraction & chunking
├── create_embeddings.py               # Vector embeddings creation
├── hybrid_search.py                   # Hybrid retriever setup
├── rag.py                             # RAG pipeline with LLM
├── diagnose.py                        # System diagnostics
├── inspect_chunks.py                  # Chunk inspection utility
├── test_rag_questions.py              # RAG testing script
├── validate_boundaries.py             # Chunk boundary validation
├── requirements.txt                   # Python dependencies
├── .env                               # Environment template


```

## ⚙️ Configuration

### Modify Retrieval Parameters

Edit `rag.py`:
```python
result = rag_query(
    question=question_text,
    top_k=3,  # Number of documents to retrieve
    filter_metadata=None  # Filter by regulator
)
```

### Change LLM Settings

Edit `rag.py`:
```python
GROQ_MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.1  # Lower = more focused
MAX_TOKENS = 2000
```

### Adjust Answer Length

Edit the RAG prompt in `rag.py`:
```python
- Keep answer between 80-120 words (be concise and direct)
```

## 🧪 Testing

Run individual test scripts:
```bash
# Test PDF processing
python process_pdfs.py

# Test embeddings
python create_embeddings.py

# Test hybrid search
python hybrid_search.py

# Test RAG pipeline
python test_rag_questions.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Basel Committee on Banking Supervision
- Financial Action Task Force (FATF)
- Reserve Bank of India (RBI)
- UAE Central Bank
- Groq for providing free LLM access


## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

- **Issues**: https://github.com/nithinraj49/banking-compliance-rag/issues
- **Discussions**: https://github.com/nithinraj49/banking-compliance-rag/discussions

# ⚠️ Disclaimer

**Important Notice:**

This tool is for **informational and educational purposes only**. 

- ✅ Use for research and learning
- ✅ Use to understand regulatory frameworks
- ❌ Do NOT use as legal advice
- ❌ Do NOT use as sole compliance reference



**Planned Features:**
- [ ] Support for more regulators (FSA, MAS, HKMA)
- [ ] Multi-language support
- [ ] Advanced filtering (by date, jurisdiction)
- [ ] Export conversations to PDF
- [ ] Custom document upload
- [ ] RAGAS evaluation metrics
- [ ] API endpoint for integration

## 📊 Statistics

- **Documents**: 9 regulatory PDFs
- **Total Chunks**: ~850+ text segments
- **Vector Dimensions**: 768 (all-mpnet-base-v2)
- **Average Response Time**: 2-3 seconds
- **Supported Regulators**: 4 (Basel, FATF, RBI, UAE)

---


**Built using LangChain, ChromaDB, and Groq AI**


