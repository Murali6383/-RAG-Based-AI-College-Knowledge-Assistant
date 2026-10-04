import time

from groq import Groq

from .config import GROQ_API_KEY, GROQ_MODEL


class GroqAnswerGenerator:

    def __init__(self):

        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is missing in .env"
            )

        self.client = Groq(
            api_key=GROQ_API_KEY
        )

        self.model = GROQ_MODEL

        print(
            f"✅ Groq loaded: {self.model}"
        )

    # ======================================================
    # MAIN GENERATION FUNCTION
    # ======================================================

    def generate(
        self,
        question: str,
        evidence: str,
        sources: list
    ):

        source_text = self.format_sources(
            sources
        )

        # ==================================================
        # SYSTEM INSTRUCTION
        # ==================================================

        system_instruction = """
You are TruthGuard AI, a college document
question-answering assistant.

Your job is to answer questions using ONLY
the evidence provided from official college
documents.

STRICT RULES:

1. Use ONLY the supplied evidence.

2. Never use outside knowledge.

3. Never guess.

4. Never invent information.

5. Answer the user's question directly.

6. If multiple rules are present, include ALL
   important rules supported by the evidence.

7. Do not stop after the first rule when
   additional relevant information is present.

8. Preserve important numbers, percentages,
   timings, fees, penalties and conditions
   exactly as written.

9. Do not calculate attendance, CGPA,
   arrears or eligibility decisions.
   Those are handled by the deterministic
   rule engine.

10. Do not mention the retrieval system.

11. Do not mention Groq.

12. Do not mention the evidence processing.

13. Do not include citations inside the answer.

14. Keep the answer clear and reasonably concise.

15. If the supplied evidence does not contain
    enough information to answer the question,
    return exactly:

NOT_FOUND
"""

        # ==================================================
        # USER PROMPT
        # ==================================================

        prompt = f"""
QUESTION:
{question}

EVIDENCE FROM COLLEGE DOCUMENTS:
{evidence}

AVAILABLE SOURCES:
{source_text}

TASK:

Answer the QUESTION using ONLY the
EVIDENCE FROM COLLEGE DOCUMENTS.

If the question asks for rules, policies,
guidelines, requirements, restrictions,
fees, timings, penalties or procedures,
include all important information supported
by the evidence.

Do NOT stop after the first rule.

Do NOT use outside knowledge.

Do NOT guess.

Do NOT invent information.

Preserve all important numbers,
percentages, fees, timings and conditions.

If the evidence does not answer the question,
return exactly:

NOT_FOUND

Return only the final answer.
"""

        # ==================================================
        # RETRY CONFIG
        # ==================================================

        max_attempts = 3

        retry_delays = [
            1,
            2
        ]

        # ==================================================
        # GENERATE
        # ==================================================

        for attempt in range(
            1,
            max_attempts + 1
        ):

            try:

                print(
                    f"🤖 Groq attempt "
                    f"{attempt}/{max_attempts}"
                )

                response = (
                    self.client.chat.completions.create(

                        model=self.model,

                        messages=[
                            {
                                "role": "system",
                                "content":
                                    system_instruction
                            },
                            {
                                "role": "user",
                                "content":
                                    prompt
                            }
                        ],

                        temperature=0.0,

                        max_completion_tokens=3000,

                        stream=False
                    )
                )

                # ==================================================
                # EXTRACT TEXT
                # ==================================================

                answer = ""

                try:

                    if response.choices:

                        answer = (
                            response
                            .choices[0]
                            .message
                            .content
                            or ""
                        )

                        answer = answer.strip()

                except Exception as extraction_error:

                    print(
                        "⚠️ Groq response extraction failed:"
                    )

                    print(
                        extraction_error
                    )

                # ==================================================
                # EMPTY RESPONSE
                # ==================================================

                if not answer:

                    print(
                        "⚠️ Groq returned empty text."
                    )

                    if attempt < max_attempts:

                        delay = (
                            retry_delays[
                                attempt - 1
                            ]
                        )

                        print(
                            f"⏳ Retrying in "
                            f"{delay} second(s)..."
                        )

                        time.sleep(
                            delay
                        )

                        continue

                    return {
                        "success": False,
                        "answer": "",
                        "reason": (
                            "Groq returned an "
                            "empty response."
                        )
                    }

                # ==================================================
                # NOT FOUND
                # ==================================================

                if (
                    answer
                    .upper()
                    .strip()
                    == "NOT_FOUND"
                ):

                    print(
                        "⚠️ Groq could not find "
                        "the answer in evidence."
                    )

                    return {
                        "success": False,
                        "answer": "",
                        "reason": (
                            "Answer not found "
                            "in evidence"
                        )
                    }

                # ==================================================
                # SUCCESS
                # ==================================================

                print(
                    "\n✅ Groq answer generated"
                )

                return {
                    "success": True,
                    "answer": answer,
                    "reason": None
                }

            except Exception as e:

                error_message = str(e)

                print(
                    f"\n❌ Groq attempt "
                    f"{attempt} failed:"
                )

                print(
                    error_message
                )

                temporary_error = (
                    "429" in error_message
                    or
                    "500" in error_message
                    or
                    "502" in error_message
                    or
                    "503" in error_message
                    or
                    "504" in error_message
                    or
                    "rate limit"
                    in error_message.lower()
                    or
                    "timeout"
                    in error_message.lower()
                )

                if (
                    temporary_error
                    and
                    attempt < max_attempts
                ):

                    delay = (
                        retry_delays[
                            attempt - 1
                        ]
                    )

                    print(
                        "⏳ Groq temporarily "
                        "unavailable."
                    )

                    print(
                        f"🔁 Retrying in "
                        f"{delay} second(s)..."
                    )

                    time.sleep(
                        delay
                    )

                    continue

                return {
                    "success": False,
                    "answer": "",
                    "reason": error_message
                }

        return {
            "success": False,
            "answer": "",
            "reason": (
                "Groq generation failed"
            )
        }

    # ======================================================
    # SOURCE FORMATTER
    # ======================================================

    def format_sources(
        self,
        sources
    ):

        if not sources:

            return (
                "No source information available."
            )

        lines = []

        for source in sources:

            lines.append(
                f"- {source['file']} "
                f"(Page {source['page']})"
            )

        return "\n".join(lines)