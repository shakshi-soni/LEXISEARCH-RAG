import os
import hashlib
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from chunker import chunk_pdf
from indexer import MemoryIndexer
from retriever import retrieve_hybrid
from generator import generate_answer

st.set_page_config(
    page_title="LexiSearch RAG",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


def call_number(text: str) -> str:
    h = hashlib.md5(text.encode()).hexdigest()
    return f"Q {h[:3].upper()}.{h[3:5]} M{h[5:7]}{h[7]} '26"


# --- HIGH-VISUAL IMPACT ARCHIVAL & TERMINAL STYLING ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Playfair+Display:ital,wght@0,600;0,700;1,400;1,600&display=swap" rel="stylesheet">

<style>
    /* 1. HIDE STREAMLIT CHROME */
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a120e; }
    ::-webkit-scrollbar-thumb { background: rgba(212, 175, 55, 0.3); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #d4af37; }

    /* Global Typography */
    html, body, [class*="css"] { 
        font-family: 'JetBrains Mono', monospace; 
    }

    /* Main Animated Background Canvas */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1c3328 0%, #0a120e 80%);
        color: #e2e8f0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: rgba(10, 18, 14, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(212, 175, 55, 0.2) !important;
        padding-top: 1.8rem !important;
    }

    /* Animated Gold Pill Badges */
    .drawer-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #0b1410;
        background: linear-gradient(135deg, #f3e5ab 0%, #d4af37 50%, #aa820a 100%);
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
        margin-bottom: 14px;
    }

    /* Hero Title with Ambient Glow */
    .hero-container {
        position: relative;
        padding-bottom: 10px;
    }
    
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-weight: 700;
        font-size: 4rem;
        background: linear-gradient(180deg, #ffffff 20%, #f3e5ab 60%, #d4af37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        line-height: 1.05;
        filter: drop-shadow(0 0 25px rgba(212, 175, 55, 0.15));
    }
    
    .hero-sub {
        font-family: 'JetBrains Mono', monospace;
        color: #8da399;
        font-size: 0.85rem;
        margin-top: 10px;
        letter-spacing: -0.01em;
    }

    /* METRIC STAT CARDS BAR */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
        margin: 22px 0 28px 0;
    }
    
    .stat-card {
        background: rgba(18, 30, 24, 0.6);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 10px;
        padding: 14px 18px;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        border-color: #d4af37;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4), 0 0 12px rgba(212, 175, 55, 0.15);
    }
    .stat-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f3e5ab;
    }
    .stat-label {
        font-size: 0.68rem;
        color: #7a8b7e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 2px;
    }

    /* Refined Glass Center Empty State */
    .reading-table {
        background: radial-gradient(circle at 50% 50%, rgba(28, 48, 38, 0.7) 0%, rgba(14, 24, 19, 0.8) 100%);
        border: 1px solid rgba(212, 175, 55, 0.25);
        border-radius: 18px;
        padding: 70px 40px;
        text-align: center;
        backdrop-filter: blur(16px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.5), inset 0 0 30px rgba(212, 175, 55, 0.05);
        margin-top: 10px;
    }

    /* Call Slip (User Bubble) with Hover Effect */
    .call-slip {
        background: linear-gradient(135deg, #22362b 0%, #15241b 100%);
        color: #f1f5f9;
        border-left: 4px solid #d4af37;
        border-radius: 10px;
        padding: 20px 24px;
        margin: 20px 0 12px auto;
        max-width: 82%;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35);
        transition: transform 0.2s ease;
    }
    .call-slip:hover {
        transform: translateX(-3px);
    }
    
    .call-slip-label {
        font-size: 0.65rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #d4af37;
        margin-bottom: 8px;
        display: block;
        font-weight: 600;
    }

    /* Index Card (AI Bubble) with Glowing Top Border */
    .index-card {
        background: rgba(18, 30, 24, 0.9);
        color: #e2e8f0;
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-top: 3px solid #d4af37;
        border-radius: 12px;
        padding: 28px 32px;
        margin: 12px 0 24px 0;
        max-width: 92%;
        box-shadow: 0 16px 40px rgba(0,0,0,0.5), 0 0 15px rgba(212, 175, 55, 0.05);
        line-height: 1.8;
        font-size: 0.96rem;
        backdrop-filter: blur(16px);
        transition: all 0.3s ease;
    }
    .index-card:hover {
        border-color: rgba(212, 175, 55, 0.4);
        box-shadow: 0 20px 45px rgba(0,0,0,0.6), 0 0 20px rgba(212, 175, 55, 0.12);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 18px;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .call-num {
        font-size: 0.78rem;
        color: #d4af37;
        background: rgba(212, 175, 55, 0.12);
        padding: 5px 12px;
        border-radius: 6px;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }

    /* Badges */
    .due-stamp {
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .stamp-sourced { 
        color: #4ade80; 
        background: rgba(74, 222, 128, 0.15);
        border: 1px solid rgba(74, 222, 128, 0.35);
    }
    .stamp-shelf { 
        color: #f87171; 
        background: rgba(248, 113, 113, 0.15);
        border: 1px solid rgba(248, 113, 113, 0.35);
    }

    /* Citations */
    .catalog-entry {
        background: rgba(10, 18, 14, 0.8);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-left: 3px solid #d4af37;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .catalog-tag {
        font-size: 0.75rem;
        color: #d4af37;
        font-weight: 600;
    }
    .catalog-text {
        font-size: 0.88rem;
        margin-top: 8px;
        color: #cbd5e1;
        line-height: 1.6;
    }

    /* High Glow Button */
    .stButton > button {
        background: linear-gradient(135deg, #f3e5ab 0%, #d4af37 50%, #aa820a 100%) !important;
        color: #0b1410 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 13px 22px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.06em;
        width: 100%;
        transition: all 0.25s ease-in-out !important;
        box-shadow: 0 4px 18px rgba(212, 175, 55, 0.25) !important;
    }
    .stButton > button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(212, 175, 55, 0.45) !important;
    }

    /* Active Pulse Status Box */
    .shelf-status {
        font-size: 0.8rem;
        padding: 14px 16px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-top: 12px;
    }
    .shelf-open { 
        color: #4ade80; 
        background: rgba(74, 222, 128, 0.08);
        border-color: rgba(74, 222, 128, 0.25);
    }
    .shelf-empty { 
        color: #94a3b8; 
        background: rgba(148, 163, 184, 0.05);
        border-color: rgba(148, 163, 184, 0.15);
    }

    /* Inputs Focus Polish */
    .stTextInput input, .stChatInput input {
        background: rgba(18, 30, 24, 0.85) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
    }
    .stTextInput input:focus, .stChatInput input:focus {
        border-color: #d4af37 !important;
        box-shadow: 0 0 16px rgba(212, 175, 55, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

API_KEY = os.environ.get("GROQ_API_KEY")

if "indexer" not in st.session_state:
    st.session_state.indexer = MemoryIndexer()
if "indexed" not in st.session_state:
    st.session_state.indexed = False
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<span class="drawer-label">Accessions Desk</span>', unsafe_allow_html=True)
    st.markdown("### 🔍 LexiSearch RAG")
    st.caption("Bring your documents to the desk. Every answer comes with its call number.")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Accession new documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Reports, contracts, papers — anything you want catalogued and searchable."
    )

    if uploaded_files:
        if st.button("Catalogue Collection"):
            all_chunks = []
            with st.spinner("Cataloguing pages, cutting index cards..."):
                for uploaded_file in uploaded_files:
                    file_bytes = uploaded_file.getvalue()
                    chunks = chunk_pdf(file_bytes, uploaded_file.name)
                    all_chunks.extend(chunks)

            if all_chunks:
                st.session_state.indexer.build_index(all_chunks)
                st.session_state.indexed = True
                st.session_state.chunk_count = len(all_chunks)
                st.toast("Collection catalogued successfully!", icon="📚")
            else:
                st.error("No extractable text found in the uploaded files.")

    if st.session_state.indexed:
        st.markdown(f"""
        <div class="shelf-status shelf-open">
            <span style="color: #4ade80;">● ACTIVE VAULT</span><br>
            <span style="font-weight: 700; font-size: 1.15rem; color: #ffffff;">{st.session_state.chunk_count}</span> vector cards ready
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="shelf-status shelf-empty">
            ○ DESK INACTIVE<br>
            Upload PDFs to launch indexing
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.messages:
        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
        if st.button("Clear Table"):
            st.session_state.messages = []
            st.rerun()

# --- MAIN HERO HEADER ---
st.markdown('<div class="hero-container">', unsafe_allow_html=True)
st.markdown('<span class="drawer-label">Intelligence Vault</span>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">LexiSearch RAG</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">// hybrid retrieval — BM25 + dense embeddings fused with RRF. '
    'grounded in your data with zero hallucination.</p>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

# --- QUICK METRICS BAR ---
st.markdown(f"""
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">BM25 + Dense</div>
        <div class="stat-label">Fusion Pipeline</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">384-Dim</div>
        <div class="stat-label">MiniLM Vectors</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">Llama-3.3-70B</div>
        <div class="stat-label">Synthesis Engine</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{st.session_state.chunk_count if st.session_state.indexed else 0}</div>
        <div class="stat-label">Indexed Chunks</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- MAIN CONTENT BODY ---
if not st.session_state.indexed:
    st.markdown("""
    <div class="reading-table">
        <div style="font-size: 3rem; margin-bottom: 12px; filter: drop-shadow(0 0 12px rgba(212, 175, 55, 0.4));">🔍</div>
        <h3 style="font-family: 'Playfair Display', serif; font-style: italic; font-weight: 600; color: #F0E9D8; font-size: 1.9rem; margin-bottom: 10px;">
            The reading table is ready
        </h3>
        <p style="color: #8da399; max-width: 480px; margin: 0 auto; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; line-height: 1.6;">
            Upload your PDF research papers or documents at the accessions desk in the sidebar to populate the hybrid retrieval engine.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    if not API_KEY:
        st.error("GROQ_API_KEY missing from your .env file.")
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'''
                    <div class="call-slip">
                        <div class="call-slip-label">Call Slip Query</div>
                        {msg["content"]}
                    </div>
                ''', unsafe_allow_html=True)
            else:
                has_sources = "sources" in msg and msg["sources"]
                stamp_html = (
                    '<span class="due-stamp stamp-sourced">SOURCED ✓</span>'
                    if has_sources else
                    '<span class="due-stamp stamp-shelf">NOT ON SHELF</span>'
                )
                st.markdown(f'''
                    <div class="index-card">
                        <div class="card-header">
                            <span class="call-num">{call_number(msg["content"])}</span>
                            {stamp_html}
                        </div>
                        {msg["content"]}
                    </div>
                ''', unsafe_allow_html=True)

                if has_sources:
                    with st.expander(f"View {len(msg['sources'])} catalogue citations"):
                        for idx, chunk in enumerate(msg["sources"], 1):
                            source = chunk["metadata"].get("source", "Unknown")
                            page = chunk["metadata"].get("page", "N/A")
                            st.markdown(f"""
                            <div class="catalog-entry">
                                <span class="catalog-tag">Card {idx} — {source}, p.{page}</span>
                                <div class="catalog-text">{chunk['text']}</div>
                            </div>
                            """, unsafe_allow_html=True)

        query = st.chat_input("Ask the intelligence vault...")

        if query:
            st.session_state.messages.append({"role": "user", "content": query})
            st.markdown(f'''
                <div class="call-slip">
                    <div class="call-slip-label">Call Slip Query</div>
                    {query}
                </div>
            ''', unsafe_allow_html=True)

            with st.spinner("Executing RRF hybrid search across vector indices..."):
                retrieved_chunks = retrieve_hybrid(query, st.session_state.indexer, top_k=5)
                answer = generate_answer(query, retrieved_chunks, api_key=API_KEY)

            st.session_state.messages.append({
                "role": "ai",
                "content": answer,
                "sources": retrieved_chunks
            })
            st.rerun()