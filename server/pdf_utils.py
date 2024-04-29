import ocrmypdf

from langchain_community.document_loaders import PDFPlumberLoader


def perform_ocr(input_pdf: str, output_pdf: str):
    """
    Run OCR on a PDF file.
    This allows PDFs with scanned documents to also be read by text extraction tools.
    """
    ocrmypdf.ocr(
        input_file=input_pdf,
        output_file=output_pdf,
        deskew=True,
        rotate_pages=True,
        force_ocr=True,
        # use_threads=4,  # Not stable on macOS
    )


def extract_text(pdf_path):
    """
    Use PDFPlumber to extract text from a PDF that has undergone OCR correction.
    """
    loader = PDFPlumberLoader(pdf_path)
    pages_data = loader.load()
    pages = {}
    texts = []
    for page_data in pages_data:
        page_number = page_data.metadata["page"]
        pages[page_number] = f"\nPage {page_number}\n" + page_data.page_content
        texts.append(pages[page_number])
    return "\n".join(texts)
