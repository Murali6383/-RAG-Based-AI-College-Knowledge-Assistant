import re

ATTENDANCE_PATTERNS = [
    r"(?:minimum|required|at least|need|needs|should maintain).*?(\d{2,3}(?:\.\d+)?)\s*%.*?(?:attendance|attend)",
    r"(\d{2,3}(?:\.\d+)?)\s*%.*?(?:minimum|required).*?(?:attendance|attend)",
]

USER_ATTENDANCE_PATTERNS = [
    r"(?:i have|my attendance is|attendance is|attendance).*?(\d{1,3}(?:\.\d+)?)\s*%",
]

def extract_percentage(text: str, patterns):
    for pattern in patterns:
        m = re.search(pattern, text.lower())
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
    return None

def attendance_decision(question: str, context: str):
    user_pct = extract_percentage(question, USER_ATTENDANCE_PATTERNS)
    required = extract_percentage(context, ATTENDANCE_PATTERNS)
    if user_pct is None or required is None:
        return None
    if user_pct < required:
        return {
            "decision": "NOT_ELIGIBLE",
            "user_percentage": user_pct,
            "required_percentage": required,
            "reason": f"{user_pct:g}% is below the required {required:g}% attendance."
        }
    return {
        "decision": "ELIGIBLE",
        "user_percentage": user_pct,
        "required_percentage": required,
        "reason": f"{user_pct:g}% meets the required {required:g}% attendance."
    }
