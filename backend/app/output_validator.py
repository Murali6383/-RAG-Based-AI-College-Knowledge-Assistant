import re


# ============================================================
# WORDS THAT SHOULD NOT BE TREATED AS FACTUAL CLAIMS
# ============================================================

STOP_WORDS = {

    # ------------------------------
    # Grammar
    # ------------------------------

    "the", "a", "an",
    "is", "are", "was", "were",
    "be", "been", "being",

    "of", "for", "to", "in", "on",
    "at", "by", "from", "with",
    "about", "into",

    "and", "or", "but", "as",

    "this", "that", "these", "those",

    "it", "its",

    "your", "you", "i", "we",
    "they", "them", "their", "our",

    # ------------------------------
    # Modal / auxiliary verbs
    # ------------------------------

    "can", "could", "may", "might",
    "must", "should", "would", "will",

    "have", "has", "had",

    "do", "does", "did",

    # ------------------------------
    # Negative / response words
    # ------------------------------

    "not", "no", "yes",

    # ------------------------------
    # Question words
    # ------------------------------

    "what", "when", "where",
    "who", "how", "why", "which",

    # ------------------------------
    # General language
    # ------------------------------

    "than", "then", "also", "only",
    "very", "more", "most", "such",
    "any", "some", "each",

    # ------------------------------
    # Natural answer language
    # ------------------------------

    "based", "provided", "document",
    "documents", "information",
    "answer", "answers",
    "following", "follows",
    "according", "relevant",
    "available", "details",
    "section", "sections",
    "includes", "include",
    "including",

    "students", "student",

    # ------------------------------
    # Formatting / headings
    # ------------------------------

    "rule", "rules",
    "regulation", "regulations",
    "policy", "policies",
    "guideline", "guidelines",

    "minimum", "maximum",
    "requirement", "requirements",

    "attendance",

    "exam", "exams",
    "examination", "examinations",
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize(text: str):
    """
    Normalize text for factual comparison.

    Important:
    - Converts 75% -> 75 %
    - Converts 75 % -> 75 %
    - Removes markdown / LaTeX formatting
    - Keeps numbers and percentages
    """

    text = text.lower()

    # Convert common LaTeX commands into spaces.
    text = re.sub(r"\\frac", " ", text)
    text = re.sub(r"\\text", " ", text)
    text = re.sub(r"[{}]", " ", text)

    # Normalize percentage spacing.
    text = re.sub(
        r"(\d+(?:\.\d+)?)\s*%",
        r"\1 %",
        text
    )

    # Keep letters, numbers, %, spaces and hyphens.
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
# NORMALIZE NUMBER
# ============================================================

def normalize_number(value: str):
    """
    Convert all equivalent number formats
    into one canonical representation.

    Examples:

        75%
        75 %
        75.0%
        75.0 %

    all become:

        75 %
    """

    value = value.strip()

    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*%?",
        value
    )

    if not match:
        return value

    number = match.group(1)

    if "." in number:
        number = number.rstrip("0").rstrip(".")

    return f"{number} %"


# ============================================================
# EXTRACT NUMBERS
# ============================================================

def extract_numbers(text: str):
    """
    Extract percentages and standalone numbers.

    Examples:

        75%
        75 %
        65%
        Rs. 250
        5 days
        20 minutes

    """

    normalized = normalize(text)

    matches = re.findall(
        r"\b\d+(?:\.\d+)?\s*%?",
        normalized
    )

    return [
        normalize_number(match)
        for match in matches
    ]


# ============================================================
# EXTRACT FACTUAL TERMS
# ============================================================

def extract_important_terms(text: str):

    words = normalize(text).split()

    terms = []

    for word in words:

        word = word.strip(".-")

        if not word:
            continue

        if word in STOP_WORDS:
            continue

        if len(word) <= 3:
            continue

        # Numbers are checked separately.
        if re.fullmatch(
            r"\d+(?:\.\d+)?%?",
            word
        ):
            continue

        terms.append(word)

    return terms


# ============================================================
# WORD FAMILY / ALIAS MATCHING
# ============================================================

