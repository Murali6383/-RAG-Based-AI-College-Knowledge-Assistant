from pathlib import Path
import json
import re

import numpy as np
import faiss

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import (
    DOCUMENTS_DIR,
    INDEX_DIR,
    EMBEDDING_MODEL,
    RELEVANCE_THRESHOLD,
    TOP_K,
)


class RAGEngine:

    def __init__(self):
        print("🔄 Loading embedding model...")

        self.model = SentenceTransformer(EMBEDDING_MODEL)

        self.index = None
        self.chunks = []

        # TF-IDF keyword search
        self.tfidf = None
        self.tfidf_matrix = None

        self.load()

    # ---------------------------------------------------------
    # PDF EXTRACTION
    # ---------------------------------------------------------

    def extract_pdfs(self):

        chunks = []

        for path in sorted(DOCUMENTS_DIR.glob("*.pdf")):

            try:
                print(f"📄 Reading: {path.name}")

                reader = PdfReader(str(path))

                for page_no, page in enumerate(reader.pages, start=1):

                    text = (page.extract_text() or "").strip()

                    if not text:
                        continue

                    # Normalize whitespace
                    text = re.sub(r"\s+", " ", text)

                    words = text.split()

                    chunk_words = 180
                    overlap = 30

                    start = 0

                    while start < len(words):

                        part = " ".join(
                            words[start:start + chunk_words]
                        ).strip()

                        if part:
                            chunks.append({
                                "text": part,
                                "file": path.name,
                                "page": page_no
                            })

                        if start + chunk_words >= len(words):
                            break

                        start += chunk_words - overlap

            except Exception as e:
                print(f"❌ Could not read {path.name}: {e}")

        print(f"✅ Total chunks created: {len(chunks)}")

        return chunks

    # ---------------------------------------------------------
    # BUILD INDEX
    # ---------------------------------------------------------

    def build(self):

        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

        self.chunks = self.extract_pdfs()

        if not self.chunks:

            self.index = None
            self.tfidf = None
            self.tfidf_matrix = None

            return 0

        texts = [c["text"] for c in self.chunks]

        # -----------------------------------------------------
        # 1. FAISS SEMANTIC INDEX
        # -----------------------------------------------------

        print("🧠 Creating semantic embeddings...")

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        vectors = np.asarray(
            vectors,
            dtype="float32"
        )

        self.index = faiss.IndexFlatIP(
            vectors.shape[1]
        )

        self.index.add(vectors)

        faiss.write_index(
            self.index,
            str(INDEX_DIR / "knowledge.faiss")
        )

        # -----------------------------------------------------
        # 2. TF-IDF KEYWORD INDEX
        # -----------------------------------------------------

        print("🔎 Creating keyword index...")

        self.tfidf = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

        self.tfidf_matrix = self.tfidf.fit_transform(texts)

        # Save chunks
        (INDEX_DIR / "chunks.json").write_text(
            json.dumps(
                self.chunks,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print("✅ FAISS + TF-IDF index created")

        return len(self.chunks)

    # ---------------------------------------------------------
    # LOAD INDEX
    # ---------------------------------------------------------

    def load(self):

        index_file = INDEX_DIR / "knowledge.faiss"
        chunks_file = INDEX_DIR / "chunks.json"

        if index_file.exists() and chunks_file.exists():

            try:

                self.index = faiss.read_index(
                    str(index_file)
                )

                self.chunks = json.loads(
                    chunks_file.read_text(
                        encoding="utf-8"
                    )
                )

                # Rebuild TF-IDF from saved chunks
                texts = [
                    c["text"]
                    for c in self.chunks
                ]

                if texts:

                    self.tfidf = TfidfVectorizer(
                        lowercase=True,
                        stop_words="english",
                        ngram_range=(1, 2)
                    )

                    self.tfidf_matrix = self.tfidf.fit_transform(
                        texts
                    )

                print(
                    f"✅ Loaded {len(self.chunks)} chunks"
                )

            except Exception as e:

                print(
                    f"⚠️ Could not load index: {e}"
                )

                self.index = None
                self.chunks = []
                self.tfidf = None
                self.tfidf_matrix = None

    # ---------------------------------------------------------
    # HYBRID SEARCH
    # ---------------------------------------------------------

    def search(
        self,
        question: str,
        k: int = TOP_K
    ):

        if (
            self.index is None
            or not self.chunks
        ):
            return [], 0.0, False

        # -----------------------------------------------------
        # STEP 1: SEMANTIC SEARCH
        # -----------------------------------------------------

        query_embedding = self.model.encode(
            [question],
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        # Retrieve more candidates than final K
        candidate_k = min(
            max(k * 2, 10),
            len(self.chunks)
        )

        semantic_scores, semantic_ids = self.index.search(
            query_embedding,
            candidate_k
        )

        # -----------------------------------------------------
        # STEP 2: TF-IDF KEYWORD SEARCH
        # -----------------------------------------------------

        keyword_scores = np.zeros(
            len(self.chunks),
            dtype="float32"
        )

        if (
            self.tfidf is not None
            and self.tfidf_matrix is not None
        ):

            query_tfidf = self.tfidf.transform(
                [question]
            )

            scores = (
                self.tfidf_matrix @ query_tfidf.T
            ).toarray().flatten()

            keyword_scores = scores

        # -----------------------------------------------------
        # STEP 3: NORMALIZE SEMANTIC SCORES
        # -----------------------------------------------------

        semantic_map = {}

        for score, idx in zip(
            semantic_scores[0],
            semantic_ids[0]
        ):

            if idx >= 0:
                semantic_map[int(idx)] = float(score)

        if semantic_map:

            semantic_min = min(
                semantic_map.values()
            )

            semantic_max = max(
                semantic_map.values()
            )

            semantic_range = (
                semantic_max - semantic_min
            )

        else:

            semantic_min = 0.0
            semantic_range = 0.0

        # -----------------------------------------------------
        # STEP 4: COMBINE SCORES
        # -----------------------------------------------------

        combined = []

        for idx in range(len(self.chunks)):

            semantic_score = semantic_map.get(
                idx,
                0.0
            )

            keyword_score = float(
                keyword_scores[idx]
            )

            # Normalize semantic score among candidates
            if semantic_range > 0:
                normalized_semantic = (
                    semantic_score - semantic_min
                ) / semantic_range
            else:
                normalized_semantic = semantic_score

            # Hybrid score
            hybrid_score = (
                0.70 * normalized_semantic
                +
                0.30 * keyword_score
            )

            combined.append(
                (
                    hybrid_score,
                    semantic_score,
                    keyword_score,
                    idx
                )
            )

        # -----------------------------------------------------
        # STEP 5: SORT
        # -----------------------------------------------------

        combined.sort(
            key=lambda x: x[0],
            reverse=True
        )

        # -----------------------------------------------------
        # STEP 6: CREATE RESULTS
        # -----------------------------------------------------

        results = []

        for (
            hybrid_score,
            semantic_score,
            keyword_score,
            idx
        ) in combined[:k]:

            item = dict(
                self.chunks[idx]
            )

            item["score"] = float(
                hybrid_score
            )

            item["semantic_score"] = float(
                semantic_score
            )

            item["keyword_score"] = float(
                keyword_score
            )

            results.append(item)

        # Best score
        best = (
            results[0]["score"]
            if results
            else 0.0
        )

        grounded = (
            best >= RELEVANCE_THRESHOLD
        )

        return (
            results,
            best,
            grounded
        )