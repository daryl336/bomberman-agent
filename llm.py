import os
import re
import json
import httpx
from openai import AzureOpenAI, AsyncAzureOpenAI
import openai
import time

use_apim = os.environ.get('USE_APIM')
print("USE APIM : ",use_apim)

def extract_json(string):
    string = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', string)
    string = re.sub(r'(?<!\\)"((?:\\.|[^"\\])*)"', lambda m: '"{}"'.format(m.group(1).replace('\n', '\\n')), string) ## prevents multi-line responses
    start_index = string.find('{')
    end_index = string.rfind('}')
    final = string[start_index:end_index + 1]
    final = json.loads(final)
    return final

def extract_eval_json(string):
    if type(string)!=dict:
        try:
            final = extract_json(string)
        except:
            final = eval(string)
    else:
        final = string
    return final

if use_apim.lower() == 'true':
    print("Loading APIM")
    client = AzureOpenAI(
        api_key = os.environ.get("OPENAI_APIM_KEY"),
        azure_endpoint = os.environ.get("OPENAI_APIM_ENDPOINT"),
        api_version = os.environ.get("OPENAI_API_VERSION"),
        timeout=int(os.environ.get("TIMEOUT")),
        http_client=httpx.Client(
            verify=os.environ.get('REQUESTS_CA_BUNDLE')
        )
    )

    a_client = AsyncAzureOpenAI(
        api_key = os.environ.get("OPENAI_APIM_KEY"),
        azure_endpoint = os.environ.get("OPENAI_APIM_ENDPOINT"),
        api_version = os.environ.get("OPENAI_API_VERSION"),
        timeout=int(os.environ.get("TIMEOUT")),
        http_client=httpx.AsyncClient(
            verify=os.environ.get('REQUESTS_CA_BUNDLE')
        )
    )
    a_client_reasoning = AsyncAzureOpenAI(
        api_key = os.environ.get("OPENAI_API_DEV_KEY"),
        azure_endpoint = os.environ.get("OPENAI_API_DEV_ENDPOINT"),
        api_version = os.environ.get("OPENAI_API_VERSION"),
        timeout=int(os.environ.get("TIMEOUT")),
        http_client=httpx.AsyncClient(
            verify=os.environ.get('REQUESTS_CA_BUNDLE')
        )
    )
    a_client_eu2_prod = AsyncAzureOpenAI(
        api_key = os.environ.get("GPT5_KEY"),
        azure_endpoint = os.environ.get("GPT5_ENDPOINT"),
        api_version = os.environ.get("OPENAI_API_VERSION"),
        timeout=int(os.environ.get("TIMEOUT")),
        http_client=httpx.AsyncClient(
            verify=os.environ.get('REQUESTS_CA_BUNDLE')
        )
    )
else:
    client = AzureOpenAI(
        api_key = os.environ.get("OPENAI_API_KEY"),
        azure_endpoint = os.environ.get("OPENAI_API_ENDPOINT"),
        api_version = os.environ.get("OPENAI_API_VERSION"),
        timeout=int(os.environ.get("TIMEOUT")),
        http_client=httpx.Client(
            verify=os.environ.get('REQUESTS_CA_BUNDLE')
        )
    )
    a_client = AsyncAzureOpenAI(
        api_key = os.environ.get("OPENAI_API_KEY"),
        azure_endpoint = os.environ.get("OPENAI_API_ENDPOINT"),
        api_version = os.environ.get("OPENAI_API_VERSION"),
        timeout=int(os.environ.get("TIMEOUT")),
        http_client=httpx.AsyncClient(
            verify=os.environ.get('REQUESTS_CA_BUNDLE')
        )
    )
    a_client_reasoning = AsyncAzureOpenAI(
        api_key = os.environ.get("OPENAI_API_DEV_KEY"),
        azure_endpoint = os.environ.get("OPENAI_API_DEV_ENDPOINT"),
        api_version = os.environ.get("OPENAI_API_VERSION"),
        timeout=int(os.environ.get("TIMEOUT")),
        http_client=httpx.AsyncClient(
            verify=os.environ.get('REQUESTS_CA_BUNDLE')
        )
    )
    a_client_eu2_prod = AsyncAzureOpenAI(
        api_key = os.environ.get("GPT5_KEY"),
        azure_endpoint = os.environ.get("GPT5_ENDPOINT"),
        api_version = os.environ.get("OPENAI_API_VERSION"),
        timeout=int(os.environ.get("TIMEOUT")),
        http_client=httpx.AsyncClient(
            verify=os.environ.get('REQUESTS_CA_BUNDLE')
        )
    )
