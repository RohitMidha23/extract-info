from typing import Any, Dict, Optional, List
from uuid import uuid4
import os


from fastapi import HTTPException
from jsonschema import Draft202012Validator, exceptions
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain
from langserve import CustomUserType
from pydantic import BaseModel, Field, validator

from server.models import get_model, DEFAULT_MODEL
from server.doctr_utils import perform_ocr, extract_text
from server.validator import validate_json_schema
from server.constants import PROMPT_PREFIX, TEMP_DIR


class ExtractResponse(BaseModel):
    """
    Response body for the extract endpoint.
    Purposely kept losose to allow for flexibility in the response.
    """

    data: List[Dict[str, Any]]


class ExtractRequest(CustomUserType):
    """Request body for the extract endpoint."""

    text: str = Field(..., description="The text to extract from.")
    json_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON schema that describes what content should be extracted "
        "from the text.",
    )
    instructions: Optional[str] = Field(
        None, description="Supplemental system instructions."
    )

    model_name: Optional[str] = Field("gpt-3.5-turbo", description="Chat model to use.")
    if json_schema:

        @validator("json_schema")
        def validate_schema(cls, v: Any) -> Dict[str, Any]:
            """Validate the schema."""
            if v is not None:
                validate_json_schema(v)
            return v


def _make_prompt_template(
    instructions: Optional[str],
) -> ChatPromptTemplate:
    """Make a system message from instructions and examples."""
    prefix = PROMPT_PREFIX
    if instructions:
        system_message = ("system", f"{prefix}\n\n{instructions}")
    else:
        system_message = ("system", prefix)
    prompt_components = [system_message]

    prompt_components.append(
        (
            "human",
            "I need to extract troubleshooting information from "
            "the following text: ```\n{text}\n```\n Output in a JSON and return the relevent page number for each problem solution.",
        ),
    )
    return ChatPromptTemplate.from_messages(prompt_components)


@chain
async def extraction_runnable(extraction_request: ExtractRequest) -> ExtractResponse:
    """An end point to extract content from a given text object."""
    schema = extraction_request.json_schema
    if schema:
        try:
            Draft202012Validator.check_schema(schema)
        except exceptions.ValidationError as e:
            raise HTTPException(status_code=422, detail=f"Invalid schema: {e.message}")

    prompt = _make_prompt_template(
        extraction_request.instructions,
    )
    model = get_model(extraction_request.model_name)
    parser = JsonOutputParser()
    if schema:
        runnable = (prompt | model.with_structured_output(schema=schema)).with_config(
            {"run_name": "extraction"}
        )
    else:
        runnable = (prompt | model).with_config({"run_name": "extraction"}) | parser

    return await runnable.ainvoke({"text": extraction_request.text})


async def extract_from_pdf(
    file: str,
    model_name: Optional[str],
    json_schema: Optional[Dict[str, Any]] = None,
) -> ExtractResponse:
    output_pdf = os.path.join(TEMP_DIR, str(uuid4()) + ".pdf")
    # output_pdf = "temp_ocr.pdf"
    perform_ocr(file, output_pdf)
    if model_name is None:
        model_name = DEFAULT_MODEL

    text = extract_text(output_pdf)
    extract_response = await extraction_runnable.ainvoke(
        ExtractRequest(text=text, json_schema=json_schema, model_name=model_name)
    )
    print(extract_response)
    print(type(extract_response))
    if isinstance(extract_response, dict):
        extract_response = [extract_response]
    response = ExtractResponse(data=extract_response)
    print(extract_response)
    print(type(response))
    return response
