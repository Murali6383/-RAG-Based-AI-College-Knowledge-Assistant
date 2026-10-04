from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import QueryRequest, QueryResponse, Source
from .rag import RAGEngine
from .rules import attendance_decision
from .llm import generate

app = FastAPI(title="TruthGuard AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
rag = RAGEngine()

@app.get("/health")
def health():
    return {"status": "ok", "chunks": len(rag.chunks), "indexed": rag.index is not None}

@app.post("/admin/reindex")
def reindex():
    count = rag.build()
    return {"message": "Index rebuilt", "chunks": count}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    results, best, grounded = rag.search(req.question)
    if not grounded:
        return QueryResponse(
            answer="I couldn't find reliable information about this in the uploaded college/company documents. I don't want to provide an unsupported answer.",
            grounded=False,
            sources=[],
            retrieval_score=best,
        )

    context = "\n\n".join(
        f"SOURCE: {r['file']} | PAGE: {r['page']}\n{r['text']}" for r in results
    )
    decision = attendance_decision(req.question, context)
    answer = generate(req.question, context, decision)
    sources = [Source(file=r["file"], page=r["page"], score=round(r["score"], 4)) for r in results]
    return QueryResponse(
        answer=answer,
        grounded=True,
        decision=decision["decision"] if decision else None,
        sources=sources,
        retrieval_score=round(best, 4),
    )
