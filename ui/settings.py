import streamlit as st
import logic.user_state as state
from logic import env_vars
from ui.ui_helpers import settings_collapse_markdown_hidden_elements


def manage_models(model_repository: state.ModelRepository) -> dict:
    """
    Returns 'models_changed': True is there're any write ioperations hapenning inside
    (e.g. adding, deleteting, updating) - might want to do upstream refresh
    """

    settings_collapse_markdown_hidden_elements()

    ADD_NEW_MODEL_TEXT = "+ Add New Model"

    def get_model_options():
        return [ADD_NEW_MODEL_TEXT] + [model.alias for model in model_repository.models]

    models_changed = False
    st.title("Manage Models")
    model_options = get_model_options()
    if "settings_selected_index" not in st.session_state:
        st.session_state["settings_selected_index"] = 0

    old_index = st.session_state["settings_selected_index"]
    selected_model_alias = st.selectbox(
        "Select Model", model_options, index=st.session_state["settings_selected_index"]
    )
    st.session_state["settings_selected_index"] = model_options.index(
        selected_model_alias
    )
    if old_index != st.session_state["settings_selected_index"]:
        st.rerun()
    selected_model = next(
        (
            model
            for model in state.model_repository.models
            if model.alias == selected_model_alias
        ),
        None,
    )
    is_env_model = selected_model.is_env if selected_model else False

    is_new_model = selected_model_alias == ADD_NEW_MODEL_TEXT
    is_fake_type = (
        selected_model.api_type == env_vars.ApiTypeOptions.FAKE
        if selected_model
        else False
    )
    st.subheader(
        "Fake Model Settings"
        if is_fake_type
        else (
            ADD_NEW_MODEL_TEXT
            if is_new_model
            else (
                "Environment Model Parameters"
                if is_env_model
                else "Custom Model Settings"
            )
        )
    )

    api_type_options = [env_vars.ApiTypeOptions.AZURE, env_vars.ApiTypeOptions.OPENAI]
    api_type_index = (
        api_type_options.index(selected_model.api_type)
        if selected_model and selected_model.api_type in api_type_options
        else 0
    )
    api_type = st.selectbox(
        "API Type",
        [option.value for option in api_type_options],
        index=api_type_index,
        disabled=is_env_model or is_fake_type,
    )
    api_type = env_vars.ApiTypeOptions.from_string(api_type)

    selected_model_alias = st.text_input(
        "Model Alias (Display Name)",
        value=selected_model_alias if not is_new_model else "",
        disabled=is_env_model or is_fake_type,
    )

    is_openai_type = api_type == env_vars.ApiTypeOptions.OPENAI

    model_or_deployment_name = st.text_input(
        'Model Name (e.g. "gpt-3.5-turbo-0613")',
        value=selected_model.model_or_deployment_name if not is_new_model else "",
        disabled=is_env_model or is_fake_type,
    )

    api_key = st.text_input(
        "API Key",
        selected_model.api_key if selected_model else "",
        disabled=is_env_model or is_fake_type,
    )

    api_base = st.text_input(
        (
            "Leave empty to use OpenAI, or set to override `base_url=` (e.g. custom model deployment)"
            if is_openai_type
            else 'API Base (e.g. "https://my_model.openai.azure.com")'
        ),
        selected_model.api_base if selected_model else "",
        disabled=is_env_model or is_fake_type,
    )

    api_version = st.text_input(
        'API Version (e.g. "2023-07-01-preview")',
        selected_model.api_version if selected_model else "",
        disabled=is_env_model or is_openai_type or is_fake_type,
    )

    tokenizer_options = [tk.value for tk in env_vars.TokenizerKind]
    tokenizer_index = (
        tokenizer_options.index(selected_model.tokenizer_kind) if selected_model else 0
    )
    tokenizer_kind = st.selectbox(
        "Tokenizer Kind",
        tokenizer_options,
        index=tokenizer_index,
        disabled=is_env_model or is_fake_type,
    )

    temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        selected_model.temperature if selected_model else 0.7,
        0.01,
        disabled=is_env_model or is_fake_type,
    )

    errors = []
    if not model_or_deployment_name and not is_env_model and is_new_model:
        errors.append("Model Name is required.")
    if not api_key and not is_env_model:
        errors.append("API Key is required.")
    if not api_version and not is_env_model and not is_openai_type:
        errors.append("API Version is required.")
    if not api_base and not is_env_model and not is_openai_type:
        errors.append("API Base is required.")
    if temperature is None and not is_env_model:
        errors.append("Temperature is required.")

    if errors:
        for error in errors:
            st.error(error)

    if is_new_model and not is_fake_type:
        if st.button("Add Model"):
            if not errors:
                try:
                    if selected_model_alias in get_model_options():
                        raise ValueError(
                            f"The model alias '{selected_model_alias}' already exists."
                        )
                    model = state.Model(
                        selected_model_alias,
                        model_or_deployment_name,
                        api_key,
                        api_type,
                        api_version,
                        api_base,
                        temperature,
                        tokenizer_kind,
                    )
                    state.model_repository.add(model)
                    st.success("Model added successfully!")
                    selected_model_alias = model.alias
                    st.session_state["settings_selected_index"] = (
                        get_model_options().index(selected_model_alias)
                    )
                    models_changed = True
                except Exception as e:
                    st.error(f"Failed to add model: {e}")
    else:
        if not is_env_model and not is_fake_type:
            if st.button("Update Model"):
                if not errors:
                    try:
                        old_alias = selected_model.alias
                        selected_model.alias = selected_model_alias
                        selected_model.model_or_deployment_name = (
                            model_or_deployment_name
                        )
                        selected_model.api_key = api_key
                        selected_model.api_type = api_type
                        selected_model.api_version = api_version
                        selected_model.api_base = api_base
                        selected_model.temperature = temperature
                        selected_model.tokenizer_kind = tokenizer_kind
                        state.model_repository.update(old_alias, selected_model)
                        selected_model_alias = selected_model.alias
                        st.success("Model updated successfully!")
                        st.session_state["settings_selected_index"] = (
                            get_model_options().index(selected_model_alias)
                        )
                        models_changed = True
                    except Exception as e:
                        st.error(f"Failed to update model: {e}")
            if st.button("Delete Model"):
                try:
                    state.model_repository.delete(selected_model.alias)
                    models_changed = True
                    st.session_state["settings_selected_index"] = 0
                except Exception as e:
                    st.error(f"Failed to delete model: {e}")
    return {"models_changed": models_changed}
