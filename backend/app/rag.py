from pathlib import Path
import json
import re
import pickle

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
    TOP_K
)


class RAGEngine:

    def __init__(self):

        print("🔄 Loading embedding model...")

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        self.index = None
        self.chunks = []

        self.vectorizer = None
        self.tfidf_matrix = None

        self.load()

    # ============================================================
    # TEXT NORMALIZATION
    # ============================================================

    def normalize_text(self, text: str):

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9%.\- ]+",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # ============================================================
    # TOKENIZATION
    # ============================================================

    def tokenize(self, text: str):

        text = self.normalize_text(text)

        return set(
            word
            for word in text.split()
            if len(word) > 2
        )

    # ============================================================
    # QUESTION ALIASES
    # ============================================================

    TERM_ALIASES = {

        "exam": [
            "exam",
            "exams",
            "examination",
            "examinations"
        ],

        "exams": [
            "exam",
            "exams",
            "examination",
            "examinations"
        ],

        "examination": [
            "exam",
            "exams",
            "examination",
            "examinations"
        ],

        "eligibility": [
            "eligibility",
            "eligible",
            "qualify",
            "qualification"
        ],

        "eligible": [
            "eligibility",
            "eligible",
            "qualify",
            "qualification"
        ],

        "rule": [
            "rule",
            "rules",
            "regulation",
            "regulations",
            "policy",
            "policies",
            "guideline",
            "guidelines"
        ],

        "rules": [
            "rule",
            "rules",
            "regulation",
            "regulations",
            "policy",
            "policies",
            "guideline",
            "guidelines"
        ],

        "attendance": [
            "attendance",
            "attended",
            "absent",
            "absence",
            "condonation"
        ],

        "hostel": [
            "hostel",
            "hostels",
            "warden",
            "mess",
            "room",
            "visitor",
            "outpass",
            "out-pass"
        ],

        "fee": [
            "fee",
            "fees",
            "payment",
            "payments",
            "dues"
        ],

        "fees": [
            "fee",
            "fees",
            "payment",
            "payments",
            "dues"
        ],

        "placement": [
            "placement",
            "placements",
            "recruitment",
            "company",
            "companies"
        ],

        "leave": [
            "leave",
            "permission",
            "absence",
            "holiday"
        ]
    }

    # ============================================================
    # PDF EXTRACTION
    # ============================================================

    def extract_pdfs(self):

        chunks = []

        for path in sorted(
            DOCUMENTS_DIR.glob("*.pdf")
        ):

            try:

                reader = PdfReader(
                    str(path)
                )

                for page_no, page in enumerate(
                    reader.pages,
                    start=1
                ):

                    text = (
                        page.extract_text()
                        or ""
                    ).strip()

                    if not text:
                        continue

                    text = re.sub(
                        r"\s+",
                        " ",
                        text
                    )

                    words = text.split()

                    chunk_words = 180
                    overlap = 30

                    start = 0

                    while start < len(words):

                        part = " ".join(
                            words[
                                start:
                                start + chunk_words
                            ]
                        ).strip()

                        if part:

                            chunks.append(
                                {
                                    "text": part,
                                    "file": path.name,
                                    "page": page_no
                                }
                            )

                        if (
                            start + chunk_words
                            >= len(words)
                        ):
                            break

                        start += (
                            chunk_words
                            - overlap
                        )

            except Exception as e:

                print(
                    f"❌ Could not read "
                    f"{path.name}: {e}"
                )

        return chunks

    # ============================================================
    # BUILD INDEX
    # ============================================================

    def build(self):

        DOCUMENTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        INDEX_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "\n📚 Extracting PDF documents..."
        )

        self.chunks = self.extract_pdfs()

        if not self.chunks:

            print(
                "❌ No document chunks found."
            )

            self.index = None
            self.vectorizer = None
            self.tfidf_matrix = None

            return 0

        print(
            f"📄 Total chunks: "
            f"{len(self.chunks)}"
        )

        texts = [
            chunk["text"]
            for chunk in self.chunks
        ]

        # --------------------------------------------------------
        # Semantic embeddings
        # --------------------------------------------------------

        print(
            "🧠 Creating semantic embeddings..."
        )

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
            str(
                INDEX_DIR /
                "knowledge.faiss"
            )
        )

        # --------------------------------------------------------
        # TF-IDF
        # --------------------------------------------------------

        print(
            "🔤 Creating TF-IDF keyword index..."
        )

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )

        self.tfidf_matrix = (
            self.vectorizer.fit_transform(
                texts
            )
        )

        with open(
            INDEX_DIR /
            "tfidf_vectorizer.pkl",
            "wb"
        ) as f:

            pickle.dump(
                self.vectorizer,
                f
            )

        (
            INDEX_DIR /
            "chunks.json"
        ).write_text(
            json.dumps(
                self.chunks,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print(
            "✅ FAISS semantic index created"
        )

        print(
            "✅ TF-IDF keyword index created"
        )

        return len(self.chunks)

    # ============================================================
    # LOAD INDEX
    # ============================================================

    def load(self):

        index_file = (
            INDEX_DIR /
            "knowledge.faiss"
        )

        chunks_file = (
            INDEX_DIR /
            "chunks.json"
        )

        vectorizer_file = (
            INDEX_DIR /
            "tfidf_vectorizer.pkl"
        )

        if not (
            index_file.exists()
            and chunks_file.exists()
        ):

            print(
                "⚠️ RAG index not found."
            )

            return

        try:

            self.index = faiss.read_index(
                str(index_file)
            )

            self.chunks = json.loads(
                chunks_file.read_text(
                    encoding="utf-8"
                )
            )

            if vectorizer_file.exists():

                with open(
                    vectorizer_file,
                    "rb"
                ) as f:

                    self.vectorizer = (
                        pickle.load(f)
                    )

            else:

                self.vectorizer = (
                    TfidfVectorizer(
                        lowercase=True,
                        stop_words="english",
                        ngram_range=(1, 2),
                        sublinear_tf=True
                    )
                )

                texts = [
                    chunk["text"]
                    for chunk in self.chunks
                ]

                self.vectorizer.fit(
                    texts
                )

            texts = [
                chunk["text"]
                for chunk in self.chunks
            ]

            self.tfidf_matrix = (
                self.vectorizer.transform(
                    texts
                )
            )

            print(
                "✅ Hybrid RAG index loaded"
            )

            print(
                f"📄 Loaded chunks: "
                f"{len(self.chunks)}"
            )

        except Exception as e:

            print(
                f"⚠️ Could not load RAG index: {e}"
            )

            self.index = None
            self.chunks = []
            self.vectorizer = None
            self.tfidf_matrix = None

    # ============================================================
    # DOCUMENT TOPIC RELEVANCE
    # ============================================================

    def document_topic_score(
        self,
        question: str,
        filename: str
    ):

        question_lower = (
            self.normalize_text(question)
        )

        filename_lower = filename.lower()

        topic_keywords = {

            "placement_guidelines.pdf": [
                "placement",
                "placements",
                "campus placement",
                "company",
                "companies",
                "arrear",
                "arrears",
                "cgpa",
                "job",
                "drive",
                "recruitment",
                "offer",
                "eligibility",
                "eligible"
            ],

            "attendance_rules.pdf": [
                "attendance",
                "attendance percentage",
                "minimum attendance",
                "absent",
                "absence",
                "condonation",
                "od",
                "attendance shortage"
            ],

            "exam_regulations.pdf": [
                "exam",
                "exams",
                "examination",
                "examinations",
                "semester exam",
                "semester exams",
                "end semester",
                "end-semester",
                "end semester exam",
                "end-semester exam",
                "eligibility to write",
                "eligibility",
                "supplementary",
                "arrear exam",
                "hall ticket",
                "question paper",
                "examination rules"
            ],

            "hostel_rules.pdf": [
                "hostel",
                "hostels",
                "warden",
                "hostel admission",
                "room",
                "mess",
                "hostel timing",
                "hostel fee",
                "hostel rules",
                "residence",
                "visitor"
            ],

            "leave_policy.pdf": [
                "leave",
                "medical leave",
                "casual leave",
                "permission",
                "leave application",
                "absence permission",
                "leave policy"
            ],

            "college_regulations.pdf": [
                "college rules",
                "college regulations",
                "campus rules",
                "dress code",
                "campus timing",
                "discipline",
                "general regulations",
                "college policy"
            ],

            "department_handbook.pdf": [
                "department",
                "department handbook",
                "cse department",
                "department rules",
                "academic activities",
                "department activities",
                "faculty",
                "laboratory"
            ]
        }

        keywords = topic_keywords.get(
            filename_lower,
            []
        )

        if not keywords:
            return 0.0

        matched_phrases = 0

        for keyword in keywords:

            if keyword in question_lower:

                if " " in keyword:
                    matched_phrases += 2
                else:
                    matched_phrases += 1

        if matched_phrases == 0:
            return 0.0

        if matched_phrases >= 2:
            return 1.0

        return 0.70

    # ============================================================
    # ALIAS MATCH
    # ============================================================

    def alias_match_score(
        self,
        question: str,
        text: str
    ):

        question_tokens = self.tokenize(
            question
        )

        text_tokens = self.tokenize(
            text
        )

        if not question_tokens:
            return 0.0

        matched = 0

        for query_word in question_tokens:

            aliases = self.TERM_ALIASES.get(
                query_word,
                [query_word]
            )

            found = False

            for alias in aliases:

                if alias in text_tokens:

                    found = True
                    break

            if found:
                matched += 1

        return (
            matched /
            len(question_tokens)
        )

    # ============================================================
    # EXACT PHRASE MATCH
    # ============================================================

    def exact_phrase_score(
        self,
        question: str,
        text: str
    ):

        question_normalized = (
            self.normalize_text(question)
        )

        text_normalized = (
            self.normalize_text(text)
        )

        if not question_normalized:
            return 0.0

        # --------------------------------------------------------
        # Full question phrase
        # --------------------------------------------------------

        if question_normalized in text_normalized:

            return 1.0

        # --------------------------------------------------------
        # Important phrases
        # --------------------------------------------------------

        important_phrases = [

            "eligibility to write",
            "end semester exams",
            "end-semester exams",
            "end semester examinations",
            "end-semester examinations",
            "hostel rules",
            "attendance rules",
            "college rules",
            "college regulations",
            "placement guidelines",
            "leave policy"
        ]

        matched = 0

        for phrase in important_phrases:

            if phrase in question_normalized:

                aliases = [
                    phrase,
                    phrase.replace(
                        "exams",
                        "examinations"
                    ),
                    phrase.replace(
                        "examinations",
                        "exams"
                    )
                ]

                for alias in aliases:

                    if alias in text_normalized:

                        matched = 1
                        break

        return float(matched)

    # ============================================================
    # KEYWORD / LEXICAL RELEVANCE
    # ============================================================

    def keyword_relevance(
        self,
        question: str,
        text: str,
        filename: str
    ):

        question_tokens = self.tokenize(
            question
        )

        text_tokens = self.tokenize(
            text
        )

        if not question_tokens:
            return 0.0

        # --------------------------------------------------------
        # Exact token overlap
        # --------------------------------------------------------

        exact_matches = (
            question_tokens
            &
            text_tokens
        )

        exact_score = (
            len(exact_matches)
            /
            len(question_tokens)
        )

        # --------------------------------------------------------
        # Word-family matching
        # --------------------------------------------------------

        family_matches = 0

        for query_word in question_tokens:

            if query_word in exact_matches:
                continue

            for text_word in text_tokens:

                if (
                    len(query_word) >= 4
                    and
                    len(text_word) >= 4
                    and
                    (
                        text_word.startswith(
                            query_word
                        )
                        or
                        query_word.startswith(
                            text_word
                        )
                    )
                ):

                    family_matches += 1
                    break

        family_score = (
            family_matches
            /
            len(question_tokens)
        )

        # --------------------------------------------------------
        # Alias score
        # --------------------------------------------------------

        alias_score = (
            self.alias_match_score(
                question,
                text
            )
        )

        # --------------------------------------------------------
        # Filename relevance
        # --------------------------------------------------------

        filename_tokens = self.tokenize(
            filename
            .replace("_", " ")
            .replace(".pdf", "")
        )

        filename_matches = (
            question_tokens
            &
            filename_tokens
        )

        filename_score = (
            len(filename_matches)
            /
            len(question_tokens)
        )

        # --------------------------------------------------------
        # Final lexical score
        # --------------------------------------------------------

        score = (
            0.40 * exact_score
            +
            0.25 * family_score
            +
            0.25 * alias_score
            +
            0.10 * filename_score
        )

        return min(
            float(score),
            1.0
        )

    # ============================================================
    # SEARCH
    # ============================================================

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

        # ========================================================
        # SEMANTIC SEARCH
        # ========================================================

        q_embedding = self.model.encode(
            [question],
            normalize_embeddings=True
        )

        q_embedding = np.asarray(
            q_embedding,
            dtype="float32"
        )

        semantic_scores, semantic_ids = (
            self.index.search(
                q_embedding,
                len(self.chunks)
            )
        )

        semantic_scores = semantic_scores[0]

        # ========================================================
        # TF-IDF SEARCH
        # ========================================================

        if (
            self.vectorizer is not None
            and
            self.tfidf_matrix is not None
        ):

            query_tfidf = (
                self.vectorizer.transform(
                    [question]
                )
            )

            keyword_scores = (
                self.tfidf_matrix
                @ query_tfidf.T
            ).toarray().flatten()

        else:

            keyword_scores = np.zeros(
                len(self.chunks),
                dtype="float32"
            )

        # ========================================================
        # RERANK
        # ========================================================

        reranked = []

        for idx in range(
            len(self.chunks)
        ):

            chunk = self.chunks[idx]

            # ----------------------------------------------------
            # Semantic
            # ----------------------------------------------------

            semantic_score = float(
                semantic_scores[idx]
            )

            semantic_score = max(
                0.0,
                min(
                    semantic_score,
                    1.0
                )
            )

            # ----------------------------------------------------
            # TF-IDF
            # ----------------------------------------------------

            keyword_score = float(
                keyword_scores[idx]
            )

            keyword_score = max(
                0.0,
                min(
                    keyword_score,
                    1.0
                )
            )

            # ----------------------------------------------------
            # Lexical
            # ----------------------------------------------------

            lexical_score = (
                self.keyword_relevance(
                    question,
                    chunk["text"],
                    chunk["file"]
                )
            )

            # ----------------------------------------------------
            # Exact phrase
            # ----------------------------------------------------

            phrase_score = (
                self.exact_phrase_score(
                    question,
                    chunk["text"]
                )
            )

            # ----------------------------------------------------
            # Topic
            # ----------------------------------------------------

            topic_score = (
                self.document_topic_score(
                    question,
                    chunk["file"]
                )
            )

            # ====================================================
            # FINAL SCORE
            # ====================================================

            final_score = (

                0.25 * semantic_score

                +

                0.20 * keyword_score

                +

                0.15 * lexical_score

                +

                0.20 * topic_score

                +

                0.20 * phrase_score
            )

            # ----------------------------------------------------
            # Strong exact phrase boost
            # ----------------------------------------------------

            if phrase_score >= 1.0:

                final_score += 0.15

            # ----------------------------------------------------
            # Strong topic boost
            # ----------------------------------------------------

            if topic_score >= 1.0:

                final_score += 0.10

            final_score = min(
                final_score,
                1.0
            )

            item = dict(chunk)

            item["score"] = float(
                final_score
            )

            item["semantic_score"] = float(
                semantic_score
            )

            item["keyword_score"] = float(
                keyword_score
            )

            item["lexical_score"] = float(
                lexical_score
            )

            item["topic_score"] = float(
                topic_score
            )

            item["phrase_score"] = float(
                phrase_score
            )

            reranked.append(
                item
            )

        # ========================================================
        # SORT
        # ========================================================

        reranked.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # ========================================================
        # REMOVE DUPLICATES
        # ========================================================

        final_results = []

        seen = set()

        for item in reranked:

            key = (
                item["file"],
                item["page"],
                item["text"][:100]
            )

            if key in seen:
                continue

            seen.add(key)

            final_results.append(
                item
            )

            if len(final_results) >= k:
                break

        # ========================================================
        # BEST SCORE
        # ========================================================

        best_score = (
            final_results[0]["score"]
            if final_results
            else 0.0
        )

        # ========================================================
        # GROUNDING
        # ========================================================

        if final_results:

            top_result = final_results[0]

            strong_phrase_match = (
                top_result["phrase_score"] >= 1.0
            )

            strong_topic_match = (
                top_result["topic_score"] >= 0.70
            )

            reasonable_semantic = (
                top_result["semantic_score"] >= 0.25
            )

            reasonable_keyword = (
                top_result["keyword_score"] >= 0.05
            )

            reasonable_lexical = (
                top_result["lexical_score"] >= 0.20
            )

            grounded = (

                best_score >= RELEVANCE_THRESHOLD

                or

                strong_phrase_match

                or

                (
                    strong_topic_match
                    and
                    (
                        reasonable_semantic
                        or
                        reasonable_keyword
                        or
                        reasonable_lexical
                    )
                )
            )

        else:

            grounded = False

        return (
            final_results,
            best_score,
            grounded
        )

    # ============================================================
    # SEARCH BY DOCUMENT
    # ============================================================

    def search_by_document(
        self,
        filename: str,
        k: int = 10
    ):

        if not self.chunks:
            return []

        matching = []

        filename_lower = filename.lower()

        for index, item in enumerate(
            self.chunks
        ):

            item_filename = (
                item.get("file", "")
                .lower()
            )

            if item_filename != filename_lower:
                continue

            result = dict(item)

            result["score"] = 1.0
            result["semantic_score"] = 1.0
            result["keyword_score"] = 1.0
            result["lexical_score"] = 1.0
            result["topic_score"] = 1.0

            result["_chunk_index"] = index

            matching.append(
                result
            )

        matching.sort(
            key=lambda item: (
                item.get("page", 0),
                item.get("_chunk_index", 0)
            )
        )

        for item in matching:

            item.pop(
                "_chunk_index",
                None
            )

        return matching[:k]

    # ============================================================
    # SEARCH MULTIPLE DOCUMENTS
    # ============================================================

    def search_multiple_documents(
        self,
        filenames,
        k_per_document=10
    ):

        if not filenames:
            return []

        all_results = []

        for filename in filenames:

            document_results = (
                self.search_by_document(
                    filename,
                    k=k_per_document
                )
            )

            all_results.extend(
                document_results
            )

        final_results = []

        seen = set()

        for item in all_results:

            key = (
                item.get("file"),
                item.get("page"),
                item.get("text", "")[:100]
            )

            if key in seen:
                continue

            seen.add(key)

            final_results.append(
                item
            )

        final_results.sort(
            key=lambda item: (
                item.get("file", ""),
                item.get("page", 0)
            )
        )

        return final_results