import re


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    "what",
    "are",
    "is",
    "the",
    "a",
    "an",
    "of",
    "for",
    "to",
    "does",
    "do",
    "can",
    "i",
    "my",
    "how",
    "much",
    "many",
    "required",
    "require",
    "need",
    "with",
    "and",
    "in",
    "on",
    "tell",
    "me",
    "about",
    "have",
    "had",
    "has",
    "this",
    "that",
    "please",
    "could",
    "would",
    "should",
    "explain",
    "give"
}


# ============================================================
# TERM ALIASES
# ============================================================

TERM_ALIASES = {

    "exam": [
        "exam",
        "exams",
        "examination",
        "examinations",
        "semester"
    ],

    "exams": [
        "exam",
        "exams",
        "examination",
        "examinations",
        "semester"
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

    "attendance": [
        "attendance",
        "attended",
        "absent",
        "absence",
        "condonation"
    ],

    "attend": [
        "attendance",
        "attended",
        "absent",
        "absence"
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

    "regulation": [
        "rule",
        "rules",
        "regulation",
        "regulations",
        "policy",
        "policies"
    ],

    "regulations": [
        "rule",
        "rules",
        "regulation",
        "regulations",
        "policy",
        "policies"
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
        "companies",
        "eligibility"
    ],

    "leave": [
        "leave",
        "permission",
        "absence",
        "holiday"
    ],

    "college": [
        "college",
        "institution",
        "campus",
        "academic"
    ],

    "academic": [
        "academic",
        "semester",
        "course",
        "credit",
        "regulation"
    ]
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize(text: str) -> str:
    """
    Standard normalization.

    Examples:

    end-semester
    end semester

    Both become:

    end semester
    """

    text = text.lower()

    # Convert hyphen and underscore to space
    text = re.sub(r"[-_/]+", " ", text)

    # Remove punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# COMPACT TEXT
# ============================================================

def compact_text(text: str) -> str:
    """
    Removes spaces, hyphens, underscores and punctuation.

    Examples:

    end-semester -> endsemester
    end semester -> endsemester
    endsemester  -> endsemester

    All become the same value.
    """

    return re.sub(
        r"[^a-z0-9]",
        "",
        text.lower()
    )


# ============================================================
# CLEAN WORD
# ============================================================

def clean_word(word: str):

    return re.sub(
        r"[^a-z0-9%]",
        "",
        word.lower()
    )


# ============================================================
# EXTRACT PERCENTAGES
# ============================================================

def extract_percentages(text: str):

    matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*%",
        text
    )

    return [
        float(value)
        for value in matches
    ]


# ============================================================
# EXTRACT IMPORTANT TERMS
# ============================================================

def extract_terms(question: str):

    words = normalize(question).split()

    terms = []

    for word in words:

        word = clean_word(word)

        if not word:
            continue

        # Ignore numbers
        if re.fullmatch(
            r"\d+(?:\.\d+)?",
            word
        ):
            continue

        # Ignore percentages
        if re.fullmatch(
            r"\d+(?:\.\d+)?%",
            word
        ):
            continue

        # Ignore stop words
        if word in STOP_WORDS:
            continue

        # Ignore very short words
        if len(word) <= 2:
            continue

        terms.append(word)

    return terms


# ============================================================
# ALIAS MATCHING
# ============================================================

def alias_supported(
    term: str,
    evidence: str
):

    evidence_words = set(
        clean_word(word)
        for word in normalize(evidence).split()
    )

    aliases = TERM_ALIASES.get(
        term,
        [term]
    )

    for alias in aliases:

        alias = clean_word(alias)

        if alias in evidence_words:
            return True

    return False


# ============================================================
# WORD FAMILY MATCHING
# ============================================================

def word_supported(
    term: str,
    evidence: str
):

    evidence_words = set(
        clean_word(word)
        for word in normalize(evidence).split()
    )

    # Exact match
    if term in evidence_words:
        return True

    # Alias match
    if alias_supported(
        term,
        evidence
    ):
        return True

    # Word-family match
    for evidence_word in evidence_words:

        if (
            len(term) >= 4
            and len(evidence_word) >= 4
        ):

            if (
                evidence_word.startswith(term)
                or term.startswith(evidence_word)
            ):
                return True

    return False


# ============================================================
# ENTITY EXTRACTION
# ============================================================

def extract_entities(question: str):

    original_words = question.split()

    entities = []

    for word in original_words:

        clean = re.sub(
            r"[^A-Za-z0-9]",
            "",
            word
        )

        if not clean:
            continue

        # Detect capitalized named entities
        if (
            clean[0].isupper()
            and clean.lower() not in STOP_WORDS
        ):

            entities.append(
                clean.lower()
            )

    return entities


# ============================================================
# ENTITY SUPPORTED CHECK
# ============================================================

def entity_supported(
    entity: str,
    evidence: str
):
    """
    Robust entity matching.

    Handles:

    end-semester
    end semester
    endsemester

    as equivalent.
    """

    entity_compact = compact_text(
        entity
    )

    evidence_compact = compact_text(
        evidence
    )

    if not entity_compact:
        return False

    return entity_compact in evidence_compact


# ============================================================
# MAIN GROUNDING CHECK
# ============================================================

def check_grounding(
    question: str,
    evidence: str
):

    # ----------------------------------------
    # Extract important question terms
    # ----------------------------------------

    terms = extract_terms(
        question
    )

    found = []

    missing = []

    # ----------------------------------------
    # Check every term against evidence
    # ----------------------------------------

    for term in terms:

        if word_supported(
            term,
            evidence
        ):

            found.append(term)

        else:

            missing.append(term)

    # ----------------------------------------
    # Check named entities
    # ----------------------------------------

    entities = extract_entities(
        question
    )

    missing_entities = []

    for entity in entities:

        if not entity_supported(
            entity,
            evidence
        ):

            missing_entities.append(
                entity
            )

    # ----------------------------------------
    # Entity failure
    # ----------------------------------------

    if missing_entities:

        return {

            "supported": False,

            "coverage": 0.0,

            "reason":
                "Required entity not found in evidence",

            "found_terms":
                found,

            "missing_terms":
                missing,

            "missing_entities":
                missing_entities
        }

    # ----------------------------------------
    # No important terms
    # ----------------------------------------

    if not terms:

        return {

            "supported": True,

            "coverage": 1.0,

            "reason":
                "No important terms detected",

            "found_terms": [],

            "missing_terms": [],

            "missing_entities": []
        }

    # ----------------------------------------
    # Calculate coverage
    # ----------------------------------------

    coverage = (
        len(found) /
        len(terms)
    )

    # ----------------------------------------
    # Minimum grounding requirement
    # ----------------------------------------

    supported = (
        coverage >= 0.5
    )

    # ----------------------------------------
    # Return result
    # ----------------------------------------

    return {

        "supported":
            supported,

        "coverage":
            coverage,

        "reason": (

            "Evidence contains sufficient "
            "question terms"

            if supported

            else

            "Evidence does not contain "
            "enough question terms"
        ),

        "found_terms":
            found,

        "missing_terms":
            missing,

        "missing_entities":
            missing_entities
    }