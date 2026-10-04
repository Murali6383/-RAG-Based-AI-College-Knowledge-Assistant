import re


# ============================================================
# BASIC EXTRACTION FUNCTIONS
# ============================================================

def extract_percentages(text: str):
    """
    Extract percentages.

    Examples:
        70%   -> [70.0]
        75 %  -> [75.0]
        80.5% -> [80.5]
    """

    matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*%",
        text
    )

    return [float(x) for x in matches]


def extract_numbers(text: str):
    """
    Extract decimal numbers.

    Examples:
        6.2 -> [6.2]
        2 arrears -> [2.0]
    """

    matches = re.findall(
        r"\b\d+(?:\.\d+)?\b",
        text
    )

    return [float(x) for x in matches]


# ============================================================
# ATTENDANCE RULE
# ============================================================

def extract_required_attendance(evidence: str):
    """
    Extract the minimum attendance requirement.

    Supports:

        minimum attendance of 75%
        minimum 75% attendance
        minimum of 75% attendance
        at least 75% attendance
        75% attendance is required
        attendance of 75% is required
        attendance ... minimum ... 75%
    """

    evidence_lower = evidence.lower()

    patterns = [

        # Minimum attendance of 75%
        r"minimum\s+attendance\s+of\s+(\d+(?:\.\d+)?)\s*%",

        # Minimum 75% attendance
        r"minimum\s+(\d+(?:\.\d+)?)\s*%\s+attendance",

        # Minimum of 75% attendance
        r"minimum\s+of\s+(\d+(?:\.\d+)?)\s*%\s+attendance",

        # At least 75% attendance
        r"at\s+least\s+(\d+(?:\.\d+)?)\s*%\s+attendance",

        # 75% attendance is required
        r"(\d+(?:\.\d+)?)\s*%\s+attendance\s+is\s+required",

        # Attendance of 75% is required
        r"attendance\s+of\s+(\d+(?:\.\d+)?)\s*%\s+is\s+required",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            evidence_lower
        )

        if match:

            return float(
                match.group(1)
            )

    # --------------------------------------------------------
    # Fallback
    #
    # If the evidence contains "attendance",
    # "minimum", and a percentage, use that percentage.
    # --------------------------------------------------------

    if (
        "attendance" in evidence_lower
        and "minimum" in evidence_lower
    ):

        percentages = extract_percentages(
            evidence
        )

        if percentages:

            return percentages[0]

    return None


def check_attendance_rule(
    question: str,
    evidence: str
):
    """
    Compare student's attendance
    against policy requirement.
    """

    question_percentages = extract_percentages(
        question
    )

    if not question_percentages:

        return {
            "rule_found": False,
            "rule": "minimum_attendance",
            "reason": (
                "Student attendance percentage "
                "not provided"
            )
        }

    required_attendance = extract_required_attendance(
        evidence
    )

    if required_attendance is None:

        return {
            "rule_found": False,
            "rule": "minimum_attendance",
            "reason": (
                "Attendance requirement "
                "not found in evidence"
            )
        }

    student_attendance = question_percentages[0]

    eligible = (
        student_attendance >= required_attendance
    )

    return {
        "rule_found": True,
        "rule": "minimum_attendance",
        "student_attendance": student_attendance,
        "required_attendance": required_attendance,
        "eligible": eligible,
        "result": (
            "Eligible"
            if eligible
            else "Not eligible"
        )
    }


# ============================================================
# CGPA RULE
# ============================================================

def extract_required_cgpa(evidence: str):
    """
    Extract minimum CGPA.

    Supports:

        Minimum CGPA of 6.5
        Required CGPA of 6.5
        CGPA of 6.5 is required
        At least 6.5 CGPA
        Minimum 6.5 CGPA

    Important:
    We don't split using '.' because
    decimal values such as 6.5 contain '.'.
    """

    evidence_lower = evidence.lower()

    patterns = [

        # Minimum CGPA of 6.5
        r"minimum\s+cgpa\s+of\s+(\d+(?:\.\d+)?)",

        # Required CGPA of 6.5
        r"required\s+cgpa\s+of\s+(\d+(?:\.\d+)?)",

        # CGPA of 6.5 is required
        r"cgpa\s+of\s+(\d+(?:\.\d+)?)\s+is\s+required",

        # At least 6.5 CGPA
        r"at\s+least\s+(\d+(?:\.\d+)?)\s+cgpa",

        # Minimum 6.5 CGPA
        r"minimum\s+(\d+(?:\.\d+)?)\s+cgpa",

        # Required 6.5 CGPA
        r"required\s+(\d+(?:\.\d+)?)\s+cgpa",

        # CGPA 6.5 is required
        r"cgpa\s+(\d+(?:\.\d+)?)\s+is\s+required",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            evidence_lower
        )

        if match:

            return float(
                match.group(1)
            )

    return None


