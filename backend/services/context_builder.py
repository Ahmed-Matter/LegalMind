
def build_context(chunks, question=None, max_chunks=2, max_chars=1200):

    if not chunks:
        return ""

    # 🔥 remove duplicates while preserving order
    seen = set()
    unique_chunks = []

    for c in chunks:
        text = c["text"].strip()
        if text not in seen:
            seen.add(text)
            unique_chunks.append(text)

    # 🔥 take top N chunks (already ranked)
    selected_chunks = unique_chunks[:max_chunks]

    # 🔥 merge into one coherent context
    merged_text = " ".join(selected_chunks)

    # 🔥 final trim (keep full meaning)
    return merged_text[:max_chars]