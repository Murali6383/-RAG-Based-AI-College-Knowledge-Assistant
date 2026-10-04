from app.rag_backup import RAGEngine

rag = RAGEngine()

count = rag.build()

print()
print("=" * 50)
print(f"✅ RAG indexing completed")
print(f"📚 Total chunks: {count}")
print("=" * 50)