TERM_ALIASES = {

    "exam": [
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

    "leave": [
        "leave",
        "permission",
        "absence"
    ],

    "placement": [
        "placement",
        "placements",
        "recruitment"
    ],

    "student": [
        "student",
        "students"
    ],

}


# ============================================================
# TERM SUPPORTED
# ============================================================

def term_supported(
    term: str,
    evidence: str
):

    evidence_words = set(
        normalize(evidence).split()
    )

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    if term in evidence_words:
        return True

    # --------------------------------------------------------
    # Alias match
    # --------------------------------------------------------

    for base_term, aliases in TERM_ALIASES.items():

        if term == base_term or term in aliases:

            for alias in aliases:

                alias_normalized = normalize(alias)

                if alias_normalized in evidence_words:
                    return True

    # --------------------------------------------------------
    # Word-family matching
    # --------------------------------------------------------

    for evidence_word in evidence_words:

        if (
            len(term) >= 5
            and len(evidence_word) >= 5
        ):

            if (
                evidence_word.startswith(term)
                or term.startswith(evidence_word)
            ):
                return True

    return False


# ============================================================
# CHECK IMPORTANT FACTUAL TERMS
# ============================================================

def check_terms(
    answer: str,
    evidence: str
):

    answer_terms = extract_important_terms(
        answer
    )

    supported_terms = []
    missing_terms = []

    for term in answer_terms:

        if term_supported(
            term,
            evidence
        ):

            supported_terms.append(term)

        else:

            missing_terms.append(term)

    if answer_terms:

        coverage = (
            len(supported_terms)
            / len(answer_terms)
        )

    else:

        coverage = 1.0

    return (
        answer_terms,
        supported_terms,
        missing_terms,
        coverage
    )


# ============================================================
# MAIN VALIDATOR
# ============================================================

def validate_answer(
    question: str,
    answer: str,
    evidence: str
):

    """
    Validate an AI-generated answer against
    retrieved college-document evidence.

    This validator checks:
        1. Empty answers
        2. Unsupported numbers
        3. Unsupported factual terms

    Completeness is handled separately.
    """

    # ========================================================
    # EMPTY ANSWER
    # ========================================================

    if not answer or not answer.strip():

        return {
            "supported": False,
            "coverage": 0.0,
            "reason": "Empty answer",
            "missing_terms": [],
            "unsupported_numbers": []
        }

    # ========================================================
    # NORMALIZE
    # ========================================================

    normalized_answer = normalize(answer)
    normalized_evidence = normalize(evidence)

    # ========================================================
    # NUMBER SAFETY
    # ========================================================

    answer_numbers = extract_numbers(
        normalized_answer
    )

    evidence_numbers = extract_numbers(
        normalized_evidence
    )

    unsupported_numbers = []

    for number in answer_numbers:

        if number not in evidence_numbers:

            if number not in unsupported_numbers:
                unsupported_numbers.append(number)

    # ========================================================
    # TERM SAFETY
    # ========================================================

    (
        answer_terms,
        supported_terms,
        missing_terms,
        coverage
    ) = check_terms(
        normalized_answer,
        normalized_evidence
    )

    # ========================================================
    # NUMBER FAILURE
    # ========================================================

    if unsupported_numbers:

        return {

            "supported": False,

            "coverage": coverage,

            "reason": (
                "Answer contains numbers "
                "not found in evidence"
            ),

            "missing_terms": missing_terms,

            "unsupported_numbers":
                unsupported_numbers

        }

    # ========================================================
    # VERY LOW FACTUAL COVERAGE
    # ========================================================

    if (
        answer_terms
        and coverage < 0.45
    ):

        return {

            "supported": False,

            "coverage": coverage,

            "reason": (
                "Answer contains too many "
                "terms unsupported by evidence"
            ),

            "missing_terms": missing_terms,

            "unsupported_numbers": []

        }

    # ========================================================
    # SUPPORTED
    # ========================================================

    return {

        "supported": True,

        "coverage": coverage,

        "reason": (
            "Answer contains no unsupported "
            "numbers and its factual terms "
            "are sufficiently grounded"
        ),

        "missing_terms": missing_terms,

        "unsupported_numbers": []

    }