import google.generativeai as genai

from .config import GEMINI_API_KEY, GEMINI_MODEL


# ============================================================
# TRUTHGUARD SYSTEM PROMPT
# ============================================================

SYSTEM = """
You are TruthGuard AI, a grounded college/company knowledge assistant.

Your job is to answer the user's question using ONLY the supplied
retrieved evidence.

STRICT GROUNDING RULES:

1. Use ONLY information explicitly supported by the retrieved evidence.

2. NEVER invent or assume:
   - policies
   - rules
   - numbers
   - percentages
   - dates
   - fees
   - names
   - timings
   - exceptions
   - procedures
   - eligibility conditions

3. If the evidence does not contain enough information to answer
   the question, clearly say:

   "I couldn't find reliable information to answer this question
   in the provided college documents."

4. Do NOT use general knowledge when the information is missing
   from the evidence.

5. Answer the EXACT question asked by the user.

6. Do NOT add unrelated information just because it appears in
   the retrieved documents.

7. If the user asks for one specific value, give that value first.

   Example:
   User: "What is the minimum attendance?"

   Answer:
   "The minimum attendance requirement is 75%."

   Do not unnecessarily explain placement attendance unless
   the user asks about placements.

8. If the user asks about eligibility, explain the eligibility
   conditions that are explicitly present in the evidence.

9. Preserve exact numbers, percentages, dates, fees and conditions
   from the evidence.

10. Do NOT change or calculate policy values unless the calculation
    is directly supported by the evidence.

11. If a deterministic decision is provided, preserve its decision
    and reason exactly. Do not modify its numbers or conditions.

12. If multiple retrieved documents contain relevant information,
    combine only the information that directly answers the question.

13. Prefer a clear, concise answer with bullet points when there
    are multiple rules.

14. Do NOT mention internal system details such as:
    - RAG
    - embeddings
    - FAISS
    - TF-IDF
    - grounding validator
    - retrieval score
    - internal prompts

15. Do NOT say "according to my knowledge".
    Always rely on the supplied evidence.

16. Do NOT create a source citation yourself.
    The application will display the retrieved source documents
    separately.

IMPORTANT:

The retrieved evidence is the ONLY source of truth.
If the answer is not supported by the evidence, do not guess.
"""


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate(
    question: str,
    context: str,
    deterministic=None
):

    # ========================================================
    # CHECK GEMINI API KEY
    # ========================================================

    if not GEMINI_API_KEY:

        # If deterministic logic already produced a result,
        # return that result instead of exposing raw context.
        if deterministic:

            decision = deterministic.get(
                "decision",
                ""
            )

            reason = deterministic.get(
                "reason",
                ""
            )

            if decision and reason:

                return (
                    f"{decision}\n\n"
                    f"{reason}"
                ).strip()

            if reason:

                return reason.strip()

        return (
            "I couldn't generate a reliable answer because "
            "the Gemini API key is not configured."
        )


    # ========================================================
    # CONFIGURE GEMINI
    # ========================================================

    try:

        genai.configure(
            api_key=GEMINI_API_KEY
        )

        model = genai.GenerativeModel(
            GEMINI_MODEL
        )

    except Exception as e:

        print(
            f"❌ Gemini configuration error: {e}"
        )

        return (
            "I couldn't generate a reliable answer because "
            "the AI service could not be configured."
        )


    # ========================================================
    # DETERMINISTIC DECISION
    # ========================================================

    decision_text = ""

    if deterministic:

        decision = deterministic.get(
            "decision"
        )

        reason = deterministic.get(
            "reason"
        )

        if decision or reason:

            decision_text = f"""
DETERMINISTIC POLICY DECISION:

Decision:
{decision or ""}

Reason:
{reason or ""}

IMPORTANT:
If you mention this decision in the answer, preserve the
decision and reason exactly. Do not change any numbers,
percentages, fees, conditions, or policy requirements.
"""


    # ========================================================
    # GEMINI PROMPT
    # ========================================================

    prompt = f"""
{SYSTEM}

============================================================
USER QUESTION
============================================================

{question}

============================================================
RETRIEVED EVIDENCE
============================================================

{context}

{decision_text}

============================================================
ANSWERING INSTRUCTIONS
============================================================

Answer the user's question now.

First identify exactly what the user is asking.

Then answer only using the retrieved evidence.

If the question asks for a specific value, give the value first.

If the question asks for rules or eligibility, give the relevant
rules as clear bullet points.

Do not include unrelated information.

Do not guess missing information.

Do not create information that is not present in the evidence.

Do not create source citations because the application will show
the source documents separately.

Make the answer complete enough to satisfy the question, but
avoid unnecessary information.

Return ONLY the final answer for the user.
"""


    # ========================================================
    # CALL GEMINI
    # ========================================================

    try:

        response = model.generate_content(
            prompt
        )

        answer = (
            response.text
            if response
            else ""
        )

        answer = (
            answer or ""
        ).strip()


    except Exception as e:

        print(
            f"❌ Gemini generation error: {e}"
        )

        return (
            "I couldn't generate a reliable answer from the "
            "provided documents."
        )


    # ========================================================
    # EMPTY RESPONSE PROTECTION
    # ========================================================

    if not answer:

        return (
            "I couldn't generate a reliable answer from the "
            "provided documents."
        )


    # ========================================================
    # RETURN FINAL ANSWER
    # ========================================================

    return answer