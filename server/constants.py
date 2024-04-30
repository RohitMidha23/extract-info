import os
from dotenv import load_dotenv

load_dotenv()

TEMP_DIR = "./tmp/"

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
