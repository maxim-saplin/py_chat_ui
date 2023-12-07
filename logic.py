from openai import OpenAI, AzureOpenAI
import os
from enum import Enum
from dotenv import load_dotenv
import tiktoken

load_dotenv()

class ApiTypeOptions(Enum):
    AZURE = 'Azure'
    OPENAI = 'OpenAI'

env_api_key = os.environ.get("OPENAI_API_KEY")
env_api_type = os.environ.get("API_TYPE")
if env_api_type not in ApiTypeOptions.__members__:
    env_api_type = ApiTypeOptions.AZURE.value
else:
    env_api_type = ApiTypeOptions[env_api_type].value
env_api_version = os.environ.get("API_VERSION")
env_api_base = os.environ.get("OPENAI_API_BASE")
env_model = os.environ.get("MODEL")
env_temperature = float(os.environ.get("TEMPERATURE"))

def get_client():
    return AzureOpenAI(api_key=env_api_key, 
                     azure_endpoint=env_api_base, 
                     api_version=env_api_version,
                     azure_deployment=env_model) if env_api_type == "azure" else OpenAI(api_key=env_api_key)

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
