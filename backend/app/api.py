from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .pipeline import TruthGuardPipeline


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="TruthGuard AI",
    description=(
        "Hallucination-Reduced RAG Assistant "
        "for College Documents"
    ),
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Load TruthGuard Pipeline
# --------------------------------------------------

print("🚀 Starting TruthGuard API...")

pipeline = TruthGuardPipeline()

print("✅ TruthGuard Pipeline ready")


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class AskRequest(BaseModel):

    question: str


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "TruthGuard AI",
        "version": "1.0.0"
    }


# --------------------------------------------------
# Ask Question
# --------------------------------------------------

@app.post("/ask")
def ask_question(request: AskRequest):

    question = request.question.strip()

    # Validate empty question
    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = pipeline.ask(question)

        return {
            "success": result.get(
                "success",
                False
            ),

            "question": question,

            "answer": result.get(
                "answer",
                ""
            ),

            "grounded": result.get(
                "grounded",
                False
            ),

            "citations": result.get(
                "citations",
                []
            ),

            "sources": result.get(
                "sources",
                []
            ),

            "retrieval_score": result.get(
                "retrieval_score",
                0.0
            ),

            "rule_result": result.get(
                "rule_result"
            ),

            "grounding": result.get(
                "grounding"
            ),

            "output_grounding": result.get(
                "output_grounding"
            )
        }

    except Exception as e:

        print(
            f"❌ API error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred "
                "while processing the question."
            )
        )