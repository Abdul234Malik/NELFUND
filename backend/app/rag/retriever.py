import os
from app.core.config import OPENAI_API_KEY  # noqa: F401

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Get the backend directory (parent of app directory)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_DIR = os.path.join(BACKEND_DIR, "chroma_db")

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Initialize vectorstore - lazy initialization to handle errors
_vectorstore = None

def get_vectorstore():
    """Get or create the vectorstore instance with error handling"""
    global _vectorstore
    # Force reinitialization to ensure we get the latest database
    try:
        _vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
            collection_name="langchain"
        )
    except Exception as e:
        print(f"Error initializing ChromaDB: {e}")
        raise
    return _vectorstore

def retrieve(query: str, k: int = 4):
    """Retrieve documents from the vectorstore"""
    try:
        vs = get_vectorstore()
        results = vs.similarity_search(query, k)
        return results
    except (AttributeError, Exception) as e:
        error_msg = str(e)
        print(f"Error in retrieve: {error_msg}")
        
        # If it's the _client error, try accessing chromadb directly
        if "'Collection' object has no attribute '_client'" in error_msg or "_client" in error_msg:
            print("ChromaDB compatibility issue detected. Trying direct access workaround...")
            try:
                import chromadb
                from langchain_community.embeddings import OpenAIEmbeddings as LangchainOpenAIEmbeddings
                
                # Try direct chromadb access
                client = chromadb.PersistentClient(path=CHROMA_DIR)
                collection = client.get_or_create_collection(name="langchain")
                
                # Get query embedding
                query_embedding = embeddings.embed_query(query)
                
                # Search directly
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k
                )
                
                # Convert to langchain documents
                docs = []
                if results.get('ids') and len(results['ids']) > 0:
                    for i, doc_id in enumerate(results['ids'][0]):
                        content = results['documents'][0][i] if results.get('documents') and results['documents'][0] else ""
                        metadata = results['metadatas'][0][i] if results.get('metadatas') and results['metadatas'][0] else {}
                        docs.append(Document(page_content=content, metadata=metadata))
                
                if docs:
                    print(f"Successfully retrieved {len(docs)} documents using direct access")
                    return docs
                else:
                    print("No documents found in database. You may need to re-ingest.")
                    return []
                    
            except Exception as e2:
                print(f"Direct access workaround also failed: {e2}")
                import traceback
                traceback.print_exc()
                return []
        
        # For other errors, return empty list
        import traceback
        traceback.print_exc()
        return []
