from .rag import RAGEngine
from .grounding import check_grounding
from .rule_engine import check_policy_rule
from .answer_generator import AnswerGenerator
from .groq_generator import GroqAnswerGenerator
from .output_validator import validate_answer
from .citation import build_citations
from .question_analyzer import analyze_question
from .document_expansion import DocumentExpansion
from .completeness import check_completeness


class TruthGuardPipeline:

    def __init__(self):

        print("🔄 Loading TruthGuard Pipeline...")

        # ==================================================
        # LOAD RAG
        # ==================================================

        self.rag = RAGEngine()

        print("✅ RAG loaded")
        print("✅ Grounding validator loaded")
        print("✅ Rule engine loaded")

        # ==================================================
        # LOAD DOCUMENT EXPANSION
        # ==================================================

        self.document_expansion = DocumentExpansion()

        print("✅ Document expansion loaded")

        # ==================================================
        # LOAD DETERMINISTIC ANSWER GENERATOR
        # ==================================================

        self.answer_generator = AnswerGenerator()

        print("✅ Deterministic answer generator loaded")

        # ==================================================
        # LOAD GROQ GENERATOR
        # ==================================================

        self.groq_generator = GroqAnswerGenerator()

        print("✅ Groq answer generator loaded")

    # ======================================================
    # BROAD QUESTION DETECTION
    # ======================================================

    def is_broad_question(
        self,
        question: str
    ) -> bool:

        question_lower = (
            question
            .lower()
            .strip()
        )

        broad_patterns = [

            "what are the rules",
            "what is the college rules",
            "what are the college rules",
            "college rules",
            "college regulations",

            "what are the hostel rules",

            "tell me the rules",
            "list the rules",

            "what are the regulations",
            "tell me about the regulations",

            "what are the policies",
            "tell me about the policies",

            "what are the guidelines",
            "tell me the guidelines",

            "what does the document say",

            "summarize the rules",
            "summarize the policy",
            "summarize the regulations",

            "what are all the rules",
            "what are all the regulations",
            "what are all the policies",

            "what are the requirements",
            "what are the procedures",
        ]

        for pattern in broad_patterns:

            if pattern in question_lower:
                return True

        return False

    # ======================================================
    # REMOVE DUPLICATE RETRIEVED CHUNKS
    # ======================================================

    def deduplicate_results(
        self,
        results
    ):

        unique_results = []
        seen = set()

        for item in results:

            key = (
                item.get("file"),
                item.get("page"),
                item.get("text", "")[:150]
            )

            if key in seen:
                continue

            seen.add(key)
            unique_results.append(item)

        return unique_results

    # ======================================================
    # BUILD EVIDENCE
    # ======================================================

    def build_evidence(
        self,
        results
    ):

        evidence_parts = []

        for item in results:

            evidence_parts.append(
                f"Source: {item['file']} | "
                f"Page: {item['page']}\n"
                f"{item['text']}"
            )

        return "\n\n".join(
            evidence_parts
        )

    # ======================================================
    # DEBUG EVIDENCE
    # ======================================================

    def print_evidence(
        self,
        results
    ):

        print(
            "\n" + "=" * 70
        )

        print(
            "📚 EVIDENCE SENT TO GROQ"
        )

        print(
            "=" * 70
        )

        for i, item in enumerate(
            results,
            1
        ):

            print(
                f"\n--- RESULT {i} ---"
            )

            print(
                f"File: {item.get('file')}"
            )

            print(
                f"Page: {item.get('page')}"
            )

            print(
                f"Score: {item.get('score')}"
            )

            print(
                "Text:"
            )

            print(
                item.get('text')
            )

        print(
            "\n" + "=" * 70
        )

    # ======================================================
    # DOCUMENT EXPANSION
    # ======================================================

    def expand_documents(
        self,
        question_analysis
    ):

        topics = question_analysis.get(
            "topics",
            []
        )

        if not topics:
            return []

        documents = (
            self.document_expansion
            .get_documents_for_topics(
                topics
            )
        )

        return documents

    # ======================================================
    # RETRIEVE EVIDENCE
    # ======================================================

    def retrieve_evidence(
        self,
        question,
        question_analysis
    ):

        broad_question = (
            question_analysis.get(
                "broad",
                False
            )
        )

        topics = (
            question_analysis.get(
                "topics",
                []
            )
        )

        multi_topic = (
            question_analysis.get(
                "multi_topic",
                False
            )
        )

        # ==================================================
        # CASE 0:
        # GENERAL COLLEGE-WIDE QUESTION
        # ==================================================

        if broad_question and not topics:

            print(
                "\n📚 General college-wide question detected."
            )

            documents = (
                self.document_expansion
                .get_all_documents()
            )

            print(
                f"📄 Expanded documents: {documents}"
            )

            results = (
                self.rag
                .search_multiple_documents(
                    documents,
                    k_per_document=10
                )
            )

            results = self.deduplicate_results(
                results
            )

            if results:

                return (
                    results,
                    1.0,
                    True
                )

        # ==================================================
        # CASE 1:
        # BROAD MULTI-TOPIC QUESTION
        # ==================================================

        if broad_question and multi_topic:

            print(
                "\n📚 Broad multi-topic question detected."
            )

            print(
                f"🧠 Detected topics: {topics}"
            )

            documents = (
                self.expand_documents(
                    question_analysis
                )
            )

            print(
                f"📄 Expanded documents: {documents}"
            )

            if documents:

                results = (
                    self.rag
                    .search_multiple_documents(
                        documents,
                        k_per_document=10
                    )
                )

                results = (
                    self.deduplicate_results(
                        results
                    )
                )

                if results:

                    best_score = max(
                        item.get(
                            "score",
                            0.0
                        )
                        for item in results
                    )

                    return (
                        results,
                        best_score,
                        True
                    )

        # ==================================================
        # CASE 2:
        # BROAD SINGLE-TOPIC QUESTION
        # ==================================================

        if broad_question and topics:

            print(
                "\n📚 Broad single-topic question detected."
            )

            print(
                f"🧠 Detected topic: {topics}"
            )

            documents = (
                self.expand_documents(
                    question_analysis
                )
            )

            print(
                f"📄 Expanded documents: {documents}"
            )

            if documents:

                all_results = []

                for document in documents:

                    document_results = (
                        self.rag.search_by_document(
                            document,
                            k=10
                        )
                    )

                    all_results.extend(
                        document_results
                    )

                all_results = (
                    self.deduplicate_results(
                        all_results
                    )
                )

                if all_results:

                    return (
                        all_results,
                        1.0,
                        True
                    )

        # ==================================================
        # CASE 3:
        # NORMAL SPECIFIC QUESTION
        # ==================================================

        print(
            "\n🎯 Using normal hybrid RAG retrieval..."
        )

        results, best_score, grounded = (
            self.rag.search(
                question,
                k=6
            )
        )

        results = (
            self.deduplicate_results(
                results
            )
        )

        return (
            results,
            best_score,
            grounded
        )

    # ======================================================
    # MAIN QUESTION HANDLER
    # ======================================================

    def ask(
        self,
        question: str
    ):

        print(
            "\n" + "=" * 60
        )

        print(
            "QUESTION:"
        )

        print(
            question
        )

        print(
            "=" * 60
        )

        # ==================================================
        # STEP 1:
        # QUESTION ANALYSIS
        # ==================================================

        question_analysis = (
            analyze_question(
                question
            )
        )

        broad_question = (
            question_analysis.get(
                "broad",
                False
            )
        )

        topics = (
            question_analysis.get(
                "topics",
                []
            )
        )

        multi_topic = (
            question_analysis.get(
                "multi_topic",
                False
            )
        )

        print(
            "\n🧠 Question Analysis:"
        )

        print(
            question_analysis
        )

        print(
            "\n🧠 Question Type:"
        )

        if broad_question and multi_topic:

            print(
                "📚 BROAD MULTI-TOPIC DOCUMENT QUESTION"
            )

        elif broad_question:

            print(
                "📚 BROAD DOCUMENT QUESTION"
            )

        else:

            print(
                "🎯 SPECIFIC DOCUMENT QUESTION"
            )

        # ==================================================
        # STEP 2:
        # RETRIEVE EVIDENCE
        # ==================================================

        (
            results,
            best_score,
            grounded_by_retrieval
        ) = self.retrieve_evidence(
            question,
            question_analysis
        )

        # ==================================================
        # STEP 3:
        # NO RESULTS
        # ==================================================

        if not results:

            print(
                "\n🛑 No relevant evidence found"
            )

            return {

                "success": False,

                "answer": (
                    "I couldn't find relevant information "
                    "in the provided documents. "
                    "I don't want to guess."
                ),

                "sources": [],
                "citations": [],
                "grounded": False,
                "grounding": None,
                "output_grounding": None,
                "completeness": None,
                "rule_result": None,
                "retrieval_score": 0.0,
                "retrieval_grounded": False
            }

        # ==================================================
        # STEP 4:
        # BUILD EVIDENCE
        # ==================================================

        evidence = (
            self.build_evidence(
                results
            )
        )

        # ==================================================
        # STEP 5:
        # DEBUG EVIDENCE
        # ==================================================

        self.print_evidence(
            results
        )

        # ==================================================
        # STEP 6:
        # INPUT GROUNDING
        # ==================================================

        grounding = check_grounding(
            question,
            evidence
        )

        print(
            "\n🔍 Grounding Check:"
        )

        print(
            grounding
        )

        # ==================================================
        # STEP 7:
        # BUILD SOURCES
        # ==================================================

        sources = [

            {
                "file": item["file"],
                "page": item["page"],
                "score": item.get(
                    "score",
                    0.0
                )
            }

            for item in results[:10]
        ]

        # ==================================================
        # STEP 8:
        # BUILD CITATIONS
        # ==================================================

        citations = build_citations(
            sources
        )

        # ==================================================
        # STEP 9:
        # QUESTION GROUNDING FAILURE
        # ==================================================

        if not grounding["supported"]:

            print(
                "\n🛑 Question rejected by "
                "Grounding Validator"
            )

            answer = (
                "I couldn't find reliable information "
                "to answer this question in the "
                "provided college documents. "
                "I don't want to guess."
            )

            return {

                "success": True,

                "answer": answer,

                "sources": [],
                "citations": [],
                "grounded": False,

                "grounding": grounding,

                "output_grounding": None,

                "completeness": None,

                "rule_result": None,

                "retrieval_score": best_score,

                "retrieval_grounded":
                    grounded_by_retrieval
            }

        # ==================================================
        # STEP 10:
        # RULE ENGINE
        # ==================================================

        rule_result = check_policy_rule(
            question,
            evidence
        )

        print(
            "\n⚙️ Rule Engine:"
        )

        print(
            rule_result
        )

        # ==================================================
        # STEP 11:
        # DEFAULT VALUES
        # ==================================================

        output_grounding = None
        completeness = None

        # ==================================================
        # STEP 12:
        # ANSWER GENERATION
        # ==================================================

        # ==================================================
        # CASE 1:
        # DETERMINISTIC RULE
        # ==================================================

        if rule_result.get(
            "rule_found",
            False
        ):

            print(
                "\n🧮 Using Deterministic Rule Engine"
            )

            answer = (
                self.answer_generator.generate(

                    question=question,

                    rule_result=rule_result,

                    evidence=evidence,

                    sources=sources,

                    grounded=True
                )
            )

        # ==================================================
        # CASE 2:
        # GENERAL DOCUMENT QUESTION
        # ==================================================

        else:

            print(
                "\n🤖 Using Groq Evidence-Based Generator"
            )

            groq_result = (
                self.groq_generator.generate(

                    question=question,

                    evidence=evidence,

                    sources=sources
                )
            )

            # ----------------------------------------------
            # GROQ FAILURE
            # ----------------------------------------------

            if not groq_result["success"]:

                print(
                    "\n🛑 Groq could not generate "
                    "a reliable answer"
                )

                return {

                    "success": False,

                    "answer": (
                        "I couldn't generate a reliable "
                        "answer from the provided college "
                        "documents. I don't want to guess."
                    ),

                    "sources": [],
                    "citations": [],

                    "grounded": False,

                    "grounding": grounding,

                    "output_grounding": None,

                    "completeness": None,

                    "rule_result": rule_result,

                    "retrieval_score": best_score,

                    "retrieval_grounded":
                        grounded_by_retrieval,

                    "generation_error":
                        groq_result["reason"]
                }

            # ----------------------------------------------
            # GROQ ANSWER
            # ----------------------------------------------

            answer = (
                groq_result["answer"]
            )

            print(
                "\n🤖 GROQ RAW ANSWER:"
            )

            print(
                answer
            )

            # ----------------------------------------------
            # OUTPUT GROUNDING
            # ----------------------------------------------

            output_grounding = (
                validate_answer(

                    question=question,

                    answer=answer,

                    evidence=evidence
                )
            )

            print(
                "\n🛡️ Output Grounding Check:"
            )

            print(
                output_grounding
            )

            # ----------------------------------------------
            # COMPLETENESS CHECK
            # ----------------------------------------------

            completeness = (
                check_completeness(

                    question=question,

                    answer=answer,

                    evidence=evidence
                )
            )

            print(
                "\n📋 Completeness Check:"
            )

            print(
                completeness
            )

            # ----------------------------------------------
            # REJECT UNSUPPORTED ANSWER
            # ----------------------------------------------

            if not output_grounding[
                "supported"
            ]:

                print(
                    "\n🛑 Groq answer rejected by "
                    "Output Grounding Validator"
                )

                return {

                    "success": False,

                    "answer": (
                        "I couldn't generate a reliable "
                        "answer from the provided college "
                        "documents. I don't want to guess."
                    ),

                    "sources": [],
                    "citations": [],

                    "grounded": False,

                    "grounding": grounding,

                    "output_grounding":
                        output_grounding,

                    "completeness":
                        completeness,

                    "rule_result":
                        rule_result,

                    "retrieval_score":
                        best_score,

                    "retrieval_grounded":
                        grounded_by_retrieval
                }

        # ==================================================
        # STEP 13:
        # COMPLETENESS FOR DETERMINISTIC ANSWERS
        # ==================================================

        if completeness is None:

            completeness = (
                check_completeness(

                    question=question,

                    answer=answer,

                    evidence=evidence
                )
            )

            print(
                "\n📋 Completeness Check:"
            )

            print(
                completeness
            )

        # ==================================================
        # STEP 14:
        # FINAL RESPONSE
        # ==================================================

        print(
            "\n✅ Answer generated"
        )

        return {

            "success": True,

            "answer": answer,

            "sources": sources,

            "citations": citations,

            "grounded": True,

            "grounding": grounding,

            "output_grounding":
                output_grounding,

            "completeness":
                completeness,

            "rule_result":
                rule_result,

            "retrieval_score":
                best_score,

            "retrieval_grounded":
                grounded_by_retrieval,

            "question_analysis":
                question_analysis
        }