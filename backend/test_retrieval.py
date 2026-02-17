"""Test script to check if ChromaDB retrieval is working"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.rag.retriever import retrieve

print("Testing ChromaDB retrieval...")
print("-" * 50)

try:
    query = "student loan eligibility"
    results = retrieve(query, k=3)
    
    print(f"Query: '{query}'")
    print(f"Retrieved {len(results)} documents")
    print("-" * 50)
    
    if len(results) == 0:
        print("❌ No documents retrieved! The database might be empty.")
        print("You may need to run the ingestion script:")
        print("  python -m app.rag.ingest")
    else:
        print("✅ Documents retrieved successfully!")
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'unknown')
            content_preview = doc.page_content[:150].replace('\n', ' ')
            print(f"\nDocument {i}:")
            print(f"  Source: {source}")
            print(f"  Content: {content_preview}...")
            
except Exception as e:
    print(f"❌ Error during retrieval: {e}")
    import traceback
    traceback.print_exc()

