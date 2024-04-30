import os
from dotenv import load_dotenv

load_dotenv()

TEMP_DIR = "./tmp/"

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PROMPT_PREFIX = (
    "You are a top-tier algorithm for extracting information from text obtained from OCR run on older PDFs. "
    "This means the data might contain a lot of errors and could even not include the word Troubleshooting explicitly."
    "Only extract information that is relevant to troubleshooting."
    "Output the information with all the relevant fields (for example the column names in a table)."
    "Make sure to output the page number on which the extracted text is found."
    "If no information is relevant, use the schema and output "
    "an empty list where appropriate."
)
