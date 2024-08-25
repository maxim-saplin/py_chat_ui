import streamlit as st
from logic.user_state import ModelRepository, ChatSessionManager
from logic.utility import num_tokens_from_messages
from ui.ui_helpers import new_chat_add_command_enter_handler, hide_tokenzer_workaround_form, new_chat_calculate_tokens, \
    new_chat_collapse_markdown_hidden_elements


def start_new_chat(model_repository: ModelRepository, session_manager: ChatSessionManager,
                   system_message: str, temperature: float) -> dict:

    new_chat_collapse_markdown_hidden_elements()
    hide_tokenzer_workaround_form()
    new_chat_calculate_tokens()
    new_chat_add_command_enter_handler()

    if 'nc_chat_token_count' not in st.session_state:
        st.session_state['nc_chat_token_count'] = None
    if 'nc_prompt_for_tokenizer' not in st.session_state:
        st.session_state['nc_prompt_for_tokenizer'] = None

    # Hidden elements to trigger server side counting of token in chat input
    with st.form("hidden"):
        txt = st.text_area("tokenizer").strip()
        st.form_submit_button("Submit")
        if txt != st.session_state['nc_prompt_for_tokenizer'] \
                and not (txt == '' and st.session_state['nc_prompt_for_tokenizer'] is None):
            st.session_state['nc_prompt_for_tokenizer'] = None if txt == '' else txt
            st.session_state['nc_chat_token_count'] = None if st.session_state['nc_prompt_for_tokenizer'] is None \
                else num_tokens_from_messages([{'role': 'User', 'content': txt}])

    st.title('New Chat')
    model_options = [model.alias for model in model_repository.models]
    old_selected_model_alias = model_repository.get_last_used_model().alias
    selected_model_index = model_options.index(old_selected_model_alias)
    selected_model_alias = st.selectbox('Model', model_options, key='select_model_dropdown', index=selected_model_index)
    if old_selected_model_alias != selected_model_alias:
        model_repository.set_last_used_model_alias(selected_model_alias)
    model = model_repository.get_model_by_alias(selected_model_alias)

    session = None
    system_message = st.text_area('System message', st.session_state['system_message'])
    temperature = st.slider('Temperature', 0.0, 1.0, temperature, 0.01)
    button_title = "Send" if st.session_state['nc_chat_token_count'] is None \
        else f"Send ({st.session_state['nc_chat_token_count']} tokens)"


    prompt = st.text_area('Prompt', key='prompt_text_area')
    if st.button(button_title, type="primary"):
        if prompt:
            session = session_manager.create_session(model, ' '.join(prompt.split()[:5]))

            if system_message:
                session.add_message({'role': 'system', 'content': system_message})
            session.add_message({'role': 'user', 'content': prompt})

            model.temperature = temperature
            model_repository.update(model.alias, model)
            st.session_state['nc_chat_token_count'] = None
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
