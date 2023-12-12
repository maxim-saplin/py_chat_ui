import os
import datetime
import pickle
import glob
from cryptography.fernet import InvalidToken
from logic.crypto import *
from logic.env_vars import *

# Current users home holder to store all data, must be set
user_dir: str = None
# Encryption key used to encrypt/decryp all user data coming to/from disk
encryption_key: bytes = None

class Model:
    def __init__(self, alias: str, deployment_name: str, api_key: str, api_type: ApiTypeOptions, api_version: str, api_base: str, temperature: float, is_env: bool = False):
        self.alias: str = alias
        self.model_or_deployment_name: str = deployment_name
        self.api_key: str = api_key
        self.api_type: ApiTypeOptions = api_type
        self.api_version: str = api_version
        self.api_base: str = api_base
        self.temperature: float = temperature
        self.is_env: bool = is_env

class ModelRepository:
    def __init__(self):
        self.models: list[Model] = []
        self.last_used_model: str = ""
        self.last_used_deployment: str = ""

    def load(self) -> None:
        try:
            with open(os.path.join(env_data_folder, user_dir, MODELS_FILE_NAME), 'rb') as f:
                encrypted_data = f.read()
                self.models, self.last_used_model, self.last_used_deployment = pickle.loads(decrypt_data(encrypted_data, encryption_key))
        except FileNotFoundError:
            pass
        except InvalidToken:
            raise Exception("Failed to decrypt the model data. The encryption key may be incorrect or the data is corrupted.")

    def add_env(self, env_model_alias: str, env_deployment_name: str, env_api_key: str, env_api_type: str, env_api_version: str, env_api_base: str, env_temperature: float) -> None:
        if not any(model.alias == env_model_alias for model in self.models):
            model = Model(env_model_alias, env_deployment_name, env_api_key, env_api_type, env_api_version, env_api_base, env_temperature, True)
            self.models.append(model)
            self.save()

    def add(self, model: Model) -> None:
        self.models.append(model)
        self.save()

    def get_model_by_alias(self, model_alias: str) -> Model | None:
        for model in self.models:
            if model.alias == model_alias:
                return model
        return None
    
    def get_last_used_model(self) -> Model | None:
        if self.last_used_model and self.get_model_by_alias(self.last_used_model):
            return self.get_model_by_alias(self.last_used_model)
        elif self.models:
            return self.models[0]
        return None
    
    def set_last_used_model(self, model_alias: str) -> None:
        self.last_used_model = model_alias
        self.save()

    def delete(self, model_alias: str) -> None:
        self.models = [model for model in self.models if model.alias != model_alias]
        if self.last_used_model == model_alias:
            self.last_used_model = ""
            self.last_used_deployment = ""
        self.save()

    def update(self, model: Model) -> None:
        for i, m in enumerate(self.models):
            if m.alias == model.alias:
                self.models[i] = model
                break
        self.save()

    def list(self) -> list[str]:
        return [model.alias for model in self.models]

    def save(self) -> None:
        os.makedirs(os.path.join(env_data_folder, user_dir), exist_ok=True)
        with open(os.path.join(env_data_folder, user_dir, MODELS_FILE_NAME), 'wb') as f:
            encrypted_data = encrypt_data(pickle.dumps((self.models, self.last_used_model, self.last_used_deployment)), encryption_key)
            f.write(encrypted_data)

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
            message_data = pickle.dumps((datetime.datetime.now(), message))
            encrypted_data = encrypt_data(message_data, encryption_key)
            # Prepend the length of the encrypted data as a 4-byte integer
            f.write(len(encrypted_data).to_bytes(4, 'big'))
            f.write(encrypted_data)

    def save(self) -> None:
        with open(self.file_path, 'wb') as f:
            data = {
                'session_id': self.session_id,
                'model_alias': self.model.alias,
                'title': self.title,
                'start_date': self.start_date
            }
            encrypted_data = encrypt_data(pickle.dumps(data), encryption_key)
            f.write(encrypted_data)

    @classmethod
    def from_file(cls, file_path: str, model_repository: ModelRepository) -> 'ChatSession':
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
                data = pickle.loads(decrypt_data(encrypted_data, encryption_key))
                model_alias = data['model_alias']
                model = model_repository.get_model_by_alias(model_alias)
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
                                # Read the length of the encrypted message
                                length_bytes = mf.read(4)
                                if not length_bytes:
                                    break  # No more messages
                                length = int.from_bytes(length_bytes, 'big')
                                # Now read the exact length of the message
                                encrypted_message_data = mf.read(length)
                                _, message = pickle.loads(decrypt_data(encrypted_message_data, encryption_key))
                                chat_session.messages.append(message)
                            except EOFError:
                                break
                            except Exception as e:
                                raise e
                chat_session.messages_file_path = messages_file_path
                return chat_session
        except InvalidToken:
            # Handle the case where the session data cannot be decrypted
            raise ValueError("Unable to decrypt the session data. The encryption key may be incorrect or the data is corrupted.")

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

model_repository: ModelRepository = None
session_manager: ChatSessionManager = None

def init(username: str, enc_key) -> None:
    global user_dir
    global encryption_key
    global model_repository
    global session_manager
    import re

    # Define a function to escape the username to be used as a valid folder name
    def escape_username(username: str) -> str:        
        return re.sub(r"[^a-zA-Z0-9_-]", "_", username)

    if not re.match(r"^[a-zA-Z0-9_-]{1,20}$", username) and not ("@" in username and 2 < len(username) < 320):
        raise ValueError("Invalid username; it must be a valid string with 1-20 characters, or a valid email address.")
    if not enc_key:
        raise ValueError("Encryption key is not set.")
    user_dir = escape_username(username)
    encryption_key = enc_key
    model_repository = ModelRepository()
    model_repository.load()
    if env_model_alias:
        model_repository.add_env(env_model_alias, env_model_name, env_api_key, env_api_type, env_api_version, env_api_base, env_temperature)
    session_manager = ChatSessionManager()