def check_cgpa_rule(
    question: str,
    evidence: str
):
    """
    Compare student's CGPA
    against minimum CGPA.
    """

    question_numbers = extract_numbers(
        question
    )

    if not question_numbers:

        return {
            "rule_found": False,
            "rule": "minimum_cgpa",
            "reason": "Student CGPA not provided"
        }

    required_cgpa = extract_required_cgpa(
        evidence
    )

    if required_cgpa is None:

        return {
            "rule_found": False,
            "rule": "minimum_cgpa",
            "reason": (
                "CGPA requirement "
                "not found in evidence"
            )
        }

    student_cgpa = question_numbers[0]

    eligible = (
        student_cgpa >= required_cgpa
    )

    return {
        "rule_found": True,
        "rule": "minimum_cgpa",
        "student_cgpa": student_cgpa,
        "required_cgpa": required_cgpa,
        "eligible": eligible,
        "result": (
            "Eligible"
            if eligible
            else "Not eligible"
        )
    }


# ============================================================
# ARREARS RULE
# ============================================================

def extract_max_arrears(evidence: str):
    """
    Extract maximum allowed arrears.

    Supports:

        No standing arrears
        Maximum 2 arrears
        Maximum of 2 arrears
        2 arrears allowed
        Up to 2 arrears
    """

    evidence_lower = evidence.lower()

    # --------------------------------------------------------
    # No standing arrears = 0
    # --------------------------------------------------------

    if "no standing arrears" in evidence_lower:

        return 0

    patterns = [

        r"maximum\s+(\d+(?:\.\d+)?)\s+arrears",

        r"maximum\s+of\s+(\d+(?:\.\d+)?)\s+arrears",

        r"(\d+(?:\.\d+)?)\s+arrears\s+allowed",

        r"up\s+to\s+(\d+(?:\.\d+)?)\s+arrears",

        r"arrears\s+limit\s+of\s+(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            evidence_lower
        )

        if match:

            return float(
                match.group(1)
            )

    return None


def check_arrears_rule(
    question: str,
    evidence: str
):
    """
    Compare student's arrears
    against maximum allowed arrears.
    """

    question_numbers = extract_numbers(
        question
    )

    if not question_numbers:

        return {
            "rule_found": False,
            "rule": "maximum_arrears",
            "reason": (
                "Student arrears count "
                "not provided"
            )
        }

    max_arrears = extract_max_arrears(
        evidence
    )

    if max_arrears is None:

        return {
            "rule_found": False,
            "rule": "maximum_arrears",
            "reason": (
                "Arrears requirement "
                "not found in evidence"
            )
        }

    student_arrears = question_numbers[0]

    eligible = (
        student_arrears <= max_arrears
    )

    return {
        "rule_found": True,
        "rule": "maximum_arrears",
        "student_arrears": student_arrears,
        "maximum_arrears": max_arrears,
        "eligible": eligible,
        "result": (
            "Eligible"
            if eligible
            else "Not eligible"
        )
    }


# ============================================================
# MAIN POLICY ENGINE
# ============================================================

def check_policy_rule(
    question: str,
    evidence: str
):
    """
    Detect policy type and execute
    the appropriate deterministic rule.
    """

    question_lower = question.lower()

    # --------------------------------------------------------
    # Attendance
    # --------------------------------------------------------

    if "attendance" in question_lower:

        return check_attendance_rule(
            question,
            evidence
        )

    # --------------------------------------------------------
    # CGPA
    # --------------------------------------------------------

    if "cgpa" in question_lower:

        return check_cgpa_rule(
            question,
            evidence
        )

    # --------------------------------------------------------
    # Arrears
    # --------------------------------------------------------

    if "arrear" in question_lower:

        return check_arrears_rule(
            question,
            evidence
        )

    # --------------------------------------------------------
    # No deterministic rule detected
    # --------------------------------------------------------

    return {
        "rule_found": False,
        "rule": None,
        "reason": (
            "No deterministic policy rule detected"
        )
    }