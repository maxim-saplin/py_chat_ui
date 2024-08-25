import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from logic.user_state import Model, ModelRepository, ChatSession, ChatSessionManager
from logic import env_vars

from logic.user_state import init

@pytest.fixture(autouse=True)
def setup_user_state():
    from cryptography.fernet import Fernet
    valid_key = Fernet.generate_key()
    # Clear any existing data files
    data_folder = os.path.join(env_vars.env_data_folder, "test_user")
    if os.path.exists(data_folder):
        shutil.rmtree(data_folder)
    init("test_user", valid_key)
    model = Model(
        alias="test_model",
        model_or_deployment_name="gpt-3.5-turbo",
        api_key="test_key",
        api_type=env_vars.ApiTypeOptions.OPENAI,
        api_version="2023-07-01-preview",
        api_base="https://api.openai.com",
        temperature=0.7,
        tokenizer_kind="cl100k_base"
    )
    session = ChatSession(session_id=1, model=model, title="Test Session")
    assert session.session_id == 1
    assert session.model.alias == "test_model"
    assert session.title == "Test Session"

def test_chat_session_manager_create_session():
    model = Model(
        alias="test_model",
        model_or_deployment_name="gpt-3.5-turbo",
        api_key="test_key",
        api_type=env_vars.ApiTypeOptions.OPENAI,
        api_version="2023-07-01-preview",
        api_base="https://api.openai.com",
        temperature=0.7,
        tokenizer_kind="cl100k_base"
    )
    repo = ModelRepository()
    repo.add(model)
    global model_repository, session_manager
    model_repository = ModelRepository()
    session_manager = ChatSessionManager()
    session_manager.sessions = []
    session_manager.sessions = []
    session = session_manager.create_session(model, "Test Session")
    assert session.session_id == 1
    assert session.model.alias == "test_model"
    assert session.title == "Test Session"
    assert len(session_manager.sessions) == 1

import tempfile
import shutil

# @pytest.fixture
# def temp_data_folder():
#     temp_dir = tempfile.mkdtemp()
#     env_vars.override_value(env_data_folder=temp_dir)
#     yield temp_dir
#     shutil.rmtree(temp_dir)

# def test_chat_session_save_load(temp_data_folder):
#     model = Model(
#         alias="test_model",
#         model_or_deployment_name="gpt-3.5-turbo",
#         api_key="test_key",
#         api_type=env_vars.ApiTypeOptions.OPENAI,
#         api_version="2023-07-01-preview",
#         api_base="https://api.openai.com",
#         temperature=0.7,
#         tokenizer_kind="cl100k_base"
#     )
#     repo = ModelRepository()
#     repo.add(model)
#     global model_repository, session_manager
#     model_repository = ModelRepository()
#     session_manager = ChatSessionManager()
#     session = session_manager.create_session(model, "Test Session")
#     session.add_message({'role': 'user', 'content': 'Hello, how are you?'})
#     session.save()

#     # Create a new session manager instance and load the data
#     session_manager = ChatSessionManager()
#     session_manager.load_sessions()

#     assert len(session_manager.sessions) == 1
#     loaded_session = session_manager.sessions[0]
#     assert loaded_session.session_id == 1
#     assert loaded_session.model.alias == "test_model"
#     assert loaded_session.title == "Test Session"
#     assert len(loaded_session.messages) == 1
#     assert loaded_session.messages[0]['content'] == 'Hello, how are you?'
#     model = Model(
#         alias="test_model",
#         model_or_deployment_name="gpt-3.5-turbo",
#         api_key="test_key",
#         api_type=env_vars.ApiTypeOptions.OPENAI,
#         api_version="2023-07-01-preview",
#         api_base="https://api.openai.com",
#         temperature=0.7,
#         tokenizer_kind="cl100k_base"
#     )
#     repo = ModelRepository()
#     repo.add(model)
#     manager = ChatSessionManager()
#     session = manager.create_session(model, "Test Session")
#     manager.delete(session.session_id)
#     assert len(manager.sessions) == 0
