DOCUMENT_TOPIC_MAP = {

    "attendance": [
        "attendance_rules.pdf"
    ],

    "exams": [
        "exam_regulations.pdf"
    ],

    "hostel": [
        "hostel_rules.pdf"
    ],

    "placement": [
        "placement_guidelines.pdf"
    ],

    "leave": [
        "leave_policy.pdf"
    ],

    "college_regulations": [
        "college_regulations.pdf"
    ],

    "department": [
        "department_handbook.pdf"
    ]

}


ALL_DOCUMENTS = [
    "college_regulations.pdf",
    "attendance_rules.pdf",
    "exam_regulations.pdf",
    "placement_guidelines.pdf",
    "hostel_rules.pdf",
    "leave_policy.pdf",
    "department_handbook.pdf"
]


class DocumentExpansion:

    def get_documents_for_topics(
        self,
        topics
    ):

        documents = []

        for topic in topics:

            for filename in DOCUMENT_TOPIC_MAP.get(
                topic,
                []
            ):

                if filename not in documents:

                    documents.append(
                        filename
                    )

        return documents

    def get_all_documents(self):

        return ALL_DOCUMENTS.copy()