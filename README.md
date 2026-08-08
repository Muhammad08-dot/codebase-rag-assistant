# Codebase Onboarding RAG Assistant

A Retrieval-Augmented Generation (RAG) tool designed for developers. It ingests an entire code repository, chunks the source code, and stores it in a FAISS vector database. Developers can then chat with their codebase to quickly onboard or find specific implementations.

## Features
- Ingests Python files and other text documents.
- Uses local HuggingFace embeddings (`BAAI/bge-small-en-v1.5`).
- Uses FAISS for high-performance vector search.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run ingestion: `python ingest.py`
3. Chat with codebase: `python chat.py`
