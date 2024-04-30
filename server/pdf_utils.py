import os
from multiprocessing import Pool, cpu_count

import ocrmypdf
import pdfplumber
from langchain_community.document_loaders import PDFPlumberLoader
from PIL import Image
from server.constants import TEMP_DIR
from server.DE_GAN.enhance import enhance_image


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


def convert_pdf_to_images(pdf_path, output_dir, debug=False):
    """
    Convert PDF pages to images for further processing.
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            im = page.to_image()

            # Save the image as a PNG
            im_path = os.path.join(output_dir, f"page_{i+1}.png")
            im.save(im_path, format="PNG")
            if debug:
                print(f"Saved {im_path}")
            image_paths.append(im_path)
    return image_paths


def process_image_page(image):
    """
    Use DE-GAN to enhance the image.
    """
    image_name = image.split("/")[-1]
    return enhance_image("deblur", image, TEMP_DIR, image_name)


def process_images_with_multiprocessing(image_paths):
    """Process images in parallel using multiprocessing."""
    with Pool(cpu_count()) as pool:
        processed_images = pool.imap_unordered(process_image_page, image_paths)
    return image_paths


def images_to_pdf(image_paths, output_pdf_path):
    """
    Convert the processed images (from file paths) back to a single PDF file.
    """
    # Open the first image to create the initial PDF
    with Image.open(image_paths[0]) as img:
        img = img.convert("RGB")  # Convert the first image to RGB to start the PDF
        img_list = []

        # Process the rest of the images
        for image_path in image_paths[1:]:
            with Image.open(image_path) as img_file:
                img_list.append(img_file.convert("RGB"))

        # Save all images into a PDF file
        img.save(output_pdf_path, save_all=True, append_images=img_list)
        print(f"PDF processing complete. Saved to: {output_pdf_path}")
