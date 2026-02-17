import os
import sys
# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Get absolute paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BACKEND_DIR, "..", "data", "nelfund_docs")
CHROMA_DIR = os.path.join(BACKEND_DIR, "chroma_db")


def ingest():
    documents = []

    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"Missing folder: {DATA_DIR}")

    # Process PDF files
    for file in os.listdir(DATA_DIR):
        if file.lower().endswith(".pdf"):
            path = os.path.join(DATA_DIR, file)
            print(f"Loading PDF: {file}")
            try:
                loader = PyPDFLoader(path)
                pages = loader.load()

                for page in pages:
                    page.metadata["source"] = file

                documents.extend(pages)
                print(f"  [OK] Loaded {len(pages)} pages from {file}")
            except Exception as e:
                print(f"  [ERROR] Error loading {file}: {e}")
        
        # Process text files
        elif file.lower().endswith(".txt"):
            path = os.path.join(DATA_DIR, file)
            print(f"Loading text file: {file}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split large text files into chunks for better processing
                doc = Document(
                    page_content=content,
                    metadata={"source": file}
                )
                documents.append(doc)
                print(f"  [OK] Loaded text file {file} ({len(content)} characters)")
            except Exception as e:
                print(f"  [ERROR] Error loading {file}: {e}")

    if not documents:
        raise ValueError("No documents (PDF or TXT) found for ingestion")
    
    print(f"\nTotal documents loaded: {len(documents)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=200
    )

    print(f"\nSplitting documents into chunks...")
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} documents")

    # Delete old database if it exists to avoid compatibility issues
    import shutil
    if os.path.exists(CHROMA_DIR):
        print(f"\nRemoving old database at {CHROMA_DIR}...")
        shutil.rmtree(CHROMA_DIR)
    
    # Create new vectorstore
    print(f"\nCreating vector database...")
    print("Initializing OpenAI embeddings...")
    try:
        embeddings = OpenAIEmbeddings()
        # Test the embeddings work
        test_embedding = embeddings.embed_query("test")
        print(f"OpenAI embeddings initialized successfully (test embedding dimension: {len(test_embedding)})")
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI embeddings: {e}")
        raise
    
    print("Creating vectorstore with OpenAI embeddings...")
    # Create Chroma instance with explicit embedding_function (matching retriever.py)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="langchain"
    )
    # Add documents to the vectorstore
    print("Adding documents to vectorstore...")
    vectorstore.add_documents(chunks)

    # Persist is not needed for newer versions, but won't hurt
    try:
        vectorstore.persist()
    except:
        pass  # Some versions don't need explicit persist
    
    print(f"\n[SUCCESS] NELFUND documents ingested successfully!")
    print(f"   - Total documents: {len(documents)}")
    print(f"   - Total chunks: {len(chunks)}")
    print(f"   - Database location: {CHROMA_DIR}")


if __name__ == "__main__":
    ingest()
