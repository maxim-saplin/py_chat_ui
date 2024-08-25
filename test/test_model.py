import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from logic.user_state import Model, ModelRepository
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
    assert model.alias == "test_model"
    assert model.model_or_deployment_name == "gpt-3.5-turbo"
    assert model.api_key == "test_key"
    assert model.api_type == env_vars.ApiTypeOptions.OPENAI
    assert model.api_version == "2023-07-01-preview"
    assert model.api_base == "https://api.openai.com"
    assert model.temperature == 0.7
    assert model.tokenizer_kind == "cl100k_base"

def test_model_repository_add():
    repo = ModelRepository()
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
    repo.add(model)
    assert len(repo.models) == 1
    assert repo.models[0].alias == "test_model"

def test_model_repository_update():
    repo = ModelRepository()
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
    repo.add(model)
    updated_model = Model(
        alias="updated_model",
        model_or_deployment_name="gpt-3.5-turbo",
        api_key="updated_key",
        api_type=env_vars.ApiTypeOptions.OPENAI,
        api_version="2023-07-01-preview",
        api_base="https://api.openai.com",
        temperature=0.8,
        tokenizer_kind="o200k_base"
    )
    repo.update("test_model", updated_model)
    assert len(repo.models) == 1
    assert repo.models[0].alias == "updated_model"
    assert repo.models[0].api_key == "updated_key"
    assert repo.models[0].temperature == 0.8
    assert repo.models[0].tokenizer_kind == "o200k_base"

import tempfile
import shutil

@pytest.fixture
def temp_data_folder():
    temp_dir = tempfile.mkdtemp()
    env_vars.override_value(env_data_folder=temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_model_repository_save_load(temp_data_folder):
    repo = ModelRepository()
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
    repo.add(model)
    repo.save()

    # Create a new repository instance and load the data
    new_repo = ModelRepository()
    new_repo.load()

    assert len(new_repo.models) == 1
    loaded_model = new_repo.models[0]
    assert loaded_model.alias == "test_model"
    assert loaded_model.model_or_deployment_name == "gpt-3.5-turbo"
    assert loaded_model.api_key == "test_key"
    assert loaded_model.api_type == env_vars.ApiTypeOptions.OPENAI
    assert loaded_model.api_version == "2023-07-01-preview"
    assert loaded_model.api_base == "https://api.openai.com"
    assert loaded_model.temperature == 0.7
    assert loaded_model.tokenizer_kind == "cl100k_base"
    repo = ModelRepository()
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
    repo.add(model)
    repo.delete("test_model")
    assert len(repo.models) == 0
