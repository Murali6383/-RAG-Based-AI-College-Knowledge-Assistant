from app.pipeline import TruthGuardPipeline


pipeline = TruthGuardPipeline()


questions = [

    "I have 70% attendance. Can I write the exam?",

    "What is the minimum CGPA required for placement?",

    "My CGPA is 6.2. Can I attend campus placement?",

    "I have 2 arrears. Can I attend campus placement?",

    "What CGPA does Google require for placement?"

]


for question in questions:

    result = pipeline.ask(question)

    print("\n\n")

    print("FINAL ANSWER:")
    print(result["answer"])

    print("\nGROUNDED:")
    print(result["grounded"])

    print("\nSOURCES:")

    for source in result.get("sources", []):

        print(
            f"- {source['file']} "
            f"(Page {source['page']}) "
            f"Score: {source['score']:.4f}"
        )

    print("\nCITATIONS:")

    for citation in result.get("citations", []):

        print(
            f"📚 {citation['citation']}"
        )

    print("\n" + "=" * 70)