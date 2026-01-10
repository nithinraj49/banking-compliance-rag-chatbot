# app.py
import streamlit as st
import sys
from pathlib import Path
import time

# Add project to path
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

# Import RAG components
from rag_pipeline_groq import rag_query

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Banking Compliance Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PROFESSIONAL CSS STYLING
# ============================================================
st.markdown("""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background - Professional gradient */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e8ba3 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Main title */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        padding: 2rem 0 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #e0e0e0;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 300;
    }
    
    /* Chat container */
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        backdrop-filter: blur(10px);
    }
    
    /* User message */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px 15px 5px 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .user-message strong {
        display: block;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Assistant message */
    .assistant-message {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #2d3748;
        padding: 1.2rem;
        border-radius: 15px 15px 15px 5px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-size: 1rem;
        line-height: 1.8;
    }
    
    .assistant-message strong {
        display: block;
        margin-bottom: 0.8rem;
        color: #1a365d;
        font-size: 0.9rem;
    }
    
    /* Source boxes */
    .source-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #f59e0b;
        color: #78350f;
        font-size: 0.95rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin: 1rem 0 2rem 0;
        color: #1e293b;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        line-height: 1.7;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input field */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.8rem;
        font-size: 1rem;
        color: #2d3748;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }
    
    /* Hide input label */
    .stTextInput > label {
        display: none;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 0.9rem;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide the form container background */
    [data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    /* Download link styling */
    .download-link {
        display: inline-block;
        color: #78350f;
        text-decoration: none;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        padding: 0.3rem 0.6rem;
        border: 1px solid #f59e0b;
        border-radius: 5px;
        transition: all 0.2s;
    }
    
    .download-link:hover {
        background: #f59e0b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0

# ============================================================
# SIDEBAR - MINIMAL & PROFESSIONAL
# ============================================================
with st.sidebar:
    # Logo/Header - UPDATED NAME
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 2rem;'>
        <h1 style='color: white; font-size: 2.5rem; margin: 0; font-weight: 700;'>🏦</h1>
        <h2 style='color: white; font-size: 1.4rem; margin: 0.8rem 0 0 0; font-weight: 600;'>Banking Compliance</h2>
        <p style='color: #b0c4de; font-size: 1rem; margin: 0.5rem 0 0 0; font-weight: 300;'>Advisory System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analytics Dashboard
    st.markdown("### 📊 Analytics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Queries", st.session_state.total_queries)
    with col2:
        st.metric("History", len(st.session_state.chat_history))
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Action Buttons
    if st.button("🗑️ Clear History", use_container_width=True, type="primary"):
        st.session_state.chat_history = []
        st.session_state.total_queries = 0
        st.rerun()
    
    # REMOVED: Quick Questions section
    


# ============================================================
# MAIN AREA
# ============================================================

# Title
st.markdown('<div class="main-title">Banking Policy & Compliance Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Regulatory Intelligence Platform</div>', unsafe_allow_html=True)

# Welcome Message - UPDATED (Generic for all regulatory documents)
if len(st.session_state.chat_history) == 0:
    st.markdown("""
    <div class="info-box">
        <h3 style='margin-top: 0; color: #1e40af;'>Welcome to Banking Compliance Advisory System</h3>
        <p style='margin-bottom: 0.5rem;'>Get instant answers about:</p>
        <ul style='margin-top: 0.5rem; margin-bottom: 1rem;'>
            <li>Banking regulations and compliance requirements</li>
            <li>Anti-Money Laundering (AML) and Counter-Terrorist Financing (CFT)</li>
            <li>Customer Due Diligence and KYC procedures</li>
            <li>Capital adequacy and liquidity standards</li>
            <li>Risk management frameworks</li>
            <li>Regulatory reporting obligations</li>
        </ul>
        <p style='margin: 0; padding-top: 1rem; border-top: 1px solid #e2e8f0; font-style: italic; color: #64748b; font-size: 0.95rem;'>
            Powered by international regulatory standards and best practices.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# CHAT HISTORY
# ============================================================
for i, chat in enumerate(st.session_state.chat_history):
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # User message - UPDATED LABEL
    st.markdown(f"""
    <div class="user-message">
        <strong>Question</strong>
        {chat['question']}
    </div>
    """, unsafe_allow_html=True)
    
    # Assistant message - UPDATED LABEL
    st.markdown(f"""
    <div class="assistant-message">
        <strong>Response</strong>
        {chat['answer']}
    </div>
    """, unsafe_allow_html=True)
    
    # Sources - With download note
    if chat.get('sources'):
        # Remove duplicate documents
        seen_docs = set()
        unique_sources = []
        for source in chat['sources']:
            doc_key = (source['source'], source['regulator'])
            if doc_key not in seen_docs:
                seen_docs.add(doc_key)
                unique_sources.append(source)
        
        # Display unique sources
        with st.expander(f"📚 Reference Documents ({len(unique_sources)})", expanded=False):
            for source in unique_sources:
                # Get file path
                pdf_path = BASE_DIR / "data" / source['source']
                
                st.markdown(f"""
                <div class="source-box">
                    <strong>📄 {source['source']}</strong><br>
                    <span style="color: #78350f; font-size: 0.9rem;">
                        {source['regulator']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                # Add download button for each source
                if pdf_path.exists():
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label=f"⬇️ Download {source['source']}",
                            data=pdf_file,
                            file_name=source['source'],
                            mime="application/pdf",
                            key=f"download_{i}_{source['source']}"
                        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# QUESTION INPUT AREA - SIMPLIFIED
# ============================================================
st.markdown("---")

with st.form("question_form", clear_on_submit=True):
    user_question = st.text_input(
        "question",
        value="",
        placeholder="💬 Ask about banking regulations, compliance, AML/CFT, capital requirements...",
        label_visibility="collapsed"
    )
    
    # REMOVED: Try Random button - Only Ask button now
    submit_button = st.form_submit_button("🚀 Submit Query", use_container_width=True)

# ============================================================
# PROCESS QUESTION
# ============================================================
def process_question(question_text):
    if not question_text or not question_text.strip():
        st.warning("⚠️ Please enter a question.")
        return
    
    with st.spinner("🔍 Analyzing regulatory documents..."):
        try:
            start_time = time.time()
            result = rag_query(
                question=question_text,
                top_k=3,
                filter_metadata=None
            )
            end_time = time.time()
            
            st.session_state.chat_history.append({
                'question': question_text,
                'answer': result['answer'],
                'sources': result['sources'],
                'time': end_time - start_time
            })
            
            st.session_state.total_queries += 1
            st.success(f"✅ Response generated in {end_time - start_time:.2f}s")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if submit_button:
    process_question(user_question)

# ============================================================
# FOOTER
# ============================================================
st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.7); padding: 2rem 0;">
    <p style="margin: 0; font-size: 1rem; font-weight: 500;">
        Banking Compliance Advisory System
    </p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; font-weight: 300;">
        Enterprise-Grade Intelligence • Secure • Compliant
    </p>
</div>
""", unsafe_allow_html=True)
