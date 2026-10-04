import re

from .question_analyzer import analyze_question


# ============================================================
# TOPIC KEYWORDS
# ============================================================

TOPIC_KEYWORDS = {

    # --------------------------------------------------------
    # Attendance
    # --------------------------------------------------------

    "attendance": [
        "attendance",
        "attended",
        "absent",
        "absence",
        "condonation",
        "attendance percentage",
        "attendance requirement",
        "attendance shortage",
        "attendance marks"
    ],

    # --------------------------------------------------------
    # Examinations
    # --------------------------------------------------------

    "exams": [
        "exam",
        "exams",
        "examination",
        "examinations",
        "end semester exam",
        "end-semester exam",
        "end semester exams",
        "end-semester exams",
        "end semester examination",
        "end-semester examination",
        "end semester examinations",
        "end-semester examinations",
        "hall ticket",
        "question paper",
        "revaluation",
        "re-evaluation",
        "malpractice",
        "arrear exam",
        "arrear exams",
        "supplementary exam",
        "supplementary exams",
        "examination hall"
    ],

    # --------------------------------------------------------
    # Hostel
    # --------------------------------------------------------

    "hostel": [
        "hostel",
        "hostels",
        "mess",
        "warden",
        "hostel room",
        "room sharing",
        "hostel visitor",
        "hostel visitors",
        "out-pass",
        "outpass",
        "hostel fee",
        "mess fee",
        "late entry"
    ],

    # --------------------------------------------------------
    # Placement
    # --------------------------------------------------------

    "placement": [
        "placement",
        "placements",
        "campus placement",
        "campus placements",
        "placement drive",
        "placement drives",
        "recruitment drive",
        "recruitment drives",
        "training and placement",
        "tpc",
        "standing arrears",
        "placement eligibility",
        "placement cgpa",
        "placement attendance",
        "company offer",
        "offer policy",
        "dream company",
        "super dream"
    ],

    # --------------------------------------------------------
    # Leave
    # --------------------------------------------------------

    "leave": [
        "leave",
        "leave policy",
        "leave rules",
        "medical leave",
        "casual leave",
        "earned leave",
        "maternity leave",
        "paternity leave",
        "leave permission",
        "leave during examinations"
    ],

    # --------------------------------------------------------
    # College Regulations
    # --------------------------------------------------------

    "college_regulations": [
        "college regulation",
        "college regulations",
        "institution regulation",
        "institution regulations",
        "academic regulation",
        "academic regulations",
        "college rule",
        "college rules",
        "academic rules",
        "general regulations"
    ],

}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize(text: str):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9%\- ]+",
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
# PHRASE PRESENT
# ============================================================

def phrase_present(
    phrase: str,
    text: str
):

    normalized_text = normalize(text)
    normalized_phrase = normalize(phrase)

    return normalized_phrase in normalized_text


# ============================================================
# CHECK WHETHER TOPIC IS PRESENT
# ============================================================

def topic_present(
    topic: str,
    text: str
):

    normalized_text = normalize(text)

    keywords = TOPIC_KEYWORDS.get(
        topic,
        []
    )

    # --------------------------------------------------------
    # Prefer multi-word / specific phrases
    # --------------------------------------------------------

    for keyword in keywords:

        normalized_keyword = normalize(
            keyword
        )

        if " " in normalized_keyword:

            if normalized_keyword in normalized_text:
                return True

    # --------------------------------------------------------
    # Single-word topic detection
    # --------------------------------------------------------

    for keyword in keywords:

        normalized_keyword = normalize(
            keyword
        )

        if " " not in normalized_keyword:

            pattern = (
                r"\b"
                + re.escape(normalized_keyword)
                + r"\b"
            )

            if re.search(
                pattern,
                normalized_text
            ):

                return True

    return False


# ============================================================
# DETECT REQUESTED TOPICS
# ============================================================

def detect_requested_topics(
    question: str
):

    question_normalized = normalize(
        question
    )

    detected = []

    # --------------------------------------------------------
    # Examine each topic
    # --------------------------------------------------------

    for topic in TOPIC_KEYWORDS:

        if topic_present(
            topic,
            question_normalized
        ):

            detected.append(topic)

    # --------------------------------------------------------
    # Important correction:
    #
    # "eligibility" alone must NOT mean placement.
    #
    # "semester" alone must NOT mean
    # college_regulations.
    # --------------------------------------------------------

    return list(
        dict.fromkeys(detected)
    )


# ============================================================
# CHECK COMPLETENESS
# ============================================================

def check_completeness(
    question: str,
    answer: str,
    evidence: str
):

    """
    Check whether the generated answer covers
    the actual topics explicitly requested
    by the user.

    This is NOT a general keyword detector.

    Example:

        "Eligibility to Write End-Semester Exams"

    should detect:

        exams

    and should NOT automatically detect:

        placement
        college_regulations
    """

    # ========================================================
    # ANALYZE QUESTION
    # ========================================================

    analysis = analyze_question(
        question
    )

    analyzer_topics = analysis.get(
        "topics",
        []
    )

    # ========================================================
    # USE STRICT TOPIC DETECTION
    # ========================================================

    requested_topics = detect_requested_topics(
        question
    )

    # --------------------------------------------------------
    # If question_analyzer found a topic that
    # strict detection confirms, keep it.
    #
    # This prevents unrelated broad keyword matches.
    # --------------------------------------------------------

    if analyzer_topics:

        filtered_topics = []

        for topic in analyzer_topics:

            if topic in requested_topics:

                filtered_topics.append(
                    topic
                )

        requested_topics = filtered_topics

    # ========================================================
    # NO IDENTIFIABLE TOPICS
    # ========================================================

    if not requested_topics:

        return {

            "complete": True,

            "coverage": 1.0,

            "requested_topics": [],

            "covered_topics": [],

            "missing_topics": [],

            "reason": (
                "No specific topics were detected"
            )

        }

    # ========================================================
    # CHECK ANSWER TOPIC COVERAGE
    # ========================================================

    covered_topics = []
    missing_topics = []

    for topic in requested_topics:

        if topic_present(
            topic,
            answer
        ):

            covered_topics.append(
                topic
            )

        else:

            missing_topics.append(
                topic
            )

    # ========================================================
    # CALCULATE COVERAGE
    # ========================================================

    coverage = (
        len(covered_topics)
        / len(requested_topics)
    )

    complete = (
        len(missing_topics) == 0
    )

    # ========================================================
    # RESULT
    # ========================================================

    if complete:

        reason = (
            "All explicitly requested topics "
            "are covered"
        )

    else:

        reason = (
            "Answer is missing one or more "
            "explicitly requested topics"
        )

    return {

        "complete": complete,

        "coverage": coverage,

        "requested_topics":
            requested_topics,

        "covered_topics":
            covered_topics,

        "missing_topics":
            missing_topics,

        "reason": reason

    }