import os
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def chat_with_codebase():
    persist_dir = "./storage"
    if not os.path.exists(persist_dir):
        print("Storage directory not found. Please run ingest.py first.")
        return
        
    print("Loading codebase index...")
    
    # Setup embedding model matching ingestion
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # Load from storage
    vector_store = FaissVectorStore.from_persist_dir(persist_dir)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, 
        persist_dir=persist_dir
    )
    
    index = load_index_from_storage(
        storage_context=storage_context,
        embed_model=embed_model
    )
    
    # In a real environment, we configure the LLM (e.g. Gemini/OpenAI).
    # Using the default query engine.
    query_engine = index.as_query_engine()
    
    print("\n--- Codebase RAG Assistant ---")
    print("Type 'exit' to quit.")
    
    while True:
        query = input("\nAsk about your codebase: ")
        if query.lower() == 'exit':
            break
            
        try:
            response = query_engine.query(query)
            print(f"\n[Assistant]: {response}")
        except Exception as e:
            print(f"Error querying LLM: {e}. Note: You may need to set your LLM API Key.")

if __name__ == "__main__":
    chat_with_codebase()
