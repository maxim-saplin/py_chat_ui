from openai import OpenAI, AzureOpenAI
import os
from dotenv import load_dotenv
import tiktoken

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
api_type = os.environ.get("API_TYPE")
api_version = os.environ.get("API_VERSION")
api_base = os.environ.get("OPENAI_API_BASE")
model = os.environ.get("MODEL")
temperature = float(os.environ.get("TEMPERATURE"))

def get_client():
    return AzureOpenAI(api_key=api_key, 
                     azure_endpoint=api_base, 
                     api_version=api_version,
                     azure_deployment=model) if api_type == "azure" else OpenAI(api_key=api_key)

encoding = tiktoken.get_encoding("cl100k_base")

def num_tokens_from_messages(messages):
    """Return the number of tokens used by a list of messages."""

    if not messages: return 0

    tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
    tokens_per_name = -1  # if there's a name, the role is omitted

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
