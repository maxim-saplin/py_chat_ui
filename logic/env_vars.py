from dotenv import load_dotenv
import os
from enum import Enum

load_dotenv()

MODELS_FILE_NAME: str = "models.dat"
CHATS_FOLDER: str = "chats"

class ApiTypeOptions(Enum):
    AZURE = 'Azure'
    OPENAI = 'OpenAI'
    FAKE = 'Fake'

env_api_key: str | None = os.environ.get("OPENAI_API_KEY")
match os.environ.get("API_TYPE", "Fake").upper():
    case "AZURE":
        env_api_type: ApiTypeOptions = ApiTypeOptions.AZURE
    case "OPENAI":
        env_api_type: ApiTypeOptions = ApiTypeOptions.OPENAI
    case "FAKE":
        env_api_type: ApiTypeOptions = ApiTypeOptions.FAKE
    case _:
        None
env_api_version: str | None = os.environ.get("API_VERSION")
env_api_base: str | None = os.environ.get("OPENAI_API_BASE")
env_model_alias: str | None = os.environ.get("ALIAS")
env_model_name: str | None = os.environ.get("MODEL")
env_temperature: float = float(os.environ.get("TEMPERATURE", "0.0"))
env_data_folder: str = os.getenv("DATA_DIR", ".data")
env_disable_auth: bool = os.environ.get("DISABLE_AUTH", "True").lower() == "true"
