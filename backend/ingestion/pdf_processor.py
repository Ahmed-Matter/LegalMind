from pypdf import PdfReader
import re


def clean_text(text):

    if not text:
        return ""

    # remove line breaks
    text = re.sub(r"\n+", " ", text)

    #   fix glued words (lowercase → uppercase)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    #   fix missing spaces after punctuation
    text = re.sub(r"([.,;:])([A-Za-z])", r"\1 \2", text)

    # fix broken words (m onth → month)
    text = re.sub(r"\b(\w)\s+(\w)\b", r"\1\2", text)
    # add space between number and word
    text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", text)

# add space between word and number
    text = re.sub(r"([A-Za-z])(\d)", r"\1 \2", text)
    # remove duplicate words
    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text, flags=re.IGNORECASE)

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_pages(file_path):

    reader = PdfReader(file_path)
    pages = []

    for i, page in enumerate(reader.pages):

        raw_text = page.extract_text()

        if not raw_text:
            continue

        text = clean_text(raw_text)

        pages.append({
            "page": i + 1,
            "text": text
        })

    return pages

# def clean_text(text):

#     if not text:
#         return ""

#     # remove line breaks
#     text = re.sub(r"\n+", " ", text)

#     #   FIX glued words (lowercase → uppercase)
#     text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

#     #   FIX missing spaces after punctuation
#     text = re.sub(r"([.,;:])([A-Za-z])", r"\1 \2", text)

#     # fix broken words (m onth → month)
#     text = re.sub(r"(\w)\s+(\w)", r"\1\2", text)

#     # remove duplicate words
#     text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text, flags=re.IGNORECASE)

#     # normalize spaces
#     text = re.sub(r"\s+", " ", text)

#     return text.strip()

# def split_text_by_page(pages, chunk_size=150, overlap=30):

    chunks = []

    for p in pages:

        text = p["text"]
        page = p["page"]

        words = text.split()

        start = 0

        while start < len(words):

            chunk_words = words[start:start+chunk_size]

            chunk = " ".join(chunk_words)

            chunks.append({
                "text": chunk,
                "page": page
            })

            start += chunk_size - overlap

    return chunks

def split_by_articles(text):
    import re

    text = re.sub(r"\s+", " ", text)

    #   split ONLY by section numbers (e.g., "1. ", "2. ")
    parts = re.split(r"(?=\d+\.\s+[A-Za-z])", text)

    chunks = []

    for part in parts:
        part = part.strip()

        # skip empty or tiny fragments
        if len(part) < 100:
            continue

        chunks.append({
            "text": part,
            "page": 0
        })

    print("Chunks found:", len(chunks))
    return chunks

def process_pdf(file_path):

    pages = extract_pages(file_path)

    full_text = " ".join(p["text"] for p in pages if p["text"])

    #   STRICT SECTION SPLIT
    import re
    parts = re.split(r"(?=\d+\.\s+[A-Za-z])", full_text)

    chunks = []

    for part in parts:
        part = part.strip()

        if len(part) < 100:
            continue

        chunks.append({
            "text": part,
            "page": 0
        })

    print("Chunks found:", len(chunks))
    return chunks


# def split_large_chunks(chunks, max_words=200, overlap=50):

    new_chunks = []

    for c in chunks:

        words = c["text"].split()

        if len(words) <= max_words:
            new_chunks.append(c)
            continue

        start = 0
        while start < len(words):

            chunk_words = words[start:start+max_words]

            new_chunks.append({
                "text": " ".join(chunk_words),
                "title": c.get("title", ""),
                "page": c.get("page", 0)
            })

            start += max_words - overlap

    return new_chunks