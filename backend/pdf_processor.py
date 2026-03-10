from pypdf import PdfReader
# read pdf pages and append text

def extract_text(file_path):
    reader=PdfReader(file_path)
    text=""

    for page in reader.pages:
        text +=page.extract_text()

    return text

def split_text(text,chunk_size=500, overlap=100):
    chunks=[]
    start=0

    while(start < len(text)):
        end=start + chunk_size
        chunk=text[start:end]

        chunks.append(chunk)
        start+=chunk_size -overlap

    return chunks

