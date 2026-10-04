from pydantic import BaseModel, Field
from typing import Optional, List

class QueryRequest(BaseModel):
    question: str = Field(min_length=1)

class Source(BaseModel):
    file: str
    page: Optional[int] = None
    score: float

class QueryResponse(BaseModel):
    answer: str
    grounded: bool
    decision: Optional[str] = None
    sources: List[Source] = []
    retrieval_score: float = 0.0
