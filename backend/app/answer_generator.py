import re


class AnswerGenerator:

    def __init__(self):
        pass

    # ==========================================================
    # SOURCE FORMATTING
    # ==========================================================

    def format_source(self, sources):

        if not sources:
            return ""

        source_lines = []
        seen = set()

        for source in sources:

            file_name = source.get(
                "file",
                "Unknown document"
            )

            page = source.get(
                "page",
                "Unknown"
            )

            key = (file_name, page)

            if key in seen:
                continue

            seen.add(key)

            source_lines.append(
                f"📄 {file_name} — Page {page}"
            )

        return "\n".join(source_lines)

    # ==========================================================
    # ATTENDANCE
    # ==========================================================

    def attendance_answer(
        self,
        rule_result,
        sources
    ):

        student = rule_result[
            "student_attendance"
        ]

        required = rule_result[
            "required_attendance"
        ]

        if rule_result["eligible"]:

            answer = (
                f"Your attendance is {student:g}%. "
                f"The required minimum attendance is "
                f"{required:g}%. "
                f"Therefore, you are eligible to "
                f"write the examination."
            )

        else:

            answer = (
                f"Your attendance is {student:g}%. "
                f"The required minimum attendance is "
                f"{required:g}%. "
                f"Therefore, you are not eligible to "
                f"write the examination."
            )

        return self._with_sources(
            answer,
            sources
        )

    # ==========================================================
    # CGPA
    # ==========================================================

    def cgpa_answer(
        self,
        rule_result,
        sources
    ):

        student = rule_result[
            "student_cgpa"
        ]

        required = rule_result[
            "required_cgpa"
        ]

        if rule_result["eligible"]:

            answer = (
                f"Your CGPA is {student:g}. "
                f"The required minimum CGPA is "
                f"{required:g}. "
                f"Therefore, you are eligible "
                f"based on the stated CGPA requirement."
            )

        else:

            answer = (
                f"Your CGPA is {student:g}. "
                f"The required minimum CGPA is "
                f"{required:g}. "
                f"Therefore, you are not eligible "
                f"based on the stated CGPA requirement."
            )

        return self._with_sources(
            answer,
            sources
        )

    # ==========================================================
    # ARREARS
    # ==========================================================

    def arrears_answer(
        self,
        rule_result,
        sources
    ):

        student = rule_result[
            "student_arrears"
        ]

        maximum = rule_result[
            "maximum_arrears"
        ]

        if rule_result["eligible"]:

            answer = (
                f"You have {student:g} arrears. "
                f"The maximum allowed arrears are "
                f"{maximum:g}. "
                f"Therefore, you are eligible "
                f"based on the stated arrears requirement."
            )

        else:

            answer = (
                f"You have {student:g} arrears. "
                f"The maximum allowed arrears are "
                f"{maximum:g}. "
                f"Therefore, you are not eligible "
                f"based on the stated arrears requirement."
            )

        return self._with_sources(
            answer,
            sources
        )

    # ==========================================================
    # GENERAL PDF QUESTION
    # ==========================================================

    def general_answer(
        self,
        question,
        evidence,
        sources
    ):

        if not evidence:

            return self.unsupported_answer()

        answer = self.extract_relevant_evidence(
            question,
            evidence
        )

        if not answer:

            answer = self.clean_evidence(
                evidence
            )

        return self._with_sources(
            answer,
            sources
        )

    # ==========================================================
    # GENERAL EVIDENCE EXTRACTION
    # ==========================================================

    def extract_relevant_evidence(
        self,
        question,
        evidence
    ):

        question_terms = self._important_words(
            question
        )

        if not question_terms:
            return None

        # ------------------------------------------------------
        # Split PDF evidence into lines first.
        # This works better for policy PDFs because many
        # important rules are written as numbered lines.
        # ------------------------------------------------------

        raw_lines = re.split(
            r"\n+",
            evidence
        )

        lines = []

        for line in raw_lines:

            line = line.strip()

            if not line:
                continue

            # Remove source metadata
            if line.lower().startswith(
                "source:"
            ):
                continue

            # Remove obvious page-only markers
            if re.fullmatch(
                r"(page\s*)?\d+",
                line.lower()
            ):
                continue

            lines.append(line)

        # ------------------------------------------------------
        # Create candidate sentences from each line.
        # ------------------------------------------------------

        candidates = []

        for line in lines:

            # PDF extraction sometimes places several
            # sentences on one line.
            parts = re.split(
                r"(?<=[.!?])\s+",
                line
            )

            for part in parts:

                part = part.strip()

                if not part:
                    continue

                candidates.append(part)

        # ------------------------------------------------------
        # Score candidates based on question terms.
        # ------------------------------------------------------

        scored = []

        question_set = set(
            question_terms
        )

        for index, sentence in enumerate(
            candidates
        ):

            sentence_terms = set(
                self._important_words(
                    sentence
                )
            )

            if not sentence_terms:
                continue

            overlap = (
                question_set
                & sentence_terms
            )

            if not overlap:
                continue

            # Basic relevance
            score = len(overlap)

            # Reward exact phrase concepts
            question_lower = question.lower()
            sentence_lower = sentence.lower()

            if "minimum" in question_lower:
                if (
                    "minimum" in sentence_lower
                    or "at least" in sentence_lower
                    or "required" in sentence_lower
                ):
                    score += 2

            if "maximum" in question_lower:
                if (
                    "maximum" in sentence_lower
                    or "up to" in sentence_lower
                    or "allowed" in sentence_lower
                ):
                    score += 2

            if "required" in question_lower:
                if "required" in sentence_lower:
                    score += 1

            if "eligible" in question_lower:
                if "eligible" in sentence_lower:
                    score += 1

            scored.append(
                (
                    score,
                    index,
                    sentence
                )
            )

        if not scored:
            return None

        # ------------------------------------------------------
        # Highest relevance first
        # ------------------------------------------------------

        scored.sort(
            key=lambda item: (
                item[0],
                -item[1]
            ),
            reverse=True
        )

        # ------------------------------------------------------
        # Select relevant sentences.
        #
        # We also include nearby sentences because policy
        # documents often split one rule across multiple
        # extracted lines.
        # ------------------------------------------------------

        selected_indexes = []

        for score, index, sentence in scored[:3]:

            selected_indexes.append(index)

            # Add immediately following sentence when
            # it looks like continuation/context.
            if index + 1 < len(candidates):

                next_sentence = candidates[
                    index + 1
                ]

                if (
                    len(next_sentence) > 20
                    and next_sentence
                    not in [
                        item[2]
                        for item in scored[:3]
                    ]
                ):

                    selected_indexes.append(
                        index + 1
                    )

        # Remove duplicates
        selected_indexes = sorted(
            set(selected_indexes)
        )

        selected = []

        for index in selected_indexes:

            sentence = candidates[index]

            if sentence not in selected:

                selected.append(sentence)

        # ------------------------------------------------------
        # Limit answer length.
        # ------------------------------------------------------

        answer = " ".join(
            selected[:5]
        )

        answer = self.clean_answer(
            answer
        )

        return answer

    # ==========================================================
    # CLEAN ANSWER
    # ==========================================================

    def clean_answer(
        self,
        text
    ):

        text = text.strip()

        # Remove source metadata
        text = re.sub(
            r"Source:\s*.*?(?=\n|$)",
            "",
            text,
            flags=re.IGNORECASE
        )

        # Remove standalone numbering artifacts
        text = re.sub(
            r"(?<!\w)\d+\.\s*$",
            "",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        # Remove repeated spaces around punctuation
        text = re.sub(
            r"\s+([,.!?])",
            r"\1",
            text
        )

        return text.strip()

    # ==========================================================
    # FALLBACK EVIDENCE CLEANING
    # ==========================================================

    def clean_evidence(
        self,
        evidence
    ):

        evidence = evidence.strip()

        evidence = re.sub(
            r"Source:\s*.*?\n",
            "",
            evidence,
            flags=re.IGNORECASE
        )

        evidence = re.sub(
            r"\s+",
            " ",
            evidence
        )

        return evidence[:1200]

    # ==========================================================
    # IMPORTANT WORDS
    # ==========================================================

    def _important_words(
        self,
        text
    ):

        stop_words = {
            "what",
            "is",
            "are",
            "the",
            "a",
            "an",
            "of",
            "for",
            "to",
            "in",
            "on",
            "and",
            "or",
            "can",
            "i",
            "my",
            "me",
            "do",
            "does",
            "how",
            "when",
            "where",
            "why",
            "who",
            "which",
            "tell",
            "about",
            "please",
            "have",
            "has",
            "had",
            "can",
            "could",
            "would",
            "should"
        }

        words = re.findall(
            r"[a-zA-Z0-9%]+",
            text.lower()
        )

        result = []

        for word in words:

            if word in stop_words:
                continue

            if len(word) <= 2:
                continue

            result.append(word)

        return result

    # ==========================================================
    # UNSUPPORTED
    # ==========================================================

    def unsupported_answer(self):

        return (
            "I couldn't find reliable information "
            "to answer this question in the provided "
            "college documents. I don't want to guess."
        )

    # ==========================================================
    # ADD SOURCES
    # ==========================================================

    def _with_sources(
        self,
        answer,
        sources
    ):

        if not sources:
            return answer

        source_text = self.format_source(
            sources
        )

        if not source_text:
            return answer

        return (
            f"{answer}\n\n"
            f"📚 Sources:\n"
            f"{source_text}"
        )

    # ==========================================================
    # MAIN GENERATOR
    # ==========================================================

    def generate(
        self,
        question,
        rule_result,
        evidence,
        sources,
        grounded=True
    ):

        # ------------------------------------------------------
        # UNSUPPORTED QUESTION
        # ------------------------------------------------------

        if not grounded:

            return self.unsupported_answer()

        # ------------------------------------------------------
        # NO RULE
        # → GENERAL PDF QUESTION
        # ------------------------------------------------------

        if not rule_result:

            return self.general_answer(
                question,
                evidence,
                sources
            )

        # ------------------------------------------------------
        # RULE NOT APPLICABLE
        # → GENERAL PDF QUESTION
        # ------------------------------------------------------

        if not rule_result.get(
            "rule_found",
            False
        ):

            return self.general_answer(
                question,
                evidence,
                sources
            )

        # ------------------------------------------------------
        # ATTENDANCE
        # ------------------------------------------------------

        if (
            rule_result["rule"]
            == "minimum_attendance"
        ):

            return self.attendance_answer(
                rule_result,
                sources
            )

        # ------------------------------------------------------
        # CGPA
        # ------------------------------------------------------

        if (
            rule_result["rule"]
            == "minimum_cgpa"
        ):

            # General CGPA question:
            # "What is the minimum CGPA?"
            if "student_cgpa" not in rule_result:

                return self.general_answer(
                    question,
                    evidence,
                    sources
                )

            # Decision question:
            # "My CGPA is 6.2..."
            return self.cgpa_answer(
                rule_result,
                sources
            )

        # ------------------------------------------------------
        # ARREARS
        # ------------------------------------------------------

        if (
            rule_result["rule"]
            == "maximum_arrears"
        ):

            if "student_arrears" not in rule_result:

                return self.general_answer(
                    question,
                    evidence,
                    sources
                )

            return self.arrears_answer(
                rule_result,
                sources
            )

        # ------------------------------------------------------
        # FALLBACK
        # ------------------------------------------------------

        return self.general_answer(
            question,
            evidence,
            sources
        )