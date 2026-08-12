<div align="center">
  <h1>💬 Codebase RAG Assistant</h1>
  <p><strong>Chat with your entire codebase using advanced Retrieval-Augmented Generation.</strong></p>
</div>

## 🚀 Overview
The Codebase RAG Assistant allows developers to ingest an entire local repository or GitHub URL and interact with it using natural language. It helps in onboarding, debugging, and understanding large codebases without having to manually sift through thousands of files.

## ✨ Features
- **Semantic Code Search:** Uses embeddings (OpenAI/BGE) to understand the semantic intent behind your queries.
- **Source Citations:** Every AI answer includes direct links/references to the specific files and line numbers it used.
- **Repository Ingestion:** Ingest local ZIP files or directly clone from GitHub URLs.
- **Interactive File Tree:** Browse the structure of the ingested project directly from the chat UI.

## 🛠️ Tech Stack
- **RAG Framework:** [LangChain](https://python.langchain.com/)
- **Vector Store:** [ChromaDB](https://www.trychroma.com/)
- **Embeddings:** `text-embedding-3-large`
- **Frontend UI:** [Streamlit](https://streamlit.io/)

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Muhammad08-dot/codebase-rag-assistant.git
   cd codebase-rag-assistant
   ```

2. **Install dependencies:**
   ```bash
   pip install langchain chromadb openai tiktoken streamlit
   ```

3. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

## 📄 License
This project is licensed under the MIT License.
