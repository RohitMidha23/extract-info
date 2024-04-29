import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_supported_models():
    """Get models according to environment secrets."""
    models = {}
    if "OPENAI_API_KEY" in os.environ:
        models["gpt-3.5-turbo"] = {
            "chat_model": ChatOpenAI(
                model="gpt-3.5-turbo", temperature=0, api_key=OPENAI_API_KEY
            ),
            "description": "The latest GPT-3.5 Turbo.",
        }

        models["gpt-4-turbo"] = {
            "chat_model": ChatOpenAI(
                model="gpt-4-turbo", temperature=0, api_key=OPENAI_API_KEY
            ),
            "description": "The latest GPT-4 Turbo model with vision capabilities.",
        }

    return models


SUPPORTED_MODELS = get_supported_models()
DEFAULT_MODEL = "gpt-3.5-turbo"


def get_model(model_name: Optional[str] = None) -> BaseChatModel:
    """Get the model."""
    if model_name is None:
        return SUPPORTED_MODELS[DEFAULT_MODEL]["chat_model"]
    else:
        supported_model_names = list(SUPPORTED_MODELS.keys())
        if model_name not in supported_model_names:
            raise ValueError(
                f"Model {model_name} not found. "
                f"Supported models: {supported_model_names}"
            )
        else:
            return SUPPORTED_MODELS[model_name]["chat_model"]
