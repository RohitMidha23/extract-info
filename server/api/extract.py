import tempfile

from typing import Optional, Dict, Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from server.extract_info import ExtractResponse, extract_from_pdf
from server.models import DEFAULT_MODEL

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
    json_schema: Optional[Dict[str, Any]] = Form(None),
) -> ExtractResponse:
    """
    Extract structured data from text.
    """
    if file is None:
        raise HTTPException(status_code=422, detail="No PDF file provided.")
    # Save the uploaded file to a temporary file
    temp_path = "temp.pdf"
    with open(temp_path, "wb") as temp:
        contents = await file.read()
        temp.write(contents)

    # with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
    #     contents = await file.read()  # read the entire file
    #     temp.write(contents)
    #     temp_path = temp.name
    print(temp_path)
    return await extract_from_pdf(
        file=temp_path, model_name=model_name, json_schema=json_schema
    )
