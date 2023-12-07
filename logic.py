from openai import OpenAI, AzureOpenAI
import os
from enum import Enum
from dotenv import load_dotenv
import tiktoken
import pickle

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

class Model:
    def __init__(self, name, api_key, api_type, api_version, api_base, temperature):
        self.name = name
        self.api_key = api_key
        self.api_type = api_type
        self.api_version = api_version
        self.api_base = api_base
        self.temperature = temperature

class ModelRepository:
    def __init__(self):
        self.models = []
        if env_model:
            self.models.append(Model('(env) ' + env_model, env_api_key, env_api_type, env_api_version, env_api_base, env_temperature))

    def load(self):
        try:
            with open('models.dat', 'rb') as f:
                self.models = pickle.load(f)
        except FileNotFoundError:
            pass

    def add(self, model):
        self.models.append(model)
        self.save()

    def delete(self, model_name):
        self.models = [model for model in self.models if model.name != model_name]
        self.save()

    def update(self, model):
        for i, m in enumerate(self.models):
            if m.name == model.name:
                self.models[i] = model
                break
        self.save()

    def list(self):
        return [model.name for model in self.models]

    def save(self):
        with open('models.dat', 'wb') as f:
            pickle.dump(self.models, f)

model_repository = ModelRepository()
model_repository.load()


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
