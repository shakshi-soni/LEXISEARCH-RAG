import fitz  # PyMuPDF


def chunk_pdf(file_bytes, filename: str):
    """Extracts text from a PDF stream into page-level chunk dictionaries."""
    if isinstance(file_bytes, str):
        file_bytes = file_bytes.encode('utf-8')
    elif hasattr(file_bytes, "getvalue"):
        file_bytes = file_bytes.getvalue()
    elif hasattr(file_bytes, "read"):
        file_bytes = file_bytes.read()

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    chunks = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        if text and text.strip():
            chunks.append({
                "text": text.strip(),
                "metadata": {
                    "source": filename,
                    "page": page_num + 1
                }
            })
            
    doc.close()
    return chunks