import streamlit as st
from logic.user_state import ModelRepository, ChatSessionManager
from logic.utility import num_tokens_from_messages
from ui.ui_helpers import new_chat_collapse_markdown_hidden_elements


def start_new_chat(model_repository: ModelRepository, session_manager: ChatSessionManager,
                   system_message: str, temperature: float) -> dict:

    new_chat_collapse_markdown_hidden_elements()

    if 'new_chat_token_count' not in st.session_state:
        st.session_state['new_chat_token_count'] = None
    if 'new_chat_prompt' not in st.session_state:
        st.session_state['new_chat_prompt'] = None

    st.title('New Chat')
    model_options = [model.alias for model in model_repository.models]
    old_selected_model_alias = model_repository.get_last_used_model().alias
    selected_model_index = model_options.index(old_selected_model_alias)
    selected_model_alias = st.selectbox('Model', model_options, key='select_model_dropdown', index=selected_model_index)
    if old_selected_model_alias != selected_model_alias:
        model_repository.set_last_used_model_alias(selected_model_alias)
        st.rerun()
    model = model_repository.get_model_by_alias(selected_model_alias)

    session = None
    system_message = st.text_area('System message', st.session_state['system_message'])
    temperature = st.slider('Temperature', 0.0, 1.0, temperature, 0.01)
    prompt_title = "Prompt" if st.session_state['new_chat_token_count'] is None \
        else f"Prompt (Tokens: {st.session_state['new_chat_token_count']})"
    if prompt := st.text_area(prompt_title, value=st.session_state['new_chat_prompt']):
        if prompt != st.session_state['new_chat_prompt']:
            st.session_state['new_chat_token_count'] = num_tokens_from_messages(
                [{'role': 'User', 'content': prompt}])
            st.session_state['new_chat_prompt'] = prompt
            st.rerun()
    if st.button("Send message", type="primary"):
        if st.session_state['new_chat_prompt']:
            session = session_manager.create_session(model, ' '.join(prompt.split()[:5]))

            if system_message:
                session.add_message({'role': 'system', 'content': system_message})
            session.add_message({'role': 'user', 'content': prompt})

            model.temperature = temperature
            model_repository.update(model.alias, model)
            st.session_state['new_chat_prompt'] = None
            st.session_state['new_chat_token_count'] = None
            st.session_state['show_chat_session'] = True

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
