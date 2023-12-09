from openai import OpenAI, AzureOpenAI
import os
import datetime
import tiktoken
import pickle
import glob
from env_vars import *

user_dir: str = None;

class Model:
    def __init__(self, name: str, api_key: str, api_type: str, api_version: str, api_base: str, temperature: float, is_env: bool = False):
        self.name: str = name
        self.api_key: str = api_key
        self.api_type: str = api_type
        self.api_version: str = api_version
        self.api_base: str = api_base
        self.temperature: float = temperature
        self.is_env: bool = is_env

class ModelRepository:
    def __init__(self):
        self.models: list[Model] = []
        self.last_used_model: str = ""

    def load(self) -> None:
        try:
            with open(os.path.join(env_data_folder, user_dir, MODELS_FILE_NAME), 'rb') as f:
                self.models, self.last_used_model = pickle.load(f)
        except FileNotFoundError:
            pass

    def add_env(self, env_model: str, env_api_key: str, env_api_type: str, env_api_version: str, env_api_base: str, env_temperature: float) -> None:
        model = Model(env_model, env_api_key, env_api_type, env_api_version, env_api_base, env_temperature, True)
        self.models.append(model)

    def add(self, model: Model) -> None:
        self.models.append(model)
        self.save()

    def get_model_by_name(self, model_name: str) -> Model | None:
        for model in self.models:
            if model.name == model_name:
                return model
        return None
    
    def get_last_used_model(self) -> Model | None:
        if self.last_used_model and self.get_model_by_name(self.last_used_model):
            return self.get_model_by_name(self.last_used_model)
        elif self.models:
            return self.models[0]
        return None
    
    def set_last_used_model(self, model_name: str) -> None:
        self.last_used_model = model_name
        self.save()

    def delete(self, model_name: str) -> None:
        self.models = [model for model in self.models if model.name != model_name]
        self.save()

    def update(self, model: Model) -> None:
        for i, m in enumerate(self.models):
            if m.name == model.name:
                self.models[i] = model
                break
        self.save()

    def list(self) -> list[str]:
        return [model.name for model in self.models]

    def save(self) -> None:
        with open(os.path.join(env_data_folder, user_dir, MODELS_FILE_NAME), 'wb') as f:
            pickle.dump((self.models, self.last_used_model), f)

class ChatSession:
    def __init__(self, session_id: int, model: Model, title: str):
        assert user_dir is not None, "user_dir must not be null"
        self.session_id: int = session_id
        self.model: Model = model
        self.title: str = title
        self.start_date: datetime.datetime = datetime.datetime.now()
        self.messages: list[dict] = []
        base_file_path = os.path.join(env_data_folder, user_dir, CHATS_FOLDER, f"{self.start_date.strftime('%Y%m%d%H%M%S%f')}_{self.session_id}")
        self.file_path: str = f"{base_file_path}.pkl"
        self.messages_file_path: str = f"{base_file_path}_messages.pkl"
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_message(self, message: dict) -> None:
        self.messages.append(message)  # Append the new message to the messages list
        self.save_message(message)

    def save_message(self, message: dict) -> None:
        if not os.path.exists(self.file_path):
            self.save()
        with open(self.messages_file_path, 'ab') as f:
            pickle.dump((datetime.datetime.now(), message), f)

    def save(self) -> None:
        with open(self.file_path, 'wb') as f:
            data = {
                'session_id': self.session_id,
                'model_name': self.model.name,
                'title': self.title,
                'start_date': self.start_date
            }
            pickle.dump(data, f)

    @classmethod
    def from_file(cls, file_path: str, model_repository: ModelRepository) -> 'ChatSession':
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            model_name = data['model_name']
            model = model_repository.get_model_by_name(model_name)
            if model is None:
                model = model_repository.last_used_model
            chat_session = cls(data['session_id'], model, data['title'])
            chat_session.start_date = data['start_date']
            chat_session.file_path = file_path
            messages_file_path = f"{os.path.splitext(file_path)[0]}_messages.pkl"
            if os.path.exists(messages_file_path):
                with open(messages_file_path, 'rb') as mf:
                    while True:
                        try:
                            _, message = pickle.load(mf)
                            chat_session.messages.append(message)
                        except EOFError:
                            break
            chat_session.messages_file_path = messages_file_path
            return chat_session

class ChatSessionManager:
    def __init__(self):
        assert user_dir is not None, "user_dir must be set before initializing ChatSessionManager"
        self.sessions: list[ChatSession] = []
        self.load_sessions()

    def create_session(self, model: Model, title: str) -> ChatSession:
        session_id = max(self.sessions, key=lambda s: s.session_id).session_id + 1 if self.sessions else 1
        session = ChatSession(session_id, model, title)
        self.sessions.append(session)
        return session

    def list_sessions(self) -> list[ChatSession]:
        return sorted(self.sessions, key=lambda s: s.start_date, reverse=True)
    
    def get_session_by_id(self, session_id: int) -> ChatSession | None:
        for session in self.sessions:
            if session.session_id == session_id:
                return session
        return None

    def load_sessions(self) -> None:
        chat_files = glob.glob(os.path.join(env_data_folder, user_dir, CHATS_FOLDER, "*.pkl"))
        for file_path in chat_files:
            if not file_path.endswith("_messages.pkl"):
                try:
                    session = ChatSession.from_file(file_path, model_repository)
                    self.sessions.append(session)
                except (EOFError, pickle.UnpicklingError):
                    continue
    def delete(self, session_id: int) -> None:
        session = self.get_session_by_id(session_id)
        if session:
            self.sessions.remove(session)
            if os.path.exists(session.file_path):
                os.remove(session.file_path)
            if os.path.exists(session.messages_file_path):
                os.remove(session.messages_file_path)

def create_client(model: Model) -> OpenAI | AzureOpenAI:
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



model_repository: ModelRepository = None;
session_manager: ChatSessionManager = None

def init(user_direrctory: str) -> None:
    global user_dir
    global model_repository
    global session_manager
    if not user_direrctory.isidentifier():
        raise ValueError("Invalid user directory name; It must start with a letter (a-z, A-Z) or an underscore () and can be followed by any number of letters, digits (0-9), or underscores")
    user_dir = user_direrctory
    model_repository = ModelRepository()
    if env_model_name:
        model_repository.add_env(env_model_name, env_api_key, env_api_type, env_api_version, env_api_base, env_temperature)
    model_repository.load()
    session_manager = ChatSessionManager()


# def is_init() -> bool:
#     """Check if the system has been initialized."""
#     return user_dir is not None and model_repository is not None and session_manager is not None

# def reset() -> None:
#     """Reset the global variables to their default state, e.g., when a logout happens."""
#     global user_dir
#     user_dir = None
#     model_repository = None
#     session_manager = None