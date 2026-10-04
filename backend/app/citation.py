def build_citations(sources):
    """
    Build clean citation information from
    retrieved PDF sources.
    """

    if not sources:
        return []

    citations = []

    seen = set()

    for source in sources:

        filename = source.get("file", "Unknown document")
        page = source.get("page", "Unknown")

        key = (filename, page)

        if key in seen:
            continue

        seen.add(key)

        citations.append({
            "file": filename,
            "page": page,
            "citation": f"{filename} — Page {page}"
        })

    return citations