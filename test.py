import ocrmypdf
from server.extract_info import ExtractResponse


def perform_ocr(input_pdf: str, output_pdf: str):
    """
    Run OCR on a PDF file.
    This allows PDFs with scanned documents to also be read by text extraction tools.
    """
    ocrmypdf.ocr(
        input_pdf,
        "output.pdf",
        deskew=True,
        rotate_pages=True,
        force_ocr=True,
        use_threads=4,
    )


def main() -> ExtractResponse:
    response = [
        {
            "Page": 2,
            "Troubleshooting Information": [
                {
                    "Issue": "Risk of electrical shock or unsupervised usage",
                    "Solution": "Always remove the batteries from the machine and wait 5 minutes before cleaning, maintaining, or repairing the machine.",
                },
                {
                    "Issue": "Machine examination before each use",
                    "Solution": "Examine the machine for loose parts or signs of wear before each use. Do not use if found in this condition.",
                },
                {
                    "Issue": "Maximum user weight limit exceeded",
                    "Solution": "Do not use the machine if you are over 300 lbs (136 kg).",
                },
                {
                    "Issue": "Loose clothing or jewelry",
                    "Solution": "Do not wear loose clothing or jewelry while using the machine.",
                },
                {
                    "Issue": "Machine setup and operation",
                    "Solution": "Set up and operate the machine on a solid, level horizontal surface.",
                },
                {
                    "Issue": "Machine usage precautions",
                    "Solution": "Use caution when stepping on and off the machine. Use the supplied foot support platforms for stability.",
                },
            ],
        },
        {
            "Page": 3,
            "Troubleshooting Information": [
                {
                    "Issue": "Object lodged between treadles",
                    "Solution": "Manually move the treadles to release the object by pushing downward on the foot rail or walk belt of the lowest treadle.",
                },
                {
                    "Issue": "Machine storage and usage",
                    "Solution": "Do not operate the machine outdoors or in moist or wet locations. Keep a safe distance around the machine for access and emergency dismounts.",
                },
                {
                    "Issue": "Maintenance and safety precautions",
                    "Solution": "Perform regular maintenance procedures, keep the walking belt clean and dry, and keep batteries away from heat sources.",
                },
            ],
        },
        {
            "Page": 20,
            "Troubleshooting Information": [
                {
                    "Issue": "Moving the machine to a new location",
                    "Solution": "Use the transport wheels to move the machine slowly into its new location without causing injury.",
                }
            ],
        },
        {
            "Page": 23,
            "Troubleshooting Information": [
                {
                    "Issue": "Walking belt lubrication",
                    "Solution": "Periodically lubricate the walking belts with silicone lubricant following the provided instructions.",
                }
            ],
        },
        {
            "Page": 28,
            "Troubleshooting Information": [
                {
                    "Issue": "Reducing static charge on walking belts",
                    "Solution": "Apply an anti-static spray to the walking belts to reduce static electric charges.",
                }
            ],
        },
    ]
    response = ExtractResponse(data=response)
    print(type(response))
    return response


if __name__ == "__main__":
    # perform_ocr("temp.pdf", "output.pdf")
    x = main()
