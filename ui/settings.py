import streamlit as st
import logic.user_state as state


def manage_models(selected_model_alias_in_settings: str, model_repository: state.ModelRepository) -> dict:
    """
    Returns 'models_changed': True is there're any write ioperations hapenning inside (e.g. adding, deleteting, updating) - might 
    want to do upstream refresh
    """
    ADD_NEW_MODEL_TEXT = '+ Add New Model'
    models_changed = False
    st.title('Manage Models')
    model_options = [ADD_NEW_MODEL_TEXT] + [model.alias for model in model_repository.models]
    model_selected_index = model_options.index(selected_model_alias_in_settings) if selected_model_alias_in_settings in model_options else 0
    selected_model_alias_in_settings = st.selectbox('Select Model', model_options, index=model_selected_index)
    selected_model = next((model for model in state.model_repository.models if model.alias == selected_model_alias_in_settings), None)
    is_env_model = selected_model.is_env if selected_model else False

    is_new_model = selected_model_alias_in_settings == ADD_NEW_MODEL_TEXT
    is_fake_type = selected_model.api_type == state.ApiTypeOptions.FAKE if selected_model else False
    st.subheader('Fake Model Settings' if is_fake_type else ADD_NEW_MODEL_TEXT if is_new_model else 'Environment Model Parameters' if is_env_model else 'Custom Model Settings')

    api_type_options = [option.value for option in state.ApiTypeOptions if option != state.ApiTypeOptions.FAKE]
    api_type_index = api_type_options.index(selected_model.api_type) if selected_model and selected_model.api_type in api_type_options else 0
    api_type = st.selectbox('API Type', api_type_options, index=api_type_index, disabled=is_env_model or is_fake_type, on_change=lambda: st.rerun())

    selected_model_alias_in_settings = st.text_input('Model Alias (Display Name)', value=selected_model_alias_in_settings if not is_new_model else '', disabled=is_env_model or is_fake_type)
    is_openai_type = api_type == state.ApiTypeOptions.OPENAI

    model_or_deployment_name = st.text_input('Model Name (e.g. "gpt-3.5-turbo-0613")', value=selected_model.model_or_deployment_name if not is_new_model else '', disabled=is_env_model or is_fake_type)
    api_key = st.text_input('API Key', selected_model.api_key if selected_model else '', disabled=is_env_model or is_fake_type)
    api_version = st.text_input('API Version (e.g. "2023-07-01-preview")', selected_model.api_version if selected_model else '', disabled=is_env_model or is_openai_type or is_fake_type)
    api_base = st.text_input('API Base (e.g. "https://my_model.openai.azure.com")', selected_model.api_base if selected_model else '', disabled=is_env_model or is_openai_type or is_fake_type)
    temperature = st.slider(f'Temperature', 0.0, 1.0, 
                            selected_model.temperature if selected_model else 0.7, 0.01, 
                            disabled=is_env_model or is_fake_type)

    # Validation summary
    errors = []
    if not model_or_deployment_name and not is_env_model and is_new_model:
        errors.append('Model Name is required.')
    if not api_key and not is_env_model:
        errors.append('API Key is required.')
    if not api_version and not is_env_model and not is_openai_type:
        errors.append('API Version is required.')
    if not api_base and not is_env_model and not is_openai_type:
        errors.append('API Base is required.')
    if temperature is None and not is_env_model:
        errors.append('Temperature is required.')

    if errors:
        for error in errors:
            st.error(error)

    if is_new_model and not is_fake_type:
        if st.button('Add Model') and not errors:
            model = state.Model(selected_model_alias_in_settings, model_or_deployment_name, api_key, api_type, api_version, api_base, temperature)
            state.model_repository.add(model)
            st.success('Model added successfully!')
            selected_model_alias_in_settings = model.alias 
            models_changed = True
    else:
        if not is_env_model and not is_fake_type:
            if st.button('Update Model') and not errors:
                selected_model.alias = selected_model_alias_in_settings
                selected_model.model_or_deployment_name = model_or_deployment_name
                selected_model.api_key = api_key
                selected_model.api_type = api_type
                selected_model.api_version = api_version
                selected_model.api_base = api_base
                selected_model.temperature = temperature
                state.model_repository.update(selected_model)
                selected_model_alias_in_settings = selected_model.alias 
                st.success('Model updated successfully!')
                models_changed = True
            if st.button('Delete Model'):
                state.model_repository.delete(selected_model.alias)
                st.success('Model deleted successfully!')
                last_model = state.model_repository.get_last_used_model()
                selected_model_alias_in_settings = last_model.alias if last_model else None
                models_changed = True
    return {
        'selected_model_alias_in_settings': selected_model_alias_in_settings,
        'models_changed': models_changed
    }