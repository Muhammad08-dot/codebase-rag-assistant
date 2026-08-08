import os
import faiss
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def ingest_codebase(directory_path: str = "./"):
    print(f"Ingesting codebase from {directory_path}...")
    
    # Load documents from the directory
    # (Excluding hidden files and virtual environments in a real app)
    documents = SimpleDirectoryReader(
        directory_path, 
        recursive=True, 
        exclude=["*.pyc", ".git/*", "__pycache__/*"]
    ).load_data()
    
    print(f"Loaded {len(documents)} code files.")
    
    # Setup embedding model
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # Setup FAISS vector store
    d = 384 # Dimension for bge-small
    faiss_index = faiss.IndexFlatL2(d)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create the index
    print("Building vector index...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model
    )
    
    # Save the index to disk
    index.storage_context.persist(persist_dir="./storage")
    print("Codebase successfully ingested and indexed in ./storage!")

if __name__ == "__main__":
    ingest_codebase()
