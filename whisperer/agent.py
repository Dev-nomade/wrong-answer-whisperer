"""Builds the Strands agent backed by Amazon Bedrock."""

import os

from strands import Agent
from strands.models import BedrockModel

from .prompts import SYSTEM_PROMPT
from .tools import log_mistake, my_weak_spots

DEFAULT_MODEL_ID = "us.amazon.nova-lite-v1:0"
DEFAULT_REGION = "us-east-1"


def _print_stream(**kwargs) -> None:
    """Print only the model's text as it streams (hides internal tool chatter)."""
    text = kwargs.get("data")
    if text:
        print(text, end="", flush=True)


def build_agent() -> Agent:
    model = BedrockModel(
        model_id=os.environ.get("WHISPERER_MODEL_ID", DEFAULT_MODEL_ID),
        region_name=os.environ.get("AWS_REGION", DEFAULT_REGION),
        temperature=0.3,  # consistent explanations, still natural
        max_tokens=900,
    )
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[log_mistake, my_weak_spots],
        callback_handler=_print_stream,
    )
