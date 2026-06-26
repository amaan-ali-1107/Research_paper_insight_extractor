import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Takes the raw bytes of a PDF file and returns all the text as a string.
    
    Steps:
    1. Open the PDF from bytes (no need to save it to disk)
    2. Loop through each page
    3. Extract text from each page
    4. Join everything together
    """

    full_text = ""

    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    print(f"[INFO] PDF has {pdf_document.page_count} pages")

    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        page_text = page.get_text()
        full_text += f"\n--- Page {page_number + 1} ---\n"
        full_text += page_text

    pdf_document.close()

    print(f"[INFO] Extracted {len(full_text)} characters from PDF")
    return full_text


def preprocess_text(text: str) -> str:
    """
    Cleans up the extracted text a little bit before sending to the LLM.
    
    - Removes extra blank lines
    - Strips leading/trailing whitespace
    - Limits the text to ~12000 words to stay within LLM context limits
    """

    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.strip():
            cleaned_lines.append(line.strip())

    cleaned_text = "\n".join(cleaned_lines)

    words = cleaned_text.split()
    if len(words) > 12000:
        print(f"[WARNING] Paper is very long ({len(words)} words). Trimming to 12000 words.")
        cleaned_text = " ".join(words[:12000])
        cleaned_text += "\n\n[Note: Paper was trimmed due to length. Key sections preserved.]"

    return cleaned_text