import re


TOPIC_KEYWORDS = {

    "attendance": {
        "attendance",
        "absent",
        "absence",
        "condonation",
        "od",
        "on-duty",
        "proxy",
        "biometric",
        "late arrival"
    },

    "exams": {
        "exam",
        "exams",
        "examination",
        "end-semester",
        "semester exam",
        "question paper",
        "hall ticket",
        "arrear",
        "arrears"
    },

    "hostel": {
        "hostel",
        "mess",
        "warden",
        "room",
        "visitor",
        "out-pass",
        "outpass"
    },

    "placement": {
        "placement",
        "placements",
        "company",
        "recruitment",
        "eligibility",
        "cgpa",
        "arrears"
    },

    "leave": {
        "leave",
        "permission",
        "holiday",
        "absence"
    },

    "college_regulations": {
        "regulation",
        "regulations",
        "academic",
        "semester",
        "course",
        "credit"
    }
}


def normalize(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\- ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_topics(question: str):

    question = normalize(question)

    detected = []

    for topic, keywords in TOPIC_KEYWORDS.items():

        for keyword in keywords:

            if keyword in question:
                detected.append(topic)
                break

    return list(dict.fromkeys(detected))


def analyze_question(question: str):

    topics = detect_topics(question)

    broad = any(
        phrase in question.lower()
        for phrase in [
            "what are the rules",
            "what are the regulations",
            "what are the policies",
            "what are the guidelines",
            "tell me the rules",
            "tell me about the rules",
            "summarize the rules",
            "what does the document say"
            "what is the college rules",
            "what are the college rules",
            "college rules",
            "college regulations",
        ]
    )

    return {
        "broad": broad,
        "topics": topics,
        "multi_topic": len(topics) > 1
    }