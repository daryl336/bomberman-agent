from dataclasses import dataclass
from agents.model_settings import ModelSettings, Reasoning
from pydantic import BaseModel
from typing import List, Dict, Literal
import aiohttp
import asyncio
import openai
import azure.core.exceptions

BATCH_SIZE = 20
BASE_BACKOFF = 5  # seconds
MAX_RETRIES=5
RETRY_DELAY_SECONDS=5
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
RETRYABLE_EXCEPTIONS = (
    openai.RateLimitError,
    openai.InternalServerError,
    openai.APIError,
    aiohttp.ClientError,
    asyncio.TimeoutError,
    ConnectionResetError,
    BrokenPipeError,
    azure.core.exceptions.HttpResponseError,
    azure.core.exceptions.ServiceRequestError,
)
MAX_SLEEP = 60

class MyAgentSettings(ModelSettings):
    normal_setting = ModelSettings(temperature=0)
    formatting_setting = ModelSettings(temperature=0, tool_choice="required")
    routing_setting = ModelSettings(temperature=0, parallel_tool_calls=True, tool_choice="required")
    tool_use_required_setting = ModelSettings(temperature=0, tool_choice="required")
    tool_use_parallel_required_setting = ModelSettings(temperature=0, tool_choice="required")
    tool_use_auto_setting = ModelSettings(temperature=0, tool_choice="auto")
    retrieval_setting = ModelSettings(temperature=0, tool_choice="required")
    
    reasoning_low_setting = ModelSettings(reasoning=Reasoning(effort="low"))
    reasoning_medium_setting = ModelSettings(reasoning=Reasoning(effort="medium", summary="auto"))
    reasoning_high_setting = ModelSettings(reasoning=Reasoning(effort="high"))
    
    tool_use_auto_reasoning_low_setting = ModelSettings(tool_choice="auto", reasoning=Reasoning(effort="low"))
    tool_use_auto_reasoning_medium_setting = ModelSettings(tool_choice="auto", reasoning=Reasoning(effort="medium"))
    tool_use_auto_reasoning_high_setting = ModelSettings(tool_choice="auto", reasoning=Reasoning(effort="high"))
    
    tool_use_required_reasoning_low_setting = ModelSettings(tool_choice="required", reasoning=Reasoning(effort="low"))
    tool_use_required_reasoning_medium_setting = ModelSettings(tool_choice="required", reasoning=Reasoning(effort="medium"))
    tool_use_required_reasoning_high_setting = ModelSettings(tool_choice="required", reasoning=Reasoning(effort="high"))
    
    tool_use_parallel_required_reasoning_low_setting = ModelSettings(tool_choice="required", reasoning=Reasoning(effort="low"))
    tool_use_parallel_required_reasoning_medium_setting = ModelSettings(tool_choice="required", reasoning=Reasoning(effort="medium"))
    tool_use_parallel_required_reasoning_high_setting = ModelSettings(tool_choice="required", reasoning=Reasoning(effort="high"))