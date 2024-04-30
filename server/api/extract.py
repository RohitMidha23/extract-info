import tempfile
import os
from typing import Optional, Dict, Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from server.extract_info import ExtractResponse, extract_from_pdf
from server.models import DEFAULT_MODEL
from server.constants import TEMP_DIR

router = APIRouter(
    prefix="/extract",
    tags=["extract"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=ExtractResponse)
async def extract(
    *,
    file: UploadFile = File(None),
    model_name: Optional[str] = Form(DEFAULT_MODEL),
) -> ExtractResponse:
    """
    Extract structured data from text.
    """
    if file is None:
        raise HTTPException(status_code=422, detail="No PDF file provided.")
    # Save the uploaded file to a temporary file
    temp_path = os.path.join(TEMP_DIR, "temp.pdf")
    with open(temp_path, "wb") as temp:
        contents = await file.read()
        temp.write(contents)

    return await extract_from_pdf(file=temp_path, model_name=model_name)
