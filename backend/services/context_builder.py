
def build_context(chunks, question=None, max_chunks=4, max_chars=2000):

    if not chunks:
        return ""

    seen = set()
    unique_chunks = []

    for c in chunks:
        text = c["text"].strip()
        if text not in seen:
            seen.add(text)
            unique_chunks.append(text)

    #   take top N chunks (already ranked)
    selected_chunks = unique_chunks[:max_chunks]

    merged_text = " ".join(selected_chunks)

    return merged_text[:max_chars]