from pypdf import PdfReader


def extract_pages(file_path):

    reader = PdfReader(file_path)

    pages = []

    for i, page in enumerate(reader.pages):

        text = page.extract_text()

        pages.append({
            "page": i + 1,
            "text": text
        })

    return pages

def split_text_by_page(pages, chunk_size=150, overlap=30):

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

