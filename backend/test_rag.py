from app.rag import RAGEngine


rag = RAGEngine()


questions = [
    "I have 2 arrears. Can I attend campus placement?",
    "What is the minimum CGPA required for placement?",
    "I have 70% attendance. Can I write the exam?",
    "What are the hostel rules?",
    "What is the leave policy?",
    "What are the exam regulations?",
]


for question in questions:

    print("\n")
    print("=" * 70)

    print("QUESTION:")
    print(question)

    results, best_score, grounded = rag.search(
        question,
        k=5
    )

    print("\nTOP RESULTS:")

    for index, item in enumerate(
        results,
        start=1
    ):

        print(
            f"\n{index}. "
            f"{item['file']} "
            f"| Page {item['page']}"
        )

        print(
            f"Final Score: "
            f"{item['score']:.4f}"
        )

        print(
            f"Semantic: "
            f"{item['semantic_score']:.4f}"
        )

        print(
            f"Keyword: "
            f"{item['keyword_score']:.4f}"
        )

        print(
            f"Lexical: "
            f"{item['lexical_score']:.4f}"
        )

        print(
            f"Text: "
            f"{item['text'][:250]}..."
        )

    print("\nBest Score:", best_score)
    print("Grounded:", grounded)

    print("=" * 70)