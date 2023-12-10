from openai import OpenAI, AzureOpenAI
import tiktoken
from logic.env_vars import ApiTypeOptions

from logic.user_state import Model

def create_client(model: Model) -> OpenAI:
    if model.api_type == ApiTypeOptions.AZURE.value:
        return AzureOpenAI(api_key=model.api_key, 
                           azure_endpoint=model.api_base, 
                           api_version=model.api_version,
                           azure_deployment=model.name)
    else:
        return OpenAI(api_key=model.api_key)

encoding = tiktoken.get_encoding("cl100k_base")

def num_tokens_from_messages(messages: list[dict]) -> int:
    """Return the number of tokens used by a list of messages."""

    if not messages: return 0

    tokens_per_message: int = 4  # every message follows <|im_start|>{role/name}\n{content}<|end|>\n
    tokens_per_name: int = -1  # if there's a name, the role is omitted

    num_tokens: int = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|im_start|>assistant<|im_sep|>
    return num_tokens