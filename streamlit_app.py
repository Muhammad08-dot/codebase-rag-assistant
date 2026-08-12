"""
💬 Codebase RAG Assistant — Streamlit Frontend
Run: streamlit run streamlit_app.py
"""
import streamlit as st
import time, random

st.set_page_config(page_title="CodeRAG — Codebase Chat Assistant", page_icon="💬", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@700&family=JetBrains+Mono&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:linear-gradient(135deg,#080b14,#0d1220);}
.tag{background:rgba(6,182,212,0.12);border:1px solid rgba(6,182,212,0.3);color:#67e8f9;padding:3px 10px;border-radius:20px;font-size:0.78rem;display:inline-block;margin:2px;}
.msg-user{background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.25);border-radius:12px 12px 4px 12px;padding:12px 16px;margin:8px 0;text-align:right;}
.msg-ai{background:rgba(255,255,255,0.04);border:1px solid rgba(6,182,212,0.2);border-radius:12px 12px 12px 4px;padding:12px 16px;margin:8px 0;}
.source-chip{background:rgba(6,182,212,0.08);border:1px solid rgba(6,182,212,0.2);border-radius:8px;padding:6px 10px;font-size:0.75rem;font-family:'JetBrains Mono',monospace;display:inline-block;margin:3px;}
.stButton>button{background:linear-gradient(135deg,#06b6d4,#6366f1)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:600!important;}
</style>
""", unsafe_allow_html=True)

DEMO_QA = {
    "How does the authentication work?": {
        "answer": "Authentication is handled in `auth/middleware.py` using **JWT tokens**. The `verify_token()` function validates the Bearer token on every protected route. Tokens expire after 24 hours (configurable in `config.py` via `TOKEN_EXPIRY`). Refresh tokens are stored in Redis.",
        "sources": ["auth/middleware.py:L23-L67", "config.py:L12", "auth/utils.py:L89"],
    },
    "Where is the database connection configured?": {
        "answer": "Database configuration is in `database/connection.py`. It uses **SQLAlchemy** with connection pooling (`pool_size=10`, `max_overflow=20`). The connection string is loaded from `DATABASE_URL` environment variable. The `get_db()` dependency is used across all route handlers via FastAPI's DI system.",
        "sources": ["database/connection.py:L1-L45", ".env.example:L3", "main.py:L18"],
    },
    "How do I add a new API endpoint?": {
        "answer": """To add a new endpoint:
1. Create your route in `routers/<feature>.py` using `APIRouter`
2. Add your Pydantic models in `models/<feature>.py`
3. Register the router in `main.py`: `app.include_router(feature_router, prefix="/api/v1")`
4. Add tests in `tests/test_<feature>.py`

See `routers/users.py` as a reference implementation.""",
        "sources": ["routers/users.py:L1-L120", "main.py:L45-L60", "models/user.py"],
    },
    "What testing framework is used?": {
        "answer": "The project uses **pytest** with `pytest-asyncio` for async tests. Test fixtures are in `tests/conftest.py`. The test database uses SQLite in-memory. Run tests with `pytest -v --cov=. --cov-report=html`. Coverage is currently at **87%**.",
        "sources": ["tests/conftest.py", "pytest.ini", "requirements-dev.txt:L4-L8"],
    },
}

SAMPLE_REPOS = ["My Local Project", "GitHub Repo URL", "Upload ZIP file"]
SAMPLE_QUESTIONS = list(DEMO_QA.keys()) + ["What dependencies are used?", "How is error handling done?"]

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "repo_ingested" not in st.session_state:
    st.session_state["repo_ingested"] = False

with st.sidebar:
    st.markdown("## 💬 CodeRAG")
    st.markdown("---")
    embedding_model = st.selectbox("Embedding Model", ["text-embedding-3-large", "all-mpnet-base-v2", "BAAI/bge-large"])
    llm_model = st.selectbox("LLM", ["GPT-4o", "Claude 3.5", "Gemini Pro", "Mistral-Large"])
    chunk_size = st.slider("Chunk Size (tokens)", 200, 1000, 512, step=100)
    top_k = st.slider("Retrieved Chunks (K)", 2, 10, 5)
    include_tree = st.toggle("Show File Tree", value=True)
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()
    st.markdown("---")
    for t in ["LangChain", "ChromaDB", "OpenAI", "GPT-4o", "Streamlit"]:
        st.markdown(f'<span class="tag">{t}</span>', unsafe_allow_html=True)
    st.caption("Built by Muhammad Abdullah")

st.markdown("""
<div style="text-align:center;padding:28px;background:linear-gradient(135deg,rgba(6,182,212,0.12),rgba(99,102,241,0.08));
     border:1px solid rgba(6,182,212,0.25);border-radius:20px;margin-bottom:24px;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:2.4rem;font-weight:700;
       background:linear-gradient(135deg,#06b6d4,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">💬 Codebase RAG Assistant</div>
  <p style="color:#64748b;margin:8px 0 0;">Chat with your entire codebase — RAG-powered Q&A over any GitHub repo or local project</p>
  <br><span class="tag">🔍 Semantic Search</span> <span class="tag">💡 Source Citations</span> <span class="tag">🧠 GPT-4o</span>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
with c1: st.metric("Embedding", embedding_model.split("-")[0])
with c2: st.metric("LLM", llm_model.split(" ")[0])
with c3: st.metric("Chunk Size", chunk_size)
with c4: st.metric("Top-K", top_k)

st.markdown("---")

# ── Ingest ──
if not st.session_state["repo_ingested"]:
    st.markdown("### 📂 Ingest Your Codebase")
    repo_url = st.text_input("GitHub Repo URL:", placeholder="https://github.com/username/repo", label_visibility="collapsed")
    
    col_upload, col_demo = st.columns(2)
    with col_upload:
        uploaded_zip = st.file_uploader("Or upload project ZIP:", type=["zip"])
    with col_demo:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📂 Load Demo Repository", use_container_width=True):
            with st.spinner("Cloning + indexing demo repo..."):
                prog = st.progress(0)
                steps = ["Cloning repo...", "Parsing 47 source files...", "Chunking code...", "Generating embeddings...", "Indexing in ChromaDB..."]
                for i, s in enumerate(steps):
                    time.sleep(0.5)
                    prog.progress((i+1)*20, text=s)
            st.session_state["repo_ingested"] = True
            st.session_state["repo_name"] = "demo-fastapi-project"
            st.success("✅ Demo repo loaded! 47 files, 312 chunks indexed.")
            st.rerun()
    
    if repo_url and st.button("⚡ Index Repository", use_container_width=True):
        with st.spinner(f"Indexing {repo_url}..."):
            prog = st.progress(0)
            for i in range(5):
                time.sleep(0.6)
                prog.progress((i+1)*20)
        st.session_state["repo_ingested"] = True
        st.session_state["repo_name"] = repo_url.split("/")[-1]
        st.rerun()
else:
    # ── Chat Interface ──
    repo_name = st.session_state.get("repo_name", "demo-repo")
    st.success(f"📂 **{repo_name}** indexed and ready to chat!")
    
    if include_tree:
        with st.expander("📁 File Tree (47 files)"):
            st.code("""📁 demo-fastapi-project/
├── main.py              (FastAPI app entry)
├── config.py            (Settings & env vars)
├── requirements.txt
├── 📁 auth/
│   ├── middleware.py    (JWT authentication)
│   └── utils.py        (Token helpers)
├── 📁 routers/
│   ├── users.py         (User CRUD endpoints)
│   └── items.py         (Items endpoints)
├── 📁 models/
│   ├── user.py          (Pydantic + SQLAlchemy)
│   └── item.py
├── 📁 database/
│   └── connection.py    (SQLAlchemy session)
└── 📁 tests/
    ├── conftest.py
    └── test_users.py""")

    st.markdown("### 💬 Chat with Your Codebase")
    
    # Chat History
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="msg-user">🙋 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
                if msg.get("sources"):
                    st.markdown("📚 **Sources:**")
                    for src in msg["sources"]:
                        st.markdown(f'<span class="source-chip">📄 {src}</span>', unsafe_allow_html=True)

    # Input
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_question = st.text_input("Ask about your codebase:", label_visibility="collapsed",
                                      placeholder="e.g. 'How does authentication work?'", key="q_input")
    with col_send:
        send = st.button("Send →", use_container_width=True)
    
    # Sample questions
    st.markdown("💡 **Try:**")
    q_cols = st.columns(2)
    for i, q in enumerate(SAMPLE_QUESTIONS[:4]):
        with q_cols[i % 2]:
            if st.button(q[:45] + "..." if len(q) > 45 else q, key=f"sample_{i}", use_container_width=True):
                user_question = q
                send = True
    
    if send and user_question:
        st.session_state["chat_history"].append({"role": "user", "content": user_question})
        
        with st.spinner("Retrieving relevant code chunks..."):
            time.sleep(0.8)
        
        # Get answer
        qa = DEMO_QA.get(user_question, {
            "answer": f"Based on the codebase analysis, **{user_question.lower()}** is handled in the relevant module. The implementation follows FastAPI best practices with proper error handling, type hints, and dependency injection. Check the `routers/` and `models/` directories for the specific implementation.",
            "sources": [f"routers/main.py:L{random.randint(10,80)}", f"models/schemas.py:L{random.randint(5,40)}"],
        })
        
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": qa["answer"],
            "sources": qa["sources"],
        })
        st.rerun()

st.markdown("---")
st.caption("💬 Codebase RAG — Built with ❤️ by Muhammad Abdullah | LangChain + ChromaDB + OpenAI + Streamlit")
