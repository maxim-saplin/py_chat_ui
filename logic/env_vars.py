from dotenv import load_dotenv
import os
from enum import Enum

load_dotenv()

MODELS_FILE_NAME: str = 'models.dat'
CHATS_FOLDER: str = 'chats'


class ApiTypeOptions(Enum):
    AZURE = 'Azure'
    OPENAI = 'OpenAI'
    FAKE = 'Fake'
    EMPTY = 'Empty'

class ApiTypeOptions(Enum):
    AZURE = 'Azure'
    OPENAI = 'OpenAI'
    FAKE = 'Fake'
    EMPTY = 'Empty'

    @classmethod
    def from_string(cls, api_type_str: str):
        for member in cls:
            if member.value == api_type_str:
                return member
        return None

class TokenizerKind(Enum):
    CL100K_BASE = 'cl100k_base'
    O200K_BASE = 'o200k_base'

    @classmethod
    def from_string(cls, api_type_str: str):
        for member in cls:
            if member.value == api_type_str:
                return member
        return None


match os.environ.get('API_TYPE', 'Fake').upper():
    case 'AZURE':
        env_api_type: ApiTypeOptions = ApiTypeOptions.AZURE
    case 'OPENAI':
        env_api_type: ApiTypeOptions = ApiTypeOptions.OPENAI
    case 'FAKE':
        env_api_type: ApiTypeOptions = ApiTypeOptions.FAKE
    case 'EMPTY':
        env_api_type: ApiTypeOptions = ApiTypeOptions.EMPTY
    case _:
        None
env_model_alias: str | None = os.environ.get(
    'ALIAS',
    'Fake auto-reply model (demonstration)'
    if env_api_type == ApiTypeOptions.FAKE else '(env)')
env_api_key: str | None = 'Fake' if env_api_type == ApiTypeOptions.FAKE else os.environ.get('OPENAI_API_KEY')
env_api_version: str | None = 'Fake' if env_api_type == ApiTypeOptions.FAKE else os.environ.get('API_VERSION')
env_api_base: str | None = 'Fake' if env_api_type == ApiTypeOptions.FAKE else os.environ.get('OPENAI_API_BASE')
env_model_name: str | None = 'Fake' if env_api_type == ApiTypeOptions.FAKE else os.environ.get('MODEL')
env_temperature: float = float(os.environ.get('TEMPERATURE', '0.7'))
env_data_folder: str = os.getenv('DATA_DIR', '.data')
env_disable_auth: bool = os.environ.get('DISABLE_AUTH', 'True').lower() == 'true'
env_disable_user_registration: bool = os.environ.get('DISBLE_USER_REG', 'False').lower() == 'true'


def print_debug():
    print(f"MODELS_FILE_NAME: {MODELS_FILE_NAME}")
    print(f"CHATS_FOLDER: {CHATS_FOLDER}")
    print(f"env_api_type: {env_api_type}")
    print(f"env_model_alias: {env_model_alias}")
    print(f"env_api_key: {env_api_key}")
    print(f"env_api_version: {env_api_version}")
    print(f"env_api_base: {env_api_base}")
    print(f"env_model_name: {env_model_name}")
    print(f"env_temperature: {env_temperature}")
    print(f"env_data_folder: {env_data_folder}")
    print(f"env_disable_auth: {env_disable_auth}")
    print(f"env_disable_user_registration: {env_disable_user_registration}")


def reset_env_to_default(**kwargs):
    global env_api_type
    global env_model_alias
    global env_api_key
    global env_api_version
    global env_api_base
    global env_model_name
    global env_temperature
    global env_data_folder
    global env_disable_auth
    global env_disable_user_registration

    env_api_type = kwargs.get('env_api_type', ApiTypeOptions.FAKE)
    env_model_alias = kwargs.get('env_model_alias', 'Fake auto-reply model (demonstration)')
    env_api_key = kwargs.get('env_api_key', 'Fake')
    env_api_version = kwargs.get('env_api_version', 'Fake')
    env_api_base = kwargs.get('env_api_base', 'Fake')
    env_model_name = kwargs.get('env_model_name', 'Fake')
    env_temperature = float(kwargs.get('env_temperature', 0.7))
    env_data_folder = kwargs.get('env_data_folder', '.data')
    env_disable_auth = kwargs.get('env_disable_auth', True)
    env_disable_user_registration = kwargs.get('env_disable_user_registration', False)


def override_value(**kwargs):
    for key, value in kwargs.items():
        if key in globals():
            globals()[key] = value
