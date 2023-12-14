import streamlit as st
from logic.user_state import ModelRepository, ChatSessionManager
from ui.ui_helpers import new_chat_collapse_markdown_hidden_elements


def start_new_chat(model_repository: ModelRepository, session_manager: ChatSessionManager,
                   system_message: str, temperature: float) -> dict:

    new_chat_collapse_markdown_hidden_elements()

    st.title('New Chat')
    model_options = [model.alias for model in model_repository.models]
    selected_model_alias = model_repository.get_last_used_model().alias
    selected_model_alias = st.selectbox('Model', model_options)
    model = model_repository.get_model_by_alias(selected_model_alias)
    model_repository.set_last_used_model_alias(selected_model_alias)

    session = None
    system_message = st.text_area('System message', st.session_state['system_message'])
    temperature = st.slider('Temperature', 0.0, 1.0, temperature, 0.01)
    prompt = st.text_area('Prompt')
    if st.button("Send message", type="primary"):
        if prompt:
            session = session_manager.create_session(model, ' '.join(prompt.split()[:5]))

            if system_message:
                session.add_message({'role': 'system', 'content': system_message})
            session.add_message({'role': 'user', 'content': prompt})

            model.temperature = temperature
            model_repository.update(model.alias, model)

    # Return the updated state
    state_update = {
        'system_message': system_message,
        'temperature': temperature
    }
    if session:
        state_update['selected_menu'] = f'{session.title} ({session.session_id})'
        state_update['chat_session_id'] = session.session_id
        state_update['prompt'] = prompt

    return state_update
